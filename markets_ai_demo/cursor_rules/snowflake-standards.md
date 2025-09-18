---
globs: *.py,*.sql
---

# Snowflake Development Standards

## Snowpark Session Management (CRITICAL RULES)
- **MANDATORY**: Always use connections.toml for authentication
- **MANDATORY**: Use Session.builder.config("connection_name", connection_name).create()
- **MANDATORY**: ALL SQL execution must use session.sql(sql_statement).collect()
- **MANDATORY**: Never use direct cursor access (session._conn._cursor)
- **MANDATORY**: Always reuse single session - never create multiple sessions
- Default connection_name: "sfseeurope-mstellwall-aws-us-west3" (configurable via command line)
- Create dedicated warehouses: MARKETS_AI_DEMO_COMPUTE_WH and MARKETS_AI_DEMO_SEARCH_WH

### SQL Execution Requirements
```python
# CORRECT - Always use this pattern for SQL execution
result = session.sql("CREATE TABLE example AS SELECT * FROM source").collect()

# CORRECT - Use Snowpark table method for counting
row_count = session.table("DATABASE.SCHEMA.TABLE_NAME").count()

# ACCEPTABLE - SQL COUNT only when complex WHERE conditions needed
result = session.sql("SELECT COUNT(*) as cnt FROM table WHERE complex_condition").collect()
row_count = result[0]['CNT']

# WRONG - Never do this
cursor = session._conn._cursor
cursor.execute(sql)
```

## Data Generation Patterns
- **Structured data**: Use Snowpark DataFrames exclusively
- **Unstructured data**: Store prompts in Snowflake tables, use cortex.complete() against Snowpark DataFrames
- **Fallback**: If Snowpark not possible, use pandas with session.write_pandas(quote_identifiers=False)

## Naming Conventions
- **Database**: MARKETS_AI_DEMO
- **Schemas**: RAW_DATA, ENRICHED_DATA, ANALYTICS
- **Tables**: UPPER_CASE with underscores
- **Columns**: Follow Snowflake identifier syntax (no spaces, special chars)
- **Company**: "Frost Markets Intelligence" throughout

## AI Component Structure
- **Semantic Views**: Business function based (earnings_analysis, portfolio_exposure, client_activity) - see semantic-views.mdc
- **Search Services**: Document type based (earnings_transcripts, research_reports, news_articles) - see cortex-search.mdc  
- **Agents**: One per scenario, multiple tools per agent

## Configuration Management
- All parameters (data volumes, date ranges, model names) in config.py
- Setup script modes: --mode=full|data-only|ai-only|scenario-specific
- Default Cortex model: llama3.1-70b