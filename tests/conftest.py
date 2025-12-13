# ====================================================================================================
# conftest.py
# ----------------------------------------------------------------------------------------------------
# Pytest configuration and shared fixtures for Orders-to-Cash test suite.
# ====================================================================================================

from __future__ import annotations

import sys
from pathlib import Path
import pytest
import pandas as pd
from datetime import date, datetime

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# ====================================================================================================
# FIXTURES - TEST DATA
# ====================================================================================================

@pytest.fixture
def sample_order_dataframe() -> pd.DataFrame:
    """
    Returns a sample order-level DataFrame for testing.
    """
    return pd.DataFrame({
        "gp_order_id": ["GP001", "GP002", "GP003"],
        "mp_order_id": ["12345", "12346", "12347"],
        "order_vendor": ["Just Eat", "Uber", "Deliveroo"],
        "total_payment_with_tips_inc_vat": [25.50, 18.75, 32.00],
        "created_at_day": [date(2025, 11, 5), date(2025, 11, 6), date(2025, 11, 7)],
        "order_completed": [1, 1, 0],
    })


@pytest.fixture
def sample_item_dataframe() -> pd.DataFrame:
    """
    Returns a sample item-level DataFrame with VAT bands.
    """
    return pd.DataFrame({
        "gp_order_id": ["GP001", "GP001", "GP002"],
        "vat_band": ["20% VAT Band", "0% VAT Band", "20% VAT Band"],
        "item_quantity_count": [2, 1, 3],
        "total_price_inc_vat": [15.00, 5.00, 18.75],
        "total_price_exc_vat": [12.50, 5.00, 15.63],
    })


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Path:
    """
    Returns a temporary directory for file I/O tests.
    """
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# ====================================================================================================
# FIXTURES - MOCKS
# ====================================================================================================

@pytest.fixture
def mock_snowflake_connection(monkeypatch):
    """
    Mocks Snowflake connection for testing without database access.
    """
    class MockCursor:
        def execute(self, sql):
            pass
        
        def fetchall(self):
            return []
        
        def close(self):
            pass
    
    class MockConnection:
        def cursor(self):
            return MockCursor()
        
        def close(self):
            pass
    
    def mock_create_connection(*args, **kwargs):
        return MockConnection()
    
    monkeypatch.setattr(
        "core.C14_snowflake_connector.create_snowflake_connection",
        mock_create_connection
    )
    
    return MockConnection()


# ====================================================================================================
# HOOKS
# ====================================================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.
    """
    # Suppress bytecode generation during tests
    sys.dont_write_bytecode = True
