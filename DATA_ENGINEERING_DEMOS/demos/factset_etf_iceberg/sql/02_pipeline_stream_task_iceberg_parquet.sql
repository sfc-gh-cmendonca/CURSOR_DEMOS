-- =============================================================================
-- PIPELINE 2: Stream (shared) → Task (attached) → Parquet (CDC Audit Only)
--
-- Pattern: Stream-attached task writes CDC events directly to Parquet
-- Best for: CDC audit trail, compliance, data lake integration
-- 
-- Flow:
--   1. Stream captures CDC from shared table
--   2. Task uses WHEN SYSTEM$STREAM_HAS_DATA to run only when changes exist
--   3. Task exports CDC events to Parquet with op_type (ADD, UPDATE, DELETE)
--   4. Stream is automatically cleared after successful read
--
-- Note: No table is created - purely CDC audit trail
-- Note: For current state, use Pipeline 1 (Iceberg) or query source directly
--
-- Prerequisites: Run config_factset.sql and 00_initialization.sql first
-- Follows PRD specification exactly
-- =============================================================================

-- Context
USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);
USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

SELECT '🔄 Setting up Pipeline 2: Stream → Task (attached) → Parquet CDC Audit Trail' AS STATUS;

-- =============================================================================
-- 1. CREATE STREAM ON SOURCE TABLE
-- =============================================================================

-- Create dedicated stream for Pipeline 2
-- Streams on shared tables are supported - stream lives in your schema, source is shared
CREATE OR REPLACE STREAM pipeline2_constituents_stream
ON TABLE ETF_DATA.PUBLIC.CONSTITUENTS
APPEND_ONLY = FALSE
COMMENT = 'Pipeline 2: CDC stream for regular table + Parquet processing';

SELECT 'Stream pipeline2_constituents_stream created' AS STATUS;

-- =============================================================================
-- 2. CREATE STREAM-ATTACHED TASK: CDC EXPORT TO PARQUET
-- =============================================================================

-- This task exports CDC events to Parquet for audit trail
-- No table is created - purely for CDC audit/compliance
-- Stream is automatically cleared after successful read

CREATE OR REPLACE TASK pipeline2_stream_to_parquet_task
WAREHOUSE = IDENTIFIER($WAREHOUSE_NAME)
SCHEDULE = $REFRESH_SCHEDULE_10MIN
WHEN SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline2_constituents_stream')
COMMENT = 'Pipeline 2: Export CDC events directly to Parquet for audit trail'
AS
    -- =======================================================================
    -- Export CDC rows to Parquet with operation metadata
    -- =======================================================================
    -- Creates audit trail of all changes with op_type and timestamp per PRD
    -- Stream is automatically cleared after successful COPY
    COPY INTO IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || '/pipeline2_cdc/')
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
            -- Compute operation type from stream metadata per PRD
            CASE
                WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
                WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
                WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
                ELSE 'UNKNOWN'
            END AS OP_TYPE,
            CURRENT_TIMESTAMP() AS PROCESSED_TS,
            TO_VARCHAR(CURRENT_TIMESTAMP(), 'YYYY-MM-DD') AS PARTITION_DATE,
            TO_VARCHAR(CURRENT_TIMESTAMP(), 'HH24') AS PARTITION_HOUR,
            METADATA$ROW_ID AS SOURCE_ROW_ID
            FROM pipeline2_constituents_stream
    )
    FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY)
    HEADER = FALSE
    INCLUDE_QUERY_ID = TRUE
    OVERWRITE = FALSE;  -- Append mode for CDC log

SELECT 'Task pipeline2_stream_to_parquet_task created' AS STATUS;

-- =============================================================================
-- 3. ENABLE TASK
-- =============================================================================

ALTER TASK pipeline2_stream_to_parquet_task RESUME;

SELECT '✅ Task pipeline2_stream_to_parquet_task resumed and active' AS STATUS;

-- =============================================================================
-- 4. VERIFICATION
-- =============================================================================

-- Show task details
SHOW TASKS LIKE 'pipeline2%';

-- Check task execution history
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'pipeline2_stream_to_parquet_task',
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;

-- Check stream status
SELECT
    'Stream has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline2_constituents_stream') AS STREAM_STATUS;

-- Check parquet files in stage
LIST IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || '/pipeline2_cdc/');

SELECT '✅ Pipeline 2 setup complete!' AS FINAL_STATUS;
SELECT 'Pattern: Stream → Task (stream-attached) → Parquet (CDC audit only)' AS PATTERN;
SELECT 'Output: Parquet files (complete CDC audit trail with ADD/UPDATE/DELETE)' AS OUTPUT;
SELECT 'Note: No table created - purely CDC export. Use Pipeline 1 for current state.' AS ARCHITECTURE_NOTE;
