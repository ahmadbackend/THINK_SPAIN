#!/bin/bash
# All-in-one: Setup and Run (for first time use)

echo "Setting up and running harvester..."
chmod +x setup_gcp.sh run_gcp.sh status.sh
./setup_gcp.sh && ./run_gcp.sh

