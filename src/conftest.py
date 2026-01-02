"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest and provides
shared fixtures for all test files.
"""

import pytest


@pytest.fixture
def sample_car_url() -> str:
    """Provide a sample car listing URL for testing."""
    return "https://www.cars.com/vehicledetail/12345"


@pytest.fixture
def sample_search_url() -> str:
    """Provide a sample search URL for testing."""
    return "https://www.cars.com/shopping/results/?stock_type=used&makes[]=toyota"
