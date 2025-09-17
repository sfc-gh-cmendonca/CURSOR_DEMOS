# SQL Patterns and Standards for Snowflake Development

## Core SQL Standards

### Database Object Naming Conventions
- **Databases**: UPPER_CASE (e.g., `MARKETS_AI_DEMO`)
- **Schemas**: UPPER_CASE (e.g., `RAW_DATA`, `ANALYTICS`)
- **Tables**: UPPER_CASE with underscores (e.g., `EARNINGS_DATA`, `RESEARCH_REPORTS`)
- **Columns**: lower_case with underscores (e.g., `company_name`, `earnings_date`)
- **Views**: UPPER_CASE with descriptive suffix (e.g., `EARNINGS_ANALYSIS_VIEW`)

### SQL Formatting Standards
```sql
-- ✅ CORRECT: Well-formatted SQL
CREATE OR REPLACE TABLE earnings_data (
    ticker VARCHAR(10) NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    revenue_millions DECIMAL(15,2),
    net_income_millions DECIMAL(15,2),
    earnings_per_share DECIMAL(10,4),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_earnings PRIMARY KEY (ticker, quarter)
);

-- ❌ WRONG: Poor formatting
CREATE OR REPLACE TABLE earnings_data(ticker VARCHAR(10) NOT NULL,quarter VARCHAR(10) NOT NULL,earnings_date DATE NOT NULL,revenue_millions DECIMAL(15,2),net_income_millions DECIMAL(15,2));
```

## Table Creation Patterns

### Standard Table Template
```sql
CREATE OR REPLACE TABLE {schema}.{table_name} (
    -- Primary key columns first
    {pk_column1} {data_type} NOT NULL,
    {pk_column2} {data_type} NOT NULL,
    
    -- Business columns in logical order
    {business_column1} {data_type},
    {business_column2} {data_type},
    
    -- Metadata columns last
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Constraints
    CONSTRAINT pk_{table_name} PRIMARY KEY ({pk_columns})
);
```

### Data Type Best Practices
```sql
-- Text data
company_name VARCHAR(200)           -- Specific length for names
description TEXT                    -- Unlimited text content
ticker VARCHAR(10)                  -- Short codes with known max length

-- Numeric data
revenue_millions DECIMAL(15,2)      -- Financial amounts with precision
market_cap_billions DECIMAL(10,3)   -- Large numbers with appropriate scale
percentage DECIMAL(5,2)             -- Percentages (e.g., 99.99%)
count_value INTEGER                 -- Whole numbers

-- Date and time
report_date DATE                    -- Dates without time
created_at TIMESTAMP_NTZ            -- Timestamps without timezone
event_datetime TIMESTAMP_LTZ        -- Timestamps with timezone

-- Boolean and flags
is_active BOOLEAN                   -- True/false values
status VARCHAR(20)                  -- Enumerated status values
```

## INSERT Patterns

### Batch Insert Template
```sql
INSERT INTO {schema}.{table_name} (
    column1,
    column2,
    column3
) VALUES
    ('value1a', 'value2a', 'value3a'),
    ('value1b', 'value2b', 'value3b'),
    ('value1c', 'value2c', 'value3c');
```

### Dynamic Insert with Error Handling
```python
def insert_batch_data(session, table_name, data_records):
    """Insert batch data with proper error handling"""
    
    # Prepare values for SQL
    values_list = []
    for record in data_records:
        # Escape single quotes and handle None values
        escaped_values = []
        for value in record.values():
            if value is None:
                escaped_values.append('NULL')
            elif isinstance(value, str):
                escaped_values.append(f"'{value.replace(\"'\", \"''\")}'")
            else:
                escaped_values.append(str(value))
        values_list.append(f"({', '.join(escaped_values)})")
    
    # Build INSERT statement
    columns = ', '.join(data_records[0].keys())
    values_clause = ',\n    '.join(values_list)
    
    insert_sql = f"""
    INSERT INTO {table_name} ({columns})
    VALUES
        {values_clause}
    """
    
    try:
        session.sql(insert_sql).collect()
        logger.info(f"✅ Inserted {len(data_records)} records into {table_name}")
    except Exception as e:
        logger.error(f"❌ Insert failed for {table_name}: {e}")
        logger.error(f"📋 SQL attempted: {insert_sql}")
        raise
```

## Query Patterns

### Basic SELECT Template
```sql
SELECT 
    -- Select specific columns, avoid SELECT *
    t.ticker,
    t.company_name,
    e.quarter,
    e.revenue_millions,
    e.earnings_per_share
FROM {schema}.{table1} t
JOIN {schema}.{table2} e ON t.ticker = e.ticker
WHERE 
    -- Filters with clear conditions
    t.sector = 'Technology'
    AND e.earnings_date >= '2024-01-01'
ORDER BY 
    -- Consistent ordering
    t.ticker,
    e.earnings_date DESC;
```

### Analytical Query Patterns
```sql
-- Aggregation with window functions
SELECT 
    ticker,
    quarter,
    revenue_millions,
    
    -- Year-over-year comparison
    LAG(revenue_millions, 4) OVER (
        PARTITION BY ticker 
        ORDER BY earnings_date
    ) AS revenue_yoy_prior,
    
    -- Calculate YoY growth
    ((revenue_millions - LAG(revenue_millions, 4) OVER (
        PARTITION BY ticker ORDER BY earnings_date
    )) / LAG(revenue_millions, 4) OVER (
        PARTITION BY ticker ORDER BY earnings_date
    )) * 100 AS revenue_yoy_growth_pct,
    
    -- Ranking within period
    RANK() OVER (
        PARTITION BY quarter 
        ORDER BY revenue_millions DESC
    ) AS revenue_rank
FROM earnings_data
WHERE sector = 'Technology'
ORDER BY ticker, earnings_date;
```

## VIEW Creation Patterns

### Standard View Template
```sql
CREATE OR REPLACE VIEW {schema}.{view_name} AS
SELECT 
    -- Business-friendly column names
    c.ticker AS company_ticker,
    c.company_name,
    c.sector,
    e.quarter AS fiscal_quarter,
    e.earnings_date AS report_date,
    
    -- Calculated fields
    e.revenue_millions AS quarterly_revenue_millions,
    e.net_income_millions AS quarterly_profit_millions,
    ROUND(e.earnings_per_share, 3) AS earnings_per_share,
    
    -- Derived metrics
    ROUND((e.revenue_millions / LAG(e.revenue_millions, 4) OVER (
        PARTITION BY c.ticker ORDER BY e.earnings_date
    ) - 1) * 100, 2) AS revenue_yoy_growth_percent
    
FROM raw_data.companies c
JOIN raw_data.earnings_data e ON c.ticker = e.ticker
WHERE c.sector = 'Technology'
ORDER BY c.ticker, e.earnings_date;
```

## Semantic View Patterns

### Complete Semantic View Template
```sql
CREATE OR REPLACE SEMANTIC VIEW {schema}.{semantic_view_name}
TABLES (
    {table_alias} AS {database}.{schema}.{physical_table}
        PRIMARY KEY ({primary_key_columns})
        WITH SYNONYMS=('synonym1','synonym2')
        COMMENT='{table_description}'
)
RELATIONSHIPS (
    {relationship_name} AS {table1}({fk_column}) REFERENCES {table2}({pk_column})
)
DIMENSIONS (
    {table_alias}.{dimension_name} AS {actual_column_name} 
        WITH SYNONYMS=('synonym1','synonym2') 
        COMMENT='{dimension_description}'
)
METRICS (
    {table_alias}.{metric_name} AS {aggregation_function}({actual_column_name})
        WITH SYNONYMS=('synonym1','synonym2')
        COMMENT='{metric_description}'
)
COMMENT='{semantic_view_description}';
```

### Semantic View Best Practices
```sql
-- ✅ CORRECT: Proper semantic view structure
CREATE OR REPLACE SEMANTIC VIEW analytics.earnings_analysis_semantic
TABLES (
    earnings_data AS markets_ai_demo.raw_data.earnings_data
        PRIMARY KEY (ticker, quarter)
        WITH SYNONYMS=('earnings','financial_results')
        COMMENT='Quarterly earnings data for technology companies',
    companies AS markets_ai_demo.raw_data.companies
        PRIMARY KEY (ticker)
        WITH SYNONYMS=('companies_master','company_data')
        COMMENT='Company reference information'
)
RELATIONSHIPS (
    earnings_to_companies AS earnings_data(ticker) REFERENCES companies(ticker)
)
DIMENSIONS (
    companies.ticker AS company_ticker 
        WITH SYNONYMS=('symbol','stock_ticker') 
        COMMENT='Company stock ticker symbol',
    companies.company_name AS company_name 
        WITH SYNONYMS=('company','firm_name') 
        COMMENT='Full company name',
    earnings_data.quarter AS fiscal_quarter 
        WITH SYNONYMS=('period','quarter') 
        COMMENT='Fiscal reporting quarter'
)
METRICS (
    earnings_data.total_revenue AS SUM(revenue_millions) 
        WITH SYNONYMS=('sum_revenue','total_sales') 
        COMMENT='Total quarterly revenue in millions',
    earnings_data.average_eps AS AVG(earnings_per_share) 
        WITH SYNONYMS=('mean_eps','avg_earnings_per_share') 
        COMMENT='Average earnings per share'
)
COMMENT='Semantic view for technology company earnings analysis';
```

## Search Service Patterns

### Cortex Search Service Template
```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE {schema}.{service_name}
ON {content_column}
ATTRIBUTES {id_column}, {title_column}, {additional_attributes}
WAREHOUSE = {warehouse_name}
TARGET_LAG = '{lag_time}'
AS (
    SELECT 
        {id_column},
        {title_column},
        {additional_attributes},
        {content_column}
    FROM {source_table}
    WHERE {filter_conditions}
);
```

### Search Service Best Practices
```sql
-- ✅ CORRECT: Proper search service structure
CREATE OR REPLACE CORTEX SEARCH SERVICE search_services.earnings_transcripts_search
ON full_transcript
ATTRIBUTES transcript_id, title, ticker, quarter, call_date
WAREHOUSE = DEMO_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        transcript_id,
        title,
        ticker,
        quarter,
        call_date,
        full_transcript
    FROM raw_data.earnings_call_transcripts
    WHERE LENGTH(full_transcript) > 100
);
```

## Data Validation Patterns

### Validation Query Templates
```sql
-- Record count validation
SELECT 
    'companies' AS table_name,
    COUNT(*) AS record_count,
    COUNT(DISTINCT ticker) AS unique_tickers
FROM raw_data.companies

UNION ALL

SELECT 
    'earnings_data' AS table_name,
    COUNT(*) AS record_count,
    COUNT(DISTINCT ticker) AS unique_tickers
FROM raw_data.earnings_data;

-- Data quality checks
SELECT 
    ticker,
    COUNT(*) AS quarter_count,
    MIN(earnings_date) AS earliest_date,
    MAX(earnings_date) AS latest_date,
    COUNT(CASE WHEN revenue_millions IS NULL THEN 1 END) AS null_revenue_count
FROM raw_data.earnings_data
GROUP BY ticker
HAVING COUNT(*) != 4  -- Should have 4 quarters per company
ORDER BY ticker;

-- Referential integrity validation
SELECT 
    e.ticker,
    COUNT(*) AS earnings_records
FROM raw_data.earnings_data e
LEFT JOIN raw_data.companies c ON e.ticker = c.ticker
WHERE c.ticker IS NULL
GROUP BY e.ticker;
```

## Performance Optimization Patterns

### Index and Clustering Recommendations
```sql
-- Clustering for large tables
ALTER TABLE raw_data.earnings_data 
CLUSTER BY (ticker, earnings_date);

-- For frequently filtered columns
ALTER TABLE raw_data.companies 
CLUSTER BY (sector);
```

### Query Optimization Patterns
```sql
-- ✅ EFFICIENT: Use specific date ranges
SELECT ticker, revenue_millions
FROM earnings_data
WHERE earnings_date BETWEEN '2024-01-01' AND '2024-12-31'
  AND ticker IN ('AAPL', 'MSFT', 'GOOGL');

-- ❌ INEFFICIENT: Open-ended queries
SELECT * FROM earnings_data
WHERE earnings_date > '2020-01-01';

-- ✅ EFFICIENT: Limit result sets
SELECT ticker, quarter, revenue_millions
FROM earnings_data
WHERE sector = 'Technology'
ORDER BY earnings_date DESC
LIMIT 100;
```

## Error Handling Patterns

### Safe SQL Execution
```python
def execute_sql_safely(session, sql_statement, operation_name):
    """Execute SQL with comprehensive error handling"""
    try:
        result = session.sql(sql_statement).collect()
        logger.info(f"✅ {operation_name} completed successfully")
        return result
    except snowflake.connector.errors.ProgrammingError as e:
        logger.error(f"❌ SQL Error in {operation_name}: {e}")
        logger.error(f"SQL: {sql_statement}")
        raise
    except snowflake.connector.errors.DatabaseError as e:
        logger.error(f"❌ Database Error in {operation_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected Error in {operation_name}: {e}")
        raise
```

### SQL Injection Prevention
```python
# ✅ CORRECT: Use parameterized queries or proper escaping
def build_safe_insert(table_name, data_dict):
    """Build INSERT statement with proper escaping"""
    columns = list(data_dict.keys())
    values = []
    
    for value in data_dict.values():
        if value is None:
            values.append('NULL')
        elif isinstance(value, str):
            # Escape single quotes
            escaped_value = value.replace("'", "''")
            values.append(f"'{escaped_value}'")
        elif isinstance(value, (int, float)):
            values.append(str(value))
        else:
            values.append(f"'{str(value)}'")
    
    sql = f"""
    INSERT INTO {table_name} ({', '.join(columns)})
    VALUES ({', '.join(values)})
    """
    return sql

# ❌ WRONG: Direct string interpolation
def unsafe_insert(table_name, user_input):
    sql = f"INSERT INTO {table_name} VALUES ('{user_input}')"  # Vulnerable!
    return sql
```

## Maintenance and Cleanup Patterns

### Cleanup Script Template
```sql
-- Safe cleanup with existence checks
DROP CORTEX SEARCH SERVICE IF EXISTS search_services.earnings_transcripts_search;
DROP CORTEX SEARCH SERVICE IF EXISTS search_services.research_reports_search;

DROP SEMANTIC VIEW IF EXISTS analytics.earnings_analysis_semantic;
DROP SEMANTIC VIEW IF EXISTS analytics.thematic_research_semantic;

DROP TABLE IF EXISTS raw_data.earnings_call_transcripts;
DROP TABLE IF EXISTS raw_data.research_reports;
DROP TABLE IF EXISTS raw_data.earnings_data;
DROP TABLE IF EXISTS raw_data.companies;

DROP SCHEMA IF EXISTS search_services;
DROP SCHEMA IF EXISTS analytics;
DROP SCHEMA IF EXISTS raw_data;

DROP DATABASE IF EXISTS markets_ai_demo;
```

### Monitoring and Maintenance Queries
```sql
-- Monitor query performance
SELECT 
    query_text,
    total_elapsed_time,
    warehouse_name,
    start_time,
    end_time
FROM table(information_schema.query_history())
WHERE warehouse_name = 'DEMO_WH'
  AND start_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
ORDER BY total_elapsed_time DESC;

-- Monitor warehouse usage
SELECT 
    warehouse_name,
    SUM(credits_used) AS total_credits,
    COUNT(*) AS query_count
FROM table(information_schema.warehouse_metering_history(
    date_range_start => CURRENT_TIMESTAMP - INTERVAL '24 hours'
))
GROUP BY warehouse_name
ORDER BY total_credits DESC;
```
