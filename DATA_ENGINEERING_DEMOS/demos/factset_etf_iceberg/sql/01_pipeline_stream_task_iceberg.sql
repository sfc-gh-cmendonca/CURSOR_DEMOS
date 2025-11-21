-- =============================================================================
-- PIPELINE 1: Stream (shared) → Task (attached) → Iceberg MERGE
--
-- Pattern: Single stream-attached task consumes stream and performs deletes then upserts
-- Best for: Simplicity - one task handles everything
-- 
-- Flow:
--   1. Stream captures CDC from shared table
--   2. Task uses WHEN SYSTEM$STREAM_HAS_DATA to run only when changes exist
--   3. Task processes DELETEs first, then upserts (INSERT + UPDATE)
--
-- Prerequisites: Run config_factset.sql and 00_initialization.sql first
-- Follows PRD specification exactly
-- =============================================================================

-- Context
USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);
USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

SELECT '🔄 Setting up Pipeline 1: Stream → Task (attached) → Iceberg' AS STATUS;

-- =============================================================================
-- 1. CREATE STREAM ON SOURCE TABLE
-- =============================================================================

-- Create dedicated stream for Pipeline 1
-- Streams on shared tables are supported - stream lives in your schema, source is shared
CREATE OR REPLACE STREAM pipeline1_constituents_stream
ON TABLE ETF_DATA.PUBLIC.CONSTITUENTS
APPEND_ONLY = FALSE
COMMENT = 'Pipeline 1: CDC stream for Iceberg processing';

SELECT 'Stream pipeline1_constituents_stream created' AS STATUS;

-- =============================================================================
-- 2. CREATE STREAM-ATTACHED TASK
-- =============================================================================

-- Single task consumes stream and performs MERGE with explicit CDC handling
-- Uses WHEN SYSTEM$STREAM_HAS_DATA for stream-attached behavior per PRD
CREATE OR REPLACE TASK pipeline1_stream_to_iceberg_merge_task
WAREHOUSE = IDENTIFIER($WAREHOUSE_NAME)
SCHEDULE = $REFRESH_SCHEDULE_10MIN
WHEN SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline1_constituents_stream')
COMMENT = 'Pipeline 1: Direct stream to Iceberg MERGE with CDC'
AS
BEGIN
    -- =======================================================================
    -- STEP 1: Process DELETEs first (per PRD requirement)
    -- =======================================================================
    DELETE FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE) AS t
    USING (
        SELECT DISTINCT
            FUND_ID,
            TICKER,
            AS_OF_DATE
        FROM pipeline1_constituents_stream
        WHERE METADATA$ACTION = 'DELETE'
    ) AS d
    WHERE t.FUND_ID = d.FUND_ID
        AND t.TICKER = d.TICKER
        AND t.AS_OF_DATE = d.AS_OF_DATE;

    -- =======================================================================
    -- STEP 2: Process upserts (INSERT and UPDATE)
    -- =======================================================================
    MERGE INTO IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE) AS t
    USING (
        -- Explicit column list per PRD (no SELECT *)
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
        FROM pipeline1_constituents_stream
        WHERE METADATA$ACTION = 'INSERT'
        -- Deduplicate if multiple changes to same key
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

SELECT 'Task pipeline1_stream_to_iceberg_merge_task created' AS STATUS;

-- =============================================================================
-- ENABLE TASK
-- =============================================================================

ALTER TASK pipeline1_stream_to_iceberg_merge_task RESUME;

SELECT '✅ Task pipeline1_stream_to_iceberg_merge_task resumed and active' AS STATUS;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Show task details
SHOW TASKS LIKE 'pipeline1%';

-- Check task execution history
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'pipeline1_stream_to_iceberg_merge_task',
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;

-- Check stream status
SELECT
    'Stream has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.pipeline1_constituents_stream') AS STREAM_STATUS;

-- Check Iceberg table row count
SELECT
    'Iceberg table row count: ' || COUNT(*) AS ICEBERG_STATUS
FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE);

SELECT '✅ Pipeline 1 setup complete!' AS FINAL_STATUS;
SELECT 'Pattern: Stream → Task (stream-attached with WHEN clause) → Iceberg MERGE' AS PATTERN;
SELECT 'Next: Run 02_pipeline_stream_task_iceberg_parquet.sql for Pipeline 2' AS NEXT_STEPS;
