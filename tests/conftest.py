"""Pytest configuration and fixtures for AWS Nuker tests."""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

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


@pytest.fixture
def mock_boto_client():
    """Create a mock boto3 client factory."""
    def _create_mock_client(service_name):
        return MagicMock()
    return _create_mock_client


@pytest.fixture
def mock_boto_session():
    """Create a mock boto3 session."""
    with patch('boto3.Session') as mock_session:
        mock_session.return_value = MagicMock()
        yield mock_session


@pytest.fixture
def sample_ec2_resources():
    """Sample EC2 resource data for testing."""
    return [
        {"id": "i-1234567890abcdef0", "name": "test-instance", "type": "instance", "state": "running"},
        {"id": "vol-1234567890abcdef0", "name": "test-volume", "type": "volume", "state": "available"},
        {"id": "snap-1234567890abcdef0", "name": "test-snapshot", "type": "snapshot", "state": "completed"},
        {"id": "sg-1234567890abcdef0", "name": "test-sg", "type": "security_group"},
    ]


@pytest.fixture
def sample_s3_resources():
    """Sample S3 resource data for testing."""
    return [
        {"id": "test-bucket-1", "name": "test-bucket-1", "type": "bucket"},
        {"id": "test-ap-1", "name": "test-ap-1", "type": "access_point", "bucket": "test-bucket-1"},
    ]


@pytest.fixture
def sample_lambda_resources():
    """Sample Lambda resource data for testing."""
    return [
        {"id": "arn:aws:lambda:us-east-1:123456789012:function:test-function", "name": "test-function", "type": "function"},
        {"id": "arn:aws:lambda:us-east-1:123456789012:layer:test-layer", "name": "test-layer", "type": "layer"},
    ]
