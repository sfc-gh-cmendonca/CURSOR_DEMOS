# Manual Agent Setup Guide for Snowflake Intelligence UI

## 🎯 Overview
This guide walks you through creating the two demo agents manually in the Snowflake Intelligence UI after deploying the database with `deploy_simple_demo.py`.

---

## 📋 Prerequisites
1. ✅ Run `python deploy_simple_demo.py` successfully
2. ✅ Verify `MARKETS_AI_DEMO` database exists with data
3. ✅ Access to Snowflake Intelligence UI
4. ✅ Appropriate permissions to create agents

---

## 🤖 Agent 1: Tech Earnings Analysis Assistant

### Step 1: Create New Agent
1. **Log into Snowflake Intelligence UI**
2. **Click "Create Agent"** or similar option
3. **Fill in Basic Information**:
   - **Agent Name**: `earnings_analysis_agent`
   - **Display Name**: `Tech Earnings Analysis Assistant`
   - **Description**: `Specialized agent for accelerating earnings season analysis in the technology sector. Provides rapid analysis of quarterly results, surprises, guidance, and peer comparisons.`

### Step 2: Configure Tools
1. **Add Tool**: Select "Cortex Analyst" tool type
2. **Tool Configuration**:
   - **Tool Name**: `earnings_analysis_semantic`
   - **Database**: `MARKETS_AI_DEMO`
   - **Schema**: `ANALYTICS`
   - **View/Table**: `earnings_analysis_semantic`
   - **Description**: `Comprehensive earnings data for technology companies including revenue, EPS, surprises, and estimates`

### Step 3: Add Instructions
**Planning Instructions**:
```
Use the earnings_analysis_semantic tool for ALL quantitative earnings analysis questions including:

- Quarterly performance analysis and comparisons
- Earnings surprise analysis (revenue and EPS vs estimates)  
- Revenue and EPS trend analysis over multiple quarters
- Peer benchmarking within technology sector
- Market cap and valuation context

Focus on recent quarters and highlight surprises or significant changes.
When users ask about SNOW, AAPL, MSFT, NVDA, provide specific financial metrics.
```

**Response Instructions**:
```
TONE: Professional, analytical, suitable for equity research analysts

FORMAT REQUIREMENTS:
- Provide specific numbers with clear context (% changes, dollar amounts)
- Always include quarter-over-quarter comparisons when relevant
- Highlight consensus beats/misses and their significance  
- Format financial figures clearly: $XXX.XM for millions
- Use tables for multi-company comparisons
- Cite specific quarters and dates for all metrics

Lead with the most important insight or surprising result.
Provide quantitative evidence for all claims.
Connect earnings performance to business fundamentals when possible.
```

### Step 4: Test Agent
**Test Questions**:
1. `"How did SNOW perform in the latest quarter compared to analyst estimates?"`
2. `"Which tech companies had the biggest earnings surprises?"`
3. `"Show me revenue trends for the major tech companies"`

---

## 🔍 Agent 2: Tech Thematic Research Assistant

### Step 1: Create New Agent
1. **Click "Create Agent"** in Snowflake Intelligence UI
2. **Fill in Basic Information**:
   - **Agent Name**: `thematic_research_agent`
   - **Display Name**: `Tech Thematic Research Assistant`
   - **Description**: `Specialized agent for discovering investment themes from technology sector research and market trends. Analyzes research reports to identify emerging opportunities and supporting evidence.`

### Step 2: Configure Tools
1. **Add Tool**: Select "Cortex Analyst" tool type
2. **Tool Configuration**:
   - **Tool Name**: `thematic_research_semantic`
   - **Database**: `MARKETS_AI_DEMO`
   - **Schema**: `ANALYTICS`
   - **View/Table**: `thematic_research_semantic`
   - **Description**: `Technology sector research reports, themes, investment theses, and analyst recommendations`

### Step 3: Add Instructions
**Planning Instructions**:
```
Use the thematic_research_semantic tool for thematic research analysis including:

- Identifying investment themes from research reports
- Analyzing ratings, price targets, and report classifications  
- Finding company-specific research insights
- Comparing analyst recommendations across reports

Focus on major technology themes like AI adoption, cloud transformation, data analytics.
Highlight companies with strong analyst support and clear investment theses.
```

**Response Instructions**:
```
TONE: Confident, research-oriented, suitable for investment decision-making

STRUCTURE FOR THEME ANALYSIS:
1. Lead with 2-3 key themes identified from recent research
2. For each theme, provide:
   - Clear theme description and market opportunity
   - Key companies positioned to benefit
   - Specific investment thesis and competitive advantages
   - Supporting evidence from analyst research

FORMATTING REQUIREMENTS:
- Use clear section headers for different themes
- Include specific company names and stock tickers
- Provide price targets when available (format: $XXX target)
- Create bullet points for key investment drivers
- Always cite specific research reports and analyst names

Balance opportunities with realistic risk assessment.
Include market size/opportunity estimates when available.
Provide actionable investment insights, not just descriptions.
```

### Step 4: Test Agent
**Test Questions**:
1. `"What are the top investment themes from recent tech research?"`
2. `"What do research analysts say about Snowflake's competitive position?"`
3. `"Show me all research reports with Buy ratings"`

---

## 🎬 Demo Execution Guide

### Before Your Demo
1. **Test both agents** with sample questions
2. **Review current tech news** for relevant context
3. **Practice key demo questions** for smooth delivery
4. **Have backup questions ready** in case of issues

### Demo Scenario 1: Earnings Analysis (15 minutes)

**Opening**: "We're analyzing tech earnings season. Let me show you how AI accelerates this from hours to minutes."

**Question Flow**:
1. **Broad Analysis**: `"How did the major tech companies perform in the most recent quarter compared to analyst estimates?"`
2. **SNOW Deep Dive**: `"Can you analyze Snowflake's earnings trajectory over the past 4 quarters?"`
3. **Performance Ranking**: `"Which tech companies showed the strongest earnings momentum?"`
4. **Summary Table**: `"Create a summary table of the top performing companies with key metrics"`

**Key Points to Highlight**:
- Speed of analysis across multiple companies
- Specific numbers with context
- Surprise analysis importance for stock performance
- Time savings: 2-3 hours → 10 minutes

### Demo Scenario 2: Thematic Research (15 minutes)

**Opening**: "Investment themes drive major allocation decisions. Finding them manually takes weeks. Watch this acceleration."

**Question Flow**:
1. **Theme Discovery**: `"What are the top investment themes from recent technology research?"`
2. **AI Theme Deep Dive**: `"Tell me more about the AI investment theme and which companies benefit most"`
3. **SNOW Analysis**: `"What do analysts say specifically about Snowflake's market position?"`
4. **Investment Summary**: `"Summarize the key investment opportunities with analyst targets"`

**Key Points to Highlight**:
- Theme synthesis from multiple research sources
- Company-specific recommendations
- Price targets and ratings context
- Time savings: weeks → minutes

---

## ✅ Success Checklist

### Agent Setup Complete When:
- [ ] Both agents created and configured
- [ ] Test questions work correctly
- [ ] Agents return specific financial data
- [ ] Response formatting looks professional
- [ ] Demo questions prepared and tested

### Demo Ready When:
- [ ] Both 15-minute scenarios practiced
- [ ] All demo questions return good results
- [ ] Backup questions prepared
- [ ] Current context (SNOW stock price, recent news) researched
- [ ] Presenter notes reviewed

---

## 🔧 Troubleshooting

### Common Issues:

**Agent not finding data**:
- Verify database name: `MARKETS_AI_DEMO`
- Check schema: `ANALYTICS`
- Confirm view names match exactly

**Poor response quality**:
- Review instructions for clarity
- Add more specific guidance
- Test with simpler questions first

**Connection issues**:
- Verify warehouse is running
- Check database permissions
- Confirm user has access to all objects

### Support:
- Check deployment logs for any data loading issues
- Verify table record counts match expectations
- Test semantic views directly in SQL if needed

---

## 🎉 Ready to Demo!

Your JPMC Markets AI Demo is now configured for impressive 15x productivity demonstrations in equity research workflows. Both scenarios showcase compelling time savings and quality improvements that will resonate with analysts and leadership.

**Next**: Follow your demo scripts and enjoy showcasing Snowflake AI capabilities! 🚀
