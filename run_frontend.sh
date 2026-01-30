#!/bin/bash

# Run Image to PDF Frontend

echo "Starting Image to PDF Frontend..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies if needed
pip install -q -r requirements.txt 2>/dev/null

# Run frontend
cd ui
python main.py
