#!/usr/bin/env python
"""
Test script to verify Image to PDF Converter installation and setup.
Run this to check if all dependencies are properly installed.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.9+ required")
        return False


def check_venv():
    """Check if running in virtual environment."""
    print_header("Virtual Environment Check")
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✓ Running in virtual environment: {sys.prefix}")
        return True
    else:
        print("⚠ Not running in virtual environment (recommended)")
        return False


def check_imports():
    """Check if required packages are installed."""
    print_header("Package Installation Check")
    
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'PIL': 'Pillow',
        'img2pdf': 'img2pdf',
        'requests': 'Requests',
        'kivy': 'Kivy',
        'pytest': 'Pytest',
    }
    
    missing = []
    for import_name, display_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name}")
            missing.append(display_name)
    
    return len(missing) == 0, missing


def check_directories():
    """Check if project directories exist."""
    print_header("Directory Structure Check")
    
    directories = {
        'backend': 'Backend directory',
        'ui': 'Frontend directory',
        'backend/services': 'Services directory',
        'backend/tests': 'Tests directory',
        'ui/screens': 'Screens directory',
        'ui/widgets': 'Widgets directory',
    }
    
    all_exist = True
    for dir_path, description in directories.items():
        full_path = Path(dir_path)
        if full_path.exists():
            print(f"✓ {description}: {dir_path}")
        else:
            print(f"✗ {description}: {dir_path}")
            all_exist = False
    
    return all_exist


def check_files():
    """Check if important files exist."""
    print_header("File Existence Check")
    
    files = {
        'backend/main.py': 'Backend main',
        'backend/models.py': 'Pydantic models',
        'backend/routes.py': 'API routes',
        'backend/config.py': 'Configuration',
        'backend/services/converter.py': 'Image converter',
        'ui/main.py': 'Frontend main',
        'requirements.txt': 'Dependencies',
        'Dockerfile': 'Docker config',
        'docker-compose.yml': 'Docker Compose',
        'QUICKSTART.md': 'Quick start guide',
        'README_DEV.md': 'Development guide',
        'API.md': 'API documentation',
    }
    
    all_exist = True
    for file_path, description in files.items():
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✓ {description}: {file_path}")
        else:
            print(f"✗ {description}: {file_path}")
            all_exist = False
    
    return all_exist


def test_backend_import():
    """Test if backend modules can be imported."""
    print_header("Backend Module Import Test")
    
    try:
        sys.path.insert(0, str(Path('backend')))
        
        from models import ConversionRequest, ConversionResponse
        print("✓ Pydantic models")
        
        from services.converter import ImageToPDFConverter
        print("✓ Image converter")
        
        from config import settings
        print("✓ Configuration")
        
        from main import app
        print("✓ FastAPI application")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_converter():
    """Test converter functionality."""
    print_header("Converter Functionality Test")
    
    try:
        from PIL import Image
        from services.converter import ImageToPDFConverter
        import io
        
        converter = ImageToPDFConverter()
        print("✓ Converter initialization")
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        test_image_data = img_bytes.getvalue()
        print("✓ Test image creation")
        
        # Test validation
        valid, msg = converter.validate_image(test_image_data, 'test.png')
        if valid:
            print("✓ Image validation")
        else:
            print(f"✗ Image validation: {msg}")
            return False
        
        # Test preprocessing
        processed = converter.preprocess_image(test_image_data, resize=False)
        if processed:
            print("✓ Image preprocessing")
        else:
            print("✗ Image preprocessing")
            return False
        
        # Test conversion
        pdf_bytes, msg = converter.convert_single(test_image_data, 'test.png')
        if pdf_bytes and pdf_bytes.startswith(b'%PDF'):
            print("✓ Single image conversion")
        else:
            print("✗ Single image conversion")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_quick_tests():
    """Run pytest if available."""
    print_header("Running Unit Tests")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'backend/tests/', '-v', '--tb=short'],
            capture_output=True,
            timeout=30,
            cwd='backend'
        )
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("⚠ Some tests failed")
            print(result.stdout.decode('utf-8', errors='ignore')[-500:])
            return False
    except subprocess.TimeoutExpired:
        print("⚠ Tests timed out")
        return False
    except Exception as e:
        print(f"⚠ Could not run tests: {e}")
        return False


def print_summary(checks):
    """Print summary of all checks."""
    print_header("Test Summary")
    
    passed = sum(1 for check in checks if check)
    total = len(checks)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start backend:  python backend/main.py")
        print("2. Start frontend: python ui/main.py")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed.")
        print("Please fix the issues above and try again.")
        return 1


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("  Image to PDF Converter - Setup Verification")
    print("="*60)
    
    checks = [
        check_python_version(),
        check_venv(),
        check_imports()[0],
        check_directories(),
        check_files(),
        test_backend_import(),
        test_converter(),
    ]
    
    # Optional: run unit tests
    if all(checks):
        checks.append(run_quick_tests())
    
    return print_summary(checks)


if __name__ == '__main__':
    sys.exit(main())
