#!/bin/bash
# Resume scraper - continues from last checkpoint

cd ~/THINK_SPAIN

# Check if already running
if pgrep -f "production_harvester.py" > /dev/null; then
    echo "⚠ Scraper is already running!"
    echo "Run ./status.sh to check or ./stop.sh to stop it first"
    exit 1
fi

echo "====================================================="
echo "RESUMING SCRAPER FROM CHECKPOINT"
echo "====================================================="

# Check progress
if [ -f "scraper_progress.json" ]; then
    CLICKS=$(python3 -c "import json; print(json.load(open('scraper_progress.json'))['clicks_performed'])" 2>/dev/null || echo "?")
    PROPERTIES=$(python3 -c "import json; print(len(json.load(open('scraper_progress.json'))['property_links']))" 2>/dev/null || echo "?")
    echo "Previous progress: $CLICKS clicks, $PROPERTIES properties"
    echo "Continuing from where it left off..."
    echo ""
fi

# Activate venv
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run setup first."
    exit 1
fi

source venv/bin/activate

# Run in background with screen
if ! command -v screen &> /dev/null; then
    echo "Installing screen..."
    sudo apt-get install -y screen
fi

screen -dmS thinkspain bash -c "source venv/bin/activate && python3 production_harvester.py"

echo "✓ Scraper resumed in background (screen session: thinkspain)"
echo ""
echo "Commands:"
echo "  screen -r thinkspain           # See live output"
echo "  ./status.sh                    # Check progress"
echo "  ./stop.sh                      # Stop scraper"
echo ""
echo "Safe to close SSH now!"

