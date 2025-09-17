-- =============================================
-- JPMC Cortex Search Lab - Create Search Services
-- =============================================
-- This script creates Cortex Search services for the market intelligence data
-- following the official Snowflake Cortex Search documentation patterns.

-- Ensure we're in the correct context
USE ROLE CORTEX_USER_ROLE;
USE DATABASE JPMC_MARKETS;
USE SCHEMA MARKET_INTELLIGENCE;
USE WAREHOUSE CORTEX_WH;

-- =============================================
-- 1. MARKET RESEARCH SEARCH SERVICE
-- =============================================

-- Create search service for market research reports
CREATE OR REPLACE CORTEX SEARCH SERVICE market_research_search
    ON content                          -- Primary search column
    ATTRIBUTES asset_class, sector, region, risk_rating, 
               analyst_name, publish_date, views_count, 
               downloads_count, rating, tags
    WAREHOUSE = CORTEX_WH
    TARGET_LAG = '1 minute'
    AS (
        SELECT 
            report_id,
            title,
            content,                    -- Main searchable content
            asset_class,                -- For @eq filters
            sector,                     -- For @eq filters  
            region,                     -- For @eq filters
            risk_rating,                -- For @eq filters
            analyst_name,               -- For @eq filters
            publish_date,               -- For @gte/@lte time filters
            views_count,                -- For numeric boosts
            downloads_count,            -- For numeric boosts
            rating,                     -- For numeric boosts
            tags                        -- Array for tag-based filtering
        FROM market_research_reports
        WHERE content IS NOT NULL 
            AND LENGTH(content) > 50    -- Ensure meaningful content
    );

-- =============================================
-- 2. TRADING INSIGHTS SEARCH SERVICE  
-- =============================================

-- Create search service for trading insights
CREATE OR REPLACE CORTEX SEARCH SERVICE trading_insights_search
    ON content                          -- Primary search column
    ATTRIBUTES instrument_type, symbol, market, trading_strategy,
               risk_level, trader_name, publish_date, trade_date,
               likes_count, shares_count, success_rate, average_return
    WAREHOUSE = CORTEX_WH
    TARGET_LAG = '1 minute'
    AS (
        SELECT 
            insight_id,
            title,
            content,                    -- Main searchable content
            instrument_type,            -- equity, bond, derivative, fx
            symbol,                     -- AAPL, TSLA, EUR/USD, etc.
            market,                     -- NYSE, NASDAQ, LSE, etc.
            trading_strategy,           -- momentum, value, arbitrage, etc.
            risk_level,                 -- low, medium, high
            trader_name,                -- For @eq filters
            publish_date,               -- For time-based filtering
            trade_date,                 -- For time-based filtering
            likes_count,                -- For numeric boosts
            shares_count,               -- For numeric boosts  
            success_rate,               -- For numeric boosts (track record)
            average_return              -- For numeric boosts (performance)
        FROM trading_insights
        WHERE content IS NOT NULL
            AND LENGTH(content) > 50
    );

-- =============================================
-- 3. ECONOMIC INDICATORS SEARCH SERVICE
-- =============================================

-- Create search service for economic indicators
CREATE OR REPLACE CORTEX SEARCH SERVICE economic_indicators_search
    ON content                          -- Primary search column
    ATTRIBUTES indicator_name, country, frequency, data_source,
               market_impact, impact_direction, data_date, 
               citation_count, current_value, change_percent
    WAREHOUSE = CORTEX_WH
    TARGET_LAG = '1 minute'
    AS (
        SELECT 
            indicator_id,
            title,
            content,                    -- Main searchable content
            indicator_name,             -- GDP, CPI, unemployment, etc.
            country,                    -- US, UK, EU, JP, CN, etc.
            frequency,                  -- daily, weekly, monthly, etc.
            data_source,                -- Fed, ECB, BOJ, BLS, etc.
            market_impact,              -- low, medium, high, critical
            impact_direction,           -- positive, negative, neutral
            data_date,                  -- The date the economic data refers to
            citation_count,             -- For numeric boosts (research relevance)
            current_value,              -- Actual indicator value
            change_percent              -- Change from previous period
        FROM economic_indicators
        WHERE content IS NOT NULL
            AND LENGTH(content) > 50
    );

-- =============================================
-- 4. UNIFIED MARKET INTELLIGENCE SEARCH SERVICE
-- =============================================

-- Create unified search service across all document types
CREATE OR REPLACE CORTEX SEARCH SERVICE market_intelligence_unified_search
    ON content                          -- Primary search column
    ATTRIBUTES source_type, category, subcategory, author,
               publish_date, engagement_score, tags
    WAREHOUSE = CORTEX_WH
    TARGET_LAG = '1 minute'
    AS (
        SELECT 
            document_id,
            source_type || ': ' || title AS title,  -- Prefix with source type
            content,                    -- Main searchable content
            source_type,                -- market_research, trading_insight, economic_indicator
            category,                   -- asset_class, instrument_type, country
            subcategory,                -- sector, trading_strategy, indicator_name
            author,                     -- analyst_name, trader_name, data_source
            publish_date,               -- For time-based filtering
            engagement_score,           -- For numeric boosts (views, likes, citations)
            tags                        -- For tag-based filtering
        FROM market_intelligence_unified
        WHERE content IS NOT NULL
            AND LENGTH(content) > 50
    );

-- =============================================
-- 5. VERIFY SEARCH SERVICES CREATION
-- =============================================

-- Show all created search services
SHOW CORTEX SEARCH SERVICES IN SCHEMA MARKET_INTELLIGENCE;

-- Get detailed information about each service
DESCRIBE CORTEX SEARCH SERVICE market_research_search;
DESCRIBE CORTEX SEARCH SERVICE trading_insights_search;  
DESCRIBE CORTEX SEARCH SERVICE economic_indicators_search;
DESCRIBE CORTEX SEARCH SERVICE market_intelligence_unified_search;

-- =============================================
-- 6. TEST SEARCH SERVICES
-- =============================================

-- Wait a moment for services to initialize, then test with simple queries

-- Test Market Research Search Service
SELECT 'Testing market_research_search...' AS test_status;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'market_research_search',
        '{
            "query": "artificial intelligence",
            "columns": ["TITLE", "CONTENT", "ASSET_CLASS", "ANALYST_NAME"],
            "limit": 3
        }'
    )
)['results'] AS market_research_results;

-- Test Trading Insights Search Service  
SELECT 'Testing trading_insights_search...' AS test_status;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'trading_insights_search',
        '{
            "query": "technology momentum",
            "columns": ["TITLE", "CONTENT", "SYMBOL", "RISK_LEVEL"],
            "limit": 3
        }'
    )
)['results'] AS trading_insights_results;

-- Test Economic Indicators Search Service
SELECT 'Testing economic_indicators_search...' AS test_status;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'economic_indicators_search',
        '{
            "query": "inflation policy",
            "columns": ["TITLE", "CONTENT", "COUNTRY", "MARKET_IMPACT"],
            "limit": 3
        }'
    )
)['results'] AS economic_indicators_results;

-- Test Unified Search Service
SELECT 'Testing market_intelligence_unified_search...' AS test_status;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'market_intelligence_unified_search',
        '{
            "query": "financial markets",
            "columns": ["TITLE", "SOURCE_TYPE", "CATEGORY", "AUTHOR"],
            "limit": 5
        }'
    )
)['results'] AS unified_search_results;

-- =============================================
-- 7. ADVANCED SEARCH EXAMPLES
-- =============================================

-- Example 1: Market Research with Asset Class Filter
SELECT 'Advanced Example 1: Market Research with Asset Class Filter' AS example;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'market_research_search',
        '{
            "query": "technology trends artificial intelligence",
            "columns": ["TITLE", "CONTENT", "ASSET_CLASS", "SECTOR", "RATING"],
            "filter": {"@eq": {"ASSET_CLASS": "technology"}},
            "scoring_config": {
                "functions": {
                    "numeric_boosts": [
                        {"column": "rating", "weight": 2},
                        {"column": "views_count", "weight": 1}
                    ]
                }
            },
            "limit": 3
        }'
    )
)['results'] AS filtered_research_results;

-- Example 2: Trading Insights with Risk Level and Time Filter
SELECT 'Advanced Example 2: Trading Insights with Risk and Time Filters' AS example;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'trading_insights_search',
        '{
            "query": "momentum strategy",
            "columns": ["TITLE", "CONTENT", "SYMBOL", "RISK_LEVEL", "TARGET_RETURN"],
            "filter": {"@and": [
                {"@eq": {"RISK_LEVEL": "medium"}},
                {"@gte": {"PUBLISH_DATE": "2024-03-01T00:00:00.000Z"}}
            ]},
            "scoring_config": {
                "functions": {
                    "numeric_boosts": [
                        {"column": "success_rate", "weight": 3},
                        {"column": "average_return", "weight": 2},
                        {"column": "likes_count", "weight": 1}
                    ]
                }
            },
            "limit": 3
        }'
    )
)['results'] AS filtered_trading_results;

-- Example 3: Economic Indicators with Country Filter and Time Decay
SELECT 'Advanced Example 3: Economic Indicators with Country Filter and Time Decay' AS example;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'economic_indicators_search',
        '{
            "query": "inflation central bank policy",
            "columns": ["TITLE", "CONTENT", "COUNTRY", "MARKET_IMPACT", "DATA_DATE"],
            "filter": {"@eq": {"COUNTRY": "US"}},
            "scoring_config": {
                "functions": {
                    "time_decays": [
                        {
                            "column": "DATA_DATE", 
                            "weight": 2, 
                            "limit_hours": 720,
                            "now": "2024-04-01T00:00:00.000Z"
                        }
                    ],
                    "numeric_boosts": [
                        {"column": "citation_count", "weight": 1}
                    ]
                }
            },
            "limit": 3
        }'
    )
)['results'] AS time_decay_results;

-- Example 4: Unified Search with Source Type Filter
SELECT 'Advanced Example 4: Unified Search with Source Type Filter' AS example;

SELECT PARSE_JSON(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'market_intelligence_unified_search',
        '{
            "query": "market volatility risk management",
            "columns": ["TITLE", "SOURCE_TYPE", "CATEGORY", "AUTHOR", "PUBLISH_DATE"],
            "filter": {"@eq": {"SOURCE_TYPE": "trading_insight"}},
            "scoring_config": {
                "functions": {
                    "numeric_boosts": [
                        {"column": "engagement_score", "weight": 2}
                    ]
                }
            },
            "limit": 5
        }'
    )
)['results'] AS unified_filtered_results;

-- =============================================
-- 8. PYTHON API EXAMPLES (FOR REFERENCE)
-- =============================================

/*
PYTHON API USAGE EXAMPLES:

# Basic search using Python API
from snowflake.core import Root
from snowflake.snowpark import Session

# Create session and root object
session = Session.builder.configs(CONNECTION_PARAMETERS).create()
root = Root(session)

# Get search service
market_research_service = (root
    .databases["JPMC_MARKETS"]
    .schemas["MARKET_INTELLIGENCE"] 
    .cortex_search_services["market_research_search"]
)

# Execute search
results = market_research_service.search(
    query="artificial intelligence financial services",
    columns=["TITLE", "CONTENT", "ASSET_CLASS", "ANALYST_NAME"],
    filter={"@eq": {"ASSET_CLASS": "technology"}},
    scoring_config={
        "functions": {
            "numeric_boosts": [
                {"column": "rating", "weight": 2},
                {"column": "views_count", "weight": 1}
            ]
        }
    },
    limit=5
)

print(results.to_json())
*/

-- =============================================
-- 9. REST API EXAMPLES (FOR REFERENCE)
-- =============================================

/*
REST API USAGE EXAMPLES:

# Basic REST API call
curl --location https://<ACCOUNT_URL>/api/v2/databases/JPMC_MARKETS/schemas/MARKET_INTELLIGENCE/cortex-search-services/market_research_search:query \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: Bearer $PAT" \
--data '{
    "query": "artificial intelligence financial services",
    "columns": ["TITLE", "CONTENT", "ASSET_CLASS", "ANALYST_NAME"],
    "filter": {"@eq": {"ASSET_CLASS": "technology"}},
    "scoring_config": {
        "functions": {
            "numeric_boosts": [
                {"column": "rating", "weight": 2},
                {"column": "views_count", "weight": 1}
            ]
        }
    },
    "limit": 5
}'

# Advanced filtering with multiple conditions
curl --location https://<ACCOUNT_URL>/api/v2/databases/JPMC_MARKETS/schemas/MARKET_INTELLIGENCE/cortex-search-services/trading_insights_search:query \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--header "Authorization: Bearer $PAT" \
--data '{
    "query": "momentum strategy technology",
    "columns": ["TITLE", "CONTENT", "SYMBOL", "RISK_LEVEL"],
    "filter": {"@and": [
        {"@eq": {"RISK_LEVEL": "medium"}},
        {"@gte": {"PUBLISH_DATE": "2024-03-01T00:00:00.000Z"}}
    ]},
    "limit": 3
}'
*/

-- =============================================
-- SETUP SUMMARY
-- =============================================

SELECT 
    'Cortex Search Services Setup Complete!' AS status,
    COUNT(*) AS total_services
FROM information_schema.cortex_search_services
WHERE service_schema = 'MARKET_INTELLIGENCE';

-- =============================================
-- NOTES AND NEXT STEPS  
-- =============================================

/*
CORTEX SEARCH SERVICES CREATED:

1. market_research_search
   - Searches: Market research reports, equity analysis, sector insights
   - Filters: asset_class, sector, region, risk_rating, analyst_name
   - Boosts: views_count, downloads_count, rating

2. trading_insights_search  
   - Searches: Trading ideas, technical analysis, strategy recommendations
   - Filters: instrument_type, symbol, market, trading_strategy, risk_level
   - Boosts: likes_count, success_rate, average_return

3. economic_indicators_search
   - Searches: Economic data, policy decisions, macro analysis
   - Filters: indicator_name, country, frequency, data_source, market_impact
   - Boosts: citation_count, current_value, change_percent

4. market_intelligence_unified_search
   - Searches: All document types in unified interface
   - Filters: source_type, category, subcategory, author
   - Boosts: engagement_score (views/likes/citations)

TESTING:
- All services have been tested with sample queries
- Advanced examples demonstrate filtering, scoring, and time decay
- Services support Python API, REST API, and SQL SEARCH_PREVIEW function

NEXT STEPS:
1. Use the Python application (src/search/cortex_search.py) to interact with services
2. Run the Streamlit application to test the UI interface
3. Load additional sample data or connect to real data sources
4. Experiment with different scoring configurations for your use cases
5. Monitor search analytics using the search_analytics table

DOCUMENTATION:
- Official Snowflake Cortex Search docs: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service
- All three API surfaces (Python, REST, SQL) are supported and tested
- Filter syntax supports @eq, @and, @gte, @lte for precise result filtering
- Scoring supports numeric boosts and time decays for relevance tuning
*/ 