"""
Production Selenium Harvester with Full Error Handling & Resume Support
- Graceful shutdown with signal handlers
- Popup detection and closing
- Resume from last checkpoint
- Retry logic for failed clicks
- Memory monitoring
- Auto-save after each click
- Screenshot on errors only
- Environment configuration
- GCP VM ready with Xvfb virtual display
- Headed mode for better detection avoidance
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium_stealth import stealth
import time
import json
import os
import signal
import sys
import logging
from datetime import datetime
import psutil
from pathlib import Path
import random

# ============================================================================
# CONFIGURATION - Can be overridden with environment variables
# ============================================================================
MAX_CLICKS = int(os.getenv('MAX_CLICKS', '15627'))
HEADLESS = False  # Always run with head mode using Xvfb virtual display
START_URL = os.getenv('START_URL', 'https://www.thinkspain.com/property-for-sale')
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'harvested_properties.json')
PROGRESS_FILE = os.getenv('PROGRESS_FILE', 'scraper_progress.json')
LOG_FILE = os.getenv('LOG_FILE', 'production_scraper.log')
ERROR_SCREENSHOT_DIR = os.getenv('ERROR_SCREENSHOT_DIR', 'error_screenshots')
MAX_CONSECUTIVE_NO_NEW = 5  # Stop after 5 consecutive clicks with no new links
RETRY_ATTEMPTS = 3  # Retry failed clicks 3 times
CLICK_TIMEOUT = 30  # Maximum seconds to wait for a click to complete
MAX_RUNTIME_HOURS = int(os.getenv('MAX_RUNTIME_HOURS', '12'))  # Maximum runtime

# Realistic timing (human-like behavior)
MIN_WAIT_BETWEEN_CLICKS = float(os.getenv('MIN_WAIT_BETWEEN_CLICKS', '5'))  # Minimum seconds between clicks
MAX_WAIT_BETWEEN_CLICKS = float(os.getenv('MAX_WAIT_BETWEEN_CLICKS', '10'))  # Maximum seconds between clicks
PAGE_LOAD_WAIT = float(os.getenv('PAGE_LOAD_WAIT', '7'))  # Wait for content to load after click

# Proxy disabled - not needed
USE_PROXY = False

# ============================================================================
# SETUP
# ============================================================================
os.makedirs(ERROR_SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionHarvester:
    def __init__(self):
        self.driver = None
        self.property_links = set()
        self.clicks_performed = 0
        self.start_time = datetime.now()
        self.shutdown_requested = False
        self.consecutive_no_new = 0
        self.last_checkpoint_click = 0

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info("=" * 70)
        logger.info("PRODUCTION SELENIUM HARVESTER - HEADED MODE WITH XVFB")
        logger.info(f"Max clicks: {MAX_CLICKS}")
        logger.info(f"Headed Mode: TRUE (Xvfb virtual display)")
        logger.info(f"Start URL: {START_URL}")
        logger.info(f"Output: {OUTPUT_FILE}")
        logger.info(f"Timing: {MIN_WAIT_BETWEEN_CLICKS}-{MAX_WAIT_BETWEEN_CLICKS}s between clicks")
        logger.info(f"Page load wait: {PAGE_LOAD_WAIT}s + random(0-2s)")
        logger.info(f"Max consecutive no-new: {MAX_CONSECUTIVE_NO_NEW}")
        logger.info(f"Max runtime: {MAX_RUNTIME_HOURS} hours")
        logger.info("=" * 70)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.warning(f"\n⚠ Received signal {signum} - Initiating graceful shutdown...")
        self.shutdown_requested = True

    def check_runtime_limit(self):
        """Check if we've exceeded maximum runtime"""
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600
        if runtime > MAX_RUNTIME_HOURS:
            logger.warning(f"⚠ Maximum runtime of {MAX_RUNTIME_HOURS} hours exceeded")
            return True
        return False

    def log_memory_usage(self):
        """Log current memory usage"""
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"  Memory usage: {memory_mb:.1f} MB")
        except Exception as e:
            logger.debug(f"Could not get memory usage: {e}")

    def take_error_screenshot(self, error_context=""):
        """Take screenshot on error"""
        try:
            if self.driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{ERROR_SCREENSHOT_DIR}/error_{timestamp}_{error_context}.png"
                self.driver.save_screenshot(filename)
                logger.info(f"  Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")


    def load_progress(self):
        """Load progress from checkpoint file"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.clicks_performed = data.get('clicks_performed', 0)
                    self.property_links = set(data.get('property_links', []))
                    self.consecutive_no_new = data.get('consecutive_no_new', 0)  # Load the counter too
                    logger.info(f"✓ Resumed from checkpoint: {self.clicks_performed} clicks, {len(self.property_links)} properties, {self.consecutive_no_new} consecutive no-new")
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")
                logger.info("Starting fresh...")

    def save_progress(self):
        """Save progress checkpoint"""
        try:
            data = {
                'clicks_performed': self.clicks_performed,
                'property_links': sorted(list(self.property_links)),
                'last_updated': datetime.now().isoformat(),
                'consecutive_no_new': self.consecutive_no_new
            }
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"  Progress saved: {self.clicks_performed} clicks")
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def save_output(self):
        """Save harvested links to output file"""
        try:
            output_data = {
                'total_properties': len(self.property_links),
                'clicks_performed': self.clicks_performed,
                'harvested_at': datetime.now().isoformat(),
                'properties': sorted(list(self.property_links))
            }
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved {len(self.property_links)} properties to {OUTPUT_FILE}")
        except Exception as e:
            logger.error(f"Failed to save output: {e}")

    def setup_driver(self):
        """Setup undetected Chrome with stealth for headed mode"""
        logger.info("Setting up Chrome driver in headed mode...")

        try:
            options = uc.ChromeOptions()

            # Chrome options for stability and stealth
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Additional options for Linux/GCP
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--remote-debugging-port=9222')

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
            return True

        except Exception as e:
            logger.error(f"Failed to setup driver: {e}", exc_info=True)
            self.take_error_screenshot("driver_setup")
            return False

    def close_popups(self):
        """Detect and close any popups"""
        try:
            # Common popup patterns
            popup_selectors = [
                "button[class*='cookie']",
                "button[class*='accept']",
                "button[class*='close']",
                "a[class*='close']",
                ".modal-close",
                "[aria-label='Close']",
                ".popup-close",
                "#close-popup"
            ]

            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            logger.info(f"  Closed popup: {selector}")
                            time.sleep(0.5)
                except:
                    pass

        except Exception as e:
            logger.debug(f"Popup check error: {e}")

    def load_page(self, url):
        """Load page with error handling and popup closing"""
        logger.info(f"Loading page: {url}")

        for attempt in range(RETRY_ATTEMPTS):
            try:
                self.driver.get(url)
                time.sleep(3)

                # Close any popups
                self.close_popups()

                logger.info("✓ Page loaded")
                return True

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS} failed: {e}")
                if attempt == RETRY_ATTEMPTS - 1:
                    logger.error("Failed to load page after all retries")
                    self.take_error_screenshot("page_load")
                    return False
                time.sleep(2)

        return False

    def find_show_more_button(self):
        """Find the Show More button with timeout"""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.show-more.pagination-load-next"))
            )
            return button
        except TimeoutException:
            return None

    def click_show_more(self):
        """Click Show More with retry logic and realistic delays"""

        for attempt in range(RETRY_ATTEMPTS):
            try:
                # Close any popups that might have appeared
                self.close_popups()

                button = self.find_show_more_button()
                if not button:
                    logger.warning("Show More button not found")
                    return False

                # Random delay before scrolling (human-like)
                time.sleep(random.uniform(0.5, 1.5))

                # Scroll into view smoothly
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)

                # Random delay after scrolling
                time.sleep(random.uniform(0.8, 2.0))

                # Click
                self.driver.execute_script("arguments[0].click();", button)
                self.clicks_performed += 1

                logger.info(f"✓ Click #{self.clicks_performed} - Show More clicked")

                # Wait for content to load (longer, realistic wait)
                wait_time = random.uniform(PAGE_LOAD_WAIT, PAGE_LOAD_WAIT + 2)
                logger.info(f"  Waiting {wait_time:.1f}s for content to load...")
                time.sleep(wait_time)

                return True

            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1}/{RETRY_ATTEMPTS} failed: {e}")
                if attempt == RETRY_ATTEMPTS - 1:
                    logger.error(f"Failed to click after {RETRY_ATTEMPTS} attempts")
                    self.take_error_screenshot(f"click_{self.clicks_performed}")
                    return False
                time.sleep(2)

        return False

    def harvest_property_links(self):
        """Extract property links from current page"""
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property-for-sale/']")

            before_count = len(self.property_links)

            for link in links:
                href = link.get_attribute('href')
                if href and '/property-for-sale/' in href:
                    property_id = href.split('/property-for-sale/')[-1].split('?')[0].split('#')[0]
                    if property_id and property_id.isdigit():
                        clean_url = f"https://www.thinkspain.com/property-for-sale/{property_id}"
                        self.property_links.add(clean_url)

            new_count = len(self.property_links) - before_count

            if new_count == 0:
                self.consecutive_no_new += 1
                logger.warning(f"  ⚠ No new links | Consecutive: {self.consecutive_no_new}/{MAX_CONSECUTIVE_NO_NEW}")
            else:
                self.consecutive_no_new = 0
                logger.info(f"  Harvested {new_count} new links | Total: {len(self.property_links)}")

            return new_count

        except Exception as e:
            logger.error(f"Error harvesting links: {e}")
            self.take_error_screenshot("harvest")
            return 0

    def run(self):
        """Main execution loop with full error handling"""

        try:
            # Load previous progress if resuming
            self.load_progress()
            resume_from_click = self.clicks_performed  # Store how many clicks were already done

            # Setup driver
            if not self.setup_driver():
                logger.error("Failed to setup driver. Exiting.")
                return

            # Load initial page
            if not self.load_page(START_URL):
                logger.error("Failed to load initial page. Exiting.")
                return

            # Human-like delay after page loads
            initial_wait = random.uniform(2, 4)
            logger.info(f"Waiting {initial_wait:.1f}s for initial page to fully load...")
            time.sleep(initial_wait)

            # RESUME LOGIC: Skip to the page where we left off
            if resume_from_click > 0:
                logger.info("=" * 70)
                logger.info(f"RESUMING: Fast-forwarding through {resume_from_click} already-clicked pages...")
                logger.info("(Not harvesting, just clicking to reach last position)")
                logger.info("=" * 70)

                for skip_click in range(resume_from_click):
                    if not self.click_show_more():
                        logger.error(f"Failed to skip to click {skip_click + 1}. Starting from here...")
                        break

                    # Short delay during fast-forward (faster than normal)
                    if (skip_click + 1) % 10 == 0:
                        logger.info(f"  Fast-forwarded {skip_click + 1}/{resume_from_click} clicks...")
                    time.sleep(random.uniform(1, 2))  # Faster during resume

                logger.info("=" * 70)
                logger.info(f"✓ REACHED POSITION: Click {resume_from_click}")
                logger.info("Now starting fresh harvest from this point...")
                logger.info("=" * 70)
                time.sleep(2)

            # Harvest current page (whether starting fresh or after resume)
            logger.info("\nHarvesting current page...")
            self.harvest_property_links()
            self.save_progress()  # Save after initial harvest
            self.save_output()     # Save to output file

            # Main clicking loop
            logger.info(f"\nStarting click loop (target: {MAX_CLICKS} clicks)...\n")

            while self.clicks_performed < MAX_CLICKS:
                # Check for shutdown signals
                if self.shutdown_requested:
                    logger.warning("Shutdown requested. Saving and exiting...")
                    break

                # Check runtime limit
                if self.check_runtime_limit():
                    logger.warning("Runtime limit exceeded. Saving and exiting...")
                    break

                # Check consecutive no-new threshold
                if self.consecutive_no_new >= MAX_CONSECUTIVE_NO_NEW:
                    logger.info(f"✓ Reached limit: {MAX_CONSECUTIVE_NO_NEW} consecutive clicks with no new links")
                    break

                # Click Show More
                if not self.click_show_more():
                    logger.warning("Failed to click Show More. Stopping...")
                    break

                # Harvest after each click
                self.harvest_property_links()

                # Save progress after EVERY click (as requested)
                self.save_progress()
                self.save_output()

                # Progress report every 10 clicks
                if self.clicks_performed % 10 == 0:
                    logger.info(f"\n--- Progress Report ---")
                    logger.info(f"Clicks: {self.clicks_performed}/{MAX_CLICKS}")
                    logger.info(f"Properties: {len(self.property_links)}")
                    logger.info(f"Runtime: {(datetime.now() - self.start_time).total_seconds() / 60:.1f} min")
                    self.log_memory_usage()
                    logger.info(f"---\n")

                # Random delay between clicks (human-like behavior)
                if self.clicks_performed < MAX_CLICKS:
                    delay = random.uniform(MIN_WAIT_BETWEEN_CLICKS, MAX_WAIT_BETWEEN_CLICKS)
                    logger.info(f"  Waiting {delay:.1f}s before next click...")
                    time.sleep(delay)

            # Final harvest
            logger.info("\nFinal harvest...")
            self.harvest_property_links()

        except KeyboardInterrupt:
            logger.warning("\n⚠ Interrupted by user (Ctrl+C)")

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            self.take_error_screenshot("main_loop")

        finally:
            # Always save before exiting
            logger.info("\n" + "=" * 70)
            logger.info("FINALIZING")
            logger.info("=" * 70)

            self.save_progress()
            self.save_output()

            # Summary
            runtime = (datetime.now() - self.start_time).total_seconds() / 60
            logger.info(f"\n✓ Total clicks: {self.clicks_performed}")
            logger.info(f"✓ Total properties: {len(self.property_links)}")
            logger.info(f"✓ Runtime: {runtime:.1f} minutes")
            logger.info(f"✓ Output saved to: {OUTPUT_FILE}")
            logger.info(f"✓ Progress saved to: {PROGRESS_FILE}")

            # Cleanup
            self.cleanup()

    def cleanup(self):
        """Cleanup browser resources"""
        if self.driver:
            try:
                logger.info("\nClosing browser...")
                self.driver.quit()
                logger.info("✓ Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("PRODUCTION SELENIUM HARVESTER")
    print("=" * 70)
    print(f"Starting in 3 seconds...")
    print("Press Ctrl+C to stop gracefully at any time")
    print("=" * 70)
    time.sleep(3)

    harvester = ProductionHarvester()
    harvester.run()

    print("\n✓ Execution complete!")

