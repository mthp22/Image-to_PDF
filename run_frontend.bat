@echo off
REM Run Image to PDF Frontend on Windows

echo Starting Image to PDF Frontend...

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install dependencies if needed
pip install -q -r requirements.txt

REM Run frontend
cd ui
python main.py
pause
