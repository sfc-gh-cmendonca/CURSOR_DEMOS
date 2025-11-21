-- =============================================================================
-- Configuration for FACTSET ETF Constituents Iceberg/Parquet ETL Demo
-- Set all parameters before running any pipeline scripts
-- 
-- Follows PRD specification for parameter management
-- =============================================================================

-- Role and Warehouse
SET ROLE_NAME = 'ACCOUNTADMIN';  -- Change to your role with appropriate privileges
SET WAREHOUSE_NAME = 'DATA_ENG_XFORM_WH';  -- Or your preferred warehouse

-- Working Database and Schema
SET WORK_DB = 'DATA_ENG_DEMO';
SET WORK_SCHEMA = 'FACTSET';

-- Iceberg Configuration
SET ICEBERG_DB = 'DATA_ENG_DEMO';
SET ICEBERG_SCHEMA = 'ICEBERG';
SET ICEBERG_TABLE = 'CONSTITUENTS_ICEBERG';

-- Source Table - FACTSET ETF Data Share (hardcoded per PRD)
-- This is the shared table that must exist in your account
SET SOURCE_TABLE = 'ETF_DATA.PUBLIC.CONSTITUENTS';

-- Business Keys (comma-separated list for join conditions)
-- Based on FACTSET ETF constituents typical structure
SET KEY_COLUMNS = 'FUND_ID, TICKER, AS_OF_DATE';

-- External Storage
-- Note: These must be pre-created in your Snowflake account
-- For production use: @EXT_STG_STREAMING_TRANSACTIONS and snowbank_iceberg_vol
-- For demo purposes, we use internal equivalents

-- Production values (commented - requires external storage setup):
-- SET EXTERNAL_STAGE = 'EXT_STG_STREAMING_TRANSACTIONS';
-- SET EXTERNAL_VOLUME = 'snowbank_iceberg_vol';

-- Demo values (using internal stage, regular table instead of Iceberg):
SET EXTERNAL_STAGE = 'FACTSET_ETF_STAGE';
SET EXTERNAL_VOLUME = 'factset_iceberg_vol';  -- Note: External volume creation requires cloud storage
SET PARQUET_OUTPUT_PATH = 'REPORTING';
SET ICEBERG_BASE_LOCATION = 'constituents';

-- Schedule Configuration (using CRON format per PRD)
SET REFRESH_SCHEDULE_10MIN = 'USING CRON */10 * * * * UTC';  -- Every 10 minutes
SET REFRESH_SCHEDULE_HOURLY = 'USING CRON 0 * * * * UTC';   -- Hourly

-- Display Configuration
SELECT 'Configuration loaded successfully' AS STATUS;
SELECT 
    $ROLE_NAME AS ROLE_NAME,
    $WAREHOUSE_NAME AS WAREHOUSE_NAME,
    $SOURCE_TABLE AS SOURCE_TABLE,
    $WORK_DB AS WORK_DB,
    $WORK_SCHEMA AS WORK_SCHEMA,
    $ICEBERG_DB AS ICEBERG_DB,
    $ICEBERG_SCHEMA AS ICEBERG_SCHEMA,
    $ICEBERG_TABLE AS ICEBERG_TABLE,
    $KEY_COLUMNS AS KEY_COLUMNS,
    $EXTERNAL_STAGE AS EXTERNAL_STAGE,
    $EXTERNAL_VOLUME AS EXTERNAL_VOLUME;

SELECT '✅ All configuration parameters set' AS FINAL_STATUS;
SELECT 'Note: This demo uses stream-attached tasks only (no Dynamic Tables)' AS ARCHITECTURE_NOTE;
SELECT 'Next: Run 00_initialization.sql to set up the environment' AS NEXT_STEPS;
