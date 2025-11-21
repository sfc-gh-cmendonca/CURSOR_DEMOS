# FACTSET ETF Constituents - Iceberg/Parquet ETL Demo

Advanced Snowflake CDC (Change Data Capture) demo showcasing **2 stream-based pipeline patterns** for processing ETF constituent data using Streams, Tasks, and Iceberg format with Parquet exports.

## 🎯 Demo Overview

This demo implements a complete ETL/ELT solution for **FACTSET ETF CONSTITUENTS data only**, demonstrating:

- **Streams on shared tables** - Create stream on `ETF_DATA.PUBLIC.CONSTITUENTS` share
- **Stream-attached Tasks** for efficient CDC processing
- **Iceberg tables** for ACID compliance
- **Parquet exports** for audit trails and data sharing
- **Complete CDC handling** (INSERT, UPDATE, DELETE)

**Note:** This demo focuses solely on the CONSTITUENTS table. No additional customer, product, transaction, or event data is needed. **Dynamic Tables are not used** (they cannot read from Streams).

### Key Features

✅ **2 Production-Ready Pipeline Patterns** - Choose the best approach for your use case  
✅ **Stream-Based** - Efficient CDC processing with `WHEN SYSTEM$STREAM_HAS_DATA()`  
✅ **CDC Semantics** - Correct handling of ADD, UPDATE, DELETE operations  
✅ **Audit Trail** - Parquet exports with operation metadata  
✅ **Monitoring** - Built-in task and stream monitoring

## 📊 Pipeline Patterns

### Pipeline 1: Stream → Task (Stream-Attached) → Iceberg
**Pattern:** Self-contained pipeline with dedicated stream and Iceberg table  
**Best for:** Simple, direct pipelines with ACID compliance and minimal latency  
**Components:**
- Creates `pipeline1_constituents_stream` on shared table
- Task (stream-attached) performs DELETE then MERGE to Iceberg table
- Only runs when stream has data (`WHEN SYSTEM$STREAM_HAS_DATA()`)

**Pros:** Simple, efficient, ACID compliance, time travel, completely independent  
**Cons:** All logic in task (less modular)

**Use Case:** When you need current state with ACID compliance (no audit trail)

---

### Pipeline 2: Stream → Task (Stream-Attached) → Parquet (CDC Audit Only)
**Pattern:** Self-contained pipeline with dedicated stream that exports CDC to Parquet only  
**Best for:** CDC audit trail, compliance, data lake integration, event streaming  
**Components:**
- Creates `pipeline2_constituents_stream` on shared table
- Single stream-attached task exports CDC events to Parquet
- No table created - purely for audit/compliance
- Stream automatically cleared after successful read

**Pros:** Simplest possible CDC pattern, minimal objects, perfect for audit/compliance, data lake ready, completely independent  
**Cons:** No queryable current state (use Pipeline 1 or source table for that)

**Use Case:** When you only need CDC audit trail for compliance, data lake, or event streaming

**Comparison with Pipeline 1:**
- Pipeline 1: **Iceberg table** with current state (ACID, time travel, schema evolution)
- Pipeline 2: **Parquet CDC files** only (audit trail, no current state)
- **Both pipelines are completely independent** - each has its own stream

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   ETF_DATA.PUBLIC.CONSTITUENTS      │
│   (FACTSET Share - Read Only)       │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ 2 STREAMS      │
        │ (Independent)  │
        └────────┬───────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
    ▼                          ▼
┌─────────┐              ┌──────────┐
│Pipeline1│              │Pipeline2 │
│Stream   │              │Stream    │
└────┬────┘              └────┬─────┘
     │                        │
     ▼                        ▼
┌─────────────┐          ┌──────────┐
│  ICEBERG    │          │ PARQUET  │
│  TABLE      │          │  FILES   │
│             │          │  (CDC    │
│ (Current    │          │  Audit   │
│  State +    │          │  Only)   │
│  ACID +     │          │          │
│  Time       │          │  No      │
│  Travel)    │          │  Table!  │
└─────────────┘          └──────────┘
```

## 📋 Prerequisites

### Required
1. **Snowflake Account** with ACCOUNTADMIN privileges (or appropriate role)
2. **FACTSET ETF Data Share**: `ETF_DATA.PUBLIC.CONSTITUENTS`
   - This share must be accessible in your account
   - No mock data - demo requires real share
3. **Snowflake CLI** (SnowSQL) or Web UI access

### Optional (for production Iceberg)
- **External Storage**: AWS S3, Azure Blob, or GCS
- **External Volume**: Configured for Iceberg tables

## 🚀 Quick Start

### Step 1: Load Configuration

```bash
cd demos/factset_etf_iceberg
snowsql -c your_connection -f config_factset.sql
```

This sets all session variables ($ROLE_NAME, $WAREHOUSE_NAME, etc.)

### Step 2: Initialize Environment

```bash
snowsql -c your_connection -f sql/00_initialization.sql
```

Creates:
- Database and schemas
- Stage for Parquet exports
- Stream on FACTSET share
- Iceberg table (or regular table for demo)
- Initial data load

### Step 3: Deploy Pipelines

**Option A: Deploy Pipeline 1 only (Iceberg current state)**
```bash
snowsql -c your_connection -f sql/01_pipeline_stream_task_iceberg.sql
```

**Option B: Deploy Pipeline 2 only (Iceberg + Parquet audit trail)**
```bash
snowsql -c your_connection -f sql/02_pipeline_stream_task_iceberg_parquet.sql
```

**Option C: Deploy both pipelines**
```bash
snowsql -c your_connection -f sql/01_pipeline_stream_task_iceberg.sql
snowsql -c your_connection -f sql/02_pipeline_stream_task_iceberg.sql
```

## 📊 What Gets Created

### Database Objects

**Workspace Schema:** `DATA_ENG_DEMO.FACTSET`
- `constituents_base` - Local snapshot (from initialization, optional)
- `pipeline1_constituents_stream` - CDC stream for Pipeline 1
- `pipeline2_constituents_stream` - CDC stream for Pipeline 2
- `pipeline1_stream_to_iceberg_merge_task` - Pipeline 1 task
- `pipeline2_stream_to_parquet_task` - Pipeline 2 task

**Iceberg Schema:** `DATA_ENG_DEMO.ICEBERG`
- `CONSTITUENTS_ICEBERG` - Current state table (Pipeline 1 only)

**Parquet Exports:** `@FACTSET_ETF_STAGE/REPORTING/`
- `pipeline2_cdc/` - CDC audit files from Pipeline 2 (ADD, UPDATE, DELETE events)

**Note:** 
- Each pipeline creates its own stream - they are completely independent
- Pipeline 2 does NOT create a table - it only exports CDC to Parquet

**Parquet Exports:** `@FACTSET_ETF_STAGE/REPORTING/`
- `pipeline2_cdc/` - CDC audit files from Pipeline 2

### Task Schedules
- Both tasks run every 10 minutes
- Tasks only execute when stream has data (`WHEN SYSTEM$STREAM_HAS_DATA()`)

## 🔍 Monitoring

### Check Stream Status
```sql
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.constituents_stream');
```

### Check Task History
```sql
-- Pipeline 1
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'pipeline1_stream_to_iceberg_merge_task',
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;

-- Pipeline 2
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'pipeline2_stream_merge_and_copy_parquet_task',
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;
```

### Check Parquet Files
```sql
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/;
```

### Query Tables

**Pipeline 1 - Iceberg Table:**
```sql
SELECT * 
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG 
LIMIT 10;

SELECT COUNT(*), MAX(LAST_UPDATED_TIMESTAMP) 
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;
```

**Pipeline 2 - Parquet Files (No Table):**
```sql
-- List CDC audit files
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/;

-- Query Parquet files directly (if needed)
SELECT $1:FUND_ID::STRING AS FUND_ID,
       $1:OP_TYPE::STRING AS OP_TYPE,
       $1:PROCESSED_TS::TIMESTAMP AS PROCESSED_TS
FROM @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/
(FILE_FORMAT => 'PARQUET_FORMAT')
LIMIT 10;
```

## 🧪 Testing

Since `ETF_DATA.PUBLIC.CONSTITUENTS` is a read-only share, you cannot insert/update/delete records to test CDC.

**To test CDC:**
1. Wait for natural changes to the share (if provider updates data)
2. Set up a local test environment with a writable table
3. Modify the stream source in `00_initialization.sql` to point to your test table

## 🧹 Cleanup

```bash
snowsql -c your_connection -f sql/99_cleanup.sql
```

Removes all tasks, streams, tables, and stages created by this demo.

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 10-minute setup guide
- **[docs/pipeline_comparison.md](docs/pipeline_comparison.md)** - Detailed pipeline comparison
- **[docs/demo_script.md](docs/demo_script.md)** - Presentation guide
- **[docs/using_factset_share.md](docs/using_factset_share.md)** - Share setup details

## 🔧 Customization

### Change Task Schedules

Edit `config_factset.sql`:
```sql
SET REFRESH_SCHEDULE_10MIN = 'USING CRON */5 * * * * UTC';  -- Change to 5 min
```

### Use Production Iceberg Format

Uncomment the Iceberg table creation in `00_initialization.sql`:
```sql
CREATE OR REPLACE ICEBERG TABLE ...
CATALOG = 'SNOWFLAKE'
EXTERNAL_VOLUME = 'snowbank_iceberg_vol'
BASE_LOCATION = 'constituents';
```

### Add Partitioning to Parquet Exports

Modify COPY statement in pipeline tasks:
```sql
COPY INTO IDENTIFIER('@' || $EXTERNAL_STAGE || '/' || $PARQUET_OUTPUT_PATH || 
    '/pipeline2_cdc/year=' || TO_VARCHAR(CURRENT_DATE(), 'YYYY') || 
    '/month=' || TO_VARCHAR(CURRENT_DATE(), 'MM') || '/')
```

## 🎯 Use Cases

### Use Case 1: Queryable Current State (Iceberg)
**Deploy:** Pipeline 1  
**Result:** Always-current view in Iceberg table with time travel  
**Query:** `SELECT * FROM ICEBERG.CONSTITUENTS_ICEBERG`  
**Benefits:** ACID transactions, time travel, schema evolution, SQL queries

### Use Case 2: CDC Audit Trail Only (Compliance/Data Lake)
**Deploy:** Pipeline 2  
**Result:** CDC audit log in Parquet (ADD/UPDATE/DELETE events)  
**Query:** Query Parquet files directly or load to data lake  
**Benefits:** Complete audit trail, data lake integration, simplest CDC pattern, no table overhead

### Use Case 3: Both (Current State + Audit Trail)
**Deploy:** Both pipelines  
**Result:** Iceberg table (current state) + Parquet files (audit trail)  
**Use:** Query current data (Pipeline 1) + complete CDC audit (Pipeline 2)

## ⚠️ Important Notes

1. **Dynamic Tables NOT used** - They cannot read from Streams in Snowflake
2. **Stream on Shared Table** - Works! Stream is in your schema, source is shared
3. **Read-Only Share** - Cannot simulate changes; monitor real updates only
4. **Parquet from Stream** - CDC exports read directly from Stream (not from tables)
5. **Task Execution** - Only runs when stream has data (efficient)
6. **Two Table Types** - Pipeline 1 uses Iceberg, Pipeline 2 uses regular table for comparison

## 📖 Key Concepts

**Stream**: Captures all DML changes (INSERT, UPDATE, DELETE) with metadata  
**Stream-Attached Task**: Executes only when `SYSTEM$STREAM_HAS_DATA()` returns TRUE  
**Iceberg Table**: ACID-compliant table format with time travel and schema evolution (Pipeline 1)  
**CDC (Change Data Capture)**: Tracking data changes for sync, audit, and analytics  
**op_type Mapping**: ADD (new), UPDATE (changed), DELETE (removed)  
**Stream Auto-Clear**: Stream automatically cleared after successful read (no manual clearing needed)

## 🤝 Support

For issues or questions:
1. Check documentation in `docs/` directory
2. Review PRD specifications
3. Verify FACTSET share access
4. Check task execution logs

---

**Version:** 2.0 (Stream-Based Only)  
**Last Updated:** 2025-11-20  
**Architecture:** Streams + Tasks (No Dynamic Tables)
