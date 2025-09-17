-- =============================================
-- JPMC Cortex Search Lab - Create Tables
-- =============================================
-- This script creates the tables to store market intelligence data
-- that will be used by Cortex Search services.

-- Ensure we're in the correct context
USE ROLE CORTEX_USER_ROLE;
USE DATABASE JPMC_MARKETS;
USE SCHEMA MARKET_INTELLIGENCE;
USE WAREHOUSE CORTEX_WH;

-- =============================================
-- 1. MARKET RESEARCH REPORTS TABLE
-- =============================================

CREATE OR REPLACE TABLE market_research_reports (
    -- Primary identifiers
    report_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    
    -- Document content (this will be searched by Cortex Search)
    content TEXT NOT NULL,
    
    -- Metadata for filtering and attributes
    asset_class VARCHAR(50),          -- equity, fixed_income, commodities, fx
    sector VARCHAR(100),              -- technology, healthcare, financials, etc.
    region VARCHAR(50),               -- north_america, europe, asia_pacific, global
    risk_rating VARCHAR(20),          -- low, medium, high
    
    -- Analyst information
    analyst_name VARCHAR(100),
    analyst_team VARCHAR(100),
    
    -- Temporal data
    publish_date TIMESTAMP_NTZ,
    report_date TIMESTAMP_NTZ,
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Document metadata
    document_type VARCHAR(50) DEFAULT 'research_report',
    source_file VARCHAR(200),
    page_count INTEGER,
    
    -- Engagement metrics (for scoring boosts)
    views_count INTEGER DEFAULT 0,
    downloads_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,   -- 0.0 to 5.0 rating
    
    -- Tags for enhanced search
    tags ARRAY,
    
    -- Full-text search optimization
    content_vector VECTOR(FLOAT, 768)  -- For future vector search if needed
);

-- =============================================
-- 2. TRADING INSIGHTS TABLE
-- =============================================

CREATE OR REPLACE TABLE trading_insights (
    -- Primary identifiers
    insight_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    
    -- Document content (searchable)
    content TEXT NOT NULL,
    
    -- Trading-specific metadata
    instrument_type VARCHAR(50),      -- equity, bond, derivative, fx
    symbol VARCHAR(20),               -- AAPL, TSLA, EUR/USD, etc.
    market VARCHAR(50),               -- NYSE, NASDAQ, LSE, etc.
    trading_strategy VARCHAR(100),    -- momentum, value, arbitrage, etc.
    
    -- Risk and performance metrics
    risk_level VARCHAR(20),           -- low, medium, high
    target_return DECIMAL(5,2),       -- Expected return percentage
    max_drawdown DECIMAL(5,2),        -- Maximum expected loss
    time_horizon VARCHAR(50),         -- intraday, short_term, medium_term, long_term
    
    -- Author information
    trader_name VARCHAR(100),
    desk VARCHAR(100),
    
    -- Temporal data
    publish_date TIMESTAMP_NTZ,
    trade_date TIMESTAMP_NTZ,
    expiry_date TIMESTAMP_NTZ,
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Performance tracking (for scoring)
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    average_return DECIMAL(5,2) DEFAULT 0.0,
    sharpe_ratio DECIMAL(5,2) DEFAULT 0.0,
    
    -- Document metadata
    document_type VARCHAR(50) DEFAULT 'trading_insight',
    urgency VARCHAR(20) DEFAULT 'medium',    -- low, medium, high, urgent
    
    -- Engagement metrics
    likes_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0
);

-- =============================================
-- 3. ECONOMIC INDICATORS TABLE
-- =============================================

CREATE OR REPLACE TABLE economic_indicators (
    -- Primary identifiers
    indicator_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    
    -- Document content (searchable)
    content TEXT NOT NULL,
    
    -- Economic data metadata
    indicator_name VARCHAR(100),      -- GDP, CPI, unemployment, fed_rate, etc.
    country VARCHAR(50),              -- US, UK, EU, JP, CN, etc.
    frequency VARCHAR(20),            -- daily, weekly, monthly, quarterly, annual
    data_source VARCHAR(100),         -- Fed, ECB, BOJ, BLS, etc.
    
    -- Data values
    current_value DECIMAL(15,4),
    previous_value DECIMAL(15,4),
    forecast_value DECIMAL(15,4),
    change_percent DECIMAL(5,2),
    
    -- Impact assessment
    market_impact VARCHAR(20),        -- low, medium, high, critical
    impact_direction VARCHAR(20),     -- positive, negative, neutral
    affected_sectors ARRAY,           -- ['technology', 'healthcare', ...]
    
    -- Temporal data
    publish_date TIMESTAMP_NTZ,
    data_date TIMESTAMP_NTZ,          -- The date the economic data refers to
    next_release_date TIMESTAMP_NTZ,
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- Document metadata
    document_type VARCHAR(50) DEFAULT 'economic_indicator',
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Research metrics
    citation_count INTEGER DEFAULT 0,
    relevance_score DECIMAL(5,2) DEFAULT 0.0
);

-- =============================================
-- 4. DOCUMENT PROCESSING LOG
-- =============================================

CREATE OR REPLACE TABLE document_processing_log (
    log_id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50),
    document_type VARCHAR(50),
    processing_status VARCHAR(50),    -- pending, processing, completed, failed
    
    -- Processing details
    file_path VARCHAR(500),
    file_size_bytes INTEGER,
    processing_start_time TIMESTAMP_NTZ,
    processing_end_time TIMESTAMP_NTZ,
    processing_duration_seconds INTEGER,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    processed_by VARCHAR(100),
    processing_version VARCHAR(20),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =============================================
-- 5. SEARCH ANALYTICS TABLE
-- =============================================

CREATE OR REPLACE TABLE search_analytics (
    search_id VARCHAR(50) PRIMARY KEY,
    
    -- Search details
    search_query TEXT,
    search_service VARCHAR(100),      -- Name of the Cortex Search service used
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    
    -- Search parameters
    filters OBJECT,                   -- JSON object containing filter parameters
    scoring_config OBJECT,            -- JSON object containing scoring configuration
    result_limit INTEGER,
    
    -- Results metadata
    total_results INTEGER,
    top_result_score DECIMAL(5,4),
    average_result_score DECIMAL(5,4),
    
    -- Performance metrics
    search_duration_ms INTEGER,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- User interaction
    clicked_results ARRAY,            -- Array of result IDs that were clicked
    dwell_time_seconds INTEGER        -- Time spent reviewing results
);

-- =============================================
-- 6. CREATE INDEXES FOR PERFORMANCE
-- =============================================

-- Market Research Reports indexes
CREATE INDEX IF NOT EXISTS idx_market_research_asset_class 
    ON market_research_reports(asset_class);
CREATE INDEX IF NOT EXISTS idx_market_research_publish_date 
    ON market_research_reports(publish_date);
CREATE INDEX IF NOT EXISTS idx_market_research_sector 
    ON market_research_reports(sector);

-- Trading Insights indexes
CREATE INDEX IF NOT EXISTS idx_trading_insights_symbol 
    ON trading_insights(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_insights_risk_level 
    ON trading_insights(risk_level);
CREATE INDEX IF NOT EXISTS idx_trading_insights_publish_date 
    ON trading_insights(publish_date);

-- Economic Indicators indexes
CREATE INDEX IF NOT EXISTS idx_economic_indicators_country 
    ON economic_indicators(country);
CREATE INDEX IF NOT EXISTS idx_economic_indicators_indicator_name 
    ON economic_indicators(indicator_name);
CREATE INDEX IF NOT EXISTS idx_economic_indicators_data_date 
    ON economic_indicators(data_date);

-- =============================================
-- 7. CREATE VIEWS FOR EASIER QUERYING
-- =============================================

-- Unified view of all searchable content
CREATE OR REPLACE VIEW market_intelligence_unified AS
SELECT 
    report_id AS document_id,
    'market_research' AS source_type,
    title,
    content,
    asset_class AS category,
    sector AS subcategory,
    analyst_name AS author,
    publish_date,
    views_count AS engagement_score,
    tags
FROM market_research_reports

UNION ALL

SELECT 
    insight_id AS document_id,
    'trading_insight' AS source_type,
    title,
    content,
    instrument_type AS category,
    trading_strategy AS subcategory,
    trader_name AS author,
    publish_date,
    likes_count AS engagement_score,
    ARRAY_CONSTRUCT(symbol, market) AS tags
FROM trading_insights

UNION ALL

SELECT 
    indicator_id AS document_id,
    'economic_indicator' AS source_type,
    title,
    content,
    country AS category,
    indicator_name AS subcategory,
    data_source AS author,
    publish_date,
    citation_count AS engagement_score,
    affected_sectors AS tags
FROM economic_indicators;

-- Recent high-impact content view
CREATE OR REPLACE VIEW recent_high_impact_content AS
SELECT 
    document_id,
    source_type,
    title,
    content,
    author,
    publish_date,
    engagement_score
FROM market_intelligence_unified
WHERE publish_date >= DATEADD('days', -30, CURRENT_DATE())
    AND engagement_score > 10
ORDER BY publish_date DESC, engagement_score DESC;

-- =============================================
-- 8. INSERT SAMPLE DATA
-- =============================================

-- Sample Market Research Reports
INSERT INTO market_research_reports VALUES
('MRR_2024_001', 'AI Revolution in Financial Services: Opportunities and Risks',
 'The integration of artificial intelligence in financial services is accelerating rapidly. This comprehensive analysis examines the transformative potential of AI technologies including machine learning, natural language processing, and robotic process automation across various financial sectors. Key opportunities include enhanced fraud detection, personalized customer experiences, algorithmic trading optimization, and regulatory compliance automation. However, significant risks include model bias, data privacy concerns, regulatory uncertainty, and systemic risk amplification. Financial institutions must develop robust AI governance frameworks while investing in talent and infrastructure to capitalize on these emerging opportunities.',
 'technology', 'financial_services', 'global', 'medium',
 'Sarah Chen', 'Technology Research', 
 '2024-03-15 09:00:00', '2024-03-15 09:00:00', CURRENT_TIMESTAMP(),
 'research_report', 'ai_financial_services_2024.pdf', 45, 156, 89, 4.2,
 ARRAY_CONSTRUCT('AI', 'machine_learning', 'fintech', 'automation')),

('MRR_2024_002', 'ESG Investment Trends: Sustainable Finance in Emerging Markets',
 'Environmental, Social, and Governance (ESG) investing has gained significant momentum in emerging markets. This report analyzes ESG investment flows, regulatory developments, and performance metrics across key emerging economies including India, Brazil, and Southeast Asia. The growing awareness of climate risks, coupled with regulatory pressure and investor demand, is driving substantial capital allocation toward sustainable investments. However, challenges include limited ESG data availability, varying regulatory standards, and greenwashing concerns. We identify key opportunities in renewable energy infrastructure, sustainable agriculture, and social impact bonds.',
 'equity', 'sustainability', 'emerging_markets', 'medium',
 'Miguel Rodriguez', 'ESG Research',
 '2024-03-10 14:30:00', '2024-03-10 14:30:00', CURRENT_TIMESTAMP(),
 'research_report', 'esg_emerging_markets_2024.pdf', 52, 203, 127, 4.5,
 ARRAY_CONSTRUCT('ESG', 'sustainability', 'emerging_markets', 'climate')),

('MRR_2024_003', 'Central Bank Digital Currencies: Implications for Global Finance',
 'Central Bank Digital Currencies (CBDCs) represent a paradigmatic shift in monetary systems. This analysis examines CBDC initiatives across major economies, including the digital yuan, digital euro, and potential digital dollar. Key implications include enhanced monetary policy transmission, improved financial inclusion, and challenges to commercial banking models. Technical considerations encompass blockchain architecture, privacy frameworks, and interoperability standards. Geopolitical implications include potential impacts on dollar dominance and cross-border payment systems. Financial institutions must prepare for a digital currency landscape while addressing cybersecurity and operational risks.',
 'fixed_income', 'monetary_policy', 'global', 'high',
 'David Kim', 'Macro Research',
 '2024-03-08 11:15:00', '2024-03-08 11:15:00', CURRENT_TIMESTAMP(),
 'research_report', 'cbdc_global_analysis_2024.pdf', 38, 178, 94, 4.1,
 ARRAY_CONSTRUCT('CBDC', 'digital_currency', 'central_banks', 'blockchain'));

-- Sample Trading Insights
INSERT INTO trading_insights VALUES
('TI_2024_001', 'Tech Momentum Strategy: Riding the AI Wave',
 'Current market conditions present compelling opportunities in AI-focused technology stocks. Technical analysis indicates strong momentum in semiconductor, cloud computing, and AI software sectors. Recommended positioning includes long positions in NVIDIA, Microsoft, and emerging AI pure-plays. Risk management through sector diversification and volatility-adjusted position sizing. Target 15-20% returns over 3-6 month horizon with maximum 8% drawdown tolerance. Key catalysts include Q1 earnings beats, increased AI spending guidance, and regulatory clarity on AI governance.',
 'equity', 'NVDA', 'NASDAQ', 'momentum',
 'medium', 18.5, 8.0, 'medium_term',
 'Alex Thompson', 'Technology Desk',
 '2024-03-20 16:45:00', '2024-03-21 09:30:00', '2024-06-21 16:00:00', CURRENT_TIMESTAMP(),
 85.2, 16.3, 1.85,
 'trading_insight', 'high', 24, 8, 5),

('TI_2024_002', 'USD/JPY Carry Trade Opportunity',
 'Interest rate differential between USD and JPY creates attractive carry trade opportunities. Fed hawkish stance versus BOJ dovish policy maintains favorable yield spread. Technical setup shows USD/JPY breaking above 150 resistance with momentum indicators confirming uptrend. Recommended strategy: long USD/JPY with 2% position size, stop loss at 148.50, target 155.00. Risk factors include BOJ intervention and global risk-off sentiment. Monitor correlation with US 10-year yields and VIX levels for early warning signals.',
 'fx', 'USDJPY', 'FX_GLOBAL', 'carry_trade',
 'medium', 12.8, 5.5, 'short_term',
 'Yuki Tanaka', 'FX Desk',
 '2024-03-19 08:30:00', '2024-03-20 07:00:00', '2024-05-20 17:00:00', CURRENT_TIMESTAMP(),
 72.4, 11.9, 1.62,
 'trading_insight', 'medium', 18, 12, 7);

-- Sample Economic Indicators
INSERT INTO economic_indicators VALUES
('EI_2024_001', 'US CPI Data Shows Persistent Core Inflation',
 'The latest US Consumer Price Index data reveals headline inflation declining to 3.2% year-over-year, while core CPI remains elevated at 3.8%. Services inflation continues to show persistence, particularly in housing and healthcare sectors. The Federal Reserve faces continued challenges in bringing inflation to the 2% target. Market implications include potential for extended higher interest rates, pressure on consumer discretionary spending, and sector rotation away from interest-sensitive equities. Bond markets are pricing in sustained Fed hawkishness through 2024.',
 'CPI', 'US', 'monthly', 'Bureau of Labor Statistics',
 3.2, 3.4, 3.1, -5.9,
 'high', 'negative', ARRAY_CONSTRUCT('consumer_discretionary', 'real_estate', 'utilities'),
 '2024-03-12 08:30:00', '2024-02-29 00:00:00', '2024-04-10 08:30:00', CURRENT_TIMESTAMP(),
 'economic_indicator', 'high', 89, 4.6),

('EI_2024_003', 'ECB Policy Decision: Rates Held Steady Amid Growth Concerns',
 'The European Central Bank maintained interest rates at 4.0% as expected, citing balanced risks between inflation persistence and economic growth concerns. President Lagarde emphasized data-dependent approach for future decisions. Eurozone growth remains subdued with particular weakness in manufacturing sectors. The ECB upgraded inflation forecasts slightly but maintained commitment to bringing inflation to 2% target. Market reaction includes EUR weakness against USD and flattening of yield curves. Banking sector faces continued pressure from potential credit losses amid economic slowdown.',
 'policy_rate', 'EU', 'monthly', 'European Central Bank',
 4.0, 4.0, 4.0, 0.0,
 'medium', 'neutral', ARRAY_CONSTRUCT('financials', 'real_estate', 'industrials'),
 '2024-03-14 13:45:00', '2024-03-14 00:00:00', '2024-04-11 13:45:00', CURRENT_TIMESTAMP(),
 'economic_indicator', 'medium', 67, 4.1);

-- =============================================
-- 9. VERIFICATION AND SUMMARY
-- =============================================

-- Display table creation summary
SELECT 
    'Tables Created Successfully' AS status,
    COUNT(*) AS total_tables
FROM information_schema.tables 
WHERE table_schema = 'MARKET_INTELLIGENCE'
    AND table_type = 'BASE TABLE';

-- Show sample data counts
SELECT 
    'market_research_reports' AS table_name,
    COUNT(*) AS row_count
FROM market_research_reports
UNION ALL
SELECT 
    'trading_insights' AS table_name,
    COUNT(*) AS row_count
FROM trading_insights
UNION ALL
SELECT 
    'economic_indicators' AS table_name,
    COUNT(*) AS row_count
FROM economic_indicators;

-- =============================================
-- NOTES
-- =============================================
/*
TABLES CREATED:
1. market_research_reports - Store equity research, sector analysis, market commentary
2. trading_insights - Store trade ideas, technical analysis, strategy recommendations  
3. economic_indicators - Store economic data releases, policy decisions, macro analysis
4. document_processing_log - Track document ingestion and processing status
5. search_analytics - Monitor Cortex Search usage and performance

NEXT STEPS:
1. Run script 03_create_search_services.sql to create Cortex Search services
2. Test the search services with sample queries
3. Load additional data using Python scripts or manual INSERT statements
4. Configure the Streamlit application to use these tables

SAMPLE DATA:
- 3 market research reports covering AI, ESG, and CBDCs
- 2 trading insights for tech momentum and FX carry trade
- 2 economic indicators covering US CPI and ECB policy
*/ 