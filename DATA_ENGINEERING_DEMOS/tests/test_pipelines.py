"""
Unit tests for data pipeline components
"""
import pytest
from unittest.mock import Mock, MagicMock
from config import DataEngDemoConfig


def test_config_values():
    """Test configuration values are set correctly"""
    assert DataEngDemoConfig.DATABASE == "DATA_ENG_DEMO"
    assert DataEngDemoConfig.SCHEMA_RAW == "RAW_DATA"
    assert DataEngDemoConfig.SCHEMA_CURATED == "CURATED"
    assert DataEngDemoConfig.NUM_CUSTOMERS > 0
    assert DataEngDemoConfig.NUM_PRODUCTS > 0


def test_date_ranges():
    """Test dynamic date generation"""
    start_date = DataEngDemoConfig.get_start_date()
    end_date = DataEngDemoConfig.get_end_date()
    
    assert start_date < end_date
    assert len(start_date) == 10  # YYYY-MM-DD format
    assert len(end_date) == 10


def test_data_volumes_reasonable():
    """Test configured data volumes are reasonable for demo"""
    assert DataEngDemoConfig.NUM_CUSTOMERS <= 10000
    assert DataEngDemoConfig.NUM_PRODUCTS <= 1000
    assert DataEngDemoConfig.NUM_STORES <= 100
    assert DataEngDemoConfig.HISTORICAL_DAYS <= 730  # Max 2 years


# Add more tests as needed for specific pipeline functions
# Example:
# def test_customer_generation():
#     mock_session = Mock()
#     generate_customers(mock_session)
#     assert mock_session.create_dataframe.called

