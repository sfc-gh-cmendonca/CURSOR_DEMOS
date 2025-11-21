-- =============================================================================
-- Data Engineering Demo - Infrastructure Setup
-- Creates database, schemas, warehouses, stages, and file formats
-- 
-- This is a SQL-only setup - no Python required
-- Run this script to set up the basic infrastructure
-- =============================================================================

-- =============================================================================
-- 1. CREATE DATABASE AND SCHEMAS
-- =============================================================================

-- Create main database
CREATE DATABASE IF NOT EXISTS DATA_ENG_DEMO
    COMMENT = 'Data Engineering Demo: ETL/ELT, Data Sharing, Dynamic Tables';

-- Create schemas
CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.RAW_DATA
    COMMENT = 'Landing zone for raw data ingestion';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.STAGING
    COMMENT = 'Staging area for data validation';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.CURATED
    COMMENT = 'Curated clean data with business logic';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.ANALYTICS
    COMMENT = 'Business-ready analytics tables';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.SHARED_DATA
    COMMENT = 'Curated data for external sharing';

SELECT 'Database and schemas created successfully' AS STATUS;

-- =============================================================================
-- 2. CREATE WAREHOUSES
-- =============================================================================

-- Loading warehouse (MEDIUM)
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_LOAD_WH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Data loading operations';

-- Transformation warehouse (LARGE)
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_XFORM_WH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Data transformation operations';

-- Analytics warehouse (XSMALL)
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_ANALYTICS_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Analytics queries';

SELECT 'Warehouses created successfully' AS STATUS;

-- =============================================================================
-- 3. CREATE STAGES AND FILE FORMATS
-- =============================================================================

USE DATABASE DATA_ENG_DEMO;
USE SCHEMA RAW_DATA;

-- CSV Stage and Format
CREATE STAGE IF NOT EXISTS CSV_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Internal stage for CSV file ingestion';

CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMPRESSION = AUTO
    COMMENT = 'CSV file format with header';

-- JSON Stage and Format
CREATE STAGE IF NOT EXISTS JSON_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Internal stage for JSON file ingestion';

CREATE FILE FORMAT IF NOT EXISTS JSON_FORMAT
    TYPE = 'JSON'
    COMPRESSION = AUTO
    STRIP_OUTER_ARRAY = TRUE
    COMMENT = 'JSON file format';

-- Parquet Stage and Format
CREATE STAGE IF NOT EXISTS PARQUET_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Internal stage for Parquet file ingestion';

CREATE FILE FORMAT IF NOT EXISTS PARQUET_FORMAT
    TYPE = 'PARQUET'
    COMPRESSION = AUTO
    BINARY_AS_TEXT = FALSE
    COMMENT = 'Parquet file format';

-- General Purpose Stage
CREATE STAGE IF NOT EXISTS GENERAL_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'General purpose internal stage';

-- Pipe-Delimited Format
CREATE FILE FORMAT IF NOT EXISTS PIPE_DELIMITED_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = '|'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMPRESSION = AUTO
    COMMENT = 'Pipe-delimited file format';

SELECT 'Stages and file formats created successfully' AS STATUS;

-- =============================================================================
-- 4. VERIFICATION
-- =============================================================================

-- Show created objects
SHOW DATABASES LIKE 'DATA_ENG_DEMO';
SHOW SCHEMAS IN DATABASE DATA_ENG_DEMO;
SHOW WAREHOUSES LIKE 'DATA_ENG%';
SHOW STAGES IN SCHEMA DATA_ENG_DEMO.RAW_DATA;
SHOW FILE FORMATS IN SCHEMA DATA_ENG_DEMO.RAW_DATA;

-- Summary
SELECT 'Infrastructure setup complete!' AS STATUS;
SELECT 'Database: DATA_ENG_DEMO' AS COMPONENT;
SELECT '5 schemas created' AS SCHEMAS;
SELECT '3 warehouses created' AS WAREHOUSES;
SELECT '4 stages + 5 file formats created' AS STAGES_FORMATS;
SELECT 'Next: Run individual demos (see demos/factset_etf_iceberg/)' AS NEXT_STEPS;

