# Snowflake Development Rules for JPMC Markets Lab

## General Coding Standards

- Write clean, readable code with meaningful variable names
- Use consistent indentation (4 spaces for Python, 2 spaces for SQL)
- Include comprehensive docstrings for all functions and classes
- Follow PEP 8 style guide for Python code
- Use type hints for all Python function parameters and return values

## Snowflake SQL Best Practices

- Always use uppercase for SQL keywords (SELECT, FROM, WHERE, etc.)
- Use meaningful table and column aliases
- Include proper indentation for complex queries
- Always qualify column names with table aliases in joins
- Use explicit JOIN syntax instead of comma-separated tables
- Add comments for complex business logic
- Use parameterized queries to prevent SQL injection
- Implement proper error handling for database operations

## Performance Optimization

- Use appropriate warehouse sizing for workloads
- Implement clustering keys for large tables
- Use materialized views for frequently accessed aggregated data
- Minimize data movement between stages
- Use LIMIT clauses during development and testing
- Implement proper indexing strategies
- Monitor query performance and credit usage

## Cortex Search Implementation

- Use semantic search for unstructured financial documents
- Implement proper chunk sizing for document processing
- Use appropriate embedding models for financial text
- Implement proper error handling for AI operations
- Cache search results when appropriate
- Use proper filtering for asset classes and risk levels

## Streamlit Application Standards

- Use session state for maintaining user context
- Implement proper error handling and user feedback
- Use caching decorators for expensive operations
- Follow responsive design principles
- Implement proper security measures for financial data
- Use environment variables for sensitive configuration

## Security Best Practices

- Never hardcode credentials or API keys
- Use Snowflake's role-based access control (RBAC)
- Implement row-level security where appropriate
- Use secure connections (SSL/TLS) for all database connections
- Validate and sanitize all user inputs
- Implement proper audit logging
- Use environment variables for configuration

## Data Engineering Standards

- Implement proper data validation and quality checks
- Use consistent naming conventions for tables and columns
- Document data lineage and transformations
- Implement proper backup and recovery procedures
- Use version control for all SQL scripts and Python code
- Implement automated testing for data pipelines

## Error Handling

- Always include try-catch blocks for database operations
- Provide meaningful error messages to users
- Log errors with sufficient context for debugging
- Implement graceful degradation for non-critical features
- Use proper exception types for different error conditions

## Documentation

- Document all API endpoints and their parameters
- Include examples for complex queries and functions
- Maintain up-to-date README files
- Document deployment and configuration procedures
- Include troubleshooting guides for common issues 