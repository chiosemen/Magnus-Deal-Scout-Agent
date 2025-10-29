# app/agents/craigslist.py

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class CraigslistAgent(BaseAgent):
    """Craigslist marketplace scraper"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://newyork.craigslist.org/search/sss"

    def scrape(self, search) -> List[Dict[str, Any]]:
        """
        Scrape Craigslist listings.

        Args:
            search: Search model instance

        Returns:
            List of listing dictionaries
        """
        listings = []

        try:
            params = {
                "query": search.keywords,
                "sort": "date",
            }

            if search.min_price:
                params["min_price"] = search.min_price
            if search.max_price:
                params["max_price"] = search.max_price

            headers = {"User-Agent": self.user_agent}
            response = httpx.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('li', class_='result-row')

            for item in items[:50]:
                try:
                    title_elem = item.find('a', class_='result-title')
                    price_elem = item.find('span', class_='result-price')
                    image_elem = item.find('img')

                    if not title_elem:
                        continue

                    url = title_elem.get('href', '')
                    external_id = url.split('/')[-1].replace('.html', '') if url else ''

                    if not external_id:
                        continue

                    price_text = price_elem.text if price_elem else "0"

                    listing = {
                        "external_id": external_id,
                        "title": title_elem.text.strip(),
                        "price": self.extract_price(price_text),
                        "currency": "USD",
                        "url": url,
                        "image_urls": [image_elem.get('src', '')] if image_elem else [],
                        "posted_at": datetime.utcnow(),
                        "metadata": {}
                    }

                    listings.append(listing)

                except Exception as e:
                    logger.error(f"Error parsing Craigslist item: {e}")
                    continue

            self.random_delay()

        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")

        return listings
