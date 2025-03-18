"""
Logger Module

This module provides logging functionality for the BVL Data Fetcher application.
It configures loggers with appropriate handlers and formatters.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SMTPHandler

# Optional: For colored console output
try:
    import colorlog

    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


def setup_logger(
        name: str,
        log_level: str = "INFO",
        log_dir: str = "logs",
        log_to_console: bool = True,
        log_to_file: bool = True,
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        use_rotating_file: bool = True,
        use_timed_rotation: bool = False,
        use_colors: bool = True,
        include_line_info: bool = False,
        include_process_info: bool = False,
) -> logging.Logger:
    """
    Set up and configure a logger with specified parameters.

    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory where log files will be stored
        log_to_console: Whether to output logs to console
        log_to_file: Whether to output logs to file
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        use_rotating_file: Use size-based file rotation
        use_timed_rotation: Use time-based file rotation
        use_colors: Use colored output for console logs
        include_line_info: Include file, function, and line number in logs
        include_process_info: Include process and thread info in logs

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers if any (prevents duplicate logs)
    if logger.handlers:
        logger.handlers.clear()

    # Create formatter with appropriate information
    log_format = []
    log_format.append("%(asctime)s")
    log_format.append("%(name)s")
    log_format.append("%(levelname)s")

    if include_line_info:
        log_format.append("%(filename)s:%(lineno)d")
        log_format.append("%(funcName)s")

    if include_process_info:
        log_format.append("PID:%(process)d")
        log_format.append("TID:%(thread)d")

    log_format.append("%(message)s")

    formatter = logging.Formatter(" - ".join(log_format))

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)

        if use_colors and COLORLOG_AVAILABLE:
            color_formatter = colorlog.ColoredFormatter(
                "%(log_color)s" + " - ".join(log_format),
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

        if use_rotating_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
        elif use_timed_rotation:
            file_handler = TimedRotatingFileHandler(
                log_file,
                when="midnight",
                interval=1,
                backupCount=30
            )
        else:
            file_handler = logging.FileHandler(log_file)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def add_email_handler(
        logger: logging.Logger,
        mailhost: str,
        fromaddr: str,
        toaddrs: list,
        subject: str,
        credentials: tuple = None,
        secure: tuple = None,
        level: str = "ERROR"
) -> None:
    """
    Add an email handler to a logger for sending error notifications.

    Args:
        logger: Logger to add the email handler to
        mailhost: SMTP mail host
        fromaddr: From email address
        toaddrs: List of to email addresses
        subject: Email subject
        credentials: (username, password) tuple
        secure: Tuple for secure connection (see SMTPHandler docs)
        level: Log level for sending emails
    """
    mail_handler = SMTPHandler(
        mailhost=mailhost,
        fromaddr=fromaddr,
        toaddrs=toaddrs,
        subject=subject,
        credentials=credentials,
        secure=secure
    )
    mail_handler.setLevel(getattr(logging, level))
    mail_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(mail_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name.

    Args:
        name: Logger name to retrieve

    Returns:
        The requested logger or the root logger if not found
    """
    return logging.getLogger(name)


def clean_old_logs(log_dir: str, days: int = 30) -> int:
    """
    Clean up log files older than the specified number of days.

    Args:
        log_dir: Directory containing log files
        days: Delete files older than this many days

    Returns:
        Number of files deleted
    """
    import time
    from pathlib import Path

    now = time.time()
    cutoff = now - (days * 86400)
    deleted = 0

    log_path = Path(log_dir)
    if not log_path.exists():
        return 0

    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff:
            log_file.unlink()
            deleted += 1

    return deleted


# Additional useful function
def log_exceptions(logger: logging.Logger):
    """
    Decorator to log exceptions raised in functions.

    Usage:
        @log_exceptions(my_logger)
        def my_function():
            ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {str(e)}")
                raise

        return wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    # Test the logger
    test_logger = setup_logger(
        "TestLogger",
        log_level="DEBUG",
        include_line_info=True
    )

    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    try:
        1 / 0
    except Exception as e:
        test_logger.exception("Caught an exception")