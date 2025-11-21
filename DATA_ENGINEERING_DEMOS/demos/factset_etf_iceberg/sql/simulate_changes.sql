-- =============================================================================
-- FACTSET ETF Constituents - Change Data Simulation
-- Simulates INSERT, UPDATE, and DELETE operations for testing CDC pipelines
-- 
-- ⚠️  IMPORTANT: This script CANNOT be used with the FACTSET share!
-- The ETF_DATA.PUBLIC.CONSTITUENTS table is READ-ONLY (it's a share).
-- Changes will come from the FACTSET share provider only.
-- 
-- This script is kept for reference but will NOT work with the hardcoded
-- FACTSET share configuration.
-- =============================================================================

-- Load configuration
USE ROLE IDENTIFIER($ROLE_NAME);
USE WAREHOUSE IDENTIFIER($WAREHOUSE_NAME);
USE DATABASE IDENTIFIER($WORK_DB);
USE SCHEMA IDENTIFIER($WORK_SCHEMA);

SELECT '🔄 Simulating CDC events for pipeline testing...' AS STATUS;

-- =============================================================================
-- SIMULATION 1: INSERT new constituents (ADD operations)
-- =============================================================================

SELECT 'Simulating INSERT operations (new constituents)...' AS STATUS;

-- Note: This assumes you're using a local test table, not the actual share
-- If using the ETF_DATA.PUBLIC.CONSTITUENTS share, you won't be able to INSERT
-- Instead, the share provider will update it and your stream will capture changes

INSERT INTO IDENTIFIER($SOURCE_TABLE) (FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE, SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE)
VALUES
    ('SPY', 'AMD', 'Advanced Micro Devices Inc.', 0.95, 250000, 47500000.00, 'Technology', 'Semiconductors', 'USA', CURRENT_DATE()),
    ('SPY', 'NFLX', 'Netflix Inc.', 0.75, 180000, 54000000.00, 'Communication Services', 'Entertainment', 'USA', CURRENT_DATE()),
    ('SPY', 'DIS', 'The Walt Disney Company', 0.65, 350000, 31500000.00, 'Communication Services', 'Entertainment', 'USA', CURRENT_DATE()),
    ('QQQ', 'AAPL', 'Apple Inc.', 11.50, 2000000, 340000000.00, 'Technology', 'Consumer Electronics', 'USA', CURRENT_DATE()),
    ('QQQ', 'MSFT', 'Microsoft Corporation', 9.25, 1200000, 425000000.00, 'Technology', 'Software', 'USA', CURRENT_DATE());

SELECT 'Added 5 new constituents' AS RESULT;

-- Wait a moment to see the effects
SELECT 'Waiting 5 seconds...' AS STATUS;
CALL SYSTEM$WAIT(5);

-- Check stream for new data
SELECT
    'Stream now has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.CONSTITUENTS_STREAM') AS STREAM_CHECK;

SELECT
    METADATA$ACTION,
    METADATA$ISUPDATE,
    FUND_ID,
    TICKER,
    CONSTITUENT_NAME,
    WEIGHT
FROM CONSTITUENTS_STREAM
WHERE METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE
LIMIT 10;

-- =============================================================================
-- SIMULATION 2: UPDATE existing constituents (UPDATE operations)
-- =============================================================================

SELECT 'Waiting 10 seconds before UPDATE simulation...' AS STATUS;
CALL SYSTEM$WAIT(10);

SELECT 'Simulating UPDATE operations (weight changes)...' AS STATUS;

UPDATE IDENTIFIER($SOURCE_TABLE)
SET
    WEIGHT = WEIGHT * 1.10,  -- Increase weight by 10%
    MARKET_VALUE = MARKET_VALUE * 1.10,
    LOAD_TIMESTAMP = CURRENT_TIMESTAMP()
WHERE TICKER IN ('AAPL', 'MSFT', 'AMZN')
    AND AS_OF_DATE = CURRENT_DATE();

SELECT 'Updated 3 constituents (AAPL, MSFT, AMZN)' AS RESULT;

-- Wait a moment
SELECT 'Waiting 5 seconds...' AS STATUS;
CALL SYSTEM$WAIT(5);

-- Check stream for updates
SELECT
    'Stream now has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.CONSTITUENTS_STREAM') AS STREAM_CHECK;

SELECT
    METADATA$ACTION,
    METADATA$ISUPDATE,
    FUND_ID,
    TICKER,
    WEIGHT,
    MARKET_VALUE
FROM CONSTITUENTS_STREAM
WHERE METADATA$ISUPDATE = TRUE
LIMIT 10;

-- =============================================================================
-- SIMULATION 3: DELETE constituents (DELETE operations)
-- =============================================================================

SELECT 'Waiting 10 seconds before DELETE simulation...' AS STATUS;
CALL SYSTEM$WAIT(10);

SELECT 'Simulating DELETE operations (removing constituents)...' AS STATUS;

DELETE FROM IDENTIFIER($SOURCE_TABLE)
WHERE TICKER IN ('BRK.B', 'JPM')
    AND AS_OF_DATE = CURRENT_DATE();

SELECT 'Deleted 2 constituents (BRK.B, JPM)' AS RESULT;

-- Wait a moment
SELECT 'Waiting 5 seconds...' AS STATUS;
CALL SYSTEM$WAIT(5);

-- Check stream for deletes
SELECT
    'Stream now has data: ' || SYSTEM$STREAM_HAS_DATA($WORK_DB || '.' || $WORK_SCHEMA || '.CONSTITUENTS_STREAM') AS STREAM_CHECK;

SELECT
    METADATA$ACTION,
    METADATA$ISUPDATE,
    FUND_ID,
    TICKER,
    CONSTITUENT_NAME
FROM CONSTITUENTS_STREAM
WHERE METADATA$ACTION = 'DELETE'
LIMIT 10;

-- =============================================================================
-- SIMULATION 4: Bulk changes (mixed operations)
-- =============================================================================

SELECT 'Waiting 10 seconds before bulk changes...' AS STATUS;
CALL SYSTEM$WAIT(10);

SELECT 'Simulating bulk changes (mixed operations)...' AS STATUS;

BEGIN TRANSACTION;

-- Insert new
INSERT INTO IDENTIFIER($SOURCE_TABLE) (FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT, SHARES, MARKET_VALUE, SECTOR, INDUSTRY, COUNTRY, AS_OF_DATE)
VALUES
    ('SPY', 'INTC', 'Intel Corporation', 0.55, 450000, 24750000.00, 'Technology', 'Semiconductors', 'USA', CURRENT_DATE()),
    ('SPY', 'CSCO', 'Cisco Systems Inc.', 0.48, 520000, 24960000.00, 'Technology', 'Networking', 'USA', CURRENT_DATE());

-- Update existing
UPDATE IDENTIFIER($SOURCE_TABLE)
SET
    SECTOR = 'Technology - AI',
    LOAD_TIMESTAMP = CURRENT_TIMESTAMP()
WHERE TICKER IN ('NVDA', 'AMD')
    AND AS_OF_DATE = CURRENT_DATE();

-- Delete some
DELETE FROM IDENTIFIER($SOURCE_TABLE)
WHERE TICKER = 'JNJ'
    AND AS_OF_DATE = CURRENT_DATE();

COMMIT;

SELECT 'Bulk changes committed: 2 inserts, 2 updates, 1 delete' AS RESULT;

-- Wait a moment
SELECT 'Waiting 5 seconds...' AS STATUS;
CALL SYSTEM$WAIT(5);

-- =============================================================================
-- VERIFICATION: Check all CDC types in stream
-- =============================================================================

SELECT '📊 Stream Summary:' AS STATUS;

SELECT
    CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
        ELSE 'UNKNOWN'
    END AS OP_TYPE,
    COUNT(*) AS EVENT_COUNT,
    COUNT(DISTINCT FUND_ID) AS UNIQUE_FUNDS,
    COUNT(DISTINCT TICKER) AS UNIQUE_TICKERS
FROM CONSTITUENTS_STREAM
GROUP BY OP_TYPE
ORDER BY EVENT_COUNT DESC;

-- Show sample of each operation type
SELECT '📋 Sample ADD events:' AS STATUS;
SELECT FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT
FROM CONSTITUENTS_STREAM
WHERE METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE
LIMIT 5;

SELECT '📋 Sample UPDATE events:' AS STATUS;
SELECT FUND_ID, TICKER, CONSTITUENT_NAME, WEIGHT
FROM CONSTITUENTS_STREAM
WHERE METADATA$ISUPDATE = TRUE
LIMIT 5;

SELECT '📋 Sample DELETE events:' AS STATUS;
SELECT FUND_ID, TICKER, CONSTITUENT_NAME
FROM CONSTITUENTS_STREAM
WHERE METADATA$ACTION = 'DELETE'
LIMIT 5;

-- =============================================================================
-- FINAL STATUS
-- =============================================================================

SELECT '✅ Change simulation completed!' AS FINAL_STATUS;
SELECT 'Stream has ' || (SELECT COUNT(*) FROM CONSTITUENTS_STREAM) || ' pending CDC events' AS STREAM_STATUS;
SELECT 'Tasks will process these changes on their next scheduled run' AS NEXT_ACTION;
SELECT 'Or manually execute: EXECUTE TASK <task_name>' AS MANUAL_OPTION;

-- Show when tasks are scheduled to run next
SELECT
    NAME,
    STATE,
    SCHEDULE,
    NEXT_SCHEDULED_TIME
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => CURRENT_TIMESTAMP()
))
WHERE NAME LIKE 'PIPELINE%'
ORDER BY NEXT_SCHEDULED_TIME
LIMIT 10;

