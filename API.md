# Image to PDF Converter API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Check if the API is running.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Code:** 200

---

### 2. Root Endpoint

Get API information and available endpoints.

**Request:**
```http
GET /
```

**Response:**
```json
{
  "message": "Image to PDF Converter API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "health": "GET /health",
    "convert_multiple": "POST /convert",
    "convert_single": "POST /convert-single",
    "download": "GET /download/{filename}"
  }
}

###  Convert Single Image

Convert a single image to PDF.

**Request:**
```http
POST /convert-single
```

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | Image file (JPEG, PNG, BMP, TIFF) |
| title | String | No | PDF title metadata |
| author | String | No | PDF author metadata |
| password | String | No | Password protection (future feature) |
| resize | Boolean | No | Auto-resize to fit page (default: true) |
| compression | Boolean | No | Enable compression (default: true) |

**Example using curl:**
```bash
curl -X POST \
  -F "file=@image.jpg" \
  -F "title=My Document" \
  -F "author=John Doe" \
  http://localhost:8000/convert-single
```

**Example using Python:**
```python
import requests

with open('image.jpg', 'rb') as f:
    files = {'file': f}
    data = {
        'title': 'My Document',
        'author': 'John Doe',
        'resize': 'true',
        'compression': 'true'
    }
    response = requests.post(
        'http://localhost:8000/convert-single',
        files=files,
        data=data
    )
    print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully converted image to PDF",
  "file_path": "./converted_pdfs/image_20240127_120530.pdf",
  "file_size": 45678
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid file or format
- `500`: Server error

###  Download PDF

Download a previously converted PDF file.

**Request:**
```http
GET /download/{filename}
```

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| filename | String | PDF filename (from conversion response) |

**Example:**
```bash
curl -O http://localhost:8000/download/combined_20240127_120530.pdf
```

**Response:**
- Binary PDF file with Content-Type: application/pdf

**Status Codes:**
- `200`: Success
- `404`: File not found
- `500`: Server error

---

## Error Codes


400 | Bad Request | Invalid file format, missing required fields |
404 | Not Found | File doesn't exist |
413 | Payload Too Large | File exceeds size limit (50MB) |
500 | Internal Server Error | Server error during processing |


```

### Check Server Status

```bash
curl http://localhost:8000/health
```

### View API Documentation

```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```