"""Scraper module — web scraping for trending system design problems."""

from agent.scraper.scraper import TrendScraper
from agent.scraper.cache import ResponseCache
from agent.scraper.sources import SOURCES, PROBLEM_KEYWORDS

__all__ = ["TrendScraper", "ResponseCache", "SOURCES", "PROBLEM_KEYWORDS"]
