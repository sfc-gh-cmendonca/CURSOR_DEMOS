# JPMC Markets AI Demo - Setup Guide
*Demo Scenarios 1 & 2 for Equity Research Analysts*

## 🎉 **Demo Successfully Deployed!** ✅

This demo includes:
- **2 Semantic Views** for Cortex Analyst (earnings analysis & thematic research) 
- **2 Cortex Search Services** for document search (transcripts & reports)
- **7 Tech Companies** with realistic sample data (AAPL, MSFT, GOOGL, NVDA, TSLA, META, SNOW)
- **Dual-Tool Agents** combining structured data analysis + unstructured content search

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

### 3. Deploy the Enhanced Dual-Tool Demo
```bash
python deploy_dual_tool_demo.py
```

✅ **This creates**:
- **2 Semantic Views** in `MARKETS_AI_DEMO.ANALYTICS` schema
- **2 Cortex Search Services** for document search
- **Sample data** for 7 tech companies (AAPL, MSFT, GOOGL, NVDA, TSLA, META, SNOW)

### 4. Configure Sophisticated Dual-Tool Agents
1. Log into Snowflake Intelligence UI
2. **Follow the comprehensive guide**: `DUAL_TOOL_AGENT_SETUP.md`
3. **Create two sophisticated agents**:
   - `Tech Earnings Analysis Assistant` (Cortex Analyst + Cortex Search)
   - `Tech Thematic Research Assistant` (Cortex Analyst + Cortex Search)
4. **Test both agents** with the enhanced dual-tool questions

### 5. Run the Enhanced Demo
Follow the advanced scripts in `DUAL_TOOL_DEMO_SCRIPTS.md`

### 6. Cleanup (Optional)
When you're done with the demo, you can clean up all objects:

```bash
# Complete cleanup - removes everything
python cleanup_demo.py complete

# Partial cleanup - keeps database structure
python cleanup_demo.py partial

# Data only cleanup - clears table data only
python cleanup_demo.py data_only
```

⚠️ **WARNING**: Cleanup actions cannot be undone!

---

## 📊 What Gets Created

### Database Structure ✅ **Successfully Deployed**
```
MARKETS_AI_DEMO/
├── RAW_DATA/
│   ├── companies (7 tech companies including SNOW)
│   ├── earnings_data (28 quarterly reports)
│   ├── earnings_call_transcripts (3 earnings call transcripts)
│   └── research_reports (3 thematic research reports)
├── ANALYTICS/
│   ├── earnings_analysis_semantic ✅ (Snowflake Semantic View)
│   └── thematic_research_semantic ✅ (Snowflake Semantic View)
└── SEARCH_SERVICES/
    ├── earnings_transcripts_search ✅ (Cortex Search Service)
    └── research_reports_search ✅ (Cortex Search Service)
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

**✅ Deployment Successful**: The semantic views and search services are working correctly!

**Agent configuration issues**:
- Ensure you're using the correct database: `MARKETS_AI_DEMO`
- Verify schema: `ANALYTICS` for semantic views
- Check ID/Title columns are set correctly for Cortex Search tools

**Agent not responding to queries**:
- Test semantic views: Use simple questions like "Show me Apple's latest earnings"
- Test search services: Use queries like "What did management say about AI strategy?"
- Verify both Cortex Analyst and Cortex Search tools are configured

**Performance optimization**:
- Use warehouse size M or L for better performance
- Search services may take 5-10 minutes to fully index after deployment
- Complex queries combining both tools may take longer initially

### Support Resources
- **Agent Setup Guide**: `DUAL_TOOL_AGENT_SETUP.md`
- **Demo Scripts**: `DUAL_TOOL_DEMO_SCRIPTS.md`
- **Cleanup Tool**: `cleanup_demo.py` (3 cleanup levels available)

---

## 🧹 Cleanup Options

The `cleanup_demo.py` script provides three levels of cleanup:

### Complete Cleanup (`python cleanup_demo.py complete`)
- ✅ Removes ENTIRE `MARKETS_AI_DEMO` database
- ✅ Removes all schemas, tables, views, and search services  
- ✅ Perfect for completely resetting after demo
- ⚠️ **WARNING**: This cannot be undone!

### Partial Cleanup (`python cleanup_demo.py partial`) 
- ✅ Removes all data and objects
- ✅ Keeps database and schema structure
- ✅ Good for keeping structure while clearing content

### Data Only Cleanup (`python cleanup_demo.py data_only`)
- ✅ Truncates all table data
- ✅ Keeps all objects, views, and services intact
- ✅ Perfect for reloading fresh demo data

### Cleanup Troubleshooting
- If cleanup fails, you can manually drop objects in Snowflake UI
- Run cleanup with different levels if complete cleanup fails
- Check object dependencies if individual drops fail

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
