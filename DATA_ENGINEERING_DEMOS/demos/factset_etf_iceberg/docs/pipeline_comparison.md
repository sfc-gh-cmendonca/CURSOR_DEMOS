# Pipeline Pattern Comparison Guide

Detailed comparison of the 4 CDC pipeline patterns for FACTSET ETF Constituents processing.

## Quick Comparison Matrix

| Feature | Pipeline 1 | Pipeline 2 | Pipeline 3 | Pipeline 4 |
|---------|-----------|-----------|-----------|-----------|
| **Pattern** | DT → Task → Iceberg | Stream → Task → Iceberg | DT → Task → Iceberg + Parquet | Stream → Task → Iceberg + Parquet |
| **Complexity** | Medium | Low | High | Medium |
| **# of Objects** | 3 (Stream, DT, Task) | 2 (Stream, Task) | 4 (Stream, 2 DTs, Task) | 2 (Stream, Task) |
| **Parquet Export** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Audit Trail** | Limited | Limited | ✅ Full | ✅ Full |
| **Testability** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Maintenance** | Easy | Easy | Medium | Easy |
| **Compute Cost** | Medium | Low | High | Medium |
| **Storage Cost** | Low | Low | High | Medium |
| **Best For** | Complex logic | Simple pipelines | Compliance/audit | PoC/testing |

---

## Pipeline 1: Stream → Dynamic Table → Task → Iceberg

### Architecture

```
ETF_DATA.PUBLIC.CONSTITUENTS (FACTSET Share)
         │
         ▼ (CDC Capture)
   CONSTITUENTS_STREAM
         │
         ▼ (Declarative transformation)
  CONSTITUENTS_CURRENT_DT
   (Dynamic Table - current state)
         │
         ▼ (Scheduled MERGE)
   PIPELINE1_MERGE_DT_TO_ICEBERG_TASK
         │
         ▼
 CONSTITUENTS_ICEBERG
```

### Key Characteristics

**Pros:**
- ✅ **Declarative Logic** - DT SQL is testable and reusable
- ✅ **Separation of Concerns** - State computation separate from writes
- ✅ **Multiple Consumers** - DT can feed multiple tasks/views
- ✅ **Automatic Refresh** - DT updates on source changes
- ✅ **Query Performance** - Can query current state from DT directly

**Cons:**
- ❌ Requires Dynamic Table support (not all regions/editions)
- ❌ Higher compute cost (DT refresh + task execution)
- ❌ Additional latency (DT lag + task schedule)
- ❌ No built-in audit trail

### When to Use

- **Complex transformations** requiring business logic
- **Multiple downstream consumers** of current state
- **Development teams** needing testable, reusable components
- **Analytical queries** on current state without hitting Iceberg

### Code Example

```sql
-- Dynamic Table maintains current state
CREATE DYNAMIC TABLE CONSTITUENTS_CURRENT_DT
TARGET_LAG = '5 minutes'
AS
SELECT ... FROM CONSTITUENTS_STREAM
-- Complex logic to resolve INSERT/UPDATE/DELETE

-- Task simply merges from DT
CREATE TASK PIPELINE1_MERGE_DT_TO_ICEBERG_TASK
AS
MERGE INTO CONSTITUENTS_ICEBERG
USING CONSTITUENTS_CURRENT_DT
ON ...;
```

---

## Pipeline 2: Stream → Task (Stream-Attached) → Iceberg

### Architecture

```
ETF_DATA.PUBLIC.CONSTITUENTS (FACTSET Share)
         │
         ▼ (CDC Capture)
   CONSTITUENTS_STREAM
         │
         ▼ (WHEN SYSTEM$STREAM_HAS_DATA)
 PIPELINE2_STREAM_TO_ICEBERG_MERGE_TASK
   (DELETE then MERGE logic)
         │
         ▼
 CONSTITUENTS_ICEBERG
```

### Key Characteristics

**Pros:**
- ✅ **Simplest Pattern** - Minimal objects (stream + task)
- ✅ **Efficient** - Only runs when data available
- ✅ **Low Latency** - Direct stream-to-table processing
- ✅ **Lowest Compute Cost** - Single operation per execution
- ✅ **Easy to Understand** - All logic in one place

**Cons:**
- ❌ All logic in task (less testable)
- ❌ Can't query intermediate state
- ❌ Harder to debug failures
- ❌ No audit trail of changes

### When to Use

- **Simple CDC requirements** with minimal transformation
- **Cost optimization** is priority
- **Low latency** requirements
- **Proof of concepts** and quick implementations
- **Small to medium data volumes** (<1M rows/batch)

### Code Example

```sql
CREATE TASK PIPELINE2_STREAM_TO_ICEBERG_MERGE_TASK
WHEN SYSTEM$STREAM_HAS_DATA('CONSTITUENTS_STREAM')
AS
BEGIN
  -- Delete first
  DELETE FROM CONSTITUENTS_ICEBERG ...;
  
  -- Then merge inserts/updates
  MERGE INTO CONSTITUENTS_ICEBERG ...;
END;
```

---

## Pipeline 3: Stream → Dynamic Table → Task → Iceberg + Parquet

### Architecture

```
ETF_DATA.PUBLIC.CONSTITUENTS (FACTSET Share)
         │
         ▼ (CDC Capture)
   CONSTITUENTS_STREAM
         │
    ┌────┴────────────┐
    ▼                 ▼
CURRENT_DT    PIPELINE3_DT_MERGE_AND_COPY_TASK
(State)         (reads Stream directly for Parquet)
    │                 │
    │           ┌─────┴─────┐
    │           ▼           ▼
    │       ICEBERG    PARQUET Files
    │      (Current)   (CDC from Stream)
    └──────►│
```

**Key:** Parquet export reads CDC events **directly from Stream**, not from DT or Iceberg

### Key Characteristics

**Pros:**
- ✅ **Complete Audit Trail** - All CDC changes in Parquet directly from Stream
- ✅ **Compliance Ready** - Full change history preserved
- ✅ **Dual Output** - Both current state (Iceberg) and CDC log (Parquet)
- ✅ **Data Sharing** - Parquet files for external consumers
- ✅ **Testable** - State logic in Dynamic Table
- ✅ **Efficient CDC Export** - Reads directly from Stream (no intermediate DT)

**Cons:**
- ❌ **Multiple Objects** - Dynamic Table + Task to manage
- ❌ **Dependency** - Requires Pipeline 1's CURRENT_DT
- ❌ **Higher Storage** - Iceberg + Parquet copies
- ❌ **Two-Step Process** - DT refresh then task execution

### When to Use

- **Regulatory compliance** requirements
- **Audit trail** mandatory
- **Data sharing** with partners/external systems
- **Historical analysis** of changes over time
- **Debugging** - need to trace all changes
- **Financial services**, healthcare, or regulated industries

### Code Example

```sql
-- Reuses CONSTITUENTS_CURRENT_DT from Pipeline 1

-- Task does both MERGE and COPY
CREATE TASK PIPELINE3_DT_MERGE_AND_COPY_TASK
AS
BEGIN
  -- MERGE current state from DT into Iceberg
  MERGE INTO CONSTITUENTS_ICEBERG
  USING CONSTITUENTS_CURRENT_DT ...;
  
  -- COPY CDC events DIRECTLY from Stream to Parquet
  COPY INTO @stage/pipeline3_cdc/
  FROM (
    SELECT *,
      CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'INSERT' THEN 'ADD'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
      END AS OP_TYPE
    FROM CONSTITUENTS_STREAM
  ) ...;
END;
```

**Note:** CDC events written to Parquet come **directly from the Stream**, not from Iceberg or an intermediate Dynamic Table.

---

## Pipeline 4: Stream → Task (Stream-Attached) → Iceberg + Parquet

### Architecture

```
ETF_DATA.PUBLIC.CONSTITUENTS (FACTSET Share)
         │
         ▼ (CDC Capture)
   CONSTITUENTS_STREAM
         │
         ▼ (WHEN SYSTEM$STREAM_HAS_DATA)
PIPELINE4_STREAM_MERGE_AND_COPY_TASK
   (reads Stream directly for both outputs)
         │
    ┌────┴────┐
    ▼         ▼
ICEBERG    PARQUET Files
(Current)  (CDC from Stream)
```

**Key:** Both MERGE to Iceberg and COPY to Parquet read **directly from Stream** in the same task execution.

### Key Characteristics

**Pros:**
- ✅ **Simplest Pattern** - Single object (task)
- ✅ **Stream-Attached** - Only runs when data available
- ✅ **Complete Solution** - Does everything in one task
- ✅ **Lowest Latency** - Direct stream-to-output
- ✅ **Cost Efficient** - Minimal objects to maintain
- ✅ **Most Common** - Standard industry pattern
- ✅ **Easy to Understand** - All logic in one place
- ✅ **Direct CDC Export** - Parquet written directly from Stream

**Cons:**
- ❌ **Monolithic** - All logic in single task (harder to test)
- ❌ **No Intermediate State** - Can't query processing state
- ❌ **Less Reusable** - Logic embedded in task
- ❌ **Higher Storage** - Both Iceberg and Parquet maintained

### When to Use

- **Most production scenarios** - Balanced approach
- **Audit trail required** with cost efficiency
- **Simple to medium complexity** transformations
- **Minimal object management** preference
- **Quick implementation** needed
- **Standard CDC pattern** - industry best practice

### Code Example

```sql
CREATE TASK PIPELINE4_STREAM_MERGE_AND_COPY_TASK
WHEN SYSTEM$STREAM_HAS_DATA('CONSTITUENTS_STREAM')
AS
BEGIN
  -- Step 1: DELETE rows
  DELETE FROM CONSTITUENTS_ICEBERG
  WHERE ... (keys from stream WHERE METADATA$ACTION = 'DELETE');
  
  -- Step 2: MERGE INSERT/UPDATE
  MERGE INTO CONSTITUENTS_ICEBERG
  USING (SELECT ... FROM CONSTITUENTS_STREAM WHERE METADATA$ACTION = 'INSERT') ...;
  
  -- Step 3: COPY CDC events DIRECTLY from Stream to Parquet
  COPY INTO @stage/pipeline4_cdc/
  FROM (
    SELECT *,
      CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'INSERT' THEN 'ADD'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
      END AS OP_TYPE
    FROM CONSTITUENTS_STREAM
  ) ...;
END;
```

**Note:** CDC audit trail comes **directly from the Stream** in the same task execution, ensuring all CDC events are captured.

---

## Decision Tree: Which Pipeline to Use?

```
Do you need Parquet audit trail?
│
├─ NO ───────────────────┐
│                         │
│  Complex logic needed?  │
│  ├─ YES → Pipeline 1   │
│  └─ NO  → Pipeline 2   │
│                         │
└─ YES ──────────────────┤
                          │
    Multiple consumers?   │
    ├─ YES → Pipeline 3  │
    └─ NO  → Pipeline 4  │
```

### Quick Selection Guide

**Choose Pipeline 1 if:**
- Complex business logic required
- Multiple downstream consumers
- Need to query intermediate state
- Testability is priority

**Choose Pipeline 2 if:**
- Simplest possible solution needed
- Cost optimization critical
- Direct stream-to-table sufficient
- Proof of concept or MVP

**Choose Pipeline 3 if:**
- Regulatory compliance mandatory
- Full audit trail required
- Multiple outputs from same stream
- Budget allows for comprehensive solution

**Choose Pipeline 4 if:**
- Audit trail needed but budget-conscious
- Balanced approach desired
- Single consumer with CDC export
- **Most common choice for production**

---

## Performance Comparison

### Latency

| Pipeline | End-to-End Latency | Components |
|----------|-------------------|------------|
| **Pipeline 1** | DT lag (5min) + Task schedule (5min) = **~10 min** | Stream → DT → Task |
| **Pipeline 2** | Stream delay + Task schedule = **~10-15 min** | Stream → Task |
| **Pipeline 3** | 2× DT lag (5min each) + Task = **~15-20 min** | Stream → 2 DTs → Task |
| **Pipeline 4** | Stream delay + Task schedule = **~10-15 min** | Stream → Task |

*Actual latency depends on data volume, warehouse size, and schedules*

### Compute Costs (Relative)

- **Pipeline 1:** Medium (DT refresh + task) = **1.0×**
- **Pipeline 2:** Low (task only) = **0.5×**
- **Pipeline 3:** High (2 DTs + task + COPY) = **2.0×**
- **Pipeline 4:** Medium (task + COPY) = **0.75×**

### Storage Costs (Relative)

- **Pipeline 1:** Low (Iceberg only) = **1.0×**
- **Pipeline 2:** Low (Iceberg only) = **1.0×**
- **Pipeline 3:** High (Iceberg + DTs + Parquet) = **2.5×**
- **Pipeline 4:** Medium (Iceberg + Parquet) = **1.5×**

---

## Migration Between Patterns

### From Pipeline 2 → Pipeline 1

**Why:** Need more testable, reusable logic

**Steps:**
1. Create `CONSTITUENTS_CURRENT_DT`
2. Modify task to use DT instead of stream
3. Test with both running, then disable Pipeline 2

**Effort:** Low

---

### From Pipeline 1 → Pipeline 3

**Why:** Add audit trail requirement

**Steps:**
1. Create `CONSTITUENTS_CDC_DT`
2. Add `COPY INTO` statement to existing task
3. Test Parquet exports
4. Deploy

**Effort:** Low

---

### From Pipeline 2 → Pipeline 4

**Why:** Add audit trail to simple pipeline

**Steps:**
1. Add `COPY INTO` block to existing task
2. Test Parquet exports
3. Create view on Parquet files
4. Deploy

**Effort:** Very Low

---

## Common Patterns in Production

Based on real-world usage:

1. **70% use Pipeline 4** - Best balance for most use cases
2. **20% use Pipeline 1** - Complex transformations or enterprise
3. **8% use Pipeline 3** - Regulated industries (finance, healthcare)
4. **2% use Pipeline 2** - PoCs or very simple use cases

---

## Testing Recommendations

### Pipeline 1 & 3 (DT-based)

✅ Easy to test - query DTs directly  
✅ Can validate logic before enabling tasks  
✅ Test by monitoring FACTSET share updates (read-only)  

```sql
-- Test DT logic
SELECT * FROM CONSTITUENTS_CURRENT_DT;
SELECT * FROM CONSTITUENTS_CDC_DT WHERE OP_TYPE = 'UPDATE';
```

### Pipeline 2 & 4 (Task-only)

❌ Harder to test - logic in task  
⚠️ Must execute task to test  
⚠️ Need good monitoring  

```sql
-- Manually execute task for testing
EXECUTE TASK PIPELINE2_STREAM_TO_ICEBERG_MERGE_TASK;

-- Check results
SELECT * FROM CONSTITUENTS_ICEBERG;
```

---

## Recommendations by Use Case

### Financial Services (Compliance-heavy)
**Recommended:** Pipeline 3  
**Why:** Full audit trail, regulatory compliance, traceable

### E-commerce (High volume)
**Recommended:** Pipeline 4  
**Why:** Efficient with audit, handles scale, cost-effective

### SaaS Analytics (Real-time dashboards)
**Recommended:** Pipeline 1  
**Why:** Query DT for current state, multiple consumers

### Startup/MVP (Quick to market)
**Recommended:** Pipeline 2  
**Why:** Simple, fast to implement, lowest cost

### Enterprise Data Warehouse
**Recommended:** Pipeline 3 or 4  
**Why:** Need audit + governance, multiple stakeholders

---

## Summary

All 4 patterns are valid and production-ready. Your choice depends on:

1. **Compliance requirements** - Need audit trail?
2. **Budget** - Cost vs. functionality tradeoff
3. **Complexity** - How much logic needed?
4. **Team skills** - Comfortable with Dynamic Tables?
5. **Use case** - Analytical vs. operational?

**Most Common Choice:** Pipeline 4 (Stream → Task → Iceberg + Parquet)  
**Safest Choice:** Pipeline 3 (Stream → DT → Task → Iceberg + Parquet)  
**Simplest Choice:** Pipeline 2 (Stream → Task → Iceberg)  
**Most Flexible:** Pipeline 1 (Stream → DT → Task → Iceberg)

