"""
Facebook Marketplace Scraper using Playwright
Includes anti-detection measures and human-like behavior
"""

from playwright.async_api import async_playwright, Browser, Page
import asyncio
import random
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FacebookMarketplaceScraper:
    """
    Advanced Facebook Marketplace scraper with anti-detection
    """
    
    # Rotate user agents to avoid detection
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    # Common Facebook Marketplace selectors (these change frequently!)
    SELECTORS = {
        'search_input': 'input[type="search"][placeholder*="Search"]',
        'listing_card': 'a[href*="/marketplace/item/"]',
        'listing_container': 'div[class*="x9f619"]',  # Main content area
    }
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        """
        Initialize the scraper
        
        Args:
            headless: Run browser in headless mode
            proxy: Proxy server URL (optional)
        """
        self.headless = headless
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Start the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self._launch_browser()
        logger.info("Facebook Marketplace scraper started")
    
    async def close(self):
        """Close the browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Facebook Marketplace scraper closed")
    
    async def _launch_browser(self) -> Browser:
        """
        Launch browser with anti-detection measures
        """
        launch_options = {
            'headless': self.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
            ]
        }
        
        if self.proxy:
            launch_options['proxy'] = {'server': self.proxy}
        
        return await self.playwright.chromium.launch(**launch_options)
    
    async def _create_page(self) -> Page:
        """
        Create a new page with realistic browser fingerprint
        """
        # Random user agent
        user_agent = random.choice(self.USER_AGENTS)
        
        # Create context with realistic settings
        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-GB',
            timezone_id='Europe/London',
            permissions=['geolocation'],
            geolocation={'latitude': 51.5074, 'longitude': -0.1278},  # London
        )
        
        page = await context.new_page()
        
        # Remove webdriver flag
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-GB', 'en-US', 'en']
            });
            
            // Override chrome
            window.chrome = {
                runtime: {}
            };
        """)
        
        return page
    
    async def _human_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def _human_scroll(self, page: Page, scrolls: int = 3):
        """
        Scroll page like a human
        """
        for i in range(scrolls):
            # Random scroll distance
            scroll_distance = random.randint(300, 800)
            
            # Scroll with random speed
            await page.evaluate(f"""
                window.scrollBy({{
                    top: {scroll_distance},
                    left: 0,
                    behavior: 'smooth'
                }});
            """)
            
            # Random delay between scrolls
            await self._human_delay(1, 3)
    
    async def _human_mouse_movement(self, page: Page):
        """
        Move mouse randomly to simulate human behavior
        """
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 1800)
            y = random.randint(100, 1000)
            await page.mouse.move(x, y)
            await self._human_delay(0.1, 0.3)
    
    async def search(
        self,
        keywords: str,
        location: str = 'london',
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search Facebook Marketplace for listings
        
        Args:
            keywords: Search keywords
            location: Location (e.g., 'london', 'manchester')
            max_price: Maximum price filter
            min_price: Minimum price filter
            max_results: Maximum number of results to return
            
        Returns:
            List of listings
        """
        page = await self._create_page()
        
        try:
            logger.info(f"Searching Facebook Marketplace: '{keywords}' in {location}")
            
            # Build URL
            url = f'https://www.facebook.com/marketplace/{location}/search'
            
            # Navigate to marketplace
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self._human_delay(2, 4)
            
            # Handle any popups or cookie banners
            await self._handle_popups(page)
            
            # Perform search
            await self._perform_search(page, keywords)
            
            # Wait for results to load
            await page.wait_for_load_state('networkidle', timeout=15000)
            await self._human_delay(2, 3)
            
            # Scroll to load more results
            await self._human_scroll(page, scrolls=4)
            
            # Extract listings
            listings = await self._extract_listings(
                page,
                max_price=max_price,
                min_price=min_price,
                max_results=max_results
            )
            
            logger.info(f"Found {len(listings)} listings for '{keywords}'")
            
            return listings
            
        except Exception as e:
            logger.error(f"Error searching Facebook Marketplace: {e}", exc_info=True)
            
            # Take screenshot for debugging
            try:
                await page.screenshot(path=f'fb_error_{datetime.now().timestamp()}.png')
            except:
                pass
            
            return []
            
        finally:
            await page.close()
    
    async def _handle_popups(self, page: Page):
        """
        Handle cookie banners and popups
        """
        try:
            # Cookie banner - try common selectors
            cookie_buttons = [
                'button[data-cookiebanner="accept_button"]',
                'button:has-text("Accept All")',
                'button:has-text("Allow All Cookies")',
                '[aria-label*="Accept"]',
            ]
            
            for selector in cookie_buttons:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        await self._human_delay(1, 2)
                        logger.info("Accepted cookies")
                        break
                except:
                    continue
            
            # Close any "Login" prompts
            close_buttons = [
                '[aria-label="Close"]',
                'div[role="button"]:has-text("Close")',
            ]
            
            for selector in close_buttons:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        await self._human_delay(0.5, 1)
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error handling popups: {e}")
    
    async def _perform_search(self, page: Page, keywords: str):
        """
        Perform search on Facebook Marketplace
        """
        try:
            # Find search input
            search_input = await page.query_selector(self.SELECTORS['search_input'])
            
            if not search_input:
                # Try alternative selectors
                search_input = await page.query_selector('input[placeholder*="Search"]')
            
            if search_input:
                # Type like a human
                await search_input.click()
                await self._human_delay(0.3, 0.7)
                
                # Type each character with delay
                for char in keywords:
                    await search_input.type(char, delay=random.randint(50, 150))
                
                await self._human_delay(0.5, 1)
                
                # Press Enter
                await page.keyboard.press('Enter')
                
                logger.info(f"Search performed for: {keywords}")
            else:
                logger.warning("Could not find search input")
                
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise
    
    async def _extract_listings(
        self,
        page: Page,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract listing data from the page
        """
        listings = []
        
        try:
            # Wait a bit for listings to render
            await self._human_delay(2, 3)
            
            # Find all listing links
            listing_elements = await page.query_selector_all(self.SELECTORS['listing_card'])
            
            logger.info(f"Found {len(listing_elements)} listing elements")
            
            for element in listing_elements[:max_results * 2]:  # Get extra in case of filtering
                try:
                    listing = await self._extract_listing_data(element)
                    
                    if not listing:
                        continue
                    
                    # Apply price filters
                    if max_price and listing['price'] > max_price:
                        continue
                    if min_price and listing['price'] < min_price:
                        continue
                    
                    listings.append(listing)
                    
                    # Stop if we have enough
                    if len(listings) >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error extracting listing: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting listings: {e}")
        
        return listings
    
    async def _extract_listing_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single listing element
        """
        try:
            # Get URL
            href = await element.get_attribute('href')
            if not href:
                return None
            
            # Extract item ID from URL
            item_id_match = re.search(r'/item/(\d+)', href)
            if not item_id_match:
                return None
            
            item_id = item_id_match.group(1)
            
            # Get all text content
            text_elements = await element.query_selector_all('span')
            texts = []
            
            for elem in text_elements:
                try:
                    text = await elem.inner_text()
                    if text and text.strip():
                        texts.append(text.strip())
                except:
                    continue
            
            if len(texts) < 2:
                return None
            
            # Parse data - Facebook's structure varies, so we look for patterns
            title = None
            price = 0.0
            location = None
            
            for text in texts:
                # Look for price (£150, $150, 150)
                if not title and not any(char.isdigit() for char in text):
                    title = text
                elif not price:
                    price_match = re.search(r'[£$€]?\s*([\d,]+\.?\d*)', text)
                    if price_match:
                        price_str = price_match.group(1).replace(',', '')
                        try:
                            price = float(price_str)
                        except:
                            pass
                elif not location and not any(char.isdigit() for char in text):
                    location = text
            
            # If we couldn't find a title, use first text
            if not title and texts:
                title = texts[0]
            
            # Build full URL
            full_url = href if href.startswith('http') else f'https://www.facebook.com{href}'
            
            return {
                'marketplace': 'facebook',
                'external_id': f'fb_{item_id}',
                'url': full_url,
                'title': title or 'Unknown',
                'price': price,
                'currency': 'GBP',  # Assume GBP for UK
                'location': location,
                'metadata': {
                    'extracted_at': datetime.utcnow().isoformat(),
                    'raw_texts': texts[:5],  # Store first 5 texts for debugging
                }
            }
            
        except Exception as e:
            logger.debug(f"Error extracting listing data: {e}")
            return None
    
    async def monitor_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Monitor a specific Facebook Marketplace search URL
        This is safer than automated searching
        
        Args:
            url: Full Facebook Marketplace search URL
            
        Returns:
            List of listings found at that URL
        """
        page = await self._create_page()
        
        try:
            logger.info(f"Monitoring Facebook URL: {url}")
            
            # Navigate to URL
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self._human_delay(2, 4)
            
            # Handle popups
            await self._handle_popups(page)
            
            # Wait for content
            await page.wait_for_load_state('networkidle', timeout=15000)
            await self._human_delay(1, 2)
            
            # Scroll to load more
            await self._human_scroll(page, scrolls=3)
            
            # Extract listings
            listings = await self._extract_listings(page)
            
            logger.info(f"Found {len(listings)} listings from URL")
            
            return listings
            
        except Exception as e:
            logger.error(f"Error monitoring URL: {e}", exc_info=True)
            return []
            
        finally:
            await page.close()


# Convenience function for one-off searches
async def search_facebook_marketplace(
    keywords: str,
    location: str = 'london',
    max_price: Optional[float] = None,
    headless: bool = True
) -> List[Dict[str, Any]]:
    """
    Quick function to search Facebook Marketplace
    
    Usage:
        results = await search_facebook_marketplace('iPhone 13', 'london', max_price=500)
    """
    async with FacebookMarketplaceScraper(headless=headless) as scraper:
        return await scraper.search(keywords, location, max_price)


# Example usage
if __name__ == "__main__":
    async def main():
        # Example 1: Search
        print("🔍 Searching for iPhone 13 in London under £500...")
        
        async with FacebookMarketplaceScraper(headless=False) as scraper:  # headless=False to watch
            results = await scraper.search(
                keywords='iPhone 13',
                location='london',
                max_price=500,
                max_results=10
            )
            
            print(f"\n✅ Found {len(results)} listings:\n")
            for listing in results:
                print(f"📱 {listing['title']}")
                print(f"   💰 £{listing['price']}")
                print(f"   📍 {listing['location']}")
                print(f"   🔗 {listing['url']}\n")
        
        # Example 2: Monitor URL
        print("\n📡 Monitoring a specific search URL...")
        url = "https://www.facebook.com/marketplace/london/search?query=macbook"
        
        async with FacebookMarketplaceScraper() as scraper:
            results = await scraper.monitor_url(url)
            print(f"Found {len(results)} listings from URL")
    
    # Run
    asyncio.run(main())
