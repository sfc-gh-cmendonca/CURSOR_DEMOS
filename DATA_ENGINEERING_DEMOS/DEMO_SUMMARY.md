# Snowflake Data Engineering Demo - FACTSET ETF CDC Pipeline

## Overview

This demo showcases production-ready **Change Data Capture (CDC)** patterns for Snowflake using the FACTSET ETF Constituents dataset. It demonstrates two independent, stream-based pipelines that highlight different approaches to CDC processing.

## 🎯 What This Demo Includes

### Architecture: Pure SQL Implementation
- **No Python required** - 100% SQL-based demo
- **No Dynamic Tables** - Uses Streams and Tasks only (Dynamic Tables cannot read from Streams)
- **Production-ready** - Idempotent DDL, explicit columns, proper error handling
- **PRD-compliant** - Follows all specifications for Snowflake CDC best practices

### Two Independent CDC Pipelines

**Pipeline 1: Stream → Task → Iceberg Table**
- Creates queryable current state with ACID compliance
- Features: Time travel, schema evolution, SQL queries
- Use case: When you need to query current state

**Pipeline 2: Stream → Task → Parquet Files (CDC Audit Only)**
- Exports CDC events directly to Parquet files
- No table created - purely for audit/compliance
- Use case: Data lake integration, compliance audit trail

## 🏗️ Architecture

```
ETF_DATA.PUBLIC.CONSTITUENTS (FACTSET Share - Read Only)
    ↓                           ↓
Pipeline 1 Stream       Pipeline 2 Stream
(Independent)           (Independent)
    ↓                           ↓
Pipeline 1 Task         Pipeline 2 Task
    ↓                           ↓
ICEBERG TABLE           PARQUET FILES
(Current State)         (CDC Audit Only)
• ACID                  • ADD events
• Time Travel           • UPDATE events
• SQL Queries           • DELETE events
```

## 📋 Quick Start

### Prerequisites
- Snowflake account with ACCOUNTADMIN or SYSADMIN privileges
- Access to **ETF_DATA.PUBLIC.CONSTITUENTS** share (FACTSET)
- Snowflake Web UI access (recommended) or SnowSQL

### ⚠️ Important: Change Tracking Check

**Before setup, verify if the FACTSET share has change tracking:**
```sql
SHOW TABLES LIKE 'CONSTITUENTS' IN ETF_DATA.PUBLIC;
```

### Setup (5 minutes)

**If change tracking is enabled on the share:**
```bash
cd demos/factset_etf_iceberg
# Copy/paste CONSOLIDATED_SETUP.sql into Snowflake Web UI and run
```

**If change tracking is NOT enabled (most common):**
```bash
cd demos/factset_etf_iceberg
# Copy/paste WORKAROUND_LOCAL_COPY.sql into Snowflake Web UI and run
```

**The workaround:**
- Creates a local writable copy of FACTSET data
- Enables change tracking on the local copy
- Streams work on local table
- Optionally syncs from share hourly

**Files:**
- `CONSOLIDATED_SETUP.sql` - Standard setup (requires change tracking on share)
- `WORKAROUND_LOCAL_COPY.sql` - Workaround for shares without change tracking ⭐ **Use this if you get Stream errors**

## 🔍 What Gets Created

### Pipeline 1 Objects
- `pipeline1_constituents_stream` - CDC stream
- `pipeline1_stream_to_iceberg_merge_task` - Task
- `CONSTITUENTS_ICEBERG` - Iceberg table (in ICEBERG schema)

### Pipeline 2 Objects
- `pipeline2_constituents_stream` - CDC stream
- `pipeline2_stream_to_parquet_task` - Task
- Parquet files at `@FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/`

## 📊 Monitoring & Queries

### Check Task Status
```sql
-- View task execution history
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'pipeline%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- Check stream status
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline1_constituents_stream');
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline2_constituents_stream');
```

### Query Pipeline 1 (Iceberg Table)
```sql
SELECT * 
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG 
LIMIT 10;

SELECT COUNT(*), MAX(LAST_UPDATED_TIMESTAMP) 
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;
```

### Query Pipeline 2 (Parquet Files)
```sql
-- List CDC audit files
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/;

-- Query Parquet files directly
SELECT $1:FUND_ID::STRING AS FUND_ID,
       $1:TICKER::STRING AS TICKER,
       $1:OP_TYPE::STRING AS OP_TYPE,
       $1:PROCESSED_TS::TIMESTAMP AS PROCESSED_TS
FROM @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/
(FILE_FORMAT => 'PARQUET_FORMAT')
LIMIT 10;
```

## 🎯 Use Cases

### Use Case 1: Queryable Current State
**Deploy:** Pipeline 1 only  
**Result:** Iceberg table with ACID compliance, time travel  
**Query with SQL:** `SELECT * FROM CONSTITUENTS_ICEBERG`

### Use Case 2: CDC Audit Trail for Compliance
**Deploy:** Pipeline 2 only  
**Result:** Parquet files with complete CDC history (ADD/UPDATE/DELETE)  
**Use for:** Compliance, audit, data lake integration

### Use Case 3: Both Current State + Audit Trail
**Deploy:** Both pipelines  
**Result:** Query current state (Pipeline 1) + complete audit trail (Pipeline 2)  
**Best for:** Production scenarios requiring both capabilities

## 🔑 Key Features

### ✅ Production-Ready
- Idempotent DDL (`CREATE OR REPLACE`, `IF NOT EXISTS`)
- Explicit column lists (no `SELECT *`)
- Proper error handling
- Stream-attached tasks with `WHEN SYSTEM$STREAM_HAS_DATA()`

### ✅ CDC Compliance
- Correct op_type mapping:
  - INSERT + METADATA$ISUPDATE=FALSE → 'ADD'
  - INSERT + METADATA$ISUPDATE=TRUE → 'UPDATE'
  - DELETE → 'DELETE'
- DELETEs processed before upserts
- Stream automatically cleared after successful read

### ✅ Independent Pipelines
- Each pipeline has its own stream
- Can deploy and test separately
- No shared dependencies
- Clear separation of concerns

## 📚 Documentation

### Main Files
- **README.md** - Project overview
- **SETUP.md** - Quick setup guide
- **demos/factset_etf_iceberg/README.md** - Demo-specific guide
- **demos/factset_etf_iceberg/QUICK_START.md** - 10-minute setup
- **docs/architecture.md** - Technical architecture

### SQL Files
- **sql/00_setup_infrastructure.sql** - Infrastructure setup
- **demos/factset_etf_iceberg/config_factset.sql** - Configuration
- **demos/factset_etf_iceberg/sql/00_initialization.sql** - Demo setup
- **demos/factset_etf_iceberg/sql/01_*.sql** - Pipeline 1 (Iceberg)
- **demos/factset_etf_iceberg/sql/02_*.sql** - Pipeline 2 (Parquet)
- **demos/factset_etf_iceberg/sql/99_cleanup.sql** - Cleanup

## 🧹 Cleanup

```bash
cd demos/factset_etf_iceberg
snowsql -c your_connection -f sql/99_cleanup.sql
```

This removes all tasks, streams, tables, and Parquet files created by the demo.

## 🚀 Why This Demo?

### Demonstrates Modern Snowflake Patterns
- **Streams on Shared Tables** - Capture CDC from FACTSET share
- **Stream-Attached Tasks** - Efficient execution with `WHEN` clause
- **Iceberg Tables** - Open format with ACID compliance
- **Parquet Exports** - Data lake integration

### Solves Real Business Problems
- **Compliance** - Complete audit trail of all changes
- **Data Lake Integration** - Export CDC to Parquet for downstream systems
- **Current State Queries** - SQL access to latest data with time travel
- **Performance** - Efficient CDC processing with minimal overhead

### Production-Ready Code
- Follows Snowflake best practices
- PRD-compliant implementation
- Idempotent and safe to re-run
- Clear error handling and monitoring

## 📞 Support

For questions or issues:
1. Review documentation in `docs/` directory
2. Check demo-specific README files
3. Verify FACTSET share access
4. Review task execution logs

## 🏆 Technical Highlights

- **No Python Required** - Pure SQL implementation
- **No Dynamic Tables** - They cannot read from Streams
- **Stream-Based CDC** - Most efficient pattern in Snowflake
- **Independent Pipelines** - Each with dedicated stream
- **Iceberg + Parquet** - Modern open formats
- **Simplest CDC Pattern** - Pipeline 2 is the minimal viable CDC implementation

---

**Version:** 3.0  
**Last Updated:** 2025-11-20  
**Architecture:** Stream-Based CDC (No Dynamic Tables)  
**Language:** Pure SQL (No Python)  
**Data Focus:** ETF Constituents Only (FACTSET)

