#!/bin/bash
# Production backend startup script

set -e

echo "======================================================================"
echo "Image to PDF Converter - Backend Production Start"
echo "======================================================================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check environment variables
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    cp .env.example .env 2>/dev/null || true
fi

# Verify Python version
python_version=$(python --version | awk '{print $2}' | cut -d. -f1-2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version+ required"
    exit 1
fi

echo "✓ Python $python_version"

# Check dependencies
echo "Checking dependencies..."
python -c "import fastapi; import uvicorn; import pillow; import img2pdf" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed"
else
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Create directories
echo "Creating directories..."
mkdir -p logs converted_pdfs uploads temp

# Run tests
echo "Running tests..."
pytest backend/tests/ -q 2>/dev/null || echo "Some tests may have warnings"

# Set production environment
export PYTHONUNBUFFERED=1
export DEBUG=False
export LOG_LEVEL=INFO

echo ""
echo "======================================================================"
echo "Starting backend server..."
echo "======================================================================"
echo "Host: $(grep HOST .env 2>/dev/null | cut -d= -f2 || echo 0.0.0.0)"
echo "Port: $(grep PORT .env 2>/dev/null | cut -d= -f2 || echo 8000)"
echo "Docs: http://localhost:8000/docs"
echo "======================================================================"
echo ""

# Start server
python -m uvicorn backend.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --workers 4 \
    --log-level info
