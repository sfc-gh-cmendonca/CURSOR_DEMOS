-- =============================================================================
-- FACTSET ETF Iceberg/Parquet ETL - Master Setup Script
-- Runs all initialization and pipeline setup scripts in sequence
-- 
-- This script sets up all 4 pipeline patterns for comparison
-- Each pattern is independent but they all share the same source stream
-- =============================================================================

SELECT '╔══════════════════════════════════════════════════════════════════╗' AS BANNER;
SELECT '║  FACTSET ETF Constituents - Iceberg/Parquet ETL                 ║' AS BANNER;
SELECT '║  Master Setup: All 4 Pipeline Patterns                          ║' AS BANNER;
SELECT '╚══════════════════════════════════════════════════════════════════╝' AS BANNER;

-- =============================================================================
-- STEP 0: Load Configuration
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 0: Loading Configuration...' AS STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

-- Load configuration variables
!source config_factset.sql

-- =============================================================================
-- STEP 1: Initialize Environment
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 1: Initializing Environment...' AS STATUS;
SELECT '  - Creating database and schemas' AS DETAIL;
SELECT '  - Creating source table with sample data' AS DETAIL;
SELECT '  - Setting up stages and Iceberg table' AS DETAIL;
SELECT '  - Creating stream for CDC' AS DETAIL;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

!source sql/00_initialization.sql

CALL SYSTEM$WAIT(3);

-- =============================================================================
-- STEP 2: Set Up Pipeline 1 (Stream → DT → Task → Iceberg)
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 2: Setting Up Pipeline 1 (DT → Task → Iceberg)...' AS STATUS;
SELECT '  Pattern: Dynamic Table computes state, Task performs MERGE' AS DETAIL;
SELECT '  Components: Stream, Dynamic Table, Task' AS DETAIL;
SELECT '  Output: Iceberg table' AS DETAIL;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

!source sql/01_pipeline_dt_task_iceberg.sql

CALL SYSTEM$WAIT(2);

-- =============================================================================
-- STEP 3: Set Up Pipeline 2 (Stream → Task → Iceberg)
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 3: Setting Up Pipeline 2 (Stream → Task → Iceberg)...' AS STATUS;
SELECT '  Pattern: Direct stream processing with task' AS DETAIL;
SELECT '  Components: Stream, Stream-attached Task' AS DETAIL;
SELECT '  Output: Iceberg table' AS DETAIL;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

!source sql/02_pipeline_stream_task_iceberg.sql

CALL SYSTEM$WAIT(2);

-- =============================================================================
-- STEP 4: Set Up Pipeline 3 (Stream → DT → Task → Iceberg + Parquet)
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 4: Setting Up Pipeline 3 (DT → Task → Iceberg + Parquet)...' AS STATUS;
SELECT '  Pattern: DT with CDC metadata, Task merges and exports' AS DETAIL;
SELECT '  Components: Stream, 2× Dynamic Tables, Task' AS DETAIL;
SELECT '  Output: Iceberg table + Parquet files' AS DETAIL;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

!source sql/03_pipeline_dt_task_iceberg_parquet.sql

CALL SYSTEM$WAIT(2);

-- =============================================================================
-- STEP 5: Set Up Pipeline 4 (Stream → Task → Iceberg + Parquet)
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'STEP 5: Setting Up Pipeline 4 (Stream → Task → Iceberg + Parquet)...' AS STATUS;
SELECT '  Pattern: All-in-one stream-attached task' AS DETAIL;
SELECT '  Components: Stream, Stream-attached Task' AS DETAIL;
SELECT '  Output: Iceberg table + Parquet files + View' AS DETAIL;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

!source sql/04_pipeline_stream_task_iceberg_parquet.sql

CALL SYSTEM$WAIT(2);

-- =============================================================================
-- VERIFICATION & SUMMARY
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT 'VERIFYING SETUP...' AS STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

-- Summary of created objects
SELECT '📊 SETUP SUMMARY:' AS INFO;

SELECT '  Databases:' AS CATEGORY;
SHOW DATABASES LIKE $WORK_DB;

SELECT '  Schemas:' AS CATEGORY;
SHOW SCHEMAS IN DATABASE IDENTIFIER($WORK_DB);

SELECT '  Tables:' AS CATEGORY;
SHOW TABLES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

SELECT '  Streams:' AS CATEGORY;
SHOW STREAMS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

SELECT '  Dynamic Tables:' AS CATEGORY;
SHOW DYNAMIC TABLES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

SELECT '  Tasks:' AS CATEGORY;
SHOW TASKS IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

SELECT '  Stages:' AS CATEGORY;
SHOW STAGES IN SCHEMA IDENTIFIER($WORK_DB || '.' || $WORK_SCHEMA);

-- Task status
SELECT '📋 TASK STATUS:' AS INFO;
SELECT 
    NAME,
    STATE,
    SCHEDULE,
    WAREHOUSE,
    COMMENT
FROM (
    SELECT * FROM TABLE(INFORMATION_SCHEMA.TASKS)
    WHERE TASK_SCHEMA = $WORK_SCHEMA
        AND NAME LIKE 'PIPELINE%'
)
ORDER BY NAME;

-- Stream status
SELECT '📡 STREAM STATUS:' AS INFO;
SELECT
    'Stream has data: ' || 
    SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.CONSTITUENTS_STREAM') AS STATUS;

-- Data counts
SELECT '📈 DATA SUMMARY:' AS INFO;
SELECT
    'ETF_CONSTITUENTS_SOURCE' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    COUNT(DISTINCT FUND_ID) AS UNIQUE_FUNDS,
    COUNT(DISTINCT TICKER) AS UNIQUE_TICKERS
FROM ETF_CONSTITUENTS_SOURCE
UNION ALL
SELECT
    'CONSTITUENTS_BASE',
    COUNT(*),
    COUNT(DISTINCT FUND_ID),
    COUNT(DISTINCT TICKER)
FROM CONSTITUENTS_BASE
UNION ALL
SELECT
    'CONSTITUENTS_ICEBERG',
    COUNT(*),
    COUNT(DISTINCT FUND_ID),
    COUNT(DISTINCT TICKER)
FROM IDENTIFIER($ICEBERG_DB || '.' || $ICEBERG_SCHEMA || '.' || $ICEBERG_TABLE);

-- =============================================================================
-- FINAL STATUS
-- =============================================================================

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;
SELECT '✅ SETUP COMPLETE!' AS FINAL_STATUS;
SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

SELECT 'All 4 pipeline patterns are configured and ready to use!' AS MESSAGE;
SELECT '' AS BLANK;

SELECT '📌 NEXT STEPS:' AS SECTION;
SELECT '  1. Simulate changes: Run sql/simulate_changes.sql' AS STEP1;
SELECT '  2. Monitor tasks: Check TASK_HISTORY for executions' AS STEP2;
SELECT '  3. Verify Iceberg: Query CONSTITUENTS_ICEBERG table' AS STEP3;
SELECT '  4. Check Parquet: List @FACTSET_ETF_STAGE/REPORTING/' AS STEP4;
SELECT '' AS BLANK;

SELECT '📖 DOCUMENTATION:' AS SECTION;
SELECT '  - README.md - Overview and quick start' AS DOC1;
SELECT '  - docs/pipeline_comparison.md - Pattern comparison' AS DOC2;
SELECT '  - docs/demo_script.md - Presentation guide' AS DOC3;
SELECT '' AS BLANK;

SELECT '🔗 USEFUL COMMANDS:' AS SECTION;
SELECT '  -- Manually execute a task:' AS CMD;
SELECT '  EXECUTE TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;' AS EXAMPLE1;
SELECT '  -- Check task history:' AS CMD2;
SELECT '  SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(...));' AS EXAMPLE2;
SELECT '  -- View stream contents:' AS CMD3;
SELECT '  SELECT * FROM CONSTITUENTS_STREAM LIMIT 10;' AS EXAMPLE3;

SELECT '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' AS SEPARATOR;

