ve#!/bin/bash
# Test if proxy is working

echo "Testing Oxylabs proxy connection..."
echo ""

# Test with curl
PROXY_USER="customer-brandonks100_vM2Tc-cc-US"
PROXY_PASS="YlDB55GgTr3FVm5_"
PROXY_URL="http://${PROXY_USER}:${PROXY_PASS}@us-pr.oxylabs.io:10000"

echo "Proxy URL: ${PROXY_URL}"
echo ""
echo "Testing connection..."
curl -x "${PROXY_URL}" -s "https://ipinfo.io/json" | head -20

echo ""
echo ""
echo "If you see JSON with IP info above, proxy is working!"
echo "If you see errors, there's a proxy authentication issue."

