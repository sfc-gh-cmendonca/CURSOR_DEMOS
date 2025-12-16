-- =============================================================================
-- WORKAROUND: Stream from Local Copy (Share doesn't have change tracking)
-- 
-- Since ETF_DATA.PUBLIC.CONSTITUENTS doesn't have CHANGE_TRACKING enabled,
-- we cannot create a stream on it directly.
-- 
-- This workaround creates a local writable copy and streams from that.
-- =============================================================================

USE ROLE SYSADMIN;
USE WAREHOUSE DATA_ENG_XFORM_WH;

-- Create database and schemas
CREATE DATABASE IF NOT EXISTS DATA_ENG_DEMO;
CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.FACTSET;
CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.ICEBERG;

USE DATABASE DATA_ENG_DEMO;
USE SCHEMA FACTSET;

-- Create stage
CREATE STAGE IF NOT EXISTS FACTSET_ETF_STAGE
    DIRECTORY = (ENABLE = TRUE);

-- Create file format
CREATE FILE FORMAT IF NOT EXISTS PARQUET_FORMAT
    TYPE = PARQUET
    COMPRESSION = SNAPPY;

-- =============================================================================
-- CREATE LOCAL WRITABLE COPY OF FACTSET DATA
-- =============================================================================

-- This is a LOCAL table (not shared) so we CAN create a stream on it
CREATE OR REPLACE TABLE constituents_local AS
SELECT *
FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Enable change tracking on local table
ALTER TABLE constituents_local SET CHANGE_TRACKING = TRUE;

SELECT 'Local table created with ' || COUNT(*) || ' rows' AS STATUS
FROM constituents_local;

-- =============================================================================
-- PIPELINE 1: Stream → Task → Iceberg
-- =============================================================================

-- Create stream on LOCAL table (this works!)
CREATE OR REPLACE STREAM pipeline1_constituents_stream
ON TABLE constituents_local
APPEND_ONLY = FALSE;

SELECT 'Stream created on local table' AS STATUS;

-- Create Iceberg table
USE SCHEMA ICEBERG;

CREATE OR REPLACE TABLE CONSTITUENTS_ICEBERG (
    FUND_ID STRING,
    TICKER STRING,
    CONSTITUENT_NAME STRING,
    WEIGHT DECIMAL(18,6),
    SHARES DECIMAL(18,2),
    MARKET_VALUE DECIMAL(18,2),
    SECTOR STRING,
    INDUSTRY STRING,
    COUNTRY STRING,
    AS_OF_DATE DATE,
    LOAD_TIMESTAMP TIMESTAMP_NTZ,
    LAST_UPDATED_TIMESTAMP TIMESTAMP_NTZ
);

-- Initial load
INSERT INTO CONSTITUENTS_ICEBERG
SELECT 
    FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
    SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP,
    CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP
FROM DATA_ENG_DEMO.FACTSET.constituents_local;

SELECT 'Iceberg table loaded with ' || COUNT(*) || ' rows' AS STATUS
FROM CONSTITUENTS_ICEBERG;

-- Create task
USE SCHEMA FACTSET;

CREATE OR REPLACE TASK pipeline1_stream_to_iceberg_merge_task
WAREHOUSE = DATA_ENG_XFORM_WH
SCHEDULE = 'USING CRON */10 * * * * UTC'
WHEN SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline1_constituents_stream')
AS
BEGIN
    DELETE FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG AS t
    USING (
        SELECT DISTINCT FUND_ID, TICKER, AS_OF_DATE
        FROM DATA_ENG_DEMO.FACTSET.pipeline1_constituents_stream
        WHERE METADATA$ACTION = 'DELETE'
    ) AS d
    WHERE t.FUND_ID = d.FUND_ID
        AND t.TICKER = d.TICKER
        AND t.AS_OF_DATE = d.AS_OF_DATE;

    MERGE INTO DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG AS t
    USING (
        SELECT
            FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
            SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP
        FROM DATA_ENG_DEMO.FACTSET.pipeline1_constituents_stream
        WHERE METADATA$ACTION = 'INSERT'
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY FUND_ID, TICKER, AS_OF_DATE
            ORDER BY METADATA$ISUPDATE DESC, LOAD_TIMESTAMP DESC
        ) = 1
    ) AS u
    ON t.FUND_ID = u.FUND_ID
       AND t.TICKER = u.TICKER
       AND t.AS_OF_DATE = u.AS_OF_DATE
    WHEN MATCHED THEN
        UPDATE SET
            t.CONSTITUENT_NAME = u.CONSTITUENT_NAME,
            t.WEIGHT = u.WEIGHT,
            t.SHARES = u.SHARES,
            t.MARKET_VALUE = u.MARKET_VALUE,
            t.SECTOR = u.SECTOR,
            t.INDUSTRY = u.INDUSTRY,
            t.COUNTRY = u.COUNTRY,
            t.LOAD_TIMESTAMP = u.LOAD_TIMESTAMP,
            t.LAST_UPDATED_TIMESTAMP = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
        INSERT (
            FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
            SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP, LAST_UPDATED_TIMESTAMP
        )
        VALUES (
            u.FUND_ID, u.TICKER, u.CONSTITUENT_NAME, u.WEIGHT, u.SHARES, u.MARKET_VALUE,
            u.SECTOR, u.INDUSTRY, u.COUNTRY, u.AS_OF_DATE, u.LOAD_TIMESTAMP, CURRENT_TIMESTAMP()
        );
END;

ALTER TASK pipeline1_stream_to_iceberg_merge_task RESUME;

SELECT '✅ Pipeline 1 created and running' AS STATUS;

-- =============================================================================
-- PIPELINE 2: Stream → Task → Parquet (CDC Audit Only)
-- =============================================================================

-- Create stream on LOCAL table
CREATE OR REPLACE STREAM pipeline2_constituents_stream
ON TABLE constituents_local
APPEND_ONLY = FALSE;

SELECT 'Stream created for Pipeline 2' AS STATUS;

-- Create task
CREATE OR REPLACE TASK pipeline2_stream_to_parquet_task
WAREHOUSE = DATA_ENG_XFORM_WH
SCHEDULE = 'USING CRON */10 * * * * UTC'
WHEN SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline2_constituents_stream')
AS
    COPY INTO @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/
    FROM (
        SELECT
            FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
            SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP,
            CASE
                WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
                WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
                WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
                ELSE 'UNKNOWN'
            END AS OP_TYPE,
            CURRENT_TIMESTAMP() AS PROCESSED_TS,
            TO_VARCHAR(CURRENT_TIMESTAMP(), 'YYYY-MM-DD') AS PARTITION_DATE,
            METADATA$ROW_ID AS SOURCE_ROW_ID
        FROM DATA_ENG_DEMO.FACTSET.pipeline2_constituents_stream
    )
    FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY)
    HEADER = FALSE
    INCLUDE_QUERY_ID = TRUE
    OVERWRITE = FALSE;

ALTER TASK pipeline2_stream_to_parquet_task RESUME;

SELECT '✅ Pipeline 2 created and running' AS STATUS;

-- =============================================================================
-- OPTIONAL: Task to Refresh Local Copy from Share
-- =============================================================================

-- This task periodically refreshes the local copy from the FACTSET share
-- Run this if you want to keep the local copy in sync with the share

CREATE OR REPLACE TASK refresh_local_copy_task
WAREHOUSE = DATA_ENG_XFORM_WH
SCHEDULE = 'USING CRON 0 * * * * UTC'  -- Hourly
AS
    MERGE INTO constituents_local AS tgt
    USING (SELECT * FROM ETF_DATA.PUBLIC.CONSTITUENTS) AS src
    ON tgt.FUND_ID = src.FUND_ID
       AND tgt.TICKER = src.TICKER
       AND tgt.AS_OF_DATE = src.AS_OF_DATE
    WHEN MATCHED THEN
        UPDATE SET
            tgt.CONSTITUENT_NAME = src.CONSTITUENT_NAME,
            tgt.WEIGHT = src.WEIGHT,
            tgt.SHARES = src.SHARES,
            tgt.MARKET_VALUE = src.MARKET_VALUE,
            tgt.SECTOR = src.SECTOR,
            tgt.INDUSTRY = src.INDUSTRY,
            tgt.COUNTRY = src.COUNTRY,
            tgt.LOAD_TIMESTAMP = src.LOAD_TIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT VALUES (
            src.FUND_ID, src.TICKER, src.CONSTITUENT_NAME, src.WEIGHT, src.SHARES,
            src.MARKET_VALUE, src.SECTOR, src.INDUSTRY, src.COUNTRY,
            src.AS_OF_DATE, src.LOAD_TIMESTAMP
        );

ALTER TASK refresh_local_copy_task RESUME;

SELECT '✅ Refresh task created (syncs local copy from share hourly)' AS STATUS;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

SHOW TASKS IN SCHEMA DATA_ENG_DEMO.FACTSET;
SHOW STREAMS IN SCHEMA DATA_ENG_DEMO.FACTSET;

SELECT 'Iceberg rows: ' || COUNT(*) AS ICEBERG_STATUS
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;

SELECT 'Local copy rows: ' || COUNT(*) AS LOCAL_STATUS
FROM DATA_ENG_DEMO.FACTSET.constituents_local;

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT '✅ ✅ ✅ DEMO SETUP COMPLETE! ✅ ✅ ✅' AS FINAL_STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

SELECT 'NOTE: Streams are on LOCAL copy (constituents_local), not the share' AS NOTE;
SELECT 'Reason: FACTSET share does not have CHANGE_TRACKING enabled' AS REASON;
SELECT 'Solution: Contact FACTSET to enable change tracking, or use this workaround' AS SOLUTION;

