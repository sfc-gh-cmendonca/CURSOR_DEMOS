# 📊 Data Directory

This directory is designed to hold sample data files for your JPMC Cortex Search lab. The SQL scripts already include sample data in the database, but this folder can contain additional datasets for experimentation and extended learning.

## 🎯 Purpose

The `data/` folder serves as a staging area for:
- **Sample financial documents** (PDFs, text files)
- **CSV files** with market data for bulk loading
- **JSON files** with structured financial content
- **Test datasets** for search experimentation
- **Export files** from search results

## 📁 Recommended Structure

```
data/
├── documents/           # PDF and text documents
│   ├── research_reports/
│   ├── trading_insights/
│   └── economic_data/
├── csv/                # CSV files for bulk data loading
│   ├── market_research.csv
│   ├── trading_data.csv
│   └── economic_indicators.csv
├── json/               # JSON structured data
│   ├── sample_reports.json
│   └── market_feeds.json
├── exports/            # Search results and analysis exports
└── samples/            # Small test datasets
```

## 🔄 Data Loading Methods

### Method 1: Using the SQL Scripts (Current)
Your database already contains sample data loaded via:
- `sql/02_create_tables.sql` - Creates tables with built-in sample data
- 3 market research reports
- 2 trading insights
- 2 economic indicators

### Method 2: CSV Bulk Loading (Future)
```sql
-- Example: Load additional data from CSV
PUT file://data/csv/market_research.csv @market_documents_stage;

COPY INTO market_research_reports
FROM @market_documents_stage/market_research.csv
FILE_FORMAT = (FORMAT_NAME = 'pdf_format');
```

### Method 3: Python Scripts (Recommended)
```python
# Example: Load data programmatically
from src.database.connection import connection_manager
import pandas as pd

# Load CSV file
df = pd.read_csv('data/csv/additional_reports.csv')

# Insert into database
with connection_manager.get_connection() as conn:
    df.to_sql('market_research_reports', conn, if_exists='append')
```

## 📄 Sample Data Already Available

Your lab includes realistic sample data covering:

### Market Research Reports
- **AI Revolution in Financial Services**: Technology trends and AI opportunities
- **ESG Investment Trends**: Sustainable finance in emerging markets  
- **Central Bank Digital Currencies**: CBDC implications for global finance

### Trading Insights
- **Tech Momentum Strategy**: AI-focused technology stock opportunities
- **USD/JPY Carry Trade**: Interest rate differential opportunities

### Economic Indicators
- **US CPI Data**: Inflation persistence and Fed policy implications
- **ECB Policy Decision**: European interest rate decisions and market impact

## 🧪 Adding Your Own Data

### 1. Document Files
Place PDF or text files in `documents/` subdirectories:
```bash
# Add research reports
cp ~/Downloads/jpmc_research_2024.pdf data/documents/research_reports/

# Add trading insights
cp ~/Downloads/fx_strategy.txt data/documents/trading_insights/
```

### 2. CSV Data Files
Create CSV files with these column structures:

**market_research_reports.csv:**
```csv
report_id,title,content,asset_class,sector,region,analyst_name,publish_date
MRR_2024_004,"Cloud Computing Outlook","Detailed analysis...",technology,software,north_america,"Jane Smith","2024-03-25"
```

**trading_insights.csv:**
```csv
insight_id,title,content,instrument_type,symbol,risk_level,trader_name,publish_date
TI_2024_003,"Energy Sector Play","Oil price dynamics...",equity,XOM,medium,"Mike Johnson","2024-03-22"
```

### 3. JSON Structured Data
```json
{
  "reports": [
    {
      "id": "MRR_2024_005",
      "title": "Cryptocurrency Market Analysis",
      "content": "Bitcoin and Ethereum market dynamics...",
      "metadata": {
        "asset_class": "digital_assets",
        "risk_rating": "high",
        "analyst": "Crypto Research Team"
      }
    }
  ]
}
```

## 🔍 Testing with New Data

After adding data files:

1. **Load into database:**
   ```bash
   # Use Python scripts in src/
   python src/utils/data_loader.py --file data/csv/new_data.csv
   ```

2. **Test search services:**
   ```sql
   -- Test new content
   SELECT PARSE_JSON(
       SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
           'market_research_search',
           '{"query": "your new content topic", "limit": 5}'
       )
   )['results'];
   ```

3. **Run analytics:**
   ```python
   from src.search.cortex_search import MarketResearchSearchService
   
   service = MarketResearchSearchService()
   results = service.search("your search terms")
   print(f"Found {len(results.results)} results")
   ```

## 📋 Data Quality Guidelines

### Content Requirements
- **Minimum content length**: 50 characters (enforced by search services)
- **Rich metadata**: Include relevant attributes for filtering
- **Proper formatting**: Clean text without excessive special characters
- **Realistic dates**: Use recent dates for time-based filtering

### Financial Content Standards
- **Market data**: Include symbols, asset classes, regions
- **Risk classifications**: Use standard risk levels (low, medium, high)
- **Author attribution**: Include analyst/trader names for credibility
- **Performance metrics**: Add engagement scores for ranking

## 🔄 Data Pipeline Integration

Future enhancements can include:
- **Automated document ingestion** from file shares
- **Real-time market data feeds** integration
- **Email/document parsing** for research reports
- **API connections** to financial data providers

## 📚 Example Data Sources

For realistic financial data, consider:
- **SEC filings** (public company reports)
- **Federal Reserve** economic data
- **Academic financial research** papers
- **Market commentary** from financial news
- **Synthetic data generators** for testing

## ⚠️ Important Notes

- **No sensitive data**: Don't store real proprietary information
- **Sample data only**: Use realistic but fictional content
- **Size limits**: Keep individual files under 100MB
- **Format consistency**: Follow established schemas
- **Version control**: Consider `.gitignore` for large files

---

**Ready to start?** The SQL scripts have already loaded sample data, so you can immediately test the Cortex Search services. Add more data here as you expand your experiments! 🚀 