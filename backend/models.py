from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class ImageFormat(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"


class ConversionRequest(BaseModel):
    title: Optional[str] = Field(default=None, description="PDF title")
    author: Optional[str] = Field(default=None, description="PDF author")
    password: Optional[str] = Field(default=None, description="PDF password protection")
    resize: bool = Field(default=True, description="Resize to fit page")
    compression: bool = Field(default=True, description="Enable compression")
    orientation: str = Field(default="portrait", description="Portrait or landscape")
    encrypt: bool = Field(default=False, description="Encrypt PDF")
    filename: Optional[str] = Field(default=None, description="Custom output filename")
    individual_files: bool = Field(default=False, description="Create separate PDFs for each image")


class ImageTransformRequest(BaseModel):
    angle: int = Field(default=0, description="Rotation angle (0, 90, 180, 270)")
    crop_left: int = Field(default=0, description="Crop pixels from left")
    crop_top: int = Field(default=0, description="Crop pixels from top")
    crop_right: int = Field(default=0, description="Crop pixels from right")
    crop_bottom: int = Field(default=0, description="Crop pixels from bottom")


class ConversionResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    file_paths: Optional[List[str]] = None  # For individual files
    file_size: Optional[int] = None
    file_sizes: Optional[List[int]] = None  # For individual files
    error_details: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user_id: Optional[str] = None


class FileMetadata(BaseModel):
    filename: str
    size: int
    format: str
    width: Optional[int] = None
    height: Optional[int] = None
