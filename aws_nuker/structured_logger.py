"""
Enhanced JSON-structured logger for AWS Nuker.

Provides structured logging with:
- JSON output format for machine parsing
- Correlation IDs for request tracing
- Sensitive data masking (account IDs, ARNs)
- Log levels with granular control
- Support for multiple output destinations
"""

import json
import logging
import re
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# Context variable for correlation ID
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """Get the current correlation ID or generate a new one."""
    cid = _correlation_id.get()
    if cid is None:
        cid = str(uuid.uuid4())[:8]
        _correlation_id.set(cid)
    return cid


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    _correlation_id.set(correlation_id)


def new_correlation_id() -> str:
    """Generate and set a new correlation ID."""
    cid = str(uuid.uuid4())[:8]
    _correlation_id.set(cid)
    return cid


class SensitiveDataMasker:
    """Masks sensitive data in log messages."""

    # Patterns for sensitive data
    PATTERNS = [
        # AWS Account ID (12 digits)
        (r"\b\d{12}\b", lambda m: "****" + m.group()[-4:]),
        # AWS Access Key ID
        (r"\bAKIA[A-Z0-9]{16}\b", lambda m: "AKIA****" + m.group()[-4:]),
        # AWS Secret Access Key (base64-like, 40 chars)
        (r"(?<=['\"])[A-Za-z0-9+/]{40}(?=['\"])", lambda m: "****MASKED****"),
        # ARN - mask account ID within ARN
        (
            r"arn:aws:[a-z0-9-]+:[a-z0-9-]*:(\d{12}):",
            lambda m: m.group().replace(m.group(1), "****" + m.group(1)[-4:]),
        ),
        # Session tokens
        (r"(?i)session[_-]?token['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9+/=]{20,}", 
         lambda m: "session_token=****MASKED****"),
        # Password patterns
        (r"(?i)password['\"]?\s*[:=]\s*['\"][^'\"]+['\"]", 
         lambda m: "password=****MASKED****"),
    ]

    @classmethod
    def mask(cls, text: str) -> str:
        """
        Mask sensitive data in the given text.

        Args:
            text: Text that may contain sensitive data

        Returns:
            Text with sensitive data masked
        """
        if not isinstance(text, str):
            return text

        result = text
        for pattern, replacer in cls.PATTERNS:
            try:
                result = re.sub(pattern, replacer, result)
            except Exception:
                # If regex fails, continue with original
                pass
        return result


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter."""

    def __init__(self, mask_sensitive: bool = True):
        """
        Initialize JSON formatter.

        Args:
            mask_sensitive: Whether to mask sensitive data
        """
        super().__init__()
        self.mask_sensitive = mask_sensitive

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": get_correlation_id(),
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "taskName"
            )
        }
        if extra_fields:
            log_data["extra"] = extra_fields

        # Mask sensitive data if enabled
        if self.mask_sensitive:
            log_data = self._mask_dict(log_data)

        return json.dumps(log_data, default=str)

    def _mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask sensitive data in a dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = SensitiveDataMasker.mask(value)
            elif isinstance(value, dict):
                result[key] = self._mask_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self._mask_dict(item) if isinstance(item, dict)
                    else SensitiveDataMasker.mask(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


class StructuredLogger:
    """
    Enhanced structured logger with JSON output and correlation IDs.

    Provides comprehensive logging with:
    - JSON structured output
    - Correlation ID tracking
    - Sensitive data masking
    - Audit trail support
    - Multiple output destinations
    """

    def __init__(
        self,
        log_dir: str = "logs",
        audit_dir: str = "audit",
        json_format: bool = True,
        mask_sensitive: bool = True,
    ):
        """
        Initialize the structured logger.

        Args:
            log_dir: Directory for general logs
            audit_dir: Directory for audit trails
            json_format: Use JSON format for logs
            mask_sensitive: Mask sensitive data
        """
        self.log_dir = Path(log_dir)
        self.audit_dir = Path(audit_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.audit_dir.mkdir(exist_ok=True)
        self.json_format = json_format
        self.mask_sensitive = mask_sensitive

        # Create timestamp for log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"aws_nuker_{timestamp}.log"
        self.audit_file = self.audit_dir / f"audit_{timestamp}.jsonl"

        # Setup loggers
        self._setup_main_logger()
        self._setup_audit_logger()

        # Initialize correlation ID for this session
        new_correlation_id()

    def _setup_main_logger(self):
        """Setup the main application logger."""
        self.logger = logging.getLogger("aws_nuker")
        self.logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self.logger.handlers = []

        # File handler with JSON format
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        if self.json_format:
            file_handler.setFormatter(JSONFormatter(mask_sensitive=self.mask_sensitive))
        else:
            file_handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))

        # Console handler with human-readable format
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(levelname)s - [%(correlation_id)s] %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(CorrelationIdFilter())

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _setup_audit_logger(self):
        """Setup the audit trail logger."""
        self.audit_logger = logging.getLogger("aws_nuker_audit")
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.propagate = False
        self.audit_logger.handlers = []

        # Audit file handler - always JSON Lines format
        audit_handler = logging.FileHandler(self.audit_file)
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(JSONFormatter(mask_sensitive=self.mask_sensitive))

        self.audit_logger.addHandler(audit_handler)

    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields."""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields."""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional extra fields."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with optional extra fields."""
        self.logger.critical(message, extra=kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)

    def audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        region: str,
        status: str,
        details: Optional[str] = None,
        **kwargs,
    ):
        """
        Log audit trail entry as structured JSON.

        Args:
            action: Action performed (e.g., "DELETE", "LIST")
            resource_type: Type of AWS resource
            resource_id: Resource identifier
            region: AWS region
            status: Status of operation (SUCCESS, FAILED, SKIPPED)
            details: Additional details
            **kwargs: Additional fields to include
        """
        audit_data = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "region": region,
            "status": status,
            "correlation_id": get_correlation_id(),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        if details:
            audit_data["details"] = details

        audit_data.update(kwargs)

        # Log as structured message
        self.audit_logger.info(
            f"ACTION={action} | TYPE={resource_type} | ID={resource_id} | "
            f"REGION={region} | STATUS={status}",
            extra=audit_data,
        )

    def log_operation_start(
        self,
        operation: str,
        service: str,
        region: str,
        resource_count: Optional[int] = None,
    ):
        """Log the start of an operation."""
        self.info(
            f"Starting {operation} for {service} in {region}",
            operation=operation,
            service=service,
            region=region,
            resource_count=resource_count,
            phase="start",
        )

    def log_operation_end(
        self,
        operation: str,
        service: str,
        region: str,
        duration_seconds: float,
        success_count: int = 0,
        failure_count: int = 0,
        skipped_count: int = 0,
    ):
        """Log the end of an operation with statistics."""
        self.info(
            f"Completed {operation} for {service} in {region} "
            f"({duration_seconds:.2f}s) - Success: {success_count}, "
            f"Failed: {failure_count}, Skipped: {skipped_count}",
            operation=operation,
            service=service,
            region=region,
            duration_seconds=duration_seconds,
            success_count=success_count,
            failure_count=failure_count,
            skipped_count=skipped_count,
            phase="end",
        )

    def log_api_call(
        self,
        service: str,
        operation: str,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
    ):
        """Log an AWS API call."""
        level = logging.DEBUG if success else logging.WARNING
        message = f"API call: {service}.{operation} ({'OK' if success else 'FAILED'}) - {duration_ms:.0f}ms"

        self.logger.log(
            level,
            message,
            extra={
                "api_service": service,
                "api_operation": operation,
                "api_success": success,
                "api_duration_ms": duration_ms,
                "api_error": error,
            },
        )

    def get_log_file(self) -> Path:
        """Get the path to the current log file."""
        return self.log_file

    def get_audit_file(self) -> Path:
        """Get the path to the current audit file."""
        return self.audit_file


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation_id to the record."""
        record.correlation_id = get_correlation_id()
        return True


# ============================================================================
# Metrics Collection
# ============================================================================


class MetricsCollector:
    """
    Simple metrics collector for tracking operation statistics.

    Provides counters and timing metrics that can be exported
    to various monitoring systems.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._counters: Dict[str, int] = {}
        self._timings: Dict[str, list] = {}
        self._start_times: Dict[str, float] = {}

    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        self._counters[metric_name] = self._counters.get(metric_name, 0) + value

    def record_timing(self, metric_name: str, duration_ms: float):
        """Record a timing metric."""
        if metric_name not in self._timings:
            self._timings[metric_name] = []
        self._timings[metric_name].append(duration_ms)

    def start_timer(self, metric_name: str):
        """Start a timer for a metric."""
        self._start_times[metric_name] = time.time()

    def stop_timer(self, metric_name: str) -> float:
        """Stop a timer and record the duration."""
        if metric_name not in self._start_times:
            return 0.0
        duration_ms = (time.time() - self._start_times[metric_name]) * 1000
        del self._start_times[metric_name]
        self.record_timing(metric_name, duration_ms)
        return duration_ms

    def get_counter(self, metric_name: str) -> int:
        """Get the current value of a counter."""
        return self._counters.get(metric_name, 0)

    def get_timing_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a timing metric."""
        timings = self._timings.get(metric_name, [])
        if not timings:
            return {"count": 0, "avg": 0, "min": 0, "max": 0, "p95": 0}

        sorted_timings = sorted(timings)
        count = len(sorted_timings)
        p95_idx = int(count * 0.95)

        return {
            "count": count,
            "avg": sum(sorted_timings) / count,
            "min": sorted_timings[0],
            "max": sorted_timings[-1],
            "p95": sorted_timings[p95_idx] if p95_idx < count else sorted_timings[-1],
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": dict(self._counters),
            "timings": {
                name: self.get_timing_stats(name)
                for name in self._timings
            },
        }

    def reset(self):
        """Reset all metrics."""
        self._counters.clear()
        self._timings.clear()
        self._start_times.clear()


# Global instances
_structured_logger_instance: Optional[StructuredLogger] = None
_metrics_collector: Optional[MetricsCollector] = None


def get_structured_logger() -> StructuredLogger:
    """Get or create the global structured logger instance."""
    global _structured_logger_instance
    if _structured_logger_instance is None:
        _structured_logger_instance = StructuredLogger()
    return _structured_logger_instance


def get_metrics() -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
