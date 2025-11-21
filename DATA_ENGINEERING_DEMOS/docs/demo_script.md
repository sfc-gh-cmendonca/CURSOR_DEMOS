# Data Engineering Demo - Presentation Script

Complete demo delivery guide for Snowflake data engineering infrastructure and demos.

## Demo Overview

**Duration:** 30-45 minutes
**Audience:** Data engineers, architects, technical decision makers
**Focus:** Infrastructure setup and FACTSET ETF CDC patterns

**Note:** This project provides infrastructure setup only. The main demo is the FACTSET ETF Constituents demo showcasing CDC patterns.

---

## Pre-Demo Checklist

- [ ] Snowflake account accessible
- [ ] FACTSET share `ETF_DATA.PUBLIC.CONSTITUENTS` accessible
- [ ] Snowflake UI opened and logged in
- [ ] Demo scripts reviewed
- [ ] Network connectivity verified

---

## Demo Flow

### Part 1: Infrastructure Overview (10 minutes)

#### Introduction

**Talk Track:**
- "Today I'll show you Snowflake's data engineering capabilities"
- "We'll cover infrastructure setup and a real-world CDC pipeline"
- "All code is production-ready and reusable"

#### Show Project Structure

```bash
cd DATA_ENGINEERING_DEMOS
tree -L 2 -I 'venv|__pycache__|*.pyc'
```

**Talk Track:**
- "Project organized for easy navigation"
- "Main setup creates infrastructure - database, schemas, warehouses"
- "Individual demos are self-contained in demos/ folder"
- "Python utilities for session management, logging, data sharing"

#### Show Configuration

Open `config.py`:

```python
# Database Configuration
DATABASE = "DATA_ENG_DEMO"
SCHEMA_RAW = "RAW_DATA"
SCHEMA_CURATED = "CURATED"
SCHEMA_ANALYTICS = "ANALYTICS"

# Warehouse Configuration
WAREHOUSE_LOAD = "DATA_ENG_LOAD_WH"
WAREHOUSE_TRANSFORM = "DATA_ENG_XFORM_WH"
WAREHOUSE_ANALYTICS = "DATA_ENG_ANALYTICS_WH"
```

**Talk Track:**
- "Everything is configurable in one place"
- "Warehouse sizing based on workload type"
- "Schema separation for data maturity levels"

#### Run Infrastructure Setup

```bash
python setup.py --connection_name demo_connection --mode full
```

**Talk Track:**
- "Setup creates database, schemas, warehouses, stages, and file formats"
- "Takes about 1-2 minutes"
- "Idempotent - safe to run multiple times"
- "No sample data created - infrastructure only"

#### Show Created Objects in Snowflake UI

```sql
-- Show database and schemas
SHOW DATABASES LIKE 'DATA_ENG_DEMO';
SHOW SCHEMAS IN DATABASE DATA_ENG_DEMO;

-- Show warehouses
SHOW WAREHOUSES LIKE 'DATA_ENG%';

-- Show stages
USE DATABASE DATA_ENG_DEMO;
USE SCHEMA RAW_DATA;
SHOW STAGES;

-- Show file formats
SHOW FILE FORMATS;
```

**Talk Track:**
- "Clean namespace structure"
- "Warehouses sized for different workload types"
- "Stages ready for multi-format ingestion"
- "Infrastructure is now ready for demos"

---

### Part 2: FACTSET ETF Constituents Demo (20-30 minutes)

#### Navigate to Demo

```bash
cd demos/factset_etf_iceberg
```

**Talk Track:**
- "This demo showcases CDC (Change Data Capture) patterns"
- "Source is FACTSET's ETF_DATA share - real production data"
- "Four different pipeline patterns to choose from"
- "Shows Streams, Dynamic Tables, Tasks, and Iceberg"

#### Show Demo Architecture

Open `README.md` and show architecture diagram:

**Talk Track:**
- "Source: FACTSET share ETF_DATA.PUBLIC.CONSTITUENTS"
- "Stream captures changes automatically"
- "Four pipeline patterns for different use cases"
- "Output: Iceberg table + Parquet audit trail"

#### Configure and Initialize

```sql
-- Run configuration
@demos/factset_etf_iceberg/config_factset.sql

-- Run initialization
@demos/factset_etf_iceberg/sql/00_initialization.sql
```

**Talk Track:**
- "Configuration sets all parameters"
- "SOURCE_TABLE is hardcoded to FACTSET share"
- "Initialization creates stream on shared table"
- "Stream lives in your schema, references the share"
- "Completely supported pattern by Snowflake"

#### Show Stream on Shared Table

```sql
-- Verify stream created
SHOW STREAMS IN SCHEMA DATA_ENG_DEMO.FACTSET;

-- Check stream metadata
DESC STREAM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM;

-- Count source records
SELECT COUNT(*) FROM ETF_DATA.PUBLIC.CONSTITUENTS;

-- Check if stream has data
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');
```

**Talk Track:**
- "Stream created successfully on shared table"
- "This is a fully supported Snowflake feature"
- "Stream captures changes AFTER it's created"
- "Source has [X] records"
- "Stream will capture all future changes from FACTSET"

#### Pipeline Pattern Comparison

Open `docs/pipeline_comparison.md`:

**Talk Track:**
- "Pipeline 1: Stream → DT → Task → Iceberg (complex transformations)"
- "Pipeline 2: Stream → Task → Iceberg (simple, direct)"
- "Pipeline 3: Stream → DT → Task → Iceberg + Parquet (compliance)"
- "Pipeline 4: Stream → Task → Iceberg + Parquet (most common)"

#### Run Pipeline 4 (Most Common)

```sql
-- Set up Pipeline 4
@demos/factset_etf_iceberg/sql/04_pipeline_stream_task_iceberg_parquet.sql

-- Verify task created
SHOW TASKS IN SCHEMA DATA_ENG_DEMO.FACTSET;

-- Check task definition
DESC TASK PIPELINE4_STREAM_MERGE_AND_COPY_PARQUET_TASK;
```

**Talk Track:**
- "This is the most balanced approach"
- "Stream-attached task - runs only when stream has data"
- "Performs both MERGE to Iceberg and COPY to Parquet"
- "Single task handles everything"
- "Production-ready pattern"

#### Show CDC Logic

Open `sql/04_pipeline_stream_task_iceberg_parquet.sql` and highlight:

```sql
-- CDC operation mapping
CASE
    WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
    WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
    WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
END AS OP_TYPE
```

**Talk Track:**
- "Stream metadata tells us INSERT, UPDATE, or DELETE"
- "We map this to our operation types"
- "MERGE handles all operation types correctly"
- "DELETE then MERGE pattern for accuracy"

#### Explain Limitations with Shared Tables

**Talk Track:**
- "Important: FACTSET share is read-only"
- "We cannot simulate changes directly"
- "Changes come from FACTSET updates only"
- "In production, this is exactly what you want"
- "Stream automatically captures when they update"

#### Monitor for Changes

```sql
-- Check if stream has captured any changes
SELECT SYSTEM$STREAM_HAS_DATA('DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM');

-- View any pending changes
SELECT 
    CASE
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = FALSE THEN 'ADD'
        WHEN METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE THEN 'UPDATE'
        WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE'
    END AS OP_TYPE,
    COUNT(*) as COUNT
FROM DATA_ENG_DEMO.FACTSET.CONSTITUENTS_STREAM
GROUP BY OP_TYPE;
```

**Talk Track:**
- "Stream may or may not have data depending on FACTSET updates"
- "If empty, it's because no changes since stream creation"
- "This is normal behavior with real shares"
- "When FACTSET updates, stream captures automatically"

#### Show Iceberg Table

```sql
-- View Iceberg table
SELECT * FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
LIMIT 10;

-- Count records
SELECT COUNT(*) FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG;

-- Show recent updates (if any processing occurred)
SELECT *
FROM DATA_ENG_DEMO.ICEBERG.CONSTITUENTS_ICEBERG
WHERE LAST_UPDATED_TIMESTAMP > DATEADD('hour', -1, CURRENT_TIMESTAMP())
LIMIT 10;
```

**Talk Track:**
- "Iceberg table maintains current state"
- "ACID compliant - all operations transactional"
- "Time travel capabilities built in"
- "Perfect for production analytics"

#### Show Task Monitoring

```sql
-- Check task execution history
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'PIPELINE%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;

-- Show task definition
SELECT 
    NAME,
    STATE,
    SCHEDULE,
    CONDITION,
    DEFINITION
FROM TABLE(INFORMATION_SCHEMA.TASKS)
WHERE NAME LIKE 'PIPELINE%';
```

**Talk Track:**
- "Tasks can be scheduled or stream-attached"
- "Stream-attached is more efficient - runs only when needed"
- "Full execution history for monitoring"
- "Easy to debug with detailed logs"

#### Show Parquet Exports

```sql
-- List exported Parquet files
LIST @FACTSET_ETF_STAGE/REPORTING/pipeline4_cdc/;

-- Show file details
SELECT 
    "name" as FILE_NAME,
    "size" as SIZE_BYTES,
    "last_modified" as LAST_MODIFIED
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
ORDER BY LAST_MODIFIED DESC
LIMIT 10;
```

**Talk Track:**
- "Parquet files provide audit trail"
- "Includes OP_TYPE, timestamps, all metadata"
- "Perfect for compliance requirements"
- "Can be shared with external systems"

---

### Part 3: Key Takeaways (5 minutes)

#### Summary

**Talk Track:**
- "We've seen infrastructure setup in minutes"
- "Complete CDC pipeline with real production data"
- "Four different patterns to choose from"
- "Production-ready, idempotent, well-documented"

#### Best Practices Highlighted

1. **Infrastructure as Code**
   - All configuration in version control
   - Parameterized and reusable
   - Idempotent operations

2. **CDC Patterns**
   - Streams for automatic change capture
   - Dynamic Tables for declarative logic
   - Tasks for orchestration
   - Stream-attached for efficiency

3. **Data Formats**
   - Iceberg for analytics (ACID, time travel)
   - Parquet for compliance (audit trail)
   - Both maintained automatically

4. **Real Production Data**
   - FACTSET share integration
   - Streams on shared tables work seamlessly
   - Read-only source protection

#### Next Steps

**Talk Track:**
- "Try this yourself - all code is in the repo"
- "Start with infrastructure setup"
- "Then explore the FACTSET demo"
- "Adapt patterns to your use cases"
- "Everything is production-ready"

---

## Common Questions

### Q: Can we use this with our own data?
**A:** Absolutely! The infrastructure supports any data source. Replace the FACTSET share with your own tables and the patterns work exactly the same.

### Q: What if we don't have the FACTSET share?
**A:** The FACTSET demo requires that specific share. However, you can adapt the patterns to any source table - just change the SOURCE_TABLE configuration.

### Q: How much does this cost?
**A:** Costs depend on:
- Warehouse usage (auto-suspend minimizes idle costs)
- Storage (Iceberg + Parquet)
- Task execution frequency
All components are configured for cost efficiency.

### Q: Is this production-ready?
**A:** Yes! All patterns follow Snowflake best practices:
- Idempotent DDL/DML
- Proper error handling
- Monitoring built-in
- Security considered
Some customization may be needed for your specific requirements.

### Q: Can we modify the shared table?
**A:** No. Shared tables are read-only. The share provider (FACTSET) controls all modifications. This is a security feature.

---

## Tips for Delivery

### Pacing
- 10 min infrastructure
- 20-30 min FACTSET demo
- 5 min wrap-up and Q&A

### Audience Engagement
- Ask about their current CDC challenges
- Relate patterns to their use cases
- Encourage questions throughout

### Common Pitfalls
- Stream might be empty if FACTSET hasn't updated - explain this is normal
- Tasks might not execute immediately - show manual execution option
- Iceberg setup requires external volume - mention regular table fallback

### Customization
- Focus on pipeline patterns most relevant to audience
- Deep dive on CDC logic if technical audience
- High-level overview if executive audience

---

**Demo Version:** 2.0 (Infrastructure + FACTSET)  
**Last Updated:** 2025-11-18
