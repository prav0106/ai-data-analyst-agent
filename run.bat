@echo off
REM ============================================================
REM AI Data Analyst Agent - Quick launcher (Windows)
REM ============================================================
setlocal

TITLE AI Data Analyst Agent

REM Change to the directory this batch file lives in
cd /d "%~dp0"

echo.
echo ==========================================
echo   AI Data Analyst Agent
echo ==========================================
echo.

REM --- 1. Check Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

echo [INFO]  Using Python:
python --version
echo.

REM --- 2. Create virtual environment if missing ---
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO]  Creating virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [INFO]  Activating virtual environment ...
call .venv\Scripts\activate.bat

REM --- 3. Install / upgrade dependencies ---
echo [INFO]  Installing dependencies from requirements.txt ...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

REM --- 4. Launch Streamlit ---
echo.
echo [INFO]  Starting Streamlit on http://localhost:8501 ...
echo         (Press Ctrl+C to stop)
echo.
streamlit run app.py

echo.
echo [INFO]  Server stopped.
pause
endlocal
