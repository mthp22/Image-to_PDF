from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import FileResponse
from typing import List, Optional
import logging
from pathlib import Path
from datetime import datetime

from models import ConversionRequest, ConversionResponse, HealthResponse, ImageTransformRequest
from services.converter import ImageToPDFConverter
from services.utils import get_file_size_mb, is_supported_image
from auth import get_current_user, auth_manager
from security import verify_api_key, RequestValidator, api_key_manager

logger = logging.getLogger(__name__)
router = APIRouter()
converter = ImageToPDFConverter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/auth/register")
async def register(email: str = Form(...), password: str = Form(...)):
    """Register a new user."""
    try:
        RequestValidator.validate_password(password)
        user = auth_manager.create_user(email, password)
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user["uid"],
            "email": user["email"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return {
            "success": False,
            "message": "Registration failed",
            "error_details": str(e),
        }


@router.get("/auth/user")
async def get_user(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        user = auth_manager.get_user(current_user["uid"])
        return {
            "success": True,
            "user": user,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return {
            "success": False,
            "message": "Failed to get user",
            "error_details": str(e),
        }


# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

@router.post("/api-key/generate")
async def generate_api_key(current_user: dict = Depends(get_current_user)):
    """Generate a new API key for the user."""
    try:
        new_key = api_key_manager.generate_key()
        return {
            "success": True,
            "message": "API key generated",
            "api_key": new_key,
            "user_id": current_user["uid"],
        }
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        return {
            "success": False,
            "message": "Failed to generate API key",
            "error_details": str(e),
        }


# ============================================================================
# CONVERSION ENDPOINTS (ENHANCED)
# ============================================================================

@router.post("/convert", response_model=ConversionResponse)
async def convert_multiple(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    encrypt: bool = Form(False),
    resize: bool = Form(True),
    compression: bool = Form(True),
    filename: Optional[str] = Form(None),
    individual_files: bool = Form(False),
    x_api_key: str = Header(None),
):
    """
    Convert multiple images to PDF(s).
    
    Can create single PDF or individual PDFs per image.
    Supports encryption and custom filenames.
    """
    try:
        # Validate API key if provided
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

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

        metadata = {}
        if title:
            metadata["title"] = title
        if author:
            metadata["author"] = author
        if password:
            metadata["password"] = password

        # Convert
        if individual_files:
            # Create separate PDF for each image
            file_paths = []
            file_sizes = []
            
            for image_content, image_name in image_files:
                pdf_bytes, msg = converter.convert_single(
                    image_content,
                    image_name,
                    metadata=metadata,
                    resize=resize,
                    compression=compression,
                )

                # Encrypt if requested
                if encrypt:
                    pdf_bytes = converter.encrypt_pdf(pdf_bytes, password or "default")

                # Save with custom or auto filename
                if filename:
                    base_name = RequestValidator.validate_filename(filename)
                    pdf_filename = f"{base_name}_{Path(image_name).stem}.pdf"
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_filename = f"{Path(image_name).stem}_{timestamp}.pdf"

                pdf_path = converter.save_pdf(pdf_bytes, pdf_filename)
                file_paths.append(str(pdf_path))
                file_sizes.append(len(pdf_bytes))

            return ConversionResponse(
                success=True,
                message=f"Successfully converted {len(files)} images to {len(file_paths)} PDF(s)",
                file_paths=file_paths,
                file_sizes=file_sizes,
            )
        else:
            # Combine into single PDF
            pdf_bytes, msg = converter.convert_multiple(
                image_files,
                metadata=metadata,
                resize=resize,
                compression=compression,
            )

            # Encrypt if requested
            if encrypt:
                pdf_bytes = converter.encrypt_pdf(pdf_bytes, password or "default")

            # Save with custom or auto filename
            if filename:
                pdf_filename = RequestValidator.validate_filename(filename)
                if not pdf_filename.endswith(".pdf"):
                    pdf_filename += ".pdf"
            else:
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
        logger.error(f"Error converting images: {e}")
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
    encrypt: bool = Form(False),
    resize: bool = Form(True),
    compression: bool = Form(True),
    filename: Optional[str] = Form(None),
    x_api_key: str = Header(None),
):
    """Convert a single image to PDF with encryption support."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

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

        metadata = {}
        if title:
            metadata["title"] = title
        if author:
            metadata["author"] = author
        if password:
            metadata["password"] = password

        pdf_bytes, msg = converter.convert_single(
            content,
            file.filename,
            metadata=metadata,
            resize=resize,
            compression=compression,
        )

        # Encrypt if requested
        if encrypt:
            pdf_bytes = converter.encrypt_pdf(pdf_bytes, password or "default")

        # Save with custom filename
        if filename:
            pdf_filename = RequestValidator.validate_filename(filename)
            if not pdf_filename.endswith(".pdf"):
                pdf_filename += ".pdf"
        else:
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


# ============================================================================
# IMAGE TRANSFORMATION ENDPOINTS
# ============================================================================

@router.post("/transform/rotate")
async def rotate_image(
    file: UploadFile = File(...),
    angle: int = Form(90),
    x_api_key: str = Header(None),
):
    """Rotate image by specified angle."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

        if angle not in [0, 90, 180, 270]:
            raise HTTPException(status_code=400, detail="Angle must be 0, 90, 180, or 270")

        content = await file.read()
        rotated = converter.rotate_image(content, angle)

        return {
            "success": True,
            "message": f"Image rotated {angle} degrees",
            "size": len(rotated),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rotating image: {e}")
        return {
            "success": False,
            "message": "Rotation failed",
            "error_details": str(e),
        }


@router.post("/transform/crop")
async def crop_image(
    file: UploadFile = File(...),
    left: int = Form(0),
    top: int = Form(0),
    right: int = Form(0),
    bottom: int = Form(0),
    x_api_key: str = Header(None),
):
    """Crop image by specified pixels."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

        content = await file.read()
        cropped = converter.crop_image(content, left, top, right, bottom)

        return {
            "success": True,
            "message": "Image cropped successfully",
            "size": len(cropped),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cropping image: {e}")
        return {
            "success": False,
            "message": "Cropping failed",
            "error_details": str(e),
        }


# ============================================================================
# FILE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/download/{filename}")
async def download_pdf(
    filename: str,
    x_api_key: str = Header(None),
):
    """Download a converted PDF file."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Sanitize filename
        filename = RequestValidator.validate_filename(filename)
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


@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    x_api_key: str = Header(None),
):
    """Delete a converted PDF file."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

        filename = RequestValidator.validate_filename(filename)
        file_path = converter.output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        converter.cleanup_file(file_path)
        return {"success": True, "message": "File deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Delete failed")


@router.get("/files/list")
async def list_files(x_api_key: str = Header(None)):
    """List all available PDF files."""
    try:
        if x_api_key and not api_key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

        files = []
        for file_path in converter.output_dir.glob("*.pdf"):
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created": file_path.stat().st_mtime,
            })

        return {
            "success": True,
            "files": files,
            "count": len(files),
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {
            "success": False,
            "message": "Failed to list files",
            "error_details": str(e),
        }
