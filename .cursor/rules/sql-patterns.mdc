---
globs: *.sql
---

# SQL Development Patterns

## CRITICAL: SQL Execution Rules
**MANDATORY**: All SQL must be executed via session.sql(sql_statement).collect()

### Function Compatibility Patterns
```python
# Test for function availability before use
try:
    result = session.sql("SELECT some_function('param')").collect()
except Exception as e:
    if "Unknown function" in str(e):
        # Use fallback approach
        result = session.sql("ALTERNATIVE_QUERY").collect()
```

## Testing Pattern
Use appropriate testing patterns for each component type:
- **Semantic Views**: See semantic-views.mdc for SEMANTIC_VIEW() testing patterns
- **SQL Functions**: Test function availability before use (see examples above)