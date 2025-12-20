"""Tests for AWS Nuker structured logger."""

import json
import re
import pytest
from aws_nuker.structured_logger import (
    StructuredLogger,
    SensitiveDataMasker,
    JSONFormatter,
    MetricsCollector,
    get_correlation_id,
    set_correlation_id,
    new_correlation_id,
    get_structured_logger,
    get_metrics,
)


class TestSensitiveDataMasker:
    """Tests for SensitiveDataMasker class."""

    def test_mask_account_id(self):
        """Test masking AWS account IDs."""
        text = "Account 123456789012 has resources"
        masked = SensitiveDataMasker.mask(text)
        assert "123456789012" not in masked
        assert "****9012" in masked

    def test_mask_access_key_id(self):
        """Test masking AWS access key IDs."""
        text = "Key: AKIAIOSFODNN7EXAMPLE"
        masked = SensitiveDataMasker.mask(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in masked
        assert "AKIA****" in masked

    def test_mask_arn_account_id(self):
        """Test masking account ID within ARN."""
        text = "arn:aws:s3:us-east-1:123456789012:bucket/my-bucket"
        masked = SensitiveDataMasker.mask(text)
        assert "123456789012" not in masked

    def test_mask_preserves_non_sensitive(self):
        """Test that non-sensitive data is preserved."""
        text = "This is a normal log message without sensitive data"
        masked = SensitiveDataMasker.mask(text)
        assert masked == text

    def test_mask_non_string(self):
        """Test that non-string input returns unchanged."""
        result = SensitiveDataMasker.mask(12345)
        assert result == 12345


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_format_produces_valid_json(self):
        """Test that formatter produces valid JSON."""
        import logging
        
        formatter = JSONFormatter(mask_sensitive=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert "timestamp" in data
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"

    def test_format_includes_correlation_id(self):
        """Test that correlation ID is included."""
        import logging
        
        set_correlation_id("test-123")
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["correlation_id"] == "test-123"


class TestCorrelationId:
    """Tests for correlation ID management."""

    def test_new_correlation_id(self):
        """Test generating new correlation ID."""
        cid = new_correlation_id()
        assert cid is not None
        assert len(cid) == 8

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        set_correlation_id("custom-id")
        assert get_correlation_id() == "custom-id"

    def test_get_generates_if_none(self):
        """Test that get generates ID if none set."""
        # Reset by setting None doesn't work with ContextVar
        # so we just test that we always get something
        cid = get_correlation_id()
        assert cid is not None


class TestMetricsCollector:
    """Tests for MetricsCollector class."""

    def test_increment(self):
        """Test counter increment."""
        collector = MetricsCollector()
        collector.increment("test_counter")
        collector.increment("test_counter", 5)
        
        assert collector.get_counter("test_counter") == 6

    def test_record_timing(self):
        """Test timing recording."""
        collector = MetricsCollector()
        collector.record_timing("api_call", 100)
        collector.record_timing("api_call", 200)
        collector.record_timing("api_call", 150)
        
        stats = collector.get_timing_stats("api_call")
        assert stats["count"] == 3
        assert stats["avg"] == 150.0
        assert stats["min"] == 100
        assert stats["max"] == 200

    def test_timer(self):
        """Test start/stop timer."""
        collector = MetricsCollector()
        collector.start_timer("operation")
        # Small delay
        import time
        time.sleep(0.01)
        duration = collector.stop_timer("operation")
        
        assert duration > 0
        stats = collector.get_timing_stats("operation")
        assert stats["count"] == 1

    def test_get_all_metrics(self):
        """Test getting all metrics."""
        collector = MetricsCollector()
        collector.increment("counter1")
        collector.increment("counter2", 5)
        collector.record_timing("timing1", 100)
        
        metrics = collector.get_all_metrics()
        assert "counters" in metrics
        assert "timings" in metrics
        assert metrics["counters"]["counter1"] == 1
        assert metrics["counters"]["counter2"] == 5

    def test_reset(self):
        """Test resetting metrics."""
        collector = MetricsCollector()
        collector.increment("counter")
        collector.record_timing("timing", 100)
        
        collector.reset()
        
        assert collector.get_counter("counter") == 0
        assert collector.get_timing_stats("timing")["count"] == 0

    def test_timing_stats_empty(self):
        """Test timing stats for non-existent metric."""
        collector = MetricsCollector()
        stats = collector.get_timing_stats("nonexistent")
        assert stats["count"] == 0
        assert stats["avg"] == 0


class TestStructuredLogger:
    """Tests for StructuredLogger class."""

    def test_logger_creation(self, tmp_path):
        """Test logger creation."""
        log_dir = tmp_path / "logs"
        audit_dir = tmp_path / "audit"
        
        logger = StructuredLogger(
            log_dir=str(log_dir),
            audit_dir=str(audit_dir),
        )
        
        assert log_dir.exists()
        assert audit_dir.exists()
        assert logger.get_log_file().exists()

    def test_log_methods(self, tmp_path):
        """Test various log methods."""
        logger = StructuredLogger(
            log_dir=str(tmp_path / "logs"),
            audit_dir=str(tmp_path / "audit"),
        )
        
        # These should not raise
        logger.info("Info message")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_audit_log(self, tmp_path):
        """Test audit logging."""
        logger = StructuredLogger(
            log_dir=str(tmp_path / "logs"),
            audit_dir=str(tmp_path / "audit"),
        )
        
        logger.audit(
            action="DELETE",
            resource_type="ec2:instance",
            resource_id="i-123",
            region="us-east-1",
            status="SUCCESS",
            details="Test deletion",
        )
        
        # Read audit file
        audit_content = logger.get_audit_file().read_text()
        assert "DELETE" in audit_content
        assert "SUCCESS" in audit_content

    def test_log_operation_start_end(self, tmp_path):
        """Test operation logging."""
        logger = StructuredLogger(
            log_dir=str(tmp_path / "logs"),
            audit_dir=str(tmp_path / "audit"),
        )
        
        logger.log_operation_start("cleanup", "ec2", "us-east-1", 5)
        logger.log_operation_end(
            "cleanup", "ec2", "us-east-1",
            duration_seconds=10.5,
            success_count=4,
            failure_count=1,
        )
        
        log_content = logger.get_log_file().read_text()
        assert "cleanup" in log_content
        assert "ec2" in log_content


class TestGlobalInstances:
    """Tests for global instance getters."""

    def test_get_structured_logger_singleton(self):
        """Test that get_structured_logger returns same instance."""
        logger1 = get_structured_logger()
        logger2 = get_structured_logger()
        assert logger1 is logger2

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns same instance."""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2
