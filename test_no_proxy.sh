#!/bin/bash
# Quick test run WITHOUT proxy to diagnose issue

cd ~/THINK_SPAIN

echo "====================================================="
echo "RUNNING TEST WITHOUT PROXY (Diagnostic Mode)"
echo "====================================================="

# Activate venv
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found."
    exit 1
fi

source venv/bin/activate

# Run with proxy disabled for testing
export USE_PROXY=false
export MAX_CLICKS=50
export HEADLESS=true

echo "Starting test run (no proxy, max 50 clicks)..."
echo "This will help diagnose if proxy is causing issues..."
echo ""

python3 production_harvester.py

echo ""
echo "====================================================="
echo "Test complete! Check the logs above."
echo "====================================================="

