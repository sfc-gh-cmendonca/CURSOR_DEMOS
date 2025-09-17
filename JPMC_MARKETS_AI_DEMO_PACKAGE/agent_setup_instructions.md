# Agent Setup Instructions for JPMC Markets AI Demo

## Overview
This document provides step-by-step instructions for setting up agents in Snowflake Intelligence for the JPMC Markets AI Demo. Each agent combines Cortex Analyst for structured data analysis with Cortex Search for unstructured content search.

## Prerequisites
- ✅ Snowflake Intelligence access
- ✅ MARKETS_AI_DEMO database deployed with `deploy_simple_demo.py`
- ✅ Appropriate permissions to create agents and search services

---

## Agent 1: Tech Earnings Analysis Assistant

### Basic Configuration
- **Agent Name**: `tech_earnings_analysis_assistant`
- **Display Name**: `Tech Earnings Analysis Assistant`
- **Description**: `Specialized agent for accelerating earnings season analysis in the technology sector. Analyzes quarterly financial results, surprises, and trends across major tech companies.`
- **Model**: `Claude 4` (or latest available)

### Tools Configuration

#### Tool 1: Cortex Analyst
- **Tool Type**: `Cortex Analyst`
- **Tool Name**: `earnings_analysis_semantic`
- **Connection**:
  - Database: `MARKETS_AI_DEMO`
  - Schema: `ANALYTICS`
  - View: `earnings_analysis_semantic`
- **Description**: `Structured earnings data analysis for technology companies including revenue, EPS, surprises, and analyst estimates`

#### Tool 2: Cortex Search (Manual Setup Required)
- **Tool Type**: `Cortex Search`
- **Tool Name**: `earnings_documents_search`
- **Search Service**: `earnings_documents_search` (to be created manually)
- **Description**: `Search earnings call transcripts, press releases, and financial filings for contextual information`

**Manual Search Service Creation**:
```sql
-- Execute in Snowflake to create search service for earnings documents
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS MARKETS_AI_DEMO.SEARCH_SERVICES.earnings_documents_search
ON full_content
ATTRIBUTES document_id, title, company_ticker, document_type, publish_date
WAREHOUSE = DEMO_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        report_id as document_id,
        title,
        tickers_covered as company_ticker,
        'Research Report' as document_type,
        publish_date,
        investment_thesis as full_content
    FROM MARKETS_AI_DEMO.RAW_DATA.research_reports
    WHERE sector = 'Technology'
);
```

### Planning Instructions
```
Tool Selection Logic:

1. For QUANTITATIVE analysis → Use earnings_analysis_semantic (Cortex Analyst):
   - Quarterly performance comparisons
   - Earnings surprise calculations
   - Revenue and EPS trend analysis
   - Peer benchmarking and rankings
   - Financial metric analysis

2. For QUALITATIVE context → Use earnings_documents_search (Cortex Search):
   - Management commentary explanations
   - Business strategy insights
   - Risk factor analysis
   - Forward guidance context

3. For COMPREHENSIVE analysis → Use BOTH tools:
   - Start with structured data for metrics
   - Add contextual insights from documents
   - Provide complete picture with numbers + narrative

Decision Tree:
- If question contains numbers, metrics, "performance", "compare" → Cortex Analyst first
- If question asks for "why", "strategy", "outlook", "management says" → Cortex Search
- If question is broad like "analyze earnings" → Use both tools sequentially
```

### Response Instructions
```
TONE: Professional, analytical, suitable for equity research analysts

RESPONSE STRUCTURE:
1. Lead with key quantitative insights (metrics, surprises, trends)
2. Support with qualitative context from documents
3. Provide investment implications and peer comparisons
4. Include specific citations and data sources

FORMATTING:
- Use specific numbers with context (% changes, absolute values)
- Format financial figures: $XXX.XM for millions, $XX.XB for billions
- Highlight surprises and significant deviations from estimates
- Create tables for multi-company comparisons
- Always cite quarters, dates, and sources

CONTENT REQUIREMENTS:
- Include both quantitative metrics AND qualitative insights
- Explain the "why" behind performance (from search results)
- Connect financial results to business strategy
- Provide forward-looking perspective when available
```

---

## Agent 2: Tech Thematic Research Assistant

### Basic Configuration
- **Agent Name**: `tech_thematic_research_assistant`
- **Display Name**: `Tech Thematic Research Assistant`
- **Description**: `Specialized agent for discovering and analyzing investment themes from technology sector research. Combines structured research data with full-text search across analyst reports.`
- **Model**: `Claude 4` (or latest available)

### Tools Configuration

#### Tool 1: Cortex Analyst
- **Tool Type**: `Cortex Analyst`
- **Tool Name**: `thematic_research_semantic`
- **Connection**:
  - Database: `MARKETS_AI_DEMO`
  - Schema: `ANALYTICS`
  - View: `thematic_research_semantic`
- **Description**: `Structured research report metadata including themes, ratings, price targets, and company coverage`

#### Tool 2: Cortex Search
- **Tool Type**: `Cortex Search`
- **Tool Name**: `research_reports_search`
- **Search Service**: `research_reports_search` (to be created manually)
- **Description**: `Full-text search across research report content for detailed thematic analysis and quote extraction`

**Manual Search Service Creation**:
```sql
-- Execute in Snowflake to create search service for research reports
CREATE CORTEX SEARCH SERVICE IF NOT EXISTS MARKETS_AI_DEMO.SEARCH_SERVICES.research_reports_search
ON investment_thesis
ATTRIBUTES report_id, title, author, firm, theme, rating, price_target
WAREHOUSE = DEMO_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        report_id,
        title,
        author,
        firm,
        theme,
        rating,
        price_target,
        investment_thesis
    FROM MARKETS_AI_DEMO.RAW_DATA.research_reports
    WHERE sector = 'Technology'
);
```

### Planning Instructions
```
Tool Selection Logic:

1. For STRUCTURED theme analysis → Use thematic_research_semantic (Cortex Analyst):
   - Theme categorization and frequency
   - Analyst ratings and price target analysis
   - Company coverage and recommendation summaries
   - Quantitative theme metrics

2. For DETAILED content analysis → Use research_reports_search (Cortex Search):
   - Specific investment thesis details
   - Supporting evidence and data points
   - Risk factor identification
   - Analyst reasoning and methodology

3. For COMPREHENSIVE theme discovery → Use BOTH tools:
   - Identify themes from structured metadata
   - Extract detailed supporting content
   - Provide complete investment case with evidence

Decision Tree:
- If question asks "what themes", "which companies", "ratings" → Cortex Analyst first
- If question asks "why", "evidence", "details", "quotes" → Cortex Search
- If question asks "analyze theme" or "investment case" → Use both tools
```

### Response Instructions
```
TONE: Confident, research-oriented, suitable for investment decision-making

RESPONSE STRUCTURE:
1. Identify 2-3 key themes from structured data
2. Elaborate each theme with detailed content from search
3. Highlight investment opportunities with supporting evidence
4. Include risk factors and analyst perspectives
5. Provide actionable investment insights

FORMATTING:
- Use clear theme headers and bullet points
- Include specific company tickers and price targets
- Quote relevant excerpts with proper attribution
- Format: "According to [Analyst] at [Firm]: '[Quote]'"
- Create investment thesis summaries for each theme

CONTENT REQUIREMENTS:
- Balance opportunities with risk analysis
- Include market size and growth projections when available
- Connect themes to specific company business models
- Provide both bull and bear perspectives
- Always cite sources and publication dates
```

---

## Testing and Validation

### Test Questions for Agent 1 (Earnings Analysis)

1. **Quantitative Focus**: 
   - `"How did SNOW perform in the latest quarter compared to analyst estimates?"`
   - `"Which tech companies had the biggest earnings surprises?"`

2. **Qualitative Context**:
   - `"What did Snowflake management say about their growth strategy?"`
   - `"Why did NVDA beat estimates so significantly?"`

3. **Combined Analysis**:
   - `"Analyze the latest earnings season for major tech companies"`
   - `"What factors drove the strong performance in cloud companies?"`

### Test Questions for Agent 2 (Thematic Research)

1. **Theme Identification**:
   - `"What are the top investment themes in recent tech research?"`
   - `"Which companies are rated as Buy by analysts?"`

2. **Detailed Analysis**:
   - `"What specific evidence supports the AI investment theme?"`
   - `"Find quotes about enterprise adoption trends"`

3. **Investment Case**:
   - `"Build an investment case for the data cloud theme"`
   - `"What are analysts saying about Snowflake's competitive position?"`

---

## Troubleshooting

### Common Issues

1. **Search Service Creation Errors**:
   - Verify DEMO_WH warehouse exists and is running
   - Check permissions for creating search services
   - Ensure target tables have data

2. **Agent Tool Configuration**:
   - Confirm database and schema names are exact: `MARKETS_AI_DEMO.ANALYTICS`
   - Verify view names match: `earnings_analysis_semantic`, `thematic_research_semantic`
   - Check that search service names match exactly

3. **Poor Response Quality**:
   - Review planning instructions for clarity
   - Test individual tools separately first
   - Adjust response instructions based on output quality

### Validation Steps

1. **Database Validation**:
```sql
-- Verify data exists
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.companies; -- Should return 7
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.earnings_data; -- Should return 28
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.research_reports; -- Should return 2
```

2. **View Validation**:
```sql
-- Test semantic views
SELECT * FROM MARKETS_AI_DEMO.ANALYTICS.earnings_analysis_semantic LIMIT 5;
SELECT * FROM MARKETS_AI_DEMO.ANALYTICS.thematic_research_semantic LIMIT 5;
```

3. **Search Service Validation**:
```sql
-- Check search services exist
SHOW CORTEX SEARCH SERVICES LIKE '%earnings%';
SHOW CORTEX SEARCH SERVICES LIKE '%research%';
```

---

## Success Criteria

### Agent Setup Complete When:
- [ ] Both agents created with correct configurations
- [ ] All tools properly connected to database objects
- [ ] Search services created and indexed
- [ ] Test questions return relevant, well-formatted responses
- [ ] Agents demonstrate both quantitative and qualitative analysis capabilities

### Demo Ready When:
- [ ] Agents respond within 30 seconds to all test questions
- [ ] Responses include specific data points and contextual insights
- [ ] Cross-referencing between structured and unstructured data works
- [ ] Demo scenarios flow smoothly with prepared questions

---

## Support Resources

- **Database Schema**: Reference `deploy_simple_demo.py` for complete table structures
- **Sample Data**: All synthetic data designed for current quarter relevance
- **Demo Scripts**: Follow `DEMO_SCENARIO_SCRIPTS.md` for detailed question flows
- **Presenter Guide**: Use `DEMO_PRESENTER_NOTES.md` for timing and talking points

Based on the reference architecture from [FSI Demos](https://github.com/mstellwa/fsi_demos/blob/main/markets_ai_demo/docs/agent_setup_instructions.md), this setup provides the comprehensive dual-tool approach needed for sophisticated financial analysis demonstrations.
