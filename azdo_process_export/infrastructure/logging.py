"""
Structured JSON logging configuration using structlog.

Provides consistent JSON logging across all modules following Better Stack guidance.
Supports different log levels (info, debug, trace) and outputs to stdout and optional file.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

import structlog


def setup_logging(
    log_level: str = "info",
    log_file: Optional[Path] = None,
    enable_trace: bool = False
) -> None:
    """
    Configure structured JSON logging for the application.
    
    Args:
        log_level: Log level (info, debug, trace)
        log_file: Optional file path for log output
        enable_trace: Enable trace-level logging
    """
    # Map string levels to logging constants
    level_map = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "trace": logging.DEBUG,  # Python logging doesn't have TRACE, use DEBUG
    }
    
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # Configure standard library logging to use stdout
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True  # Override any existing configuration
    )
    
    # Configure structlog
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
    
    # Add trace context processor for trace level
    if enable_trace or log_level.lower() == "trace":
        processors.append(_add_trace_context)
    
    # Use JSON renderer for structured output
    processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Configure file logging if specified
    if log_file:
        _setup_file_logging(log_file, level)


def _add_trace_context(logger: Any, name: str, event_dict: dict) -> dict:
    """Add trace context information to log entries."""
    import traceback
    import threading
    
    event_dict["trace"] = {
        "thread_id": threading.get_ident(),
        "thread_name": threading.current_thread().name,
    }
    
    # Add stack trace for debug/trace levels
    if event_dict.get("level") in ("debug", "trace"):
        stack = traceback.extract_stack()
        # Get the caller frame (skip logging infrastructure frames)
        caller_frame = None
        for frame in reversed(stack):
            if not any(skip in frame.filename for skip in ["logging", "structlog"]):
                caller_frame = frame
                break
        
        if caller_frame:
            event_dict["trace"]["caller"] = {
                "filename": caller_frame.filename,
                "line": caller_frame.lineno,
                "function": caller_frame.name,
            }
    
    return event_dict


def _setup_file_logging(log_file: Path, level: int) -> None:
    """Setup file logging handler."""
    # Ensure directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add file handler to root logger
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    
    logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a properly configured logger for a module.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def get_trace_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger with trace-level context enabled.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured structlog logger with trace context
    """
    logger = structlog.get_logger(name)
    return logger.bind(trace_enabled=True)