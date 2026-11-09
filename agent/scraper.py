"""
Web scraper for trending system design problems.

Scrapes multiple sources to discover new problem sets that should be added to the repo.
"""

import asyncio
import logging
import re
from typing import Optional

import httpx

from config import settings
from models import Category, TrendingProblem

logger = logging.getLogger("agent.scraper")

# ------------------------------------------------------------------ #
#  Source definitions
# ------------------------------------------------------------------ #

SOURCES = {
    "algomaster": {
        "url": "https://algomaster.io/system-design",
        "type": "html",
    },
    "hellointerview": {
        "url": "https://www.hellointerview.com/courses/system-design",
        "type": "html",
    },
    "designgurus": {
        "url": "https://www.designgurus.io/edutitles/system-design-master-class",
        "type": "html",
    },
    "educative": {
        "url": "https://www.educative.io/courses/grokking-the-system-design-interview",
        "type": "html",
    },
}


class TrendScraper:
    """Scrape trending system design problems from multiple sources."""

    def __init__(self) -> None:
        self.delay = settings.SCRAPER_REQUEST_DELAY
        self.timeout = settings.SCRAPER_TIMEOUT
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.enabled_sources = settings.SCRAPER_SOURCES

    # ------------------------------------------------------------------ #
    #  Main entry point
    # ------------------------------------------------------------------ #
    async def scrape_all(self) -> list:
        """Scrape all enabled sources and return unique problems."""
        all_problems: dict = {}

        for source_name in self.enabled_sources:
            if source_name not in SOURCES:
                logger.warning("Unknown source: %s", source_name)
                continue

            try:
                problems = await self._scrape_source(source_name)
                for prob in problems:
                    key = (prob.category.value, prob.slug)
                    if key not in all_problems:
                        all_problems[key] = prob
                    else:
                        # Keep the one with more sources
                        all_problems[key].source += f", {prob.source}"
            except Exception as exc:
                logger.error("Failed to scrape %s: %s", source_name, exc)

        return list(all_problems.values())

    # ------------------------------------------------------------------ #
    #  Source scrapers
    # ------------------------------------------------------------------ #
    async def _scrape_source(self, source_name: str) -> list:
        """Dispatch to the appropriate scraper for a source."""
        source_info = SOURCES[source_name]
        url = source_info["url"]

        html_text = await self._fetch_html(url)
        if not html_text:
            return []

        if source_name == "algomaster":
            return self._parse_algomaster(html_text, source_name)
        elif source_name == "hellointerview":
            return self._parse_hellointerview(html_text, source_name)
        elif source_name == "designgurus":
            return self._parse_designgurus(html_text, source_name)
        elif source_name == "educative":
            return self._parse_educative(html_text, source_name)

        return []

    # ------------------------------------------------------------------ #
    #  HTTP fetching
    # ------------------------------------------------------------------ #
    async def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                await asyncio.sleep(self.delay)
                return response.text
            except httpx.HTTPError as exc:
                logger.error("HTTP error fetching %s: %s", url, exc)
                return None

    # ------------------------------------------------------------------ #
    #  Parsers
    # ------------------------------------------------------------------ #
    def _parse_algomaster(self, html_text: str, source: str) -> list:
        """Parse AlgoMaster page for system design problems."""
        problems = []

        # Extract problem names from common patterns
        # e.g., "Design Twitter", "Design URL Shortener"
        patterns = [
            r"Design\s+([A-Za-z0-9\s]+?)(?:</|<|\"|')",
            r"([A-Z][A-Za-z\s]+(?:System|Service|Platform))",
        ]

        # Known HLD problems from AlgoMaster
        known_problems = [
            ("URL Shortener", Category.HLD),
            ("TikTok", Category.HLD),
            ("YouTube", Category.HLD),
            ("WhatsApp", Category.HLD),
            ("Uber", Category.HLD),
            ("Instagram", Category.HLD),
            ("LinkedIn", Category.HLD),
            ("Twitter", Category.HLD),
            ("Amazon", Category.HLD),
            ("Spotify", Category.HLD),
            ("Netflix", Category.HLD),
            ("Google Docs", Category.HLD),
            ("Rate Limiter", Category.HLD),
            ("Web Crawler", Category.HLD),
            ("Chat System", Category.HLD),
            ("News Feed", Category.HLD),
            ("Parking Lot", Category.LLD),
            ("LRU Cache", Category.LLD),
            ("Snake and Ladder", Category.LLD),
            ("Tic Tac Toe", Category.LLD),
            ("Vending Machine", Category.LLD),
            ("Stack Overflow", Category.LLD),
            ("Elevator System", Category.LLD),
            ("Pub Sub System", Category.LLD),
            ("Chess", Category.LLD),
            ("Coffee Vending Machine", Category.LLD),
            ("Restaurant Management", Category.LLD),
            ("Movie Ticket Booking", Category.LLD),
            ("Online Auction", Category.LLD),
            ("Food Delivery", Category.LLD),
            ("Ride Sharing", Category.LLD),
        ]

        for name, category in known_problems:
            # Check if the problem appears in the HTML
            if name.lower() in html_text.lower():
                problems.append(TrendingProblem(
                    name=name,
                    category=category,
                    source=source,
                    url=SOURCES["algomaster"]["url"],
                ))

        # Also try to extract any new problems not in our known list
        for match in re.finditer(r"Design\s+([A-Z][A-Za-z\s]{3,30})", html_text):
            name = match.group(1).strip()
            if name and len(name) > 3:
                # Check if already added
                if not any(p.name == name for p in problems):
                    problems.append(TrendingProblem(
                        name=name,
                        category=Category.HLD,
                        source=source,
                        url=SOURCES["algomaster"]["url"],
                    ))

        return problems

    def _parse_hellointerview(self, html_text: str, source: str) -> list:
        """Parse HelloInterview page for system design problems."""
        problems = []

        # Known problems from HelloInterview
        known_problems = [
            ("System Design Fundamentals", Category.HLD),
            ("Load Balancer", Category.HLD),
            ("CDN", Category.HLD),
            ("Cache", Category.HLD),
            ("Database Sharding", Category.HLD),
            ("Message Queue", Category.HLD),
            ("Rate Limiter", Category.HLD),
            ("Web Crawler", Category.HLD),
            ("URL Shortener", Category.HLD),
            ("TikTok", Category.HLD),
            ("YouTube", Category.HLD),
            ("WhatsApp", Category.HLD),
            ("Uber", Category.HLD),
            ("Instagram", Category.HLD),
            ("Twitter", Category.HLD),
            ("Amazon", Category.HLD),
            ("Spotify", Category.HLD),
            ("Netflix", Category.HLD),
            ("Parking Lot", Category.LLD),
            ("LRU Cache", Category.LLD),
            ("Snake and Ladder", Category.LLD),
            ("Tic Tac Toe", Category.LLD),
            ("Vending Machine", Category.LLD),
            ("Stack Overflow", Category.LLD),
            ("Pub Sub System", Category.LLD),
            ("Elevator System", Category.LLD),
            ("Chess", Category.LLD),
            ("Splitwise", Category.LLD),
            ("Digital Wallet", Category.LLD),
        ]

        for name, category in known_problems:
            if name.lower() in html_text.lower():
                problems.append(TrendingProblem(
                    name=name,
                    category=category,
                    source=source,
                    url=SOURCES["hellointerview"]["url"],
                ))

        return problems

    def _parse_designgurus(self, html_text: str, source: str) -> list:
        """Parse DesignGurus page for system design problems."""
        problems = []

        known_problems = [
            ("URL Shortener", Category.HLD),
            ("TikTok", Category.HLD),
            ("YouTube", Category.HLD),
            ("WhatsApp", Category.HLD),
            ("Uber", Category.HLD),
            ("Instagram", Category.HLD),
            ("LinkedIn", Category.HLD),
            ("Twitter", Category.HLD),
            ("Amazon", Category.HLD),
            ("Spotify", Category.HLD),
            ("Netflix", Category.HLD),
            ("Google Docs", Category.HLD),
            ("Rate Limiter", Category.HLD),
            ("Web Crawler", Category.HLD),
            ("Chat System", Category.HLD),
            ("News Feed", Category.HLD),
            ("Parking Lot", Category.LLD),
            ("LRU Cache", Category.LLD),
            ("Snake and Ladder", Category.LLD),
            ("Tic Tac Toe", Category.LLD),
            ("Vending Machine", Category.LLD),
            ("Stack Overflow", Category.LLD),
            ("Pub Sub System", Category.LLD),
            ("Elevator System", Category.LLD),
            ("Chess", Category.LLD),
            ("Coffee Vending Machine", Category.LLD),
            ("Restaurant Management", Category.LLD),
            ("Movie Ticket Booking", Category.LLD),
            ("Online Auction", Category.LLD),
            ("Food Delivery", Category.LLD),
            ("Ride Sharing", Category.LLD),
        ]

        for name, category in known_problems:
            if name.lower() in html_text.lower():
                problems.append(TrendingProblem(
                    name=name,
                    category=category,
                    source=source,
                    url=SOURCES["designgurus"]["url"],
                ))

        return problems

    def _parse_educative(self, html_text: str, source: str) -> list:
        """Parse Educative page for system design problems."""
        problems = []

        known_problems = [
            ("URL Shortener", Category.HLD),
            ("TikTok", Category.HLD),
            ("YouTube", Category.HLD),
            ("WhatsApp", Category.HLD),
            ("Uber", Category.HLD),
            ("Instagram", Category.HLD),
            ("LinkedIn", Category.HLD),
            ("Twitter", Category.HLD),
            ("Amazon", Category.HLD),
            ("Spotify", Category.HLD),
            ("Netflix", Category.HLD),
            ("Google Docs", Category.HLD),
            ("Rate Limiter", Category.HLD),
            ("Web Crawler", Category.HLD),
            ("Chat System", Category.HLD),
            ("News Feed", Category.HLD),
            ("Video Streaming", Category.HLD),
            ("Search Suggestions", Category.HLD),
            ("Autocomplete", Category.HLD),
            ("IP Lookup", Category.HLD),
            ("Contact Management", Category.HLD),
            ("Web Server", Category.HLD),
            ("DNS System", Category.HLD),
            ("Bloom Filter", Category.HLD),
            ("LFU Cache", Category.HLD),
            ("Minion", Category.HLD),
            ("Message Queue", Category.HLD),
            ("Hit Counter", Category.HLD),
            ("Oyster Card", Category.HLD),
            ("Bus Tracking", Category.HLD),
            ("CricInfo", Category.HLD),
            ("Google Maps", Category.HLD),
            ("Free Parking", Category.HLD),
            ("Online File Storage", Category.HLD),
            ("Online Music Player", Category.HLD),
            ("Online Auction", Category.HLD),
            ("Online Gaming", Category.HLD),
            ("Online Exam", Category.HLD),
            ("Online Shopping", Category.HLD),
            ("Online Stock Broker", Category.HLD),
            ("Online Video Streaming", Category.HLD),
            ("Online Job Portal", Category.HLD),
            ("Online Food Delivery", Category.HLD),
            ("Online Ride Sharing", Category.HLD),
            ("Online Hotel Booking", Category.HLD),
            ("Online Flight Booking", Category.HLD),
            ("Online Train Booking", Category.HLD),
            ("Online Bus Booking", Category.HLD),
            ("Online Movie Booking", Category.HLD),
            ("Online Concert Booking", Category.HLD),
            ("Online Event Booking", Category.HLD),
            ("Online Ticket Booking", Category.HLD),
        ]

        for name, category in known_problems:
            if name.lower() in html_text.lower():
                problems.append(TrendingProblem(
                    name=name,
                    category=category,
                    source=source,
                    url=SOURCES["educative"]["url"],
                ))

        return problems
