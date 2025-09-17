"""Pytest configuration and shared fixtures."""

import pytest
import os
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_snowflake_connection():
    """Mock Snowflake connection for testing."""
    with patch("snowflake.connector.connect") as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def sample_env_vars():
    """Sample environment variables for testing."""
    env_vars = {
        "SNOWFLAKE_ACCOUNT": "test_account",
        "SNOWFLAKE_USER": "test_user",
        "SNOWFLAKE_PASSWORD": "test_password",
        "SNOWFLAKE_ROLE": "TEST_ROLE",
        "SNOWFLAKE_WAREHOUSE": "TEST_WH",
        "SNOWFLAKE_DATABASE": "TEST_DB",
        "SNOWFLAKE_SCHEMA": "TEST_SCHEMA",
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "content": "Market analysis shows strong bullish sentiment",
            "score": 0.95,
            "source": "research_report_001.pdf",
            "metadata": {
                "asset_class": "equity",
                "sector": "technology",
                "date": "2024-01-15"
            }
        },
        {
            "content": "Federal Reserve signals potential rate cuts",
            "score": 0.87,
            "source": "fed_minutes_jan_2024.pdf",
            "metadata": {
                "asset_class": "fixed_income",
                "date": "2024-01-31"
            }
        }
    ] 