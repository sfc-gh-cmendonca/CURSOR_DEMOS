"""
Data Transformation Pipeline
Handles data transformations from raw to curated layers
"""
from snowflake.snowpark import Session
from config import DataEngDemoConfig
from utils.logging_utils import setup_logger, log_step

logger = setup_logger("transformation")


def transform_to_curated(session: Session) -> None:
    """
    Transform data from STAGING to CURATED schema
    Applies business rules, enrichments, and data quality improvements
    
    Args:
        session: Active Snowpark session
    
    Creates curated versions of:
        - CUSTOMERS (with calculated fields)
        - PRODUCTS (with enriched attributes)
        - TRANSACTIONS (with derived metrics)
    """
    log_step(logger, "Data Transformation to Curated", "START")
    
    _transform_customers(session)
    _transform_products(session)
    _transform_transactions(session)
    
    log_step(logger, "Data Transformation to Curated", "COMPLETE")


def _transform_customers(session: Session) -> None:
    """Transform and enrich customer dimension"""
    logger.info("Transforming customers to curated layer...")
    
    transform_sql = f"""
        CREATE OR REPLACE TABLE {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS AS
        SELECT 
            CUSTOMER_ID,
            FIRST_NAME,
            LAST_NAME,
            UPPER(FIRST_NAME || ' ' || LAST_NAME) AS FULL_NAME,
            LOWER(EMAIL) AS EMAIL,
            PHONE,
            ADDRESS,
            CITY,
            STATE,
            ZIP_CODE,
            COUNTRY,
            CUSTOMER_SEGMENT,
            LOYALTY_TIER,
            ACCOUNT_CREATED_DATE,
            LIFETIME_VALUE,
            IS_ACTIVE,
            LAST_PURCHASE_DATE,
            -- Calculated fields
            DATEDIFF('day', ACCOUNT_CREATED_DATE, CURRENT_DATE()) AS CUSTOMER_AGE_DAYS,
            DATEDIFF('day', LAST_PURCHASE_DATE, CURRENT_DATE()) AS DAYS_SINCE_LAST_PURCHASE,
            CASE 
                WHEN DATEDIFF('day', LAST_PURCHASE_DATE, CURRENT_DATE()) <= 30 THEN 'Highly Active'
                WHEN DATEDIFF('day', LAST_PURCHASE_DATE, CURRENT_DATE()) <= 90 THEN 'Active'
                WHEN DATEDIFF('day', LAST_PURCHASE_DATE, CURRENT_DATE()) <= 180 THEN 'At Risk'
                ELSE 'Inactive'
            END AS CUSTOMER_STATUS,
            -- Data quality flags
            CASE 
                WHEN EMAIL IS NULL OR EMAIL = '' THEN FALSE
                WHEN PHONE IS NULL OR PHONE = '' THEN FALSE
                ELSE TRUE
            END AS HAS_COMPLETE_CONTACT_INFO,
            CURRENT_TIMESTAMP() AS CURATED_TIMESTAMP
        FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_RAW}.CUSTOMERS
        WHERE CUSTOMER_ID IS NOT NULL
    """
    
    session.sql(transform_sql).collect()
    
    row_count = session.table(
        f"{DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS"
    ).count()
    
    logger.info(f"✅ Curated CUSTOMERS created with {row_count:,} rows")


def _transform_products(session: Session) -> None:
    """Transform and enrich product dimension"""
    logger.info("Transforming products to curated layer...")
    
    transform_sql = f"""
        CREATE OR REPLACE TABLE {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.PRODUCTS AS
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            CATEGORY,
            SUBCATEGORY,
            BRAND,
            UNIT_PRICE,
            COST,
            MARGIN_PCT,
            IN_STOCK,
            STOCK_QUANTITY,
            SUPPLIER_ID,
            IS_ACTIVE,
            -- Calculated fields
            UNIT_PRICE - COST AS PROFIT_PER_UNIT,
            CASE 
                WHEN UNIT_PRICE < 50 THEN 'Low'
                WHEN UNIT_PRICE < 200 THEN 'Medium'
                WHEN UNIT_PRICE < 500 THEN 'High'
                ELSE 'Premium'
            END AS PRICE_TIER,
            CASE 
                WHEN STOCK_QUANTITY = 0 THEN 'Out of Stock'
                WHEN STOCK_QUANTITY < 50 THEN 'Low Stock'
                WHEN STOCK_QUANTITY < 200 THEN 'Adequate'
                ELSE 'Well Stocked'
            END AS STOCK_STATUS,
            -- Data quality
            CASE 
                WHEN PRODUCT_NAME IS NULL OR PRODUCT_NAME = '' THEN FALSE
                WHEN UNIT_PRICE IS NULL OR UNIT_PRICE <= 0 THEN FALSE
                WHEN COST IS NULL OR COST < 0 THEN FALSE
                ELSE TRUE
            END AS DATA_QUALITY_FLAG,
            CURRENT_TIMESTAMP() AS CURATED_TIMESTAMP
        FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_RAW}.PRODUCTS
        WHERE PRODUCT_ID IS NOT NULL
    """
    
    session.sql(transform_sql).collect()
    
    row_count = session.table(
        f"{DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.PRODUCTS"
    ).count()
    
    logger.info(f"✅ Curated PRODUCTS created with {row_count:,} rows")


def _transform_transactions(session: Session) -> None:
    """Transform and enrich transaction fact table"""
    logger.info("Transforming transactions to curated layer...")
    
    transform_sql = f"""
        CREATE OR REPLACE TABLE {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS AS
        SELECT 
            t.TRANSACTION_ID,
            t.TRANSACTION_DATE,
            t.TRANSACTION_TIMESTAMP,
            t.CUSTOMER_ID,
            t.STORE_ID,
            t.PRODUCT_ID,
            t.QUANTITY,
            t.UNIT_PRICE,
            t.DISCOUNT_PCT,
            t.TOTAL_AMOUNT,
            t.PAYMENT_METHOD,
            t.CHANNEL,
            -- Temporal dimensions
            YEAR(t.TRANSACTION_DATE) AS TRANSACTION_YEAR,
            QUARTER(t.TRANSACTION_DATE) AS TRANSACTION_QUARTER,
            MONTH(t.TRANSACTION_DATE) AS TRANSACTION_MONTH,
            DAYOFWEEK(t.TRANSACTION_DATE) AS TRANSACTION_DAY_OF_WEEK,
            HOUR(t.TRANSACTION_TIMESTAMP) AS TRANSACTION_HOUR,
            CASE 
                WHEN DAYOFWEEK(t.TRANSACTION_DATE) IN (0, 6) THEN TRUE
                ELSE FALSE
            END AS IS_WEEKEND,
            -- Calculated metrics
            t.UNIT_PRICE * t.QUANTITY AS SUBTOTAL,
            (t.UNIT_PRICE * t.QUANTITY * t.DISCOUNT_PCT / 100) AS DISCOUNT_AMOUNT,
            t.TOTAL_AMOUNT / t.QUANTITY AS EFFECTIVE_PRICE_PER_UNIT,
            -- Enrichment from dimensions
            c.CUSTOMER_SEGMENT,
            c.LOYALTY_TIER,
            p.CATEGORY AS PRODUCT_CATEGORY,
            p.BRAND AS PRODUCT_BRAND,
            p.COST AS PRODUCT_COST,
            -- Profitability
            t.TOTAL_AMOUNT - (p.COST * t.QUANTITY) AS TRANSACTION_PROFIT,
            -- Data quality
            CASE 
                WHEN t.CUSTOMER_ID IS NULL THEN FALSE
                WHEN t.PRODUCT_ID IS NULL THEN FALSE
                WHEN t.TOTAL_AMOUNT IS NULL OR t.TOTAL_AMOUNT <= 0 THEN FALSE
                WHEN t.QUANTITY IS NULL OR t.QUANTITY <= 0 THEN FALSE
                ELSE TRUE
            END AS DATA_QUALITY_FLAG,
            CURRENT_TIMESTAMP() AS CURATED_TIMESTAMP
        FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_RAW}.TRANSACTIONS t
        LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS c
            ON t.CUSTOMER_ID = c.CUSTOMER_ID
        LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.PRODUCTS p
            ON t.PRODUCT_ID = p.PRODUCT_ID
        WHERE t.TRANSACTION_ID IS NOT NULL
    """
    
    session.sql(transform_sql).collect()
    
    row_count = session.table(
        f"{DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS"
    ).count()
    
    logger.info(f"✅ Curated TRANSACTIONS created with {row_count:,} rows")


def create_aggregated_views(session: Session) -> None:
    """
    Create aggregated analytical views in ANALYTICS schema
    """
    log_step(logger, "Creating Analytical Views", "START")
    
    # Daily sales summary
    logger.info("Creating daily sales summary view...")
    session.sql(f"""
        CREATE OR REPLACE VIEW {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_ANALYTICS}.DAILY_SALES_SUMMARY AS
        SELECT 
            TRANSACTION_DATE,
            COUNT(DISTINCT TRANSACTION_ID) AS TRANSACTION_COUNT,
            COUNT(DISTINCT CUSTOMER_ID) AS UNIQUE_CUSTOMERS,
            SUM(TOTAL_AMOUNT) AS TOTAL_REVENUE,
            SUM(TRANSACTION_PROFIT) AS TOTAL_PROFIT,
            AVG(TOTAL_AMOUNT) AS AVG_TRANSACTION_VALUE,
            SUM(CASE WHEN CHANNEL = 'Online' THEN TOTAL_AMOUNT ELSE 0 END) AS ONLINE_REVENUE,
            SUM(CASE WHEN CHANNEL = 'In-Store' THEN TOTAL_AMOUNT ELSE 0 END) AS INSTORE_REVENUE,
            SUM(CASE WHEN CHANNEL = 'Mobile App' THEN TOTAL_AMOUNT ELSE 0 END) AS MOBILE_REVENUE
        FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS
        WHERE DATA_QUALITY_FLAG = TRUE
        GROUP BY TRANSACTION_DATE
    """).collect()
    
    # Customer lifetime value
    logger.info("Creating customer LTV view...")
    session.sql(f"""
        CREATE OR REPLACE VIEW {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_ANALYTICS}.CUSTOMER_LTV AS
        SELECT 
            c.CUSTOMER_ID,
            c.FULL_NAME,
            c.CUSTOMER_SEGMENT,
            c.LOYALTY_TIER,
            COUNT(DISTINCT t.TRANSACTION_ID) AS TRANSACTION_COUNT,
            SUM(t.TOTAL_AMOUNT) AS TOTAL_SPENT,
            AVG(t.TOTAL_AMOUNT) AS AVG_TRANSACTION,
            MAX(t.TRANSACTION_DATE) AS LAST_PURCHASE_DATE,
            DATEDIFF('day', MAX(t.TRANSACTION_DATE), CURRENT_DATE()) AS DAYS_SINCE_LAST_PURCHASE
        FROM {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS c
        LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.TRANSACTIONS t
            ON c.CUSTOMER_ID = t.CUSTOMER_ID
        GROUP BY c.CUSTOMER_ID, c.FULL_NAME, c.CUSTOMER_SEGMENT, c.LOYALTY_TIER
    """).collect()
    
    logger.info("✅ Analytical views created successfully")
    log_step(logger, "Creating Analytical Views", "COMPLETE")


if __name__ == "__main__":
    from utils.snowpark_session import get_snowpark_session, set_context
    
    session = get_snowpark_session()
    set_context(session, database=DataEngDemoConfig.DATABASE)
    
    transform_to_curated(session)
    create_aggregated_views(session)
    
    session.close()

