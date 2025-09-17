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
- **Semantic Views**: Business function based (earnings_analysis, portfolio_exposure, client_activity)
- **Search Services**: Document type based (earnings_transcripts, research_reports, news_articles)
- **Agents**: One per scenario, multiple tools per agent

## Configuration Management
- All parameters (data volumes, date ranges, model names) in config.py
- Setup script modes: --mode=full|data-only|ai-only|scenario-specific
- Default Cortex model: llama3.1-70b

## Error Handling Patterns
```python
def execute_sql_with_retry(session: Session, sql: str, operation: str, max_retries: int = 3) -> Any:
    """Execute SQL with retry logic and proper error handling"""
    for attempt in range(max_retries):
        try:
            result = session.sql(sql).collect()
            logger.info(f"✅ {operation} - Success")
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ {operation} - Failed after {max_retries} attempts: {e}")
                logger.error(f"📋 SQL that failed: {sql}")
                raise
            else:
                logger.warning(f"⚠️ {operation} - Attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Optimization
- Use appropriate warehouse sizes (M or L for Cortex operations)
- Implement connection pooling for high-volume operations
- Cache frequently accessed metadata
- Use RESULT_SCAN for query result reuse
- Monitor query performance with QUERY_HISTORY views

## Security Best Practices
- Never hardcode credentials in scripts
- Use role-based access control (RBAC)
- Implement least-privilege principle
- Audit and monitor access patterns
- Use secure stages for file uploads

## Testing Patterns
```python
def validate_deployment(session: Session) -> Dict[str, bool]:
    """Comprehensive deployment validation"""
    validation_results = {}
    
    test_cases = [
        ("Database exists", "SHOW DATABASES LIKE 'MARKETS_AI_DEMO'"),
        ("Semantic views", "SHOW SEMANTIC VIEWS IN SCHEMA ANALYTICS"),
        ("Search services", "SHOW CORTEX SEARCH SERVICES IN SCHEMA SEARCH_SERVICES"),
        ("Sample data", "SELECT COUNT(*) FROM RAW_DATA.COMPANIES")
    ]
    
    for test_name, sql in test_cases:
        try:
            result = session.sql(sql).collect()
            validation_results[test_name] = len(result) > 0
            logger.info(f"✅ {test_name}: PASS")
        except Exception as e:
            validation_results[test_name] = False
            logger.error(f"❌ {test_name}: FAIL - {e}")
    
    return validation_results
```
