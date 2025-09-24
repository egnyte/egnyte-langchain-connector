"""Pytest configuration and fixtures for Egnyte Retriever tests."""

import os
import time
from typing import Optional

import pytest


def load_env_vars():
    """Load environment variables from tests/.env file if available."""
    try:
        import os

        from dotenv import load_dotenv

        # Load from tests/.env specifically
        tests_env_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "tests", ".env"
        )
        if os.path.exists(tests_env_path):
            load_dotenv(tests_env_path)
        else:
            # Fallback to default .env loading
            load_dotenv()
    except ImportError:
        # python-dotenv not available, skip loading
        pass


def get_egnyte_credentials() -> tuple[Optional[str], Optional[str]]:
    """Get Egnyte credentials from environment variables.

    Returns:
        Tuple of (domain, user_token) or (None, None) if not available
    """
    load_env_vars()

    domain = os.getenv("EGNYTE_DOMAIN")
    user_token = os.getenv("EGNYTE_USER_TOKEN")

    # Clean up domain if it has protocol or extra formatting
    if domain:
        domain = domain.strip('"').strip("'")
        if domain.startswith("https://"):
            domain = domain[8:]
        elif domain.startswith("http://"):
            domain = domain[7:]
        if domain.startswith("."):
            domain = domain[1:]

    return domain, user_token


@pytest.fixture(scope="session")
def egnyte_credentials():
    """Fixture to provide Egnyte credentials for integration tests."""
    domain, user_token = get_egnyte_credentials()

    if not domain or not user_token:
        pytest.skip(
            "Egnyte credentials not available. Set EGNYTE_DOMAIN and "
            "EGNYTE_USER_TOKEN environment variables."
        )

    return {"domain": domain, "user_token": user_token}


@pytest.fixture(scope="session")
def skip_if_no_credentials():
    """Fixture to skip tests if no credentials are available."""
    domain, user_token = get_egnyte_credentials()

    if not domain or not user_token:
        pytest.skip(
            "Integration tests require EGNYTE_DOMAIN and EGNYTE_USER_TOKEN "
            "environment variables"
        )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring API credentials",
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test not requiring external dependencies"
    )


@pytest.fixture(autouse=True)
def rate_limit_delay(request):
    """Add delay between integration tests to avoid rate limiting."""
    # Only add delay for integration tests
    if "integration" in str(request.fspath):
        # Add delay before each test (except the first one in a session)
        if hasattr(request.session, "_integration_test_count"):
            time.sleep(5)  # 5 second delay between integration tests
            request.session._integration_test_count += 1
        else:
            request.session._integration_test_count = 1


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Mark unit tests
        elif "unit_tests" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
