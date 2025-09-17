# JPMC Markets AI Demo - Presenter Notes
*Demo Scenarios 1 & 2 for Equity Research Analysts*

---

## 🎯 Demo Overview

**Target Audience**: JPMC Leadership, Technology Teams, Data Scientists  
**Duration**: 30 minutes total (15 minutes per scenario)  
**Focus**: Technology sector with emphasis on Snowflake Inc. (SNOW)  
**Objective**: Showcase Snowflake AI capabilities for accelerating equity research workflows

### Key Value Propositions
1. **Scenario 1**: Reduce earnings analysis time from hours to minutes
2. **Scenario 2**: Discover investment themes from unstructured research faster
3. **Combined**: Enable analysts to focus on higher-value insights and client interaction

---

## 📋 Pre-Demo Checklist

### Technical Setup (5 minutes before demo)
- [ ] Snowflake Intelligence UI loaded and logged in
- [ ] Both agents (earnings_analysis_agent, thematic_research_agent) accessible
- [ ] MARKETS_AI_DEMO database visible with current quarter data
- [ ] Test one quick query to ensure agents are responsive
- [ ] Have backup browser tab ready

### Presenter Setup
- [ ] Review latest tech sector news for current context
- [ ] Confirm current date/quarter for dynamic data references
- [ ] Have SNOW current stock price ready for relevance
- [ ] Practice key demo questions to ensure smooth delivery

---

## 🎬 Demo Scenario 1: Earnings Analysis (15 minutes)

### Opening Hook (2 minutes)
**"It's earnings season, and you have 50+ tech companies reporting this week. Traditionally, an analyst might spend 2-3 hours per company just gathering and synthesizing the numbers. Let me show you how we can accelerate this to minutes."**

### Setup Context
- Open Snowflake Intelligence
- Navigate to Earnings Analysis Agent
- **Key Message**: "This agent has access to 8 quarters of earnings data with real-time updates"

### Question Flow (10 minutes)

#### Question 1: Broad Performance Overview (3 minutes)
**Ask Agent**: *"How did the major tech companies perform in the most recent quarter compared to analyst estimates? Focus on revenue and EPS surprises."*

**Expected Response Highlights**:
- Revenue/EPS surprise percentages for AAPL, MSFT, GOOGL, NVDA, SNOW
- Specific dollar amounts and percentages
- Quarter-over-quarter comparisons

**Presenter Commentary**:
- "Notice how quickly we get specific numbers with context"
- "This would typically require pulling data from multiple sources"
- "The agent automatically focuses on the most recent quarter"

#### Question 2: Deep Dive on SNOW (4 minutes)
**Ask Agent**: *"Can you analyze Snowflake's earnings trajectory over the past 4 quarters? How has their revenue growth and guidance compared to expectations?"*

**Expected Response Highlights**:
- SNOW's quarterly revenue progression
- Growth rates and guidance accuracy
- Comparison to cloud/data analytics peers

**Presenter Commentary**:
- "Here we see SNOW's growth-stage dynamics"
- "Notice the agent understands context about high-growth companies"
- "Guidance analysis is crucial for growth stocks"

#### Question 3: Sector Comparison (2 minutes)
**Ask Agent**: *"Which tech companies showed the strongest earnings momentum in the latest quarter, and how do their margins compare?"*

**Expected Response Highlights**:
- Ranking of tech companies by performance metrics
- Margin analysis (gross, operating)
- Trend identification

**Presenter Commentary**:
- "Cross-company analysis that would take hours manually"
- "Margin trends indicate operational efficiency"

#### Question 4: Visualization Request (1 minute)
**Ask Agent**: *"Create a table showing the top 5 tech companies by revenue surprise percentage for the latest quarter."*

**Expected Response**: Formatted table with company names, actual vs expected revenue, surprise %

### Scenario 1 Wrap-up (3 minutes)
**Key Messages**:
- "What we just did in 10 minutes would typically take an analyst 2-3 hours"
- "The agent understands financial context and provides relevant comparisons"
- "Data is current and dynamically updated"
- "This frees analysts to focus on investment implications rather than data gathering"

---

## 🎬 Demo Scenario 2: Thematic Research (15 minutes)

### Transition Hook (2 minutes)
**"Now imagine you're tasked with identifying the next big investment theme in tech. You have hundreds of research reports, but finding the emerging patterns manually is extremely time-consuming. Let's see how AI can accelerate theme discovery."**

### Setup Context
- Switch to Thematic Research Agent
- **Key Message**: "This agent analyzes research reports and can search full-text content to identify investment themes"

### Question Flow (10 minutes)

#### Question 1: Theme Discovery (3 minutes)
**Ask Agent**: *"What are the top investment themes emerging from recent technology sector research reports? Include the key companies and investment theses."*

**Expected Response Highlights**:
- AI/Enterprise AI adoption theme
- Data cloud transformation theme
- Company names and specific investment theses
- Price targets and ratings

**Presenter Commentary**:
- "The agent synthesizes multiple research reports instantly"
- "Notice how it identifies both the theme and supporting companies"
- "Investment theses are summarized from detailed reports"

#### Question 2: Deep Dive on AI Theme (4 minutes)
**Ask Agent**: *"Can you elaborate on the artificial intelligence investment theme? Which companies are positioned to benefit most, and what are the key risks analysts are highlighting?"*

**Expected Response Highlights**:
- Detailed AI theme analysis
- Specific companies (NVDA, MSFT, SNOW, etc.)
- Risk factors from analyst reports
- Market size/opportunity estimates

**Presenter Commentary**:
- "This pulls from multiple research reports and synthesizes the content"
- "Risk analysis is crucial for balanced investment decisions"
- "The agent provides both opportunities and challenges"

#### Question 3: SNOW-Specific Research (2 minutes)
**Ask Agent**: *"What do research analysts say specifically about Snowflake's position in the data cloud market? Include any recent price targets."*

**Expected Response Highlights**:
- SNOW-specific analyst commentary
- Data cloud positioning analysis
- Recent price targets and ratings
- Competitive advantages cited

**Presenter Commentary**:
- "Company-specific insights from multiple research sources"
- "Price targets help with valuation context"

#### Question 4: Research Source Citation (1 minute)
**Ask Agent**: *"Can you find specific quotes from research reports about enterprise AI adoption trends?"*

**Expected Response**: Actual excerpts from research reports with proper attribution

### Scenario 2 Wrap-up (3 minutes)
**Key Messages**:
- "Theme discovery that would take days of reading is completed in minutes"
- "The agent can both summarize themes and find specific supporting evidence"
- "Research reports are searchable at the content level, not just metadata"
- "This enables analysts to identify opportunities faster and with better supporting evidence"

---

## 🎯 Demo Conclusion (5 minutes)

### Summary of Value Delivered
1. **Time Savings**: Hours of manual work → Minutes of AI-assisted analysis
2. **Comprehensive Coverage**: Access to all data sources simultaneously
3. **Current Information**: Dynamic data that updates with latest earnings and research
4. **Better Analysis**: More time for insights and client interaction

### Technical Differentiators
- **Snowflake Cortex Analyst**: Natural language to SQL with financial context
- **Cortex Search**: Semantic search across unstructured research content
- **Snowflake Intelligence**: Orchestrates multiple AI capabilities seamlessly
- **Data Freshness**: Real-time connection to operational data systems

### Business Impact
- **Analyst Productivity**: 3-5x faster earnings and thematic analysis
- **Research Quality**: More comprehensive coverage of data sources
- **Client Value**: Faster turnaround on market insights and investment ideas
- **Competitive Advantage**: Earlier identification of investment themes

---

## 🛠️ Technical Q&A Preparation

### Common Questions & Answers

**Q: "How current is the data?"**
A: "The demo uses synthetic data with dynamic dates that update relative to the current quarter. In production, this would connect to real-time market data feeds and research databases."

**Q: "Can this handle other sectors besides technology?"**
A: "Absolutely. The same framework applies to any sector - we just need to load the relevant company data and research reports. The AI models understand financial concepts across industries."

**Q: "What about data security and compliance?"**
A: "Snowflake provides enterprise-grade security with role-based access control, data encryption, and audit logging. All data stays within your Snowflake environment."

**Q: "How does this integrate with existing research workflows?"**
A: "The agents can be embedded into existing tools via APIs, or accessed through Snowflake Intelligence UI. They complement rather than replace existing research processes."

**Q: "What's the implementation timeline?"**
A: "Basic setup takes days, not months. The main effort is data integration and training agents on your specific research processes."

### Demo Troubleshooting

**If agent doesn't respond quickly**:
- "While we wait, let me highlight that this is processing complex financial calculations in real-time..."
- Have backup screenshots ready

**If specific data points are questioned**:
- "This is synthetic demo data designed to show capabilities. In production, this would be your actual market data feeds."

**If asked about accuracy**:
- "The AI provides rapid insights that analysts then validate and enhance with their expertise. It's about augmenting human intelligence, not replacing it."

---

## 📊 Success Metrics

### Immediate Demo Goals
- [ ] Both scenarios completed within 30 minutes
- [ ] All 8 questions answered successfully by agents
- [ ] Clear demonstration of time savings value proposition
- [ ] Audience engagement and follow-up questions

### Follow-up Opportunities
- Detailed technical architecture discussion
- Proof of concept with real JPMC data
- Integration planning with existing research systems
- Training program for analysts

---

## 🎁 Demo Assets Provided

### For Audience
- This presenter notes document
- Complete deployment script (`deploy_markets_ai_demo.py`)
- Agent configuration files
- Database schema documentation

### For Technical Teams
- Full SQL DDL for database structure
- Synthetic data generation scripts
- Cortex Analyst semantic view definitions
- Cortex Search service configurations

**Next Steps**: Ready to deploy in your Snowflake environment using the provided script and TOML connection file.

---

*Demo prepared for JPMC Markets Team - September 2025*
