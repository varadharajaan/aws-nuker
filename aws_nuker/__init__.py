"""
AWS Nuker - A comprehensive AWS resource cleanup tool.

This package provides functionality to destroy all non-default AWS resources
across multiple regions and services.

Features:
- 100+ AWS service handlers
- Structured JSON logging with correlation IDs
- Circuit breaker and retry patterns for reliability
- Pre-flight credential and permission validation
- Custom exception hierarchy for better error handling
"""

__version__ = "1.0.0"
__author__ = "AWS Nuker Team"

# Core exports
from .config import NukerConfig, ALL_AWS_REGIONS, ALL_AWS_SERVICES
from .orchestrator import AWSNuker
from .base_handler import ResourceHandler
from .registry import get_handler, get_available_services

# Observability
from .logger import get_logger
from .structured_logger import (
    StructuredLogger,
    get_structured_logger,
    get_correlation_id,
    set_correlation_id,
    new_correlation_id,
    get_metrics,
)

# Reliability
from .reliability import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    RetryConfig,
    RetryContext,
    retry_with_backoff,
    get_aws_retry_config,
    get_circuit_breaker_registry,
    Bulkhead,
)

# Pre-flight checks
from .preflight import (
    PreflightChecker,
    PreflightReport,
    CheckResult,
    CheckStatus,
    run_preflight_checks,
)

# Exceptions
from .exceptions import (
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

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core
    "NukerConfig",
    "ALL_AWS_REGIONS",
    "ALL_AWS_SERVICES",
    "AWSNuker",
    "ResourceHandler",
    "get_handler",
    "get_available_services",
    # Logging
    "get_logger",
    "StructuredLogger",
    "get_structured_logger",
    "get_correlation_id",
    "set_correlation_id",
    "new_correlation_id",
    "get_metrics",
    # Reliability
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "RetryConfig",
    "RetryContext",
    "retry_with_backoff",
    "get_aws_retry_config",
    "get_circuit_breaker_registry",
    "Bulkhead",
    # Pre-flight
    "PreflightChecker",
    "PreflightReport",
    "CheckResult",
    "CheckStatus",
    "run_preflight_checks",
    # Exceptions
    "AWSNukerError",
    "ConfigurationError",
    "InvalidRegionError",
    "InvalidServiceError",
    "AuthenticationError",
    "CredentialsNotFoundError",
    "CredentialsExpiredError",
    "PermissionDeniedError",
    "ResourceError",
    "ResourceNotFoundError",
    "ResourceInUseError",
    "DependencyViolationError",
    "DeletionError",
    "ServiceError",
    "ServiceUnavailableError",
    "ServiceNotSupportedError",
    "RateLimitExceededError",
    "ThrottlingError",
    "HandlerError",
    "HandlerNotFoundError",
    "HandlerInitializationError",
    "CircuitBreakerError",
    "ValidationError",
    "PreflightCheckError",
]
