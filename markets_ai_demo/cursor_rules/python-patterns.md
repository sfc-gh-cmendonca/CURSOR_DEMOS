---
globs: *.py
---

# Python Development Patterns

## Snowpark Session Management (CRITICAL)
**MANDATORY**: All SQL execution MUST use `session.sql().collect()` pattern for compatibility outside Cursor

### Session Creation Pattern
```python
from snowflake.snowpark import Session
import argparse
from config import DemoConfig

def get_snowpark_session(connection_name: str = None) -> Session:
    """Create Snowpark session using connections.toml"""
    if not connection_name:
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection_name", default=DemoConfig.SNOWFLAKE_CONNECTION_NAME)
        args = parser.parse_args()
        connection_name = args.connection_name
    
    session = Session.builder.config("connection_name", connection_name).create()
    return session
```

### Session Reuse Pattern (MANDATORY)
```python
# CORRECT: Always reuse the single session passed from main
def some_function(session: Session) -> None:
    result = session.sql("SELECT * FROM table").collect()
    
# WRONG: Never create new sessions in functions
def bad_function():
    session = Session.builder.create()  # DON'T DO THIS
```

## SQL Execution Pattern (CRITICAL)
**MANDATORY**: ALL SQL execution must use this exact pattern:

```python
# CORRECT: Always use session.sql().collect()
sql_statement = "CREATE TABLE example AS SELECT * FROM source"
result = session.sql(sql_statement).collect()

# CORRECT: For queries returning data
query = "SELECT * FROM table LIMIT 10"
result = session.sql(query).collect()

# CORRECT: For counting rows - use Snowpark table method
row_count = session.table("DATABASE.SCHEMA.TABLE_NAME").count()

# ACCEPTABLE: SQL COUNT as fallback if table method not suitable
query = "SELECT COUNT(*) as cnt FROM table WHERE condition = 'value'"
result = session.sql(query).collect()
row_count = result[0]['CNT']

# WRONG: Never use direct cursor access
cursor = session._conn._cursor  # DON'T DO THIS
cursor.execute(sql)  # DON'T DO THIS
```

## Dynamic Date Generation Pattern (CRITICAL)
**MANDATORY**: Never use hardcoded dates - always generate dynamically

```python
# CORRECT: Dynamic date generation
from utils.date_utils import get_historical_quarters, get_dynamic_date_range
from config import DemoConfig

# For quarterly data (earnings, estimates, reports)
quarters = get_historical_quarters()  # Uses NUM_HISTORICAL_QUARTERS from config
recent_quarters = get_historical_quarters()[:3]  # Last 3 quarters
specific_count = get_historical_quarters(4)  # Override default

# For daily data (prices, trading, events)
start_date, end_date = get_dynamic_date_range()  # Covers all quarters

# WRONG: Hardcoded dates
quarters = ["2024-Q1", "2024-Q2", "2024-Q3"]  # DON'T DO THIS
start_date = "2024-01-01"  # DON'T DO THIS
```

### Date Generation Rules
- **NEVER** hardcode years like "2024" or dates like "2024-01-01"
- **ALWAYS** use utilities from `utils.date_utils`
- **MAKE** time periods configurable through `config.py`
- **ENSURE** demo relevance by using current date as reference

## Unstructured Data Generation Pattern
```python
from snowflake.snowpark.functions import col, lit
from snowflake.cortex import complete

# 1. Generate prompts dynamically
prompts_data = [{"prompt": f"Generate {context}..."} for context in contexts]

# 2. Create Snowpark DataFrame
prompts_df = session.create_dataframe(prompts_data)

# 3. Save prompts to table
prompts_df.write.mode("overwrite").save_as_table("TEMP_PROMPTS")

# 4. Use with_column for content generation
content_df = prompts_df.with_column(
    "generated_content",
    complete(lit(DemoConfig.CORTEX_MODEL_NAME), col("prompt"))
)

# 5. Save final results
content_df.write.mode("overwrite").save_as_table("FINAL_TABLE")
```

## Error Handling for SQL
```python
try:
    result = session.sql(sql_statement).collect()
    print("✅ SQL executed successfully")
except Exception as e:
    print(f"❌ SQL execution failed: {str(e)}")
    # MANDATORY: Always provide the full SQL for debugging when it fails
    print(f"📋 Full SQL attempted:")
    print(sql_statement)
    print("❓ Please help fix the SQL syntax error above")
    raise
```


## Function Compatibility Patterns
```python
# CORRECT: Test function availability before use
try:
    result = session.sql("SELECT some_function('param')").collect()
except Exception as e:
    if "Unknown function" in str(e):
        # Fallback to alternative approach
        result = session.sql("ALTERNATIVE_APPROACH").collect()
```

## Configuration Usage
- Always import: from config import DemoConfig
- Use DemoConfig constants for all parameters
- Support command-line overrides for connection names