#!/bin/bash

# Run Image to PDF Backend

echo "Starting Image to PDF Backend..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install -q -r requirements.txt 2>/dev/null

# Create output directories
mkdir -p backend/converted_pdfs
mkdir -p backend/logs

# Run backend
cd backend
python main.py
