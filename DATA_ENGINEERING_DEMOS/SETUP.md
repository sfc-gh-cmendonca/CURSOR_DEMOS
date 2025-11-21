# Data Engineering Demo - Setup Guide

Pure SQL-based setup for Snowflake Data Engineering demonstrations.

## Quick Start

### Option 1: SnowSQL (Recommended)

```bash
# Run the setup script
snowsql -c your_connection -f sql/00_setup_infrastructure.sql
```

### Option 2: Snowflake Web UI

1. Log into Snowflake UI
2. Open a new SQL worksheet
3. Copy and paste the contents of `sql/00_setup_infrastructure.sql`
4. Execute all

### Option 3: VS Code with Snowflake Extension

1. Install Snowflake extension in VS Code
2. Configure your connection
3. Open `sql/00_setup_infrastructure.sql`
4. Execute the script

## What Gets Created

### Database and Schemas
- **DATA_ENG_DEMO** - Main database
  - **RAW_DATA** - Landing zone for raw data
  - **STAGING** - Staging area for validation
  - **CURATED** - Clean data with business logic
  - **ANALYTICS** - Business-ready analytics
  - **SHARED_DATA** - Data for external sharing

### Warehouses
- **DATA_ENG_LOAD_WH** (MEDIUM) - Data loading operations
- **DATA_ENG_XFORM_WH** (LARGE) - Data transformations
- **DATA_ENG_ANALYTICS_WH** (XSMALL) - Analytics queries

### Stages and File Formats
- **CSV_STAGE** + **CSV_FORMAT** - CSV file ingestion
- **JSON_STAGE** + **JSON_FORMAT** - JSON file ingestion
- **PARQUET_STAGE** + **PARQUET_FORMAT** - Parquet file ingestion
- **GENERAL_STAGE** - General purpose stage
- **PIPE_DELIMITED_FORMAT** - Pipe-delimited files

## Verification

After running the setup, verify with:

```sql
-- Check database and schemas
SHOW DATABASES LIKE 'DATA_ENG_DEMO';
SHOW SCHEMAS IN DATABASE DATA_ENG_DEMO;

-- Check warehouses
SHOW WAREHOUSES LIKE 'DATA_ENG%';

-- Check stages and formats
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA RAW_DATA;
SHOW STAGES;
SHOW FILE FORMATS;
```

## Working with Demos

### FACTSET ETF Constituents Demo

This demo is completely self-contained and has its own setup process.

**Location:** `demos/factset_etf_iceberg/`

**Prerequisites:**
- Infrastructure setup completed (above)
- Access to FACTSET share: `ETF_DATA.PUBLIC.CONSTITUENTS`

**Setup:**
```sql
-- Navigate to demo directory and follow instructions
-- See demos/factset_etf_iceberg/README.md
@demos/factset_etf_iceberg/config_factset.sql
@demos/factset_etf_iceberg/sql/00_initialization.sql
```

## Cleanup

To remove all demo objects:

```sql
-- WARNING: This drops everything!
@sql/99_cleanup.sql
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

## Configuration

### Custom Database Name

Edit `sql/00_setup_infrastructure.sql` and change:

```sql
CREATE DATABASE IF NOT EXISTS YOUR_DB_NAME
```

### Custom Warehouse Sizes

Edit warehouse definitions in `sql/00_setup_infrastructure.sql`:

```sql
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_LOAD_WH
    WAREHOUSE_SIZE = 'MEDIUM'  -- Change to SMALL, LARGE, etc.
```

## Troubleshooting

### Permission Issues

**Problem:** `Insufficient privileges to operate on database`

**Solution:** Use ACCOUNTADMIN role or grant necessary privileges:
```sql
USE ROLE ACCOUNTADMIN;
-- Or grant privileges to your role
GRANT CREATE DATABASE ON ACCOUNT TO ROLE YOUR_ROLE;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE YOUR_ROLE;
```

### Object Already Exists

**Problem:** Objects already exist from previous setup

**Solution:** Either:
1. Run cleanup script first: `@sql/99_cleanup.sql`
2. Use `CREATE OR REPLACE` statements (already in setup script)

### Warehouse Suspended

**Problem:** Warehouse is suspended when trying to query

**Solution:** Warehouses auto-suspend. They'll auto-resume, or manually resume:
```sql
ALTER WAREHOUSE DATA_ENG_ANALYTICS_WH RESUME;
```

## Next Steps

1. ✅ **Verify Setup** - Run verification queries above
2. 📊 **Explore Demos** - See `demos/factset_etf_iceberg/`
3. 🔧 **Customize** - Modify SQL scripts for your environment
4. 🚀 **Build** - Create your own demos using this infrastructure

## Architecture

```
DATA_ENG_DEMO (Database)
├── RAW_DATA (Schema)
│   ├── Stages: CSV, JSON, Parquet, General
│   └── File Formats: CSV, JSON, Parquet, Pipe-Delimited
├── STAGING (Schema)
├── CURATED (Schema)
├── ANALYTICS (Schema)
└── SHARED_DATA (Schema)

Warehouses:
├── DATA_ENG_LOAD_WH (MEDIUM)
├── DATA_ENG_XFORM_WH (LARGE)
└── DATA_ENG_ANALYTICS_WH (XSMALL)
```

## Support Resources

- **Snowflake Documentation:** https://docs.snowflake.com
- **Project README:** `README.md`
- **FACTSET Demo:** `demos/factset_etf_iceberg/README.md`
- **Architecture Guide:** `docs/architecture.md`

---

**Version:** 3.0 (SQL-Only)  
**Last Updated:** 2025-11-18

