"""Tests for AWS Nuker custom exception hierarchy."""

import pytest
from aws_nuker.exceptions import (
    AWSNukerError,
    ConfigurationError,
    InvalidRegionError,
    InvalidServiceError,
    AuthenticationError,
    CredentialsNotFoundError,
    CredentialsExpiredError,
    PermissionDeniedError,
    ResourceError,
    ResourceNotFoundError,
    ResourceInUseError,
    DependencyViolationError,
    DeletionError,
    ServiceError,
    ServiceUnavailableError,
    ServiceNotSupportedError,
    RateLimitExceededError,
    ThrottlingError,
    HandlerError,
    HandlerNotFoundError,
    HandlerInitializationError,
    CircuitBreakerError,
    ValidationError,
    PreflightCheckError,
)


class TestAWSNukerError:
    """Tests for the base AWSNukerError class."""

    def test_basic_creation(self):
        """Test basic error creation."""
        error = AWSNukerError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}
        assert error.cause is None

    def test_with_details(self):
        """Test error creation with details."""
        error = AWSNukerError(
            message="Test error",
            details={"key": "value", "count": 42},
        )
        assert error.details == {"key": "value", "count": 42}

    def test_with_cause(self):
        """Test error creation with cause exception."""
        cause = ValueError("Original error")
        error = AWSNukerError("Wrapped error", cause=cause)
        assert error.cause is cause

    def test_to_dict(self):
        """Test conversion to dictionary."""
        cause = ValueError("Original")
        error = AWSNukerError(
            message="Test error",
            details={"key": "value"},
            cause=cause,
        )
        result = error.to_dict()
        
        assert result["error_type"] == "AWSNukerError"
        assert result["message"] == "Test error"
        assert result["details"] == {"key": "value"}
        assert "Original" in result["cause"]


class TestConfigurationErrors:
    """Tests for configuration-related errors."""

    def test_invalid_region_error(self):
        """Test InvalidRegionError."""
        error = InvalidRegionError(
            region="invalid-region",
            valid_regions=["us-east-1", "us-west-2"],
        )
        assert "invalid-region" in str(error)
        assert error.details["invalid_region"] == "invalid-region"
        assert "us-east-1" in error.details["valid_regions"]

    def test_invalid_service_error(self):
        """Test InvalidServiceError."""
        error = InvalidServiceError(
            service="nonexistent",
            valid_services=["ec2", "s3", "lambda"],
        )
        assert "nonexistent" in str(error)
        assert error.details["invalid_service"] == "nonexistent"


class TestAuthenticationErrors:
    """Tests for authentication-related errors."""

    def test_credentials_not_found(self):
        """Test CredentialsNotFoundError."""
        error = CredentialsNotFoundError()
        assert "credentials not found" in str(error).lower()
        assert "hint" in error.details

    def test_credentials_expired(self):
        """Test CredentialsExpiredError."""
        error = CredentialsExpiredError()
        assert "expired" in str(error).lower()

    def test_permission_denied(self):
        """Test PermissionDeniedError."""
        error = PermissionDeniedError(
            action="DeleteBucket",
            resource="arn:aws:s3:::my-bucket",
            required_permission="s3:DeleteBucket",
        )
        assert "DeleteBucket" in str(error)
        assert error.details["action"] == "DeleteBucket"
        assert error.details["required_permission"] == "s3:DeleteBucket"


class TestResourceErrors:
    """Tests for resource-related errors."""

    def test_resource_not_found(self):
        """Test ResourceNotFoundError."""
        error = ResourceNotFoundError(
            resource_type="ec2:instance",
            resource_id="i-1234567890abcdef0",
            region="us-east-1",
        )
        assert "i-1234567890abcdef0" in str(error)
        assert error.details["resource_type"] == "ec2:instance"
        assert error.details["region"] == "us-east-1"

    def test_resource_in_use(self):
        """Test ResourceInUseError."""
        error = ResourceInUseError(
            resource_type="ec2:volume",
            resource_id="vol-123",
            dependent_resources=["i-abc", "i-def"],
        )
        assert "vol-123" in str(error)
        assert error.details["dependent_resources"] == ["i-abc", "i-def"]

    def test_dependency_violation(self):
        """Test DependencyViolationError."""
        error = DependencyViolationError(
            resource_type="ec2:security_group",
            resource_id="sg-123",
            dependencies=["i-abc"],
        )
        assert "dependencies" in str(error).lower()
        assert error.details["dependencies"] == ["i-abc"]

    def test_deletion_error(self):
        """Test DeletionError."""
        cause = Exception("API error")
        error = DeletionError(
            resource_type="s3:bucket",
            resource_id="my-bucket",
            reason="Bucket not empty",
            region="us-east-1",
            cause=cause,
        )
        assert "my-bucket" in str(error)
        assert "Bucket not empty" in str(error)
        assert error.cause is cause


class TestServiceErrors:
    """Tests for service-related errors."""

    def test_service_unavailable(self):
        """Test ServiceUnavailableError."""
        error = ServiceUnavailableError(service="ec2", region="us-east-1")
        assert "ec2" in str(error)
        assert error.details["region"] == "us-east-1"

    def test_service_not_supported(self):
        """Test ServiceNotSupportedError."""
        error = ServiceNotSupportedError(service="bedrock", region="eu-central-1")
        assert "bedrock" in str(error)
        assert "eu-central-1" in str(error)

    def test_rate_limit_exceeded(self):
        """Test RateLimitExceededError."""
        error = RateLimitExceededError(service="dynamodb", retry_after=30)
        assert "dynamodb" in str(error)
        assert error.details["retry_after_seconds"] == 30

    def test_throttling_error(self):
        """Test ThrottlingError."""
        error = ThrottlingError(
            service="ec2",
            operation="DescribeInstances",
            region="us-east-1",
        )
        assert "ec2" in str(error)
        assert error.details["operation"] == "DescribeInstances"


class TestHandlerErrors:
    """Tests for handler-related errors."""

    def test_handler_not_found(self):
        """Test HandlerNotFoundError."""
        error = HandlerNotFoundError(service="unknown-service")
        assert "unknown-service" in str(error)

    def test_handler_initialization_error(self):
        """Test HandlerInitializationError."""
        cause = ImportError("Module not found")
        error = HandlerInitializationError(
            service="ec2",
            reason="Missing dependency",
            cause=cause,
        )
        assert "ec2" in str(error)
        assert "Missing dependency" in str(error)
        assert error.cause is cause


class TestCircuitBreakerError:
    """Tests for CircuitBreakerError."""

    def test_circuit_breaker_error(self):
        """Test CircuitBreakerError."""
        error = CircuitBreakerError(
            service="s3",
            failure_count=5,
            reset_time=30.0,
        )
        assert "s3" in str(error)
        assert "5" in str(error)
        assert error.details["failure_count"] == 5
        assert error.details["reset_time_seconds"] == 30.0


class TestValidationErrors:
    """Tests for validation-related errors."""

    def test_preflight_check_error(self):
        """Test PreflightCheckError."""
        error = PreflightCheckError(
            check_name="aws_credentials",
            reason="Credentials expired",
            details={"error_code": "ExpiredToken"},
        )
        assert "aws_credentials" in str(error)
        assert "Credentials expired" in str(error)
        assert error.details["error_code"] == "ExpiredToken"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_inheritance(self):
        """Test that all exceptions inherit from AWSNukerError."""
        exceptions = [
            ConfigurationError("test"),
            AuthenticationError("test"),
            ResourceError("test"),
            ServiceError("ec2", "test"),
            HandlerError("test"),
            ValidationError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AWSNukerError)
            assert isinstance(exc, Exception)

    def test_specific_inheritance(self):
        """Test specific inheritance chains."""
        # Configuration errors
        assert isinstance(InvalidRegionError("test"), ConfigurationError)
        assert isinstance(InvalidServiceError("test"), ConfigurationError)
        
        # Authentication errors
        assert isinstance(CredentialsNotFoundError(), AuthenticationError)
        assert isinstance(CredentialsExpiredError(), AuthenticationError)
        
        # Resource errors
        assert isinstance(ResourceNotFoundError("t", "i"), ResourceError)
        assert isinstance(DeletionError("t", "i", "r"), ResourceError)
        
        # Service errors
        assert isinstance(ThrottlingError("s", "o"), ServiceError)
