import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Setup and configure logger with custom formatting
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        settings.LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def log_excel_loading(file_path: Path, rows: int, columns: int, sheet_name: str = "Sheet1") -> None:
    """
    Log Excel file loading information
    
    Args:
        file_path: Path to the Excel file
        rows: Number of rows loaded
        columns: Number of columns loaded
        sheet_name: Name of the sheet loaded
    """
    logger = setup_logger(__name__)
    logger.info("=" * 80)
    logger.info(f"📊 Loading Excel File: {file_path.name}")
    logger.info(f"📁 Path: {file_path}")
    logger.info(f"📋 Sheet: {sheet_name}")
    logger.info(f"📈 Rows: {rows:,}")
    logger.info(f"📉 Columns: {columns}")
    logger.info("=" * 80)


def log_app_startup() -> None:
    """Log application startup information"""
    logger = setup_logger(__name__)
    logger.info("🚀 Starting AEO/GEO Analytics API")
    logger.info(f"🔧 Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"🌐 Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"📚 API Version: {settings.API_VERSION}")


def log_app_shutdown() -> None:
    """Log application shutdown information"""
    logger = setup_logger(__name__)
    logger.info("🛑 Shutting down AEO/GEO Analytics API")
