# app/agents/ebay.py

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class EbayAgent(BaseAgent):
    """eBay marketplace scraper"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ebay.com/sch/i.html"

    def scrape(self, search) -> List[Dict[str, Any]]:
        """
        Scrape eBay listings.

        Args:
            search: Search model instance

        Returns:
            List of listing dictionaries
        """
        listings = []

        try:
            # Build search URL
            params = {
                "_nkw": search.keywords,
                "_sop": 10,  # Sort by ending soonest
            }

            # Add price filters
            if search.min_price:
                params["_udlo"] = search.min_price
            if search.max_price:
                params["_udhi"] = search.max_price

            # Make request
            headers = {"User-Agent": self.user_agent}
            response = httpx.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('li', class_='s-item')

            for item in items[:50]:  # Limit to 50 items
                try:
                    # Extract listing data
                    title_elem = item.find('h3', class_='s-item__title')
                    price_elem = item.find('span', class_='s-item__price')
                    link_elem = item.find('a', class_='s-item__link')
                    image_elem = item.find('img')

                    if not all([title_elem, price_elem, link_elem]):
                        continue

                    # Extract external ID from URL
                    url = link_elem.get('href', '')
                    external_id = url.split('/itm/')[-1].split('?')[0] if '/itm/' in url else ''

                    if not external_id:
                        continue

                    listing = {
                        "external_id": external_id,
                        "title": title_elem.text.strip(),
                        "price": self.extract_price(price_elem.text),
                        "currency": "USD",
                        "url": url,
                        "image_urls": [image_elem.get('src', '')] if image_elem else [],
                        "posted_at": datetime.utcnow(),
                        "metadata": {}
                    }

                    listings.append(listing)

                except Exception as e:
                    logger.error(f"Error parsing eBay item: {e}")
                    continue

            self.random_delay()

        except Exception as e:
            logger.error(f"Error scraping eBay: {e}")

        return listings
