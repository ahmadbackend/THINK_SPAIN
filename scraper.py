"""
ThinkSpain Property ID Harvester
- Scrapes property IDs and URLs from paginated listings
- Rate limiting with 1 second delay (increases on 500 errors)
- Resume capability: saves progress every 30 minutes (~1800 requests)
- Error handling: retries failed pages, logs failures
- No HTML storage: only extracts IDs and URLs
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime
from pathlib import Path
import sys

# Configuration
BASE_URL = "https://www.thinkspain.com/property-for-sale"
DELAY_SECONDS = 1
DELAY_ON_500 = 10  # seconds to wait on server overload
MAX_RETRIES = 5
SAVE_INTERVAL = 1000  # Save every 1800 requests (30 minutes at 1 req/sec)
MAX_CONSECUTIVE_FAILURES = 3

# File paths
OUTPUT_FILE = "harvested_properties.json"
PROGRESS_FILE = "scraper_progress.json"
LOG_FILE = "scraper.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PropertyHarvester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.harvested_properties = []
        self.current_page = 1
        self.total_harvested = 0
        self.failed_pages = []
        self.consecutive_failures = 0
        self.last_save_time = time.time()
        self.last_save_count = 0

    def load_progress(self):
        """Load previous progress if exists"""
        if Path(PROGRESS_FILE).exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.current_page = progress.get('last_page', 1)
                    self.total_harvested = progress.get('total_harvested', 0)
                    self.failed_pages = progress.get('failed_pages', [])
                    logger.info(f"✓ Resumed from page {self.current_page}, {self.total_harvested} properties already harvested")
                    logger.info(f"✓ {len(self.failed_pages)} failed pages recorded")
            except Exception as e:
                logger.error(f"Error loading progress: {e}")

        if Path(OUTPUT_FILE).exists():
            try:
                with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                    self.harvested_properties = json.load(f)
                    logger.info(f"✓ Loaded {len(self.harvested_properties)} existing properties")
            except Exception as e:
                logger.error(f"Error loading existing data: {e}")

    def save_progress(self, force=False):
        """Save progress to files"""
        current_time = time.time()
        items_since_last_save = self.total_harvested - self.last_save_count

        # Save every SAVE_INTERVAL (30 min) or when forced
        if force or items_since_last_save >= SAVE_INTERVAL:
            try:
                # Save harvested data
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.harvested_properties, f, ensure_ascii=False, indent=2)

                # Save progress
                progress = {
                    'last_page': self.current_page,
                    'total_harvested': self.total_harvested,
                    'failed_pages': self.failed_pages,
                    'last_update': datetime.now().isoformat()
                }
                with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, indent=2)

                self.last_save_time = current_time
                self.last_save_count = self.total_harvested
                logger.info(f"✓ Progress saved: {self.total_harvested} properties, page {self.current_page}")

            except Exception as e:
                logger.error(f"Error saving progress: {e}")

    def get_page_url(self, page_num):
        """Generate URL for page number"""
        if page_num == 1:
            return BASE_URL
        return f"{BASE_URL}?numpag={page_num}"

    def extract_properties_from_html(self, html_content):
        """Extract property IDs and URLs from HTML using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find the JSON-LD script tag with id="item-list-structured-data"
            script_tag = soup.find('script', {'id': 'item-list-structured-data', 'type': 'application/ld+json'})

            if not script_tag:
                logger.warning("No item-list-structured-data found in page")
                return []

            # Parse JSON from script content
            json_data = json.loads(script_tag.string)

            # Extract properties from itemListElement
            properties = []
            item_list = json_data.get('itemListElement', [])

            for item in item_list:
                if item.get('@type') == 'ListItem':
                    product = item.get('item', {})
                    property_id = product.get('productID') or product.get('@id', '').split('/')[-1]
                    property_url = product.get('url') or product.get('@id')

                    if property_id and property_url:
                        properties.append({
                            'id': property_id,
                            'url': property_url
                        })

            return properties

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting properties: {e}")
            return []

    def fetch_page(self, page_num, retry_count=0):
        """Fetch a single page with retry logic"""
        url = self.get_page_url(page_num)

        try:
            response = self.session.get(url, timeout=30)

            # Handle server overload (500 error)
            if response.status_code == 500:
                if retry_count < MAX_RETRIES:
                    logger.warning(f"Server overload (500) on page {page_num}, waiting {DELAY_ON_500}s before retry {retry_count + 1}/{MAX_RETRIES}")
                    time.sleep(DELAY_ON_500)
                    return self.fetch_page(page_num, retry_count + 1)
                else:
                    logger.error(f"Failed page {page_num} after {MAX_RETRIES} retries (500 error)")
                    return None

            # Check for successful response
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Page {page_num} returned status code {response.status_code}")
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying page {page_num} ({retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(DELAY_SECONDS * 2)
                    return self.fetch_page(page_num, retry_count + 1)
                return None

        except requests.RequestException as e:
            logger.error(f"Request error on page {page_num}: {e}")
            if retry_count < MAX_RETRIES:
                logger.info(f"Retrying page {page_num} ({retry_count + 1}/{MAX_RETRIES})")
                time.sleep(DELAY_SECONDS * 2)
                return self.fetch_page(page_num, retry_count + 1)
            return None

    def process_page(self, page_num):
        """Process a single page"""
        logger.info(f"Processing page {page_num}...")

        html_content = self.fetch_page(page_num)

        if html_content is None:
            self.failed_pages.append(page_num)
            logger.error(f"✗ Page {page_num} failed after all retries")
            return False

        # Extract properties
        properties = self.extract_properties_from_html(html_content)

        if not properties:
            logger.warning(f"No properties found on page {page_num} - might be end of results")
            return False

        # Add to harvested list (avoid duplicates)
        existing_ids = {prop['id'] for prop in self.harvested_properties}
        new_properties = [prop for prop in properties if prop['id'] not in existing_ids]

        self.harvested_properties.extend(new_properties)
        self.total_harvested += len(new_properties)

        logger.info(f"✓ Page {page_num}: Found {len(properties)} properties ({len(new_properties)} new)")

        return True

    def run(self):
        """Main scraping loop"""
        logger.info("=" * 60)
        logger.info("ThinkSpain Property ID Harvester Started")
        logger.info("=" * 60)

        # Load previous progress
        self.load_progress()

        try:
            while True:
                # Process current page
                success = self.process_page(self.current_page)

                if success:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1

                    # Stop if 3 consecutive failures
                    if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        logger.error(f"✗ {MAX_CONSECUTIVE_FAILURES} consecutive failures detected")
                        logger.error(f"✗ Failed pages: {self.failed_pages[-MAX_CONSECUTIVE_FAILURES:]}")
                        logger.error("✗ Stopping script as requested")
                        break

                    # Check if we've reached the end (no properties found)
                    if not success and self.consecutive_failures == 1:
                        logger.info("No properties found - likely reached end of results")
                        break

                # Save progress periodically
                self.save_progress()

                # Move to next page
                self.current_page += 1

                # Rate limiting
                time.sleep(DELAY_SECONDS)

        except KeyboardInterrupt:
            logger.info("\n⚠ Script interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            # Final save
            self.save_progress(force=True)

            # Summary
            logger.info("=" * 60)
            logger.info("Scraping Summary")
            logger.info("=" * 60)
            logger.info(f"Total properties harvested: {self.total_harvested}")
            logger.info(f"Last page processed: {self.current_page}")
            logger.info(f"Failed pages: {len(self.failed_pages)}")
            if self.failed_pages:
                logger.info(f"Failed page numbers: {self.failed_pages}")
            logger.info(f"Output saved to: {OUTPUT_FILE}")
            logger.info("=" * 60)


if __name__ == "__main__":
    harvester = PropertyHarvester()
    harvester.run()

