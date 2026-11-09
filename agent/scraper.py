"""
Web scraper for trending system design problems.

Scrapes multiple sources to discover new problem sets that should be added to the repo.
Features:
- HTML response caching to avoid redundant fetches
- Exponential backoff retry logic
- Real HTML parsing with regex-based extraction
- Multiple sources including GitHub trending repos
- Rate limiting between requests
"""

import asyncio
import hashlib
import json
import logging
import math
import re
import time
from datetime import datetime, timezone
from pathlib import Path
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
        "urls": [
            "https://algomaster.io/system-design",
            "https://algomaster.io/learn/lld",
        ],
        "type": "html",
    },
    "hellointerview": {
        "urls": [
            "https://www.hellointerview.com/courses/system-design",
        ],
        "type": "html",
    },
    "designgurus": {
        "urls": [
            "https://www.designgurus.io/edutitles/system-design-master-class",
        ],
        "type": "html",
    },
    "educative": {
        "urls": [
            "https://www.educative.io/courses/grokking-the-system-design-interview",
        ],
        "type": "html",
    },
    "github_trending": {
        "urls": [
            "https://github.com/trending?since=monthly",
        ],
        "type": "github",
    },
}

# Comprehensive problem keyword database for detection
PROBLEM_KEYWORDS = {
    # HLD - System Design
    "url shortener": (Category.HLD, ["URL Shortener", "TinyURL", "Bitly"]),
    "tiktok": (Category.HLD, ["TikTok", "Short Video", "Video Feed"]),
    "youtube": (Category.HLD, ["YouTube", "Video Streaming", "Video Platform"]),
    "whatsapp": (Category.HLD, ["WhatsApp", "Messaging App", "Chat Application"]),
    "uber": (Category.HLD, ["Uber", "Ride Sharing", "Ride Hailing"]),
    "instagram": (Category.HLD, ["Instagram", "Photo Sharing", "Image Feed"]),
    "linkedin": (Category.HLD, ["LinkedIn", "Professional Network", "Social Graph"]),
    "twitter": (Category.HLD, ["Twitter", "X Platform", "Microblog", "Tweet"]),
    "amazon": (Category.HLD, ["Amazon", "E-commerce", "Online Shopping"]),
    "spotify": (Category.HLD, ["Spotify", "Music Streaming", "Audio Platform"]),
    "netflix": (Category.HLD, ["Netflix", "Video on Demand", "Streaming Service"]),
    "google docs": (Category.HLD, ["Google Docs", "Collaborative Editor", "Real-time Editor"]),
    "rate limiter": (Category.HLD, ["Rate Limiter", "Throttling", "Rate Limiting"]),
    "web crawler": (Category.HLD, ["Web Crawler", "Spider", "Search Crawler"]),
    "chat system": (Category.HLD, ["Chat System", "Chat Application", "Messaging"]),
    "news feed": (Category.HLD, ["News Feed", "Social Feed", "Activity Feed"]),
    "rag system": (Category.HLD, ["RAG", "Retrieval Augmented Generation", "Vector Search"]),
    "llm inference": (Category.HLD, ["LLM Inference", "Model Serving", "AI Inference"]),
    "fraud detection": (Category.HLD, ["Fraud Detection", "Fraud Prevention"]),
    "flash sale": (Category.HLD, ["Flash Sale", "Lightning Deal"]),
    "ad platform": (Category.HLD, ["Ad Platform", "Ad Tech", "Advertising"]),
    "ci/cd pipeline": (Category.HLD, ["CI/CD", "Continuous Integration", "Deployment Pipeline"]),
    "semantic search": (Category.HLD, ["Semantic Search", "Vector Search", "Similarity Search"]),
    "digital wallet": (Category.HLD, ["Digital Wallet", "Payment Wallet", "E-wallet"]),
    "workflow orchestration": (Category.HLD, ["Workflow", "Orchestration", "DAG Execution"]),
    "live streaming": (Category.HLD, ["Live Streaming", "Video Live", "Twitch"]),
    "notification system": (Category.HLD, ["Notification", "Push Notification"]),
    "payment system": (Category.HLD, ["Payment", "Payment Gateway"]),
    "dns system": (Category.HLD, ["DNS", "Domain Name System"]),
    "web server": (Category.HLD, ["Web Server", "HTTP Server"]),
    "load balancer": (Category.HLD, ["Load Balancer", "LB"]),
    "cdn": (Category.HLD, ["CDN", "Content Delivery Network"]),
    "message queue": (Category.HLD, ["Message Queue", "MQ", "Kafka"]),
    "cache system": (Category.HLD, ["Cache", "Caching System"]),
    "search engine": (Category.HLD, ["Search Engine", "Full Text Search"]),
    "recommendation system": (Category.HLD, ["Recommendation", "Rec System"]),
    "analytics pipeline": (Category.HLD, ["Analytics", "Data Pipeline"]),
    "log aggregation": (Category.HLD, ["Log Aggregation", "Logging System"]),
    "file storage": (Category.HLD, ["File Storage", "Dropbox", "Cloud Storage"]),
    "image processing": (Category.HLD, ["Image Processing", "Image Service"]),
    "autocomplete": (Category.HLD, ["Autocomplete", "Typeahead", "Search Suggestions"]),
    "hit counter": (Category.HLD, ["Hit Counter", "Page Counter"]),
    "google maps": (Category.HLD, ["Google Maps", "Map Service"]),
    "stock broker": (Category.HLD, ["Stock Broker", "Trading Platform"]),
    "hotel booking": (Category.HLD, ["Hotel Booking", "Accommodation"]),
    "flight booking": (Category.HLD, ["Flight Booking", "Airline"]),
    "cricinfo": (Category.HLD, ["CricInfo", "Cricket Score", "Live Score"]),
    # LLD - Object Oriented Design
    "parking lot": (Category.LLD, ["Parking Lot", "Parking"]),
    "lru cache": (Category.LLD, ["LRU Cache", "Least Recently Used"]),
    "lfu cache": (Category.LLD, ["LFU Cache", "Least Frequently Used"]),
    "snake and ladder": (Category.LLD, ["Snake and Ladder", "Snakes and Ladders"]),
    "snake game": (Category.LLD, ["Snake Game"]),
    "tic tac toe": (Category.LLD, ["Tic Tac Toe", "Tic-Tac-Toe"]),
    "vending machine": (Category.LLD, ["Vending Machine"]),
    "stack overflow": (Category.LLD, ["Stack Overflow", "Q&A Platform"]),
    "elevator system": (Category.LLD, ["Elevator", "Lift System"]),
    "pub sub system": (Category.LLD, ["Pub Sub", "Publisher Subscriber"]),
    "chess": (Category.LLD, ["Chess Game", "Chess"]),
    "coffee vending": (Category.LLD, ["Coffee Vending", "Coffee Machine"]),
    "restaurant management": (Category.LLD, ["Restaurant", "Restaurant Management"]),
    "movie ticket booking": (Category.LLD, ["Movie Ticket", "Cinema Booking"]),
    "online auction": (Category.LLD, ["Online Auction", "Auction"]),
    "food delivery": (Category.LLD, ["Food Delivery", "Swiggy", "Zomato"]),
    "ride sharing": (Category.LLD, ["Ride Sharing", "Ride Share"]),
    "splitwise": (Category.LLD, ["Splitwise", "Expense Splitting"]),
    "text editor": (Category.LLD, ["Text Editor", "Editor"]),
    "atm": (Category.LLD, ["ATM", "Automated Teller"]),
    "logging framework": (Category.LLD, ["Logging", "Logger"]),
    "car rental": (Category.LLD, ["Car Rental", "Vehicle Rental"]),
    "library management": (Category.LLD, ["Library", "Book Management"]),
    "traffic signal": (Category.LLD, ["Traffic Signal", "Traffic Light"]),
    "concert booking": (Category.LLD, ["Concert Booking", "Event Ticket"]),
    "social network": (Category.LLD, ["Social Network", "Social Media"]),
    "digital wallet": (Category.LLD, ["Digital Wallet", "Wallet"]),
    "airline management": (Category.LLD, ["Airline", "Flight Management"]),
    "stock exchange": (Category.LLD, ["Stock Exchange", "Trading"]),
    "course registration": (Category.LLD, ["Course Registration", "University"]),
    # Distributed Systems
    "vector database": (Category.DISTRIBUTED_SYSTEMS, ["Vector DB", "Vector Database", "ANN"]),
    "feature store": (Category.DISTRIBUTED_SYSTEMS, ["Feature Store", "ML Features"]),
    "secret management": (Category.DISTRIBUTED_SYSTEMS, ["Secret Management", "Vault"]),
    "distributed cache": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Cache", "Cache Cluster"]),
    "distributed lock": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Lock", "Lock Service"]),
    "distributed tracing": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Tracing", "Tracing"]),
    "distributed config": (Category.DISTRIBUTED_SYSTEMS, ["Distributed Config", "Config Service"]),
    "event sourcing": (Category.DISTRIBUTED_SYSTEMS, ["Event Sourcing", "Event Store"]),
    "circuit breaker": (Category.DISTRIBUTED_SYSTEMS, ["Circuit Breaker"]),
    "idempotency": (Category.DISTRIBUTED_SYSTEMS, ["Idempotency", "Idempotent"]),
    "saga pattern": (Category.DISTRIBUTED_SYSTEMS, ["Saga", "Saga Pattern"]),
    "consistent hashing": (Category.DISTRIBUTED_SYSTEMS, ["Consistent Hashing"]),
    "leader election": (Category.DISTRIBUTED_SYSTEMS, ["Leader Election", "Election"]),
    # Trade-offs
    "sql vs nosql": (Category.TRADEOFFS, ["SQL vs NoSQL", "Relational vs Non-relational"]),
    "monolith vs microservices": (Category.TRADEOFFS, ["Monolith vs Microservices"]),
    "rest vs grpc": (Category.TRADEOFFS, ["REST vs gRPC"]),
    "graphql vs rest": (Category.TRADEOFFS, ["GraphQL vs REST"]),
    "vector db vs traditional": (Category.TRADEOFFS, ["Vector DB vs Traditional"]),
    "edge vs centralized": (Category.TRADEOFFS, ["Edge vs Centralized", "Edge Computing"]),
    "build vs buy": (Category.TRADEOFFS, ["Build vs Buy", "Buy vs Build"]),
    # Java
    "virtual threads": (Category.JAVA, ["Virtual Threads", "Project Loom"]),
    "record patterns": (Category.JAVA, ["Record Patterns", "Pattern Switch"]),
    "pattern matching": (Category.JAVA, ["Pattern Matching", "Instanceof"]),
    "structured concurrency": (Category.JAVA, ["Structured Concurrency"]),
    "stamped lock": (Category.JAVA, ["StampedLock", "Stamped Lock"]),
    "lock free": (Category.JAVA, ["Lock Free", "Lock-free"]),
    "disruptor": (Category.JAVA, ["Disruptor", "Disruptor Pattern"]),
    "actor model": (Category.JAVA, ["Actor", "Actor Model"]),
}


class ResponseCache:
    """Simple file-based cache for HTTP responses."""

    def __init__(self, cache_dir: str, ttl_hours: int) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_hours * 3600
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[str]:
        key = self._key(url)
        cache_file = self.cache_dir / f"{key}.html"
        meta_file = self.cache_dir / f"{key}.meta"

        if not cache_file.exists() or not meta_file.exists():
            return None

        try:
            meta = json.loads(meta_file.read_text())
            age = time.time() - meta.get("timestamp", 0)
            if age > self.ttl_seconds:
                cache_file.unlink(missing_ok=True)
                meta_file.unlink(missing_ok=True)
                return None
            return cache_file.read_text()
        except Exception:
            return None

    def put(self, url: str, content: str) -> None:
        key = self._key(url)
        cache_file = self.cache_dir / f"{key}.html"
        meta_file = self.cache_dir / f"{key}.meta"

        try:
            cache_file.write_text(content)
            meta_file.write_text(json.dumps({"timestamp": time.time(), "url": url}))
        except Exception as exc:
            logger.warning("Failed to cache %s: %s", url, exc)

    def cleanup(self) -> int:
        """Remove expired cache entries. Returns count of removed files."""
        removed = 0
        for meta_file in self.cache_dir.glob("*.meta"):
            try:
                meta = json.loads(meta_file.read_text())
                age = time.time() - meta.get("timestamp", 0)
                if age > self.ttl_seconds:
                    meta_file.unlink()
                    (self.cache_dir / (meta_file.stem + ".html")).unlink(missing_ok=True)
                    removed += 1
            except Exception:
                pass
        return removed


class TrendScraper:
    """Scrape trending system design problems from multiple sources."""

    def __init__(self) -> None:
        self.delay = settings.SCRAPER_REQUEST_DELAY
        self.timeout = settings.SCRAPER_TIMEOUT
        self.user_agent = settings.SCRAPER_USER_AGENT
        self.enabled_sources = settings.SCRAPER_SOURCES
        self.max_retries = settings.SCRAPER_MAX_RETRIES
        self.retry_backoff = settings.SCRAPER_RETRY_BACKOFF
        self.cache = ResponseCache(settings.CACHE_DIR, settings.CACHE_TTL_HOURS)

    # ------------------------------------------------------------------ #
    #  Main entry point
    # ------------------------------------------------------------------ #
    async def scrape_all(self) -> list:
        """Scrape all enabled sources and return unique problems."""
        # Cleanup expired cache entries
        cleaned = self.cache.cleanup()
        if cleaned > 0:
            logger.info("Cleaned %d expired cache entries", cleaned)

        all_problems: dict = {}
        tasks = []

        for source_name in self.enabled_sources:
            if source_name not in SOURCES:
                logger.warning("Unknown source: %s", source_name)
                continue
            tasks.append(self._scrape_source(source_name))

        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Scraper task failed: %s", result)
                continue
            for prob in result:
                key = (prob.category.value, prob.slug)
                if key not in all_problems:
                    all_problems[key] = prob
                else:
                    all_problems[key].source_count += 1
                    all_problems[key].source += f", {prob.source}"

        # Sort by source count (problems appearing in more sources are more important)
        sorted_problems = sorted(
            all_problems.values(),
            key=lambda p: p.source_count,
            reverse=True,
        )

        logger.info("Found %d unique trending problems across all sources", len(sorted_problems))
        return sorted_problems

    # ------------------------------------------------------------------ #
    #  Source scrapers
    # ------------------------------------------------------------------ #
    async def _scrape_source(self, source_name: str) -> list:
        """Dispatch to the appropriate scraper for a source."""
        source_info = SOURCES[source_name]
        all_problems = []

        for url in source_info.get("urls", []):
            try:
                html_text = await self._fetch_html_with_retry(url)
                if not html_text:
                    continue

                if source_info["type"] == "github":
                    problems = self._parse_github_trending(html_text, source_name)
                else:
                    problems = self._parse_html_generic(html_text, source_name)

                all_problems.extend(problems)
                logger.info("Source %s (%s): found %d problems", source_name, url, len(problems))
            except Exception as exc:
                logger.error("Failed to scrape %s (%s): %s", source_name, url, exc)

        return all_problems

    # ------------------------------------------------------------------ #
    #  HTTP fetching with retry
    # ------------------------------------------------------------------ #
    async def _fetch_html_with_retry(self, url: str) -> Optional[str]:
        """Fetch HTML with exponential backoff retry."""
        # Check cache first
        cached = self.cache.get(url)
        if cached:
            logger.info("Cache hit for %s", url)
            return cached

        headers = {"User-Agent": self.user_agent}
        last_error = None

        for attempt in range(self.max_retries):
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                try:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    content = response.text

                    # Cache the response
                    self.cache.put(url, content)
                    await asyncio.sleep(self.delay)
                    return content
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code >= 500:
                        last_error = exc
                        wait_time = self.retry_backoff ** (attempt + 1)
                        logger.warning(
                            "Server error on attempt %d/%d for %s: %s. Retrying in %.1fs...",
                            attempt + 1, self.max_retries, url, exc, wait_time,
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("Client error for %s: %s", url, exc)
                        return None
                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    last_error = exc
                    wait_time = self.retry_backoff ** (attempt + 1)
                    logger.warning(
                        "Connection error on attempt %d/%d for %s: %s. Retrying in %.1fs...",
                        attempt + 1, self.max_retries, url, exc, wait_time,
                    )
                    await asyncio.sleep(wait_time)

        logger.error("All %d retries exhausted for %s: %s", self.max_retries, url, last_error)
        return None

    # ------------------------------------------------------------------ #
    #  Generic HTML parser (replaces all individual parsers)
    # ------------------------------------------------------------------ #
    def _parse_html_generic(self, html_text: str, source: str) -> list:
        """Parse HTML using keyword matching against the comprehensive problem database."""
        problems = []
        html_lower = html_text.lower()
        seen_names: set = set()

        for keyword, (category, aliases) in PROBLEM_KEYWORDS.items():
            # Check if any alias appears in the HTML
            matched = False
            for alias in aliases:
                if alias.lower() in html_lower:
                    matched = True
                    break

            if matched:
                # Use the first alias as the canonical name
                name = aliases[0]
                if name not in seen_names:
                    seen_names.add(name)
                    problems.append(TrendingProblem(
                        name=name,
                        category=category,
                        source=source,
                        url=SOURCES[source]["urls"][0] if isinstance(SOURCES[source]["urls"], list) else SOURCES[source]["urls"],
                    ))

        # Also extract "Design X" patterns for new HLD problems
        for match in re.finditer(
            r"(?:design|build|implement)\s+([A-Z][A-Za-z\s]{3,40}(?:system|service|platform|engine))",
            html_text,
            re.IGNORECASE,
        ):
            name = match.group(1).strip()
            # Clean up common suffixes
            name = re.sub(r"\s+(system|service|platform|engine)\s*$", "", name, flags=re.IGNORECASE).strip()
            if name and len(name) > 3 and name not in seen_names:
                seen_names.add(name)
                problems.append(TrendingProblem(
                    name=name,
                    category=Category.HLD,
                    source=source,
                    url=SOURCES[source]["urls"][0] if isinstance(SOURCES[source]["urls"], list) else SOURCES[source]["urls"],
                ))

        return problems

    def _parse_github_trending(self, html_text: str, source: str) -> list:
        """Parse GitHub trending page for system design repos."""
        problems = []
        seen_names: set = set()

        # Extract repo descriptions that mention system design
        sd_keywords = [
            "system-design", "system design", "distributed-systems",
            "low-level-design", "lld", "hld", "architecture",
        ]

        # Find repo names and descriptions
        for match in re.finditer(r'/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', html_text):
            repo = match.group(1).lower()
            is_sd = any(kw in repo for kw in sd_keywords)
            if is_sd and repo not in seen_names:
                seen_names.add(repo)
                # Extract problem name from repo name
                name = repo.replace("-", " ").title()
                problems.append(TrendingProblem(
                    name=name,
                    category=Category.HLD,
                    source=source,
                    url=f"https://github.com/{repo}",
                ))

        return problems
