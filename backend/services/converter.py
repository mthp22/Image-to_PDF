import io
import os
from pathlib import Path
from typing import List
from PIL import Image
import img2pdf
import logging

logger = logging.getLogger(__name__)


class ImageToPDFConverter:
    """Convert images to PDF with preprocessing and metadata support."""

    def __init__(self, config=None):
        """Initialize converter with optional config."""
        if config is None:
            from config import settings
            config = settings
        
        self.config = config
        self.SUPPORTED_FORMATS = config.SUPPORTED_FORMATS
        self.MAX_FILE_SIZE = config.MAX_FILE_SIZE
        self.MAX_IMAGE_SIZE = config.MAX_IMAGE_DIMENSION
        self.output_dir = config.OUTPUT_DIR
        self.target_width = config.TARGET_PDF_WIDTH
        self.target_height = config.TARGET_PDF_HEIGHT
        self.output_dir.mkdir(exist_ok=True)

    def validate_image(self, image_data: bytes, filename: str) -> tuple[bool, str]:
        """Validate image format and integrity."""
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()

            # Re-open since verify() closes the file
            img = Image.open(io.BytesIO(image_data))

            file_ext = Path(filename).suffix.lower().lstrip(".")
            if file_ext not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported format: {file_ext}"

            if len(image_data) > self.MAX_FILE_SIZE:
                return False, "File size exceeds maximum allowed"

            return True, "Valid"
        except Exception as e:
            return False, str(e)

    def rotate_image(self, image_data: bytes, angle: int) -> bytes:
        """Rotate image by specified angle."""
        try:
            img = Image.open(io.BytesIO(image_data))
            img = img.rotate(angle, expand=True)
            
            output = io.BytesIO()
            img.save(output, format="PNG", optimize=True)
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error rotating image: {e}")
            raise

    def crop_image(
        self,
        image_data: bytes,
        left: int = 0,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
    ) -> bytes:
        """Crop image by specified pixels."""
        try:
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            
            # Calculate crop box
            left = max(0, left)
            top = max(0, top)
            right = min(width, width - right)
            bottom = min(height, height - bottom)
            
            if left < right and top < bottom:
                img = img.crop((left, top, right, bottom))
            
            output = io.BytesIO()
            img.save(output, format="PNG", optimize=True)
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            raise

    def preprocess_image(
        self,
        image_data: bytes,
        resize: bool = True,
        target_width: int = None,
        target_height: int = None,
    ) -> bytes:
        """Preprocess image: resize, normalize format, convert RGBA to RGB."""
        try:
            if target_width is None:
                target_width = self.target_width
            if target_height is None:
                target_height = self.target_height

            img = Image.open(io.BytesIO(image_data))

            # Convert RGBA to RGB
            if img.mode == "RGBA":
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if needed
            if resize:
                img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # Save to bytes
            output = io.BytesIO()
            img.save(output, format="PNG", quality=self.config.PNG_QUALITY, optimize=True)
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise

    def convert_single(
        self,
        image_data: bytes,
        filename: str,
        metadata: dict = None,
        resize: bool = True,
        compression: bool = True,
    ) -> tuple[bytes, str]:
        """Convert single image to PDF."""
        try:
            # Validate
            valid, msg = self.validate_image(image_data, filename)
            if not valid:
                raise ValueError(msg)

            # Preprocess
            processed = self.preprocess_image(image_data, resize)
            img = Image.open(io.BytesIO(processed))

            # Convert to PDF
            pdf_bytes = img2pdf.convert(processed)

            # Add metadata if provided
            if metadata:
                pdf_bytes = self._add_metadata(pdf_bytes, metadata)

            return pdf_bytes, "Success"
        except Exception as e:
            logger.error(f"Error converting single image: {e}")
            raise

    def convert_multiple(
        self,
        image_files: List[tuple[bytes, str]],
        metadata: dict = None,
        resize: bool = True,
        compression: bool = True,
    ) -> tuple[bytes, str]:
        """Convert multiple images to single PDF."""
        try:
            processed_images = []

            for image_data, filename in image_files:
                # Validate
                valid, msg = self.validate_image(image_data, filename)
                if not valid:
                    raise ValueError(f"{filename}: {msg}")

                # Preprocess
                processed = self.preprocess_image(image_data, resize)
                processed_images.append(processed)

            # Convert all to PDF
            pdf_bytes = img2pdf.convert(processed_images)

            # Add metadata if provided
            if metadata:
                pdf_bytes = self._add_metadata(pdf_bytes, metadata)

            return pdf_bytes, "Success"
        except Exception as e:
            logger.error(f"Error converting multiple images: {e}")
            raise

    def _add_metadata(self, pdf_bytes: bytes, metadata: dict) -> bytes:
        """Add metadata to PDF using pikepdf."""
        try:
            import pikepdf

            with pikepdf.open(io.BytesIO(pdf_bytes)) as pdf:
                # Add title
                if "title" in metadata:
                    pdf.docinfo["/Title"] = metadata["title"]

                # Add author
                if "author" in metadata:
                    pdf.docinfo["/Author"] = metadata["author"]

                # Encrypt if password provided
                if "password" in metadata and metadata["password"]:
                    pdf.save(
                        io.BytesIO(),
                        encryption=pikepdf.Encryption(
                            owner=metadata["password"],
                            user=metadata["password"],
                            R=4
                        )
                    )

                # Save with metadata
                output = io.BytesIO()
                pdf.save(output)
                output.seek(0)
                return output.getvalue()
        except Exception as e:
            logger.warning(f"Could not add metadata: {e}")
            return pdf_bytes

    def encrypt_pdf(self, pdf_bytes: bytes, password: str) -> bytes:
        """Encrypt PDF with password."""
        try:
            import pikepdf

            with pikepdf.open(io.BytesIO(pdf_bytes)) as pdf:
                output = io.BytesIO()
                pdf.save(
                    output,
                    encryption=pikepdf.Encryption(
                        owner=password,
                        user=password,
                        R=4
                    )
                )
                output.seek(0)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error encrypting PDF: {e}")
            raise

    def save_pdf(self, pdf_bytes: bytes, filename: str) -> Path:
        """Save PDF to output directory."""
        try:
            output_path = self.output_dir / filename
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            return output_path
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            raise

    def cleanup_file(self, file_path: Path):
        """Delete a file safely."""
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Error deleting file {file_path}: {e}")
