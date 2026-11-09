"""Tests for data models."""

import pytest
from agent.core.models import (
    Category, TrendingProblem, ExistingProblem,
    GeneratedFile, RunHistory,
)


class TestTrendingProblem:
    def test_slug_generation(self):
        prob = TrendingProblem(name="URL Shortener", category=Category.HLD, source="test", url="http://test")
        assert prob.slug == "url-shortener"

    def test_slug_with_special_chars(self):
        prob = TrendingProblem(name="Chat System (Real-time)", category=Category.HLD, source="test", url="http://test")
        assert prob.slug == "chat-system-real-time"

    def test_slug_strips_dashes(self):
        prob = TrendingProblem(name="---Test---", category=Category.HLD, source="test", url="http://test")
        assert prob.slug == "test"

    def test_to_dict(self):
        prob = TrendingProblem(name="Twitter", category=Category.HLD, source="algomaster", url="http://test")
        d = prob.to_dict()
        assert d["name"] == "Twitter"
        assert d["slug"] == "twitter"
        assert d["category"] == "hld"
        assert d["source"] == "algomaster"


class TestRunHistory:
    def test_empty_history(self):
        h = RunHistory()
        assert len(h.added_slugs) == 0
        assert h.last_run == ""
        assert len(h.pr_urls) == 0

    def test_to_dict_and_from_dict(self):
        h = RunHistory(added_slugs={"twitter", "linkedin"}, last_run="2024-01-01", pr_urls=["url1"])
        d = h.to_dict()
        h2 = RunHistory.from_dict(d)
        assert h2.added_slugs == {"twitter", "linkedin"}
        assert h2.last_run == "2024-01-01"
        assert h2.pr_urls == ["url1"]

    def test_from_dict_empty(self):
        h = RunHistory.from_dict({})
        assert len(h.added_slugs) == 0


class TestCategory:
    def test_all_categories(self):
        assert Category.HLD.value == "hld"
        assert Category.LLD.value == "lld"
        assert Category.DISTRIBUTED_SYSTEMS.value == "distributed-systems"
        assert Category.TRADEOFFS.value == "tradeoffs"
        assert Category.JAVA.value == "java"


class TestExistingProblem:
    def test_creation(self):
        p = ExistingProblem(name="Twitter", category=Category.HLD, path="/hld/twitter", slug="twitter")
        assert p.name == "Twitter"
        assert p.category == Category.HLD


class TestGeneratedFile:
    def test_creation(self):
        f = GeneratedFile(path="hld/twitter/README.md", content="# Test", category=Category.HLD, problem_name="Twitter")
        assert f.path == "hld/twitter/README.md"
        assert f.category == Category.HLD
