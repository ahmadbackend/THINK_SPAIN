# Think Spain Property Scraper

Automated property link harvester for thinkspain.com using Selenium with headed mode (Xvfb virtual display).

## Features

✓ **Headed Mode** - Runs Chrome in normal (non-headless) mode using Xvfb virtual display for better detection avoidance  
✓ **Realistic Timing** - 5-10 second delays between clicks to mimic human behavior  
✓ **Auto-Save** - Progress saved after every click  
✓ **Resume Support** - Continue from any point  
✓ **Background Execution** - Runs in screen session, safe to close SSH  
✓ **No Proxy Required** - Works without proxy services  

## Quick Start (GCP VM)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/THINK_SPAIN.git
cd THINK_SPAIN

# 2. Start scraper
chmod +x *.sh
./start.sh

# 3. Check progress
./status.sh

# 4. View live output (optional)
screen -r thinkspain
# Press Ctrl+A then D to detach

# 5. Stop scraper (optional)
./stop.sh

# 6. Resume after stopping
./resume.sh
```

## Requirements

- GCP VM (Debian/Ubuntu)
- Python 3.8+
- Google Chrome
- Xvfb (X Virtual Framebuffer)
- Screen

All dependencies are automatically installed by `start.sh`.

## Output Files

- `harvested_properties.json` - All scraped property links
- `scraper_progress.json` - Checkpoint for resume functionality
- `production_scraper.log` - Detailed execution logs

## Configuration

Edit these values in `production_harvester.py` if needed:

```python
MAX_CLICKS = 15627  # Maximum number of "Show More" clicks
MIN_WAIT_BETWEEN_CLICKS = 5  # Minimum seconds between clicks
MAX_WAIT_BETWEEN_CLICKS = 10  # Maximum seconds between clicks
MAX_CONSECUTIVE_NO_NEW = 5  # Stop after N clicks with no new properties
```

## How It Works

1. Opens Chrome in headed mode via Xvfb virtual display
2. Loads thinkspain.com property search page
3. Clicks "Show More" button repeatedly
4. Harvests property links after each click
5. Saves progress automatically
6. Uses realistic human-like delays

## Notes

- Safe to close SSH connection - scraper runs in background
- Graceful shutdown on Ctrl+C or system signals
- Memory usage monitoring
- Error screenshots on failures
- Popup detection and auto-closing

## License

MIT

