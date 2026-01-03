====================================
THINK SPAIN HARVESTER - GCP VM
====================================

HOW TO RUN (Simple 5 Steps):
-----------------------------

1. CREATE VM:
   gcloud compute instances create thinkspain-scraper --zone=us-central1-a --machine-type=e2-medium --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --boot-disk-size=20GB

2. UPLOAD FILES:
   gcloud compute scp --recurse . thinkspain-scraper:~/THINK_SPAIN --zone=us-central1-a

3. SSH TO VM:
   gcloud compute ssh thinkspain-scraper --zone=us-central1-a

4. SETUP (once):
   cd THINK_SPAIN
   chmod +x *.sh
   ./setup_gcp.sh

5. RUN:
   ./run_gcp.sh

DOWNLOAD RESULTS:
-----------------
gcloud compute scp thinkspain-scraper:~/THINK_SPAIN/harvested_properties.json . --zone=us-central1-a

CHECK STATUS:
-------------
./status.sh

STOP:
-----
Press Ctrl+C or: pkill -f production_harvester.py

====================================

