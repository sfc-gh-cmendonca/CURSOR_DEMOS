# Using the FACTSET ETF_DATA Share

Complete guide for connecting to and using the FACTSET `ETF_DATA.PUBLIC.CONSTITUENTS` share in this demo.

## Overview

This demo is **hardcoded** to work exclusively with FACTSET's `ETF_DATA.PUBLIC.CONSTITUENTS` data share. You create a **stream in your own schema** that references the **shared table**, and all 4 pipeline patterns work seamlessly.

**Important:** This demo requires access to the FACTSET share. No mock data or fallback options are provided - the share is mandatory.

## Key Concept: Streams on Shared Tables

**Important:** Streams on shared tables are fully supported in Snowflake!

- **Stream location:** Your database/schema (e.g., `DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM`)
- **Source location:** FACTSET share (e.g., `ETF_DATA.PUBLIC.CONSTITUENTS`)
- **How it works:** Stream metadata lives in your account, but references the shared table

## Setup Instructions

### Step 1: Verify Share Access

First, check if you have access to the FACTSET share:

```sql
-- List all shares available to you
SHOW SHARES;

-- Check specific share
SHOW SHARES LIKE 'ETF_DATA';

-- View share details
DESC SHARE ETF_DATA;

-- View tables in the share
SHOW TABLES IN ETF_DATA.PUBLIC;

-- Query the constituents table
SELECT * FROM ETF_DATA.PUBLIC.CONSTITUENTS LIMIT 10;
```

If you don't see `ETF_DATA`, you need to:
1. Contact FACTSET to provision access
2. Provide your Snowflake account identifier
3. Wait for share to be granted

### Step 2: Configure the Demo

In `config_factset.sql`, the source is **hardcoded**:

```sql
SET SOURCE_TABLE = 'ETF_DATA.PUBLIC.CONSTITUENTS';  -- FACTSET share (hardcoded)
```

**This cannot be changed** - the demo is designed exclusively for the FACTSET share.

### Step 3: Run Initialization

```sql
-- Load config
@demos/factset_etf_iceberg/config_factset.sql

-- Initialize (creates stream on the share)
@demos/factset_etf_iceberg/sql/00_initialization.sql
```

The initialization will:
- Create `DATA_ENG_DEMO` database and schemas
- **Verify access** to the FACTSET share (fails if not accessible)
- Create a **local snapshot** from the share (optional, for reference)
- Create a **stream** on the shared table
- Set up Iceberg table structure
- Configure stages for Parquet exports

### Step 4: Verify Stream on Shared Table

```sql
-- Show your stream
SHOW STREAMS IN SCHEMA DATA_ENG_DEMO.FACTSET;

-- Describe the stream
DESC STREAM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM;

-- Verify it references the share
SELECT 
    'Stream: DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM' AS OBJECT,
    'Source: ETF_DATA.PUBLIC.CONSTITUENTS' AS SOURCE,
    'This works! Stream in your schema, source in share.' AS NOTE;
```

## Understanding the Data Flow

```
┌──────────────────────────────────────┐
│   FACTSET Account                    │
│   ETF_DATA.PUBLIC.CONSTITUENTS       │  ← Shared table (read-only)
└───────────────┬──────────────────────┘
                │ (Share provider updates data)
                │
                ▼
┌──────────────────────────────────────┐
│   Your Account                       │
│   DATA_ENG_DEMO.FACTSET              │
│                                      │
│   CONSTITUENTS_STREAM ◄──────────────┤  ← Stream captures changes
│   (Your stream, their data)          │
└───────────────┬──────────────────────┘
                │
                ▼ (Your pipelines process)
       ┌────────┴────────┐
       ▼                 ▼
  ICEBERG_TABLE    PARQUET_FILES
  (Your data)      (Your files)
```

## How Changes are Captured

1. **FACTSET updates** `ETF_DATA.PUBLIC.CONSTITUENTS` in their account
2. **Your stream** automatically sees those changes (INSERT/UPDATE/DELETE)
3. **Your tasks** process the stream and update your Iceberg table
4. **Your Parquet exports** capture the audit trail

You have **no control** over when FACTSET updates their data. The stream simply captures whatever changes they make.

## Testing Without Share Access

**This demo requires the FACTSET share to run.** There is no mock data fallback.

If you don't have access to `ETF_DATA.PUBLIC.CONSTITUENTS`:
1. Contact FACTSET to provision access
2. Provide your Snowflake account identifier
3. Wait for the share to be granted to your account

**You cannot run this demo without the FACTSET share.**

## Common Questions

### Q: Can I modify the shared table?

**A: No.** Shared tables are read-only. You can only query them. The share provider (FACTSET) controls all modifications.

### Q: How do I simulate changes for testing?

**A:** Wait for FACTSET to update their share. Since we're using a real data share (not a mock table), changes come from the share provider only.

### Q: Does the stream consume credits?

**A: Minimal.** Streams have negligible storage overhead. Most costs come from:
- Your tasks processing the stream
- Your Iceberg table storage
- Your Parquet file exports

### Q: What if FACTSET adds new columns?

**A: Stream captures them automatically.** However, your Iceberg table schema is fixed. You'll need to:
1. Alter your Iceberg table to add new columns, OR
2. Recreate it with `SELECT *` to include all columns

### Q: Can I create multiple streams on the same share?

**A: Yes!** Each pipeline could have its own stream if needed. But usually one stream feeding multiple downstream processes is more efficient.

### Q: What happens if the share is revoked?

**A:** Your stream will fail to refresh. Tasks will error. You'll need to:
1. Contact FACTSET to restore access
2. The demo cannot function without the share

## Best Practices

### Production Setup

1. **Verify share access** - Ensure FACTSET share is accessible
2. **Monitor share availability** - Alert if share access lost
3. **Set appropriate task schedules** - Match FACTSET's update frequency
4. **Size warehouses correctly** - Based on data volume from share
5. **Test with snapshots first** - Copy share data to local table for testing

### Development/Testing Setup

1. **Copy share snapshot** - `CREATE TABLE test_data AS SELECT * FROM share`
2. **Test patterns on snapshot** - Validate logic before production
3. **Use stream on actual share** - Once patterns are validated

### Monitoring

```sql
-- Check if share is accessible
SELECT COUNT(*) FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Check stream lag
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- Check last share update (if available in share metadata)
SELECT MAX(LOAD_TIMESTAMP) FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Monitor task processing
SELECT * 
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

## Troubleshooting

### Issue: "Object does not exist: ETF_DATA.PUBLIC.CONSTITUENTS"

**Solution:** Share not accessible. Check:
- `SHOW SHARES` - Is ETF_DATA listed?
- Contact FACTSET for access
- **This demo cannot run without the share**

### Issue: "Insufficient privileges on share"

**Solution:** Need IMPORTED PRIVILEGES. Run:
```sql
GRANT IMPORTED PRIVILEGES ON DATABASE ETF_DATA TO ROLE YOUR_ROLE;
```

### Issue: "Cannot create stream on shared table"

**Solution:** This should work! But check:
- Snowflake account edition (Enterprise required for some features)
- Role has CREATE STREAM privilege
- Try different share or contact Snowflake support

### Issue: Stream shows no data even after share updates

**Solution:** 
- Stream only captures changes AFTER creation
- Changes before stream creation are not captured
- Recreate stream to start fresh: `CREATE OR REPLACE STREAM...`

## Additional Resources

- **Snowflake Data Sharing:** https://docs.snowflake.com/en/user-guide/data-sharing-intro
- **Streams on Shared Tables:** https://docs.snowflake.com/en/user-guide/streams
- **FACTSET Documentation:** Contact FACTSET for share-specific docs
- **Demo Main README:** `../README.md`

---

**Summary:** This demo is **hardcoded** to use the FACTSET share `ETF_DATA.PUBLIC.CONSTITUENTS` exclusively. The stream-on-shared-table pattern is fully supported and production-ready!

