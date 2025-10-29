# app/agents/gumtree.py

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class GumtreeAgent(BaseAgent):
    """Gumtree marketplace scraper"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.gumtree.com/search"

    def scrape(self, search) -> List[Dict[str, Any]]:
        """
        Scrape Gumtree listings.

        Args:
            search: Search model instance

        Returns:
            List of listing dictionaries
        """
        listings = []

        try:
            # Build search URL
            params = {
                "q": search.keywords,
            }

            if search.location:
                params["location"] = search.location

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
            items = soup.find_all('article', class_='listing-maxi')

            for item in items[:50]:
                try:
                    title_elem = item.find('h2')
                    price_elem = item.find('span', class_='listing-price')
                    link_elem = item.find('a', class_='listing-link')
                    image_elem = item.find('img')

                    if not all([title_elem, link_elem]):
                        continue

                    url = link_elem.get('href', '')
                    external_id = url.split('/')[-1] if url else ''

                    if not external_id:
                        continue

                    price_text = price_elem.text if price_elem else "0"

                    listing = {
                        "external_id": external_id,
                        "title": title_elem.text.strip(),
                        "price": self.extract_price(price_text),
                        "currency": "GBP",
                        "url": f"https://www.gumtree.com{url}" if url.startswith('/') else url,
                        "image_urls": [image_elem.get('src', '')] if image_elem else [],
                        "posted_at": datetime.utcnow(),
                        "metadata": {}
                    }

                    listings.append(listing)

                except Exception as e:
                    logger.error(f"Error parsing Gumtree item: {e}")
                    continue

            self.random_delay()

        except Exception as e:
            logger.error(f"Error scraping Gumtree: {e}")

        return listings
