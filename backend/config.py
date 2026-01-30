import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""

    # App
    APP_NAME = "Image to PDF Converter"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = Path("./logs")

    # File handling
    UPLOAD_DIR = Path("./uploads")
    OUTPUT_DIR = Path("./converted_pdfs")
    TEMP_DIR = Path("./temp")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB

    # Image processing
    SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "bmp", "tiff", "tif"}
    MAX_IMAGE_DIMENSION = 20000  # pixels
    TARGET_PDF_WIDTH = 2100  # A4 width in pixels
    TARGET_PDF_HEIGHT = 2970  # A4 height in pixels
    JPEG_QUALITY = 95
    PNG_QUALITY = 95

    # CORS
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:5000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5000",
        "*",  # Allow all for development
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    # PDF settings
    PDF_COMPRESSION_ENABLED = True
    PDF_COMPRESSION_LEVEL = 6  # 0-9

    # Cleanup
    CLEANUP_ON_STARTUP = True
    CLEANUP_AGE_DAYS = 7  # Delete PDFs older than 7 days

    @classmethod
    def create_directories(cls):
        """Create required directories."""
        cls.LOG_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_config(cls):
        """Get configuration as dictionary."""
        return {
            "app_name": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "debug": cls.DEBUG,
            "host": cls.HOST,
            "port": cls.PORT,
            "log_level": cls.LOG_LEVEL,
            "max_file_size": cls.MAX_FILE_SIZE,
            "supported_formats": list(cls.SUPPORTED_FORMATS),
            "pdf_compression": cls.PDF_COMPRESSION_ENABLED,
        }


# Create settings instance
settings = Settings()

# Initialize directories on import
settings.create_directories()
