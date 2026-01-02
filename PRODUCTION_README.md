# Quick Start Guide - Production Harvester

## 🎯 What's New in Production Version

### ✅ All Your Requirements Implemented:

1. **DigitalOcean Ready** - Complete deployment guide + requirements file
2. **Graceful Shutdown** - Handles crashes, Ctrl+C, server shutdowns
3. **Popup Handling** - Auto-closes cookie consent and other popups
4. **Auto-save After Each Click** - Progress saved to .json after every click
5. **Resume Support** - Continues from last checkpoint
6. **Retry Logic** - Retries failed clicks 3 times
7. **Memory Monitoring** - Logs memory usage
8. **Stop on No New Links** - Stops after 3 consecutive clicks with no new data
9. **Error Screenshots** - Only captures screenshots when errors occur
10. **Environment Config** - Easy configuration via .env file

---

## 🚀 Quick Test (Windows)

```bash
# Run the production harvester locally
python production_harvester.py
```

Press **Ctrl+C** at any time - it will save and exit gracefully!

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `production_harvester.py` | Main production script with all features |
| `requirements_production.txt` | Pinned dependencies for DigitalOcean |
| `install_chrome_digitalocean.sh` | Chrome installation script for Ubuntu |
| `.env.example` | Environment configuration template |
| `run_production.bat` | Windows runner |
| `run_production.sh` | Linux/DigitalOcean runner |
| `DEPLOYMENT_GUIDE.md` | Complete deployment instructions |

---

## 🎮 Configuration Options

Edit `.env` or set environment variables:

```bash
MAX_CLICKS=200              # Stop after N clicks
HEADLESS=true              # true for server, false for local
START_URL=https://...      # Starting URL
OUTPUT_FILE=harvested_properties.json
PROGRESS_FILE=scraper_progress.json
MAX_RUNTIME_HOURS=12       # Maximum runtime
```

---

## 📊 Output Files

### 1. `harvested_properties.json` - Main output
```json
{
  "total_properties": 352,
  "clicks_performed": 21,
  "harvested_at": "2026-01-03T00:08:32",
  "properties": [
    "https://www.thinkspain.com/property-for-sale/8917427",
    "https://www.thinkspain.com/property-for-sale/8917428",
    ...
  ]
}
```

### 2. `scraper_progress.json` - Resume checkpoint
```json
{
  "clicks_performed": 21,
  "property_links": [...],
  "last_updated": "2026-01-03T00:08:32",
  "consecutive_no_new": 0
}
```

### 3. `production_scraper.log` - Detailed logs
```
2026-01-03 00:22:56 - INFO - ✓ Click #1 - Show More clicked
2026-01-03 00:23:06 - INFO -   Harvested 16 new links | Total: 32
```

### 4. `error_screenshots/` - Error screenshots only
Screenshots are only taken when errors occur, not on every click.

---

## 🔄 How Resume Works

1. Run the script: `python production_harvester.py`
2. It harvests links and saves after each click
3. If interrupted (Ctrl+C, crash, shutdown):
   - Progress is saved to `scraper_progress.json`
   - All harvested links are in `harvested_properties.json`
4. Run again: `python production_harvester.py`
   - Automatically loads progress
   - Continues from where it left off
   - No duplicates (uses set tracking)

**To start fresh:** Delete `scraper_progress.json`

---

## 🛑 Stop Conditions

The script stops when:
1. ✅ Reaches MAX_CLICKS (default 200)
2. ✅ 3 consecutive clicks with no new links
3. ✅ Runtime exceeds MAX_RUNTIME_HOURS (default 12)
4. ✅ User presses Ctrl+C (graceful)
5. ✅ Server sends SIGTERM (graceful)
6. ✅ No more "Show More" button

---

## 💡 Testing

### Test 1: Graceful Shutdown
```bash
python production_harvester.py
# Wait for a few clicks
# Press Ctrl+C
# Check that files are saved properly
```

### Test 2: Resume
```bash
python production_harvester.py
# Let it run for 5 clicks
# Press Ctrl+C
# Run again - should resume from click 5
```

### Test 3: Popup Handling
```bash
# Run on a page with cookie popups
# Check log for "Closed popup" messages
```

---

## 🎯 Key Improvements Over Test Version

| Feature | Test Version | Production Version |
|---------|-------------|-------------------|
| Save frequency | End only | **After every click** |
| Resume | ❌ | ✅ |
| Retry | ❌ | ✅ (3 attempts) |
| Popups | ❌ | ✅ (Auto-close) |
| Graceful shutdown | ❌ | ✅ (SIGTERM, Ctrl+C) |
| Memory monitoring | ❌ | ✅ |
| Screenshots | Never | **On errors only** |
| Environment config | ❌ | ✅ (.env) |
| Runtime limit | ❌ | ✅ (12h default) |
| Stop on no new | 5 clicks | **3 clicks** |

---

## 🐛 Common Issues

### "Show More button not found"
- **Normal** - Means you've reached the end of available properties
- Script will save and exit gracefully

### Script stops early
- Check `consecutive_no_new` in progress file
- If it's ≥3, that means no new links for 3 consecutive clicks
- This is the expected behavior you requested

### Want to continue past the limit?
- Delete `scraper_progress.json` to reset the counter
- Or try a different URL with more properties

---

## 📞 Need Help?

1. Check `production_scraper.log` for detailed logs
2. Check `error_screenshots/` for error visuals
3. Check `scraper_progress.json` for current state
4. See `DEPLOYMENT_GUIDE.md` for full deployment instructions

---

**Ready to deploy?** See `DEPLOYMENT_GUIDE.md` for complete DigitalOcean setup! 🚀

