# Image to PDF Converter

A full-stack application for converting images to PDF documents with a FastAPI backend and Kivy-based cross-platform UI.

## Features

 **Batch & Single Conversion**
- Convert 1 or multiple images to PDF
- Support for JPEG, PNG, BMP, TIFF formats

**Smart Image Processing**
- Automatic resize to fit A4/Letter pages


**PDF Metadata**
- Add title and author to PDFs
-Password protection



## Quick Start 
### 1. Install Dependencies

```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Start Backend

**Terminal 1:**
```bash
python backend/main.py
```

API runs at: http://localhost:8000

### 3. Start Frontend

**Terminal 2:**
```bash
python ui/main.py
```

## Docker Deployment

```bash
docker-compose up --build
```

## Testing

```bash
pytest backend/tests/

# Verify setup
python test_setup.py
```

## Configuration

Create `.env` file (copy from `.env.example`):
```
API_URL=http://localhost:8000
PORT=8000
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800
```