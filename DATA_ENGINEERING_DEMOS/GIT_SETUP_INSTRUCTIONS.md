# Git Setup and Sharing Instructions

## Step 1: Initialize Git Repository

```bash
cd /Users/cmendonca/Git/CURSOR_DEMOS/DATA_ENGINEERING_DEMOS

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "feat: Snowflake CDC demo with FACTSET ETF data

- Pure SQL implementation (no Python required)
- 2 independent stream-based CDC pipelines
- Pipeline 1: Stream → Iceberg table (current state)
- Pipeline 2: Stream → Parquet files (CDC audit only)
- No Dynamic Tables (they cannot read from Streams)
- PRD-compliant with proper CDC handling
- Completely self-contained demos"
```

## Step 2: Create GitHub Repository

### Option A: Using GitHub CLI (if installed)
```bash
# Create public repo
gh repo create DATA_ENGINEERING_DEMOS --public --source=. --remote=origin

# Push code
git push -u origin main
```

### Option B: Using GitHub Web UI
1. Go to https://github.com/new
2. Repository name: `DATA_ENGINEERING_DEMOS`
3. Description: `Snowflake Data Engineering Demo - FACTSET ETF CDC Pipelines`
4. Choose: **Public** (so customers can access)
5. Click "Create repository"
6. Then run:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS.git

# Rename branch to main (if needed)
git branch -M main

# Push code
git push -u origin main
```

## Step 3: Get Shareable Link

After pushing, your repository will be available at:

```
https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS
```

### Direct Link to Demo
```
https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS/tree/main/demos/factset_etf_iceberg
```

### Direct Link to Summary
```
https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS/blob/main/DEMO_SUMMARY.md
```

## Step 4: Share with Customer

Send them:

**📧 Email Template:**

```
Subject: Snowflake CDC Demo - FACTSET ETF Data Pipeline

Hi [Customer Name],

I've prepared a comprehensive Snowflake CDC demo showcasing production-ready 
Change Data Capture patterns using FACTSET ETF Constituents data.

🔗 Demo Repository: https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS

📊 Key Features:
• Pure SQL implementation (no Python required)
• 2 independent CDC pipelines (Iceberg table + Parquet audit trail)
• Stream-based architecture (production-ready)
• Complete documentation and setup guides

📋 Quick Links:
• Demo Summary: https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS/blob/main/DEMO_SUMMARY.md
• FACTSET Demo: https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS/tree/main/demos/factset_etf_iceberg
• Quick Start: https://github.com/YOUR_USERNAME/DATA_ENGINEERING_DEMOS/blob/main/demos/factset_etf_iceberg/QUICK_START.md

⏱️ Setup Time: 5-10 minutes
📖 Prerequisites: Snowflake account + FACTSET share access

Let me know if you have any questions!

Best regards,
[Your Name]
```

## Alternative: Share as ZIP

If you prefer not to use GitHub:

```bash
cd /Users/cmendonca/Git/CURSOR_DEMOS

# Create ZIP file
zip -r DATA_ENGINEERING_DEMOS.zip DATA_ENGINEERING_DEMOS \
  -x "*.pyc" "*__pycache__*" "*.DS_Store"

# The ZIP file can be shared via email or cloud storage
```

## Key Files to Highlight

When sharing with customers, point them to:

1. **DEMO_SUMMARY.md** - Executive overview
2. **demos/factset_etf_iceberg/README.md** - Complete demo guide
3. **demos/factset_etf_iceberg/QUICK_START.md** - 10-minute setup
4. **sql/00_setup_infrastructure.sql** - Infrastructure setup
5. **demos/factset_etf_iceberg/sql/** - All pipeline SQL files

## Repository README

Make sure your repository has a good README for visibility. The existing 
README.md at the root is already comprehensive and customer-ready.

