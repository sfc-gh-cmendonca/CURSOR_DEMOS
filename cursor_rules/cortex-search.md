# Cortex Search Development Patterns

## CRITICAL: Cortex Search Service Creation Rules
**MANDATORY**: Follow these exact patterns for all Cortex Search service development

### Complete Syntax Pattern
```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE <database>.<schema>.<service_name>
ON <content_column>
ATTRIBUTES <id_column>, <title_column>, <other_attributes>
WAREHOUSE = <warehouse_name>
TARGET_LAG = '5 minutes'
AS
SELECT
    <id_column>,
    <title_column>,
    <content_column>,
    <other_attribute_columns>
FROM <source_table>;
```

### Critical ID/TITLE Pattern (MANDATORY)
**All Cortex Search services MUST include ID and TITLE columns in ATTRIBUTES for agent configuration:**

#### Required ATTRIBUTES Order:
```sql
ATTRIBUTES <ID_COLUMN>, <TITLE_COLUMN>, <other_attributes...>
```

#### Standard ID/TITLE Mappings:
```sql
-- EARNINGS_TRANSCRIPTS_SEARCH
ATTRIBUTES TRANSCRIPT_ID, TITLE, TICKER, FISCAL_QUARTER

-- RESEARCH_REPORTS_SEARCH  
ATTRIBUTES REPORT_ID, TITLE, REPORT_TYPE, THEMATIC_TAGS, AUTHOR, PUBLISHED_DATE

-- NEWS_ARTICLES_SEARCH
ATTRIBUTES ARTICLE_ID, HEADLINE, SOURCE, AFFECTED_TICKER, PUBLISHED_AT
```

### Service Creation Best Practices

#### Content Column Patterns:
```sql
-- For structured text content
ON FULL_TEXT

-- For unstructured document body
ON BODY

-- For concatenated fields (if needed)
ON CONCAT(TITLE, ' ', BODY)
```

#### Warehouse Configuration:
```sql
-- Use dedicated search warehouse
WAREHOUSE = MARKETS_AI_DEMO_SEARCH_WH

-- TARGET_LAG for real-time updates
TARGET_LAG = '5 minutes'
```

#### ATTRIBUTES Best Practices:
```sql
-- ✅ CORRECT - ID first, TITLE second, then other relevant fields
ATTRIBUTES DOCUMENT_ID, TITLE, CATEGORY, AUTHOR, PUBLISHED_DATE

-- ❌ WRONG - Random order, no clear ID/TITLE pattern
ATTRIBUTES CATEGORY, AUTHOR, DOCUMENT_ID, PUBLISHED_DATE, TITLE
```

### Complete Working Examples

#### Earnings Transcripts Search Service:
```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE ANALYTICS.EARNINGS_TRANSCRIPTS_SEARCH
ON FULL_TEXT
ATTRIBUTES TRANSCRIPT_ID, TITLE, TICKER, FISCAL_QUARTER
WAREHOUSE = MARKETS_AI_DEMO_SEARCH_WH
TARGET_LAG = '5 minutes'
AS
SELECT
    TRANSCRIPT_ID,
    TITLE,
    TICKER,
    FISCAL_QUARTER,
    FULL_TEXT
FROM RAW_DATA.EARNINGS_CALL_TRANSCRIPTS;
```

#### Research Reports Search Service:
```sql
CREATE OR REPLACE CORTEX SEARCH SERVICE ANALYTICS.RESEARCH_REPORTS_SEARCH
ON FULL_TEXT
ATTRIBUTES REPORT_ID, TITLE, REPORT_TYPE, THEMATIC_TAGS, AUTHOR, PUBLISHED_DATE
WAREHOUSE = MARKETS_AI_DEMO_SEARCH_WH
TARGET_LAG = '5 minutes'
AS
SELECT
    REPORT_ID,
    TITLE,
    REPORT_TYPE,
    THEMATIC_TAGS,
    AUTHOR,
    PUBLISHED_DATE,
    FULL_TEXT
FROM RAW_DATA.RESEARCH_REPORTS;
```

### Testing and Validation Patterns

#### Service Existence Check:
```sql
-- Test if service exists and is ready
SHOW CORTEX SEARCH SERVICES LIKE '%SERVICE_NAME%';
```

#### Service Functionality Test:
```sql
-- Test search functionality (when available)
SELECT SEARCH_PREVIEW('ANALYTICS.SERVICE_NAME', 'test query') LIMIT 3;
```

#### Fallback Testing Pattern:
```python
# Test for function availability before use
try:
    result = session.sql("SELECT SEARCH_PREVIEW('service', 'query')").collect()
except Exception as e:
    if "Unknown function" in str(e):
        # Use fallback approach
        result = session.sql("SHOW CORTEX SEARCH SERVICES LIKE '%service%'").collect()
```

### Agent Configuration Pattern
When configuring Cortex Search tools in Snowflake Intelligence agents:

```markdown
Tool Type: Cortex Search
Tool Name: search_{document_type}
Search Service: ANALYTICS.{SERVICE_NAME}
ID Column: {ID_COLUMN}
Title Column: {TITLE_COLUMN}
Description: {tool_description}
```

### Common Errors and Solutions

| Error | Cause | Solution |
|----|----|----|
| `Column not found in ATTRIBUTES` | SELECT columns don't match ATTRIBUTES | Ensure exact match between ATTRIBUTES and SELECT columns |
| `Warehouse not found` | Invalid warehouse name | Use `MARKETS_AI_DEMO_SEARCH_WH` for search services |
| `Service not ready` | Service still indexing | Wait 5-10 minutes for indexing to complete |
| `SEARCH_PREVIEW not found` | Function not available in environment | Use `SHOW CORTEX SEARCH SERVICES` as fallback |
| `Agent can't find documents` | Missing ID/TITLE columns | Ensure ID and TITLE columns are first in ATTRIBUTES |

**CRITICAL**: Cortex Search services are required for document search in Snowflake Intelligence agents - they provide semantic search capabilities over unstructured data.
