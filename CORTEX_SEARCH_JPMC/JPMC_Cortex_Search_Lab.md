# Cortex Search Hands-On Lab for JPMC Markets Team

## Overview

This hands-on lab will guide you through building a sophisticated search and RAG (Retrieval Augmented Generation) application using Snowflake Cortex Search, specifically designed for markets data and financial research use cases. You'll learn to create intelligent search experiences over market research reports, trading insights, and financial documents.

## Lab Objectives

By the end of this lab, you will:
- Understand Cortex Search capabilities for financial data
- Build a market research document search engine
- Create a trading insights chatbot using RAG
- Implement advanced filtering for market segments and asset classes
- Deploy a Streamlit application for the Markets team

## Prerequisites

- Snowflake account with Cortex features enabled
- Access to the `SNOWFLAKE.CORTEX_USER` database role
- Basic SQL knowledge
- Familiarity with financial markets terminology

## Dataset Overview

We'll work with three main datasets:
1. **Market Research Reports** - Equity research, bond analysis, commodity insights
2. **Trading Insights** - Daily market commentary, trade ideas, risk assessments
3. **Economic Indicators** - Fed minutes, ECB statements, economic data releases

## Lab Structure

### Part 1: Environment Setup and Data Preparation
### Part 2: Building Market Research Search
### Part 3: Creating Trading Insights Chatbot
### Part 4: Advanced Filtering and Analytics
### Part 5: Streamlit Application Deployment

---

## Part 1: Environment Setup and Data Preparation

### Step 1: Create Database and Schema

```sql
-- Create dedicated database for Markets team
CREATE DATABASE IF NOT EXISTS JPMC_MARKETS;
USE DATABASE JPMC_MARKETS;

-- Create schema for market data
CREATE SCHEMA IF NOT EXISTS MARKET_INTELLIGENCE;
USE SCHEMA MARKET_INTELLIGENCE;

-- Create warehouse for compute
CREATE WAREHOUSE IF NOT EXISTS MARKETS_WH 
WITH WAREHOUSE_SIZE = 'MEDIUM' 
AUTO_SUSPEND = 60 
AUTO_RESUME = TRUE;

USE WAREHOUSE MARKETS_WH;
```

### Step 2: Create Sample Market Research Table

```sql
-- Market Research Reports Table
CREATE OR REPLACE TABLE MARKET_RESEARCH_REPORTS (
    report_id STRING,
    title STRING,
    content TEXT,
    asset_class STRING,
    sector STRING,
    region STRING,
    analyst_name STRING,
    publication_date DATE,
    rating STRING,
    target_price FLOAT,
    ticker_symbol STRING
);

-- Insert sample market research data
INSERT INTO MARKET_RESEARCH_REPORTS VALUES
('RPT001', 'Q4 2024 Technology Sector Outlook', 
 'The technology sector continues to show resilience despite macroeconomic headwinds. Cloud computing adoption remains strong with enterprise spending on digital transformation initiatives increasing 15% YoY. Key players like Microsoft, Amazon, and Google are well-positioned for continued growth. We maintain our overweight recommendation on large-cap tech stocks with particular emphasis on AI-enabled companies. Risk factors include potential regulatory changes and interest rate sensitivity.',
 'Equity', 'Technology', 'North America', 'Sarah Chen', '2024-01-15', 'Overweight', NULL, 'TECH'),

('RPT002', 'Federal Reserve Policy Impact on Bond Markets',
 'Recent Federal Reserve communications suggest a more dovish stance heading into 2024. The central bank has signaled potential rate cuts if inflation continues to moderate. This environment presents opportunities in intermediate-term Treasury bonds and high-grade corporate credit. Duration risk should be carefully managed as yield curve dynamics remain uncertain. Investment grade corporate spreads are attractive at current levels.',
 'Fixed Income', 'Government', 'North America', 'Michael Rodriguez', '2024-01-20', 'Positive', NULL, 'BONDS'),

('RPT003', 'Commodity Markets: Energy Transition Opportunities',
 'The energy transition is creating significant opportunities in critical minerals and renewable energy infrastructure. Copper demand is expected to surge 20% by 2030 driven by electrification trends. Lithium prices have corrected from peaks but long-term fundamentals remain strong. Oil markets face supply constraints while demand patterns shift. We recommend exposure to energy transition metals through diversified commodity funds.',
 'Commodities', 'Energy', 'Global', 'David Kim', '2024-01-18', 'Positive', 95.50, 'COMMODITIES');
```

### Step 3: Create Trading Insights Table

```sql
-- Trading Insights and Commentary Table
CREATE OR REPLACE TABLE TRADING_INSIGHTS (
    insight_id STRING,
    title STRING,
    content TEXT,
    market_segment STRING,
    urgency_level STRING,
    trade_idea STRING,
    risk_level STRING,
    time_horizon STRING,
    analyst_name STRING,
    publication_timestamp TIMESTAMP
);

-- Insert sample trading insights
INSERT INTO TRADING_INSIGHTS VALUES
('TI001', 'USD/JPY Technical Breakout Setup',
 'USD/JPY has broken above key resistance at 150.00 with strong momentum. Technical indicators suggest further upside potential to 152.50. Bank of Japan intervention risk remains but appears limited at current levels. Consider long USD/JPY positions with tight stop loss at 149.50. Position size should reflect elevated volatility in this pair.',
 'FX', 'Medium', 'Long USD/JPY', 'Medium', 'Short-term', 'Alex Thompson', '2024-01-22 09:30:00'),

('TI002', 'Equity Index Volatility Play',
 'VIX has declined to sub-15 levels creating opportunities for volatility strategies. Equity markets showing complacency despite geopolitical risks. Consider long volatility positions through VIX calls or variance swaps. Target entry on further VIX decline below 14. Risk management crucial as volatility timing is challenging.',
 'Equity Derivatives', 'High', 'Long Volatility', 'High', 'Short-term', 'Lisa Wang', '2024-01-22 14:15:00'),

('TI003', 'Credit Spread Tightening Opportunity',
 'Investment grade credit spreads have widened 15bp this week on earnings concerns. This presents attractive entry points for credit investors. Focus on A-rated corporates in defensive sectors. Expect spreads to tighten as earnings fears prove overblown. Target 3-month holding period with 10bp tightening potential.',
 'Credit', 'Low', 'Long Credit', 'Low', 'Medium-term', 'Robert Chang', '2024-01-22 16:45:00');
```

### Step 4: Create Economic Indicators Table

```sql
-- Economic Indicators and Central Bank Communications
CREATE OR REPLACE TABLE ECONOMIC_INDICATORS (
    indicator_id STRING,
    title STRING,
    content TEXT,
    source_institution STRING,
    indicator_type STRING,
    region STRING,
    impact_level STRING,
    release_date DATE,
    next_update DATE
);

-- Insert sample economic data
INSERT INTO ECONOMIC_INDICATORS VALUES
('EI001', 'FOMC December Meeting Minutes',
 'Federal Reserve officials expressed cautious optimism about inflation trends while acknowledging labor market resilience. Several members noted the importance of remaining flexible in policy approach. Discussion centered on the appropriate pace of potential rate adjustments in 2024. Committee members emphasized data dependence and gradual approach to policy normalization.',
 'Federal Reserve', 'Monetary Policy', 'United States', 'High', '2024-01-03', '2024-02-01'),

('EI002', 'ECB Economic Bulletin January 2024',
 'European Central Bank highlighted improving economic conditions across the Eurozone while noting persistent inflation concerns in services sector. Growth projections revised modestly higher for 2024. Wage growth momentum continues but shows signs of stabilization. Bank stressed commitment to price stability mandate while monitoring employment trends.',
 'European Central Bank', 'Economic Outlook', 'Europe', 'High', '2024-01-11', '2024-02-08'),

('EI003', 'Bank of England Financial Stability Report',
 'UK financial system remains resilient despite elevated interest rates and geopolitical uncertainties. Household debt levels manageable but warrant monitoring. Commercial real estate sector facing headwinds from higher financing costs. Banks maintain strong capital positions and adequate liquidity buffers.',
 'Bank of England', 'Financial Stability', 'United Kingdom', 'Medium', '2024-01-16', '2024-04-16');
```

---

## Part 2: Building Market Research Search

### Step 5: Create Cortex Search Service for Market Research

```sql
-- Create Cortex Search Service for Market Research Reports
CREATE OR REPLACE CORTEX SEARCH SERVICE MARKET_RESEARCH_SEARCH
ON content
ATTRIBUTES asset_class, sector, region, analyst_name, rating, ticker_symbol
WAREHOUSE = MARKETS_WH
TARGET_LAG = '1 hour'
AS (
    SELECT 
        report_id,
        title,
        content,
        asset_class,
        sector,
        region,
        analyst_name,
        rating,
        ticker_symbol,
        publication_date
    FROM MARKET_RESEARCH_REPORTS
);
```

### Step 6: Test Market Research Search

```sql
-- Test basic search functionality
SELECT * FROM TABLE(
    JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_RESEARCH_SEARCH(
        query => 'technology sector outlook artificial intelligence',
        limit => 5
    )
);

-- Test filtered search by asset class
SELECT * FROM TABLE(
    JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_RESEARCH_SEARCH(
        query => 'federal reserve interest rates',
        filter => {'asset_class': 'Fixed Income'},
        limit => 3
    )
);

-- Test search with multiple filters
SELECT * FROM TABLE(
    JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_RESEARCH_SEARCH(
        query => 'investment opportunities growth',
        filter => {
            'region': 'North America',
            'rating': 'Overweight'
        },
        limit => 5
    )
);
```

---

## Part 3: Creating Trading Insights Chatbot

### Step 7: Create Trading Insights Search Service

```sql
-- Create Cortex Search Service for Trading Insights
CREATE OR REPLACE CORTEX SEARCH SERVICE TRADING_INSIGHTS_SEARCH
ON content
ATTRIBUTES market_segment, urgency_level, risk_level, time_horizon, analyst_name
WAREHOUSE = MARKETS_WH
TARGET_LAG = '15 minutes'
AS (
    SELECT 
        insight_id,
        title,
        content,
        market_segment,
        urgency_level,
        trade_idea,
        risk_level,
        time_horizon,
        analyst_name,
        publication_timestamp
    FROM TRADING_INSIGHTS
);
```

### Step 8: Build RAG Function for Trading Chatbot

```sql
-- Create function for RAG-powered trading assistant
CREATE OR REPLACE FUNCTION TRADING_ASSISTANT(question STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.9'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'generate_response'
AS
$$
def generate_response(question):
    import snowflake.snowpark as snowpark
    from snowflake.snowpark.functions import call_builtin
    
    # Get current session
    session = snowpark.context.get_active_session()
    
    # Search for relevant trading insights
    search_results = session.sql(f"""
        SELECT content, market_segment, trade_idea, risk_level
        FROM TABLE(JPMC_MARKETS.MARKET_INTELLIGENCE.TRADING_INSIGHTS_SEARCH(
            query => '{question}',
            limit => 3
        ))
    """).collect()
    
    # Prepare context from search results
    context = ""
    for row in search_results:
        context += f"Trading Insight: {row['CONTENT']} "
        context += f"Market: {row['MARKET_SEGMENT']} "
        context += f"Trade Idea: {row['TRADE_IDEA']} "
        context += f"Risk: {row['RISK_LEVEL']}\\n\\n"
    
    # Create prompt for LLM
    prompt = f"""
    You are a senior trading analyst at JPMorgan Chase. Based on the following trading insights and market intelligence, 
    provide a concise and actionable response to the trader's question.
    
    Question: {question}
    
    Relevant Trading Intelligence:
    {context}
    
    Guidelines:
    - Provide specific, actionable advice
    - Include risk considerations
    - Mention time horizons when relevant
    - Use professional trading terminology
    - Be concise but comprehensive
    
    Response:
    """
    
    # Generate response using Cortex LLM
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mixtral-8x7b',
            '{prompt}'
        ) as response
    """).collect()
    
    return result[0]['RESPONSE'] if result else "Unable to generate response."
$$;
```

### Step 9: Test Trading Assistant

```sql
-- Test the trading assistant function
SELECT TRADING_ASSISTANT('What are the current opportunities in FX markets?');

SELECT TRADING_ASSISTANT('Should I be concerned about volatility levels?');

SELECT TRADING_ASSISTANT('Any credit market opportunities this week?');
```

---

## Part 4: Advanced Filtering and Analytics

### Step 10: Create Economic Indicators Search Service

```sql
-- Create search service for economic indicators
CREATE OR REPLACE CORTEX SEARCH SERVICE ECONOMIC_INDICATORS_SEARCH
ON content
ATTRIBUTES source_institution, indicator_type, region, impact_level
WAREHOUSE = MARKETS_WH
TARGET_LAG = '30 minutes'
AS (
    SELECT 
        indicator_id,
        title,
        content,
        source_institution,
        indicator_type,
        region,
        impact_level,
        release_date,
        next_update
    FROM ECONOMIC_INDICATORS
);
```

### Step 11: Create Comprehensive Market Intelligence Function

```sql
-- Create comprehensive market intelligence search function
CREATE OR REPLACE FUNCTION MARKET_INTELLIGENCE_SEARCH(
    query STRING,
    search_type STRING DEFAULT 'ALL'
)
RETURNS TABLE (
    source STRING,
    title STRING,
    content STRING,
    category STRING,
    relevance_score FLOAT,
    metadata VARIANT
)
LANGUAGE SQL
AS
$$
    WITH research_results AS (
        SELECT 
            'RESEARCH' as source,
            title,
            content,
            asset_class as category,
            score as relevance_score,
            OBJECT_CONSTRUCT(
                'analyst_name', analyst_name,
                'sector', sector,
                'region', region,
                'rating', rating,
                'publication_date', publication_date
            ) as metadata
        FROM TABLE(JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_RESEARCH_SEARCH(
            query => query,
            limit => 5
        ))
        WHERE search_type IN ('ALL', 'RESEARCH')
    ),
    
    trading_results AS (
        SELECT 
            'TRADING' as source,
            title,
            content,
            market_segment as category,
            score as relevance_score,
            OBJECT_CONSTRUCT(
                'analyst_name', analyst_name,
                'trade_idea', trade_idea,
                'risk_level', risk_level,
                'time_horizon', time_horizon,
                'urgency_level', urgency_level
            ) as metadata
        FROM TABLE(JPMC_MARKETS.MARKET_INTELLIGENCE.TRADING_INSIGHTS_SEARCH(
            query => query,
            limit => 5
        ))
        WHERE search_type IN ('ALL', 'TRADING')
    ),
    
    economic_results AS (
        SELECT 
            'ECONOMIC' as source,
            title,
            content,
            indicator_type as category,
            score as relevance_score,
            OBJECT_CONSTRUCT(
                'source_institution', source_institution,
                'region', region,
                'impact_level', impact_level,
                'release_date', release_date
            ) as metadata
        FROM TABLE(JPMC_MARKETS.MARKET_INTELLIGENCE.ECONOMIC_INDICATORS_SEARCH(
            query => query,
            limit => 5
        ))
        WHERE search_type IN ('ALL', 'ECONOMIC')
    )
    
    SELECT * FROM research_results
    UNION ALL
    SELECT * FROM trading_results
    UNION ALL
    SELECT * FROM economic_results
    ORDER BY relevance_score DESC
$$;
```

### Step 12: Test Comprehensive Search

```sql
-- Test comprehensive market intelligence search
SELECT * FROM TABLE(MARKET_INTELLIGENCE_SEARCH('interest rates federal reserve'));

-- Test specific search types
SELECT * FROM TABLE(MARKET_INTELLIGENCE_SEARCH('volatility risk', 'TRADING'));

SELECT * FROM TABLE(MARKET_INTELLIGENCE_SEARCH('technology sector', 'RESEARCH'));
```

---

## Part 5: Streamlit Application Deployment

### Step 13: Create Streamlit Application

Create a new file called `jpmc_markets_intelligence.py`:

```python
import streamlit as st
import snowflake.connector
from snowflake.snowpark import Session
import pandas as pd
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="JPMC Markets Intelligence",
    page_icon="📈",
    layout="wide"
)

# Snowflake connection
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])

@st.cache_data
def run_query(query):
    with init_connection().cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Header
st.title("🏦 JPMC Markets Intelligence Platform")
st.markdown("*Powered by Snowflake Cortex Search*")

# Sidebar for filters and settings
with st.sidebar:
    st.header("Search Filters")
    
    search_type = st.selectbox(
        "Search Scope",
        ["ALL", "RESEARCH", "TRADING", "ECONOMIC"],
        help="Select the type of content to search"
    )
    
    if search_type in ["ALL", "RESEARCH"]:
        st.subheader("Research Filters")
        asset_classes = st.multiselect(
            "Asset Classes",
            ["Equity", "Fixed Income", "Commodities", "FX"],
            help="Filter by asset class"
        )
        
        sectors = st.multiselect(
            "Sectors",
            ["Technology", "Healthcare", "Financial", "Energy", "Consumer"],
            help="Filter by sector"
        )
    
    if search_type in ["ALL", "TRADING"]:
        st.subheader("Trading Filters")
        risk_levels = st.multiselect(
            "Risk Levels",
            ["Low", "Medium", "High"],
            help="Filter by risk level"
        )
        
        time_horizons = st.multiselect(
            "Time Horizons",
            ["Short-term", "Medium-term", "Long-term"],
            help="Filter by time horizon"
        )

# Main search interface
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Search Markets Intelligence",
        placeholder="e.g., 'Federal Reserve policy impact on equities' or 'USD/JPY technical outlook'"
    )

with col2:
    search_button = st.button("🔍 Search", type="primary")
    chat_mode = st.toggle("Chat Mode", help="Enable AI assistant responses")

# Search execution
if search_button and search_query:
    with st.spinner("Searching markets intelligence..."):
        # Execute search query
        search_sql = f"""
        SELECT * FROM TABLE(JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_INTELLIGENCE_SEARCH(
            '{search_query}', '{search_type}'
        ))
        """
        
        results = run_query(search_sql)
        
        # Store in search history
        st.session_state.search_history.append({
            'query': search_query,
            'timestamp': datetime.now(),
            'results_count': len(results)
        })
        
        if results:
            st.success(f"Found {len(results)} relevant results")
            
            # Display results
            for i, row in enumerate(results):
                source, title, content, category, score, metadata = row
                
                with st.expander(f"📄 {title} ({source}) - Score: {score:.3f}"):
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**Content:** {content}")
                    
                    # Display metadata
                    if metadata:
                        metadata_dict = json.loads(metadata)
                        st.markdown("**Metadata:**")
                        for key, value in metadata_dict.items():
                            if value:
                                st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            # Chat mode response
            if chat_mode and search_type in ["ALL", "TRADING"]:
                with st.spinner("Generating AI response..."):
                    chat_sql = f"""
                    SELECT JPMC_MARKETS.MARKET_INTELLIGENCE.TRADING_ASSISTANT('{search_query}') as response
                    """
                    chat_result = run_query(chat_sql)
                    
                    if chat_result:
                        st.markdown("---")
                        st.markdown("### 🤖 AI Trading Assistant Response")
                        st.markdown(chat_result[0][0])
        else:
            st.warning("No results found. Try adjusting your search query or filters.")

# Analytics dashboard
if st.session_state.search_history:
    st.markdown("---")
    st.subheader("📊 Search Analytics")
    
    # Recent searches
    with st.expander("Recent Searches"):
        df_history = pd.DataFrame(st.session_state.search_history)
        st.dataframe(df_history, use_container_width=True)
    
    # Quick access to market data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Latest Market Research"):
            latest_research_sql = """
            SELECT title, analyst_name, publication_date 
            FROM JPMC_MARKETS.MARKET_INTELLIGENCE.MARKET_RESEARCH_REPORTS 
            ORDER BY publication_date DESC 
            LIMIT 5
            """
            latest_research = run_query(latest_research_sql)
            for row in latest_research:
                st.write(f"• {row[0]} - {row[1]}")
    
    with col2:
        if st.button("⚡ Urgent Trading Insights"):
            urgent_insights_sql = """
            SELECT title, market_segment, urgency_level 
            FROM JPMC_MARKETS.MARKET_INTELLIGENCE.TRADING_INSIGHTS 
            WHERE urgency_level = 'High'
            ORDER BY publication_timestamp DESC 
            LIMIT 5
            """
            urgent_insights = run_query(urgent_insights_sql)
            for row in urgent_insights:
                st.write(f"• {row[0]} ({row[1]})")
    
    with col3:
        if st.button("📅 Upcoming Economic Events"):
            upcoming_events_sql = """
            SELECT title, source_institution, next_update 
            FROM JPMC_MARKETS.MARKET_INTELLIGENCE.ECONOMIC_INDICATORS 
            WHERE next_update >= CURRENT_DATE()
            ORDER BY next_update 
            LIMIT 5
            """
            upcoming_events = run_query(upcoming_events_sql)
            for row in upcoming_events:
                st.write(f"• {row[0]} - {row[2]}")

# Footer
st.markdown("---")
st.markdown("*JPMC Markets Intelligence Platform - Built with Snowflake Cortex Search*")
```

### Step 14: Configure Streamlit Secrets

Create a `.streamlit/secrets.toml` file:

```toml
[snowflake]
user = "your_username"
password = "your_password"
account = "your_account"
warehouse = "MARKETS_WH"
database = "JPMC_MARKETS"
schema = "MARKET_INTELLIGENCE"
```

### Step 15: Deploy the Application

```bash
# Install required packages
pip install streamlit snowflake-connector-python snowflake-snowpark-python

# Run the application
streamlit run jpmc_markets_intelligence.py
```

---

## Part 6: Advanced Features and Testing

### Step 16: Create Performance Monitoring

```sql
-- Create view for search analytics
-- This view provides analytics on document counts across different services
-- It creates a unified view that:
-- 1. Tracks total documents in Market Research Reports
-- 2. Tracks total documents in Trading Insights
-- 3. Tracks total documents in Economic Indicators
-- The view updates automatically when queried to show current counts
CREATE OR REPLACE VIEW SEARCH_ANALYTICS AS
SELECT 
    'MARKET_RESEARCH' as service_name,
    CURRENT_TIMESTAMP() as check_time,
    (SELECT COUNT(*) FROM MARKET_RESEARCH_REPORTS) as total_documents
UNION ALL
SELECT 
    'TRADING_INSIGHTS' as service_name,
    CURRENT_TIMESTAMP() as check_time,
    (SELECT COUNT(*) FROM TRADING_INSIGHTS) as total_documents
UNION ALL
SELECT 
    'ECONOMIC_INDICATORS' as service_name,
    CURRENT_TIMESTAMP() as check_time,
    (SELECT COUNT(*) FROM ECONOMIC_INDICATORS) as total_documents;

-- Query to check search service status
SHOW CORTEX SEARCH SERVICES;
```

### Step 17: Sample Test Queries

Test your implementation with these market-specific queries:

```sql
-- Test 1: Cross-asset search
SELECT * FROM TABLE(MARKET_INTELLIGENCE_SEARCH(
    'inflation impact on bond yields and equity valuations'
));


-- Test 2: Risk-focused search
-- Test 2: Risk-focused search - searches for trading opportunities with high volatility
-- This query uses the MARKET_INTELLIGENCE_SEARCH function to find documents
-- that contain information about high volatility trading opportunities
-- It will return relevant market research reports that discuss volatile market conditions
-- and potential trading strategies to capitalize on price movements
SELECT * FROM TABLE(MARKET_INTELLIGENCE_SEARCH(
    'high volatility trading opportunities'
));

-- Test 3: Regional focus
SELECT * FROM TABLE(TRADING_INSIGHTS_SEARCH(
    query => 'European markets central bank policy',
    filter => {'market_segment': 'FX'}
));

-- Test 4: AI Assistant queries
SELECT TRADING_ASSISTANT('What are the key risks to watch in credit markets this week?');

SELECT TRADING_ASSISTANT('Should we be positioning for higher volatility?');
```

---

## Part 7: Production Considerations

### Security and Access Control

```sql
-- Create role for Markets team
CREATE ROLE IF NOT EXISTS MARKETS_ANALYST;
CREATE ROLE IF NOT EXISTS MARKETS_TRADER;
CREATE ROLE IF NOT EXISTS MARKETS_MANAGER;

-- Grant appropriate permissions
GRANT USAGE ON DATABASE JPMC_MARKETS TO ROLE MARKETS_ANALYST;
GRANT USAGE ON SCHEMA MARKET_INTELLIGENCE TO ROLE MARKETS_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA MARKET_INTELLIGENCE TO ROLE MARKETS_ANALYST;

-- Grant search service usage
GRANT USAGE ON CORTEX SEARCH SERVICE MARKET_RESEARCH_SEARCH TO ROLE MARKETS_ANALYST;
GRANT USAGE ON CORTEX SEARCH SERVICE TRADING_INSIGHTS_SEARCH TO ROLE MARKETS_TRADER;
GRANT USAGE ON CORTEX SEARCH SERVICE ECONOMIC_INDICATORS_SEARCH TO ROLE MARKETS_ANALYST;
```

### Data Refresh Strategy

```sql
-- Create tasks for regular data refresh
CREATE OR REPLACE TASK REFRESH_MARKET_RESEARCH
WAREHOUSE = MARKETS_WH
SCHEDULE = 'USING CRON 0 9 * * * America/New_York'
AS
ALTER CORTEX SEARCH SERVICE MARKET_RESEARCH_SEARCH REFRESH;

CREATE OR REPLACE TASK REFRESH_TRADING_INSIGHTS
WAREHOUSE = MARKETS_WH
SCHEDULE = 'USING CRON */15 * * * * America/New_York'
AS
ALTER CORTEX SEARCH SERVICE TRADING_INSIGHTS_SEARCH REFRESH;

-- Resume tasks
ALTER TASK REFRESH_MARKET_RESEARCH RESUME;
ALTER TASK REFRESH_TRADING_INSIGHTS RESUME;
```

---

## Conclusion

You have successfully built a comprehensive Cortex Search solution for the JPMC Markets team that includes:

1. **Multi-source search** across research reports, trading insights, and economic indicators
2. **AI-powered trading assistant** using RAG capabilities
3. **Advanced filtering** by asset class, risk level, and time horizon
4. **Production-ready Streamlit application** with analytics dashboard
5. **Security controls** and automated refresh mechanisms

### Key Benefits Achieved:

- **Unified Search Experience**: One platform for all markets intelligence
- **Real-time Insights**: 15-minute refresh for trading insights
- **Risk-aware Recommendations**: Built-in risk level filtering
- **Contextual AI Responses**: RAG-powered assistant with market context
- **Scalable Architecture**: Easy to add new data sources and search services

### Next Steps:

1. **Data Integration**: Connect to real market data feeds
2. **Advanced Analytics**: Add sentiment analysis and trend detection
3. **Mobile Access**: Extend Streamlit app for mobile trading
4. **Alert System**: Implement real-time notifications for high-impact events
5. **Performance Optimization**: Fine-tune search parameters based on usage patterns

This lab provides a solid foundation for building sophisticated search and AI applications on financial markets data using Snowflake Cortex Search.

---

## Additional Resources

- [Snowflake Cortex Search Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [JPMC Python Training Repository](https://github.com/jpmorganchase/python-training)
- [Cortex Search Quickstart Guide](https://quickstarts.snowflake.com/guide/getting-started-with-llamaparse-and-cortex-search/)

---

**License**: Apache 2.0  
**Contact**: Your JPMC Technology Team 