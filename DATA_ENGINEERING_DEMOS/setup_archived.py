"""
Main Setup Script for Data Engineering Demo
Orchestrates the complete demo environment setup
"""
import argparse
import sys
from config import DataEngDemoConfig
from utils.snowpark_session import get_snowpark_session, set_context, enable_query_tagging
from utils.logging_utils import setup_logger, log_step, PipelineTimer
from pipelines import setup_stages_and_formats, transform_to_curated, run_data_quality_checks
from pipelines.transformation import create_aggregated_views
from data_sharing import setup_demo_share

# Note: Data generation removed - this setup is for the main demo infrastructure only
# The FACTSET ETF demo (demos/factset_etf_iceberg/) is self-contained and doesn't need this setup

logger = setup_logger("setup")


def setup_database_and_schemas(session):
    """Create database and schemas"""
    with PipelineTimer(logger, "Database and Schema Setup"):
        # Execute SQL setup script
        logger.info("Creating database and schemas...")
        
        # Create database
        session.sql(f"""
            CREATE DATABASE IF NOT EXISTS {DataEngDemoConfig.DATABASE}
            COMMENT = 'Data Engineering Demo: ETL/ELT, Data Sharing, Dynamic Tables'
        """).collect()
        
        # Create schemas
        schemas = [
            (DataEngDemoConfig.SCHEMA_RAW, 'Landing zone for raw data ingestion'),
            (DataEngDemoConfig.SCHEMA_STAGING, 'Staging area for data validation'),
            (DataEngDemoConfig.SCHEMA_CURATED, 'Curated clean data with business logic'),
            (DataEngDemoConfig.SCHEMA_ANALYTICS, 'Business-ready analytics tables'),
            (DataEngDemoConfig.SCHEMA_SHARED, 'Curated data for external sharing')
        ]
        
        for schema_name, comment in schemas:
            session.sql(f"""
                CREATE SCHEMA IF NOT EXISTS {DataEngDemoConfig.DATABASE}.{schema_name}
                COMMENT = '{comment}'
            """).collect()
            logger.info(f"✅ Schema created: {schema_name}")


def setup_warehouses(session):
    """Create compute warehouses"""
    with PipelineTimer(logger, "Warehouse Setup"):
        warehouses = [
            (DataEngDemoConfig.WAREHOUSE_LOAD, 'MEDIUM', 'Data loading operations'),
            (DataEngDemoConfig.WAREHOUSE_TRANSFORM, 'LARGE', 'Data transformation operations'),
            (DataEngDemoConfig.WAREHOUSE_ANALYTICS, 'XSMALL', 'Analytics queries')
        ]
        
        for wh_name, size, comment in warehouses:
            session.sql(f"""
                CREATE WAREHOUSE IF NOT EXISTS {wh_name}
                WAREHOUSE_SIZE = '{size}'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE
                COMMENT = '{comment}'
            """).collect()
            logger.info(f"✅ Warehouse created: {wh_name} ({size})")


def note_about_demos():
    """
    Note: Synthetic data generation has been removed from this main setup.
    
    This setup script creates the base infrastructure (database, schemas, warehouses).
    Individual demos (like demos/factset_etf_iceberg/) are self-contained and include
    their own data setup specific to their use case.
    
    For FACTSET ETF Constituents demo, see: demos/factset_etf_iceberg/
    """
    pass


def setup_pipeline_infrastructure(session):
    """Set up stages, file formats, and pipes"""
    with PipelineTimer(logger, "Pipeline Infrastructure Setup"):
        set_context(session,
                   database=DataEngDemoConfig.DATABASE,
                   schema=DataEngDemoConfig.SCHEMA_RAW,
                   warehouse=DataEngDemoConfig.WAREHOUSE_LOAD)
        
        setup_stages_and_formats(session)


def transform_data(session):
    """Transform data to curated layer"""
    with PipelineTimer(logger, "Data Transformation"):
        set_context(session,
                   database=DataEngDemoConfig.DATABASE,
                   warehouse=DataEngDemoConfig.WAREHOUSE_TRANSFORM)
        
        enable_query_tagging(session, "DATA_ENG_DEMO_TRANSFORM")
        
        # Transform to curated
        transform_to_curated(session)
        
        # Create analytical views
        create_aggregated_views(session)


def validate_data_quality(session):
    """Run data quality checks"""
    with PipelineTimer(logger, "Data Quality Validation"):
        set_context(session,
                   database=DataEngDemoConfig.DATABASE,
                   warehouse=DataEngDemoConfig.WAREHOUSE_ANALYTICS)
        
        all_passed = True
        for table in ["CUSTOMERS", "PRODUCTS", "TRANSACTIONS"]:
            results = run_data_quality_checks(session, table)
            if results["quality_score"] < DataEngDemoConfig.QUALITY_THRESHOLD_PASS * 100:
                all_passed = False
        
        if all_passed:
            logger.info("✅ All data quality checks passed!")
        else:
            logger.warning("⚠️  Some data quality checks failed")


def setup_dynamic_tables(session):
    """Create dynamic tables for incremental processing"""
    with PipelineTimer(logger, "Dynamic Tables Setup"):
        set_context(session,
                   database=DataEngDemoConfig.DATABASE,
                   warehouse=DataEngDemoConfig.WAREHOUSE_TRANSFORM)
        
        logger.info("Creating dynamic tables...")
        
        # Customer transaction summary
        session.sql(f"""
            CREATE OR REPLACE DYNAMIC TABLE {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMER_TRANSACTION_SUMMARY
            TARGET_LAG = '{DataEngDemoConfig.DYNAMIC_TABLE_REFRESH}'
            WAREHOUSE = {DataEngDemoConfig.WAREHOUSE_TRANSFORM}
            AS
            SELECT 
                c.CUSTOMER_ID,
                c.FULL_NAME,
                c.CUSTOMER_SEGMENT,
                c.LOYALTY_TIER,
                COUNT(DISTINCT t.TRANSACTION_ID) AS TOTAL_TRANSACTIONS,
                SUM(t.TOTAL_AMOUNT) AS TOTAL_SPENT,
                AVG(t.TOTAL_AMOUNT) AS AVG_TRANSACTION_VALUE,
                MAX(t.TRANSACTION_DATE) AS LAST_TRANSACTION_DATE,
                MIN(t.TRANSACTION_DATE) AS FIRST_TRANSACTION_DATE,
                CURRENT_TIMESTAMP() AS LAST_UPDATED
            FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS c
            LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS t
                ON c.CUSTOMER_ID = t.CUSTOMER_ID
            GROUP BY c.CUSTOMER_ID, c.FULL_NAME, c.CUSTOMER_SEGMENT, c.LOYALTY_TIER
        """).collect()
        
        logger.info("✅ Dynamic tables created successfully")


def setup_data_sharing(session):
    """Set up data shares"""
    with PipelineTimer(logger, "Data Sharing Setup"):
        set_context(session,
                   database=DataEngDemoConfig.DATABASE,
                   warehouse=DataEngDemoConfig.WAREHOUSE_ANALYTICS)
        
        setup_demo_share(session)


def cleanup_demo(session):
    """Clean up all demo objects"""
    log_step(logger, "Demo Cleanup", "START")
    
    logger.warning("🗑️  Cleaning up all demo objects...")
    logger.warning("⚠️  This will delete all data!")
    
    # Drop database (cascades to all objects)
    session.sql(f"DROP DATABASE IF EXISTS {DataEngDemoConfig.DATABASE}").collect()
    
    # Drop warehouses
    for wh in [DataEngDemoConfig.WAREHOUSE_LOAD, 
               DataEngDemoConfig.WAREHOUSE_TRANSFORM,
               DataEngDemoConfig.WAREHOUSE_ANALYTICS]:
        session.sql(f"DROP WAREHOUSE IF EXISTS {wh}").collect()
    
    # Drop share
    session.sql(f"DROP SHARE IF EXISTS {DataEngDemoConfig.SHARE_NAME}").collect()
    
    logger.info("✅ Cleanup complete!")
    log_step(logger, "Demo Cleanup", "COMPLETE")


def validate_setup(session):
    """Validate the demo setup"""
    log_step(logger, "Setup Validation", "START")
    
    validation_results = {
        "database_exists": False,
        "schemas_exist": 0,
        "tables_exist": 0,
        "warehouses_exist": 0,
        "share_exists": False
    }
    
    # Check database
    try:
        result = session.sql(f"SHOW DATABASES LIKE '{DataEngDemoConfig.DATABASE}'").collect()
        validation_results["database_exists"] = len(result) > 0
    except:
        pass
    
    # Check schemas
    try:
        result = session.sql(f"SHOW SCHEMAS IN DATABASE {DataEngDemoConfig.DATABASE}").collect()
        validation_results["schemas_exist"] = len(result)
    except:
        pass
    
    # Check tables
    try:
        set_context(session, database=DataEngDemoConfig.DATABASE)
        for schema in [DataEngDemoConfig.SCHEMA_RAW, DataEngDemoConfig.SCHEMA_CURATED]:
            result = session.sql(f"SHOW TABLES IN SCHEMA {schema}").collect()
            validation_results["tables_exist"] += len(result)
    except:
        pass
    
    # Check warehouses
    try:
        for wh in [DataEngDemoConfig.WAREHOUSE_LOAD, 
                   DataEngDemoConfig.WAREHOUSE_TRANSFORM,
                   DataEngDemoConfig.WAREHOUSE_ANALYTICS]:
            result = session.sql(f"SHOW WAREHOUSES LIKE '{wh}'").collect()
            if len(result) > 0:
                validation_results["warehouses_exist"] += 1
    except:
        pass
    
    # Check share
    try:
        result = session.sql(f"SHOW SHARES LIKE '{DataEngDemoConfig.SHARE_NAME}'").collect()
        validation_results["share_exists"] = len(result) > 0
    except:
        pass
    
    # Print results
    logger.info("📊 Validation Results:")
    logger.info(f"   Database exists: {'✅' if validation_results['database_exists'] else '❌'}")
    logger.info(f"   Schemas: {validation_results['schemas_exist']}")
    logger.info(f"   Tables: {validation_results['tables_exist']}")
    logger.info(f"   Warehouses: {validation_results['warehouses_exist']}/3")
    logger.info(f"   Share exists: {'✅' if validation_results['share_exists'] else '❌'}")
    
    log_step(logger, "Setup Validation", "COMPLETE")
    
    return validation_results


def main():
    """Main setup orchestration"""
    parser = argparse.ArgumentParser(description="Data Engineering Demo Setup")
    parser.add_argument("--connection_name", 
                       default=DataEngDemoConfig.SNOWFLAKE_CONNECTION_NAME,
                       help="Snowflake connection name from connections.toml")
    parser.add_argument("--mode",
                       choices=["full", "quick", "cleanup", "validate"],
                       default="full",
                       help="Setup mode: full (all steps), quick (minimal data), cleanup (remove all), validate (check setup)")
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🚀 DATA ENGINEERING DEMO SETUP")
    logger.info(f"   Version: {DataEngDemoConfig.DEMO_VERSION}")
    logger.info(f"   Mode: {args.mode}")
    logger.info("=" * 80)
    
    # Create session
    session = get_snowpark_session(args.connection_name)
    
    try:
        if args.mode == "cleanup":
            cleanup_demo(session)
            
        elif args.mode == "validate":
            validate_setup(session)
            
        elif args.mode in ["full", "quick"]:
            # Adjust data volumes for quick mode
            if args.mode == "quick":
                logger.info("📦 Quick mode: Using minimal data volumes")
                DataEngDemoConfig.NUM_CUSTOMERS = 100
                DataEngDemoConfig.NUM_PRODUCTS = 50
                DataEngDemoConfig.NUM_TRANSACTIONS_PER_DAY = 50
            
            # Execute setup steps
            setup_database_and_schemas(session)
            setup_warehouses(session)
            setup_pipeline_infrastructure(session)
            
            # Note: Data generation removed - see individual demos for data setup
            # Example: demos/factset_etf_iceberg/ includes its own data initialization
            
            logger.info("\n" + "=" * 80)
            logger.info("⚠️  Note: This main setup creates infrastructure only")
            logger.info("   For complete demos with data, see:")
            logger.info("   - demos/factset_etf_iceberg/ (FACTSET ETF Constituents)")
            logger.info("=" * 80 + "\n")
            
            # Removed: generate_demo_data, transform_data, validate_data_quality
            # These are demo-specific and included in individual demo folders
            
            # Keep these for general setup
            # setup_dynamic_tables(session)  # Commented out - demo-specific
            # setup_data_sharing(session)    # Commented out - demo-specific
            
            # Validate
            logger.info("\n" + "=" * 80)
            logger.info("🎉 Setup Complete! Running validation...")
            logger.info("=" * 80 + "\n")
            validate_setup(session)
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ DATA ENGINEERING DEMO READY!")
            logger.info("=" * 80)
            logger.info(f"📊 Database: {DataEngDemoConfig.DATABASE}")
            logger.info(f"🔗 Data Share: {DataEngDemoConfig.SHARE_NAME}")
            logger.info(f"📖 See docs/demo_script.md for demo delivery guide")
            logger.info("=" * 80)
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        raise
    finally:
        session.close()
        logger.info("🔌 Session closed")


if __name__ == "__main__":
    main()

