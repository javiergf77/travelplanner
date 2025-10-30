#!/bin/bash
# Quick start script for Linux/Mac

echo ""
echo "============================================================"
echo "   AI Travel Booker - Corporate Edition"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv env
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please ensure Python 3.10+ is installed"
        exit 1
    fi
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment found"
fi

echo ""
echo "[2/3] Activating virtual environment..."
source env/bin/activate

echo ""
echo "[3/3] Checking dependencies..."
pip install -r requirements.txt --quiet --disable-pip-version-check
if [ $? -ne 0 ]; then
    echo "WARNING: Some dependencies may have failed to install"
    echo "Trying to start anyway..."
fi

echo ""
echo "============================================================"
echo "   Starting Application..."
echo "============================================================"
echo ""
echo ">> Simple Mode: Leave 'Use CrewAI Agents' unchecked"
echo ">> CrewAI Mode: Requires Ollama (see SETUP_GUIDE.md)"
echo ""
echo "Opening: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "============================================================"
echo ""

python app_gradio_enhanced.py

