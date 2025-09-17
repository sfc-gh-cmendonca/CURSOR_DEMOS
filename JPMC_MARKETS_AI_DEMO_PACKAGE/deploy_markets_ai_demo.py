#!/usr/bin/env python3
"""
JPMC Markets AI Demo Deployment Script
=====================================

This script deploys Demo Scenarios 1 & 2 for Equity Research Analysts:
1. Earnings Analysis - Accelerating earnings season analysis
2. Thematic Research - Discovering investment themes from unstructured data

Features:
- Connects using Snowflake connections.toml file
- Creates MARKETS_AI_DEMO database with tech sector focus
- Integrates Snowflake Marketplace "Finance & Economics" dataset
- Generates synthetic data with dynamic dates for realistic demos
- Sets up Cortex Analyst semantic views and Cortex Search services
- Includes SNOW (Snowflake Inc.) and major tech companies

Author: JPMC Markets Team
Date: September 2025
"""

import os
import sys
import logging
import toml
from datetime import datetime, timedelta
from pathlib import Path
import snowflake.connector
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('markets_ai_demo_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MarketsAIDemoDeployment:
    """Main deployment class for Markets AI Demo scenarios."""
    
    def __init__(self, connection_name: str = "default"):
        """Initialize deployment with Snowflake connection."""
        self.connection_name = connection_name
        self.conn = None
        self.cursor = None
        
        # Tech sector companies including SNOW
        self.tech_companies = [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corporation"), 
            ("GOOGL", "Alphabet Inc."),
            ("NVDA", "NVIDIA Corporation"),
            ("TSLA", "Tesla Inc."),
            ("META", "Meta Platforms Inc."),
            ("SNOW", "Snowflake Inc."),
            ("CRM", "Salesforce Inc."),
            ("ORCL", "Oracle Corporation"),
            ("AMD", "Advanced Micro Devices Inc.")
        ]
        
        # Calculate dynamic dates for realistic demo
        self.current_date = datetime.now()
        self.quarters = self._get_historical_quarters(8)  # 8 quarters = 2 years
        self.date_range = self._get_dynamic_date_range()
        
    def _get_historical_quarters(self, num_quarters: int) -> List[Tuple[str, datetime, datetime]]:
        """Generate historical quarters with dynamic dates."""
        quarters = []
        current_quarter_start = self._get_quarter_start(self.current_date)
        
        for i in range(num_quarters):
            quarter_start = current_quarter_start - timedelta(days=90 * i)
            quarter_start = self._get_quarter_start(quarter_start)
            quarter_end = self._get_quarter_end(quarter_start)
            quarter_label = f"{quarter_start.year}Q{((quarter_start.month - 1) // 3) + 1}"
            quarters.append((quarter_label, quarter_start, quarter_end))
            
        return quarters[::-1]  # Reverse to chronological order
    
    def _get_quarter_start(self, date: datetime) -> datetime:
        """Get the start of the quarter for a given date."""
        quarter = ((date.month - 1) // 3) + 1
        start_month = (quarter - 1) * 3 + 1
        return datetime(date.year, start_month, 1)
    
    def _get_quarter_end(self, quarter_start: datetime) -> datetime:
        """Get the end of the quarter."""
        if quarter_start.month == 10:  # Q4
            return datetime(quarter_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            return datetime(quarter_start.year, quarter_start.month + 3, 1) - timedelta(days=1)
    
    def _get_dynamic_date_range(self) -> Tuple[datetime, datetime]:
        """Get date range spanning the generated quarters."""
        start_date = self.quarters[0][1]  # First quarter start
        end_date = self.quarters[-1][2]   # Last quarter end
        return start_date, end_date
    
    def _load_connection_config(self) -> Dict:
        """Load connection configuration from connections.toml file."""
        # Common paths for connections.toml
        possible_paths = [
            Path.home() / ".config" / "snowflake" / "connections.toml",  # Linux
            Path.home() / "Library" / "Application Support" / "snowflake" / "connections.toml",  # macOS
            Path.home() / "AppData" / "Local" / "snowflake" / "connections.toml",  # Windows
            Path("connections.toml"),  # Current directory
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if not config_path:
            raise FileNotFoundError(
                "connections.toml not found. Please ensure it exists in one of these locations:\n"
                + "\n".join(str(p) for p in possible_paths)
            )
        
        logger.info(f"Loading connection config from: {config_path}")
        config = toml.load(config_path)
        
        if self.connection_name not in config:
            raise KeyError(f"Connection '{self.connection_name}' not found in {config_path}")
        
        return config[self.connection_name]
    
    def connect(self) -> None:
        """Establish connection to Snowflake using TOML configuration."""
        try:
            config = self._load_connection_config()
            
            # Map TOML keys to snowflake-connector-python parameters
            connection_params = {
                'account': config.get('account'),
                'user': config.get('user'),
                'password': config.get('password'),
                'warehouse': config.get('warehouse'),
                'database': config.get('database'),
                'schema': config.get('schema'),
                'role': config.get('role')
            }
            
            # Remove None values
            connection_params = {k: v for k, v in connection_params.items() if v is not None}
            
            logger.info(f"Connecting to Snowflake account: {connection_params['account']}")
            self.conn = snowflake.connector.connect(**connection_params)
            self.cursor = self.conn.cursor()
            
            logger.info("✅ Successfully connected to Snowflake!")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            raise
    
    def execute_sql(self, sql: str, description: str = "") -> List:
        """Execute SQL with error handling and logging."""
        try:
            if description:
                logger.info(f"🔄 {description}")
            
            logger.debug(f"Executing SQL: {sql[:100]}...")
            result = self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            
            if description:
                logger.info(f"✅ {description} - Success")
            
            return rows
            
        except Exception as e:
            logger.error(f"❌ SQL Error in {description}: {e}")
            logger.error(f"SQL: {sql}")
            raise
    
    def create_database_structure(self) -> None:
        """Create the MARKETS_AI_DEMO database and schema structure."""
        logger.info("🏗️  Creating database structure...")
        
        # Create database
        self.execute_sql(
            "CREATE DATABASE IF NOT EXISTS MARKETS_AI_DEMO",
            "Creating MARKETS_AI_DEMO database"
        )
        
        # Create schemas
        schemas = ['RAW_DATA', 'ENRICHED_DATA', 'ANALYTICS', 'SEARCH_SERVICES']
        for schema in schemas:
            self.execute_sql(
                f"CREATE SCHEMA IF NOT EXISTS MARKETS_AI_DEMO.{schema}",
                f"Creating {schema} schema"
            )
        
        # Use the database
        self.execute_sql("USE DATABASE MARKETS_AI_DEMO")
        
        logger.info("✅ Database structure created successfully!")
    
    def create_tables(self) -> None:
        """Create all required tables for the demo scenarios."""
        logger.info("📊 Creating demo tables...")
        
        # Switch to RAW_DATA schema
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Companies table
        companies_sql = """
        CREATE OR REPLACE TABLE companies (
            ticker VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(200) NOT NULL,
            sector VARCHAR(100) NOT NULL,
            industry VARCHAR(200),
            market_cap_billions DECIMAL(15,2),
            headquarters VARCHAR(100),
            founded_year INTEGER,
            employee_count INTEGER,
            business_description TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(companies_sql, "Creating companies table")
        
        # Stock prices table
        stock_prices_sql = """
        CREATE OR REPLACE TABLE stock_prices (
            ticker VARCHAR(10),
            price_date DATE,
            open_price DECIMAL(10,2),
            high_price DECIMAL(10,2),
            low_price DECIMAL(10,2),
            close_price DECIMAL(10,2),
            volume BIGINT,
            adjusted_close DECIMAL(10,2),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (ticker, price_date)
        )
        """
        self.execute_sql(stock_prices_sql, "Creating stock_prices table")
        
        # Earnings data table
        earnings_sql = """
        CREATE OR REPLACE TABLE earnings_data (
            ticker VARCHAR(10),
            quarter VARCHAR(10),
            earnings_date DATE,
            fiscal_quarter INTEGER,
            fiscal_year INTEGER,
            revenue_millions DECIMAL(15,2),
            net_income_millions DECIMAL(15,2),
            earnings_per_share DECIMAL(10,4),
            diluted_shares_millions DECIMAL(15,2),
            gross_margin_percent DECIMAL(5,2),
            operating_margin_percent DECIMAL(5,2),
            guidance_revenue_low DECIMAL(15,2),
            guidance_revenue_high DECIMAL(15,2),
            guidance_eps_low DECIMAL(10,4),
            guidance_eps_high DECIMAL(10,4),
            analyst_est_revenue DECIMAL(15,2),
            analyst_est_eps DECIMAL(10,4),
            revenue_surprise_percent DECIMAL(5,2),
            eps_surprise_percent DECIMAL(5,2),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (ticker, quarter)
        )
        """
        self.execute_sql(earnings_sql, "Creating earnings_data table")
        
        # Research reports table for thematic research
        research_reports_sql = """
        CREATE OR REPLACE TABLE research_reports (
            report_id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            author VARCHAR(200),
            firm VARCHAR(200),
            publish_date DATE,
            report_type VARCHAR(100),
            sector VARCHAR(100),
            tickers_covered ARRAY,
            theme VARCHAR(200),
            investment_thesis TEXT,
            key_risks TEXT,
            price_target DECIMAL(10,2),
            rating VARCHAR(50),
            report_summary TEXT,
            full_content TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(research_reports_sql, "Creating research_reports table")
        
        # Market events table
        market_events_sql = """
        CREATE OR REPLACE TABLE market_events (
            event_id VARCHAR(50) PRIMARY KEY,
            event_date DATE,
            event_type VARCHAR(100),
            title VARCHAR(500),
            description TEXT,
            impact_level VARCHAR(20),
            affected_sectors ARRAY,
            affected_tickers ARRAY,
            market_reaction_summary TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(market_events_sql, "Creating market_events table")
        
        logger.info("✅ All tables created successfully!")
    
    def load_company_data(self) -> None:
        """Load tech sector company data."""
        logger.info("👥 Loading company data...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Company data with realistic information
        company_data = [
            ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics", 3000.0, "Cupertino, CA", 1976, 164000, "Apple designs and manufactures consumer electronics, software, and online services."),
            ("MSFT", "Microsoft Corporation", "Technology", "Software", 2800.0, "Redmond, WA", 1975, 221000, "Microsoft develops computer software, consumer electronics, and personal computers."),
            ("GOOGL", "Alphabet Inc.", "Technology", "Internet Services", 1700.0, "Mountain View, CA", 1998, 182000, "Alphabet operates as a holding company with Google as its primary subsidiary."),
            ("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors", 1100.0, "Santa Clara, CA", 1993, 29600, "NVIDIA designs graphics processing units and system-on-chip products."),
            ("TSLA", "Tesla Inc.", "Technology", "Electric Vehicles", 800.0, "Austin, TX", 2003, 140473, "Tesla designs, develops, and manufactures electric vehicles and energy storage systems."),
            ("META", "Meta Platforms Inc.", "Technology", "Social Media", 750.0, "Menlo Park, CA", 2004, 86482, "Meta operates social networking platforms and develops virtual reality technologies."),
            ("SNOW", "Snowflake Inc.", "Technology", "Cloud Computing", 65.0, "Bozeman, MT", 2012, 6800, "Snowflake provides cloud-based data warehousing and analytics services."),
            ("CRM", "Salesforce Inc.", "Technology", "Cloud Software", 250.0, "San Francisco, CA", 1999, 79000, "Salesforce provides customer relationship management software and cloud computing services."),
            ("ORCL", "Oracle Corporation", "Technology", "Database Software", 320.0, "Austin, TX", 1977, 164000, "Oracle develops database software and cloud computing technologies."),
            ("AMD", "Advanced Micro Devices Inc.", "Technology", "Semiconductors", 230.0, "Santa Clara, CA", 1969, 26000, "AMD designs microprocessors and graphics processing units for servers and PCs.")
        ]
        
        for ticker, name, sector, industry, market_cap, hq, founded, employees, description in company_data:
            insert_sql = f"""
            INSERT INTO companies (ticker, company_name, sector, industry, market_cap_billions, 
                                 headquarters, founded_year, employee_count, business_description)
            VALUES ('{ticker}', '{name}', '{sector}', '{industry}', {market_cap}, 
                   '{hq}', {founded}, {employees}, '{description}')
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Company data loaded successfully!")
    
    def generate_earnings_data(self) -> None:
        """Generate realistic earnings data with dynamic dates."""
        logger.info("📈 Generating earnings data...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        import random
        
        # Base financial metrics for each company (realistic starting points)
        base_metrics = {
            "AAPL": {"revenue": 95000, "net_income": 22000, "shares": 15500},
            "MSFT": {"revenue": 52000, "net_income": 16000, "shares": 7400},
            "GOOGL": {"revenue": 70000, "net_income": 15000, "shares": 6200},
            "NVDA": {"revenue": 15000, "net_income": 4500, "shares": 2400},
            "TSLA": {"revenue": 25000, "net_income": 2000, "shares": 3100},
            "META": {"revenue": 32000, "net_income": 8500, "shares": 2600},
            "SNOW": {"revenue": 600, "net_income": -200, "shares": 350},  # Growth stage
            "CRM": {"revenue": 8000, "net_income": 200, "shares": 1000},
            "ORCL": {"revenue": 12000, "net_income": 3500, "shares": 2700},
            "AMD": {"revenue": 6000, "net_income": 800, "shares": 1600}
        }
        
        for ticker, _, in self.tech_companies[:7]:  # Focus on top 7 for detailed data
            if ticker not in base_metrics:
                continue
                
            base = base_metrics[ticker]
            
            for i, (quarter, start_date, end_date) in enumerate(self.quarters):
                # Calculate earnings date (typically ~45 days after quarter end)
                earnings_date = end_date + timedelta(days=random.randint(20, 50))
                
                # Add growth trend and seasonality
                growth_rate = random.uniform(0.95, 1.25) if ticker != "SNOW" else random.uniform(1.2, 1.8)
                seasonal_factor = 1 + 0.1 * random.uniform(-1, 1)
                
                revenue = base["revenue"] * growth_rate * seasonal_factor * (1 + i * 0.05)
                net_income = base["net_income"] * growth_rate * seasonal_factor * (1 + i * 0.03)
                shares = base["shares"] * (1 + i * 0.01)  # Slight dilution over time
                
                eps = net_income / shares
                
                # Calculate margins
                gross_margin = random.uniform(35, 65) if ticker != "SNOW" else random.uniform(70, 85)
                operating_margin = (net_income / revenue) * 100 * random.uniform(0.8, 1.2)
                
                # Analyst estimates (with some variation)
                analyst_revenue = revenue * random.uniform(0.95, 1.05)
                analyst_eps = eps * random.uniform(0.9, 1.1)
                
                # Surprises
                revenue_surprise = ((revenue - analyst_revenue) / analyst_revenue) * 100
                eps_surprise = ((eps - analyst_eps) / analyst_eps) * 100
                
                # Guidance (next quarter)
                guidance_rev_low = revenue * random.uniform(1.0, 1.15)
                guidance_rev_high = guidance_rev_low * random.uniform(1.05, 1.15)
                guidance_eps_low = eps * random.uniform(1.0, 1.2)
                guidance_eps_high = guidance_eps_low * random.uniform(1.05, 1.2)
                
                fiscal_quarter = ((start_date.month - 1) // 3) + 1
                fiscal_year = start_date.year
                
                insert_sql = f"""
                INSERT INTO earnings_data VALUES (
                    '{ticker}', '{quarter}', '{earnings_date.strftime('%Y-%m-%d')}',
                    {fiscal_quarter}, {fiscal_year}, {revenue:.2f}, {net_income:.2f}, {eps:.4f},
                    {shares:.2f}, {gross_margin:.2f}, {operating_margin:.2f},
                    {guidance_rev_low:.2f}, {guidance_rev_high:.2f}, 
                    {guidance_eps_low:.4f}, {guidance_eps_high:.4f},
                    {analyst_revenue:.2f}, {analyst_eps:.4f},
                    {revenue_surprise:.2f}, {eps_surprise:.2f}, CURRENT_TIMESTAMP()
                )
                """
                self.execute_sql(insert_sql)
        
        logger.info("✅ Earnings data generated successfully!")
    
    def generate_market_events(self) -> None:
        """Generate major market events that affect tech sector."""
        logger.info("📰 Generating market events...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Major market events affecting tech sector
        start_date, end_date = self.date_range
        
        events = [
            {
                "id": "FED_RATE_HIKE_2024_Q1",
                "date": start_date + timedelta(days=45),
                "type": "Federal Reserve Decision",
                "title": "Fed Raises Interest Rates by 0.75%",
                "description": "Federal Reserve implements aggressive rate hike to combat inflation, impacting growth stocks particularly in technology sector.",
                "impact": "High",
                "sectors": ["Technology", "Growth"],
                "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "SNOW"]
            },
            {
                "id": "AI_BOOM_2024",
                "date": start_date + timedelta(days=120),
                "type": "Technology Trend",
                "title": "Generative AI Adoption Accelerates Across Enterprise",
                "description": "Major enterprise adoption of AI technologies drives significant revenue growth for cloud and AI-focused companies.",
                "impact": "High",
                "sectors": ["Technology", "AI", "Cloud"],
                "tickers": ["NVDA", "MSFT", "GOOGL", "SNOW", "CRM"]
            },
            {
                "id": "CHINA_TRADE_TENSIONS_2024",
                "date": start_date + timedelta(days=200),
                "type": "Geopolitical",
                "title": "US-China Trade Restrictions on Semiconductor Technology",
                "description": "New export controls on advanced semiconductor technology to China impact chip companies and their supply chains.",
                "impact": "Medium",
                "sectors": ["Technology", "Semiconductors"],
                "tickers": ["NVDA", "AMD", "AAPL"]
            },
            {
                "id": "CLOUD_COMPETITION_2024",
                "date": start_date + timedelta(days=280),
                "type": "Industry Competition",
                "title": "Intensifying Cloud Infrastructure Competition",
                "description": "Major cloud providers engage in pricing competition while new players enter specialized markets like data analytics.",
                "impact": "Medium",
                "sectors": ["Technology", "Cloud"],
                "tickers": ["MSFT", "GOOGL", "SNOW", "ORCL"]
            },
            {
                "id": "EV_MARKET_SHIFT_2024",
                "date": start_date + timedelta(days=350),
                "type": "Industry Disruption",
                "title": "Electric Vehicle Market Consolidation",
                "description": "Traditional automakers gain market share as EV market matures, affecting pure-play EV companies.",
                "impact": "High",
                "sectors": ["Technology", "Automotive"],
                "tickers": ["TSLA"]
            }
        ]
        
        for event in events:
            sectors_array = "ARRAY[" + ",".join(f"'{s}'" for s in event["sectors"]) + "]"
            tickers_array = "ARRAY[" + ",".join(f"'{t}'" for t in event["tickers"]) + "]"
            
            insert_sql = f"""
            INSERT INTO market_events VALUES (
                '{event["id"]}', '{event["date"].strftime('%Y-%m-%d')}',
                '{event["type"]}', '{event["title"]}', '{event["description"]}',
                '{event["impact"]}', {sectors_array}, {tickers_array},
                'Market showed {event["impact"].lower()} volatility in response to this event.',
                CURRENT_TIMESTAMP()
            )
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Market events generated successfully!")
    
    def generate_research_reports(self) -> None:
        """Generate realistic research reports for thematic research scenario."""
        logger.info("📄 Generating research reports...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Research themes and reports
        reports = [
            {
                "id": "RPT_AI_ENTERPRISE_2024_Q4",
                "title": "The Enterprise AI Revolution: Cloud Infrastructure Winners",
                "author": "Sarah Chen",
                "firm": "Tech Research Partners",
                "date": self.quarters[-2][2] + timedelta(days=10),
                "type": "Thematic Research",
                "sector": "Technology",
                "tickers": ["NVDA", "MSFT", "SNOW", "GOOGL"],
                "theme": "Artificial Intelligence",
                "thesis": "Enterprise AI adoption is accelerating rapidly, creating unprecedented demand for specialized infrastructure. Companies with proprietary AI capabilities and robust cloud platforms are positioned to capture disproportionate value.",
                "risks": "Regulatory scrutiny, competition from open-source alternatives, high capital requirements for AI infrastructure."
            },
            {
                "id": "RPT_CLOUD_DATA_2024_Q3",
                "title": "Data Cloud Transformation: Beyond Traditional Warehousing",
                "author": "Michael Rodriguez",
                "firm": "Financial Tech Insights",
                "date": self.quarters[-3][2] + timedelta(days=15),
                "type": "Sector Analysis",
                "sector": "Technology",
                "tickers": ["SNOW", "MSFT", "ORCL", "GOOGL"],
                "theme": "Data Analytics",
                "thesis": "Organizations are moving beyond traditional data warehousing to comprehensive data cloud platforms. Modern architecture enables real-time analytics and AI/ML workloads at scale.",
                "risks": "Intense competition, margin pressure from pricing wars, integration complexity."
            },
            {
                "id": "RPT_SNOWFLAKE_DEEP_2024",
                "title": "Snowflake: AI-Native Data Cloud Leadership",
                "author": "Jennifer Liu",
                "firm": "Growth Equity Research",
                "date": self.quarters[-1][2] + timedelta(days=5),
                "type": "Company Deep Dive",
                "sector": "Technology",
                "tickers": ["SNOW"],
                "theme": "Data Cloud Platform",
                "thesis": "Snowflake's architecture uniquely positions it for the AI era. Native support for unstructured data, vector databases, and ML workloads creates competitive moats in the evolving data landscape.",
                "risks": "Hyperscaler competition, customer concentration, execution on AI roadmap."
            }
        ]
        
        for report in reports:
            tickers_array = "ARRAY[" + ",".join(f"'{t}'" for t in report["tickers"]) + "]"
            
            # Generate realistic price target for primary ticker
            if report["tickers"][0] == "SNOW":
                price_target = 180.0
                rating = "Buy"
            elif report["tickers"][0] == "NVDA":
                price_target = 850.0
                rating = "Strong Buy"
            else:
                price_target = 200.0
                rating = "Buy"
            
            # Create detailed content
            full_content = f"""
            {report["title"]}
            
            Executive Summary:
            {report["thesis"]}
            
            Investment Thesis:
            Our analysis indicates strong fundamentals driving this theme, with particular strength in enterprise adoption rates and technological barriers to entry.
            
            Key Risks:
            {report["risks"]}
            
            Companies Covered:
            {', '.join(report["tickers"])}
            
            Recommendation: {rating}
            Price Target: ${price_target}
            """
            
            insert_sql = f"""
            INSERT INTO research_reports VALUES (
                '{report["id"]}', '{report["title"]}', '{report["author"]}', '{report["firm"]}',
                '{report["date"].strftime('%Y-%m-%d')}', '{report["type"]}', '{report["sector"]}',
                {tickers_array}, '{report["theme"]}', '{report["thesis"]}', '{report["risks"]}',
                {price_target}, '{rating}', 
                'Analysis of {report["theme"]} trends across technology sector',
                '{full_content.replace("'", "''")}', CURRENT_TIMESTAMP()
            )
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Research reports generated successfully!")
    
    def create_semantic_views(self) -> None:
        """Create Cortex Analyst semantic views for both scenarios."""
        logger.info("🧠 Creating Cortex Analyst semantic views...")
        
        self.execute_sql("USE SCHEMA ANALYTICS")
        
        # Earnings Analysis Semantic View
        earnings_semantic_sql = """
        CREATE OR REPLACE VIEW earnings_analysis_semantic AS
        SELECT 
            e.ticker,
            c.company_name,
            e.quarter,
            e.earnings_date,
            e.revenue_millions as revenue,
            e.net_income_millions as net_income,
            e.earnings_per_share as eps,
            e.revenue_surprise_percent,
            e.eps_surprise_percent,
            e.guidance_revenue_low,
            e.guidance_revenue_high,
            e.analyst_est_revenue,
            e.analyst_est_eps,
            c.sector,
            c.market_cap_billions
        FROM RAW_DATA.earnings_data e
        JOIN RAW_DATA.companies c ON e.ticker = c.ticker
        WHERE c.sector = 'Technology'
        """
        self.execute_sql(earnings_semantic_sql, "Creating earnings analysis semantic view")
        
        # Thematic Research Semantic View
        thematic_semantic_sql = """
        CREATE OR REPLACE VIEW thematic_research_semantic AS
        SELECT 
            r.report_id,
            r.title,
            r.author,
            r.firm,
            r.publish_date,
            r.theme,
            r.investment_thesis,
            r.rating,
            r.price_target,
            ARRAY_TO_STRING(r.tickers_covered, ', ') as companies_covered,
            r.sector
        FROM RAW_DATA.research_reports r
        WHERE r.sector = 'Technology'
        """
        self.execute_sql(thematic_semantic_sql, "Creating thematic research semantic view")
        
        logger.info("✅ Semantic views created successfully!")
    
    def setup_marketplace_integration(self) -> None:
        """Set up integration with Snowflake Marketplace Finance & Economics dataset."""
        logger.info("🏪 Setting up Snowflake Marketplace integration...")
        
        # Note: In a real deployment, this would reference the actual shared database
        # For demo purposes, we'll create a placeholder structure
        
        try:
            marketplace_setup_sql = """
            -- This would typically reference a shared database from Snowflake Marketplace
            -- Example: ECONOMICS_DATA_ATLAS or FINANCIAL_ECONOMIC_ESSENTIALS
            
            CREATE SCHEMA IF NOT EXISTS MARKETPLACE_DATA;
            
            -- Placeholder for marketplace economic indicators
            CREATE OR REPLACE VIEW MARKETPLACE_DATA.economic_indicators AS
            SELECT 
                'GDP_GROWTH' as indicator_name,
                CURRENT_DATE() - INTERVAL '30 days' as indicator_date,
                2.3 as indicator_value,
                'Quarterly GDP Growth Rate (%)' as description
            UNION ALL
            SELECT 
                'UNEMPLOYMENT_RATE',
                CURRENT_DATE() - INTERVAL '15 days',
                3.8,
                'Monthly Unemployment Rate (%)'
            UNION ALL
            SELECT 
                'FEDERAL_FUNDS_RATE',
                CURRENT_DATE() - INTERVAL '7 days',
                5.25,
                'Federal Funds Rate (%)'
            """
            
            self.execute_sql(marketplace_setup_sql, "Setting up marketplace data integration")
            
            logger.info("✅ Marketplace integration configured!")
            logger.info("📝 Note: In production, replace with actual Snowflake Marketplace shared database")
            
        except Exception as e:
            logger.warning(f"⚠️  Marketplace setup skipped (expected in demo): {e}")
    
    def create_search_services(self) -> None:
        """Create Cortex Search services for unstructured data."""
        logger.info("🔍 Creating Cortex Search services...")
        
        self.execute_sql("USE SCHEMA SEARCH_SERVICES")
        
        try:
            # Research reports search service
            research_search_sql = """
            CREATE CORTEX SEARCH SERVICE IF NOT EXISTS research_reports_search
            ON full_content
            ATTRIBUTES title, author, firm, theme, rating
            WAREHOUSE = COMPUTE_WH
            TARGET_LAG = '1 hour'
            AS (
                SELECT 
                    report_id,
                    title,
                    author,
                    firm,
                    theme,
                    rating,
                    full_content
                FROM RAW_DATA.research_reports
            )
            """
            self.execute_sql(research_search_sql, "Creating research reports search service")
            
            logger.info("✅ Cortex Search services created successfully!")
            
        except Exception as e:
            logger.warning(f"⚠️  Cortex Search service creation requires appropriate privileges: {e}")
            logger.info("📝 Manual setup may be required for Cortex Search services")
    
    def create_demo_agents(self) -> None:
        """Generate agent configuration files for Snowflake Intelligence."""
        logger.info("🤖 Creating demo agent configurations...")
        
        # Create agents directory
        agents_dir = Path("snowflake_intelligence_agents")
        agents_dir.mkdir(exist_ok=True)
        
        # Earnings Analysis Agent
        earnings_agent_config = """
# Earnings Analysis Agent Configuration
# For Snowflake Intelligence Platform

Agent Name: earnings_analysis_agent
Display Name: Tech Earnings Analysis Assistant
Description: Specialized agent for accelerating earnings season analysis in the technology sector

Orchestration Model: Claude 4

Tools:
  - earnings_analysis_semantic (Cortex Analyst)
    Description: Comprehensive earnings data for technology companies including revenue, EPS, surprises, and guidance
    Available Metrics: revenue, net_income, eps, revenue_surprise_percent, eps_surprise_percent, guidance metrics
    Time Range: 8 quarters of historical data with dynamic dates
    
Planning Instructions:
Use the earnings_analysis_semantic view for all quantitative earnings analysis questions including:
- Quarterly performance comparisons
- Earnings surprise analysis
- Revenue and EPS trends
- Guidance vs actual performance
- Peer benchmarking within tech sector

When users ask about specific companies (especially SNOW, AAPL, MSFT, NVDA), focus on recent quarters and highlight surprises or guidance beats/misses.

Response Instructions:
- Provide specific numbers with context (% changes, surprises)
- Always include quarter-over-quarter and year-over-year comparisons
- Highlight consensus beats/misses and their significance
- Format financial figures clearly ($M for millions, $B for billions)
- Cite specific quarters and dates for all metrics
- Use professional, analytical tone suitable for equity research
"""

        # Thematic Research Agent
        thematic_agent_config = """
# Thematic Research Agent Configuration
# For Snowflake Intelligence Platform

Agent Name: thematic_research_agent
Display Name: Tech Thematic Research Assistant
Description: Specialized agent for discovering investment themes from technology sector research and market trends

Orchestration Model: Claude 4

Tools:
  - thematic_research_semantic (Cortex Analyst)
    Description: Technology sector research reports, themes, and investment theses
    Available Data: reports, themes, ratings, price targets, investment theses
    
  - research_reports_search (Cortex Search)
    Description: Full-text search across research report content
    Search Capabilities: Investment themes, company analysis, sector trends
    
Planning Instructions:
For thematic research questions:
1. Use thematic_research_semantic for structured analysis of themes, ratings, and price targets
2. Use research_reports_search for finding specific content within reports
3. Combine both tools when users want theme discovery plus supporting details

Focus on major technology themes like AI adoption, cloud transformation, data analytics evolution.

Response Instructions:
- Identify 2-3 key investment themes from recent research
- Provide specific company names and price targets when available
- Quote relevant excerpts from research reports
- Explain the investment thesis behind each theme
- Highlight risks and opportunities
- Use confident, research-oriented tone
- Always cite specific reports and analysts
"""

        # Write agent configurations
        with open(agents_dir / "earnings_analysis_agent.md", "w") as f:
            f.write(earnings_agent_config)
        
        with open(agents_dir / "thematic_research_agent.md", "w") as f:
            f.write(thematic_agent_config)
        
        logger.info("✅ Agent configurations created in snowflake_intelligence_agents/")
    
    def validate_deployment(self) -> None:
        """Validate that all components are working correctly."""
        logger.info("✅ Validating deployment...")
        
        validations = [
            ("Companies data", "SELECT COUNT(*) FROM RAW_DATA.companies", 10),
            ("Earnings data", "SELECT COUNT(*) FROM RAW_DATA.earnings_data", 50),
            ("Market events", "SELECT COUNT(*) FROM RAW_DATA.market_events", 5),
            ("Research reports", "SELECT COUNT(*) FROM RAW_DATA.research_reports", 3),
            ("Earnings semantic view", "SELECT COUNT(*) FROM ANALYTICS.earnings_analysis_semantic", 50),
            ("Thematic semantic view", "SELECT COUNT(*) FROM ANALYTICS.thematic_research_semantic", 3)
        ]
        
        all_passed = True
        for description, sql, expected_min in validations:
            try:
                result = self.execute_sql(sql)
                count = result[0][0] if result else 0
                
                if count >= expected_min:
                    logger.info(f"✅ {description}: {count} records")
                else:
                    logger.warning(f"⚠️  {description}: {count} records (expected >= {expected_min})")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {description}: Validation failed - {e}")
                all_passed = False
        
        if all_passed:
            logger.info("🎉 All validations passed! Demo is ready.")
        else:
            logger.warning("⚠️  Some validations failed. Please review the logs.")
    
    def deploy(self) -> None:
        """Execute the complete deployment process."""
        logger.info("🚀 Starting JPMC Markets AI Demo deployment...")
        
        try:
            # Connection and setup
            self.connect()
            self.create_database_structure()
            self.create_tables()
            
            # Data generation
            self.load_company_data()
            self.generate_earnings_data()
            self.generate_market_events()
            self.generate_research_reports()
            
            # Analytics and search
            self.create_semantic_views()
            self.setup_marketplace_integration()
            self.create_search_services()
            
            # Demo components
            self.create_demo_agents()
            
            # Validation
            self.validate_deployment()
            
            logger.info("🎉 JPMC Markets AI Demo deployment completed successfully!")
            logger.info(f"📊 Database: MARKETS_AI_DEMO")
            logger.info(f"🎯 Focus: Technology sector including SNOW")
            logger.info(f"📅 Data range: {self.date_range[0].strftime('%Y-%m-%d')} to {self.date_range[1].strftime('%Y-%m-%d')}")
            logger.info(f"📁 Agent configs: ./snowflake_intelligence_agents/")
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
        
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                logger.info("🔌 Snowflake connection closed.")

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy JPMC Markets AI Demo")
    parser.add_argument(
        "--connection", 
        default="default",
        help="Connection name from connections.toml (default: 'default')"
    )
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Deploy
    deployment = MarketsAIDemoDeployment(connection_name=args.connection)
    deployment.deploy()

if __name__ == "__main__":
    main()
