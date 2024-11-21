"""Logging utilities for consistent logging across the project."""
import logging
from functools import wraps
from typing import Any, Callable


def log_operation(logger: logging.Logger):
    """Decorator to log operation entry and exit with timing."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            operation = func.__name__.replace("_", " ").title()
            logger.info(f"Starting {operation}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation}")
                return result

            except Exception as e:
                logger.error(f"Error in {operation}: {str(e)}")
                raise

        return wrapper

    return decorator


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up logging with consistent formatting."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
