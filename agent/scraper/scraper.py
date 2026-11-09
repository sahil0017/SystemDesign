"""Web scraper for trending system design problems.

Scrapes multiple sources to discover new problem sets that should be added to the repo.
Features:
- HTML response caching to avoid redundant fetches
- Exponential backoff retry logic
- Real HTML parsing with regex-based extraction
- Multiple sources including GitHub trending repos
- Rate limiting between requests
"""

import asyncio
import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from agent.core.config import settings
from agent.core.models import Category, TrendingProblem
from agent.scraper.cache import ResponseCache
from agent.scraper.sources import SOURCES, PROBLEM_KEYWORDS

logger = logging.getLogger("agent.scraper")


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
