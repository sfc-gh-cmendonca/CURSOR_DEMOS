"""
Snowpark Session Management
Centralized session creation using connections.toml
"""
from snowflake.snowpark import Session
import argparse
from config import DataEngDemoConfig


def get_snowpark_session(connection_name: str = None) -> Session:
    """
    Create Snowpark session using connections.toml
    
    Args:
        connection_name: Name of connection in connections.toml
                        If None, uses command-line arg or default from config
    
    Returns:
        Session: Active Snowpark session
    
    Example:
        >>> session = get_snowpark_session("demo_connection")
        >>> result = session.sql("SELECT CURRENT_VERSION()").collect()
    """
    if not connection_name:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--connection_name",
            default=DataEngDemoConfig.SNOWFLAKE_CONNECTION_NAME,
            help="Snowflake connection name from connections.toml"
        )
        args, _ = parser.parse_known_args()
        connection_name = args.connection_name
    
    print(f"🔌 Connecting to Snowflake using connection: {connection_name}")
    
    try:
        session = Session.builder.config("connection_name", connection_name).create()
        print(f"✅ Connected successfully to {session.get_current_account()}")
        print(f"📍 Current database: {session.get_current_database()}")
        print(f"📍 Current schema: {session.get_current_schema()}")
        return session
    except Exception as e:
        print(f"❌ Failed to create Snowpark session: {str(e)}")
        print(f"💡 Make sure connections.toml has entry for '{connection_name}'")
        raise


def set_context(session: Session, database: str = None, schema: str = None, 
                warehouse: str = None) -> None:
    """
    Set session context (database, schema, warehouse)
    
    Args:
        session: Active Snowpark session
        database: Database name to use
        schema: Schema name to use
        warehouse: Warehouse name to use
    
    Example:
        >>> set_context(session, database="DATA_ENG_DEMO", schema="RAW_DATA")
    """
    if database:
        session.sql(f"USE DATABASE {database}").collect()
        print(f"📍 Using database: {database}")
    
    if schema:
        session.sql(f"USE SCHEMA {schema}").collect()
        print(f"📍 Using schema: {schema}")
    
    if warehouse:
        session.sql(f"USE WAREHOUSE {warehouse}").collect()
        print(f"🏭 Using warehouse: {warehouse}")


def enable_query_tagging(session: Session, tag: str) -> None:
    """
    Enable query tagging for monitoring and cost attribution
    
    Args:
        session: Active Snowpark session
        tag: Tag to apply to queries
    
    Example:
        >>> enable_query_tagging(session, "DATA_ENG_DEMO_LOAD")
    """
    session.sql(f"ALTER SESSION SET QUERY_TAG = '{tag}'").collect()
    print(f"🏷️  Query tag set: {tag}")

