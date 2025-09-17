# JPMC Markets AI Demo - Scenario Scripts
*Detailed Question Flows for Demo Scenarios 1 & 2*

---

## 📋 Demo Execution Guide

### Prerequisites
1. Run `python deploy_markets_ai_demo.py` to deploy the demo
2. Verify Snowflake Intelligence agents are configured
3. Confirm current date for dynamic data context
4. Test agent responsiveness before demo

---

## 🎬 Scenario 1: Earnings Analysis Agent
*15-minute standalone demo showcasing accelerated earnings season analysis*

### Context Setting (1 minute)
**Presenter**: "We're in the middle of tech earnings season. Our analyst team needs to quickly synthesize performance across 10 major technology companies. Traditionally, this analysis takes 2-3 hours per company. Let me show you how we can accelerate this to minutes."

**Action**: Open Snowflake Intelligence → Navigate to Earnings Analysis Agent

---

### Question 1: Quarterly Performance Overview (3 minutes)

#### The Ask
**Copy/Paste into Agent**: 
```
How did the major tech companies perform in the most recent quarter compared to analyst estimates? Focus on revenue and EPS surprises for Apple, Microsoft, Google, NVIDIA, and Snowflake.
```

#### Expected Agent Response Pattern
- **Revenue surprises**: Specific % beats/misses for each company
- **EPS surprises**: Actual vs expected earnings per share
- **Context**: Quarter identification and dates
- **Ranking**: Companies ordered by surprise magnitude

#### Presenter Commentary (while agent processes)
"Notice that I'm asking about multiple companies simultaneously. The agent has access to 8 quarters of earnings data with real-time updates. This would typically require pulling data from multiple financial databases and calculation tools."

#### Key Points to Highlight
- **Speed**: Complex multi-company analysis in seconds
- **Accuracy**: Specific dollar amounts and percentages
- **Context**: Automatic focus on most recent quarter
- **Comparisons**: Built-in relative performance analysis

---

### Question 2: Snowflake Deep Dive (4 minutes)

#### The Ask
**Copy/Paste into Agent**:
```
Can you analyze Snowflake's earnings trajectory over the past 4 quarters? Include revenue growth rates, guidance accuracy, and how their performance compares to other cloud/data companies.
```

#### Expected Agent Response Pattern
- **Quarterly progression**: Revenue growth quarter-over-quarter
- **Guidance analysis**: Actual vs guided performance
- **Growth metrics**: Year-over-year comparisons
- **Peer context**: Comparison to other cloud companies

#### Presenter Commentary
"Here we're drilling down into a specific company that's particularly relevant to our data infrastructure strategy. Notice how the agent understands the context of high-growth SaaS companies and provides appropriate benchmarks."

#### Key Points to Highlight
- **Growth-stage awareness**: Agent understands SNOW's business model
- **Guidance tracking**: Crucial for growth stock analysis
- **Peer benchmarking**: Automatic industry context
- **Trend identification**: Multi-quarter pattern recognition

---

### Question 3: Sector Performance Ranking (2 minutes)

#### The Ask
**Copy/Paste into Agent**:
```
Which tech companies showed the strongest earnings momentum in the latest quarter? Rank them by revenue surprise and include operating margin analysis.
```

#### Expected Agent Response Pattern
- **Performance ranking**: Companies ordered by metrics
- **Surprise analysis**: Revenue beat/miss percentages  
- **Margin trends**: Operating efficiency indicators
- **Momentum indicators**: Quarter-over-quarter improvements

#### Presenter Commentary
"This type of cross-sectional analysis would typically require building custom spreadsheets and pulling data from multiple sources. The agent does this automatically with current data."

#### Key Points to Highlight
- **Ranking capability**: Automatic sorting and comparison
- **Multiple metrics**: Revenue and profitability combined
- **Operational insight**: Margin analysis for efficiency trends
- **Investment relevance**: Performance indicators for stock selection

---

### Question 4: Visualization and Export (1 minute)

#### The Ask
**Copy/Paste into Agent**:
```
Create a summary table showing company name, latest quarter revenue, revenue surprise %, and EPS surprise % for the top 5 performing tech companies.
```

#### Expected Agent Response Pattern
- **Formatted table**: Clean, professional presentation
- **Key metrics**: Revenue, surprises, company names
- **Sorted results**: Top performers highlighted
- **Export-ready**: Suitable for reports/presentations

#### Presenter Commentary
"The agent can format results for immediate use in client presentations or internal reports. This table is ready to be copied into our research reports."

---

### Scenario 1 Wrap-up (4 minutes)

#### Value Delivered Summary
**Presenter**: "In just 10 minutes, we've accomplished what would typically take an analyst 2-3 hours:
- ✅ Multi-company earnings analysis across 10 tech companies
- ✅ Deep-dive analysis on Snowflake's growth trajectory  
- ✅ Sector-wide performance ranking with margin analysis
- ✅ Export-ready summary table for client reporting"

#### Technical Capabilities Demonstrated
- **Natural language queries** → Complex financial analysis
- **Multi-table joins** → Earnings, estimates, company data
- **Contextual understanding** → Growth vs value stock metrics
- **Dynamic data** → Current quarter with proper date handling

#### Business Impact
- **Analyst productivity**: 3x faster earnings analysis
- **Coverage expansion**: Ability to analyze more companies
- **Insight quality**: More time for interpretation vs data gathering
- **Client value**: Faster turnaround on market insights

---

## 🎬 Scenario 2: Thematic Research Agent
*15-minute standalone demo showcasing investment theme discovery*

### Context Setting (1 minute)
**Presenter**: "Investment themes drive major allocation decisions. Identifying emerging themes early provides competitive advantage, but manually reviewing hundreds of research reports is extremely time-intensive. Let me show you how AI can accelerate theme discovery from weeks to minutes."

**Action**: Switch to Thematic Research Agent in Snowflake Intelligence

---

### Question 5: Investment Theme Discovery (3 minutes)

#### The Ask
**Copy/Paste into Agent**:
```
What are the top investment themes emerging from recent technology sector research reports? Include the key companies being highlighted and the main investment theses.
```

#### Expected Agent Response Pattern
- **Theme identification**: AI/Enterprise AI, Data Cloud, etc.
- **Supporting companies**: NVDA, MSFT, SNOW, etc.
- **Investment theses**: Summarized from research reports
- **Market opportunity**: Size and growth projections

#### Presenter Commentary (while processing)
"The agent is analyzing multiple research reports simultaneously, extracting themes and synthesizing investment arguments. This type of thematic analysis typically requires reading dozens of reports manually."

#### Key Points to Highlight
- **Theme synthesis**: Multiple reports → Coherent themes
- **Company mapping**: Themes → Specific investment opportunities
- **Thesis summary**: Complex arguments → Digestible insights
- **Current relevance**: Recent research with timely themes

---

### Question 6: AI Theme Deep Dive (4 minutes)

#### The Ask
**Copy/Paste into Agent**:
```
Can you elaborate on the artificial intelligence investment theme? Which companies are best positioned to benefit, what are the key growth drivers, and what risks are analysts highlighting?
```

#### Expected Agent Response Pattern
- **Theme elaboration**: Detailed AI adoption trends
- **Company positioning**: NVDA (chips), MSFT (cloud), SNOW (data)
- **Growth drivers**: Enterprise adoption, infrastructure demand
- **Risk factors**: Competition, regulation, execution risk

#### Presenter Commentary
"This deep-dive pulls from multiple research reports to provide a comprehensive view of the AI theme. Notice how it balances opportunities with risks - crucial for investment decision-making."

#### Key Points to Highlight
- **Multi-source synthesis**: Comprehensive theme coverage
- **Balanced analysis**: Opportunities AND risks
- **Investment relevance**: Actionable company insights
- **Market context**: Size, growth, competitive dynamics

---

### Question 7: Snowflake Research Analysis (2 minutes)

#### The Ask
**Copy/Paste into Agent**:
```
What do research analysts say specifically about Snowflake's competitive position in the data cloud market? Include any recent price targets and ratings.
```

#### Expected Agent Response Pattern
- **Competitive analysis**: SNOW vs peers in data cloud
- **Analyst opinions**: Specific research commentary
- **Price targets**: Recent valuations from research firms
- **Rating consensus**: Buy/Hold/Sell recommendations

#### Presenter Commentary
"Here we're drilling down to company-specific research insights. This would normally require searching through multiple research databases and analyst reports."

#### Key Points to Highlight
- **Company focus**: Targeted analysis on specific stock
- **Valuation context**: Price targets for investment decisions
- **Competitive positioning**: Market share and differentiation
- **Analyst consensus**: Multiple firm perspectives synthesized

---

### Question 8: Research Source Verification (1 minute)

#### The Ask
**Copy/Paste into Agent**:
```
Can you provide specific quotes from research reports about enterprise AI adoption trends? Include the analyst names and firms.
```

#### Expected Agent Response Pattern
- **Direct quotes**: Actual excerpts from research reports
- **Source attribution**: Analyst names and research firms
- **Publication dates**: Recent research timeframes
- **Supporting evidence**: Specific data points cited

#### Presenter Commentary
"The agent can surface the actual research content, not just summaries. This provides the supporting evidence needed for investment committee presentations."

---

### Scenario 2 Wrap-up (4 minutes)

#### Value Delivered Summary
**Presenter**: "In 10 minutes, we've accomplished thematic research that would typically take 1-2 weeks:
- ✅ Identified top investment themes from dozens of research reports
- ✅ Deep analysis of AI theme with companies and risk factors
- ✅ Company-specific research insights with price targets
- ✅ Source verification with actual research quotes and attribution"

#### Technical Capabilities Demonstrated
- **Semantic search** → Relevant content discovery
- **Theme extraction** → Pattern recognition across reports
- **Content synthesis** → Multiple sources → Coherent analysis
- **Source attribution** → Audit trail for investment decisions

#### Business Impact
- **Theme discovery**: Weeks of manual work → Minutes of AI analysis
- **Research coverage**: Comprehensive vs selective due to time constraints
- **Investment timing**: Earlier identification of emerging themes
- **Decision quality**: Better supporting evidence and risk analysis

---

## 🎯 Combined Demo Impact

### Total Time Investment
- **Traditional approach**: 4-6 hours for comparable analysis
- **AI-augmented approach**: 20 minutes + analyst interpretation
- **Time savings**: ~15x productivity improvement

### Quality Improvements
- **Coverage**: All relevant companies vs sample due to time limits
- **Recency**: Current quarter data vs potentially stale information
- **Consistency**: Standardized analysis vs analyst-dependent approaches
- **Auditability**: Clear source attribution vs memory-based insights

### Strategic Value
- **Competitive advantage**: Earlier theme identification
- **Resource allocation**: Analysts focus on insights vs data gathering
- **Client service**: Faster response to market developments
- **Risk management**: More comprehensive coverage of investment universe

---

## 🛠️ Demo Troubleshooting

### If Agent Response is Slow
**Presenter**: "The agent is processing complex financial calculations across multiple data sources in real-time. This is the type of analysis that would typically require several different tools and manual data integration."

### If Asked About Data Accuracy
**Presenter**: "This demo uses synthetic data designed to showcase capabilities. In production, this connects to your real market data feeds, research databases, and earnings data sources."

### If Technical Questions Arise
**Presenter**: "The underlying technology uses Snowflake Cortex Analyst for structured data analysis and Cortex Search for unstructured research content. Happy to dive deeper into the technical architecture after the demo."

---

## 📝 Demo Execution Checklist

### Before Starting
- [ ] Snowflake Intelligence UI loaded and responsive
- [ ] Both agents accessible and tested
- [ ] Current date noted for dynamic data context  
- [ ] Backup browser tab ready
- [ ] Demo questions copied and ready to paste

### During Demo
- [ ] Maintain energy and enthusiasm
- [ ] Highlight time savings at each step
- [ ] Connect features to business value
- [ ] Engage audience with questions
- [ ] Handle any technical issues smoothly

### After Demo
- [ ] Summarize key value propositions
- [ ] Provide deployment script and documentation
- [ ] Schedule follow-up technical discussions
- [ ] Capture feedback and requirements

---

*Ready for live demo execution - September 2025*
