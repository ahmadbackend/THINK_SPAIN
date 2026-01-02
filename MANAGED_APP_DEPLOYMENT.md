# Managed App Deployment Guide (DigitalOcean App Platform)

## ✅ Problem Solved

You were getting the error:
> "Verify the repo contains supported file types, such as package.json, requirements.txt, or a Dockerfile"

**Solution**: Added the required files for managed app deployment.

---

## 📁 Files Added for Managed Deployment

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (required by managed platforms) |
| `Procfile` | Tells platform how to run the app |
| `runtime.txt` | Specifies Python version |
| `Aptfile` | System packages (Chrome dependencies) |
| `.do/app.yaml` | DigitalOcean App Platform configuration |

---

## 🚀 Deployment Steps (DigitalOcean App Platform)

### 1. Push to GitHub
```bash
git add .
git commit -m "Add managed app deployment files"
git push origin main
```

### 2. Create App on DigitalOcean

1. Go to https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. Select your repository
5. Select branch (usually `main`)
6. Click **"Next"**

### 3. Configure App

**Type**: Choose **"Worker"** (not Web Service, since this is a background scraper)

**Run Command**: Should auto-detect from `Procfile`:
```
python production_harvester.py
```

**Build Command** (if asked):
```
pip install -r requirements.txt
```

### 4. Set Environment Variables

Click **"Environment Variables"** and add:

| Variable | Value |
|----------|-------|
| `HEADLESS` | `true` |
| `MAX_CLICKS` | `200` |
| `START_URL` | `https://www.thinkspain.com/property-for-sale` |
| `OUTPUT_FILE` | `harvested_properties.json` |
| `PROGRESS_FILE` | `scraper_progress.json` |
| `LOG_FILE` | `production_scraper.log` |
| `MAX_RUNTIME_HOURS` | `12` |

### 5. Choose Instance Size

**Recommended**: Basic plan ($5/month minimum)
- Basic ($5/mo) - 512 MB RAM (might be tight)
- **Professional ($12/mo) - 1 GB RAM (recommended)** ✅

### 6. Deploy

Click **"Create Resources"** and wait for deployment.

---

## 📊 Monitoring Your Deployment

### View Logs
1. Go to your app in DigitalOcean dashboard
2. Click **"Runtime Logs"**
3. You'll see the scraper logs in real-time:
```
✓ Click #1 - Show More clicked
  Harvested 16 new links | Total: 32
```

### Download Output Files

**Option 1**: Use DigitalOcean Console
1. Click **"Console"** tab
2. Access files:
```bash
cat harvested_properties.json
cat scraper_progress.json
```

**Option 2**: Set up persistent storage (recommended for long runs)
- Add a volume in App Platform settings
- Mount to `/data`
- Update `.env` to save files to `/data/`

---

## ⚠️ Important Notes for Managed Apps

### 1. **File Persistence**
- Managed apps have **ephemeral filesystems**
- Files are lost when app restarts
- Solutions:
  - Add a **volume** (persistent storage)
  - Save to **object storage** (DigitalOcean Spaces, S3)
  - Use a **database** to store results

### 2. **Chrome/Chromium**
- The `Aptfile` tells DigitalOcean to install Chrome
- `HEADLESS=true` is required (no display available)

### 3. **Runtime Limits**
- Worker processes can run indefinitely
- But consider costs if it runs 24/7
- Set `MAX_RUNTIME_HOURS` appropriately

### 4. **Restart Behavior**
- If app crashes, it auto-restarts
- With resume support, it will continue from last checkpoint
- **But** only if you have persistent storage!

---

## 💾 Adding Persistent Storage (Recommended)

### Without persistent storage:
- ❌ Output files lost on restart
- ❌ Progress lost on restart
- ❌ Logs lost on restart

### With persistent storage:
- ✅ Output files saved permanently
- ✅ Progress persists across restarts
- ✅ Logs kept for review

### How to Add:

1. In App Platform, go to your app
2. Click **"Settings"** → **"Add Volume"**
3. Mount path: `/data`
4. Size: 1 GB minimum
5. Update environment variables:
```
OUTPUT_FILE=/data/harvested_properties.json
PROGRESS_FILE=/data/scraper_progress.json
LOG_FILE=/data/production_scraper.log
ERROR_SCREENSHOT_DIR=/data/error_screenshots
```

---

## 🔄 Alternative: Use Object Storage

Instead of volumes, save to DigitalOcean Spaces:

### 1. Install boto3
Add to `requirements.txt`:
```
boto3==1.34.34
```

### 2. Modify script to upload results
After each save, upload to Spaces:
```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET'
)

s3.upload_file('harvested_properties.json', 'your-bucket', 'harvested_properties.json')
```

---

## 🐛 Troubleshooting

### "Build failed"
- Check that `requirements.txt` is in repo root
- Check Python version in `runtime.txt` is supported

### "Chrome not found"
- Verify `Aptfile` is in repo root
- Check build logs for Chrome installation

### "App keeps restarting"
- Check runtime logs for errors
- Increase instance size if out of memory
- Check `MAX_RUNTIME_HOURS` setting

### "Files not persisting"
- Add a volume (see persistent storage section above)
- Or use object storage

---

## 💰 Cost Estimate

### Basic Worker ($5/mo)
- 512 MB RAM
- Might struggle with Chrome
- Not recommended

### Professional Worker ($12/mo) ✅ Recommended
- 1 GB RAM
- Should handle Chrome fine
- Recommended for production

### With Volume Storage (+$1/mo per GB)
- 1 GB volume = $1/mo
- Total: ~$13/mo

---

## 🎯 Quick Checklist

- [x] `requirements.txt` added ✅
- [x] `Procfile` added ✅
- [x] `runtime.txt` added ✅
- [x] `Aptfile` added ✅
- [ ] Push to GitHub
- [ ] Create app on DigitalOcean
- [ ] Set environment variables
- [ ] Add persistent volume (recommended)
- [ ] Deploy and monitor logs

---

## 📞 Quick Commands

### Push to GitHub
```bash
git add .
git commit -m "Add managed app deployment files"
git push origin main
```

### View logs (from DigitalOcean Console)
```bash
tail -f /var/log/production_scraper.log
cat /data/harvested_properties.json | python3 -m json.tool
```

---

**Your app is now ready for managed deployment!** 🚀

Just push to GitHub and create the app on DigitalOcean App Platform.

