# Snowflake Data Engineering Demos - Sub-Demos Collection

This directory contains specialized, self-contained demos showcasing advanced Snowflake data engineering patterns.

## Available Demos

### 1. FACTSET ETF Constituents - Iceberg/Parquet ETL

**Path:** `factset_etf_iceberg/`

**Overview:** Comprehensive CDC (Change Data Capture) demo showcasing 4 different pipeline patterns for processing ETF constituent data using Snowflake Streams, Dynamic Tables, Tasks, and Iceberg tables with Parquet exports.

**Key Features:**
- 4 independent pipeline patterns (choose the best for your use case)
- Streams on shared tables (or local sources)
- Dynamic Tables for declarative transformations
- Tasks with stream-attached execution
- Iceberg tables for ACID compliance
- Parquet exports for audit trails
- Complete INSERT/UPDATE/DELETE handling

**Technologies:**
- Snowflake Streams
- Dynamic Tables
- Tasks (scheduled & stream-attached)
- Iceberg Tables
- Parquet File Format
- CDC Patterns

**Duration:** 30-45 minutes (setup + demo)

**Best For:**
- Understanding CDC patterns in Snowflake
- Choosing between different ETL/ELT approaches
- Learning Streams, Dynamic Tables, and Tasks
- Implementing audit trails and compliance
- Financial services, regulated industries

**Documentation:**
- [README.md](factset_etf_iceberg/README.md) - Full documentation
- [QUICK_START.md](factset_etf_iceberg/QUICK_START.md) - 10-minute quick start
- [Pipeline Comparison](factset_etf_iceberg/docs/pipeline_comparison.md) - Pattern comparison
- [Demo Script](factset_etf_iceberg/docs/demo_script.md) - Presentation guide

**Quick Start:**
```sql
-- 1. Configure
@demos/factset_etf_iceberg/config_factset.sql

-- 2. Initialize
@demos/factset_etf_iceberg/sql/00_initialization.sql

-- 3. Run a pipeline (choose one)
@demos/factset_etf_iceberg/sql/04_pipeline_stream_task_iceberg_parquet.sql

-- 4. Simulate changes
@demos/factset_etf_iceberg/sql/simulate_changes.sql
```

**SQL Scripts:**
- `00_initialization.sql` - Environment setup
- `01_pipeline_dt_task_iceberg.sql` - Pattern 1: DT → Task → Iceberg
- `02_pipeline_stream_task_iceberg.sql` - Pattern 2: Stream → Task → Iceberg  
- `03_pipeline_dt_task_iceberg_parquet.sql` - Pattern 3: DT → Task → Iceberg + Parquet
- `04_pipeline_stream_task_iceberg_parquet.sql` - Pattern 4: Stream → Task → Iceberg + Parquet
- `simulate_changes.sql` - Test data generator
- `99_cleanup.sql` - Complete cleanup

---

## Demo Structure

Each sub-demo follows this standard structure:

```
demo_name/
├── README.md                    # Full documentation
├── QUICK_START.md              # Fast-track setup (optional)
├── config_*.sql                # Configuration parameters
├── sql/                        # SQL scripts
│   ├── 00_initialization.sql   # Environment setup
│   ├── 01-0N_*.sql            # Main demo scripts
│   └── 99_cleanup.sql         # Cleanup script
├── docs/                       # Additional documentation
│   ├── demo_script.md         # Presentation guide
│   └── *.md                   # Technical docs
└── scripts/                    # Helper scripts (optional)
```

## Adding New Demos

To add a new sub-demo:

1. Create directory under `demos/`
2. Follow the structure above
3. Include comprehensive README
4. Provide cleanup script
5. Update this index

## Usage Guidelines

### Before Running

1. Read the demo's README.md
2. Check prerequisites
3. Configure parameters in config file
4. Ensure you have appropriate Snowflake privileges

### During Demo

1. Run initialization first
2. Follow the demo script or quick start
3. Test with provided simulation scripts
4. Monitor execution (task history, streams, etc.)

### After Demo

1. Run cleanup script to remove all objects
2. Review costs in Snowflake UI
3. Suspend warehouses if not auto-suspend

## Demo Categories

### CDC & Streaming
- **FACTSET ETF Iceberg** - CDC patterns with Streams and Tasks

### Coming Soon
- **Real-time IoT Pipeline** - Streaming data with Snowpipe
- **ML Feature Store** - Snowpark ML with feature engineering
- **Data Mesh** - Multi-domain architecture with data products

## Support

For issues or questions:
1. Check the demo's README and documentation
2. Review Snowflake documentation links
3. Examine task execution history for errors
4. Verify stream and table states

## Contributing

To contribute a new demo:
1. Follow the standard structure
2. Include comprehensive documentation
3. Provide working code with sample data
4. Test end-to-end before submission
5. Update this index

---

**Main Project:** [DATA_ENGINEERING_DEMOS](../README.md)  
**Version:** 1.0  
**Last Updated:** 2025-11-18

