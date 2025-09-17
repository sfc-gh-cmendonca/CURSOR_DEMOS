---
description: Guidelines for synthetic data generation ensuring realistic correlations
---

# Data Generation Framework

## Master Event Log Strategy
The MASTER_EVENT_LOG table drives all data generation to ensure realistic correlations:
- Create 5-10 major market events first
- All subsequent data (prices, news, filings) must reference these events
- Events should affect multiple companies to show cross-sector impact

## Data Correlation Requirements
- Stock prices must show volatility on event dates
- News articles must be generated based on events in MASTER_EVENT_LOG
- SEC filings must reference events in MD&A sections
- Earnings transcripts must include analyst questions about events

## Unstructured Data Generation Process
1. Generate dynamic prompts using Python f-strings with structured data context
2. Store prompts in temporary Snowflake table
3. Create Snowpark DataFrame from prompt table
4. Use with_column() to add cortex.complete() generated content
5. Save results to permanent Snowflake table

## Dynamic Date Generation (CRITICAL)
**MANDATORY**: All data generation must use dynamic dates based on current execution date

### Configuration-Based Approach
```python
# In config.py
NUM_HISTORICAL_QUARTERS = 8    # Configurable quarters to generate
NUM_HISTORICAL_YEARS = 3       # Calculated from quarters
```

### Dynamic Date Utilities
```python
# Use these utilities for all date generation
from utils.date_utils import get_historical_quarters, get_dynamic_date_range

# For quarterly data (earnings, estimates)
quarters = get_historical_quarters()  # Returns 8 quarters from current date
recent_quarters = get_historical_quarters()[:3]  # Last 3 quarters

# For daily data (prices, events, trading)
start_date, end_date = get_dynamic_date_range()  # 2-year span from quarters
```

### Implementation Rules
- **NEVER use hardcoded dates** like "2024-01-01" or "2024-Q1"
- **Always calculate** dates relative to datetime.now()
- **Make time periods configurable** through config.py
- **Ensure demo relevance** by using current/recent quarters

## Data Volume Guidelines
- **Companies**: 10-15 real tickers (AAPL, MSFT, GOOGL, etc.)
- **Clients**: 20-25 fictional institutional clients
- **History**: Dynamic based on NUM_HISTORICAL_QUARTERS (default: 8 quarters/2 years)
- **Events**: 5-10 market-moving events spread across dynamic date range

## Quality Assurance
- Every agent question in scenarios must have supporting data
- Cross-reference event dates across all generated tables
- Ensure sentiment scores align with event types (positive/negative)
- Validate that geographic revenue exposure data supports risk scenarios

## Marketplace Data
- Use the "Finance & Economics" Snowflake Marketplace dataset