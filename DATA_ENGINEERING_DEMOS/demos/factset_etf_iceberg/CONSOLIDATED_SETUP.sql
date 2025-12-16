-- =============================================================================
-- FACTSET ETF CDC Demo - Consolidated Setup
-- Run this entire file in one Snowflake worksheet to set up both pipelines
-- 
-- This file combines config + initialization + both pipelines
-- All session variables work correctly when run together
-- =============================================================================

-- =============================================================================
-- CONFIGURATION
-- =============================================================================

-- Role and Warehouse
SET ROLE_NAME = 'SYSADMIN';  -- Change to ACCOUNTADMIN if needed
SET WAREHOUSE_NAME = 'DATA_ENG_XFORM_WH';

-- Working Database and Schema
SET WORK_DB = 'DATA_ENG_DEMO';
SET WORK_SCHEMA = 'FACTSET';

-- Iceberg Configuration
SET ICEBERG_DB = 'DATA_ENG_DEMO';
SET ICEBERG_SCHEMA = 'ICEBERG';
SET ICEBERG_TABLE = 'CONSTITUENTS_ICEBERG';

-- Source Table - FACTSET ETF Data Share (hardcoded)
SET SOURCE_TABLE = 'ETF_DATA.PUBLIC.CONSTITUENTS';

-- External Storage
SET EXTERNAL_STAGE = 'FACTSET_ETF_STAGE';
SET PARQUET_OUTPUT_PATH = 'REPORTING';

-- Schedule Configuration
SET REFRESH_SCHEDULE_10MIN = 'USING CRON */10 * * * * UTC';

SELECT '✅ Configuration loaded' AS STATUS;

-- =============================================================================
-- INITIALIZATION
-- =============================================================================

USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);

-- Create database and schemas
CREATE DATABASE IF NOT EXISTS IDENTIFIER($WORK_DB);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA);

USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Create stage
CREATE STAGE IF NOT EXISTS IDENTIFIER($EXTERNAL_STAGE)
    DIRECTORY = (ENABLE = TRUE);

-- Create file format
CREATE FILE FORMAT IF NOT EXISTS PARQUET_FORMAT
    TYPE = PARQUET
    COMPRESSION = SNAPPY;

-- Create local base snapshot
CREATE OR REPLACE TABLE constituents_base AS
SELECT *
FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Create Iceberg table
USE SCHEMA IDENTIFIER($ICEBERG_SCHEMA);

CREATE OR REPLACE TABLE IDENTIFIER($ICEBERG_TABLE) (
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
INSERT INTO IDENTIFIER($ICEBERG_TABLE)
SELECT 
    FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
    SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP,
    CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP
FROM IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA || '.constituents_base');

SELECT '✅ Initialization complete' AS STATUS;

-- =============================================================================
-- PIPELINE 1: Stream → Task → Iceberg
-- =============================================================================

USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Create stream
CREATE OR REPLACE STREAM pipeline1_constituents_stream
ON TABLE ETF_DATA.PUBLIC.CONSTITUENTS
APPEND_ONLY = FALSE;

-- Create task
CREATE OR REPLACE TASK pipeline1_stream_to_iceberg_merge_task
WAREHOUSE = IDENTIFIER($WAREHOUSE_NAME)
SCHEDULE = $REFRESH_SCHEDULE_10MIN
WHEN SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline1_constituents_stream')
AS
BEGIN
    DELETE FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE) AS t
    USING (
        SELECT DISTINCT FUND_ID, TICKER, AS_OF_DATE
        FROM pipeline1_constituents_stream
        WHERE METADATA$ACTION = 'DELETE'
    ) AS d
    WHERE t.FUND_ID = d.FUND_ID
        AND t.TICKER = d.TICKER
        AND t.AS_OF_DATE = d.AS_OF_DATE;

    MERGE INTO IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE) AS t
    USING (
        SELECT
            FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE,
            SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE, LOAD_TIMESTAMP
        FROM pipeline1_constituents_stream
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

-- Enable task
ALTER TASK pipeline1_stream_to_iceberg_merge_task RESUME;

SELECT '✅ Pipeline 1 deployed' AS STATUS;

-- =============================================================================
-- PIPELINE 2: Stream → Task → Parquet (CDC Audit Only)
-- =============================================================================

-- Create stream
CREATE OR REPLACE STREAM pipeline2_constituents_stream
ON TABLE ETF_DATA.PUBLIC.CONSTITUENTS
APPEND_ONLY = FALSE;

-- Create task
CREATE OR REPLACE TASK pipeline2_stream_to_parquet_task
WAREHOUSE = IDENTIFIER($WAREHOUSE_NAME)
SCHEDULE = $REFRESH_SCHEDULE_10MIN
WHEN SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline2_constituents_stream')
AS
    COPY INTO IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || '/pipeline2_cdc/')
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
        FROM pipeline2_constituents_stream
    )
    FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY)
    HEADER = FALSE
    INCLUDE_QUERY_ID = TRUE
    OVERWRITE = FALSE;

-- Enable task
ALTER TASK pipeline2_stream_to_parquet_task RESUME;

SELECT '✅ Pipeline 2 deployed' AS STATUS;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Show all created objects
SHOW TASKS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
SHOW STREAMS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
SHOW TABLES IN SCHEMA IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA);

-- Check data
SELECT 'Iceberg table rows: ' || COUNT(*) AS STATUS
FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE);

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT '✅ ✅ ✅ DEMO SETUP COMPLETE! ✅ ✅ ✅' AS FINAL_STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'Pipeline 1: Stream → Iceberg table (current state)' AS PIPELINE_1;
SELECT 'Pipeline 2: Stream → Parquet files (CDC audit)' AS PIPELINE_2;
SELECT 'Both pipelines are running and will process changes automatically' AS NOTE;

