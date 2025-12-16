#!/bin/bash

# FACTSET ETF CDC Demo - Complete Setup Script
# Uses factset_demo connection configured in ~/.snowsql/config

set -e  # Exit on error

# Set SnowSQL path
SNOWSQL="/Users/cmendonca/Applications/SnowSQL.app/Contents/MacOS/snowsql"

echo "🚀 FACTSET ETF CDC Demo Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Navigate to demo directory
cd /Users/cmendonca/Git/CURSOR_DEMOS/DATA_ENGINEERING_DEMOS/demos/factset_etf_iceberg

echo "📋 Step 1: Loading configuration..."
$SNOWSQL -c factset_demo -f config_factset.sql -o quiet=true -o friendly=false

echo ""
echo "🏗️  Step 2: Initializing environment..."
$SNOWSQL -c factset_demo -f sql/00_initialization.sql -o quiet=true -o friendly=false

echo ""
echo "⚙️  Step 3: Deploying Pipeline 1 (Iceberg table)..."
$SNOWSQL -c factset_demo -f sql/01_pipeline_stream_task_iceberg.sql -o quiet=true -o friendly=false

echo ""
echo "⚙️  Step 4: Deploying Pipeline 2 (Parquet CDC)..."
$SNOWSQL -c factset_demo -f sql/02_pipeline_stream_task_iceberg_parquet.sql -o quiet=true -o friendly=false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ✅ ✅ DEMO SETUP COMPLETE! ✅ ✅ ✅"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Verify setup:"
echo "  $SNOWSQL -c factset_demo -q \"SHOW TASKS IN SCHEMA DATA_ENG_DEMO.FACTSET\""
echo ""
echo "📖 Monitor tasks:"
echo "  $SNOWSQL -c factset_demo -q \"SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY()) WHERE NAME LIKE 'pipeline%' ORDER BY SCHEDULED_TIME DESC LIMIT 5\""
echo ""
echo "🗑️  Cleanup when done:"
echo "  $SNOWSQL -c factset_demo -f sql/99_cleanup.sql"
echo ""

