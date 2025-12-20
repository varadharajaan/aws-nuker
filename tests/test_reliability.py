"""Tests for AWS Nuker reliability patterns."""

import threading
import time
import pytest
from aws_nuker.reliability import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerRegistry,
    get_circuit_breaker_registry,
    RetryConfig,
    RetryContext,
    retry_with_backoff,
    calculate_backoff,
    is_retryable_error,
    is_aws_retryable_error,
    get_aws_retry_config,
    Bulkhead,
)


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initial_state_is_closed(self):
        """Test that circuit breaker starts in closed state."""
        cb = CircuitBreaker("test-service")
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()

    def test_opens_after_failure_threshold(self):
        """Test that circuit opens after reaching failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test-service", config)

        # Record failures
        for _ in range(3):
            cb.record_failure()

        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()

    def test_success_resets_failure_count(self):
        """Test that success resets the failure count."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test-service", config)

        # Record 2 failures (not enough to open)
        cb.record_failure()
        cb.record_failure()

        # Record a success
        cb.record_success()

        # Record 2 more failures (should not open since count was reset)
        cb.record_failure()
        cb.record_failure()

        assert cb.state == CircuitState.CLOSED

    def test_transitions_to_half_open_after_timeout(self):
        """Test that circuit transitions to half-open after timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.1,  # Very short timeout for testing
        )
        cb = CircuitBreaker("test-service", config)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.15)

        # Check state (should transition to half-open)
        assert cb.state == CircuitState.HALF_OPEN

    def test_half_open_closes_on_success(self):
        """Test that circuit closes after success in half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.05,
        )
        cb = CircuitBreaker("test-service", config)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.1)

        # Should be half-open now
        assert cb.can_execute()

        # Record successes to close
        cb.record_success()
        cb.record_success()

        assert cb.state == CircuitState.CLOSED

    def test_half_open_reopens_on_failure(self):
        """Test that circuit reopens if failure occurs in half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.05,
        )
        cb = CircuitBreaker("test-service", config)

        # Open the circuit
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.1)

        # Should be half-open now
        assert cb.can_execute()

        # Record failure - should reopen
        cb.record_failure()

        assert cb.state == CircuitState.OPEN

    def test_stats_tracking(self):
        """Test that statistics are tracked correctly."""
        cb = CircuitBreaker("test-service")

        cb.record_success()
        cb.record_success()
        cb.record_failure()

        stats = cb.get_stats()
        assert stats.total_calls == 3
        assert stats.successful_calls == 2
        assert stats.failed_calls == 1

    def test_reset(self):
        """Test reset functionality."""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker("test-service", config)

        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()


class TestCircuitBreakerRegistry:
    """Tests for CircuitBreakerRegistry."""

    def test_get_creates_new_breaker(self):
        """Test that get creates a new circuit breaker."""
        registry = CircuitBreakerRegistry()
        cb = registry.get("new-service")
        assert cb is not None
        assert cb.name == "new-service"

    def test_get_returns_same_breaker(self):
        """Test that get returns the same breaker for same name."""
        registry = CircuitBreakerRegistry()
        cb1 = registry.get("test-service")
        cb2 = registry.get("test-service")
        assert cb1 is cb2

    def test_reset_all(self):
        """Test reset_all functionality."""
        registry = CircuitBreakerRegistry()
        
        # Create and open some breakers
        for name in ["svc1", "svc2", "svc3"]:
            cb = registry.get(name, CircuitBreakerConfig(failure_threshold=1))
            cb.record_failure()
            assert cb.state == CircuitState.OPEN

        # Reset all
        registry.reset_all()

        # All should be closed
        for name in ["svc1", "svc2", "svc3"]:
            assert registry.get(name).state == CircuitState.CLOSED


class TestRetryConfig:
    """Tests for RetryConfig and related functions."""

    def test_calculate_backoff_exponential(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            base_delay_seconds=1.0,
            exponential_base=2.0,
            jitter=False,
        )

        assert calculate_backoff(0, config) == 1.0
        assert calculate_backoff(1, config) == 2.0
        assert calculate_backoff(2, config) == 4.0
        assert calculate_backoff(3, config) == 8.0

    def test_calculate_backoff_max_cap(self):
        """Test that backoff is capped at max delay."""
        config = RetryConfig(
            base_delay_seconds=1.0,
            max_delay_seconds=5.0,
            exponential_base=2.0,
            jitter=False,
        )

        assert calculate_backoff(10, config) == 5.0

    def test_calculate_backoff_with_jitter(self):
        """Test that jitter adds randomness."""
        config = RetryConfig(
            base_delay_seconds=1.0,
            jitter=True,
            jitter_factor=0.5,
        )

        # With jitter, values should vary
        delays = [calculate_backoff(0, config) for _ in range(10)]
        unique_delays = set(delays)
        
        # Should have some variation (not all the same)
        assert len(unique_delays) > 1

    def test_is_retryable_error_with_retryable(self):
        """Test is_retryable_error with retryable exception."""
        config = RetryConfig(retryable_exceptions=(ValueError,))
        assert is_retryable_error(ValueError("test"), config)

    def test_is_retryable_error_with_non_retryable(self):
        """Test is_retryable_error with non-retryable exception."""
        config = RetryConfig(
            retryable_exceptions=(ValueError,),
            non_retryable_exceptions=(KeyError,),
        )
        # KeyError should not be retryable even if it matches retryable
        assert not is_retryable_error(KeyError("test"), config)


class TestRetryContext:
    """Tests for RetryContext class."""

    def test_retry_context_success(self):
        """Test RetryContext with successful operation."""
        config = RetryConfig(max_retries=3)
        ctx = RetryContext(config)

        assert ctx.should_retry()
        ctx.success()
        assert not ctx.should_retry()

    def test_retry_context_failure_and_retry(self):
        """Test RetryContext with failure and retry."""
        config = RetryConfig(
            max_retries=3,
            base_delay_seconds=0.01,  # Very short for testing
        )
        ctx = RetryContext(config)

        assert ctx.should_retry()
        ctx.failure(ValueError("error 1"))
        assert ctx.attempt == 1
        
        assert ctx.should_retry()
        ctx.failure(ValueError("error 2"))
        assert ctx.attempt == 2

    def test_retry_context_max_retries_exceeded(self):
        """Test RetryContext when max retries exceeded."""
        config = RetryConfig(
            max_retries=2,
            base_delay_seconds=0.01,
        )
        ctx = RetryContext(config)

        # First call
        ctx.failure(ValueError("error 1"))
        assert ctx.should_retry()  # Can still retry
        
        # Second call
        ctx.failure(ValueError("error 2"))
        assert ctx.should_retry()  # Last retry
        
        # Third call - exceeds max retries
        ctx.failure(ValueError("error 3"))
        
        # Now should_retry raises because we've exhausted retries
        with pytest.raises(ValueError):
            ctx.should_retry()


class TestRetryDecorator:
    """Tests for retry_with_backoff decorator."""

    def test_decorator_success(self):
        """Test decorator with successful function."""
        call_count = 0

        @retry_with_backoff(RetryConfig(max_retries=3))
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count == 1

    def test_decorator_retry_then_success(self):
        """Test decorator that fails then succeeds."""
        call_count = 0

        @retry_with_backoff(RetryConfig(max_retries=3, base_delay_seconds=0.01))
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count == 3

    def test_decorator_exhausts_retries(self):
        """Test decorator when all retries exhausted."""
        call_count = 0

        @retry_with_backoff(RetryConfig(max_retries=2, base_delay_seconds=0.01))
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 3  # Initial + 2 retries


class TestAWSRetryConfig:
    """Tests for AWS-specific retry configuration."""

    def test_is_aws_retryable_error_throttling(self):
        """Test detection of throttling errors."""
        # Create a mock ClientError-like exception
        class MockClientError(Exception):
            def __init__(self, code):
                self.response = {"Error": {"Code": code}}
                super().__init__(code)

        assert is_aws_retryable_error(MockClientError("Throttling"))
        assert is_aws_retryable_error(MockClientError("RequestLimitExceeded"))
        assert not is_aws_retryable_error(MockClientError("InvalidParameterValue"))

    def test_get_aws_retry_config_default(self):
        """Test default AWS retry config."""
        config = get_aws_retry_config()
        assert config.max_retries == 3
        assert config.jitter is True

    def test_get_aws_retry_config_dynamodb(self):
        """Test DynamoDB-specific retry config."""
        config = get_aws_retry_config("dynamodb")
        assert config.max_retries == 10  # DynamoDB needs more retries


class TestBulkhead:
    """Tests for Bulkhead pattern."""

    def test_acquire_within_limit(self):
        """Test acquiring slots within the limit."""
        bulkhead = Bulkhead("test", max_concurrent=3)

        assert bulkhead.acquire(timeout=1)
        assert bulkhead.acquire(timeout=1)
        assert bulkhead.acquire(timeout=1)
        assert bulkhead.active_count == 3

    def test_acquire_at_limit_timeout(self):
        """Test that acquire times out when at limit."""
        bulkhead = Bulkhead("test", max_concurrent=1, max_wait_seconds=0.1)

        assert bulkhead.acquire(timeout=1)
        # Second acquire should timeout
        assert not bulkhead.acquire(timeout=0.1)

    def test_release(self):
        """Test releasing a slot."""
        bulkhead = Bulkhead("test", max_concurrent=1)

        bulkhead.acquire()
        assert bulkhead.active_count == 1

        bulkhead.release()
        assert bulkhead.active_count == 0

    def test_context_manager(self):
        """Test bulkhead as context manager."""
        bulkhead = Bulkhead("test", max_concurrent=2)

        with bulkhead:
            assert bulkhead.active_count == 1
            with bulkhead:
                assert bulkhead.active_count == 2

        assert bulkhead.active_count == 0

    def test_stats(self):
        """Test bulkhead statistics."""
        bulkhead = Bulkhead("test-bulkhead", max_concurrent=2)

        bulkhead.acquire()
        stats = bulkhead.get_stats()

        assert stats["name"] == "test-bulkhead"
        assert stats["max_concurrent"] == 2
        assert stats["active"] == 1
        assert stats["available"] == 1
