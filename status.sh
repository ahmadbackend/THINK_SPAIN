#!/bin/bash
# Quick status check for the harvester

echo "=========================================="
echo "HARVESTER STATUS CHECK"
echo "=========================================="
echo ""

# Check if running
if pgrep -f "production_harvester.py" > /dev/null; then
    echo "✓ Harvester is RUNNING"
    echo ""
    PID=$(pgrep -f "production_harvester.py")
    echo "  PID: $PID"
    echo "  Runtime: $(ps -o etime= -p $PID)"
else
    echo "✗ Harvester is NOT running"
fi

echo ""

# Check progress
if [ -f "scraper_progress.json" ]; then
    echo "Progress:"
    CLICKS=$(python3 -c "import json; print(json.load(open('scraper_progress.json'))['clicks_performed'])" 2>/dev/null || echo "?")
    PROPERTIES=$(python3 -c "import json; print(len(json.load(open('scraper_progress.json'))['property_links']))" 2>/dev/null || echo "?")
    UPDATED=$(python3 -c "import json; print(json.load(open('scraper_progress.json'))['last_updated'])" 2>/dev/null || echo "?")
    echo "  Clicks: $CLICKS"
    echo "  Properties: $PROPERTIES"
    echo "  Last updated: $UPDATED"
else
    echo "No progress file found"
fi

echo ""

# Show last 10 log lines
if [ -f "production_scraper.log" ]; then
    echo "Last 10 log lines:"
    echo "---"
    tail -10 production_scraper.log
else
    echo "No log file found"
fi

echo ""
echo "=========================================="

