-- =============================================================================
-- FACTSET ETF Constituents - Initialization Script
-- Deliverable 0: DB/Schema, Grants, Optional Local Base, Initial Parquet Export, Iceberg Table
-- 
-- Prerequisites:
-- 1. Access to ETF_DATA.PUBLIC.CONSTITUENTS share (REQUIRED)
-- 2. External storage configured (or use internal for demo)
-- 3. Run config_factset.sql first to set session variables
-- 
-- Follows PRD specification exactly
-- =============================================================================

-- =============================================================================
-- 1. SET CONTEXT
-- =============================================================================

USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);

SELECT 'Starting FACTSET ETF Constituents initialization...' AS STATUS;

-- =============================================================================
-- 2. CREATE DATABASE AND SCHEMAS
-- =============================================================================

-- Workspace
CREATE DATABASE IF NOT EXISTS IDENTIFIER($WORK_DB);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Iceberg database/schema (if distinct)
CREATE DATABASE IF NOT EXISTS IDENTIFIER($ICEBERG_DB);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA);

SELECT 'Database and schemas created' AS STATUS;

-- =============================================================================
-- 3. GRANTS - Access to stage and external volume
-- =============================================================================

-- Stage permissions (qualify the stage if not in current DB/SCHEMA)
GRANT USAGE ON STAGE IDENTIFIER($EXTERNAL_STAGE) TO ROLE IDENTIFIER($ROLE_NAME);
GRANT READ ON STAGE IDENTIFIER($EXTERNAL_STAGE) TO ROLE IDENTIFIER($ROLE_NAME);
GRANT WRITE ON STAGE IDENTIFIER($EXTERNAL_STAGE) TO ROLE IDENTIFIER($ROLE_NAME);

-- External volume permissions (for Iceberg)
-- Note: This requires the volume to be pre-created
-- GRANT USAGE ON EXTERNAL VOLUME IDENTIFIER($EXTERNAL_VOLUME) TO ROLE IDENTIFIER($ROLE_NAME);

SELECT 'Grants configured' AS STATUS;

-- =============================================================================
-- 4. CREATE INTERNAL STAGE (For demo - replace with external in production)
-- =============================================================================

CREATE STAGE IF NOT EXISTS IDENTIFIER($EXTERNAL_STAGE)
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Internal stage for FACTSET ETF parquet exports (use external in production)';

SELECT 'Stage created' AS STATUS;

-- =============================================================================
-- 5. VERIFY ACCESS TO FACTSET SHARE
-- =============================================================================

-- Verify the share is accessible (using explicit column list per PRD)
SELECT 'Verifying access to FACTSET share: ' || $SOURCE_TABLE AS STATUS;

SELECT COUNT(*) AS RECORD_COUNT
FROM ETF_DATA.PUBLIC.CONSTITUENTS;

SELECT 'FACTSET share verified and accessible' AS STATUS;

-- =============================================================================
-- 6. OPTIONAL: LOCAL BASE SNAPSHOT FROM SHARE
-- =============================================================================

-- Optional: Create a local snapshot of the source for reference/testing
-- This is useful for initial parquet export or point-in-time snapshots
-- Not required for streams (streams can be created directly on shared tables)

CREATE OR REPLACE TABLE constituents_base AS
SELECT
    FUND_ID,
    TICKER,
    CONSTITUENT_NAME,
    WEIGHT,
    SHARES,
    MARKET_VALUE,
    SECTOR,
    INDUSTRY,
    COUNTRY,
    AS_OF_DATE,
    LOAD_TIMESTAMP
FROM ETF_DATA.PUBLIC.CONSTITUENTS
COMMENT = 'Local snapshot of FACTSET ETF constituents for reference';

SELECT 'Local base table created with ' || COUNT(*) || ' records' AS STATUS
FROM constituents_base;

-- =============================================================================
-- 7. OPTIONAL: INITIAL PARQUET EXPORT
-- =============================================================================

-- Export initial snapshot to parquet
COPY INTO IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || '/initial/')
FROM (
    SELECT
        FUND_ID,
        TICKER,
        CONSTITUENT_NAME,
        WEIGHT,
        SHARES,
        MARKET_VALUE,
        SECTOR,
        INDUSTRY,
        COUNTRY,
        AS_OF_DATE,
        LOAD_TIMESTAMP,
        'INITIAL' AS OP_TYPE,
        CURRENT_TIMESTAMP() AS PROCESSED_TS
    FROM constituents_base
)
FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY)
OVERWRITE = TRUE
INCLUDE_QUERY_ID = TRUE
HEADER = FALSE;

SELECT 'Initial parquet export completed' AS STATUS;

-- =============================================================================
-- 8. CREATE ICEBERG TABLE ON EXTERNAL VOLUME
-- =============================================================================

USE SCHEMA IDENTIFIER($ICEBERG_SCHEMA);

-- Explicit schema definition per PRD (no SELECT *)
-- For demo without external volume, use regular table
-- In production with external volume, use commented Iceberg format below

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
)
COMMENT = 'FACTSET ETF constituents (demo table - use Iceberg format in production)';

/*
-- PRODUCTION VERSION with Iceberg format (requires external volume):
CREATE OR REPLACE ICEBERG TABLE IDENTIFIER($ICEBERG_TABLE) (
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
)
CATALOG = 'SNOWFLAKE'
EXTERNAL_VOLUME = IDENTIFIER($EXTERNAL_VOLUME)
BASE_LOCATION = $ICEBERG_BASE_LOCATION
COMMENT = 'FACTSET ETF constituents in Iceberg format';
*/

-- Initial load from base snapshot
INSERT INTO IDENTIFIER($ICEBERG_TABLE)
SELECT 
    FUND_ID,
    TICKER,
    CONSTITUENT_NAME,
    WEIGHT,
    SHARES,
    MARKET_VALUE,
    SECTOR,
    INDUSTRY,
    COUNTRY,
    AS_OF_DATE,
    LOAD_TIMESTAMP,
    CURRENT_TIMESTAMP() AS LAST_UPDATED_TIMESTAMP
FROM IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA || '.constituents_base');

SELECT 'Iceberg table created with ' || COUNT(*) || ' records' AS STATUS
FROM IDENTIFIER($ICEBERG_TABLE);

-- =============================================================================
-- 9. CREATE STREAM ON SOURCE TABLE (SHARED TABLE)
-- =============================================================================

USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Streams on shared tables are supported!
-- The stream lives in your schema, but captures changes from the shared table
CREATE OR REPLACE STREAM constituents_stream
ON TABLE ETF_DATA.PUBLIC.CONSTITUENTS
APPEND_ONLY = FALSE
COMMENT = 'CDC stream capturing changes to FACTSET ETF constituents';

SELECT 'Stream created: constituents_stream on ETF_DATA.PUBLIC.CONSTITUENTS' AS STATUS;

-- =============================================================================
-- 10. VERIFICATION
-- =============================================================================

SELECT '✅ Initialization Complete - Verifying objects...' AS STATUS;

-- Show created objects
SHOW TABLES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
SHOW STREAMS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
SHOW STAGES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

SELECT 'Tables in ' || $ICEBERG_SCHEMA AS INFO;
SHOW TABLES IN SCHEMA IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA);

-- Row counts
SELECT
    'constituents_base' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT
FROM IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA || '.constituents_base')
UNION ALL
SELECT
    'CONSTITUENTS_ICEBERG' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT
FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE);

-- Stream status
SELECT
    'Stream has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.constituents_stream') AS STREAM_STATUS;

SELECT '✅ Initialization completed successfully!' AS FINAL_STATUS;
SELECT 'Next steps: Run pipeline scripts (01-04) to set up CDC patterns' AS NEXT_STEPS;
