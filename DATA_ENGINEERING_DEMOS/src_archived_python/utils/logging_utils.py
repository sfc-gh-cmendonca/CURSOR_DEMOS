"""
Logging Configuration and Utilities
"""
import logging
import sys
from datetime import datetime
from config import DataEngDemoConfig


def setup_logger(name: str = "data_eng_demo", level: str = None) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR) - uses config default if None
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logger("pipeline")
        >>> logger.info("Pipeline started")
    """
    if level is None:
        level = DataEngDemoConfig.LOG_LEVEL
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_step(logger: logging.Logger, step_name: str, status: str = "START") -> None:
    """
    Log a pipeline step with consistent formatting
    
    Args:
        logger: Logger instance
        step_name: Name of the step
        status: Status (START, COMPLETE, FAILED)
    
    Example:
        >>> logger = setup_logger()
        >>> log_step(logger, "Data Ingestion", "START")
        >>> # ... do work ...
        >>> log_step(logger, "Data Ingestion", "COMPLETE")
    """
    symbols = {
        "START": "▶️",
        "COMPLETE": "✅",
        "FAILED": "❌",
        "WARNING": "⚠️"
    }
    
    symbol = symbols.get(status, "📍")
    separator = "=" * 80
    
    if status == "START":
        logger.info(f"\n{separator}")
        logger.info(f"{symbol} {step_name} - {status}")
        logger.info(f"{separator}")
    elif status == "COMPLETE":
        logger.info(f"{symbol} {step_name} - {status}")
        logger.info(f"{separator}\n")
    else:
        logger.log(
            logging.ERROR if status == "FAILED" else logging.WARNING,
            f"{symbol} {step_name} - {status}"
        )


def log_metrics(logger: logging.Logger, metrics: dict) -> None:
    """
    Log metrics in a formatted way
    
    Args:
        logger: Logger instance
        metrics: Dictionary of metric names and values
    
    Example:
        >>> log_metrics(logger, {
        ...     "rows_processed": 10000,
        ...     "duration_seconds": 45.2,
        ...     "success_rate": 0.98
        ... })
    """
    logger.info("📊 Metrics:")
    for key, value in metrics.items():
        # Format numbers nicely
        if isinstance(value, float):
            formatted_value = f"{value:.2f}"
        elif isinstance(value, int):
            formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)
        
        logger.info(f"   {key}: {formatted_value}")


class PipelineTimer:
    """
    Context manager for timing pipeline operations
    
    Example:
        >>> logger = setup_logger()
        >>> with PipelineTimer(logger, "Data Load"):
        ...     # Do work
        ...     pass
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        log_step(self.logger, self.operation_name, "START")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            log_step(self.logger, self.operation_name, "COMPLETE")
            self.logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        else:
            log_step(self.logger, self.operation_name, "FAILED")
            self.logger.error(f"❌ Error: {exc_val}")
        
        return False  # Don't suppress exceptions

