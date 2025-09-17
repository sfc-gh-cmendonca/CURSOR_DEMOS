#!/usr/bin/env python3
"""
JPMC Markets AI Demo Cleanup Script
===================================

This script removes all demo objects from Snowflake to clean up after the demo.
"""

import toml
import snowflake.connector
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DemoCleanup:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def load_connection_config(self, connection_name="default"):
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
            raise FileNotFoundError(f"connections.toml not found")
        
        config = toml.load(config_path)
        return config[connection_name]
    
    def connect_to_snowflake(self) -> None:
        """Establish connection to Snowflake."""
        config = self.load_connection_config()
        connection_params = {
            'account': config.get('account'),
            'user': config.get('user'),
            'password': config.get('password'),
            'warehouse': config.get('warehouse', 'DEMO_WH'),
            'database': config.get('database'),
            'schema': config.get('schema'),
            'role': config.get('role')
        }
        connection_params = {k: v for k, v in connection_params.items() if v is not None}
        
        logger.info(f"Connecting to Snowflake account: {config.get('account')}")
        self.conn = snowflake.connector.connect(**connection_params)
        self.cursor = self.conn.cursor()
        logger.info("✅ Successfully connected to Snowflake!")
    
    def execute_sql(self, sql: str, operation: str) -> None:
        """Execute SQL with error handling."""
        try:
            logger.info(f"🔄 {operation}")
            self.cursor.execute(sql)
            logger.info(f"✅ {operation} - Success")
        except Exception as e:
            logger.warning(f"⚠️ {operation} - Warning: {e}")
            # Continue with cleanup even if some objects don't exist
    
    def cleanup_search_services(self) -> None:
        """Drop Cortex Search services."""
        logger.info("🔍 Cleaning up Cortex Search services...")
        
        # Use MARKETS_AI_DEMO database
        self.execute_sql("USE DATABASE MARKETS_AI_DEMO", "Switching to MARKETS_AI_DEMO database")
        self.execute_sql("USE SCHEMA SEARCH_SERVICES", "Switching to SEARCH_SERVICES schema")
        
        # Drop search services
        search_services = [
            "earnings_documents_search",
            "research_reports_search"
        ]
        
        for service in search_services:
            self.execute_sql(f"DROP CORTEX SEARCH SERVICE IF EXISTS {service}", f"Dropping {service}")
        
        logger.info("✅ Search services cleanup completed!")
    
    def cleanup_semantic_views(self) -> None:
        """Drop semantic views."""
        logger.info("🧠 Cleaning up semantic views...")
        
        self.execute_sql("USE SCHEMA ANALYTICS", "Switching to ANALYTICS schema")
        
        # Drop semantic views
        semantic_views = [
            "earnings_analysis_semantic",
            "thematic_research_semantic"
        ]
        
        for view in semantic_views:
            self.execute_sql(f"DROP SEMANTIC VIEW IF EXISTS {view}", f"Dropping semantic view {view}")
        
        logger.info("✅ Semantic views cleanup completed!")
    
    def cleanup_tables(self) -> None:
        """Drop all demo tables."""
        logger.info("📊 Cleaning up demo tables...")
        
        self.execute_sql("USE SCHEMA RAW_DATA", "Switching to RAW_DATA schema")
        
        # Drop tables in reverse order (considering dependencies)
        tables = [
            "market_events",
            "earnings_call_transcripts", 
            "research_reports",
            "earnings_data",
            "companies"
        ]
        
        for table in tables:
            self.execute_sql(f"DROP TABLE IF EXISTS {table}", f"Dropping table {table}")
        
        logger.info("✅ Tables cleanup completed!")
    
    def cleanup_schemas(self) -> None:
        """Drop demo schemas."""
        logger.info("🏗️ Cleaning up schemas...")
        
        # Drop schemas
        schemas = [
            "SEARCH_SERVICES",
            "ANALYTICS", 
            "RAW_DATA"
        ]
        
        for schema in schemas:
            self.execute_sql(f"DROP SCHEMA IF EXISTS {schema}", f"Dropping schema {schema}")
        
        logger.info("✅ Schemas cleanup completed!")
    
    def cleanup_database(self) -> None:
        """Drop the entire demo database."""
        logger.info("🗑️ Cleaning up demo database...")
        
        # Switch to a different database before dropping MARKETS_AI_DEMO
        self.execute_sql("USE DATABASE SNOWFLAKE", "Switching to SNOWFLAKE database")
        
        # Drop the demo database
        self.execute_sql("DROP DATABASE IF EXISTS MARKETS_AI_DEMO", "Dropping MARKETS_AI_DEMO database")
        
        logger.info("✅ Database cleanup completed!")
    
    def run_cleanup(self, cleanup_level: str = "complete") -> None:
        """Run the cleanup process."""
        try:
            logger.info("🧹 Starting JPMC Markets AI Demo cleanup...")
            
            self.connect_to_snowflake()
            
            if cleanup_level == "complete":
                # Complete cleanup - remove everything
                logger.info("🗑️ Performing COMPLETE cleanup (removing all demo objects)...")
                self.cleanup_search_services()
                self.cleanup_semantic_views()
                self.cleanup_tables()
                self.cleanup_schemas()
                self.cleanup_database()
                
            elif cleanup_level == "partial":
                # Partial cleanup - keep database structure, remove data
                logger.info("🧽 Performing PARTIAL cleanup (keeping structure, removing data)...")
                self.cleanup_search_services()
                self.cleanup_semantic_views()
                self.cleanup_tables()
                
            elif cleanup_level == "data_only":
                # Data only cleanup - remove only table data
                logger.info("🧼 Performing DATA ONLY cleanup (truncating tables)...")
                self.execute_sql("USE DATABASE MARKETS_AI_DEMO", "Switching to demo database")
                self.execute_sql("USE SCHEMA RAW_DATA", "Switching to RAW_DATA schema")
                
                tables = ["market_events", "earnings_call_transcripts", "research_reports", "earnings_data", "companies"]
                for table in tables:
                    self.execute_sql(f"TRUNCATE TABLE IF EXISTS {table}", f"Truncating table {table}")
            
            logger.info("🎉 Demo cleanup completed successfully!")
            logger.info(f"📊 Cleanup level: {cleanup_level.upper()}")
            
            if cleanup_level == "complete":
                logger.info("✅ All demo objects have been removed from Snowflake")
            elif cleanup_level == "partial":
                logger.info("✅ Demo data removed, database structure preserved")
            elif cleanup_level == "data_only":
                logger.info("✅ Table data cleared, structure and objects preserved")
                
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()
                logger.info("🔌 Connection closed")

def main():
    """Main function with cleanup level options."""
    import sys
    
    cleanup_level = "complete"  # Default
    
    if len(sys.argv) > 1:
        level = sys.argv[1].lower()
        if level in ["complete", "partial", "data_only"]:
            cleanup_level = level
        else:
            print("❌ Invalid cleanup level. Use: complete, partial, or data_only")
            sys.exit(1)
    
    print(f"""
🧹 JPMC Markets AI Demo Cleanup
===============================

Cleanup Level: {cleanup_level.upper()}

Options:
- complete:   Remove all demo objects (database, schemas, tables, views, search services)
- partial:    Remove data and objects, keep database structure
- data_only:  Clear table data only, keep all objects

Usage: python cleanup_demo.py [complete|partial|data_only]

⚠️  WARNING: This action cannot be undone!
""")
    
    if cleanup_level == "complete":
        confirm = input("Are you sure you want to COMPLETELY remove all demo objects? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cleanup cancelled")
            sys.exit(0)
    
    cleanup = DemoCleanup()
    cleanup.run_cleanup(cleanup_level)

if __name__ == "__main__":
    main()
