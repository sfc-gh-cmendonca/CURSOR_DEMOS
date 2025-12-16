# FACTSET ETF Iceberg/Parquet ETL - Quick Start Guide

Get up and running with the demo in 10 minutes.

## ⚠️ FIRST: Check Change Tracking

**Before starting, check if the FACTSET share has change tracking enabled:**

```sql
SHOW TABLES LIKE 'CONSTITUENTS' IN ETF_DATA.PUBLIC;
```

Look for the `change_tracking` column. If it shows **"OFF"** or is not enabled:
- ❌ **DO NOT use the standard setup files**
- ✅ **USE:** `WORKAROUND_LOCAL_COPY.sql` instead (see below)

---

## ⚡ Setup Option 1: Share WITH Change Tracking

**Use this if** change tracking is enabled on the FACTSET share.

### Via Snowflake Web UI (Easiest)

1. Log into Snowflake Web UI
2. Open a new worksheet
3. Copy/paste entire contents of `CONSOLIDATED_SETUP.sql`
4. Click "Run All"

**Done!** Both pipelines are now set up.

---

## ⚡ Setup Option 2: Share WITHOUT Change Tracking (Workaround)

**Use this if** change tracking is NOT enabled on the FACTSET share.

### Via Snowflake Web UI (Recommended)

1. Log into Snowflake Web UI
2. Open a new worksheet  
3. Copy/paste entire contents of `WORKAROUND_LOCAL_COPY.sql`
4. Click "Run All"

**What this does:**
- Creates a local writable copy of FACTSET data
- Enables change tracking on local copy
- Creates streams on local table (works!)
- Sets up both pipelines
- Optionally syncs local copy from share hourly

**File locations:**
- Local: `WORKAROUND_LOCAL_COPY.sql`
- GitHub: https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/blob/main/DATA_ENGINEERING_DEMOS/demos/factset_etf_iceberg/WORKAROUND_LOCAL_COPY.sql

### Step 3: Choose & Run a Pipeline (2 minutes)

**Option A: Simplest Pattern (Recommended for first run)**

```sql
@demos/factset_etf_iceberg/sql/02_pipeline_stream_task_iceberg.sql
```

**Option B: With Audit Trail (Recommended for production)**

```sql
@demos/factset_etf_iceberg/sql/04_pipeline_stream_task_iceberg_parquet.sql
```

**Option C: Run All 4 Patterns (For comparison)**

```sql
@demos/factset_etf_iceberg/scripts/run_all_pipelines.sql
```

---

## ⚡ 5-Minute Demo

**Note:** Since this demo uses the FACTSET share (read-only), changes come from FACTSET's updates to `ETF_DATA.PUBLIC.CONSTITUENTS`. You cannot directly modify the shared table.

### Step 1: Check Stream for Changes

```sql
-- See captured CDC events
SELECT 
    CASE
        WHEN METADATA$ACTION = 'INSERT' AND NOT METADATA$ISUPDATE THEN 'ADD'
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
    END AS OP_TYPE,
    TICKER,
    WEIGHT
FROM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM
LIMIT 20;
```

### Step 3: Execute Task Manually

```sql
-- Force task to run (instead of waiting for schedule)
EXECUTE TASK DATA_ENG_DEMO.FACTSET.PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;
```

### Step 4: Verify Results

```sql
-- Check Iceberg table
SELECT * FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
ORDER BY LAST_UPDATED_TIMESTAMP DESC
LIMIT 10;

-- Check Parquet audit trail (Pipeline 4 only)
SELECT 
    OP_TYPE,
    COUNT(*) AS EVENT_COUNT
FROM DATA_ENG_DEMO.FACTSET.PIPELINE4_CDC_AUDIT_TRAIL
GROUP BY OP_TYPE;
```

---

## 🎯 Choosing Your Pipeline

**"Just need basic CDC"** → Use Pipeline 2  
**"Need audit trail for compliance"** → Use Pipeline 4  
**"Complex transformations needed"** → Use Pipeline 1  
**"Budget allows comprehensive solution"** → Use Pipeline 3  

**80% of users choose Pipeline 4** (balanced approach with audit trail)

---

## 🔍 Quick Verification

After setup, run this to verify everything works:

```sql
-- Check all objects created
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA FACTSET;

-- Tables exist?
SHOW TABLES;

-- Stream exists and captures data?
SHOW STREAMS;
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- Tasks running?
SHOW TASKS;

-- Iceberg table populated?
SELECT COUNT(*) FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;
```

Expected results:
- ✅ 3-4 tables (source, base, Iceberg)
- ✅ 1 stream (CONSTITUENTS_STREAM)
- ✅ 1-4 tasks (depending on which pipelines you ran)
- ✅ 2 dynamic tables (if ran Pipeline 1 or 3)
- ✅ 10+ rows in Iceberg table

---

## 📊 Monitoring Your Pipeline

### Check Task Execution

```sql
SELECT 
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

### Check Stream Status

```sql
-- How many events pending?
SELECT COUNT(*) FROM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM;

-- What types of events?
SELECT 
    METADATA$ACTION,
    METADATA$ISUPDATE,
    COUNT(*) AS COUNT
FROM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM
GROUP BY METADATA$ACTION, METADATA$ISUPDATE;
```

### Check Dynamic Table Refresh (Pipeline 1 & 3)

```sql
SELECT 
    NAME,
    STATE,
    DATA_TIMESTAMP,
    SCHEDULING_STATE
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
WHERE NAME LIKE 'CONSTITUENTS%'
ORDER BY DATA_TIMESTAMP DESC
LIMIT 5;
```

---

## 🧪 Monitoring & Validation

**Note:** Since this demo uses the FACTSET share (read-only), testing relies on monitoring real changes from FACTSET.

### Check for New Changes

```sql
-- Monitor if FACTSET has updated the share
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- View any pending changes
SELECT 
    CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
    END AS OP_TYPE,
    COUNT(*) AS COUNT
FROM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM
GROUP BY OP_TYPE;
```

### Verify Pipeline Execution

```sql
-- Check task history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;

-- Verify Iceberg table data
SELECT COUNT(*) as TOTAL_RECORDS
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;

-- Check recent updates
SELECT *
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG 
WHERE LAST_UPDATED_TIMESTAMP > DATEADD('hour', -1, CURRENT_TIMESTAMP())
LIMIT 10;
```

### Manual Task Execution

```sql
-- If stream has data, manually trigger a task
EXECUTE TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;

-- Check results
SELECT 'Task executed' AS STATUS;
```

---

## 🧹 Cleanup When Done

```sql
@demos/factset_etf_iceberg/sql/99_cleanup.sql
```

**Warning:** This removes all demo objects and data!

---

## 🆘 Troubleshooting

### Issue: "Table already exists"

**Solution:** Run cleanup first, then re-run initialization

```sql
@demos/factset_etf_iceberg/sql/99_cleanup.sql
@demos/factset_etf_iceberg/sql/00_initialization.sql
```

### Issue: "Stream has no data"

**Solution:** Wait for FACTSET to update their share. Since `ETF_DATA.PUBLIC.CONSTITUENTS` is a read-only share, you cannot directly modify it. Changes come from the share provider only.

### Issue: "Task not executing"

**Solution:** Check if task is suspended

```sql
-- Resume task
ALTER TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK RESUME;

-- Manually execute
EXECUTE TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;
```

### Issue: "External volume not found"

**Solution:** Demo works without external volume - uses regular table

The initialization script detects this and creates a regular table instead of Iceberg. The patterns work identically.

---

## 📚 Learn More

- **Full README:** `README.md`
- **Pipeline Comparison:** `docs/pipeline_comparison.md`
- **Demo Script:** `docs/demo_script.md`

---

## 🎓 What You've Learned

After completing this quick start, you've seen:

✅ How Streams capture CDC automatically  
✅ How to map METADATA to operation types  
✅ Stream-attached tasks with `SYSTEM$STREAM_HAS_DATA`  
✅ MERGE pattern for upserts  
✅ Parquet export for audit trails  
✅ Task scheduling and execution  

---

**Time to Complete:** 10 minutes  
**Next Step:** Monitor the stream and tasks as FACTSET updates their share!

