"""Response cache — file-based HTTP response caching."""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("agent.scraper.cache")


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
