-- =============================================================================
-- Data Engineering Demo - Cleanup Script
-- Removes all demo objects
-- 
-- WARNING: This will drop all databases, warehouses, and associated data
-- Run this when you want to completely remove the demo environment
-- =============================================================================

-- Display warning
SELECT '⚠️  WARNING: This will drop all demo objects!' AS WARNING;
SELECT 'Press Ctrl+C now if you want to cancel' AS ACTION;
SELECT 'Waiting 5 seconds...' AS STATUS;

CALL SYSTEM$WAIT(5);

-- =============================================================================
-- 1. DROP WAREHOUSES
-- =============================================================================

SELECT 'Dropping warehouses...' AS STATUS;

DROP WAREHOUSE IF EXISTS DATA_ENG_LOAD_WH;
DROP WAREHOUSE IF EXISTS DATA_ENG_XFORM_WH;
DROP WAREHOUSE IF EXISTS DATA_ENG_ANALYTICS_WH;

SELECT 'Warehouses dropped' AS STATUS;

-- =============================================================================
-- 2. DROP DATABASE (includes all schemas, tables, stages, formats)
-- =============================================================================

SELECT 'Dropping database (includes all schemas and objects)...' AS STATUS;

DROP DATABASE IF EXISTS DATA_ENG_DEMO;

SELECT 'Database dropped' AS STATUS;

-- =============================================================================
-- 3. VERIFICATION
-- =============================================================================

-- Verify cleanup
SHOW DATABASES LIKE 'DATA_ENG_DEMO';
SHOW WAREHOUSES LIKE 'DATA_ENG%';

SELECT '✅ Cleanup complete!' AS STATUS;
SELECT 'All demo objects have been removed' AS RESULT;
