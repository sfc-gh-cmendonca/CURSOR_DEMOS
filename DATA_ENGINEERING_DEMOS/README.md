# Snowflake Data Engineering Demo

A comprehensive **SQL-only** demonstration of Snowflake's data engineering capabilities, showcasing:
1. **Infrastructure Setup** - Database, schemas, warehouses, stages, file formats
2. **CDC Pipelines** - Change Data Capture with Streams, Dynamic Tables, and Tasks  
3. **Data Sharing** - Real production data from FACTSET marketplace
4. **Iceberg Tables** - ACID compliance and time travel

**No Python required! Pure SQL implementation.**

## 🎯 Demo Overview

This demo provides infrastructure setup and a production-ready CDC demo using FACTSET ETF data.

### Main Components

**Infrastructure Setup** (5 minutes)
- Creates database, schemas, warehouses
- Sets up stages and file formats
- Pure SQL - no dependencies

**FACTSET ETF Constituents Demo** (30-45 minutes)
- 4 different CDC pipeline patterns
- Streams on shared tables
- Dynamic Tables for transformations
- Tasks for orchestration
- Iceberg tables for current state
- Parquet exports for audit trail

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Infrastructure (SQL-Only)        │
├─────────────────────────────────────┤
│  Database: DATA_ENG_DEMO             │
│  Schemas: RAW_DATA, CURATED,        │
│           ANALYTICS, SHARED_DATA     │
│  Warehouses: LOAD, TRANSFORM,       │
│             ANALYTICS               │
│  Stages + File Formats              │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  FACTSET ETF CDC Demo                │
├─────────────────────────────────────┤
│  Source: ETF_DATA.PUBLIC.CONSTITUENTS│
│  Stream captures CDC                 │
│  4 Pipeline Patterns:                │
│    1. Stream→DT→Task→Iceberg        │
│    2. Stream→Task→Iceberg           │
│    3. Stream→DT→Task→Iceberg+Parquet│
│    4. Stream→Task→Iceberg+Parquet   │
│  Output: Iceberg + Parquet           │
└─────────────────────────────────────┘
```

## 📋 Prerequisites

1. **Snowflake Account** with ACCOUNTADMIN privileges
2. **SnowSQL** or Snowflake Web UI access
3. **FACTSET Share** (for ETF demo): `ETF_DATA.PUBLIC.CONSTITUENTS`

**No Python required!**

## 🚀 Quick Start

### Step 1: Infrastructure Setup

**Option A: Single SQL Script (Recommended)**
```bash
snowsql -c your_connection -f sql/00_setup_infrastructure.sql
```

**Option B: Snowflake Web UI**
1. Log into Snowflake
2. Open SQL worksheet
3. Copy/paste `sql/00_setup_infrastructure.sql`
4. Execute all statements

**Option C: Step-by-step**
```bash
snowsql -c your_connection -f sql/01_database_setup.sql
snowsql -c your_connection -f sql/02_file_formats.sql
snowsql -c your_connection -f sql/03_stages.sql
```

### Step 2: Verify Setup

```sql
USE DATABASE DATA_ENG_DEMO;
SHOW SCHEMAS;
SHOW WAREHOUSES LIKE 'DATA_ENG%';
SHOW STAGES IN SCHEMA RAW_DATA;
SHOW FILE FORMATS IN SCHEMA RAW_DATA;
```

### Step 3: Run FACTSET ETF Demo

See **[demos/factset_etf_iceberg/README.md](demos/factset_etf_iceberg/README.md)** for complete demo instructions.

```bash
cd demos/factset_etf_iceberg
# Follow README.md or QUICK_START.md
```

## 📁 Project Structure

```
DATA_ENGINEERING_DEMOS/
├── README.md                        # This file
├── SETUP.md                         # Detailed setup guide
├── sql/                             # Infrastructure SQL scripts
│   ├── 00_setup_infrastructure.sql # Complete setup (recommended)
│   ├── 01_database_setup.sql       # Database and schemas
│   ├── 02_file_formats.sql         # File formats
│   ├── 03_stages.sql               # Stages
│   ├── 04_dynamic_tables.sql       # Dynamic tables
│   ├── 05_materialized_views.sql   # Materialized views
│   ├── 06_data_shares.sql          # Data shares
│   └── 99_cleanup.sql              # Cleanup script
├── docs/                            # Documentation
│   ├── architecture.md             # Technical architecture
│   ├── demo_script.md              # Presentation guide
│   └── setup_guide.md              # Setup instructions
├── demos/                           # Self-contained demos
│   └── factset_etf_iceberg/        # FACTSET ETF CDC demo
│       ├── README.md                # Demo overview
│       ├── QUICK_START.md           # 10-minute guide
│       ├── config_factset.sql       # Configuration
│       ├── sql/                     # Pipeline SQL scripts
│       │   ├── 00_initialization.sql
│       │   ├── 01-04_pipeline_*.sql
│       │   └── 99_cleanup.sql
│       └── docs/                    # Demo documentation
└── requirements.txt                 # No dependencies needed!
```

## 🏗️ What Gets Created

### Database and Schemas
- **DATA_ENG_DEMO** - Main database
  - **RAW_DATA** - Landing zone for raw data ingestion
  - **STAGING** - Staging area for data validation
  - **CURATED** - Cleaned data with business logic
  - **ANALYTICS** - Business-ready analytics tables
  - **SHARED_DATA** - Data for external sharing

### Warehouses
- **DATA_ENG_LOAD_WH** (MEDIUM) - Data loading operations
- **DATA_ENG_XFORM_WH** (LARGE) - Data transformation operations
- **DATA_ENG_ANALYTICS_WH** (XSMALL) - Analytics queries

### Stages and File Formats
- **CSV_STAGE** + **CSV_FORMAT** - CSV file ingestion
- **JSON_STAGE** + **JSON_FORMAT** - JSON file ingestion
- **PARQUET_STAGE** + **PARQUET_FORMAT** - Parquet file ingestion
- **GENERAL_STAGE** - General purpose stage
- **PIPE_DELIMITED_FORMAT** - Pipe-delimited files

## 📊 Demo Data

This main setup creates **infrastructure only** (no sample data).

**For complete demos with data:**
- **FACTSET ETF Constituents:** See `demos/factset_etf_iceberg/` - CDC patterns with Streams, Dynamic Tables, Tasks, and Iceberg
- Each demo is self-contained with its own data setup

All demos use **dynamic dates** relative to execution date for relevance.

## 🧪 Testing

Test the setup with SQL queries:

```sql
-- Verify database and schemas
USE DATABASE DATA_ENG_DEMO;
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
SHOW SCHEMAS;

-- Check warehouses
SHOW WAREHOUSES LIKE 'DATA_ENG%';
DESCRIBE WAREHOUSE DATA_ENG_ANALYTICS_WH;

-- Check stages
USE SCHEMA RAW_DATA;
SHOW STAGES;
LIST @CSV_STAGE;

-- Check file formats
SHOW FILE FORMATS;
DESCRIBE FILE FORMAT CSV_FORMAT;
```

## 🛠️ Configuration

Edit `sql/00_setup_infrastructure.sql` to customize:

```sql
-- Database name
CREATE DATABASE IF NOT EXISTS DATA_ENG_DEMO ...
-- Change to: YOUR_DATABASE_NAME

-- Warehouse sizes
CREATE WAREHOUSE IF NOT EXISTS DATA_ENG_LOAD_WH
    WAREHOUSE_SIZE = 'MEDIUM'  -- Change to: SMALL, LARGE, etc.
    ...
```

## 🔧 Common Operations

### Rebuild Entire Setup

```bash
# Cleanup
snowsql -c your_connection -f sql/99_cleanup.sql

# Rebuild
snowsql -c your_connection -f sql/00_setup_infrastructure.sql
```

### Work with Individual Demos

```bash
# Navigate to a specific demo
cd demos/factset_etf_iceberg

# Follow that demo's README for setup and data operations
```

### Monitor Pipeline Health

```sql
-- Check task execution history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- Check warehouse usage
SELECT *
FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
    DATE_RANGE_START => DATEADD('day', -7, CURRENT_DATE())
))
WHERE WAREHOUSE_NAME LIKE 'DATA_ENG%';

-- Check storage
SELECT 
    TABLE_CATALOG || '.' || TABLE_SCHEMA || '.' || TABLE_NAME AS FULL_NAME,
    ROW_COUNT,
    BYTES / POWER(1024, 3) AS SIZE_GB
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('RAW_DATA', 'CURATED', 'ANALYTICS')
ORDER BY BYTES DESC;
```

## 📝 Notes

- **SQL-Only** - No Python dependencies required
- **Infrastructure Setup** - Creates empty schemas ready for demos
- **FACTSET Demo** - Complete working example with real data
- **Modular** - Each demo is self-contained
- **Production-Ready** - Idempotent DDL, proper error handling

## 🤝 Support

For issues or questions:
1. Check **[SETUP.md](SETUP.md)** for setup help
2. Review **[docs/architecture.md](docs/architecture.md)** for architecture details
3. See demo-specific README files
4. Review Snowflake documentation

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Quick setup guide
- **[docs/architecture.md](docs/architecture.md)** - Architecture details
- **[docs/demo_script.md](docs/demo_script.md)** - Presentation guide
- **[docs/setup_guide.md](docs/setup_guide.md)** - Detailed setup instructions
- **[demos/factset_etf_iceberg/README.md](demos/factset_etf_iceberg/README.md)** - FACTSET demo guide

## 🗂️ Version History

- **v3.0** (Current) - Pure SQL implementation, no Python required
- **v2.0** - Python-based setup (archived to `src_archived_python/`)
- **v1.0** - Initial release

---

**Tech Stack:** Pure SQL | Snowflake | SnowSQL  
**Demo Type:** Infrastructure + CDC Patterns  
**Duration:** 5 min setup + 30-45 min demo  
**Last Updated:** 2025-11-18
