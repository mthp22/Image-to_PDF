@echo off
REM Run Image to PDF Backend on Windows

echo Starting Image to PDF Backend...

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install dependencies if needed
pip install -q -r requirements.txt

REM Create output directories
if not exist backend\converted_pdfs mkdir backend\converted_pdfs
if not exist backend\logs mkdir backend\logs

REM Run backend
cd backend
python main.py
pause
