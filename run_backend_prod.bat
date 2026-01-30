@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo Image to PDF Converter - Backend Production Start
echo ======================================================================

REM Check virtual environment
if not exist "venv" (
    echo Error: Virtual environment not found
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check environment variables
if not exist ".env" (
    echo Warning: .env file not found
    if exist ".env.example" copy .env.example .env
)

REM Create directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "converted_pdfs" mkdir converted_pdfs
if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp

REM Set production environment
set PYTHONUNBUFFERED=1
set DEBUG=False
set LOG_LEVEL=INFO

echo.
echo ======================================================================
echo Starting backend server...
echo ======================================================================
echo Host: 0.0.0.0
echo Port: 8000
echo Docs: http://localhost:8000/docs
echo ======================================================================
echo.

REM Start server
python -m uvicorn backend.main:app ^
    --host 0.0.0.0 ^
    --port 8000 ^
    --workers 1 ^
    --log-level info

pause
