"""
Logger configuration for AWS Nuker.

Provides centralized logging functionality with file and console output,
including audit trail capabilities.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class NukerLogger:
    """Centralized logging system for AWS Nuker."""

    def __init__(self, log_dir: str = "logs", audit_dir: str = "audit"):
        """
        Initialize the logger.

        Args:
            log_dir: Directory for general logs
            audit_dir: Directory for audit trails
        """
        self.log_dir = Path(log_dir)
        self.audit_dir = Path(audit_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.audit_dir.mkdir(exist_ok=True)

        # Create timestamp for log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"aws_nuker_{timestamp}.log"
        self.audit_file = self.audit_dir / f"audit_{timestamp}.log"

        # Setup loggers
        self._setup_main_logger()
        self._setup_audit_logger()

    def _setup_main_logger(self):
        """Setup the main application logger."""
        self.logger = logging.getLogger("aws_nuker")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _setup_audit_logger(self):
        """Setup the audit trail logger."""
        self.audit_logger = logging.getLogger("aws_nuker_audit")
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.propagate = False

        # Audit file handler
        audit_handler = logging.FileHandler(self.audit_file)
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        audit_handler.setFormatter(audit_formatter)

        self.audit_logger.addHandler(audit_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

    def audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        region: str,
        status: str,
        details: Optional[str] = None,
    ):
        """
        Log audit trail entry.

        Args:
            action: Action performed (e.g., "DELETE", "LIST")
            resource_type: Type of AWS resource
            resource_id: Resource identifier
            region: AWS region
            status: Status of operation (SUCCESS, FAILED, SKIPPED)
            details: Additional details
        """
        audit_msg = (
            f"ACTION={action} | TYPE={resource_type} | "
            f"ID={resource_id} | REGION={region} | STATUS={status}"
        )
        if details:
            audit_msg += f" | DETAILS={details}"

        self.audit_logger.info(audit_msg)

    def get_log_file(self) -> Path:
        """Get the path to the current log file."""
        return self.log_file

    def get_audit_file(self) -> Path:
        """Get the path to the current audit file."""
        return self.audit_file


# Global logger instance
_logger_instance: Optional[NukerLogger] = None


def get_logger() -> NukerLogger:
    """Get or create the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = NukerLogger()
    return _logger_instance
