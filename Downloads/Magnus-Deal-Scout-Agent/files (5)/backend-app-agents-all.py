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


# app/agents/ebay.py

import httpx
from bs4 import BeautifulSoup
from .base import BaseAgent


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
                    print(f"Error parsing eBay item: {e}")
                    continue
            
            self.random_delay()
            
        except Exception as e:
            print(f"Error scraping eBay: {e}")
        
        return listings


# app/agents/facebook.py

class FacebookAgent(BaseAgent):
    """Facebook Marketplace scraper"""
    
    def scrape(self, search) -> List[Dict[str, Any]]:
        """
        Scrape Facebook Marketplace listings.
        
        Note: Facebook requires authentication and uses dynamic JavaScript.
        This is a placeholder implementation.
        """
        print(f"Facebook scraping for: {search.keywords}")
        
        # TODO: Implement Facebook Marketplace scraping
        # Requires Selenium or Playwright for JavaScript rendering
        # and proper authentication handling
        
        return []


# app/agents/gumtree.py

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
                    print(f"Error parsing Gumtree item: {e}")
                    continue
            
            self.random_delay()
            
        except Exception as e:
            print(f"Error scraping Gumtree: {e}")
        
        return listings


# app/agents/craigslist.py

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
                    print(f"Error parsing Craigslist item: {e}")
                    continue
            
            self.random_delay()
            
        except Exception as e:
            print(f"Error scraping Craigslist: {e}")
        
        return listings


# app/agents/__init__.py

from .base import BaseAgent
from .ebay import EbayAgent
from .facebook import FacebookAgent
from .gumtree import GumtreeAgent
from .craigslist import CraigslistAgent

__all__ = [
    'BaseAgent',
    'EbayAgent',
    'FacebookAgent',
    'GumtreeAgent',
    'CraigslistAgent',
]
