# Data Engineering Demo - Setup Guide

Complete guide for setting up and configuring the Snowflake Data Engineering Demo infrastructure.

## Prerequisites

### 1. Snowflake Account
- Active Snowflake account
- ACCOUNTADMIN role access (for creating databases, warehouses)
- Sufficient credits for demo execution

### 2. Local Environment
- Python 3.8 or higher
- pip package manager
- Terminal/command line access

### 3. Snowflake CLI Configuration
- SnowSQL installed (optional but recommended)
- Snowflake connections.toml configured

## Installation Steps

### Step 1: Clone or Download Project

```bash
cd /path/to/your/workspace
# If in a Git repository
git pull origin main

# Navigate to demo directory
cd DATA_ENGINEERING_DEMOS
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Snowflake Connection

Create or update `~/.snowflake/connections.toml`:

```toml
[demo_connection]
account = "your-account-identifier"
user = "your-username"
password = "your-password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"  # Temporary - demo creates its own
database = "DEMO"         # Temporary - demo creates its own
schema = "PUBLIC"         # Temporary - demo creates its own
```

**Alternative: Environment Variables**

```bash
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"
```

### Step 4: Verify Connection

```bash
python -c "from src.utils.snowpark_session import get_snowpark_session; s = get_snowpark_session('demo_connection'); print('✅ Connection successful'); s.close()"
```

## Running the Setup

### Quick Setup (Recommended)

```bash
python setup.py --connection_name demo_connection --mode full
```

This will:
1. Create database and schemas
2. Set up warehouses
3. Configure stages and file formats
4. Display summary

**Expected Output:**
```
🚀 Starting Data Engineering Demo Setup
================================================================================
⏱️ Starting: Database and Schema Setup
✅ Database created: DATA_ENG_DEMO
✅ Schema created: RAW_DATA
✅ Schema created: CURATED
✅ Schema created: ANALYTICS
✅ Completed in X.XX seconds
...
✅ Setup Complete!
```

### Alternative: Step-by-Step Setup

If you prefer to run individual steps:

```bash
# 1. Set up database and schemas
python -c "from setup import setup_database_and_schemas; from src.utils.snowpark_session import get_snowpark_session; setup_database_and_schemas(get_snowpark_session('demo_connection'))"

# 2. Set up warehouses
python -c "from setup import setup_warehouses; from src.utils.snowpark_session import get_snowpark_session; setup_warehouses(get_snowpark_session('demo_connection'))"

# 3. Set up pipeline infrastructure
python -c "from setup import setup_pipeline_infrastructure; from src.utils.snowpark_session import get_snowpark_session; setup_pipeline_infrastructure(get_snowpark_session('demo_connection'))"
```

### SQL-Only Setup (No Python)

If you prefer SQL only:

```sql
-- Create database and schemas
CREATE DATABASE IF NOT EXISTS DATA_ENG_DEMO;

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.RAW_DATA
    COMMENT = 'Landing zone for raw data ingestion';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.CURATED
    COMMENT = 'Transformed and enriched data layer';

CREATE SCHEMA IF NOT EXISTS DATA_ENG_DEMO.ANALYTICS
    COMMENT = 'Analytics-ready aggregated views';

-- Create warehouses
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_LOAD_WH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_XFORM_WH
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_ANALYTICS_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Create stages
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA RAW_DATA;

CREATE STAGE IF NOT EXISTS CSV_STAGE
    DIRECTORY = (ENABLE = TRUE);

CREATE STAGE IF NOT EXISTS JSON_STAGE
    DIRECTORY = (ENABLE = TRUE);

CREATE STAGE IF NOT EXISTS PARQUET_STAGE
    DIRECTORY = (ENABLE = TRUE);

CREATE STAGE IF NOT EXISTS GENERAL_STAGE
    DIRECTORY = (ENABLE = TRUE);

-- Create file formats
CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1;

CREATE FILE FORMAT IF NOT EXISTS JSON_FORMAT
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE;

CREATE FILE FORMAT IF NOT EXISTS PARQUET_FORMAT
    TYPE = 'PARQUET';

CREATE FILE FORMAT IF NOT EXISTS PIPE_DELIMITED_FORMAT
    TYPE = 'CSV'
    FIELD_DELIMITER = '|'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1;
```

## Configuration Customization

Edit `config.py` to customize:

```python
# Database Configuration
DATABASE = "DATA_ENG_DEMO"  # Change database name
SCHEMA_RAW = "RAW_DATA"
SCHEMA_CURATED = "CURATED"
SCHEMA_ANALYTICS = "ANALYTICS"

# Warehouse Configuration
WAREHOUSE_LOAD = "DATA_ENG_LOAD_WH"
WAREHOUSE_TRANSFORM = "DATA_ENG_XFORM_WH"
WAREHOUSE_ANALYTICS = "DATA_ENG_ANALYTICS_WH"

# Warehouse Sizes
WAREHOUSE_SIZE_LOAD = "MEDIUM"       # Change warehouse sizes
WAREHOUSE_SIZE_TRANSFORM = "LARGE"
WAREHOUSE_SIZE_ANALYTICS = "XSMALL"
```

## Verification

### Check Database and Schemas

```sql
USE ROLE ACCOUNTADMIN;

-- Verify database
SHOW DATABASES LIKE 'DATA_ENG_DEMO';

-- Verify schemas
SHOW SCHEMAS IN DATABASE DATA_ENG_DEMO;
```

### Check Warehouses

```sql
-- Verify warehouses
SHOW WAREHOUSES LIKE 'DATA_ENG%';

-- Check warehouse configuration
DESCRIBE WAREHOUSE DATA_ENG_LOAD_WH;
```

### Check Stages and File Formats

```sql
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA RAW_DATA;

-- Verify stages
SHOW STAGES;

-- Verify file formats
SHOW FILE FORMATS;
```

### Test Query Execution

```sql
-- Use analytics warehouse
USE WAREHOUSE DATA_ENG_ANALYTICS_WH;

-- Simple test query
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE();
```

## Working with Demos

### FACTSET ETF Constituents Demo

**Note:** This demo is self-contained and has its own setup process.

**Prerequisites:**
- Infrastructure setup completed (above)
- Access to FACTSET share: `ETF_DATA.PUBLIC.CONSTITUENTS`

**Setup:**
```bash
cd demos/factset_etf_iceberg

# Follow the demo's README
cat README.md

# Quick start (10 minutes)
cat QUICK_START.md
```

**Configuration:**
```sql
-- Run configuration
@demos/factset_etf_iceberg/config_factset.sql

-- Run initialization
@demos/factset_etf_iceberg/sql/00_initialization.sql
```

See `demos/factset_etf_iceberg/README.md` for complete documentation.

## Cleanup

### Remove All Objects

```bash
python setup.py --connection_name demo_connection --mode cleanup
```

Or manually:

```sql
-- Drop warehouses
DROP WAREHOUSE IF EXISTS DATA_ENG_LOAD_WH;
DROP WAREHOUSE IF EXISTS DATA_ENG_XFORM_WH;
DROP WAREHOUSE IF EXISTS DATA_ENG_ANALYTICS_WH;

-- Drop database (includes all schemas)
DROP DATABASE IF EXISTS DATA_ENG_DEMO;
```

### Cleanup FACTSET Demo

```sql
-- From FACTSET demo directory
@demos/factset_etf_iceberg/sql/99_cleanup.sql
```

## Troubleshooting

### Connection Issues

**Problem:** `SnowflakeLoginException: Incorrect username or password`

**Solution:**
1. Verify credentials in connections.toml
2. Check account identifier format (should be `account.region.cloud`)
3. Ensure password is correct
4. Try authenticating manually with SnowSQL

**Problem:** `ProgrammingError: 002003: Sql compilation error: Object does not exist`

**Solution:**
1. Verify database and schema exist
2. Check role has access to objects
3. Use fully qualified names (DATABASE.SCHEMA.OBJECT)

### Permission Issues

**Problem:** `Insufficient privileges to operate on database`

**Solution:**
1. Use ACCOUNTADMIN role for setup
2. Grant necessary privileges:
```sql
GRANT CREATE DATABASE ON ACCOUNT TO ROLE YOUR_ROLE;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE YOUR_ROLE;
```

### Python Issues

**Problem:** `ModuleNotFoundError: No module named 'snowflake'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** `ImportError: cannot import name 'Session'`

**Solution:**
```bash
pip install --upgrade snowflake-snowpark-python
```

### Warehouse Issues

**Problem:** Warehouse suspended, queries fail

**Solution:**
Warehouses auto-suspend. Use `AUTO_RESUME = TRUE` (already configured) or manually resume:
```sql
ALTER WAREHOUSE DATA_ENG_ANALYTICS_WH RESUME;
```

## Advanced Configuration

### Multi-Environment Setup

Create separate configurations for dev/test/prod:

```python
# config_dev.py
DATABASE = "DATA_ENG_DEMO_DEV"
WAREHOUSE_LOAD = "DATA_ENG_LOAD_WH_DEV"
# ... other settings

# config_prod.py
DATABASE = "DATA_ENG_DEMO_PROD"
WAREHOUSE_LOAD = "DATA_ENG_LOAD_WH_PROD"
# ... other settings
```

### Resource Monitors

Set up resource monitors to control costs:

```sql
CREATE RESOURCE MONITOR DATA_ENG_DEMO_MONITOR
    WITH CREDIT_QUOTA = 100
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS 
        ON 75 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

-- Assign to warehouses
ALTER WAREHOUSE DATA_ENG_LOAD_WH SET RESOURCE_MONITOR = DATA_ENG_DEMO_MONITOR;
ALTER WAREHOUSE DATA_ENG_XFORM_WH SET RESOURCE_MONITOR = DATA_ENG_DEMO_MONITOR;
ALTER WAREHOUSE DATA_ENG_ANALYTICS_WH SET RESOURCE_MONITOR = DATA_ENG_DEMO_MONITOR;
```

### Role-Based Access Control

Create custom roles for different user types:

```sql
-- Create roles
CREATE ROLE IF NOT EXISTS DATA_ENG_ADMIN;
CREATE ROLE IF NOT EXISTS DATA_ENG_DEVELOPER;
CREATE ROLE IF NOT EXISTS DATA_ENG_ANALYST;

-- Grant database access
GRANT USAGE ON DATABASE DATA_ENG_DEMO TO ROLE DATA_ENG_ADMIN;
GRANT USAGE ON DATABASE DATA_ENG_DEMO TO ROLE DATA_ENG_DEVELOPER;
GRANT USAGE ON DATABASE DATA_ENG_DEMO TO ROLE DATA_ENG_ANALYST;

-- Grant schema access
GRANT ALL ON SCHEMA DATA_ENG_DEMO.RAW_DATA TO ROLE DATA_ENG_ADMIN;
GRANT USAGE ON SCHEMA DATA_ENG_DEMO.RAW_DATA TO ROLE DATA_ENG_DEVELOPER;
GRANT USAGE ON SCHEMA DATA_ENG_DEMO.ANALYTICS TO ROLE DATA_ENG_ANALYST;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE DATA_ENG_ANALYTICS_WH TO ROLE DATA_ENG_ANALYST;
GRANT USAGE ON WAREHOUSE DATA_ENG_XFORM_WH TO ROLE DATA_ENG_DEVELOPER;
GRANT ALL ON WAREHOUSE DATA_ENG_LOAD_WH TO ROLE DATA_ENG_ADMIN;
```

## Next Steps

1. **Verify Setup**: Run verification queries above
2. **Explore Demos**: Navigate to `demos/factset_etf_iceberg/`
3. **Customize**: Modify config.py for your environment
4. **Build**: Create your own demos using this infrastructure

## Support Resources

- **Snowflake Documentation:** https://docs.snowflake.com
- **Snowpark Python Guide:** https://docs.snowflake.com/en/developer-guide/snowpark/python/index
- **Demo Repo:** Check README.md in project root
- **FACTSET Demo:** See `demos/factset_etf_iceberg/README.md`

---

**Last Updated:** 2025-11-18  
**Version:** 2.0 (Infrastructure Setup)
