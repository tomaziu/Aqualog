import sys
from pathlib import Path

from loguru import logger

Path("logs").mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Add stdout logger with simple format for development
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add file logger with rotation and JSON serialization for production
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    serialize=True,  # JSON output
)

# Separate error log
logger.add(
    "logs/error.log",
    rotation="10 MB",
    retention="10 days",
    level="ERROR",
    serialize=True,
    backtrace=True,
    diagnose=True,
)

__all__ = ["logger"]
