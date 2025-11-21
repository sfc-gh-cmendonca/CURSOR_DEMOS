# Data Engineering Demo - Architecture

Technical architecture documentation for the Snowflake Data Engineering Demo.

## Overview

This project provides infrastructure setup for data engineering demonstrations using Snowflake's native capabilities:
- **Database & Schema Management** - Structured namespace organization
- **Warehouse Configuration** - Compute resource setup
- **Pipeline Infrastructure** - Stages and file formats
- **Data Sharing Components** - Share creation and monitoring utilities

**Note:** This main setup creates **infrastructure only** (no sample data). For complete working demos with data, see:
- **FACTSET ETF Constituents Demo:** `demos/factset_etf_iceberg/` - CDC pipelines with Streams, Tasks, and Iceberg (no Dynamic Tables)

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   MAIN SETUP (Infrastructure Only)               │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE: DATA_ENG_DEMO                       │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  RAW_DATA   │  │   CURATED   │  │  ANALYTICS  │            │
│  │   Schema    │  │    Schema   │  │   Schema    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                   │
│  Empty schemas ready for demo data                              │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        WAREHOUSES                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ LOAD_WH      │  │ TRANSFORM_WH │  │ ANALYTICS_WH │          │
│  │ (MEDIUM)     │  │ (LARGE)      │  │ (XSMALL)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  Compute resources for different workload types                 │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STAGES & FILE FORMATS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CSV_STAGE   │  │  JSON_STAGE  │  │ PARQUET_STAGE│          │
│  │  + Format    │  │  + Format    │  │  + Format    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  Internal stages configured and ready for data ingestion        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                DEMO: FACTSET ETF Constituents                    │
│              (demos/factset_etf_iceberg/)                        │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           ETF_DATA.PUBLIC.CONSTITUENTS (Share)                   │
│                    ↓ (2 Independent Streams)                     │
│              pipeline1_stream | pipeline2_stream                 │
│                    ↓ (2 Pipeline Patterns)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pipeline 1: Stream→Task→Iceberg Table                   │  │
│  │     (Stream-attached task with WHEN clause)              │  │
│  │     ↓                                                     │  │
│  │     CONSTITUENTS_ICEBERG (current state, Iceberg)        │  │
│  │                                                           │  │
│  │  Pipeline 2: Stream→Task→Parquet (CDC Audit Only)        │  │
│  │     (Stream-attached task with WHEN clause)              │  │
│  │     ↓                                                     │  │
│  │     Parquet Files (CDC audit trail only, NO TABLE)       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Note: Pipeline 1 uses Iceberg table (ACID, time travel, SQL)  │
│  Note: Pipeline 2 writes CDC to Parquet only (no table)        │
│  Note: Each pipeline has its own stream (completely independent)│
│  Note: Dynamic Tables NOT used (cannot read from Streams)       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Database & Schema Management

#### Database: DATA_ENG_DEMO
**Purpose:** Central namespace for all data engineering demonstrations

#### Schemas Created:
- **RAW_DATA** - Landing zone for raw ingested data
- **CURATED** - Cleaned and transformed data layer
- **ANALYTICS** - Aggregated analytics and reporting layer

**Note:** These schemas are created empty. Individual demos populate them as needed.

**Characteristics:**
- Time travel enabled (90 days)
- Fail-safe enabled (7 days)
- Change tracking enabled for CDC patterns

### 2. Data Ingestion Infrastructure

#### Stages
- **CSV_STAGE** - Internal stage for CSV files
- **JSON_STAGE** - Internal stage for JSON files
- **PARQUET_STAGE** - Internal stage for Parquet files
- **GENERAL_STAGE** - General purpose stage

**Configuration:**
- Directory enabled for listing files
- Internal encryption enabled
- Ready for COPY INTO operations

#### File Formats
- **CSV_FORMAT** - Comma-delimited with header
- **JSON_FORMAT** - JSON with outer array stripping
- **PARQUET_FORMAT** - Parquet with binary as text
- **PIPE_DELIMITED_FORMAT** - Alternative delimiter format

#### Loading Mechanisms Supported
- **COPY INTO** - Bulk loading from stages
- **Snowpipe** - Continuous micro-batch loading
- **External Tables** - Query data in external storage
- **File Format Auto-Detection** - Automatic format inference

### 3. Pipeline Infrastructure

#### Transformation Components
The setup provides infrastructure for:
- **Streams** - Change data capture for CDC patterns
- **Tasks** - Scheduled or event-driven processing
- **Materialized Views** - Pre-computed aggregations (not used in current demos)
- **Dynamic Tables** - Continuous incremental transformations (not compatible with Streams)

**Note:** The FACTSET demo uses Streams and Tasks only. Dynamic Tables cannot read from Streams in Snowflake, so stream-based CDC pipelines use Tasks directly. See `demos/factset_etf_iceberg/` for implementation.

### 4. Data Sharing Infrastructure

#### Components Created:
- **Share creation utilities** (`src/data_sharing/shares.py`)
- **Share monitoring** (`src/data_sharing/monitoring.py`)

**Capabilities:**
- Create and manage Snowflake Data Shares
- Monitor share usage and access patterns
- Track share consumer activity
- Audit trail for governance

**Note:** No shares are created by default. Create shares as needed for specific demos.

## Compute Infrastructure

### Warehouses

#### DATA_ENG_LOAD_WH (Medium)
- **Purpose:** Data ingestion and loading operations
- **Size:** Medium
- **Auto-suspend:** 5 minutes
- **Auto-resume:** Enabled
- **Use cases:** 
  - COPY INTO operations
  - File staging and uploads
  - Initial data loads
  - Bulk insert operations

#### DATA_ENG_XFORM_WH (Large)
- **Purpose:** Data transformation workloads
- **Size:** Large
- **Auto-suspend:** 5 minutes
- **Auto-resume:** Enabled
- **Use cases:** 
  - Dynamic table refresh operations
  - Complex joins and aggregations
  - Data quality checks
  - CDC processing (MERGE operations)

#### DATA_ENG_ANALYTICS_WH (X-Small)
- **Purpose:** Analytics and querying
- **Size:** X-Small
- **Auto-suspend:** 1 minute
- **Auto-resume:** Enabled
- **Use cases:** 
  - Ad-hoc queries
  - Reporting and dashboards
  - Data exploration
  - Metadata queries

### Warehouse Design Principles
- **Auto-suspend** minimizes costs during idle periods
- **Auto-resume** provides seamless user experience
- **Size appropriate** for workload characteristics
- **Separation** prevents resource contention

## Python Source Code Structure

### Core Modules

#### `config.py`
**Purpose:** Central configuration for all demo parameters

**Key Settings:**
- Database and schema names
- Warehouse configurations
- Snowflake connection settings
- File format specifications

#### `src/config/`
**Purpose:** Configuration package

**Files:**
- `__init__.py` - Package initializer

#### `src/utils/`
**Purpose:** Utility functions for demo execution

**Modules:**
- `snowpark_session.py` - Snowpark session management
  - Session creation with connections.toml
  - Context switching (database, schema, warehouse)
  - Query tagging for monitoring
  
- `date_utils.py` - Dynamic date generation
  - Historical quarter generation
  - Date range calculations
  - Reference date management
  
- `logging_utils.py` - Logging framework
  - Structured logging setup
  - Pipeline timing decorators
  - Error tracking

#### `src/pipelines/`
**Purpose:** ETL/ELT pipeline components

**Modules:**
- `ingestion.py` - Data ingestion utilities
  - Stage setup and management
  - File format configuration
  - COPY INTO wrappers
  
- `transformation.py` - Data transformation logic
  - Curated layer creation
  - Business logic application
  - Aggregation helpers
  
- `validation.py` - Data quality checks
  - NULL detection
  - Format validation
  - Range checks
  - Referential integrity

#### `src/data_sharing/`
**Purpose:** Data sharing functionality

**Modules:**
- `shares.py` - Share creation and management
  - Create/alter/drop shares
  - Grant/revoke access
  - Secure view creation
  
- `monitoring.py` - Share usage tracking
  - Access logging
  - Consumer queries
  - Usage metrics

### Setup Script

#### `setup.py`
**Purpose:** Main orchestration for demo setup

**Functions:**
- `setup_database_and_schemas()` - Database and schema creation
- `setup_warehouses()` - Warehouse provisioning
- `setup_pipeline_infrastructure()` - Stages and file formats
- `main()` - Execution orchestrator

**Command Line Options:**
- `--connection_name` - Snowflake connection to use
- `--mode` - Setup mode (full, quick, cleanup)

## Security & Governance

### Role-Based Access Control (RBAC)
**Recommended Roles:**
- **ACCOUNTADMIN** - Initial setup and configuration
- **SYSADMIN** - Warehouse and database management
- **DATA_ENG_ROLE** - Pipeline execution and data management
- **ANALYST_ROLE** - Read-only analytics access

### Object Permissions
**Principle of Least Privilege:**
- Grant only necessary permissions
- Use roles to group permissions
- Regular permission audits
- Document access patterns

### Data Protection
**Encryption:**
- Data encrypted at rest (automatic)
- Data encrypted in transit (TLS/SSL)
- Encryption key management by Snowflake

**Time Travel:**
- 90-day retention for data recovery
- Point-in-time queries
- Fail-safe 7-day protection

## Monitoring & Observability

### Query History
Track all SQL execution:
```sql
SELECT *
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_TAG = 'DATA_ENG_DEMO_GENERATION'
ORDER BY START_TIME DESC
LIMIT 100;
```

### Warehouse Usage
Monitor compute consumption:
```sql
SELECT *
FROM TABLE(INFORMATION_SCHEMA.WAREHOUSE_METERING_HISTORY(
    DATE_RANGE_START => DATEADD('day', -7, CURRENT_DATE())
))
WHERE WAREHOUSE_NAME LIKE 'DATA_ENG%'
ORDER BY START_TIME DESC;
```

### Storage Metrics
Track storage growth:
```sql
SELECT 
    TABLE_CATALOG || '.' || TABLE_SCHEMA || '.' || TABLE_NAME AS FULL_NAME,
    ROW_COUNT,
    BYTES / POWER(1024, 3) AS SIZE_GB,
    BYTES / ROW_COUNT AS BYTES_PER_ROW
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('RAW_DATA', 'CURATED', 'ANALYTICS')
ORDER BY BYTES DESC;
```

## Demos

### FACTSET ETF Constituents Demo

**Location:** `demos/factset_etf_iceberg/`

**Description:** Production-ready CDC demo showcasing 2 stream-based pipeline patterns for processing ETF constituent data using Streams, Tasks, and Iceberg format with Parquet exports.

**Key Features:**
- Streams on shared tables (ETF_DATA.PUBLIC.CONSTITUENTS)
- Stream-attached tasks with `WHEN SYSTEM$STREAM_HAS_DATA()` conditions
- Iceberg tables for ACID compliance
- Parquet exports for audit trails
- Complete CDC handling (INSERT, UPDATE, DELETE)
- Correct op_type mapping (ADD, UPDATE, DELETE)

**Pipeline Patterns:**
1. **Stream → Task → Iceberg Table** - Current state with ACID compliance
   - Creates dedicated stream on shared table
   - Task performs DELETE then MERGE operations
   - Only executes when stream has data
   - **Creates Iceberg table** for queryable current state with ACID, time travel, schema evolution
   
2. **Stream → Task → Parquet (CDC Audit Only)** - Simplest CDC pattern
   - Creates dedicated stream on shared table
   - Task exports CDC events directly to Parquet
   - Only executes when stream has data
   - **No table created** - purely for CDC audit trail, compliance, data lake integration

**Comparison:**
- **Pipeline 1 (Iceberg Table)**: Queryable current state, ACID, time travel, schema evolution, SQL access
- **Pipeline 2 (Parquet Only)**: Simplest CDC pattern, complete audit trail, no table overhead, data lake ready
- **Both**: Completely independent, each has own stream

**Important Notes:**
- **Dynamic Tables NOT used** - They cannot read from Streams in Snowflake
- **Parquet exports read directly from Stream** - Not from tables, ensuring true CDC audit trail
- **Stream-attached execution** - Tasks only run when `SYSTEM$STREAM_HAS_DATA()` returns TRUE
- **Production-ready** - Idempotent DDL, explicit columns, proper error handling

**Documentation:**
- `demos/factset_etf_iceberg/README.md` - Complete overview
- `demos/factset_etf_iceberg/QUICK_START.md` - 10-minute setup guide
- `demos/factset_etf_iceberg/docs/pipeline_comparison.md` - Pattern comparison
- `demos/factset_etf_iceberg/docs/demo_script.md` - Presentation guide

## Best Practices

### Performance Optimization
1. **Clustering** - Cluster keys on frequently filtered columns
2. **Partitioning** - Leverage micro-partitions naturally
3. **Materialization** - Pre-compute expensive aggregations
4. **Caching** - Utilize result cache for repeated queries

### Cost Management
1. **Auto-suspend** - Minimize idle warehouse costs
2. **Size appropriately** - Right-size warehouses for workload
3. **Monitor usage** - Track compute and storage consumption
4. **Optimize queries** - Reduce scan volume and complexity

### Development Workflow
1. **Version control** - Track all SQL and Python in Git
2. **Environment separation** - Dev/test/prod isolation
3. **CI/CD** - Automated testing and deployment
4. **Documentation** - Maintain architecture and design docs

### Data Quality
1. **Validation** - Check data at ingestion
2. **Monitoring** - Alert on quality issues
3. **Lineage** - Track data transformations
4. **Testing** - Unit tests for transformation logic

## Troubleshooting

### Common Issues

#### Connection Failures
**Symptom:** Unable to connect to Snowflake  
**Solutions:**
- Verify credentials in connections.toml
- Check network connectivity
- Confirm account identifier format
- Validate role permissions

#### Performance Issues
**Symptom:** Queries running slowly  
**Solutions:**
- Check warehouse size
- Review query execution plan
- Add clustering keys
- Optimize joins and filters

#### Permission Errors
**Symptom:** Insufficient privileges messages  
**Solutions:**
- Verify role assignments
- Check object ownership
- Grant necessary permissions
- Use ACCOUNTADMIN for setup

## Additional Resources

- **Snowflake Documentation:** https://docs.snowflake.com
- **Snowpark Python:** https://docs.snowflake.com/en/developer-guide/snowpark/python/index
- **Data Sharing:** https://docs.snowflake.com/en/user-guide/data-sharing-intro
- **Dynamic Tables:** https://docs.snowflake.com/en/user-guide/dynamic-tables-intro
- **Streams & Tasks:** https://docs.snowflake.com/en/user-guide/streams-intro

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Snowflake documentation
3. Examine demo-specific README files
4. Contact your Snowflake representative

---

**Last Updated:** 2025-11-20  
**Version:** 3.0 (Infrastructure-only, Stream-based demos)
