#!/bin/bash
# Run with screen - Allows reattaching to see live output

cd ~/THINK_SPAIN

# Check if already running
if pgrep -f "production_harvester.py" > /dev/null; then
    echo "⚠ Scraper is already running!"
    echo "Run ./status.sh to check or ./stop.sh to stop it first"
    exit 1
fi

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo "Installing screen..."
    sudo apt-get install -y screen
fi

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements_production.txt
fi

# Start in detached screen session
screen -dmS thinkspain bash -c "source venv/bin/activate && python3 production_harvester.py"

echo "====================================================="
echo "Scraper started in screen session 'thinkspain'"
echo "====================================================="
echo ""
echo "Useful commands:"
echo "  screen -r thinkspain     # Reattach to see live output"
echo "  screen -list             # List all screen sessions"
echo "  ./status.sh              # Check progress"
echo "  Ctrl+A then D            # Detach from screen (inside session)"
echo ""
echo "You can safely close SSH. The scraper will keep running."
echo "To stop: screen -X -S thinkspain quit"
echo ""

