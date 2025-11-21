"""
Data Share Monitoring and Usage Analytics
Track data share consumption and access patterns
"""
from snowflake.snowpark import Session
from config import DataEngDemoConfig
from utils.logging_utils import setup_logger, log_step

logger = setup_logger("share_monitoring")


def monitor_share_usage(session: Session, share_name: str = None) -> dict:
    """
    Monitor usage of a data share
    
    Args:
        session: Active Snowpark session
        share_name: Name of the share to monitor
    
    Returns:
        Dictionary with usage statistics
    """
    if share_name is None:
        share_name = DataEngDemoConfig.SHARE_NAME
    
    log_step(logger, f"Monitoring Share Usage: {share_name}", "START")
    
    usage_stats = {
        "share_name": share_name,
        "objects_shared": 0,
        "accounts_with_access": 0,
        "queries_executed": 0
    }
    
    # Count objects in share
    try:
        objects_result = session.sql(f"""
            SHOW GRANTS TO SHARE {share_name}
        """).collect()
        
        usage_stats["objects_shared"] = len(objects_result)
        logger.info(f"Objects shared: {usage_stats['objects_shared']}")
        
    except Exception as e:
        logger.warning(f"Could not retrieve object count: {str(e)}")
    
    # Show accounts with access (demo environment may not have consumer accounts)
    try:
        accounts_result = session.sql(f"""
            SHOW GRANTS OF SHARE {share_name}
        """).collect()
        
        usage_stats["accounts_with_access"] = len(accounts_result)
        logger.info(f"Accounts with access: {usage_stats['accounts_with_access']}")
        
    except Exception as e:
        logger.info("No consumer accounts configured (expected in demo)")
    
    logger.info(f"📊 Share Usage Summary:")
    logger.info(f"   Share Name: {usage_stats['share_name']}")
    logger.info(f"   Objects Shared: {usage_stats['objects_shared']}")
    logger.info(f"   Accounts with Access: {usage_stats['accounts_with_access']}")
    
    log_step(logger, f"Monitoring Share Usage: {share_name}", "COMPLETE")
    
    return usage_stats


def create_share_monitoring_view(session: Session) -> None:
    """
    Create a view to monitor data share access and usage
    
    Args:
        session: Active Snowpark session
    """
    logger.info("Creating share monitoring view...")
    
    database = DataEngDemoConfig.DATABASE
    schema = DataEngDemoConfig.SCHEMA_ANALYTICS
    
    # Note: In a production environment, you would use ACCOUNT_USAGE views
    # For demo purposes, we create a placeholder monitoring structure
    
    monitor_sql = f"""
        CREATE OR REPLACE VIEW {database}.{schema}.SHARE_MONITORING AS
        SELECT 
            CURRENT_TIMESTAMP() AS MONITORING_TIMESTAMP,
            '{DataEngDemoConfig.SHARE_NAME}' AS SHARE_NAME,
            'ACTIVE' AS SHARE_STATUS,
            'Demo monitoring - use ACCOUNT_USAGE in production' AS NOTE
    """
    
    session.sql(monitor_sql).collect()
    logger.info(f"✅ Monitoring view created: {database}.{schema}.SHARE_MONITORING")


def show_share_info(session: Session, share_name: str = None) -> None:
    """
    Display comprehensive information about a share
    
    Args:
        session: Active Snowpark session
        share_name: Name of the share
    """
    if share_name is None:
        share_name = DataEngDemoConfig.SHARE_NAME
    
    logger.info(f"📋 Share Information: {share_name}")
    logger.info("=" * 80)
    
    # Show basic share info
    try:
        share_info = session.sql(f"SHOW SHARES LIKE '{share_name}'").collect()
        if share_info:
            for row in share_info:
                logger.info(f"Share Name: {row.get('name', 'N/A')}")
                logger.info(f"Kind: {row.get('kind', 'N/A')}")
                logger.info(f"Database: {row.get('database_name', 'N/A')}")
                logger.info(f"Owner: {row.get('owner', 'N/A')}")
                logger.info(f"Comment: {row.get('comment', 'N/A')}")
    except Exception as e:
        logger.warning(f"Could not retrieve share info: {str(e)}")
    
    logger.info("-" * 80)
    
    # Show objects in share
    try:
        logger.info("Objects in Share:")
        objects = session.sql(f"SHOW GRANTS TO SHARE {share_name}").collect()
        for obj in objects:
            logger.info(f"  - {obj.get('granted_on', 'N/A')}: {obj.get('name', 'N/A')}")
    except Exception as e:
        logger.warning(f"Could not retrieve objects: {str(e)}")
    
    logger.info("=" * 80)


if __name__ == "__main__":
    from utils.snowpark_session import get_snowpark_session, set_context
    
    session = get_snowpark_session()
    set_context(session, database=DataEngDemoConfig.DATABASE)
    
    # Monitor the demo share
    usage_stats = monitor_share_usage(session)
    print(f"\nShare '{usage_stats['share_name']}' has {usage_stats['objects_shared']} objects")
    
    # Show detailed info
    show_share_info(session)
    
    session.close()

