---
globs: *.py,*.sql
---

# Semantic Views Development Patterns

## CRITICAL: Semantic View Creation Rules
**MANDATORY**: Follow these exact patterns for all semantic view development

### Complete Syntax Pattern
```sql
CREATE OR REPLACE SEMANTIC VIEW <database>.<schema>.<view_name>
	TABLES (
		<table_alias> AS <physical_table_name>
			PRIMARY KEY (column1, column2) 
			WITH SYNONYMS=('synonym1','synonym2') 
			COMMENT='Table description'
	)
	RELATIONSHIPS (
		<relationship_name> AS <table_alias>(foreign_key_column) REFERENCES <table_alias>(primary_key_column)
	)
	DIMENSIONS (
		<table_alias>.<alias_name> AS <actual_column_name> WITH SYNONYMS=('synonym1','synonym2') COMMENT='Description'
	)
	METRICS (
		<table_alias>.<alias_name> AS <aggregation_function>(<actual_column_name>) WITH SYNONYMS=('synonym1','synonym2') COMMENT='Description'
	)
	COMMENT='View description';
```

### Section-by-Section Patterns

#### TABLES Section Pattern
```sql
TABLES (
	<table_alias> AS <database>.<schema>.<physical_table_name>
		PRIMARY KEY (column1, column2) 
		WITH SYNONYMS=('synonym1','synonym2') 
		COMMENT='Table description'
)
```

**Examples:**
```sql
-- ✅ CORRECT
ACTUALS AS ENRICHED_DATA.EARNINGS_ACTUALS
	PRIMARY KEY (TICKER, FISCAL_QUARTER, METRIC_NAME)
	WITH SYNONYMS=('earnings_results','financial_results')
	COMMENT='Actual quarterly earnings results'

-- ❌ WRONG - reversed order
ENRICHED_DATA.EARNINGS_ACTUALS AS ACTUALS
```

#### RELATIONSHIPS Section Pattern
```sql
RELATIONSHIPS (
	<relationship_name> AS <table_alias>(foreign_key_column) REFERENCES <table_alias>(primary_key_column)
)
```

**Examples:**
```sql
-- ✅ CORRECT
ACTUALS_TO_COMPANIES AS ACTUALS(TICKER) REFERENCES COMPANIES(TICKER)

-- ❌ WRONG - missing table aliases
ACTUALS(TICKER) REFERENCES COMPANIES(TICKER)
```

#### DIMENSIONS Section Pattern (CRITICAL)
```sql
DIMENSIONS (
	<table_alias>.<alias_name> AS <actual_column_name> WITH SYNONYMS=('synonym1','synonym2') COMMENT='Description'
)
```

**Key Rule**: `<actual_column_name>` MUST exist in the physical table

**Examples:**
```sql
-- ✅ CORRECT - TICKER exists in RAW_DATA.COMPANIES table
COMPANIES.COMPANY_TICKER AS TICKER WITH SYNONYMS=('symbol','stock_ticker') COMMENT='Company ticker symbol'

-- ✅ CORRECT - COMPANY_NAME exists in RAW_DATA.COMPANIES table  
COMPANIES.COMPANY_NAME AS COMPANY_NAME WITH SYNONYMS=('company','firm_name') COMMENT='Company name'

-- ❌ WRONG - COMPANY_TICKER does not exist as column in physical table
COMPANIES.TICKER AS COMPANY_TICKER WITH SYNONYMS=('symbol','stock_ticker')
```

#### METRICS Section Pattern (CRITICAL)
```sql
METRICS (
	<table_alias>.<alias_name> AS <aggregation_function>(<actual_column_name>) WITH SYNONYMS=('synonym1','synonym2') COMMENT='Description'
)
```

**Key Rule**: Must use aggregation functions (SUM, AVG, COUNT, MAX, MIN, etc.)

**Examples:**
```sql
-- ✅ CORRECT - Uses aggregation function
ACTUALS.TOTAL_ACTUAL AS SUM(ACTUAL_VALUE) WITH SYNONYMS=('sum_actual','total_reported') COMMENT='Sum of actual values'

-- ✅ CORRECT - Uses aggregation function
ESTIMATES.AVG_ESTIMATE AS AVG(ESTIMATE_VALUE) WITH SYNONYMS=('mean_consensus','average_forecast') COMMENT='Average estimate'

-- ❌ WRONG - No aggregation function
ACTUALS.ACTUAL_VALUE AS ACTUAL_VALUE WITH SYNONYMS=('reported_value')
```

### Critical Syntax Rules

#### ✅ CORRECT Patterns
```sql
-- Table declaration
HOLDINGS AS SAM_DEMO.CURATED.FACT_POSITION_DAILY_ABOR

-- Relationship declaration  
HOLDINGS_TO_PORTFOLIOS AS HOLDINGS(PORTFOLIOID) REFERENCES PORTFOLIOS(PORTFOLIOID)

-- Dimension (alias_name AS actual_column_name)
PORTFOLIOS.PORTFOLIO_NAME AS PORTFOLIO_NAME WITH SYNONYMS=('fund_name','strategy_name')

-- Metric (alias_name AS aggregation_function)
HOLDINGS.TOTAL_MARKET_VALUE AS SUM(MARKET_VALUE) WITH SYNONYMS=('exposure','aum')
```

#### ❌ WRONG Patterns  
```sql
-- Wrong table order
SAM_DEMO.CURATED.FACT_POSITION_DAILY_ABOR AS HOLDINGS

-- Wrong dimension format (actual_column AS alias)
PORTFOLIOS.PORTFOLIO_NAME AS FUND_NAME

-- Wrong metric format (no aggregation)
HOLDINGS.MARKET_VALUE AS MARKET_VALUE

-- Duplicate expression names
ACTUALS.ACTUAL_VALUE AS SUM(ACTUAL_VALUE)
ACTUALS.TOTAL_VALUE AS SUM(ACTUAL_VALUE)  -- Same source column twice

-- Reserved word usage
HOLDINGS.SELECT AS SELECT_VALUE  -- SELECT is reserved

-- Duplicate synonyms across dimensions/metrics
SECURITIES: synonyms=('company_name')
ISSUERS: synonyms=('company_name')  -- Conflict!
```

### Formatting Requirements (MANDATORY)

- **Indentation**: Use tabs, not spaces
- **Synonyms**: Use `WITH SYNONYMS=('syn1','syn2')` format (equals sign, no spaces)
- **Comments**: Include meaningful comments for all elements
- **Case Sensitivity**: Use exact column names from `DESCRIBE TABLE <physical_table>`
- **No PUBLIC Keyword**: Never use PUBLIC in DIMENSIONS or METRICS sections
- **Unique Synonyms**: Each synonym can only appear once across all dimensions and metrics
- **Unique Expressions**: Each table.column can only appear once in METRICS section

### Column Name Verification Process

**MANDATORY**: Before creating semantic views, verify actual column names:

```python
# 1. Check table structure
session.sql("DESCRIBE TABLE RAW_DATA.COMPANIES").show()
session.sql("DESCRIBE TABLE RAW_DATA.CONSENSUS_ESTIMATES").show()
session.sql("DESCRIBE TABLE ENRICHED_DATA.EARNINGS_ACTUALS").show()

# 2. Use exact column names in semantic view
# If DESCRIBE shows column 'TICKER', use:
COMPANIES.COMPANY_TICKER AS TICKER  # ✅ CORRECT

# NOT:
COMPANIES.TICKER AS COMPANY_TICKER  # ❌ WRONG
```

### Error Handling Pattern

```python
def create_semantic_view(session: Session) -> None:
    semantic_view_sql = """..."""
    
    try:
        result = session.sql(semantic_view_sql).collect()
        print("✅ Semantic view created successfully")
    except Exception as e:
        print(f"❌ Failed to create semantic view: {str(e)}")
        print(f"📋 Full SQL attempted:")
        print(semantic_view_sql)
        print("❓ Please help fix the SQL syntax error above")
        raise
```

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid identifier 'COLUMN_NAME'` | Column doesn't exist in physical table | Run `DESCRIBE TABLE` and use actual column name |
| `Duplicate expression name` | Same table.column used twice in METRICS | Use different source columns or combine logic |
| `You can only define aliases` | Snowpark parsing conflict | SQL syntax likely correct, issue with Snowpark |
| `Unexpected 'FACTS'` | FACTS section not supported | Use METRICS section instead |
| `syntax error` | Invalid section format | Check TABLES(), RELATIONSHIPS(), DIMENSIONS(), METRICS() |

### Complete Working Example

```sql
CREATE OR REPLACE SEMANTIC VIEW ANALYTICS.EARNINGS_ANALYSIS_VIEW
	TABLES (
		ACTUALS AS ENRICHED_DATA.EARNINGS_ACTUALS
			PRIMARY KEY (TICKER, FISCAL_QUARTER, METRIC_NAME)
			WITH SYNONYMS=('earnings_results','financial_results')
			COMMENT='Actual quarterly earnings results',
		ESTIMATES AS RAW_DATA.CONSENSUS_ESTIMATES  
			PRIMARY KEY (TICKER, FISCAL_QUARTER, METRIC_NAME, PROVIDER)
			WITH SYNONYMS=('consensus_estimates','analyst_estimates')
			COMMENT='Consensus estimates from data providers',
		COMPANIES AS RAW_DATA.COMPANIES
			PRIMARY KEY (TICKER)
			WITH SYNONYMS=('companies_master','company_info')
			COMMENT='Company master data'
	)
	RELATIONSHIPS (
		ACTUALS_TO_COMPANIES AS ACTUALS(TICKER) REFERENCES COMPANIES(TICKER),
		ESTIMATES_TO_COMPANIES AS ESTIMATES(TICKER) REFERENCES COMPANIES(TICKER)
	)
	DIMENSIONS (
		COMPANIES.COMPANY_TICKER AS TICKER WITH SYNONYMS=('symbol','stock_ticker') COMMENT='Company stock ticker',
		COMPANIES.COMPANY_NAME AS COMPANY_NAME WITH SYNONYMS=('company','firm_name') COMMENT='Company name',
		ACTUALS.FISCAL_QUARTER AS FISCAL_QUARTER WITH SYNONYMS=('period','quarter') COMMENT='Fiscal quarter',
		ACTUALS.METRIC_NAME AS METRIC_NAME WITH SYNONYMS=('financial_metric','kpi') COMMENT='Financial metric'
	)
	METRICS (
		ACTUALS.TOTAL_ACTUAL AS SUM(ACTUAL_VALUE) WITH SYNONYMS=('sum_actual','total_reported') COMMENT='Sum of actual results',
		ESTIMATES.AVG_ESTIMATE AS AVG(ESTIMATE_VALUE) WITH SYNONYMS=('mean_consensus','average_forecast') COMMENT='Average consensus estimate'
	)
	COMMENT='Earnings analysis semantic view for Cortex Analyst';
```

### Testing and Validation Patterns

#### Semantic View Testing Pattern (MANDATORY)
**CRITICAL**: Use these exact patterns for testing semantic views:

```sql
-- Basic functionality test
SELECT * FROM SEMANTIC_VIEW(
    {semantic_view_name}
    METRICS {primary_metric}
    DIMENSIONS {primary_dimension}
) LIMIT 5;

-- Complex query test
SELECT * FROM SEMANTIC_VIEW(
    {semantic_view_name}
    METRICS {metric1}, {metric2}
    DIMENSIONS {dimension1}, {dimension2}, {dimension3}
) LIMIT 10;

-- Business scenario test (use actual business queries your agents will run)
SELECT * FROM SEMANTIC_VIEW(
    {semantic_view_name}
    DIMENSIONS {relevant_dimensions}
    METRICS {relevant_metrics}
    WHERE {business_filters}
) LIMIT 20;
```

#### Testing Examples for Each View:

**EARNINGS_ANALYSIS_VIEW:**
```sql
-- Basic test
SELECT * FROM SEMANTIC_VIEW(
    ANALYTICS.EARNINGS_ANALYSIS_VIEW
    METRICS TOTAL_ACTUAL
    DIMENSIONS TICKER
) LIMIT 5;

-- Complex test
SELECT * FROM SEMANTIC_VIEW(
    ANALYTICS.EARNINGS_ANALYSIS_VIEW
    METRICS TOTAL_ACTUAL, AVG_ESTIMATE
    DIMENSIONS TICKER, FISCAL_QUARTER, METRIC_NAME
) LIMIT 10;
```

**THEMATIC_RESEARCH_VIEW:**
```sql
-- Basic test
SELECT * FROM SEMANTIC_VIEW(
    ANALYTICS.THEMATIC_RESEARCH_VIEW
    METRICS AVG_PRICE
    DIMENSIONS TICKER
) LIMIT 5;
```

**CLIENT_MARKET_IMPACT_VIEW:**
```sql
-- Basic test
SELECT * FROM SEMANTIC_VIEW(
    ANALYTICS.CLIENT_MARKET_IMPACT_VIEW
    METRICS ENGAGEMENT_COUNT
    DIMENSIONS CLIENT_NAME
) LIMIT 5;
```

### Development Workflow

1. **Plan the semantic view** - identify tables, relationships, dimensions, metrics
2. **Verify column names** - run `DESCRIBE TABLE` on each physical table
3. **Create the SQL** - follow exact syntax patterns above
4. **Test creation** - use error handling pattern to debug issues
5. **Validate functionality** - use SEMANTIC_VIEW() testing patterns above

**CRITICAL**: Semantic views are required for Cortex Analyst - regular SQL views will NOT work.