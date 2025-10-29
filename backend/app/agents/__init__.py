# app/agents/__init__.py

from app.agents.base import BaseAgent
from app.agents.ebay import EbayAgent
from app.agents.facebook import FacebookAgent
from app.agents.gumtree import GumtreeAgent
from app.agents.craigslist import CraigslistAgent

__all__ = [
    'BaseAgent',
    'EbayAgent',
    'FacebookAgent',
    'GumtreeAgent',
    'CraigslistAgent',
]
