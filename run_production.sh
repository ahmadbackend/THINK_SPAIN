#!/bin/bash
# Linux/DigitalOcean script to run production harvester

echo "====================================================="
echo "PRODUCTION HARVESTER - Linux/DigitalOcean"
echo "====================================================="

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the harvester
echo "Starting production harvester..."
python3 production_harvester.py

echo "Harvester finished."

