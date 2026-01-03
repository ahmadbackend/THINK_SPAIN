#!/bin/bash
# All-in-one fix: Disable proxy + slow down + increase threshold

cd ~/THINK_SPAIN

echo "====================================================="
echo "APPLYING FIX: Disable Proxy + Slower Timing"
echo "====================================================="

# Stop any running scraper
./stop.sh 2>/dev/null

# Create .env with safe settings
cat > .env << 'EOF'
# Disable proxy (might be causing blocks)
USE_PROXY=false

# Slower, more realistic timing
MIN_WAIT_BETWEEN_CLICKS=8
MAX_WAIT_BETWEEN_CLICKS=15
PAGE_LOAD_WAIT=10

# More patient threshold
MAX_CONSECUTIVE_NO_NEW=10
EOF

echo "✓ Configuration updated:"
echo "  - Proxy: DISABLED"
echo "  - Wait between clicks: 8-15 seconds"
echo "  - Page load wait: 10 seconds"
echo "  - Consecutive threshold: 10 (was 5)"
echo ""

# Activate venv
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found."
    exit 1
fi

source venv/bin/activate

# Run in screen
if ! command -v screen &> /dev/null; then
    echo "Installing screen..."
    sudo apt-get install -y screen
fi

screen -dmS thinkspain bash -c "source venv/bin/activate && python3 production_harvester.py"

echo "====================================================="
echo "✓ Scraper started with fixed settings!"
echo "====================================================="
echo ""
echo "Commands:"
echo "  screen -r thinkspain    # See live output"
echo "  ./status.sh             # Check progress"
echo "  ./stop.sh               # Stop scraper"
echo ""
echo "Wait 5-10 minutes, then run ./status.sh"
echo "If clicks progress past 30, the fix worked!"
echo ""

