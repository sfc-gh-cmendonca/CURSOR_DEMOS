"""Database connection utilities for Snowflake."""

import snowflake.connector
from snowflake.snowpark import Session
from snowflake.connector import DictCursor
from contextlib import contextmanager
from typing import Dict, Any, Optional, Generator
from loguru import logger

from ..config.settings import snowflake_settings, app_settings


class SnowflakeConnectionManager:
    """Manages Snowflake database connections with best practices."""
    
    def __init__(self):
        self._connection_params = self._build_connection_params()
        self._session_params = self._build_session_params()
    
    def _build_connection_params(self) -> Dict[str, Any]:
        """Build connection parameters for snowflake-connector-python."""
        params = {
            "account": snowflake_settings.account,
            "user": snowflake_settings.user,
            "role": snowflake_settings.role,
            "warehouse": snowflake_settings.warehouse,
            "database": snowflake_settings.database,
            "schema": snowflake_settings.schema,
            "client_session_keep_alive": True,
            "network_timeout": app_settings.query_timeout_seconds,
            "login_timeout": 60,
        }
        
        # Add authentication method
        if snowflake_settings.password:
            params["password"] = snowflake_settings.password
        elif snowflake_settings.private_key_path:
            params["private_key_path"] = snowflake_settings.private_key_path
            if snowflake_settings.private_key_passphrase:
                params["private_key_passphrase"] = snowflake_settings.private_key_passphrase
        elif snowflake_settings.authenticator:
            params["authenticator"] = snowflake_settings.authenticator
        
        return params
    
    def _build_session_params(self) -> Dict[str, Any]:
        """Build session parameters for Snowpark."""
        return {
            "account": snowflake_settings.account,
            "user": snowflake_settings.user,
            "password": snowflake_settings.password,
            "role": snowflake_settings.role,
            "warehouse": snowflake_settings.warehouse,
            "database": snowflake_settings.database,
            "schema": snowflake_settings.schema,
        }
    
    @contextmanager
    def get_connection(self) -> Generator[snowflake.connector.SnowflakeConnection, None, None]:
        """
        Get a database connection with proper error handling and cleanup.
        
        Yields:
            SnowflakeConnection: Active database connection
        """
        connection = None
        try:
            logger.debug("Establishing Snowflake connection")
            connection = snowflake.connector.connect(**self._connection_params)
            
            # Set session parameters for optimal performance
            with connection.cursor() as cursor:
                # Enable query result caching
                cursor.execute("ALTER SESSION SET USE_CACHED_RESULT = TRUE")
                
                # Set query timeout
                cursor.execute(f"ALTER SESSION SET QUERY_TIMEOUT = {app_settings.query_timeout_seconds}")
                
                # Set timezone for consistent results
                cursor.execute("ALTER SESSION SET TIMEZONE = 'UTC'")
                
                logger.debug("Session parameters configured")
            
            yield connection
            
        except snowflake.connector.Error as e:
            logger.error(f"Snowflake connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in connection: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    logger.debug("Snowflake connection closed")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True) -> Generator[Any, None, None]:
        """
        Get a database cursor with proper error handling and cleanup.
        
        Args:
            dict_cursor: Whether to use DictCursor for row-as-dict results
            
        Yields:
            Cursor: Database cursor
        """
        with self.get_connection() as connection:
            cursor_class = DictCursor if dict_cursor else None
            cursor = connection.cursor(cursor_class)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def get_snowpark_session(self) -> Session:
        """
        Get a Snowpark session for DataFrame operations.
        
        Returns:
            Session: Snowpark session
        """
        try:
            logger.debug("Creating Snowpark session")
            session = Session.builder.configs(self._session_params).create()
            
            # Set session parameters
            session.sql(f"ALTER SESSION SET QUERY_TIMEOUT = {app_settings.query_timeout_seconds}").collect()
            session.sql("ALTER SESSION SET USE_CACHED_RESULT = TRUE").collect()
            session.sql("ALTER SESSION SET TIMEZONE = 'UTC'").collect()
            
            logger.debug("Snowpark session created successfully")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create Snowpark session: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT CURRENT_VERSION() as version")
                result = cursor.fetchone()
                version = result["VERSION"] if result else "Unknown"
                logger.info(f"Connected to Snowflake version: {version}")
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None,
        fetch_all: bool = True
    ) -> Optional[Any]:
        """
        Execute a SQL query with proper error handling.
        
        Args:
            query: SQL query to execute
            params: Query parameters for safe substitution
            fetch_all: Whether to fetch all results
            
        Returns:
            Query results or None
        """
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_all:
                    results = cursor.fetchall()
                    logger.debug(f"Query returned {len(results)} rows")
                    return results
                else:
                    result = cursor.fetchone()
                    logger.debug("Query returned single row")
                    return result
                    
        except snowflake.connector.Error as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise


# Global connection manager instance
connection_manager = SnowflakeConnectionManager()


def get_connection_manager() -> SnowflakeConnectionManager:
    """Get the global connection manager instance."""
    return connection_manager


@contextmanager
def get_db_connection():
    """Convenience function to get a database connection."""
    with connection_manager.get_connection() as conn:
        yield conn


@contextmanager  
def get_db_cursor(dict_cursor: bool = True):
    """Convenience function to get a database cursor."""
    with connection_manager.get_cursor(dict_cursor) as cursor:
        yield cursor


def execute_sql(query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Convenience function to execute a SQL query."""
    return connection_manager.execute_query(query, params) 