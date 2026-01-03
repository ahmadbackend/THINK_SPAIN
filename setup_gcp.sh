#!/bin/bash
# GCP VM Setup Script - Run this ONCE after creating your VM

set -e

echo "====================================================="
echo "GCP VM SETUP FOR THINK SPAIN HARVESTER"
echo "====================================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
echo "Installing Python 3..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install Chrome and ChromeDriver
echo "Installing Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# ChromeDriver (handled automatically by undetected-chromedriver)
echo "ChromeDriver will be managed automatically by undetected-chromedriver package"
CHROME_VERSION=$(google-chrome --version)
echo "Chrome installed: $CHROME_VERSION"

# Install required system libraries
echo "Installing system dependencies..."
sudo apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    xvfb

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_production.txt

echo ""
echo "====================================================="
echo "✓ SETUP COMPLETE!"
echo "====================================================="
echo ""
echo "Next steps:"
echo "1. Upload your project files to this VM"
echo "2. Run: source venv/bin/activate"
echo "3. Run: ./run_gcp.sh"
echo ""

