"""
Master Configuration for Snowflake Data Engineering Demo
Combines ETL/ELT Pipelines, Data Sharing, and Dynamic Tables
"""
from datetime import datetime, timedelta


class DataEngDemoConfig:
    """Central configuration for all data engineering demo scenarios"""
    
    # ============================================================================
    # SNOWFLAKE CONNECTION
    # ============================================================================
    SNOWFLAKE_CONNECTION_NAME = "demo_connection"
    
    # ============================================================================
    # DATABASE & SCHEMA ARCHITECTURE
    # ============================================================================
    DATABASE = "DATA_ENG_DEMO"
    
    # Main schemas
    SCHEMA_RAW = "RAW_DATA"              # Landing zone for raw data
    SCHEMA_STAGING = "STAGING"            # Intermediate transformations
    SCHEMA_CURATED = "CURATED"            # Clean, validated data
    SCHEMA_ANALYTICS = "ANALYTICS"        # Business-ready analytics tables
    SCHEMA_SHARED = "SHARED_DATA"         # Data for external sharing
    
    # ============================================================================
    # WAREHOUSE CONFIGURATION
    # ============================================================================
    WAREHOUSE_LOAD = "DATA_ENG_LOAD_WH"      # For data ingestion (Medium)
    WAREHOUSE_TRANSFORM = "DATA_ENG_XFORM_WH" # For transformations (Large)
    WAREHOUSE_ANALYTICS = "DATA_ENG_ANALYTICS_WH" # For queries (X-Small)
    
    # ============================================================================
    # DEMO SCENARIOS
    # ============================================================================
    # Scenario 1: ETL/ELT Pipeline
    PIPELINE_SOURCE_FORMATS = ["CSV", "JSON", "PARQUET"]
    PIPELINE_BATCH_SIZE = 1000
    
    # Scenario 2: Data Sharing
    SHARE_NAME = "DATA_ENG_CUSTOMER_SHARE"
    SHARE_DESCRIPTION = "Curated sales and customer analytics for partners"
    
    # Scenario 3: Dynamic Tables & Incremental Processing
    DYNAMIC_TABLE_REFRESH = "1 MINUTE"  # Refresh interval for dynamic tables
    MATERIALIZED_VIEW_REFRESH = "5 MINUTES"
    
    # ============================================================================
    # DATA GENERATION PARAMETERS
    # ============================================================================
    # Time ranges (dynamic)
    HISTORICAL_DAYS = 365  # 1 year of historical data
    FORECAST_DAYS = 90     # 3 months of forecasted data
    
    @staticmethod
    def get_start_date() -> str:
        """Get dynamic start date (1 year ago)"""
        start = datetime.now() - timedelta(days=DataEngDemoConfig.HISTORICAL_DAYS)
        return start.strftime('%Y-%m-%d')
    
    @staticmethod
    def get_end_date() -> str:
        """Get dynamic end date (today)"""
        return datetime.now().strftime('%Y-%m-%d')
    
    # Data volumes
    NUM_CUSTOMERS = 1000
    NUM_PRODUCTS = 200
    NUM_STORES = 50
    NUM_TRANSACTIONS_PER_DAY = 500
    
    # ============================================================================
    # ETL/ELT CONFIGURATION
    # ============================================================================
    # Stage names for file ingestion
    STAGE_CSV = "CSV_STAGE"
    STAGE_JSON = "JSON_STAGE"
    STAGE_PARQUET = "PARQUET_STAGE"
    
    # File format names
    FILE_FORMAT_CSV = "CSV_FORMAT"
    FILE_FORMAT_JSON = "JSON_FORMAT"
    FILE_FORMAT_PARQUET = "PARQUET_FORMAT"
    
    # Pipe names for continuous loading
    PIPE_TRANSACTIONS = "TRANSACTIONS_PIPE"
    PIPE_CUSTOMER_EVENTS = "CUSTOMER_EVENTS_PIPE"
    
    # ============================================================================
    # DATA QUALITY RULES
    # ============================================================================
    DATA_QUALITY_CHECKS = [
        "NULL_CHECK",
        "DUPLICATE_CHECK",
        "RANGE_CHECK",
        "REFERENTIAL_INTEGRITY",
        "FORMAT_VALIDATION"
    ]
    
    QUALITY_THRESHOLD_PASS = 0.95  # 95% pass rate required
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    CLUSTERING_KEYS = {
        "transactions": ["transaction_date", "store_id"],
        "customer_events": ["event_date", "customer_id"],
        "products": ["category", "brand"]
    }
    
    # ============================================================================
    # MONITORING & OBSERVABILITY
    # ============================================================================
    ENABLE_QUERY_TAGGING = True
    ENABLE_RESOURCE_MONITORS = True
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # ============================================================================
    # DEMO METADATA
    # ============================================================================
    DEMO_VERSION = "1.0.0"
    DEMO_CREATED_DATE = "2025-11-18"
    DEMO_DESCRIPTION = "Comprehensive Data Engineering Demo: ETL/ELT, Data Sharing, Dynamic Tables"

