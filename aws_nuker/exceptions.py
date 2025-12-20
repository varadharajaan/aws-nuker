"""
Custom exception hierarchy for AWS Nuker.

Provides structured error handling with clear categories for different
failure modes, enabling better debugging and observability.
"""

from typing import Optional, Dict, Any


class AWSNukerError(Exception):
    """Base exception for all AWS Nuker errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize AWSNukerError.

        Args:
            message: Human-readable error message
            details: Additional context about the error
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON logging."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }
        if self.cause:
            result["cause"] = str(self.cause)
        return result


# ============================================================================
# Configuration Errors
# ============================================================================


class ConfigurationError(AWSNukerError):
    """Raised when there's a configuration problem."""

    pass


class InvalidRegionError(ConfigurationError):
    """Raised when an invalid AWS region is specified."""

    def __init__(self, region: str, valid_regions: Optional[list] = None):
        details = {"invalid_region": region}
        if valid_regions:
            details["valid_regions"] = valid_regions
        super().__init__(
            message=f"Invalid AWS region: {region}",
            details=details,
        )


class InvalidServiceError(ConfigurationError):
    """Raised when an invalid AWS service is specified."""

    def __init__(self, service: str, valid_services: Optional[list] = None):
        details = {"invalid_service": service}
        if valid_services:
            details["valid_services"] = valid_services[:20]  # Limit list size
        super().__init__(
            message=f"Invalid AWS service: {service}",
            details=details,
        )


# ============================================================================
# Authentication & Authorization Errors
# ============================================================================


class AuthenticationError(AWSNukerError):
    """Raised when AWS authentication fails."""

    def __init__(
        self,
        message: str = "AWS authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, details=details)


class CredentialsNotFoundError(AuthenticationError):
    """Raised when AWS credentials cannot be found."""

    def __init__(self):
        super().__init__(
            message="AWS credentials not found. Please configure credentials.",
            details={"hint": "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or use AWS CLI"},
        )


class CredentialsExpiredError(AuthenticationError):
    """Raised when AWS credentials have expired."""

    def __init__(self):
        super().__init__(
            message="AWS credentials have expired. Please refresh credentials.",
        )


class PermissionDeniedError(AWSNukerError):
    """Raised when permission is denied for an operation."""

    def __init__(
        self,
        action: str,
        resource: str,
        required_permission: Optional[str] = None,
    ):
        details = {"action": action, "resource": resource}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(
            message=f"Permission denied: {action} on {resource}",
            details=details,
        )


# ============================================================================
# Resource Errors
# ============================================================================


class ResourceError(AWSNukerError):
    """Base class for resource-related errors."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        region: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
        if region:
            error_details["region"] = region
        super().__init__(message=message, details=error_details, cause=cause)


class ResourceNotFoundError(ResourceError):
    """Raised when a resource cannot be found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        region: Optional[str] = None,
    ):
        super().__init__(
            message=f"Resource not found: {resource_type}/{resource_id}",
            resource_type=resource_type,
            resource_id=resource_id,
            region=region,
        )


class ResourceInUseError(ResourceError):
    """Raised when a resource cannot be deleted because it's in use."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        dependent_resources: Optional[list] = None,
    ):
        details = {}
        if dependent_resources:
            details["dependent_resources"] = dependent_resources
        super().__init__(
            message=f"Resource in use: {resource_type}/{resource_id}",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )


class DependencyViolationError(ResourceError):
    """Raised when deletion fails due to resource dependencies."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        dependencies: Optional[list] = None,
    ):
        details = {}
        if dependencies:
            details["dependencies"] = dependencies
        super().__init__(
            message=f"Cannot delete {resource_type}/{resource_id}: has dependencies",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )


class DeletionError(ResourceError):
    """Raised when resource deletion fails."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        reason: str,
        region: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=f"Failed to delete {resource_type}/{resource_id}: {reason}",
            resource_type=resource_type,
            resource_id=resource_id,
            region=region,
            details={"reason": reason},
            cause=cause,
        )


# ============================================================================
# Service Errors
# ============================================================================


class ServiceError(AWSNukerError):
    """Base class for AWS service-related errors."""

    def __init__(
        self,
        service: str,
        message: str,
        region: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        error_details = details or {}
        error_details["service"] = service
        if region:
            error_details["region"] = region
        super().__init__(message=message, details=error_details, cause=cause)


class ServiceUnavailableError(ServiceError):
    """Raised when an AWS service is unavailable."""

    def __init__(self, service: str, region: Optional[str] = None):
        super().__init__(
            service=service,
            message=f"Service unavailable: {service}",
            region=region,
        )


class ServiceNotSupportedError(ServiceError):
    """Raised when a service is not supported in a region."""

    def __init__(self, service: str, region: str):
        super().__init__(
            service=service,
            message=f"Service {service} is not supported in region {region}",
            region=region,
        )


class RateLimitExceededError(ServiceError):
    """Raised when AWS API rate limits are exceeded."""

    def __init__(
        self,
        service: str,
        retry_after: Optional[int] = None,
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            service=service,
            message=f"Rate limit exceeded for {service}",
            details=details,
        )


class ThrottlingError(ServiceError):
    """Raised when requests are being throttled by AWS."""

    def __init__(
        self,
        service: str,
        operation: str,
        region: Optional[str] = None,
    ):
        super().__init__(
            service=service,
            message=f"Throttled: {service}/{operation}",
            region=region,
            details={"operation": operation},
        )


# ============================================================================
# Handler Errors
# ============================================================================


class HandlerError(AWSNukerError):
    """Base class for handler-related errors."""

    pass


class HandlerNotFoundError(HandlerError):
    """Raised when a handler for a service cannot be found."""

    def __init__(self, service: str):
        super().__init__(
            message=f"No handler found for service: {service}",
            details={"service": service},
        )


class HandlerInitializationError(HandlerError):
    """Raised when a handler fails to initialize."""

    def __init__(
        self,
        service: str,
        reason: str,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=f"Failed to initialize handler for {service}: {reason}",
            details={"service": service, "reason": reason},
            cause=cause,
        )


# ============================================================================
# Circuit Breaker Errors
# ============================================================================


class CircuitBreakerError(AWSNukerError):
    """Raised when circuit breaker is open."""

    def __init__(
        self,
        service: str,
        failure_count: int,
        reset_time: Optional[float] = None,
    ):
        details = {
            "service": service,
            "failure_count": failure_count,
        }
        if reset_time:
            details["reset_time_seconds"] = reset_time
        super().__init__(
            message=f"Circuit breaker open for {service} after {failure_count} failures",
            details=details,
        )


# ============================================================================
# Validation Errors
# ============================================================================


class ValidationError(AWSNukerError):
    """Raised when input validation fails."""

    pass


class PreflightCheckError(ValidationError):
    """Raised when pre-flight checks fail."""

    def __init__(
        self,
        check_name: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["check_name"] = check_name
        error_details["reason"] = reason
        super().__init__(
            message=f"Pre-flight check failed: {check_name} - {reason}",
            details=error_details,
        )
