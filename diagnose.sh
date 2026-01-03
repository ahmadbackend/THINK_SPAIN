#!/bin/bash
# Diagnostic script to see full error logs

cd ~/THINK_SPAIN

echo "=========================================="
echo "LAST 50 LOG LINES:"
echo "=========================================="
tail -50 production_scraper.log

echo ""
echo "=========================================="
echo "CHECKING FOR ERRORS:"
echo "=========================================="
grep -i "error\|failed\|exception" production_scraper.log | tail -20

echo ""
echo "=========================================="
echo "PROXY STATUS:"
echo "=========================================="
grep -i "proxy" production_scraper.log | tail -10

echo ""
echo "=========================================="
echo "CONSECUTIVE NO-NEW:"
echo "=========================================="
grep "Consecutive:" production_scraper.log | tail -10

echo ""
echo "=========================================="
echo "CLICK ATTEMPTS:"
echo "=========================================="
grep "Click #" production_scraper.log | tail -20

