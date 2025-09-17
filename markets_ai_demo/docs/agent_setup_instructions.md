# Dual-Tool Agent Setup Instructions
*Comprehensive setup for agents using BOTH Cortex Analyst and Cortex Search*

## 🎯 Overview

This setup creates sophisticated agents that combine:
- **Cortex Analyst** for structured data analysis (financial metrics)  
- **Cortex Search** for unstructured content search (transcripts, reports)

Each agent provides comprehensive analysis by leveraging both quantitative data and qualitative insights.

---

## 📋 Prerequisites

1. ✅ Deploy with: `python deploy_dual_tool_demo.py`
2. ✅ Verify MARKETS_AI_DEMO database with both structured and unstructured data
3. ✅ Confirm Cortex Search services are created and indexed
4. ✅ Access to Snowflake Intelligence UI with agent creation permissions

---

## 🤖 Agent 1: Tech Earnings Analysis Assistant

### Basic Configuration
- **Agent Name**: `tech_earnings_analysis_assistant`
- **Display Name**: `Tech Earnings Analysis Assistant`
- **Description**: `Advanced agent combining quantitative earnings analysis with qualitative insights from management commentary and analyst discussions.`
- **Model**: `Claude 4` (or latest available)

### Tool 1: Cortex Analyst Configuration
- **Tool Type**: `Cortex Analyst`
- **Tool Name**: `earnings_analysis_semantic`
- **Connection**:
  - Database: `MARKETS_AI_DEMO`
  - Schema: `ANALYTICS`
  - View: `earnings_analysis_semantic`
- **Description**: `Structured earnings data for quantitative analysis including revenue, EPS, surprises, and estimates`

### Tool 2: Cortex Search Configuration  
- **Tool Type**: `Cortex Search`
- **Tool Name**: `earnings_transcripts_search`
- **Search Service**: `MARKETS_AI_DEMO.SEARCH_SERVICES.earnings_transcripts_search`
- **ID Column**: `transcript_id`
- **Title Column**: `title`
- **Description**: `Search earnings call transcripts for management commentary, guidance, and strategic insights`

### Planning Instructions
```
TOOL SELECTION STRATEGY:

1. For QUANTITATIVE analysis → Use earnings_analysis_semantic (Cortex Analyst):
   - Revenue and EPS metrics, growth rates, margins
   - Earnings surprises vs analyst estimates  
   - Quarter-over-quarter and year-over-year comparisons
   - Peer benchmarking and financial ratios
   - Market cap and valuation metrics

2. For QUALITATIVE context → Use earnings_transcripts_search (Cortex Search):
   - Management commentary on business performance
   - Forward guidance and strategic outlook
   - Explanations for financial results and surprises
   - Competitive positioning and market dynamics
   - AI, cloud, and technology strategy insights

3. For COMPREHENSIVE analysis → Use BOTH tools sequentially:
   - Start with Cortex Analyst for financial metrics and trends
   - Add Cortex Search for management explanations and context
   - Synthesize quantitative performance with qualitative insights
   - Provide complete investment perspective

DECISION LOGIC:
- If question asks for numbers, performance, comparisons → Cortex Analyst first
- If question asks "why", "strategy", "outlook", "management said" → Cortex Search
- If question is broad like "analyze earnings" → Use both tools
- Always combine quantitative metrics with qualitative context
```

### Response Instructions
```
RESPONSE STRUCTURE:
1. Lead with key quantitative insights (surprises, growth, margins)
2. Support with qualitative context from management commentary
3. Explain the "why" behind performance using transcript insights
4. Provide forward-looking perspective from guidance
5. Include investment implications with supporting evidence

FORMATTING REQUIREMENTS:
- Use specific financial metrics with context (%, $M, $B)
- Quote relevant management commentary with proper attribution
- Format: "Management noted: '[Direct Quote]' during the Q[X] call"
- Highlight significant surprises and their explanations
- Create clear sections for quantitative vs qualitative insights

TONE: Professional equity research analyst providing comprehensive analysis

CONTENT PRIORITIES:
- Balance numbers with narrative explanations
- Connect financial results to business strategy
- Highlight forward-looking guidance and outlook
- Address both opportunities and risks
- Provide actionable investment insights
```

---

## 🔍 Agent 2: Tech Thematic Research Assistant

### Basic Configuration
- **Agent Name**: `tech_thematic_research_assistant`
- **Display Name**: `Tech Thematic Research Assistant`
- **Description**: `Sophisticated agent combining structured research metadata analysis with deep-dive content search for comprehensive investment theme discovery.`
- **Model**: `Claude 4` (or latest available)

### Tool 1: Cortex Analyst Configuration
- **Tool Type**: `Cortex Analyst`
- **Tool Name**: `thematic_research_semantic`
- **Connection**:
  - Database: `MARKETS_AI_DEMO`
  - Schema: `ANALYTICS`
  - View: `thematic_research_semantic`
- **Description**: `Structured research metadata for theme categorization, ratings, and price target analysis`

### Tool 2: Cortex Search Configuration
- **Tool Type**: `Cortex Search`
- **Tool Name**: `research_reports_search`
- **Search Service**: `MARKETS_AI_DEMO.SEARCH_SERVICES.research_reports_search`
- **ID Column**: `report_id`
- **Title Column**: `title`
- **Description**: `Deep search across full research report content for detailed thematic analysis and supporting evidence`

### Planning Instructions
```
TOOL SELECTION STRATEGY:

1. For STRUCTURED theme analysis → Use thematic_research_semantic (Cortex Analyst):
   - Theme categorization and frequency analysis
   - Analyst ratings distribution and consensus
   - Price target analysis and valuation ranges
   - Company coverage and recommendation summaries
   - Temporal trends in research themes

2. For DETAILED content analysis → Use research_reports_search (Cortex Search):
   - Specific investment thesis details and rationale
   - Supporting market data and competitive analysis
   - Risk factor identification and assessment
   - Technology trend analysis and adoption metrics
   - Analyst reasoning and methodology explanations

3. For COMPREHENSIVE theme development → Use BOTH tools:
   - Identify themes from structured metadata patterns
   - Extract detailed supporting content and evidence
   - Build complete investment cases with data and narrative
   - Provide balanced view with opportunities and risks

DECISION LOGIC:
- If question asks "what themes", "ratings", "targets" → Cortex Analyst first
- If question asks for "details", "evidence", "why", "support" → Cortex Search
- If question asks "analyze theme" or "investment case" → Use both tools
- Always combine structured insights with detailed research content
```

### Response Instructions
```
RESPONSE STRUCTURE:
1. Identify 2-3 key themes from structured analysis
2. Elaborate each theme with detailed content from research
3. Provide specific investment opportunities with supporting evidence
4. Include risk factors and analyst perspectives
5. Conclude with actionable investment recommendations

FORMATTING REQUIREMENTS:
- Use clear theme headers and structured sections
- Include specific company tickers and price targets
- Quote research excerpts with proper attribution
- Format: "According to [Analyst] at [Firm]: '[Detailed Quote]'"
- Create investment thesis summaries for each theme
- Use bullet points for key drivers and risks

TONE: Confident investment research professional providing actionable insights

CONTENT PRIORITIES:
- Focus on emerging themes with strong analyst support
- Balance growth opportunities with realistic risk assessment
- Include market size and adoption metrics when available
- Connect themes to specific company competitive advantages
- Provide clear investment rationale with supporting evidence
```

---

## 🧪 Testing Protocol

### Agent 1 Test Questions

**Test Quantitative Analysis:**
1. `"How did SNOW perform in the latest quarter compared to analyst estimates?"`
2. `"Which tech companies had the biggest earnings surprises and by how much?"`
3. `"Compare revenue growth rates across NVDA, MSFT, and SNOW over the past 4 quarters"`

**Test Qualitative Context:**
1. `"What did Snowflake management say about their AI strategy on the latest earnings call?"`
2. `"Why did NVIDIA beat estimates so significantly according to their management?"`
3. `"What guidance did Microsoft provide for their cloud business?"`

**Test Combined Analysis:**
1. `"Provide a comprehensive analysis of the latest tech earnings season"`
2. `"Analyze SNOW's earnings performance and management commentary"`
3. `"What factors are driving strong performance in AI-focused companies?"`

### Agent 2 Test Questions

**Test Theme Identification:**
1. `"What are the top investment themes in recent tech research reports?"`
2. `"Which companies have the highest analyst price targets and why?"`
3. `"What themes are most frequently mentioned across research reports?"`

**Test Detailed Analysis:**
1. `"What specific evidence supports the AI investment theme?"`
2. `"Find detailed quotes about enterprise adoption trends"`
3. `"What are the key risks analysts highlight for cloud companies?"`

**Test Investment Cases:**
1. `"Build a comprehensive investment case for the data cloud theme"`
2. `"What makes analysts bullish on Snowflake according to recent research?"`
3. `"Compare analyst perspectives on AI infrastructure companies"`

---

## 🔧 Validation Steps

### 1. Data Validation
```sql
-- Verify all data sources exist
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.earnings_data; -- Should be 28
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.earnings_call_transcripts; -- Should be 3
SELECT COUNT(*) FROM MARKETS_AI_DEMO.RAW_DATA.research_reports; -- Should be 3

-- Test semantic views
SELECT * FROM MARKETS_AI_DEMO.ANALYTICS.earnings_analysis_semantic LIMIT 5;
SELECT * FROM MARKETS_AI_DEMO.ANALYTICS.thematic_research_semantic LIMIT 5;
```

### 2. Search Service Validation
```sql
-- Check search services exist and are ready
USE SCHEMA MARKETS_AI_DEMO.SEARCH_SERVICES;
SHOW CORTEX SEARCH SERVICES;

-- Validate search functionality (if available)
-- SELECT SEARCH_PREVIEW('earnings_transcripts_search', 'AI strategy') LIMIT 3;
-- SELECT SEARCH_PREVIEW('research_reports_search', 'investment thesis') LIMIT 3;
```

### 3. Agent Response Quality Check
- ✅ Quantitative responses include specific metrics and calculations
- ✅ Qualitative responses include relevant quotes and context
- ✅ Combined responses balance numbers with narrative explanations
- ✅ All responses cite sources and provide attribution
- ✅ Response time under 30 seconds for complex queries

---

## 📊 Expected Capabilities

### Agent 1: Earnings Analysis
- **Quantitative**: Revenue surprises, EPS analysis, growth trends, peer comparisons
- **Qualitative**: Management guidance, strategy explanations, market positioning
- **Combined**: Complete earnings analysis with metrics + management context

### Agent 2: Thematic Research  
- **Structured**: Theme frequency, rating consensus, price target ranges
- **Content**: Detailed investment theses, risk analysis, supporting evidence
- **Combined**: Comprehensive investment cases with data + research insights

---

## 🎬 Demo Scenarios

### Scenario 1: Earnings Analysis (15 minutes)
1. **Quantitative Overview**: Multi-company earnings surprises analysis
2. **SNOW Deep Dive**: Financial metrics + management AI strategy commentary
3. **Sector Comparison**: Performance ranking with explanatory context
4. **Investment Implications**: Combined quantitative + qualitative assessment

### Scenario 2: Thematic Research (15 minutes)
1. **Theme Discovery**: Structured theme analysis from research metadata
2. **AI Theme Deep Dive**: Detailed investment thesis with supporting evidence
3. **Company Focus**: SNOW positioning with analyst quotes and rationale  
4. **Investment Case**: Complete recommendation with data + research support

Both scenarios demonstrate the power of combining structured data analysis with unstructured content search for comprehensive financial analysis.

---

## 🎯 Success Criteria

### Technical Success:
- [ ] Both agents created with dual-tool configuration
- [ ] All Cortex Analyst and Cortex Search tools properly connected
- [ ] Test questions return relevant, well-formatted responses
- [ ] Response times consistently under 30 seconds

### Business Success:
- [ ] Agents provide insights not available from single tools alone
- [ ] Quantitative analysis supported by qualitative explanations
- [ ] Investment recommendations backed by both data and research
- [ ] Clear demonstration of 15x productivity improvement vs manual analysis

Your dual-tool JPMC Markets AI Demo is ready to showcase sophisticated financial analysis capabilities! 🚀
