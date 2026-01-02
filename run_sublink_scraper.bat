@echo off
echo ========================================
echo ThinkSpain REGIONAL Property Harvester
echo ========================================
echo.
echo Scrapes 17 Autonomous Communities (regions)
echo Global deduplication - stops at 225,422 unique properties
echo Each region saved to separate JSON file
echo.
py -3.12 regional_scraper.py
pause

