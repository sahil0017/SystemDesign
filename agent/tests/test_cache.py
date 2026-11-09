"""Tests for the response cache."""

import os
import tempfile
import time

import pytest
from agent.scraper.cache import ResponseCache


class TestResponseCache:
    def test_put_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(tmpdir, ttl_hours=1)
            cache.put("http://example.com", "<html>test</html>")
            result = cache.get("http://example.com")
            assert result == "<html>test</html>"

    def test_get_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(tmpdir, ttl_hours=1)
            result = cache.get("http://nonexistent.com")
            assert result is None

    def test_ttl_expiration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # TTL of 0 hours = immediate expiration
            cache = ResponseCache(tmpdir, ttl_hours=0)
            cache.put("http://example.com", "<html>test</html>")
            # Should expire immediately
            result = cache.get("http://example.com")
            assert result is None

    def test_cleanup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(tmpdir, ttl_hours=0)
            cache.put("http://a.com", "<html>a</html>")
            cache.put("http://b.com", "<html>b</html>")
            removed = cache.cleanup()
            assert removed == 2

    def test_different_urls_different_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResponseCache(tmpdir, ttl_hours=1)
            cache.put("http://a.com", "<html>a</html>")
            cache.put("http://b.com", "<html>b</html>")
            assert cache.get("http://a.com") == "<html>a</html>"
            assert cache.get("http://b.com") == "<html>b</html>"
