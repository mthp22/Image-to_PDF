import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os


def setup_logging(log_dir: str = "./logs", log_level: int = logging.INFO):
    """Configure logging with file and console handlers."""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    log_file = log_path / "app.log"

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert bytes to MB."""
    return round(file_size_bytes / (1024 * 1024), 2)


def get_file_extension(filename: str) -> str:
    """Get file extension without dot."""
    return Path(filename).suffix.lstrip(".").lower()


def is_supported_image(filename: str) -> bool:
    """Check if file is a supported image format."""
    supported = {"jpeg", "jpg", "png", "bmp", "tiff", "tif"}
    return get_file_extension(filename) in supported


def cleanup_temp_files(directory: str, pattern: str = "*"):
    """Clean up temporary files in directory."""
    try:
        path = Path(directory)
        if path.exists():
            for file in path.glob(pattern):
                if file.is_file():
                    file.unlink()
    except Exception as e:
        logging.error(f"Error cleaning up temp files: {e}")
