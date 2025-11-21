"""
Data Ingestion Pipeline
Handles multi-format data loading from stages
"""
from snowflake.snowpark import Session
from config import DataEngDemoConfig
from utils.logging_utils import setup_logger, log_step

logger = setup_logger("ingestion")


def setup_stages_and_formats(session: Session) -> None:
    """
    Create internal stages and file formats for data ingestion
    
    Args:
        session: Active Snowpark session
    
    Creates:
        - Internal stages for CSV, JSON, and Parquet files
        - Corresponding file formats
    """
    log_step(logger, "Stage and Format Setup", "START")
    
    database = DataEngDemoConfig.DATABASE
    schema = DataEngDemoConfig.SCHEMA_RAW
    
    # Create CSV stage and format
    logger.info("Creating CSV stage and format...")
    session.sql(f"""
        CREATE STAGE IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.STAGE_CSV}
        COMMENT = 'Internal stage for CSV file ingestion'
    """).collect()
    
    session.sql(f"""
        CREATE FILE FORMAT IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.FILE_FORMAT_CSV}
        TYPE = 'CSV'
        FIELD_DELIMITER = ','
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF = ('NULL', 'null', '')
        EMPTY_FIELD_AS_NULL = TRUE
        COMPRESSION = AUTO
        COMMENT = 'CSV file format with header'
    """).collect()
    
    # Create JSON stage and format
    logger.info("Creating JSON stage and format...")
    session.sql(f"""
        CREATE STAGE IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.STAGE_JSON}
        COMMENT = 'Internal stage for JSON file ingestion'
    """).collect()
    
    session.sql(f"""
        CREATE FILE FORMAT IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.FILE_FORMAT_JSON}
        TYPE = 'JSON'
        COMPRESSION = AUTO
        STRIP_OUTER_ARRAY = TRUE
        COMMENT = 'JSON file format'
    """).collect()
    
    # Create Parquet stage and format
    logger.info("Creating Parquet stage and format...")
    session.sql(f"""
        CREATE STAGE IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.STAGE_PARQUET}
        COMMENT = 'Internal stage for Parquet file ingestion'
    """).collect()
    
    session.sql(f"""
        CREATE FILE FORMAT IF NOT EXISTS {database}.{schema}.{DataEngDemoConfig.FILE_FORMAT_PARQUET}
        TYPE = 'PARQUET'
        COMPRESSION = AUTO
        COMMENT = 'Parquet file format'
    """).collect()
    
    logger.info("✅ All stages and formats created successfully")
    log_step(logger, "Stage and Format Setup", "COMPLETE")


def load_data_from_stage(session: Session, stage_name: str, file_format: str,
                        target_table: str, file_pattern: str = None) -> int:
    """
    Load data from a stage into a table using COPY INTO
    
    Args:
        session: Active Snowpark session
        stage_name: Name of the stage (e.g., '@CSV_STAGE')
        file_format: Name of the file format
        target_table: Fully qualified target table name
        file_pattern: Optional file pattern to match (e.g., '.*transactions.*')
    
    Returns:
        Number of rows loaded
    
    Example:
        >>> rows = load_data_from_stage(
        ...     session,
        ...     '@CSV_STAGE',
        ...     'CSV_FORMAT',
        ...     'DATA_ENG_DEMO.STAGING.TRANSACTIONS',
        ...     '.*transactions.*'
        ... )
    """
    log_step(logger, f"Loading data into {target_table}", "START")
    
    # Build COPY INTO statement
    pattern_clause = f"PATTERN = '{file_pattern}'" if file_pattern else ""
    
    copy_sql = f"""
        COPY INTO {target_table}
        FROM {stage_name}
        FILE_FORMAT = (FORMAT_NAME = '{file_format}')
        {pattern_clause}
        ON_ERROR = 'CONTINUE'
        PURGE = FALSE
    """
    
    logger.info(f"Executing COPY INTO from {stage_name}...")
    logger.info(f"SQL: {copy_sql}")
    
    try:
        result = session.sql(copy_sql).collect()
        
        # Parse results
        rows_loaded = sum(row['ROWS_LOADED'] for row in result if 'ROWS_LOADED' in row)
        rows_parsed = sum(row['ROWS_PARSED'] for row in result if 'ROWS_PARSED' in row)
        errors = sum(row['ERRORS_SEEN'] for row in result if 'ERRORS_SEEN' in result)
        
        logger.info(f"✅ Data load completed:")
        logger.info(f"   Rows parsed: {rows_parsed:,}")
        logger.info(f"   Rows loaded: {rows_loaded:,}")
        logger.info(f"   Errors: {errors:,}")
        
        if errors > 0:
            logger.warning(f"⚠️  {errors} errors encountered during load")
        
        log_step(logger, f"Loading data into {target_table}", "COMPLETE")
        return rows_loaded
        
    except Exception as e:
        logger.error(f"❌ Failed to load data: {str(e)}")
        log_step(logger, f"Loading data into {target_table}", "FAILED")
        raise


def create_snowpipe(session: Session, pipe_name: str, stage_name: str,
                   file_format: str, target_table: str) -> None:
    """
    Create a Snowpipe for continuous data loading
    
    Args:
        session: Active Snowpark session
        pipe_name: Name for the pipe
        stage_name: Source stage name
        file_format: File format name
        target_table: Target table for loading
    
    Example:
        >>> create_snowpipe(
        ...     session,
        ...     'TRANSACTIONS_PIPE',
        ...     '@CSV_STAGE',
        ...     'CSV_FORMAT',
        ...     'DATA_ENG_DEMO.RAW_DATA.TRANSACTIONS'
        ... )
    """
    log_step(logger, f"Creating Snowpipe {pipe_name}", "START")
    
    database = DataEngDemoConfig.DATABASE
    schema = DataEngDemoConfig.SCHEMA_RAW
    
    pipe_sql = f"""
        CREATE OR REPLACE PIPE {database}.{schema}.{pipe_name}
        AUTO_INGEST = FALSE
        COMMENT = 'Continuous loading pipe for {target_table}'
        AS
        COPY INTO {target_table}
        FROM {stage_name}
        FILE_FORMAT = (FORMAT_NAME = '{file_format}')
        ON_ERROR = 'CONTINUE'
    """
    
    logger.info(f"Creating pipe: {pipe_name}")
    session.sql(pipe_sql).collect()
    
    logger.info(f"✅ Snowpipe {pipe_name} created successfully")
    log_step(logger, f"Creating Snowpipe {pipe_name}", "COMPLETE")


def refresh_snowpipe(session: Session, pipe_name: str) -> None:
    """
    Manually refresh a Snowpipe to process files in stage
    
    Args:
        session: Active Snowpark session
        pipe_name: Fully qualified pipe name
    
    Example:
        >>> refresh_snowpipe(session, 'DATA_ENG_DEMO.RAW_DATA.TRANSACTIONS_PIPE')
    """
    logger.info(f"Refreshing Snowpipe: {pipe_name}")
    
    refresh_sql = f"ALTER PIPE {pipe_name} REFRESH"
    session.sql(refresh_sql).collect()
    
    logger.info(f"✅ Pipe refreshed successfully")


if __name__ == "__main__":
    from utils.snowpark_session import get_snowpark_session, set_context
    
    session = get_snowpark_session()
    set_context(session, database=DataEngDemoConfig.DATABASE, schema=DataEngDemoConfig.SCHEMA_RAW)
    
    setup_stages_and_formats(session)
    
    session.close()

