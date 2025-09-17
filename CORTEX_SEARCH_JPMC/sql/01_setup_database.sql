-- =============================================
-- JPMC Cortex Search Lab - Database Setup
-- =============================================
-- This script sets up the foundational database infrastructure
-- for the JPMC Markets Intelligence Cortex Search lab.

-- Set context for execution
USE ROLE ACCOUNTADMIN;

-- =============================================
-- 1. CREATE DATABASE AND SCHEMA
-- =============================================

-- Create the main database for JPMC Markets data
CREATE DATABASE IF NOT EXISTS JPMC_MARKETS
    COMMENT = 'JPMC Markets Intelligence database for Cortex Search lab';

-- Create schema for market intelligence data
CREATE SCHEMA IF NOT EXISTS JPMC_MARKETS.MARKET_INTELLIGENCE
    COMMENT = 'Schema containing market research, trading insights, and economic data';

-- =============================================
-- 2. CREATE WAREHOUSE FOR CORTEX OPERATIONS
-- =============================================

-- Create dedicated warehouse for Cortex Search operations
CREATE WAREHOUSE IF NOT EXISTS CORTEX_WH
    WITH 
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Dedicated warehouse for Cortex Search operations';

-- =============================================
-- 3. CREATE ROLE AND GRANT PERMISSIONS
-- =============================================

-- Create role for Cortex users
CREATE ROLE IF NOT EXISTS CORTEX_USER_ROLE
    COMMENT = 'Role for users accessing Cortex Search services';

-- Grant database and schema usage
GRANT USAGE ON DATABASE JPMC_MARKETS TO ROLE CORTEX_USER_ROLE;
GRANT USAGE ON SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE CORTEX_WH TO ROLE CORTEX_USER_ROLE;

-- Grant table permissions (will be applied after tables are created)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;

-- Grant Cortex permissions
GRANT CREATE CORTEX SEARCH SERVICE ON SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;
GRANT USAGE ON ALL CORTEX SEARCH SERVICES IN SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;
GRANT USAGE ON FUTURE CORTEX SEARCH SERVICES IN SCHEMA JPMC_MARKETS.MARKET_INTELLIGENCE TO ROLE CORTEX_USER_ROLE;

-- =============================================
-- 4. CREATE FILE FORMAT AND STAGE
-- =============================================

-- Switch to the target database and schema
USE DATABASE JPMC_MARKETS;
USE SCHEMA MARKET_INTELLIGENCE;
USE WAREHOUSE CORTEX_WH;

-- Create file format for PDF documents
CREATE FILE FORMAT IF NOT EXISTS pdf_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMMENT = 'File format for loading market document metadata';

-- Create stage for document storage
CREATE STAGE IF NOT EXISTS market_documents_stage
    FILE_FORMAT = pdf_format
    COMMENT = 'Stage for storing market research documents and metadata';

-- =============================================
-- 5. VERIFICATION QUERIES
-- =============================================

-- Verify database and schema creation
SHOW DATABASES LIKE 'JPMC_MARKETS';
SHOW SCHEMAS IN DATABASE JPMC_MARKETS;

-- Verify warehouse creation
SHOW WAREHOUSES LIKE 'CORTEX_WH';

-- Verify role and permissions
SHOW ROLES LIKE 'CORTEX_USER_ROLE';

-- Display setup summary
SELECT 
    'Database Setup Complete' AS status,
    CURRENT_DATABASE() AS current_db,
    CURRENT_SCHEMA() AS current_schema,
    CURRENT_WAREHOUSE() AS current_warehouse,
    CURRENT_ROLE() AS current_role;

-- =============================================
-- SETUP NOTES
-- =============================================
/*
NEXT STEPS:
1. Run script 02_create_tables.sql to create the data tables
2. Run script 03_create_search_services.sql to set up Cortex Search services
3. Load sample data using the provided Python scripts or manual INSERT statements

IMPORTANT:
- Ensure you have ACCOUNTADMIN privileges to run this script
- Update warehouse size (MEDIUM) based on your workload requirements
- Modify role permissions as needed for your organization's security policies
*/ 