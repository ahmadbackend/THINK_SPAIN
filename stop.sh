#!/bin/bash
# Stop the harvester gracefully

echo "Stopping harvester..."

# Try to kill the process
if pgrep -f "production_harvester.py" > /dev/null; then
    PID=$(pgrep -f "production_harvester.py")
    echo "Found process: $PID"
    kill $PID
    echo "✓ Stop signal sent (Ctrl+C equivalent)"
    echo "Waiting for graceful shutdown..."
    sleep 3

    # Check if still running
    if pgrep -f "production_harvester.py" > /dev/null; then
        echo "⚠ Process still running. Forcing stop..."
        kill -9 $PID
        echo "✓ Force stopped"
    else
        echo "✓ Stopped gracefully"
    fi
else
    echo "✗ Harvester is not running"
fi

# Stop screen session if exists
if screen -list | grep -q thinkspain; then
    screen -X -S thinkspain quit
    echo "✓ Screen session closed"
fi

echo ""
echo "Done!"

