"""
Reliability patterns for AWS Nuker.

Implements circuit breaker, retry with exponential backoff,
and bulkhead patterns for fault tolerance.
"""

import random
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from .exceptions import (
    CircuitBreakerError,
    RateLimitExceededError,
    ThrottlingError,
)


# Type variable for generic return type
T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests flow through
    OPEN = "open"          # Failing, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures before opening
    success_threshold: int = 2          # Successes needed to close
    timeout_seconds: float = 30.0       # Time before attempting recovery
    half_open_max_calls: int = 3        # Max calls in half-open state


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: int = 0


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping calls to a failing service
    and allowing recovery time.
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit breaker (usually service name)
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = threading.Lock()
        self._stats = CircuitBreakerStats()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_state_timeout()
            return self._state

    def _check_state_timeout(self):
        """Check if timeout has elapsed and transition to half-open."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            elapsed = (datetime.now() - self._last_failure_time).total_seconds()
            if elapsed >= self.config.timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
                self._half_open_calls = 0

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        if self._state != new_state:
            self._state = new_state
            self._stats.state_changes += 1

    def can_execute(self) -> bool:
        """Check if the circuit allows execution."""
        with self._lock:
            self._check_state_timeout()

            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.OPEN:
                self._stats.rejected_calls += 1
                return False
            else:  # HALF_OPEN
                if self._half_open_calls < self.config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False

    def record_success(self):
        """Record a successful call."""
        with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.last_success_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self._failure_count = 0
                    self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.last_failure_time = datetime.now()
            self._last_failure_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open state opens the circuit
                self._transition_to(CircuitState.OPEN)
                self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self._stats

    def reset(self):
        """Reset the circuit breaker to initial state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._half_open_calls = 0


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Provides a central place to access circuit breakers for different services.
    """

    def __init__(self):
        """Initialize the registry."""
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
        self._default_config = CircuitBreakerConfig()

    def get(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.

        Args:
            name: Name of the circuit breaker
            config: Optional configuration

        Returns:
            Circuit breaker instance
        """
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    config=config or self._default_config,
                )
            return self._breakers[name]

    def get_all_stats(self) -> Dict[str, CircuitBreakerStats]:
        """Get statistics for all circuit breakers."""
        with self._lock:
            return {
                name: breaker.get_stats()
                for name, breaker in self._breakers.items()
            }

    def reset_all(self):
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# Global registry
_circuit_breaker_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    global _circuit_breaker_registry
    if _circuit_breaker_registry is None:
        _circuit_breaker_registry = CircuitBreakerRegistry()
    return _circuit_breaker_registry


# ============================================================================
# Retry with Exponential Backoff
# ============================================================================


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd
    jitter_factor: float = 0.5  # 0.0 to 1.0
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()


def calculate_backoff(
    attempt: int,
    config: RetryConfig,
) -> float:
    """
    Calculate backoff delay with exponential increase and optional jitter.

    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    # Exponential backoff: base_delay * exponential_base^attempt
    delay = config.base_delay_seconds * (config.exponential_base ** attempt)

    # Cap at maximum delay
    delay = min(delay, config.max_delay_seconds)

    # Add jitter if enabled
    if config.jitter:
        jitter_range = delay * config.jitter_factor
        delay = delay + random.uniform(-jitter_range, jitter_range)
        delay = max(0.1, delay)  # Ensure minimum delay

    return delay


def is_retryable_error(
    error: Exception,
    config: RetryConfig,
) -> bool:
    """
    Check if an error should trigger a retry.

    Args:
        error: The exception that occurred
        config: Retry configuration

    Returns:
        True if the error should trigger a retry
    """
    # Check non-retryable first
    if isinstance(error, config.non_retryable_exceptions):
        return False

    # Check retryable
    return isinstance(error, config.retryable_exceptions)


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        config: Retry configuration
        on_retry: Optional callback called on each retry with (error, attempt, delay)

    Example:
        @retry_with_backoff(RetryConfig(max_retries=5))
        def call_aws_api():
            ...
    """
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if attempt >= cfg.max_retries:
                        raise

                    if not is_retryable_error(e, cfg):
                        raise

                    # Calculate delay
                    delay = calculate_backoff(attempt, cfg)

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1, delay)

                    # Wait before retry
                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class RetryContext:
    """
    Context manager for retry logic with backoff.

    Provides more control than the decorator version.

    Example:
        retry_ctx = RetryContext(RetryConfig(max_retries=3))
        while retry_ctx.should_retry():
            try:
                result = call_api()
                retry_ctx.success()
                break
            except Exception as e:
                retry_ctx.failure(e)
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry context."""
        self.config = config or RetryConfig()
        self._attempt = 0
        self._last_error: Optional[Exception] = None
        self._succeeded = False

    @property
    def attempt(self) -> int:
        """Get current attempt number (1-based)."""
        return self._attempt

    @property
    def last_error(self) -> Optional[Exception]:
        """Get the last error that occurred."""
        return self._last_error

    def should_retry(self) -> bool:
        """Check if another retry should be attempted."""
        if self._succeeded:
            return False
        if self._attempt > self.config.max_retries:
            if self._last_error:
                raise self._last_error
            return False
        return True

    def success(self):
        """Mark the operation as successful."""
        self._succeeded = True

    def failure(self, error: Exception):
        """
        Record a failure and wait before next retry if applicable.

        Args:
            error: The exception that occurred
        """
        self._last_error = error
        self._attempt += 1

        if not is_retryable_error(error, self.config):
            raise error

        if self._attempt <= self.config.max_retries:
            delay = calculate_backoff(self._attempt - 1, self.config)
            time.sleep(delay)


# ============================================================================
# AWS-Specific Retry Configurations
# ============================================================================


# Common AWS SDK exception names that are retryable
AWS_RETRYABLE_ERROR_CODES = {
    "Throttling",
    "ThrottlingException",
    "RequestThrottled",
    "RequestThrottledException",
    "ProvisionedThroughputExceededException",
    "ServiceUnavailable",
    "ServiceUnavailableException",
    "InternalError",
    "InternalServiceError",
    "RequestLimitExceeded",
    "BandwidthLimitExceeded",
    "TooManyRequestsException",
    "SlowDown",
}


def is_aws_retryable_error(error: Exception) -> bool:
    """
    Check if an AWS error should trigger a retry.

    Args:
        error: The exception from boto3/botocore

    Returns:
        True if the error should trigger a retry
    """
    # Check for our custom exceptions
    if isinstance(error, (ThrottlingError, RateLimitExceededError)):
        return True

    # Check for botocore ClientError
    error_code = getattr(error, "response", {}).get("Error", {}).get("Code", "")
    if error_code in AWS_RETRYABLE_ERROR_CODES:
        return True

    # Check error message for common patterns
    error_str = str(error).lower()
    retryable_patterns = [
        "throttl",
        "rate exceeded",
        "too many requests",
        "service unavailable",
        "internal error",
        "connection reset",
        "connection timeout",
    ]
    return any(pattern in error_str for pattern in retryable_patterns)


def get_aws_retry_config(service: str = "default") -> RetryConfig:
    """
    Get retry configuration optimized for AWS API calls.

    Args:
        service: AWS service name for service-specific tuning

    Returns:
        Retry configuration
    """
    # Service-specific configurations
    configs = {
        "dynamodb": RetryConfig(
            max_retries=10,
            base_delay_seconds=0.05,
            max_delay_seconds=25.0,
        ),
        "s3": RetryConfig(
            max_retries=5,
            base_delay_seconds=0.5,
            max_delay_seconds=20.0,
        ),
        "lambda": RetryConfig(
            max_retries=3,
            base_delay_seconds=1.0,
            max_delay_seconds=30.0,
        ),
        "ec2": RetryConfig(
            max_retries=4,
            base_delay_seconds=1.0,
            max_delay_seconds=30.0,
        ),
    }

    return configs.get(service, RetryConfig(
        max_retries=3,
        base_delay_seconds=1.0,
        max_delay_seconds=60.0,
    ))


# ============================================================================
# Bulkhead Pattern
# ============================================================================


class Bulkhead:
    """
    Bulkhead pattern implementation for resource isolation.

    Limits concurrent executions to prevent resource exhaustion
    and isolate failures.
    """

    def __init__(
        self,
        name: str,
        max_concurrent: int = 10,
        max_wait_seconds: float = 30.0,
    ):
        """
        Initialize bulkhead.

        Args:
            name: Name of the bulkhead
            max_concurrent: Maximum concurrent executions
            max_wait_seconds: Maximum time to wait for a slot
        """
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_wait_seconds = max_wait_seconds
        self._semaphore = threading.Semaphore(max_concurrent)
        self._active_count = 0
        self._rejected_count = 0
        self._lock = threading.Lock()

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a slot in the bulkhead.

        Args:
            timeout: Optional timeout in seconds. If None, uses max_wait_seconds.
                     If 0, performs a non-blocking attempt.

        Returns:
            True if slot acquired, False if timed out or slot not available
        """
        # Use explicit timeout if provided (including 0 for non-blocking),
        # otherwise fall back to max_wait_seconds
        wait_time = timeout if timeout is not None else self.max_wait_seconds
        acquired = self._semaphore.acquire(timeout=wait_time)

        with self._lock:
            if acquired:
                self._active_count += 1
            else:
                self._rejected_count += 1

        return acquired

    def release(self):
        """Release a slot in the bulkhead."""
        self._semaphore.release()
        with self._lock:
            self._active_count = max(0, self._active_count - 1)

    @property
    def active_count(self) -> int:
        """Get the number of active executions."""
        with self._lock:
            return self._active_count

    @property
    def available_count(self) -> int:
        """Get the number of available slots."""
        with self._lock:
            return self.max_concurrent - self._active_count

    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        with self._lock:
            return {
                "name": self.name,
                "max_concurrent": self.max_concurrent,
                "active": self._active_count,
                "available": self.max_concurrent - self._active_count,
                "rejected": self._rejected_count,
            }

    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            raise TimeoutError(f"Bulkhead {self.name} timeout waiting for slot")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False
