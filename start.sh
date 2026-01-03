#!/bin/bash
# Start harvester with Xvfb virtual display for headed Chrome

cd ~/THINK_SPAIN

echo "====================================================="
echo "STARTING HARVESTER (Headed Mode with Xvfb)"
echo "====================================================="

# Install dependencies
echo "Checking dependencies..."
sudo apt-get update -qq
sudo apt-get install -y google-chrome-stable xvfb screen 2>&1 | grep -v "already" || true

# Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install -q --upgrade pip
pip install -q -r requirements_production.txt

echo "✓ Setup complete"
echo ""

# Start Xvfb on display :99
echo "Starting Xvfb virtual display..."
pkill -f "Xvfb :99" 2>/dev/null || true
sleep 1
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
XVFB_PID=$!
export DISPLAY=:99
echo "✓ Xvfb started on display :99 (PID: $XVFB_PID)"
sleep 2

# Run in screen session
echo "Starting scraper in screen session..."
screen -dmS thinkspain bash -c "export DISPLAY=:99; cd ~/THINK_SPAIN; source venv/bin/activate; python3 production_harvester.py"

echo ""
echo "====================================================="
echo "✓ SCRAPER STARTED!"
echo "====================================================="
echo ""
echo "Commands:"
echo "  screen -r thinkspain    # See live output (Ctrl+A then D to detach)"
echo "  ./status.sh             # Check progress"
echo "  ./stop.sh               # Stop scraper"
echo ""
echo "✓ Safe to close SSH - scraper runs in background!"
echo "====================================================="
