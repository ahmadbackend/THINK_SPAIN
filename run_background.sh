#!/bin/bash
# Run scraper in background - Survives SSH disconnect

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

# Run in background with nohup (survives SSH disconnect)
nohup python3 production_harvester.py > production_scraper.log 2>&1 &

PID=$!
echo "Scraper started in background!"
echo "PID: $PID"
echo "Log file: production_scraper.log"
echo ""
echo "To check status: ./status.sh"
echo "To view logs: tail -f production_scraper.log"
echo "To stop: kill $PID"
echo ""
echo "You can now safely close SSH. The scraper will keep running."

