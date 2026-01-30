import pytest
import io
from PIL import Image
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.converter import ImageToPDFConverter


@pytest.fixture
def converter():
    return ImageToPDFConverter()


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    img = Image.new("RGB", (200, 200), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_png_image():
    """Create a sample PNG image."""
    img = Image.new("RGB", (300, 400), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_rgba_image():
    """Create a sample RGBA image."""
    img = Image.new("RGBA", (200, 200), color=(255, 0, 0, 128))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestImageValidation:
    def test_valid_image(self, converter, sample_image):
        """Test validation of valid image."""
        valid, msg = converter.validate_image(sample_image, "test.png")
        assert valid is True
        assert msg == "Valid"

    def test_unsupported_format(self, converter, sample_image):
        """Test validation of unsupported format."""
        valid, msg = converter.validate_image(sample_image, "test.xyz")
        assert valid is False
        assert "Unsupported format" in msg

    def test_corrupted_image(self, converter):
        """Test validation of corrupted image."""
        corrupted = b"not a real image"
        valid, msg = converter.validate_image(corrupted, "test.png")
        assert valid is False


class TestPreprocessing:
    def test_rgb_image_preprocessing(self, converter, sample_image):
        """Test preprocessing of RGB image."""
        processed = converter.preprocess_image(sample_image, resize=False)
        assert processed is not None
        assert len(processed) > 0

        # Verify output is valid
        img = Image.open(io.BytesIO(processed))
        assert img.mode == "RGB"

    def test_rgba_to_rgb_conversion(self, converter, sample_rgba_image):
        """Test RGBA to RGB conversion."""
        processed = converter.preprocess_image(sample_rgba_image, resize=False)
        img = Image.open(io.BytesIO(processed))
        assert img.mode == "RGB"

    def test_image_resize(self, converter, sample_png_image):
        """Test image resizing."""
        processed = converter.preprocess_image(
            sample_png_image, resize=True, target_width=100, target_height=100
        )
        img = Image.open(io.BytesIO(processed))
        # Check that image is not larger than target
        assert img.width <= 100 or img.height <= 100


class TestConversion:
    def test_single_image_conversion(self, converter, sample_image):
        """Test conversion of single image."""
        pdf_bytes, msg = converter.convert_single(sample_image, "test.png")
        assert msg == "Success"
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # Check PDF header
        assert pdf_bytes.startswith(b"%PDF")

    def test_single_image_with_metadata(self, converter, sample_image):
        """Test single image conversion with metadata."""
        metadata = {"title": "Test Title", "author": "Test Author"}
        pdf_bytes, msg = converter.convert_single(
            sample_image, "test.png", metadata=metadata
        )
        assert msg == "Success"
        assert pdf_bytes.startswith(b"%PDF")

    def test_multiple_images_conversion(self, converter, sample_image, sample_png_image):
        """Test conversion of multiple images."""
        images = [(sample_image, "test1.png"), (sample_png_image, "test2.png")]
        pdf_bytes, msg = converter.convert_multiple(images)
        assert msg == "Success"
        assert pdf_bytes is not None
        assert pdf_bytes.startswith(b"%PDF")

    def test_multiple_images_with_metadata(
        self, converter, sample_image, sample_png_image
    ):
        """Test multiple images conversion with metadata."""
        images = [(sample_image, "test1.png"), (sample_png_image, "test2.png")]
        metadata = {"title": "Multi Page", "author": "Test"}
        pdf_bytes, msg = converter.convert_multiple(images, metadata=metadata)
        assert msg == "Success"
        assert pdf_bytes.startswith(b"%PDF")


class TestFileSaving:
    def test_save_pdf(self, converter, sample_image):
        """Test saving PDF to file."""
        pdf_bytes, _ = converter.convert_single(sample_image, "test.png")
        path = converter.save_pdf(pdf_bytes, "test_output.pdf")
        assert path.exists()
        assert path.suffix == ".pdf"
        # Cleanup
        converter.cleanup_file(path)

    def test_cleanup_file(self, converter, sample_image):
        """Test file cleanup."""
        pdf_bytes, _ = converter.convert_single(sample_image, "test.png")
        path = converter.save_pdf(pdf_bytes, "test_cleanup.pdf")
        assert path.exists()
        converter.cleanup_file(path)
        assert not path.exists()
