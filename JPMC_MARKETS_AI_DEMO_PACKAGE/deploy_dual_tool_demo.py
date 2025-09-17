#!/usr/bin/env python3
"""
JPMC Markets AI Demo - Dual Tool Deployment Script
==================================================

This script creates a comprehensive demo with BOTH Cortex Analyst and Cortex Search tools:
- Scenario 1: Earnings Analysis Agent (Analyst + Search)
- Scenario 2: Thematic Research Agent (Analyst + Search)

Each agent uses structured data analysis AND unstructured content search
"""

import os
import sys
import logging
import toml
from datetime import datetime, timedelta
from pathlib import Path
import snowflake.connector
from typing import Dict, List, Tuple
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DualToolMarketsDemo:
    """Enhanced deployment with both Cortex Analyst and Cortex Search capabilities."""
    
    def __init__(self, connection_name: str = "default"):
        """Initialize with Snowflake connection."""
        self.connection_name = connection_name
        self.conn = None
        self.cursor = None
        
        # Tech companies for demo
        self.tech_companies = [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corporation"), 
            ("GOOGL", "Alphabet Inc."),
            ("NVDA", "NVIDIA Corporation"),
            ("SNOW", "Snowflake Inc."),
            ("META", "Meta Platforms Inc."),
            ("TSLA", "Tesla Inc.")
        ]
        
        # Calculate current quarter dates
        self.current_date = datetime.now()
        self.quarters = self._get_recent_quarters(4)  # Last 4 quarters
        
    def _get_recent_quarters(self, num_quarters: int) -> List[Tuple[str, datetime, datetime]]:
        """Generate recent quarters with labels."""
        quarters = []
        base_date = datetime(self.current_date.year, ((self.current_date.month - 1) // 3) * 3 + 1, 1)
        
        for i in range(num_quarters):
            quarter_start = base_date - timedelta(days=90 * i)
            quarter_start = datetime(quarter_start.year, ((quarter_start.month - 1) // 3) * 3 + 1, 1)
            
            if quarter_start.month == 10:
                quarter_end = datetime(quarter_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                quarter_end = datetime(quarter_start.year, quarter_start.month + 3, 1) - timedelta(days=1)
            
            quarter_label = f"{quarter_start.year}Q{((quarter_start.month - 1) // 3) + 1}"
            quarters.append((quarter_label, quarter_start, quarter_end))
            
        return quarters[::-1]  # Chronological order
    
    def _load_connection_config(self) -> Dict:
        """Load connection from connections.toml."""
        possible_paths = [
            Path.home() / ".config" / "snowflake" / "connections.toml",
            Path.home() / "Library" / "Application Support" / "snowflake" / "connections.toml",
            Path.home() / "AppData" / "Local" / "snowflake" / "connections.toml",
            Path("connections.toml"),
        ]
        
        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if not config_path:
            raise FileNotFoundError(f"connections.toml not found in any of: {possible_paths}")
        
        logger.info(f"Loading connection from: {config_path}")
        config = toml.load(config_path)
        
        if self.connection_name not in config:
            raise KeyError(f"Connection '{self.connection_name}' not found")
        
        return config[self.connection_name]
    
    def connect(self) -> None:
        """Connect to Snowflake."""
        try:
            config = self._load_connection_config()
            
            connection_params = {
                'account': config.get('account'),
                'user': config.get('user'),
                'password': config.get('password'),
                'warehouse': config.get('warehouse', 'DEMO_WH'),
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
            logger.error(f"❌ Failed to connect: {e}")
            raise
    
    def execute_sql(self, sql: str, description: str = "") -> List:
        """Execute SQL with logging."""
        try:
            if description:
                logger.info(f"🔄 {description}")
            
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
        """Create database and schemas."""
        logger.info("🏗️ Creating database structure...")
        
        # Create database
        self.execute_sql(
            "CREATE DATABASE IF NOT EXISTS MARKETS_AI_DEMO",
            "Creating MARKETS_AI_DEMO database"
        )
        
        # Use database
        self.execute_sql("USE DATABASE MARKETS_AI_DEMO")
        
        # Create schemas
        schemas = ['RAW_DATA', 'ANALYTICS', 'SEARCH_SERVICES']
        for schema in schemas:
            self.execute_sql(
                f"CREATE SCHEMA IF NOT EXISTS {schema}",
                f"Creating {schema} schema"
            )
        
        logger.info("✅ Database structure created!")
    
    def create_tables(self) -> None:
        """Create tables for both structured and unstructured data."""
        logger.info("📊 Creating demo tables...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Companies table
        companies_sql = """
        CREATE OR REPLACE TABLE companies (
            ticker VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(200) NOT NULL,
            sector VARCHAR(100) NOT NULL,
            market_cap_billions DECIMAL(15,2),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(companies_sql, "Creating companies table")
        
        # Earnings data table
        earnings_sql = """
        CREATE OR REPLACE TABLE earnings_data (
            ticker VARCHAR(10),
            quarter VARCHAR(10),
            earnings_date DATE,
            revenue_millions DECIMAL(15,2),
            net_income_millions DECIMAL(15,2),
            earnings_per_share DECIMAL(10,4),
            analyst_est_revenue DECIMAL(15,2),
            analyst_est_eps DECIMAL(10,4),
            revenue_surprise_percent DECIMAL(5,2),
            eps_surprise_percent DECIMAL(5,2),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (ticker, quarter)
        )
        """
        self.execute_sql(earnings_sql, "Creating earnings_data table")
        
        # Earnings call transcripts table (for search)
        transcripts_sql = """
        CREATE OR REPLACE TABLE earnings_call_transcripts (
            transcript_id VARCHAR(50) PRIMARY KEY,
            ticker VARCHAR(10),
            quarter VARCHAR(10),
            call_date DATE,
            call_type VARCHAR(50),
            title VARCHAR(500),
            participants TEXT,
            management_remarks TEXT,
            qa_section TEXT,
            full_transcript TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(transcripts_sql, "Creating earnings_call_transcripts table")
        
        # Research reports table
        research_reports_sql = """
        CREATE OR REPLACE TABLE research_reports (
            report_id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            author VARCHAR(200),
            firm VARCHAR(200),
            publish_date DATE,
            sector VARCHAR(100),
            tickers_covered VARCHAR(500),
            theme VARCHAR(200),
            investment_thesis TEXT,
            key_risks TEXT,
            market_analysis TEXT,
            company_analysis TEXT,
            rating VARCHAR(50),
            price_target DECIMAL(10,2),
            full_report TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        self.execute_sql(research_reports_sql, "Creating research_reports table")
        
        logger.info("✅ All tables created!")
    
    def load_company_data(self) -> None:
        """Load tech sector company data."""
        logger.info("👥 Loading company data...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        for ticker, name in self.tech_companies:
            market_cap = 1000 if ticker == "AAPL" else 500 if ticker == "MSFT" else 200
            insert_sql = f"""
            INSERT INTO companies (ticker, company_name, sector, market_cap_billions)
            VALUES ('{ticker}', '{name}', 'Technology', {market_cap})
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Company data loaded!")
    
    def generate_earnings_data(self) -> None:
        """Generate earnings data with realistic metrics."""
        logger.info("📈 Generating earnings data...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        for ticker, company_name in self.tech_companies:
            for quarter_label, start_date, end_date in self.quarters:
                
                earnings_date = end_date + timedelta(days=random.randint(15, 45))
                
                # Base financial metrics
                if ticker == "SNOW":
                    revenue = random.uniform(600, 800)  # Millions
                    net_income = random.uniform(-50, 50)  # Growth stage
                    eps = net_income / 350  # Share count
                elif ticker == "AAPL":
                    revenue = random.uniform(90000, 95000)
                    net_income = random.uniform(20000, 25000)
                    eps = net_income / 15500
                elif ticker == "NVDA":
                    revenue = random.uniform(18000, 22000)
                    net_income = random.uniform(4000, 6000)
                    eps = net_income / 2500
                else:
                    revenue = random.uniform(20000, 50000)
                    net_income = random.uniform(5000, 15000)
                    eps = net_income / 7000
                
                # Analyst estimates (with some variation)
                analyst_revenue = revenue * random.uniform(0.95, 1.05)
                analyst_eps = eps * random.uniform(0.9, 1.1)
                
                # Calculate surprises
                revenue_surprise = ((revenue - analyst_revenue) / analyst_revenue) * 100
                eps_surprise = ((eps - analyst_eps) / analyst_eps) * 100
                
                insert_sql = f"""
                INSERT INTO earnings_data VALUES (
                    '{ticker}', '{quarter_label}', '{earnings_date.strftime('%Y-%m-%d')}',
                    {revenue:.2f}, {net_income:.2f}, {eps:.4f},
                    {analyst_revenue:.2f}, {analyst_eps:.4f},
                    {revenue_surprise:.2f}, {eps_surprise:.2f}, 
                    CURRENT_TIMESTAMP()
                )
                """
                self.execute_sql(insert_sql)
        
        logger.info("✅ Earnings data generated!")
    
    def generate_earnings_transcripts(self) -> None:
        """Generate earnings call transcripts for search functionality."""
        logger.info("🎙️ Generating earnings call transcripts...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Generate transcripts for the latest quarter for key companies
        latest_quarter = self.quarters[-1]
        key_companies = [("SNOW", "Snowflake Inc."), ("NVDA", "NVIDIA Corporation"), ("MSFT", "Microsoft Corporation")]
        
        for ticker, company_name in key_companies:
            call_date = latest_quarter[2] + timedelta(days=random.randint(20, 40))
            
            if ticker == "SNOW":
                management_remarks = f"""
                Good afternoon and thank you for joining {company_name}'s {latest_quarter[0]} earnings call. 
                I'm pleased to report another strong quarter with revenue growth of 35% year-over-year. 
                Our data cloud platform continues to see exceptional adoption across enterprises globally.
                
                Key highlights this quarter include significant wins in the AI and machine learning space. 
                Customers are increasingly choosing Snowflake as their foundation for AI initiatives due to our 
                unique architecture that unifies structured and unstructured data. We've seen tremendous growth 
                in our Cortex AI services, which are enabling customers to build intelligent applications faster.
                
                Looking ahead, we remain confident in our ability to capture the massive market opportunity 
                in data and AI. Our product innovation continues to accelerate with new capabilities in 
                document AI, vector search, and machine learning operations.
                """
                
                qa_section = f"""
                Q: Can you elaborate on the AI opportunity and how Snowflake is positioned?
                A: The AI revolution is fundamentally changing how organizations work with data. What we're seeing 
                is that successful AI applications require a unified data foundation that can handle both structured 
                and unstructured data at scale. Snowflake's architecture is uniquely positioned for this.
                
                Q: What are you seeing in terms of customer adoption of Cortex AI?
                A: Cortex AI adoption has exceeded our expectations. Customers are using our vector database 
                capabilities, our search services, and our LLM functions to build production AI applications. 
                The feedback has been extremely positive.
                
                Q: How should we think about the competitive landscape in data and AI?
                A: We believe our differentiated architecture gives us significant advantages. The ability to 
                process structured and unstructured data together, combined with our Cortex AI services, 
                creates a compelling platform for AI applications.
                """
                
            elif ticker == "NVDA":
                management_remarks = f"""
                Thank you for joining NVIDIA's {latest_quarter[0]} earnings call. We delivered record revenue 
                driven by exceptional demand for our AI computing platforms. Data center revenue reached new highs 
                as enterprises accelerate their AI adoption.
                
                The AI revolution continues to drive unprecedented demand for our H100 and A100 GPUs. 
                We're seeing strong adoption across cloud service providers, enterprises, and sovereign AI initiatives. 
                Our Omniverse platform is enabling new workflows in digital twins and simulation.
                
                Looking forward, we expect continued strong demand for AI infrastructure as organizations 
                deploy generative AI applications at scale.
                """
                
                qa_section = f"""
                Q: Can you provide more details on enterprise AI adoption trends?
                A: Enterprise adoption of AI is accelerating rapidly. We're seeing companies move from 
                experimentation to production deployment of AI applications. This is driving significant 
                infrastructure investment and demand for our platforms.
                
                Q: How are you positioned for the next phase of AI development?
                A: We continue to innovate across the full stack from chips to software. Our CUDA ecosystem 
                remains the foundation for AI development, and we're expanding our platform capabilities 
                to serve the growing AI market.
                """
                
            else:  # MSFT
                management_remarks = f"""
                Good afternoon. Microsoft delivered strong results for {latest_quarter[0]} with revenue growth 
                across all business segments. Our intelligent cloud segment continues to benefit from AI adoption 
                and Azure's growing market share.
                
                Azure AI services are seeing tremendous demand as customers build AI-powered applications. 
                Our partnership with OpenAI has enabled us to integrate cutting-edge AI capabilities 
                across our entire product portfolio, from Office 365 to Azure.
                
                We're particularly excited about the momentum in Azure AI and the adoption of GitHub Copilot, 
                which is transforming how developers write code.
                """
                
                qa_section = f"""
                Q: Can you quantify the impact of AI on Azure growth?
                A: AI services are becoming a significant contributor to Azure growth. We're seeing strong 
                adoption of Azure OpenAI Service and other AI capabilities. This is still early innings 
                for AI adoption across enterprises.
                
                Q: How are customers using AI services in practice?
                A: Customers are building everything from customer service chatbots to code generation 
                tools to document analysis systems. The breadth of use cases continues to expand as 
                the technology matures.
                """
            
            full_transcript = f"""
            {company_name} {latest_quarter[0]} Earnings Call Transcript
            
            MANAGEMENT REMARKS:
            {management_remarks}
            
            Q&A SECTION:
            {qa_section}
            """
            
            insert_sql = f"""
            INSERT INTO earnings_call_transcripts VALUES (
                '{ticker}_{latest_quarter[0]}_TRANSCRIPT',
                '{ticker}',
                '{latest_quarter[0]}',
                '{call_date.strftime('%Y-%m-%d')}',
                'Quarterly Earnings Call',
                '{company_name} {latest_quarter[0]} Earnings Call',
                'Management Team, Analysts',
                '{management_remarks.replace("'", "''")}',
                '{qa_section.replace("'", "''")}',
                '{full_transcript.replace("'", "''")}',
                CURRENT_TIMESTAMP()
            )
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Earnings call transcripts generated!")
    
    def generate_research_reports(self) -> None:
        """Generate detailed research reports for search functionality."""
        logger.info("📄 Generating research reports...")
        
        self.execute_sql("USE SCHEMA RAW_DATA")
        
        # Detailed research reports
        reports = [
            {
                "id": "RPT_AI_ENTERPRISE_2024",
                "title": "The Enterprise AI Revolution: Infrastructure Winners",
                "author": "Sarah Chen",
                "firm": "Tech Research Partners",
                "date": self.quarters[-1][2] + timedelta(days=10),
                "tickers": "NVDA, MSFT, GOOGL, SNOW",
                "theme": "Artificial Intelligence",
                "thesis": "Enterprise AI adoption is accelerating rapidly creating unprecedented demand for specialized infrastructure and platforms.",
                "risks": "Regulatory scrutiny, competition from open source alternatives, high capital requirements for AI infrastructure development.",
                "market_analysis": "The global AI market is expected to reach $1.8 trillion by 2030. Enterprise adoption is moving from experimentation to production deployment, driving significant infrastructure investment.",
                "company_analysis": "NVIDIA leads in AI chips with H100 dominance. Microsoft Azure AI services seeing strong growth. Snowflake positioned well for AI data needs with Cortex platform.",
                "rating": "Buy",
                "target": 280.0
            },
            {
                "id": "RPT_DATA_CLOUD_2024",
                "title": "Data Cloud Transformation: Beyond Traditional Warehousing",
                "author": "Michael Rodriguez", 
                "firm": "Financial Tech Insights",
                "date": self.quarters[-1][2] + timedelta(days=15),
                "tickers": "SNOW, MSFT, ORCL",
                "theme": "Data Analytics",
                "thesis": "Organizations are moving beyond traditional data warehousing to comprehensive data cloud platforms that enable real-time analytics and AI workloads.",
                "risks": "Intense competition from hyperscale cloud providers, margin pressure from pricing wars, complexity of data migration projects.",
                "market_analysis": "The data cloud market is experiencing rapid transformation as organizations seek unified platforms for structured and unstructured data processing.",
                "company_analysis": "Snowflake leads in cloud-native architecture. Microsoft Azure Synapse gaining traction. Oracle modernizing with Autonomous Database offerings.",
                "rating": "Buy",
                "target": 200.0
            },
            {
                "id": "RPT_SNOWFLAKE_DEEP_2024",
                "title": "Snowflake: AI-Native Data Cloud Leadership",
                "author": "Jennifer Liu",
                "firm": "Growth Equity Research", 
                "date": self.quarters[-1][2] + timedelta(days=5),
                "tickers": "SNOW",
                "theme": "Data Cloud Platform",
                "thesis": "Snowflake architecture uniquely positions it for the AI era with native support for unstructured data, vector databases, and ML workloads creating competitive advantages.",
                "risks": "Hyperscaler competition from AWS, Google, Microsoft. Customer concentration risks. Execution challenges on AI roadmap expansion.",
                "market_analysis": "The convergence of data and AI is creating new market opportunities. Organizations need platforms that can handle both traditional analytics and modern AI workloads seamlessly.",
                "company_analysis": "Snowflake Cortex AI services differentiating the platform. Strong customer adoption of new AI capabilities. Expanding use cases beyond traditional data warehousing into AI and ML.",
                "rating": "Strong Buy",
                "target": 220.0
            }
        ]
        
        for report in reports:
            full_report = f"""
            {report["title"]}
            
            Author: {report["author"]}, {report["firm"]}
            Date: {report["date"].strftime('%Y-%m-%d')}
            Companies Covered: {report["tickers"]}
            
            EXECUTIVE SUMMARY:
            {report["thesis"]}
            
            INVESTMENT THESIS:
            {report["market_analysis"]}
            
            COMPANY ANALYSIS:
            {report["company_analysis"]}
            
            KEY RISKS:
            {report["risks"]}
            
            RECOMMENDATION: {report["rating"]}
            PRICE TARGET: ${report["target"]}
            
            This report provides detailed analysis of investment opportunities in the {report["theme"]} sector 
            with specific focus on infrastructure and platform companies positioned to benefit from technological 
            transformation and enterprise adoption trends.
            """
            
            insert_sql = f"""
            INSERT INTO research_reports VALUES (
                '{report["id"]}', '{report["title"]}', '{report["author"]}', '{report["firm"]}',
                '{report["date"].strftime('%Y-%m-%d')}', 'Technology', '{report["tickers"]}',
                '{report["theme"]}', '{report["thesis"].replace("'", "''")}', '{report["risks"].replace("'", "''")}',
                '{report["market_analysis"].replace("'", "''")}', '{report["company_analysis"].replace("'", "''")}',
                '{report["rating"]}', {report["target"]}, '{full_report.replace("'", "''")}',
                CURRENT_TIMESTAMP()
            )
            """
            self.execute_sql(insert_sql)
        
        logger.info("✅ Research reports generated!")
    
    def create_semantic_views(self) -> None:
        """Create semantic views for Cortex Analyst."""
        logger.info("🧠 Creating semantic views...")
        
        self.execute_sql("USE SCHEMA ANALYTICS")
        
        # Earnings analysis view
        earnings_view_sql = """
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
            e.analyst_est_revenue,
            e.analyst_est_eps,
            c.market_cap_billions
        FROM RAW_DATA.earnings_data e
        JOIN RAW_DATA.companies c ON e.ticker = c.ticker
        WHERE c.sector = 'Technology'
        """
        self.execute_sql(earnings_view_sql, "Creating earnings analysis view")
        
        # Thematic research view
        thematic_view_sql = """
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
            r.tickers_covered as companies_covered,
            r.sector
        FROM RAW_DATA.research_reports r
        WHERE r.sector = 'Technology'
        """
        self.execute_sql(thematic_view_sql, "Creating thematic research view")
        
        logger.info("✅ Semantic views created!")
    
    def create_search_services(self) -> None:
        """Create Cortex Search services for unstructured data."""
        logger.info("🔍 Creating Cortex Search services...")
        
        self.execute_sql("USE SCHEMA SEARCH_SERVICES")
        
        try:
            # Earnings transcripts search service
            transcripts_search_sql = """
            CREATE OR REPLACE CORTEX SEARCH SERVICE earnings_transcripts_search
            ON full_transcript
            ATTRIBUTES transcript_id, title, ticker, quarter, call_date
            WAREHOUSE = DEMO_WH
            TARGET_LAG = '1 hour'
            AS (
                SELECT 
                    transcript_id,
                    title,
                    ticker,
                    quarter,
                    call_date,
                    full_transcript
                FROM RAW_DATA.earnings_call_transcripts
            )
            """
            self.execute_sql(transcripts_search_sql, "Creating earnings transcripts search service")
            
            # Research reports search service
            research_search_sql = """
            CREATE OR REPLACE CORTEX SEARCH SERVICE research_reports_search
            ON full_report
            ATTRIBUTES report_id, title, author, firm, theme, rating, price_target
            WAREHOUSE = DEMO_WH
            TARGET_LAG = '1 hour'
            AS (
                SELECT 
                    report_id,
                    title,
                    author,
                    firm,
                    theme,
                    rating,
                    price_target,
                    full_report
                FROM RAW_DATA.research_reports
            )
            """
            self.execute_sql(research_search_sql, "Creating research reports search service")
            
            logger.info("✅ Cortex Search services created successfully!")
            
        except Exception as e:
            logger.warning(f"⚠️ Cortex Search service creation issue: {e}")
            logger.info("📝 Services may need manual creation or require special privileges")
    
    def validate_deployment(self) -> None:
        """Validate deployment."""
        logger.info("✅ Validating deployment...")
        
        validations = [
            ("Companies", "SELECT COUNT(*) FROM RAW_DATA.companies", 7),
            ("Earnings data", "SELECT COUNT(*) FROM RAW_DATA.earnings_data", 28),
            ("Earnings transcripts", "SELECT COUNT(*) FROM RAW_DATA.earnings_call_transcripts", 3),
            ("Research reports", "SELECT COUNT(*) FROM RAW_DATA.research_reports", 3),
            ("Earnings view", "SELECT COUNT(*) FROM ANALYTICS.earnings_analysis_semantic", 28),
            ("Research view", "SELECT COUNT(*) FROM ANALYTICS.thematic_research_semantic", 3)
        ]
        
        for description, sql, expected_min in validations:
            try:
                result = self.execute_sql(sql)
                count = result[0][0] if result else 0
                logger.info(f"✅ {description}: {count} records")
            except Exception as e:
                logger.error(f"❌ {description}: Validation failed - {e}")
        
        # Check search services
        try:
            self.execute_sql("USE SCHEMA SEARCH_SERVICES")
            search_services = self.execute_sql("SHOW CORTEX SEARCH SERVICES")
            logger.info(f"🔍 Search services created: {len(search_services)}")
        except:
            logger.warning("⚠️ Could not validate search services")
    
    def deploy(self) -> None:
        """Execute complete deployment."""
        logger.info("🚀 Starting dual-tool JPMC Markets AI Demo deployment...")
        
        try:
            self.connect()
            self.create_database_structure()
            self.create_tables()
            self.load_company_data()
            self.generate_earnings_data()
            self.generate_earnings_transcripts()
            self.generate_research_reports()
            self.create_semantic_views()
            self.create_search_services()
            self.validate_deployment()
            
            logger.info("🎉 Dual-tool demo deployment completed successfully!")
            logger.info("📊 Database: MARKETS_AI_DEMO")
            logger.info("🎯 Focus: Technology sector including SNOW")
            logger.info("🛠️ Tools: Cortex Analyst + Cortex Search for each agent")
            logger.info("📈 Ready for sophisticated dual-tool Demo Scenarios!")
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
        
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                logger.info("🔌 Connection closed")

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy dual-tool JPMC Markets AI Demo")
    parser.add_argument(
        "--connection", 
        default="default",
        help="Connection name from connections.toml"
    )
    
    args = parser.parse_args()
    
    deployment = DualToolMarketsDemo(connection_name=args.connection)
    deployment.deploy()

if __name__ == "__main__":
    main()
