# Agent Setup Patterns and Instruction Templates for Snowflake Intelligence

## Agent Configuration Patterns

### Basic Agent Structure
```yaml
agent_name: descriptive_agent_name
display_name: "Human Readable Agent Name"
description: "Clear description of agent capabilities and purpose"
model: "claude-4" # or latest available
```

### Tool Configuration Templates

#### Cortex Analyst Tool Template
```yaml
tool_type: "Cortex Analyst"
tool_name: "semantic_view_name"
connection:
  database: "DATABASE_NAME"
  schema: "SCHEMA_NAME"
  view: "semantic_view_name"
description: "Description of what this tool analyzes"
```

#### Cortex Search Tool Template
```yaml
tool_type: "Cortex Search"
tool_name: "search_service_name"
search_service: "DATABASE.SCHEMA.search_service_name"
id_column: "unique_id_column"
title_column: "title_column"
description: "Description of what content this searches"
```

### Planning Instructions Template
```markdown
TOOL SELECTION STRATEGY:

1. For QUANTITATIVE analysis → Use {analyst_tool_name} (Cortex Analyst):
   - Financial metrics and calculations
   - Trend analysis and comparisons
   - Numerical data aggregation
   - Performance indicators

2. For QUALITATIVE insights → Use {search_tool_name} (Cortex Search):
   - Management commentary
   - Strategic insights
   - Risk factors
   - Forward-looking statements

RESPONSE STRUCTURE:
- Start with quantitative findings
- Enhance with qualitative context
- Provide specific data points and quotes
- Conclude with actionable insights
```

### Agent Examples

#### Financial Analysis Agent
```yaml
agent_name: "earnings_analysis_assistant"
display_name: "Tech Earnings Analysis Assistant"
description: "Advanced agent combining quantitative earnings analysis with qualitative insights from management commentary and analyst discussions."
model: "claude-4"

tools:
  - tool_type: "Cortex Analyst"
    tool_name: "earnings_analysis_semantic"
    connection:
      database: "MARKETS_AI_DEMO"
      schema: "ANALYTICS"
      view: "earnings_analysis_semantic"
    description: "Structured earnings data for quantitative analysis including revenue, EPS, surprises, and estimates"
  
  - tool_type: "Cortex Search"
    tool_name: "earnings_transcripts_search"
    search_service: "MARKETS_AI_DEMO.SEARCH_SERVICES.earnings_transcripts_search"
    id_column: "transcript_id"
    title_column: "title"
    description: "Search earnings call transcripts for management commentary, guidance, and strategic insights"
```

#### Research Analysis Agent
```yaml
agent_name: "thematic_research_assistant"
display_name: "Tech Thematic Research Assistant"
description: "Sophisticated agent analyzing investment themes through structured research data and comprehensive content analysis."
model: "claude-4"

tools:
  - tool_type: "Cortex Analyst"
    tool_name: "thematic_research_semantic"
    connection:
      database: "MARKETS_AI_DEMO"
      schema: "ANALYTICS"
      view: "thematic_research_semantic"
    description: "Structured research metadata for theme categorization, ratings, and price target analysis"
  
  - tool_type: "Cortex Search"
    tool_name: "research_reports_search"
    search_service: "MARKETS_AI_DEMO.SEARCH_SERVICES.research_reports_search"
    id_column: "report_id"
    title_column: "title"
    description: "Deep search across full research report content for detailed thematic analysis and supporting evidence"
```

## Configuration Best Practices

### Naming Conventions
- **Agent names**: lowercase_with_underscores
- **Display names**: Title Case with proper spacing
- **Tool names**: match the underlying data source name
- **Descriptions**: Clear, specific, actionable

### Tool Selection Guidelines
- **Use Cortex Analyst** for structured data analysis, metrics, calculations
- **Use Cortex Search** for unstructured content, commentary, insights
- **Combine both tools** for comprehensive analysis that requires both quantitative and qualitative insights

### Planning Instructions Best Practices
- **Clear tool selection criteria** based on query type
- **Structured response format** for consistency
- **Specific examples** of when to use each tool
- **Quality guidelines** for response content

## Validation Checklist

### Pre-Deployment Validation
- [ ] Semantic views exist and contain data
- [ ] Search services are created and indexed
- [ ] Database/schema permissions are correct
- [ ] ID and Title columns are properly configured
- [ ] Agent descriptions are clear and accurate

### Post-Deployment Testing
- [ ] Test basic queries for each tool
- [ ] Verify tool selection logic works correctly
- [ ] Confirm response quality and format
- [ ] Test complex multi-tool scenarios
- [ ] Validate error handling and edge cases

## Common Configuration Issues

### Tool Connection Problems
- **Database not found**: Verify database name and permissions
- **Schema access denied**: Check role permissions for schema
- **View does not exist**: Confirm semantic view creation
- **Search service unavailable**: Verify service is created and indexed

### Agent Response Issues
- **Tool selection confusion**: Improve planning instructions clarity
- **Inconsistent responses**: Standardize response format requirements
- **Missing context**: Enhance tool descriptions and examples
- **Performance problems**: Optimize queries and warehouse sizing

## Integration with Snowflake Intelligence

### Manual Setup Process
1. **Access Snowflake Intelligence UI**
2. **Create New Agent** with basic configuration
3. **Add Cortex Analyst Tool** with semantic view connection
4. **Add Cortex Search Tool** with search service connection
5. **Configure Planning Instructions** with tool selection strategy
6. **Test Agent** with sample queries
7. **Iterate and Refine** based on response quality

### Automated Configuration (Future)
- YAML-based agent definitions
- Bulk agent deployment scripts
- Configuration validation tools
- Performance monitoring and optimization
