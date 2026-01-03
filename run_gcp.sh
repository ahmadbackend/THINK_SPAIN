#!/bin/bash
# GCP VM Run Script - Use this to start the harvester

set -e

echo "====================================================="
echo "STARTING THINK SPAIN HARVESTER ON GCP"
echo "====================================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run setup_gcp.sh first."
    exit 1
fi

# Set production environment variables (GCP optimized)
export HEADLESS=true
export MAX_CLICKS=500
export MAX_RUNTIME_HOURS=12

# Load additional environment variables if .env exists
if [ -f .env ]; then
    echo "Loading additional variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run with virtual display (for headless mode)
echo "Starting harvester in headless mode..."
xvfb-run -a python3 production_harvester.py

echo ""
echo "====================================================="
echo "Harvester finished!"
echo "====================================================="
echo ""
echo "To download results:"
echo "  gcloud compute scp VM_NAME:~/harvested_properties.json ."
echo ""

