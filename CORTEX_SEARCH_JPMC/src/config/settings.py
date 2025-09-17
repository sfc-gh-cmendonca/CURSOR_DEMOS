"""Configuration settings for the JPMC Cortex Search Lab."""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from loguru import logger


class SnowflakeSettings(BaseSettings):
    """Snowflake connection settings."""
    
    account: str = Field(..., env="SNOWFLAKE_ACCOUNT")
    user: str = Field(..., env="SNOWFLAKE_USER")
    password: Optional[str] = Field(None, env="SNOWFLAKE_PASSWORD")
    role: str = Field("CORTEX_USER_ROLE", env="SNOWFLAKE_ROLE")
    warehouse: str = Field("COMPUTE_WH", env="SNOWFLAKE_WAREHOUSE")
    database: str = Field("JPMC_MARKETS", env="SNOWFLAKE_DATABASE")
    schema: str = Field("MARKET_INTELLIGENCE", env="SNOWFLAKE_SCHEMA")
    
    # Alternative authentication
    private_key_path: Optional[str] = Field(None, env="SNOWFLAKE_PRIVATE_KEY_PATH")
    private_key_passphrase: Optional[str] = Field(None, env="SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")
    authenticator: Optional[str] = Field(None, env="SNOWFLAKE_AUTHENTICATOR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class StreamlitSettings(BaseSettings):
    """Streamlit application settings."""
    
    server_port: int = Field(8501, env="STREAMLIT_SERVER_PORT")
    server_address: str = Field("localhost", env="STREAMLIT_SERVER_ADDRESS")
    theme_base: str = Field("light", env="STREAMLIT_THEME_BASE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ApplicationSettings(BaseSettings):
    """General application settings."""
    
    app_name: str = Field("JPMC Markets Intelligence", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    
    # Security settings
    session_timeout_minutes: int = Field(60, env="SESSION_TIMEOUT_MINUTES")
    max_concurrent_users: int = Field(100, env="MAX_CONCURRENT_USERS")
    
    # Performance settings
    query_timeout_seconds: int = Field(300, env="QUERY_TIMEOUT_SECONDS")
    max_results_per_page: int = Field(1000, env="MAX_RESULTS_PER_PAGE")
    cache_expiry_minutes: int = Field(15, env="CACHE_EXPIRY_MINUTES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CortexSearchSettings(BaseSettings):
    """Cortex Search specific settings."""
    
    embedding_model: str = Field("snowflake-arctic-embed-m", env="EMBEDDING_MODEL")
    search_limit: int = Field(50, env="SEARCH_LIMIT")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class APISettings(BaseSettings):
    """External API settings."""
    
    alpha_vantage_api_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    finnhub_api_key: Optional[str] = Field(None, env="FINNHUB_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instances
snowflake_settings = SnowflakeSettings()
streamlit_settings = StreamlitSettings()
app_settings = ApplicationSettings()
cortex_settings = CortexSearchSettings()
api_settings = APISettings()


def configure_logging() -> None:
    """Configure application logging based on settings."""
    logger.remove()  # Remove default logger
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level=app_settings.log_level,
        format=log_format,
        compression="zip"
    )
    
    if app_settings.debug_mode:
        logger.add(
            lambda msg: print(msg, end=""),
            level="DEBUG",
            format=log_format,
            colorize=True
        )
    else:
        logger.add(
            lambda msg: print(msg, end=""),
            level="INFO",
            format=log_format,
            colorize=True
        )


def validate_settings() -> bool:
    """Validate all required settings are properly configured."""
    try:
        # Check Snowflake credentials
        if not snowflake_settings.account or not snowflake_settings.user:
            logger.error("Missing required Snowflake connection parameters")
            return False
            
        # Check authentication method
        if not snowflake_settings.password and not snowflake_settings.private_key_path:
            logger.error("No authentication method configured (password or private key)")
            return False
            
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Settings validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Settings validation failed: {e}")
        return False


# Initialize logging on module import
configure_logging()
logger.info("Configuration loaded successfully") 