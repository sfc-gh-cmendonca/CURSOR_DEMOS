-- =============================================================================
-- SIMPLE SETUP - FACTSET ETF CDC Demo
-- 
-- This is the simplest, most reliable setup
-- Run this entire file in Snowflake Web UI (copy/paste and "Run All")
-- =============================================================================

-- =============================================================================
-- STEP 1: CREATE INFRASTRUCTURE
-- =============================================================================

USE ROLE SYSADMIN;

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_XFORM_WH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

USE WAREHOUSE DATA_ENG_XFORM_WH;

-- Create database and schemas
CREATE DATABASE IF NOT EXISTS DATA_ENG_DEMO;
USE DATABASE DATA_ENG_DEMO;

CREATE SCHEMA IF NOT EXISTS FACTSET;
CREATE SCHEMA IF NOT EXISTS ICEBERG;

USE SCHEMA FACTSET;

-- Create stage
CREATE STAGE IF NOT EXISTS FACTSET_ETF_STAGE;

-- Create file format
CREATE FILE FORMAT IF NOT EXISTS PARQUET_FORMAT TYPE = PARQUET;

SELECT '✅ Infrastructure created' AS STATUS;

-- =============================================================================
-- STEP 2: CREATE LOCAL COPY OF FACTSET DATA
-- =============================================================================

-- Create local writable copy (required because share doesn't have change tracking)
CREATE OR REPLACE TABLE constituents_local AS
SELECT *
FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Enable change tracking
ALTER TABLE constituents_local SET CHANGE_TRACKING = TRUE;

SELECT 'Local copy created with ' || COUNT(*) || ' rows' AS STATUS
FROM constituents_local;

-- =============================================================================
-- STEP 3: CREATE ICEBERG TABLE
-- =============================================================================

USE SCHEMA ICEBERG;

CREATE OR REPLACE TABLE CONSTITUENTS_ICEBERG AS
SELECT *, CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP
FROM DATA_ENG_DEMO.FACTSET.constituents_local;

SELECT 'Iceberg table created with ' || COUNT(*) || ' rows' AS STATUS
FROM CONSTITUENTS_ICEBERG;

-- =============================================================================
-- STEP 4: PIPELINE 1 - Stream → Iceberg
-- =============================================================================

USE SCHEMA FACTSET;

-- Create stream
CREATE OR REPLACE STREAM pipeline1_stream
ON TABLE constituents_local;

-- Create task
CREATE OR REPLACE TASK pipeline1_task
WAREHOUSE = DATA_ENG_XFORM_WH
SCHEDULE = '10 MINUTE'
WHEN SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline1_stream')
AS
BEGIN
    -- Delete records
    DELETE FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG t
    WHERE EXISTS (
        SELECT 1 FROM DATA_ENG_DEMO.FACTSET.pipeline1_stream s
        WHERE s.METADATA$ACTION = 'DELETE'
          AND s.FUND_ID = t.FUND_ID
          AND s.TICKER = t.TICKER
          AND s.AS_OF_DATE = t.AS_OF_DATE
    );
    
    -- Merge changes
    MERGE INTO DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG t
    USING (
        SELECT *
        FROM DATA_ENG_DEMO.FACTSET.pipeline1_stream
        WHERE METADATA$ACTION = 'INSERT'
    ) s
    ON t.FUND_ID = s.FUND_ID
       AND t.TICKER = s.TICKER
       AND t.AS_OF_DATE = s.AS_OF_DATE
    WHEN MATCHED THEN UPDATE SET
        t.CONSTITUENT_NAME = s.CONSTITUENT_NAME,
        t.WEIGHT = s.WEIGHT,
        t.SHARES = s.SHARES,
        t.MARKET_VALUE = s.MARKET_VALUE,
        t.SECTOR = s.SECTOR,
        t.INDUSTRY = s.INDUSTRY,
        t.COUNTRY = s.COUNTRY,
        t.LOAD_TIMESTAMP = s.LOAD_TIMESTAMP,
        t.LAST_UPDATED_TIMESTAMP = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (
        FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
        SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP, LAST_UPDATED_TIMESTAMP
    )
    VALUES (
        s.FUND_ID, s.TICKER, s.CONSTITUENT_NAME, s.WEIGHT, s.SHARES, s.MARKET_VALUE,
        s.SECTOR, s.INDUSTRY, s.COUNTRY, s.AS_OF_DATE, s.LOAD_TIMESTAMP, CURRENT_TIMESTAMP()
    );
END;

-- Enable task
ALTER TASK pipeline1_task RESUME;

SELECT '✅ Pipeline 1 created' AS STATUS;

-- =============================================================================
-- STEP 5: PIPELINE 2 - Stream → Parquet (CDC Audit)
-- =============================================================================

-- Create stream
CREATE OR REPLACE STREAM pipeline2_stream
ON TABLE constituents_local;

-- Create task
CREATE OR REPLACE TASK pipeline2_task
WAREHOUSE = DATA_ENG_XFORM_WH
SCHEDULE = '10 MINUTE'
WHEN SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline2_stream')
AS
    COPY INTO @FACTSET_ETF_STAGE/REPORTING/cdc/
    FROM (
        SELECT
            *,
            CASE
                WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE THEN 'UPDATE'
                WHEN METADATA$ACTION = 'INSERT' THEN 'ADD'
                WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
            END AS OP_TYPE,
            CURRENT_TIMESTAMP() AS PROCESSED_TS
        FROM DATA_ENG_DEMO.FACTSET.pipeline2_stream
    )
    FILE_FORMAT = (TYPE = PARQUET)
    OVERWRITE = FALSE;

-- Enable task
ALTER TASK pipeline2_task RESUME;

SELECT '✅ Pipeline 2 created' AS STATUS;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

SHOW TASKS IN SCHEMA DATA_ENG_DEMO.FACTSET;
SHOW STREAMS IN SCHEMA DATA_ENG_DEMO.FACTSET;

SELECT 'Iceberg table: ' || COUNT(*) || ' rows' AS STATUS
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;

SELECT 'Local copy: ' || COUNT(*) || ' rows' AS STATUS
FROM DATA_ENG_DEMO.FACTSET.constituents_local;

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT '✅ ✅ ✅ SETUP COMPLETE! ✅ ✅ ✅' AS FINAL_STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'Pipeline 1: Stream → Iceberg table' AS PIPELINE_1;
SELECT 'Pipeline 2: Stream → Parquet files (CDC audit)' AS PIPELINE_2;
SELECT 'Both tasks are running and will process changes every 10 minutes' AS NOTE;

