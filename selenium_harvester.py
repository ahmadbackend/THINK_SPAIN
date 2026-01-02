"""
Selenium Script with Undetected Chrome + Stealth
Clicks "Show More" button and harvests property links
Test: 200 clicks to verify 1,500 property limit and duplicates
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
import time
import pandas as pd
from datetime import datetime
import logging

# Configuration
TEST_CLICKS = 200  # Number of times to click "Show More" for testing
HEADLESS = False  # Set to True to run headless
# Use a broader search to test full pagination (all of Spain has more properties)
START_URL = "https://www.thinkspain.com/property-for-sale"
OUTPUT_CSV = "harvested_links_test.csv"
LOG_FILE = "selenium_scraper.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PropertyHarvester:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.property_links = set()  # Use set to track unique links
        self.clicks_performed = 0

    def setup_driver(self):
        """Setup undetected Chrome with stealth"""
        logger.info("Setting up undetected Chrome driver...")

        options = uc.ChromeOptions()

        if self.headless:
            options.add_argument('--headless')

        # Additional stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Initialize undetected Chrome
        self.driver = uc.Chrome(options=options, version_main=None)

        # Apply selenium-stealth
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        logger.info("✓ Driver setup complete")

    def load_page(self, url):
        """Load the initial page"""
        logger.info(f"Loading page: {url}")
        self.driver.get(url)
        time.sleep(3)  # Wait for page to fully load
        logger.info("✓ Page loaded")

    def find_show_more_button(self):
        """Find the 'Show More' button"""
        try:
            # Wait for button to be clickable
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.show-more.pagination-load-next"))
            )
            return button
        except TimeoutException:
            logger.warning("Show More button not found or not clickable")
            return None

    def click_show_more(self):
        """Click the Show More button"""
        try:
            button = self.find_show_more_button()
            if button:
                # Scroll button into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)

                # Click using JavaScript to avoid interception
                self.driver.execute_script("arguments[0].click();", button)
                self.clicks_performed += 1

                # Wait for new content to load
                time.sleep(1.5)

                logger.info(f"✓ Click #{self.clicks_performed} - Show More clicked")
                return True
            else:
                logger.warning("Show More button not found")
                return False
        except Exception as e:
            logger.error(f"Error clicking Show More: {e}")
            return False

    def harvest_property_links(self):
        """Extract all property links from the current page"""
        try:
            # Find all property links (href="/property-for-sale/XXXXXXX")
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property-for-sale/']")

            before_count = len(self.property_links)

            for link in links:
                href = link.get_attribute('href')
                if href and '/property-for-sale/' in href:
                    # Extract clean property ID URL
                    if href.startswith('http'):
                        # Full URL like "https://www.thinkspain.com/property-for-sale/8917427"
                        property_id = href.split('/property-for-sale/')[-1].split('?')[0].split('#')[0]
                        if property_id and property_id.isdigit():
                            clean_url = f"https://www.thinkspain.com/property-for-sale/{property_id}"
                            self.property_links.add(clean_url)

            new_count = len(self.property_links) - before_count
            logger.info(f"  Harvested {new_count} new links | Total unique: {len(self.property_links)}")

            return new_count
        except Exception as e:
            logger.error(f"Error harvesting links: {e}")
            return 0

    def run_test(self, max_clicks=200):
        """Run the test: click Show More N times and harvest all links"""
        logger.info("=" * 70)
        logger.info("SELENIUM PROPERTY HARVESTER - TEST MODE")
        logger.info(f"Target clicks: {max_clicks}")
        logger.info("=" * 70)

        try:
            self.setup_driver()
            self.load_page(START_URL)

            # Harvest initial page
            logger.info("\nHarvesting initial page...")
            self.harvest_property_links()

            # Click Show More N times
            logger.info(f"\nStarting to click Show More {max_clicks} times...\n")

            consecutive_no_new = 0

            for i in range(max_clicks):
                if not self.click_show_more():
                    logger.warning(f"Failed to click Show More at attempt {i+1}")
                    break

                # Harvest after each click
                new_links = self.harvest_property_links()

                # Check if we're getting new links
                if new_links == 0:
                    consecutive_no_new += 1
                    logger.warning(f"⚠ No new links for {consecutive_no_new} consecutive clicks")

                    if consecutive_no_new >= 5:
                        logger.info("✓ Detected pagination loop (5 clicks with no new links)")
                        logger.info("✓ Reached the limit of available properties")
                        break
                else:
                    consecutive_no_new = 0

                # Progress report every 10 clicks
                if (i + 1) % 10 == 0:
                    logger.info(f"\n--- Progress Report ---")
                    logger.info(f"Clicks performed: {self.clicks_performed}")
                    logger.info(f"Unique links: {len(self.property_links)}")
                    logger.info(f"---\n")

            # Final harvest
            logger.info("\nFinal harvest...")
            self.harvest_property_links()

        except KeyboardInterrupt:
            logger.info("\n⚠ Interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self.save_results()
            self.cleanup()

    def save_results(self):
        """Save harvested links to CSV"""
        logger.info("\n" + "=" * 70)
        logger.info("SAVING RESULTS")
        logger.info("=" * 70)

        if not self.property_links:
            logger.warning("No links to save")
            return

        # Convert set to list and create DataFrame
        links_list = sorted(list(self.property_links))

        # Extract property IDs
        data = []
        for url in links_list:
            property_id = url.split('/property-for-sale/')[-1]
            data.append({
                'property_id': property_id,
                'url': url
            })

        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

        logger.info(f"✓ Saved {len(links_list)} unique property links to {OUTPUT_CSV}")
        logger.info(f"✓ Total clicks performed: {self.clicks_performed}")
        logger.info(f"✓ Unique properties: {len(self.property_links)}")

        # Check for duplicates (should be 0 since we used a set)
        duplicates = len(data) - len(set(d['property_id'] for d in data))
        logger.info(f"✓ Duplicates removed: {duplicates}")

        logger.info("=" * 70)

    def cleanup(self):
        """Close the browser"""
        if self.driver:
            logger.info("\nClosing browser...")
            self.driver.quit()
            logger.info("✓ Browser closed")


if __name__ == "__main__":
    print("=" * 70)
    print("SELENIUM PROPERTY LINK HARVESTER")
    print("=" * 70)
    print(f"Test Mode: Click 'Show More' {TEST_CLICKS} times")
    print(f"Start URL: {START_URL}")
    print(f"Headless: {HEADLESS}")
    print(f"Output: {OUTPUT_CSV}")
    print("=" * 70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    harvester = PropertyHarvester(headless=HEADLESS)
    harvester.run_test(max_clicks=TEST_CLICKS)

    print("\n✓ Test complete! Check the output files:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {LOG_FILE}")

