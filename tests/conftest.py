"""Pytest configuration and fixtures for AWS Nuker tests."""

import pytest
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Set mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def reset_correlation_id():
    """Reset correlation ID after test."""
    from aws_nuker.structured_logger import new_correlation_id
    new_correlation_id()
    yield
    new_correlation_id()


@pytest.fixture
def fresh_metrics():
    """Provide fresh metrics collector for each test."""
    from aws_nuker.structured_logger import MetricsCollector
    return MetricsCollector()


@pytest.fixture
def fresh_circuit_breaker_registry():
    """Provide fresh circuit breaker registry for each test."""
    from aws_nuker.reliability import CircuitBreakerRegistry
    return CircuitBreakerRegistry()
