from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
import logging
from pathlib import Path
from datetime import datetime

from models import ConversionRequest, ConversionResponse, HealthResponse
from services.converter import ImageToPDFConverter
from services.utils import get_file_size_mb, is_supported_image

logger = logging.getLogger(__name__)
router = APIRouter()
converter = ImageToPDFConverter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@router.post("/convert", response_model=ConversionResponse)
async def convert_multiple(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    resize: bool = Form(True),
    compression: bool = Form(True),
):
    """
    Convert multiple images to a single PDF.

    - **files**: List of image files (JPEG, PNG, BMP, TIFF)
    - **title**: Optional PDF title
    - **author**: Optional PDF author
    - **password**: Optional password protection
    - **resize**: Resize images to fit A4 page
    - **compression**: Enable compression
    """
    try:
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")

        # Validate all files
        image_files = []
        for file in files:
            if not is_supported_image(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file.filename}",
                )

            content = await file.read()
            valid, msg = converter.validate_image(content, file.filename)
            if not valid:
                raise HTTPException(status_code=400, detail=f"{file.filename}: {msg}")

            image_files.append((content, file.filename))

        # Convert
        metadata = {}
        if title:
            metadata["title"] = title
        if author:
            metadata["author"] = author

        pdf_bytes, msg = converter.convert_multiple(
            image_files, metadata=metadata, resize=resize, compression=compression
        )

        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"combined_{timestamp}.pdf"
        pdf_path = converter.save_pdf(pdf_bytes, pdf_filename)

        logger.info(f"Successfully converted {len(files)} images to {pdf_filename}")

        return ConversionResponse(
            success=True,
            message="Successfully converted images to PDF",
            file_path=str(pdf_path),
            file_size=len(pdf_bytes),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting multiple images: {e}")
        return ConversionResponse(
            success=False,
            message="Conversion failed",
            error_details=str(e),
        )


@router.post("/convert-single", response_model=ConversionResponse)
async def convert_single(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    resize: bool = Form(True),
    compression: bool = Form(True),
):
    """
    Convert a single image to PDF.

    - **file**: Single image file (JPEG, PNG, BMP, TIFF)
    - **title**: Optional PDF title
    - **author**: Optional PDF author
    - **password**: Optional password protection
    - **resize**: Resize image to fit A4 page
    - **compression**: Enable compression
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        if not is_supported_image(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file.filename}",
            )

        content = await file.read()
        valid, msg = converter.validate_image(content, file.filename)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

        # Convert
        metadata = {}
        if title:
            metadata["title"] = title
        if author:
            metadata["author"] = author

        pdf_bytes, msg = converter.convert_single(
            content, file.filename, metadata=metadata, resize=resize, compression=compression
        )

        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{Path(file.filename).stem}_{timestamp}.pdf"
        pdf_path = converter.save_pdf(pdf_bytes, pdf_filename)

        logger.info(f"Successfully converted {file.filename} to {pdf_filename}")

        return ConversionResponse(
            success=True,
            message="Successfully converted image to PDF",
            file_path=str(pdf_path),
            file_size=len(pdf_bytes),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting image: {e}")
        return ConversionResponse(
            success=False,
            message="Conversion failed",
            error_details=str(e),
        )


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """Download a converted PDF file."""
    try:
        file_path = converter.output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail="Download failed")
