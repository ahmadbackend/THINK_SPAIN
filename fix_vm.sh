#!/bin/bash
# Quick fix for ChromeDriver issue - Run this on your VM

echo "====================================================="
echo "FIXING CHROMEDRIVER ISSUE"
echo "====================================================="

cd ~/THINK_SPAIN || exit 1

# Pull latest fixes from GitHub
echo "Pulling latest updates from GitHub..."
git pull origin main

# Make scripts executable
chmod +x *.sh

echo ""
echo "✓ Fixed! Now run:"
echo "  ./run_gcp.sh"
echo ""

