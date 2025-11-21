-- =============================================================================
-- FACTSET ETF Constituents - Cleanup Script
-- Removes all demo objects created for Iceberg/Parquet ETL pipelines
-- 
-- WARNING: This will delete all tasks, streams, tables, and data!
-- Note: No Dynamic Tables in this demo (they don't support Streams)
-- =============================================================================

-- Load configuration
USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);

SELECT '🧹 Starting cleanup of FACTSET ETF Iceberg/Parquet demo...' AS STATUS;

-- =============================================================================
-- 1. SUSPEND AND DROP TASKS (must be done before dropping other objects)
-- =============================================================================

USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Suspend all tasks first
ALTER TASK IF EXISTS PIPELINE1_STREAM_TO_ICEBERG_MERGE_TASK SUSPEND;
ALTER TASK IF EXISTS PIPELINE2_STREAM_TO_PARQUET_TASK SUSPEND;

SELECT 'Tasks suspended' AS STATUS;

-- Drop tasks
DROP TASK IF EXISTS PIPELINE1_STREAM_TO_ICEBERG_MERGE_TASK;
DROP TASK IF EXISTS PIPELINE2_STREAM_TO_PARQUET_TASK;

SELECT 'Tasks dropped' AS STATUS;

-- =============================================================================
-- 2. DROP STREAMS
-- =============================================================================

DROP STREAM IF EXISTS CONSTITUENTS_STREAM;  -- Legacy from initialization
DROP STREAM IF EXISTS PIPELINE1_CONSTITUENTS_STREAM;  -- Pipeline 1 stream
DROP STREAM IF EXISTS PIPELINE2_CONSTITUENTS_STREAM;  -- Pipeline 2 stream

SELECT 'Streams dropped' AS STATUS;

-- =============================================================================
-- 3. DROP REGULAR TABLES
-- =============================================================================

DROP TABLE IF EXISTS CONSTITUENTS_BASE;
DROP TABLE IF EXISTS ETF_CONSTITUENTS_SOURCE;

SELECT 'Regular tables dropped' AS STATUS;

-- =============================================================================
-- 4. DROP ICEBERG TABLE
-- =============================================================================

USE SCHEMA IDENTIFIER($ICEBERG_SCHEMA);

DROP TABLE IF EXISTS IDENTIFIER($ICEBERG_TABLE);

SELECT 'Iceberg table dropped' AS STATUS;

-- =============================================================================
-- 5. CLEAN UP STAGE FILES (Optional)
-- =============================================================================

USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Remove all files from stage
REMOVE IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || '/');

SELECT 'Stage files removed' AS STATUS;

-- Optionally drop the stage itself
-- DROP STAGE IF EXISTS IDENTIFIER($EXTERNAL_STAGE);

-- =============================================================================
-- 6. DROP FILE FORMATS (Optional)
-- =============================================================================

DROP FILE FORMAT IF EXISTS PARQUET_FORMAT;

SELECT 'File formats dropped' AS STATUS;

-- =============================================================================
-- 7. DROP SCHEMAS (Optional - only if you want to completely remove)
-- =============================================================================

-- Uncomment to drop schemas completely
-- DROP SCHEMA IF EXISTS IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA) CASCADE;
-- DROP SCHEMA IF EXISTS IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA) CASCADE;

-- SELECT 'Schemas dropped' AS STATUS;

-- =============================================================================
-- 8. VERIFICATION
-- =============================================================================

SELECT 'Cleanup verification...' AS STATUS;

-- Check for remaining tasks
SHOW TASKS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

-- Check for remaining streams
SHOW STREAMS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

-- Check for remaining tables
SHOW TABLES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);
SHOW TABLES IN SCHEMA IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA);

-- List files in stage
LIST IDENTIFIER('@' || $EXTERNAL_STAGE || '/') PATTERN = '.*';

SELECT '✅ Cleanup completed!' AS FINAL_STATUS;
SELECT 'All FACTSET ETF Iceberg/Parquet demo objects have been removed' AS MESSAGE;

