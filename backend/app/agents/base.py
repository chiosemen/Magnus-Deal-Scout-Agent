# app/agents/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import time
import random
from app.config import settings


class BaseAgent(ABC):
    """Base class for marketplace scraper agents"""

    def __init__(self):
        self.user_agent = settings.SCRAPING_USER_AGENT
        self.timeout = settings.SCRAPING_TIMEOUT
        self.max_retries = settings.SCRAPING_MAX_RETRIES
        self.delay = settings.SCRAPING_DELAY_SECONDS

    @abstractmethod
    def scrape(self, search) -> List[Dict[str, Any]]:
        """
        Scrape listings for a given search.

        Args:
            search: Search model instance

        Returns:
            List of listing dictionaries
        """
        pass

    def random_delay(self):
        """Add random delay between requests"""
        delay = self.delay + random.uniform(0, 2)
        time.sleep(delay)

    def extract_price(self, price_str: str) -> float:
        """Extract numeric price from string"""
        try:
            # Remove currency symbols and commas
            price = ''.join(c for c in price_str if c.isdigit() or c == '.')
            return float(price) if price else 0.0
        except:
            return 0.0
