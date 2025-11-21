## FACTSET ETF Iceberg/Parquet ETL - Demo Delivery Script

Complete presentation guide for delivering a 30-45 minute demo of CDC patterns with Streams, Dynamic Tables, Tasks, and Iceberg.

---

## Demo Overview

**Duration:** 30-45 minutes  
**Audience:** Data engineers, architects, solution engineers  
**Objective:** Showcase 4 CDC pipeline patterns and help audience choose the right approach

**Key Messages:**
1. Snowflake provides native CDC capabilities (Streams, Tasks, Dynamic Tables)
2. Multiple patterns available - choose based on requirements
3. Production-ready patterns with audit trails
4. No external tools needed for complex CDC scenarios

---

## Pre-Demo Checklist

- [ ] Run `00_initialization.sql` (database, tables, stream created)
- [ ] Run at least Pipeline 2 and Pipeline 4 (most relevant)
- [ ] Verify access to FACTSET share `ETF_DATA.PUBLIC.CONSTITUENTS`
- [ ] Check if share has recent updates (stream might be empty if no changes)
- [ ] Open Snowflake UI with worksheets ready
- [ ] Have architecture diagram visible
- [ ] Test queries return data

---

## Demo Flow

### Introduction (5 minutes)

**Setup the Problem:**

"Today we're looking at a common scenario: maintaining ETF constituent data with full change tracking. We need to:
- Capture all changes (INSERT, UPDATE, DELETE)
- Maintain current state in Iceberg format
- Export audit trail to Parquet for compliance
- Process efficiently at scale"

**Show Source Data:**

```sql
-- Show source table (FACTSET share)
SELECT * FROM ETF_DATA.PUBLIC.CONSTITUENTS LIMIT 10;

-- Explain the data
SELECT 
    FUND_ID,
    COUNT(*) AS CONSTITUENT_COUNT,
    SUM(MARKET_VALUE) AS TOTAL_MARKET_VALUE
FROM ETF_DATA.PUBLIC.CONSTITUENTS
GROUP BY FUND_ID;
```

**Talk Track:**
- "This is our source - ETF constituent data from FACTSET share"
- "We're using the actual FACTSET share: ETF_DATA.PUBLIC.CONSTITUENTS"
- "Notice the business keys: FUND_ID, TICKER, AS_OF_DATE"

---

### Part 1: Streams & CDC Basics (10 minutes)

**Create/Show Stream:**

```sql
-- Show the stream
DESC STREAM CONSTITUENTS_STREAM;

-- Check if it has data
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- Show stream contents
SELECT 
    METADATA$ACTION,
    METADATA$ISUPDATE,
    FUND_ID,
    TICKER,
    WEIGHT
FROM CONSTITUENTS_STREAM
LIMIT 10;
```

**Talk Track:**
- "Streams capture CDC automatically - no triggers needed"
- "METADATA$ACTION tells us INSERT or DELETE"
- "METADATA$ISUPDATE=TRUE means this is an update, not a new record"
- "This works on shared tables too - stream in your schema, source in share"

**Note About Changes:**

Since we're using the FACTSET share (read-only), changes come from the share provider:

```sql
-- We CANNOT modify the shared table directly
-- Changes come from FACTSET updates to ETF_DATA.PUBLIC.CONSTITUENTS
-- Stream captures those changes automatically
```

**Show Stream After Changes:**

```sql
-- See the captured changes
SELECT 
    CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
    END AS OP_TYPE,
    FUND_ID,
    TICKER,
    WEIGHT
FROM CONSTITUENTS_STREAM
ORDER BY OP_TYPE;
```

**Talk Track:**
- "See how we mapped metadata to operation types"
- "ADD - completely new record"
- "UPDATE - modification to existing"
- "DELETE - removed record"
- "This is the foundation for all our patterns"

---

### Part 2: Pattern Demo - Simple Direct Processing (10 minutes)

**Show Pipeline 2 (Stream → Task → Iceberg):**

```sql
-- Show the task definition
SHOW TASKS LIKE 'PIPELINE2%';

DESC TASK PIPELINE2_STREAM_TO_ICEBERG_MERGE_TASK;
```

**Explain Pattern:**

**Talk Track:**
- "This is the simplest pattern - stream directly to task"
- "Task only runs when stream has data - saves compute"
- "It does DELETEs first, then MERGEs for INSERT/UPDATE"
- "All logic in the task - simple but effective"

**Show Task Logic:**

```sql
-- Pseudo-code (show in editor)
CREATE TASK PIPELINE2_...
WHEN SYSTEM$STREAM_HAS_DATA('CONSTITUENTS_STREAM')
AS
BEGIN
  -- 1. Process DELETEs
  DELETE FROM ICEBERG_TABLE
  WHERE key IN (SELECT key FROM STREAM WHERE METADATA$ACTION = 'DELETE');
  
  -- 2. MERGE INSERTs and UPDATEs
  MERGE INTO ICEBERG_TABLE
  USING (SELECT * FROM STREAM WHERE METADATA$ACTION = 'INSERT')
  ON keys_match
  WHEN MATCHED THEN UPDATE ...
  WHEN NOT MATCHED THEN INSERT ...;
END;
```

**Manually Execute Task:**

```sql
-- Force execute for demo
EXECUTE TASK PIPELINE2_STREAM_TO_ICEBERG_MERGE_TASK;

-- Check results
SELECT * FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
WHERE TICKER IN ('DEMO', 'AAPL');

-- Verify JNJ was deleted
SELECT COUNT(*) FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
WHERE TICKER = 'JNJ';  -- Should be 0
```

**Talk Track:**
- "Task executed successfully"
- "DEMO record was added"
- "AAPL weight was updated"
- "JNJ was deleted"
- "Stream is now consumed - has no more data"

---

### Part 3: Pattern Demo - With Audit Trail (10 minutes)

**Show Pipeline 4 (Stream → Task → Iceberg + Parquet):**

```sql
SHOW TASKS LIKE 'PIPELINE4%';

DESC TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;
```

**Explain Pattern:**

**Talk Track:**
- "This pattern adds audit trail export"
- "Same MERGE logic as Pipeline 2"
- "Plus COPY INTO to export CDC events to Parquet"
- "Parquet includes OP_TYPE, timestamps, and all metadata"
- "Perfect for compliance and debugging"

**Monitor for Changes:**

```sql
-- Check if FACTSET has updated the share (creates stream data)
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- If stream has data, execute task manually
EXECUTE TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;
```

**Show Parquet Export:**

```sql
-- List exported files
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline4_cdc/;

-- Query the Parquet files
SELECT 
    OP_TYPE,
    COUNT(*) AS EVENT_COUNT,
    MIN(PROCESSED_TS) AS FIRST_EVENT,
    MAX(PROCESSED_TS) AS LAST_EVENT
FROM PIPELINE4_CDC_AUDIT_TRAIL
GROUP BY OP_TYPE;

-- Show sample events
SELECT 
    FUND_ID,
    TICKER,
    OP_TYPE,
    WEIGHT,
    PROCESSED_TS
FROM PIPELINE4_CDC_AUDIT_TRAIL
ORDER BY PROCESSED_TS DESC
LIMIT 10;
```

**Talk Track:**
- "Every change is preserved in Parquet format"
- "Includes operation type, all business columns, and timestamps"
- "Can partition by date, op_type, or other fields"
- "External systems can consume these files"
- "Full audit trail for compliance"

---

### Part 4: Dynamic Tables (Optional - 5 minutes)

**Show Pipeline 1 (Stream → DT → Task):**

```sql
-- Show Dynamic Table
SHOW DYNAMIC TABLES LIKE 'CONSTITUENTS_CURRENT_DT';

-- Query current state from DT
SELECT * FROM CONSTITUENTS_CURRENT_DT
WHERE FUND_ID = 'SPY'
LIMIT 10;

-- Show refresh history
SELECT 
    NAME,
    STATE,
    DATA_TIMESTAMP,
    REFRESH_START_TIME,
    REFRESH_END_TIME
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
    NAME => 'DATA_ENG_DEMO.FACTSET.CONSTITUENTS_CURRENT_DT'
))
ORDER BY DATA_TIMESTAMP DESC
LIMIT 5;
```

**Talk Track:**
- "Dynamic Tables are like materialized views but smarter"
- "They refresh automatically based on source changes"
- "All logic is declarative SQL - very testable"
- "Can query current state without hitting Iceberg"
- "Great for complex transformations"

---

### Part 5: Monitoring & Operations (5 minutes)

**Show Task Monitoring:**

```sql
-- Task execution history
SELECT 
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    ERROR_CODE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC;

-- Stream status
SELECT 
    'Stream has data: ' || 
    SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM') AS STATUS;
```

**Show Health Checks:**

```sql
-- Verify data integrity
SELECT 
    'Source records' AS METRIC,
    COUNT(*) AS VALUE
FROM ETF_DATA.PUBLIC.CONSTITUENTS
UNION ALL
SELECT 
    'Iceberg records',
    COUNT(*)
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
UNION ALL
SELECT 
    'CDC events exported',
    COUNT(*)
FROM PIPELINE4_CDC_AUDIT_TRAIL;
```

**Talk Track:**
- "Built-in monitoring via INFORMATION_SCHEMA"
- "Task history shows success/failure"
- "Stream status tells us if there's pending work"
- "Can alert on failures or lag"

---

### Conclusion & Q&A (5 minutes)

**Summary:**

"We've seen 4 patterns for CDC processing:
1. **Pipeline 1** - Dynamic Table for complex logic
2. **Pipeline 2** - Simplest direct processing
3. **Pipeline 3** - Full audit with Dynamic Tables
4. **Pipeline 4** - Balanced approach with audit trail

**Most teams use Pipeline 4** for the balance of simplicity and functionality."

**Key Takeaways:**

"Key points to remember:
- ✅ Streams capture CDC automatically
- ✅ Tasks can be stream-attached (run only when needed)
- ✅ Dynamic Tables for declarative, testable logic
- ✅ Parquet exports for audit and compliance
- ✅ All native Snowflake - no external tools
- ✅ Production-ready patterns that scale"

**Next Steps:**

"To try this yourself:
1. Clone the demo repo
2. Run initialization script
3. Pick a pipeline pattern
4. Monitor for share updates and observe CDC behavior
5. Adapt to your use case"

---

## Common Questions

**Q: Which pipeline should I use?**  
A: Pipeline 4 for most cases (balanced). Pipeline 3 if budget allows and compliance critical. Pipeline 2 for POCs.

**Q: Can I use this on a shared table?**  
A: Yes! Stream goes in your schema, source can be a share. We demonstrated with local table but pattern is identical.

**Q: What about very large data volumes?**  
A: All patterns scale. Adjust warehouse size, task schedule, and Dynamic Table lag based on volume.

**Q: How do I handle late-arriving data?**  
A: Stream captures it whenever it arrives. Use AS_OF_DATE or timestamp to order. Tasks process in arrival order.

**Q: Cost considerations?**  
A: Pipeline 2 cheapest (task only). Pipeline 3 most expensive (2 DTs + task + storage). Pipeline 4 balanced.

**Q: Can I mix patterns?**  
A: Not on same stream - pick one. But you can use different patterns for different tables.

**Q: What about Iceberg requirements?**  
A: External volume needed for production Iceberg. Demo shows fallback to regular tables if not available.

**Q: How do I debug failures?**  
A: Check TASK_HISTORY for errors. Query stream to see pending data. DT-based patterns easier to debug.

---

## Demo Tips

### Preparation
- Run setup 1 hour before
- Test all queries work
- Have backup data in case stream is empty
- Practice the flow 2-3 times

### Delivery
- Start with the problem (CDC requirements)
- Show simplest pattern first (Pipeline 2)
- Build up to more complex (Pipeline 4)
- Use architecture diagrams
- Live execute tasks - shows it really works

### Common Pitfalls
- Stream might be empty if FACTSET hasn't updated the share - explain this is normal with real shares
- Tasks might fail first time - have error handling ready
- Iceberg might not be available - mention it's optional, demo uses regular tables as fallback
- Audience might get lost in details - keep high-level

### Time Management
- 5 min intro
- 10 min streams basics
- 10 min Pipeline 2
- 10 min Pipeline 4
- 5 min monitoring
- 5 min Q&A
- **TOTAL: 45 minutes**

For 30-minute version: Skip Dynamic Tables section and one pipeline pattern.

---

## Success Criteria

Demo is successful if audience can:
- ✅ Explain what Streams capture
- ✅ Understand INSERT vs UPDATE vs DELETE handling
- ✅ Choose between Pipeline 2 and Pipeline 4
- ✅ Know when to use Dynamic Tables
- ✅ Understand Parquet audit trail benefits

---

**Good luck with your demo! 🚀**

