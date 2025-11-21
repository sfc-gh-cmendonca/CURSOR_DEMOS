# Customer Email Template

Copy and customize this email to share the demo with your customer.

---

**Subject:** Snowflake CDC Demo - FACTSET ETF Data Pipeline

---

Hi [Customer Name],

I've prepared a comprehensive **Snowflake Change Data Capture (CDC) demo** showcasing production-ready patterns using **FACTSET ETF Constituents** data.

## 🔗 Demo Repository
**https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/tree/main/DATA_ENGINEERING_DEMOS**

## 📊 What's Included

This demo showcases **2 independent CDC pipelines** using Snowflake Streams and Tasks:

**Pipeline 1: Stream → Task → Iceberg Table**
- Queryable current state with ACID compliance
- Time travel and schema evolution
- Perfect for: SQL queries on current data

**Pipeline 2: Stream → Task → Parquet Files**
- CDC audit trail only (no table overhead)
- Complete change history (ADD, UPDATE, DELETE)
- Perfect for: Compliance, audit, data lake integration

## 🎯 Key Highlights

✅ **Pure SQL** - No Python dependencies required  
✅ **Stream-Based CDC** - Production-ready Snowflake patterns  
✅ **Independent Pipelines** - Each completely self-contained  
✅ **PRD-Compliant** - Follows all Snowflake best practices  
✅ **FACTSET Data** - Works with your existing ETF_DATA share

## 📚 Quick Links

- **Executive Summary:** [DEMO_SUMMARY.md](https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/blob/main/DATA_ENGINEERING_DEMOS/DEMO_SUMMARY.md)
- **Quick Start (10 min):** [QUICK_START.md](https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/blob/main/DATA_ENGINEERING_DEMOS/demos/factset_etf_iceberg/QUICK_START.md)
- **Complete Guide:** [README.md](https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/blob/main/DATA_ENGINEERING_DEMOS/demos/factset_etf_iceberg/README.md)
- **SQL Scripts:** [sql/](https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/tree/main/DATA_ENGINEERING_DEMOS/demos/factset_etf_iceberg/sql)

## ⏱️ Setup Time
**5-10 minutes** to get both pipelines running

## 📋 Prerequisites
- Snowflake account with ACCOUNTADMIN privileges
- Access to **ETF_DATA.PUBLIC.CONSTITUENTS** share (FACTSET)
- SnowSQL or Snowflake Web UI

## 🚀 Quick Setup

```bash
# 1. Infrastructure setup
snowsql -c your_connection -f sql/00_setup_infrastructure.sql

# 2. Demo setup
cd demos/factset_etf_iceberg
snowsql -c your_connection -f config_factset.sql
snowsql -c your_connection -f sql/00_initialization.sql

# 3. Deploy pipelines
snowsql -c your_connection -f sql/01_pipeline_stream_task_iceberg.sql
snowsql -c your_connection -f sql/02_pipeline_stream_task_iceberg_parquet.sql
```

## 💡 Why This Demo?

This demo solves real business challenges:

**Compliance & Audit**
- Complete CDC audit trail in Parquet format
- Track all changes (ADD, UPDATE, DELETE)
- Ready for regulatory requirements

**Data Lake Integration**
- Export CDC events directly to Parquet
- No table overhead
- Simplest possible CDC pattern

**Current State Queries**
- Iceberg table with ACID compliance
- Time travel for historical analysis
- SQL access to latest data

## 🎓 Learning Outcomes

After running this demo, you'll understand:
- How to create Streams on shared tables
- Stream-attached Tasks with `WHEN SYSTEM$STREAM_HAS_DATA()`
- Iceberg tables vs Regular tables
- CDC op_type mapping (ADD/UPDATE/DELETE)
- Production-ready CDC patterns

## 📞 Questions?

Let me know if you have any questions or need help setting this up!

Best regards,  
[Your Name]

---

**Repository:** https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS  
**Demo:** https://github.com/sfc-gh-cmendonca/CURSOR_DEMOS/tree/main/DATA_ENGINEERING_DEMOS

