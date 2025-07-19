"""
Unit tests for structured JSON logging functionality.

Tests validate that logs are properly formatted as JSON and contain required fields.
"""

import json
import logging
import tempfile
from io import StringIO
from pathlib import Path
import pytest
import structlog
import sys

from azdo_process_export.infrastructure.logging import setup_logging, get_logger, get_trace_logger


class TestStructuredLogging:
    """Test structured logging functionality."""

    def setup_method(self):
        """Reset logging configuration before each test."""
        # Clear any existing structlog configuration
        structlog.reset_defaults()
        # Clear standard library loggers
        logging.getLogger().handlers.clear()
        logging.getLogger().setLevel(logging.NOTSET)

    def _capture_logs(self, log_level="info", enable_trace=False):
        """Helper to capture logs to a StringIO buffer."""
        log_buffer = StringIO()
        
        # Configure logging to write to our buffer instead of stdout
        logging.basicConfig(
            format="%(message)s",
            stream=log_buffer,
            level=getattr(logging, log_level.upper()),
            force=True
        )
        
        # Configure structlog with the same setup as our main function
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        if enable_trace:
            from azdo_process_export.infrastructure.logging import _add_trace_context
            processors.append(_add_trace_context)
        
        processors.append(structlog.processors.JSONRenderer())
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            context_class=dict,
            cache_logger_on_first_use=True,
        )
        
        return log_buffer

    def test_setup_logging_default_level(self):
        """Test default logging setup with info level."""
        log_buffer = self._capture_logs("info")
        logger = get_logger("test_module")
        
        logger.info("Test message", key="value")
        
        log_line = log_buffer.getvalue().strip()
        
        # Should be valid JSON
        log_data = json.loads(log_line)
        
        # Check required fields
        assert log_data["event"] == "Test message"
        assert log_data["key"] == "value"
        assert log_data["logger"] == "test_module"
        assert log_data["level"] == "info"
        assert "timestamp" in log_data
        
        # Timestamp should be ISO format
        assert log_data["timestamp"].endswith("Z")

    def test_setup_logging_debug_level(self):
        """Test logging setup with debug level."""
        log_buffer = self._capture_logs("debug")
        logger = get_logger("test_module")
        
        logger.debug("Debug message", debug_info="test")
        
        log_line = log_buffer.getvalue().strip()
        log_data = json.loads(log_line)
        
        assert log_data["event"] == "Debug message"
        assert log_data["debug_info"] == "test"
        assert log_data["level"] == "debug"

    def test_setup_logging_trace_level(self):
        """Test logging setup with trace level and trace context."""
        log_buffer = self._capture_logs("debug", enable_trace=True)
        logger = get_logger("test_module")
        
        logger.debug("Trace message", trace_data="test")
        
        log_line = log_buffer.getvalue().strip()
        log_data = json.loads(log_line)
        
        assert log_data["event"] == "Trace message"
        assert log_data["trace_data"] == "test"
        assert log_data["level"] == "debug"  # trace maps to debug in Python logging
        assert "trace" in log_data
        assert "thread_id" in log_data["trace"]
        assert "thread_name" in log_data["trace"]

    def test_file_logging(self, tmp_path):
        """Test logging to file functionality."""
        log_file = tmp_path / "test.log"
        setup_logging(log_level="info", log_file=log_file)
        logger = get_logger("test_module")
        
        logger.info("File test message", file_key="file_value")
        
        # Check file was created and contains JSON log
        assert log_file.exists()
        log_content = log_file.read_text().strip()
        log_data = json.loads(log_content)
        
        assert log_data["event"] == "File test message"
        assert log_data["file_key"] == "file_value"
        assert log_data["logger"] == "test_module"

    def test_multiple_log_entries(self):
        """Test multiple log entries are properly formatted."""
        log_buffer = self._capture_logs("info")
        logger = get_logger("test_module")
        
        logger.info("First message", count=1)
        logger.warning("Warning message", count=2)
        logger.error("Error message", count=3)
        
        log_lines = log_buffer.getvalue().strip().split("\n")
        
        assert len(log_lines) == 3
        
        for i, line in enumerate(log_lines, 1):
            log_data = json.loads(line)
            assert log_data["count"] == i
            assert "timestamp" in log_data
            assert "logger" in log_data
            assert "level" in log_data

    def test_get_trace_logger(self):
        """Test trace logger functionality."""
        log_buffer = self._capture_logs("info", enable_trace=True)
        logger = get_trace_logger("trace_module")
        
        logger.info("Trace logger test", trace_enabled=True)
        
        log_line = log_buffer.getvalue().strip()
        log_data = json.loads(log_line)
        
        assert log_data["event"] == "Trace logger test"
        assert log_data["trace_enabled"] is True
        assert log_data["logger"] == "trace_module"

    def test_structured_data_types(self):
        """Test logging with various data types."""
        log_buffer = self._capture_logs("info")
        logger = get_logger("test_module")
        
        logger.info(
            "Complex data test",
            string_val="test",
            int_val=42,
            float_val=3.14,
            bool_val=True,
            list_val=[1, 2, 3],
            dict_val={"nested": "value"}
        )
        
        log_line = log_buffer.getvalue().strip()
        log_data = json.loads(log_line)
        
        assert log_data["string_val"] == "test"
        assert log_data["int_val"] == 42
        assert log_data["float_val"] == 3.14
        assert log_data["bool_val"] is True
        assert log_data["list_val"] == [1, 2, 3]
        assert log_data["dict_val"] == {"nested": "value"}

    def test_exception_logging(self):
        """Test exception logging includes stack trace."""
        log_buffer = self._capture_logs("info")
        logger = get_logger("test_module")
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred", error_context="test")
        
        log_line = log_buffer.getvalue().strip()
        log_data = json.loads(log_line)
        
        assert log_data["event"] == "Exception occurred"
        assert log_data["error_context"] == "test"
        assert log_data["level"] == "error"
        assert "exception" in log_data
        assert "ValueError: Test exception" in log_data["exception"]

    def test_log_level_filtering(self):
        """Test that log level filtering works correctly."""
        log_buffer = self._capture_logs("warning")
        logger = get_logger("test_module")
        
        logger.debug("Should not appear")
        logger.info("Should not appear")
        logger.warning("Should appear")
        logger.error("Should appear")
        
        log_output = log_buffer.getvalue().strip()
        log_lines = log_output.split("\n") if log_output else []
        
        # Should only have warning and error
        assert len(log_lines) == 2
        
        warning_data = json.loads(log_lines[0])
        error_data = json.loads(log_lines[1])
        
        assert warning_data["event"] == "Should appear"
        assert warning_data["level"] == "warning"
        assert error_data["event"] == "Should appear"
        assert error_data["level"] == "error"

    def test_logger_name_consistency(self):
        """Test that logger names are properly preserved."""
        log_buffer = self._capture_logs("info")
        
        logger1 = get_logger("module1")
        logger2 = get_logger("module2.submodule")
        
        logger1.info("Message from module1")
        logger2.info("Message from submodule")
        
        log_lines = log_buffer.getvalue().strip().split("\n")
        
        log1_data = json.loads(log_lines[0])
        log2_data = json.loads(log_lines[1])
        
        assert log1_data["logger"] == "module1"
        assert log2_data["logger"] == "module2.submodule"

    def test_integration_with_setup_logging(self, tmp_path):
        """Test integration with the main setup_logging function."""
        # Test that the public API works correctly
        log_file = tmp_path / "integration.log"
        setup_logging(log_level="debug", log_file=log_file, enable_trace=True)
        
        logger = get_logger("integration_test")
        logger.info("Integration test message", test_key="test_value")
        
        # Verify file output
        assert log_file.exists()
        log_content = log_file.read_text().strip()
        log_data = json.loads(log_content)
        
        assert log_data["event"] == "Integration test message"
        assert log_data["test_key"] == "test_value"
        assert log_data["logger"] == "integration_test"
        assert log_data["level"] == "info"
        assert "timestamp" in log_data