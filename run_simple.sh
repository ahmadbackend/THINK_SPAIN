#!/bin/bash
# Simple run script - Auto-creates venv if missing

cd ~/THINK_SPAIN

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements_production.txt
else
    source venv/bin/activate
fi

python3 production_harvester.py

