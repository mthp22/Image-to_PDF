import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import io
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


@pytest.fixture
def sample_image_file():
    """Create sample image file."""
    img = Image.new("RGB", (200, 200), color="green")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return ("test.png", img_bytes, "image/png")


@pytest.fixture
def multiple_image_files():
    """Create multiple sample image files."""
    images = []
    for i in range(3):
        img = Image.new("RGB", (200, 200), color=(i * 80, i * 80, i * 80))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        images.append((f"test{i}.png", img_bytes, "image/png"))
    return images


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data


class TestSingleConversion:
    def test_convert_single_image(self, sample_image_file):
        """Test single image conversion."""
        filename, file_obj, content_type = sample_image_file
        response = client.post(
            "/convert-single",
            files={"file": (filename, file_obj, content_type)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_path" in data
        assert data["file_size"] > 0

    def test_convert_single_with_metadata(self, sample_image_file):
        """Test single image conversion with metadata."""
        filename, file_obj, content_type = sample_image_file
        response = client.post(
            "/convert-single",
            files={"file": (filename, file_obj, content_type)},
            data={
                "title": "Test PDF",
                "author": "Test Author",
                "resize": "true",
                "compression": "true",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_convert_single_no_file(self):
        """Test single conversion without file."""
        response = client.post("/convert-single")
        assert response.status_code != 200


class TestMultipleConversion:
    def test_convert_multiple_images(self, multiple_image_files):
        """Test multiple images conversion."""
        files = [
            ("files", (name, obj, ctype))
            for name, obj, ctype in multiple_image_files
        ]
        response = client.post("/convert", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_size"] > 0

    def test_convert_multiple_with_metadata(self, multiple_image_files):
        """Test multiple images conversion with metadata."""
        files = [
            ("files", (name, obj, ctype))
            for name, obj, ctype in multiple_image_files
        ]
        response = client.post(
            "/convert",
            files=files,
            data={
                "title": "Multi-page PDF",
                "author": "Test Author",
                "resize": "true",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_convert_multiple_no_files(self):
        """Test multiple conversion without files."""
        response = client.post("/convert")
        assert response.status_code != 200

    def test_convert_unsupported_format(self):
        """Test conversion with unsupported format."""
        # Create a dummy file with unsupported extension
        response = client.post(
            "/convert-single",
            files={"file": ("test.xyz", b"dummy content", "application/octet-stream")},
        )
        assert response.status_code != 200


class TestDownloadEndpoint:
    def test_download_nonexistent_file(self):
        """Test downloading non-existent file."""
        response = client.get("/download/nonexistent.pdf")
        assert response.status_code == 404

    def test_download_existing_file(self, sample_image_file):
        """Test downloading existing file."""
        # First, create a PDF
        filename, file_obj, content_type = sample_image_file
        create_response = client.post(
            "/convert-single",
            files={"file": (filename, file_obj, content_type)},
        )
        assert create_response.status_code == 200
        pdf_filename = create_response.json()["file_path"].split("/")[-1]

        # Now download it
        download_response = client.get(f"/download/{pdf_filename}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/pdf"


class TestErrorHandling:
    def test_corrupted_image(self):
        """Test handling of corrupted image."""
        response = client.post(
            "/convert-single",
            files={"file": ("test.png", b"corrupted data", "image/png")},
        )
        assert response.status_code == 400

    def test_invalid_file_extension(self):
        """Test invalid file extension."""
        response = client.post(
            "/convert-single",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400
