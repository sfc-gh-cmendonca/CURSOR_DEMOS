# FACTSET ETF Demo - Setup Using Snowflake Web UI

**Easiest method - no SnowSQL connection issues!**

## Step-by-Step Instructions

### Step 1: Log into Snowflake Web UI

1. Go to: https://app.snowflake.com/ (or your specific Snowflake URL)
2. Log in with your credentials
3. Select role: **SYSADMIN** or **ACCOUNTADMIN**

### Step 2: Open SQL Worksheet

1. Click **"Worksheets"** in the left navigation
2. Click **"+ Worksheet"** to create a new worksheet
3. You should now have a blank SQL editor

### Step 3: Run Configuration

1. Open file: `config_factset.sql` 
2. **Copy entire contents** of the file
3. **Paste** into Snowflake worksheet
4. Click **"Run All"** (or press Cmd+Enter)

You should see output showing all configuration parameters.

### Step 4: Run Initialization

1. Open file: `sql/00_initialization.sql`
2. **Copy entire contents**
3. **Paste** into a new Snowflake worksheet
4. Click **"Run All"**

This creates:
- Database and schemas
- Stream on FACTSET share
- Iceberg table
- Stage for Parquet files

### Step 5: Deploy Pipeline 1 (Iceberg Table)

1. Open file: `sql/01_pipeline_stream_task_iceberg.sql`
2. **Copy entire contents**
3. **Paste** into a new Snowflake worksheet
4. Click **"Run All"**

This creates:
- `pipeline1_constituents_stream`
- `pipeline1_stream_to_iceberg_merge_task`

### Step 6: Deploy Pipeline 2 (Parquet CDC)

1. Open file: `sql/02_pipeline_stream_task_iceberg_parquet.sql`
2. **Copy entire contents**
3. **Paste** into a new Snowflake worksheet
4. Click **"Run All"**

This creates:
- `pipeline2_constituents_stream`
- `pipeline2_stream_to_parquet_task`

## ✅ Verification

Run this in a Snowflake worksheet:

```sql
-- Check tasks
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA FACTSET;
SHOW TASKS;

-- Check streams
SHOW STREAMS;

-- Check Iceberg table
SELECT COUNT(*) FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;

-- Check stream status
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline1_constituents_stream');
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.pipeline2_constituents_stream');
```

## 🎯 Expected Results

After successful setup, you should see:
- ✅ 2 tasks created and running
- ✅ 2 streams created
- ✅ 1 Iceberg table with data
- ✅ Tasks in "started" state

## 🔧 Troubleshooting

### Issue: "Object does not exist: ETF_DATA.PUBLIC.CONSTITUENTS"

**Solution:** You don't have access to the FACTSET share. Contact FACTSET or your admin.

### Issue: "Insufficient privileges"

**Solution:** Switch to ACCOUNTADMIN role:
```sql
USE ROLE ACCOUNTADMIN;
```

Then re-run the scripts.

### Issue: "External volume not found"

**Solution:** This is expected. The demo uses regular tables instead of Iceberg format by default. The scripts handle this automatically.

## 📊 Monitor Pipeline Execution

```sql
-- View task execution history
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'pipeline%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- View Parquet files
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline2_cdc/;
```

## 🧹 Cleanup (When Done)

1. Open file: `sql/99_cleanup.sql`
2. Copy contents
3. Paste into Snowflake worksheet
4. Run All

This removes all demo objects.

---

**Total Time:** 10-15 minutes  
**No SnowSQL Required!** ✅

