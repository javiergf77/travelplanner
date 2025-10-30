@echo off
REM Quick start script for Windows
echo.
echo ============================================================
echo    AI Travel Booker - Corporate Edition
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "env\" (
    echo [1/3] Creating virtual environment...
    python -m venv env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python 3.10+ is installed
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment found
)

echo.
echo [2/3] Activating virtual environment...
call env\Scripts\activate.bat

echo.
echo [3/3] Checking dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo Trying to start anyway...
)

echo.
echo ============================================================
echo    Starting Application...
echo ============================================================
echo.
echo ^>^> Simple Mode: Leave "Use CrewAI Agents" unchecked
echo ^>^> CrewAI Mode: Requires Ollama (see SETUP_GUIDE.md)
echo.
echo Opening: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python app_gradio_enhanced.py

pause

