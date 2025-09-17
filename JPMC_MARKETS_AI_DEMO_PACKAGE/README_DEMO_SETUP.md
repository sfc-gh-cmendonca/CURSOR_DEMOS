# JPMC Markets AI Demo - Setup Guide
*Demo Scenarios 1 & 2 for Equity Research Analysts*

## 🎯 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Snowflake Connection
Ensure your `connections.toml` file is properly configured at one of these locations:
- **macOS**: `~/Library/Application Support/snowflake/connections.toml`
- **Linux**: `~/.config/snowflake/connections.toml`  
- **Windows**: `%USERPROFILE%\AppData\Local\snowflake\connections.toml`

Example `connections.toml` content:
```toml
[default]
account = "your_account_identifier"
user = "your_username"
password = "your_password"
warehouse = "COMPUTE_WH"
database = "MARKETS_AI_DEMO"
schema = "RAW_DATA"
role = "SYSADMIN"
```

### 3. Deploy the Demo
```bash
python deploy_markets_ai_demo.py
```

### 4. Configure Snowflake Intelligence Agents
1. Log into Snowflake Intelligence UI
2. Import agent configurations from `snowflake_intelligence_agents/` directory:
   - `earnings_analysis_agent.md`
   - `thematic_research_agent.md`
3. Test both agents with simple queries

### 5. Run the Demo
Follow the detailed scripts in `DEMO_SCENARIO_SCRIPTS.md`

---

## 📊 What Gets Created

### Database Structure
```
MARKETS_AI_DEMO/
├── RAW_DATA/
│   ├── companies (10 tech companies including SNOW)
│   ├── earnings_data (8 quarters per company)
│   ├── stock_prices (2 years daily data)
│   ├── market_events (5 major tech sector events)
│   └── research_reports (3 thematic research reports)
├── ENRICHED_DATA/
│   └── (Reserved for future enhancements)
├── ANALYTICS/
│   ├── earnings_analysis_semantic (Cortex Analyst view)
│   └── thematic_research_semantic (Cortex Analyst view)
├── SEARCH_SERVICES/
│   └── research_reports_search (Cortex Search service)
└── MARKETPLACE_DATA/
    └── economic_indicators (Placeholder for marketplace data)
```

### Tech Companies Included
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.  
- **NVDA** - NVIDIA Corporation
- **TSLA** - Tesla Inc.
- **META** - Meta Platforms Inc.
- **SNOW** - Snowflake Inc. ⭐ (Primary focus)
- **CRM** - Salesforce Inc.
- **ORCL** - Oracle Corporation
- **AMD** - Advanced Micro Devices Inc.

### Data Features
- **Dynamic dates**: All data uses current date as reference
- **Realistic correlations**: Earnings surprises tied to market events
- **Growth patterns**: SNOW shows high-growth SaaS characteristics
- **Market events**: 5 major events affecting tech sector performance
- **Research themes**: AI adoption, data cloud transformation, sector trends

---

## 🎬 Demo Scenarios

### Scenario 1: Earnings Analysis (15 minutes)
**Agent**: `earnings_analysis_agent`  
**Focus**: Accelerating earnings season analysis  
**Key Questions**:
1. Multi-company quarterly performance vs estimates
2. Snowflake earnings trajectory and guidance analysis  
3. Tech sector performance ranking with margins
4. Summary table generation

### Scenario 2: Thematic Research (15 minutes)  
**Agent**: `thematic_research_agent`  
**Focus**: Investment theme discovery from research reports  
**Key Questions**:
1. Top investment themes from recent research
2. AI theme deep dive with companies and risks
3. Snowflake competitive positioning analysis
4. Research source verification with quotes

---

## 🛠️ Technical Architecture

### Snowflake Cortex Integration
- **Cortex Analyst**: Semantic views for structured earnings data
- **Cortex Search**: Full-text search across research reports
- **Snowflake Intelligence**: Agent orchestration platform
- **Dynamic Data**: All dates calculated relative to deployment time

### Agent Capabilities
- **Natural language**: Complex financial queries in plain English
- **Multi-table joins**: Automatic relationship understanding
- **Financial context**: Industry-specific knowledge and benchmarks
- **Source attribution**: Clear audit trail for all insights

### Data Quality Features
- **Realistic metrics**: Based on actual company performance patterns
- **Event correlation**: Market events drive stock price and earnings volatility
- **Growth profiles**: Each company shows appropriate growth characteristics
- **Seasonal patterns**: Quarterly variations reflect business cycles

---

## 📋 Pre-Demo Checklist

### Technical Validation
- [ ] Database deployment completed successfully
- [ ] All tables populated with expected record counts
- [ ] Semantic views queryable from Snowflake Intelligence
- [ ] Both agents respond to test queries
- [ ] Current quarter data reflects recent timeframe

### Presenter Preparation  
- [ ] Review latest tech sector news for current context
- [ ] Practice key demo questions for smooth delivery
- [ ] Confirm SNOW current stock price for relevance
- [ ] Test demo questions with agents
- [ ] Prepare backup slides for technical issues

### Audience Materials
- [ ] `DEMO_PRESENTER_NOTES.md` reviewed
- [ ] `DEMO_SCENARIO_SCRIPTS.md` ready for execution
- [ ] Technical architecture slides prepared
- [ ] Follow-up discussion topics identified

---

## 🎯 Success Metrics

### Demo Execution
- Both scenarios completed within 30 minutes
- All 8 demo questions answered successfully
- Clear demonstration of 15x time savings
- Audience engagement and follow-up questions

### Technical Performance
- Agent response times under 30 seconds
- Accurate financial calculations and comparisons
- Proper handling of dynamic date references
- Clean formatting of tables and visualizations

### Business Value Communication
- Clear articulation of analyst productivity gains
- Specific examples of hours saved per analysis
- Connection between features and investment outcomes
- Compelling case for implementation

---

## 🔧 Troubleshooting

### Common Issues

**Agent not responding**:
- Check Snowflake Intelligence connection
- Verify agent configurations are properly imported
- Test with simpler queries first

**Data appears outdated**:
- Confirm deployment script used dynamic date generation
- Check that current_date calculations are working
- Verify quarters are calculated from current date

**Missing data**:
- Check deployment logs for any failed table creation
- Validate record counts match expected minimums
- Ensure all SQL statements executed successfully

**Performance issues**:
- Verify warehouse size is appropriate (M or L recommended)
- Check for query result caching configuration
- Monitor for concurrent usage affecting performance

### Support Resources
- Deployment logs: `markets_ai_demo_deployment.log`
- Database validation queries in deployment script
- Agent configuration templates in `snowflake_intelligence_agents/`
- Technical architecture documentation

---

## 📈 Next Steps

### Immediate (Post-Demo)
1. Gather audience feedback and requirements
2. Schedule technical deep-dive sessions
3. Identify specific use cases for JPMC implementation
4. Plan proof-of-concept with real data

### Short Term (1-2 weeks)
1. Integration planning with existing research systems
2. Data source identification and mapping
3. User training program development
4. Security and compliance review

### Medium Term (1-3 months)
1. Production deployment planning
2. Analyst workflow integration
3. Performance optimization and scaling
4. Additional use case development

---

*Demo ready for deployment - September 2025*

**Contact**: JPMC Markets Team for technical support and implementation planning
