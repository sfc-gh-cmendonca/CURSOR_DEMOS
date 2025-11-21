"""
Data Sharing Management
Create and manage Snowflake data shares
"""
from snowflake.snowpark import Session
from typing import List
from config import DataEngDemoConfig
from utils.logging_utils import setup_logger, log_step

logger = setup_logger("data_sharing")


def create_data_share(session: Session, share_name: str = None, 
                     comment: str = None) -> None:
    """
    Create a Snowflake data share
    
    Args:
        session: Active Snowpark session
        share_name: Name for the share (uses config default if None)
        comment: Description of the share
    
    Example:
        >>> create_data_share(session, "CUSTOMER_ANALYTICS_SHARE", 
        ...                  "Curated customer analytics for partners")
    """
    if share_name is None:
        share_name = DataEngDemoConfig.SHARE_NAME
    
    if comment is None:
        comment = DataEngDemoConfig.SHARE_DESCRIPTION
    
    log_step(logger, f"Creating Data Share: {share_name}", "START")
    
    # Create share
    create_sql = f"""
        CREATE SHARE IF NOT EXISTS {share_name}
        COMMENT = '{comment}'
    """
    
    logger.info(f"Creating share: {share_name}")
    session.sql(create_sql).collect()
    
    logger.info(f"✅ Share {share_name} created successfully")
    log_step(logger, f"Creating Data Share: {share_name}", "COMPLETE")


def add_objects_to_share(session: Session, share_name: str, 
                        database: str, schema: str, 
                        tables: List[str] = None, 
                        views: List[str] = None) -> None:
    """
    Add database objects to an existing share
    
    Args:
        session: Active Snowpark session
        share_name: Name of the share
        database: Database to share from
        schema: Schema to share from
        tables: List of table names to share
        views: List of view names to share
    
    Example:
        >>> add_objects_to_share(
        ...     session, 
        ...     "CUSTOMER_ANALYTICS_SHARE",
        ...     "DATA_ENG_DEMO",
        ...     "SHARED_DATA",
        ...     tables=["CUSTOMER_SUMMARY", "SALES_METRICS"]
        ... )
    """
    log_step(logger, f"Adding Objects to Share: {share_name}", "START")
    
    # Grant usage on database
    logger.info(f"Granting database usage: {database}")
    session.sql(f"GRANT USAGE ON DATABASE {database} TO SHARE {share_name}").collect()
    
    # Grant usage on schema
    logger.info(f"Granting schema usage: {schema}")
    session.sql(f"GRANT USAGE ON SCHEMA {database}.{schema} TO SHARE {share_name}").collect()
    
    # Add tables
    if tables:
        logger.info(f"Adding {len(tables)} tables to share...")
        for table in tables:
            logger.info(f"  - {table}")
            session.sql(f"""
                GRANT SELECT ON TABLE {database}.{schema}.{table} 
                TO SHARE {share_name}
            """).collect()
    
    # Add views
    if views:
        logger.info(f"Adding {len(views)} views to share...")
        for view in views:
            logger.info(f"  - {view}")
            session.sql(f"""
                GRANT SELECT ON VIEW {database}.{schema}.{view} 
                TO SHARE {share_name}
            """).collect()
    
    logger.info(f"✅ Objects added to share {share_name} successfully")
    log_step(logger, f"Adding Objects to Share: {share_name}", "COMPLETE")


def grant_share_to_account(session: Session, share_name: str, 
                          account_identifier: str) -> None:
    """
    Grant a share to another Snowflake account
    
    Args:
        session: Active Snowpark session
        share_name: Name of the share
        account_identifier: Target account identifier (e.g., 'AB12345.US-EAST-1')
    
    Note:
        Requires ACCOUNTADMIN role in demo environment
        In production, use proper account locators
    
    Example:
        >>> grant_share_to_account(session, "CUSTOMER_ANALYTICS_SHARE", 
        ...                       "XY98765.US-WEST-2")
    """
    log_step(logger, f"Granting Share to Account", "START")
    
    logger.info(f"Granting share {share_name} to account {account_identifier}")
    
    grant_sql = f"""
        ALTER SHARE {share_name} 
        ADD ACCOUNTS = {account_identifier}
    """
    
    try:
        session.sql(grant_sql).collect()
        logger.info(f"✅ Share granted to account {account_identifier}")
    except Exception as e:
        logger.warning(f"⚠️  Could not grant share (demo environment): {str(e)}")
        logger.info("💡 In production, use actual account identifiers")
    
    log_step(logger, f"Granting Share to Account", "COMPLETE")


def list_share_objects(session: Session, share_name: str) -> None:
    """
    List all objects in a share
    
    Args:
        session: Active Snowpark session
        share_name: Name of the share to inspect
    """
    logger.info(f"Listing objects in share: {share_name}")
    
    objects_sql = f"SHOW GRANTS TO SHARE {share_name}"
    
    try:
        results = session.sql(objects_sql).collect()
        
        if results:
            logger.info(f"📋 Objects in share {share_name}:")
            for row in results:
                logger.info(f"   - {row['granted_on']} {row['name']}: {row['privilege']}")
        else:
            logger.info(f"No objects currently in share {share_name}")
    
    except Exception as e:
        logger.warning(f"Could not list share objects: {str(e)}")


def create_secure_view_for_sharing(session: Session, view_name: str, 
                                   base_table: str, columns: List[str],
                                   filter_condition: str = None) -> None:
    """
    Create a secure view for data sharing with column and row-level filtering
    
    Args:
        session: Active Snowpark session
        view_name: Name for the secure view
        base_table: Fully qualified base table name
        columns: List of columns to include
        filter_condition: Optional WHERE clause for row filtering
    
    Example:
        >>> create_secure_view_for_sharing(
        ...     session,
        ...     "SHARED_CUSTOMER_SUMMARY",
        ...     "DATA_ENG_DEMO.CURATED.CUSTOMERS",
        ...     ["CUSTOMER_ID", "CUSTOMER_SEGMENT", "LIFETIME_VALUE"],
        ...     "IS_ACTIVE = TRUE"
        ... )
    """
    logger.info(f"Creating secure view: {view_name}")
    
    columns_str = ", ".join(columns)
    where_clause = f"WHERE {filter_condition}" if filter_condition else ""
    
    view_sql = f"""
        CREATE OR REPLACE SECURE VIEW {view_name} AS
        SELECT {columns_str}
        FROM {base_table}
        {where_clause}
    """
    
    session.sql(view_sql).collect()
    logger.info(f"✅ Secure view {view_name} created")


def setup_demo_share(session: Session) -> None:
    """
    Set up complete demo data share with curated analytics
    
    Args:
        session: Active Snowpark session
    
    Creates:
        - Secure views in SHARED_DATA schema
        - Data share with analytics objects
    """
    log_step(logger, "Setting Up Demo Data Share", "START")
    
    share_name = DataEngDemoConfig.SHARE_NAME
    database = DataEngDemoConfig.DATABASE
    shared_schema = DataEngDemoConfig.SCHEMA_SHARED
    
    # Create shared schema if not exists
    logger.info(f"Creating schema: {shared_schema}")
    session.sql(f"""
        CREATE SCHEMA IF NOT EXISTS {database}.{shared_schema}
        COMMENT = 'Shared data for external partners'
    """).collect()
    
    # Create secure views for sharing
    logger.info("Creating secure views for sharing...")
    
    # Customer summary (no PII)
    session.sql(f"""
        CREATE OR REPLACE SECURE VIEW {database}.{shared_schema}.CUSTOMER_SUMMARY AS
        SELECT 
            CUSTOMER_ID,
            CUSTOMER_SEGMENT,
            LOYALTY_TIER,
            LIFETIME_VALUE,
            CUSTOMER_AGE_DAYS,
            CUSTOMER_STATUS
        FROM {database}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS
        WHERE IS_ACTIVE = TRUE
    """).collect()
    
    # Sales metrics (aggregated)
    session.sql(f"""
        CREATE OR REPLACE SECURE VIEW {database}.{shared_schema}.SALES_METRICS AS
        SELECT 
            TRANSACTION_DATE,
            TRANSACTION_YEAR,
            TRANSACTION_QUARTER,
            TRANSACTION_MONTH,
            PRODUCT_CATEGORY,
            CHANNEL,
            COUNT(DISTINCT TRANSACTION_ID) AS TRANSACTION_COUNT,
            SUM(TOTAL_AMOUNT) AS TOTAL_REVENUE,
            AVG(TOTAL_AMOUNT) AS AVG_TRANSACTION_VALUE
        FROM {database}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS
        WHERE DATA_QUALITY_FLAG = TRUE
        GROUP BY 
            TRANSACTION_DATE, TRANSACTION_YEAR, TRANSACTION_QUARTER,
            TRANSACTION_MONTH, PRODUCT_CATEGORY, CHANNEL
    """).collect()
    
    # Product performance
    session.sql(f"""
        CREATE OR REPLACE SECURE VIEW {database}.{shared_schema}.PRODUCT_PERFORMANCE AS
        SELECT 
            p.PRODUCT_ID,
            p.PRODUCT_NAME,
            p.CATEGORY,
            p.SUBCATEGORY,
            p.BRAND,
            p.PRICE_TIER,
            COUNT(t.TRANSACTION_ID) AS UNITS_SOLD,
            SUM(t.TOTAL_AMOUNT) AS TOTAL_REVENUE
        FROM {database}.{DataEngDemoConfig.SCHEMA_CURATED}.PRODUCTS p
        LEFT JOIN {database}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS t
            ON p.PRODUCT_ID = t.PRODUCT_ID
        WHERE p.IS_ACTIVE = TRUE
        GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME, p.CATEGORY, 
                 p.SUBCATEGORY, p.BRAND, p.PRICE_TIER
    """).collect()
    
    # Create the share
    create_data_share(session, share_name)
    
    # Add views to share
    add_objects_to_share(
        session,
        share_name,
        database,
        shared_schema,
        views=["CUSTOMER_SUMMARY", "SALES_METRICS", "PRODUCT_PERFORMANCE"]
    )
    
    # List what's in the share
    list_share_objects(session, share_name)
    
    logger.info(f"✅ Demo data share setup complete")
    log_step(logger, "Setting Up Demo Data Share", "COMPLETE")


if __name__ == "__main__":
    from utils.snowpark_session import get_snowpark_session, set_context
    
    session = get_snowpark_session()
    set_context(session, database=DataEngDemoConfig.DATABASE)
    
    setup_demo_share(session)
    
    session.close()

