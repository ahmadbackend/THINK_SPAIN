# Production Deployment Guide - DigitalOcean

## 🚀 Features Implemented

✅ **Graceful Shutdown** - Handles SIGTERM, SIGINT, Ctrl+C gracefully
✅ **Resume Support** - Continues from last checkpoint if interrupted
✅ **Retry Logic** - Retries failed clicks 3 times before giving up
✅ **Memory Monitoring** - Logs memory usage every 10 clicks
✅ **Auto-save** - Saves progress after EVERY click to .json file
✅ **Popup Handling** - Automatically detects and closes popups
✅ **Error Screenshots** - Captures screenshots on errors only (not every click)
✅ **Environment Config** - Configurable via environment variables
✅ **Stop Condition** - Stops after 3 consecutive clicks with no new links
✅ **Timeout Protection** - Maximum 12-hour runtime by default

---

## 📋 Prerequisites

### DigitalOcean Droplet
- Ubuntu 20.04 or 22.04
- Minimum 2GB RAM (recommended 4GB)
- 25GB storage

---

## 🔧 Installation Steps

### 1. Connect to Your DigitalOcean Droplet
```bash
ssh root@your-droplet-ip
```

### 2. Update System
```bash
apt-get update
apt-get upgrade -y
```

### 3. Install Python 3.10+
```bash
apt-get install -y python3 python3-pip python3-venv
python3 --version  # Should be 3.10+
```

### 4. Upload Files to Droplet
From your local machine:
```bash
scp production_harvester.py root@your-droplet-ip:/root/
scp requirements_production.txt root@your-droplet-ip:/root/
scp install_chrome_digitalocean.sh root@your-droplet-ip:/root/
scp run_production.sh root@your-droplet-ip:/root/
scp .env.example root@your-droplet-ip:/root/.env
```

Or use git:
```bash
cd /root
git clone your-repo-url
cd your-repo-folder
```

### 5. Install Chrome and Dependencies
```bash
chmod +x install_chrome_digitalocean.sh
./install_chrome_digitalocean.sh
```

### 6. Setup Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt
```

### 7. Configure Environment
```bash
nano .env
```

Edit the settings:
```
HEADLESS=true
MAX_CLICKS=200
START_URL=https://www.thinkspain.com/property-for-sale
```

### 8. Test Run (Optional)
```bash
# Test with visible browser (if you have X11 forwarding)
python3 production_harvester.py
```

---

## 🎯 Running in Production

### Option 1: Direct Run
```bash
chmod +x run_production.sh
./run_production.sh
```

### Option 2: Background with nohup
```bash
nohup python3 production_harvester.py > output.log 2>&1 &
```

### Option 3: Using screen (recommended)
```bash
# Install screen
apt-get install -y screen

# Start a new screen session
screen -S harvester

# Run the script
python3 production_harvester.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r harvester
# Kill session: screen -X -S harvester quit
```

### Option 4: Using systemd service
Create `/etc/systemd/system/harvester.service`:
```ini
[Unit]
Description=Property Harvester Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/root/venv/bin/python3 /root/production_harvester.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable harvester
systemctl start harvester
systemctl status harvester
```

---

## 📊 Monitoring

### Check Logs
```bash
tail -f production_scraper.log
```

### Check Progress
```bash
cat scraper_progress.json | python3 -m json.tool
```

### Check Output
```bash
cat harvested_properties.json | python3 -m json.tool | head -50
```

### Stop Gracefully
```bash
# If running in foreground: Ctrl+C
# If running in background: pkill -TERM -f production_harvester.py
# With systemd: systemctl stop harvester
```

---

## 🔄 Resume After Interruption

The script automatically resumes from where it left off:

1. It saves progress after every click to `scraper_progress.json`
2. On restart, it loads the progress and continues
3. No duplicate links will be harvested (uses set to track unique URLs)

To start fresh (reset):
```bash
rm scraper_progress.json
```

---

## 🐛 Troubleshooting

### Chrome Not Starting
```bash
# Check Chrome installation
google-chrome --version

# Install missing dependencies
apt-get install -y chromium-browser chromium-chromedriver
```

### Memory Issues
```bash
# Check memory
free -h

# If low memory, reduce Chrome memory usage by editing production_harvester.py
# Add to Chrome options:
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--disable-software-rasterizer')
```

### Error Screenshots
Check the `error_screenshots/` folder for screenshots taken when errors occur.

### Stuck or Not Clicking
- Check the log file for errors
- Screenshot will be saved automatically on errors
- Script will retry 3 times before giving up

---

## 📈 Expected Performance

- **Speed**: ~15-30 seconds per click (depends on page load time)
- **Memory**: 200-500 MB (Chrome can grow over time)
- **200 clicks**: Approximately 1-2 hours
- **Max runtime**: 12 hours (configurable)

---

## ⚠️ Important Notes

1. **Headless Mode**: Always use `HEADLESS=true` on DigitalOcean
2. **Backups**: Output files are saved after every click
3. **Stop Condition**: Stops after 3 consecutive clicks with no new links
4. **Graceful Shutdown**: Always stop with Ctrl+C or SIGTERM (not kill -9)
5. **Resume Support**: Can resume from any checkpoint

---

## 🎉 Success Indicators

The script is working if you see:
```
✓ Click #1 - Show More clicked
  Harvested 16 new links | Total: 32
✓ Click #2 - Show More clicked
  Harvested 16 new links | Total: 48
```

Final output:
```
✓ Total clicks: 200
✓ Total properties: 1500
✓ Runtime: 120.5 minutes
✓ Output saved to: harvested_properties.json
```

---

## 📞 Support

If you encounter issues:
1. Check `production_scraper.log`
2. Check `error_screenshots/` folder
3. Check Chrome installation: `google-chrome --version`
4. Check memory: `free -h`
5. Verify network: `curl -I https://www.thinkspain.com`

---

Good luck with your deployment! 🚀

