"""Tests for the problem generator."""

import os
import tempfile
from pathlib import Path

import pytest
from agent.core.models import Category, TrendingProblem, ExistingProblem
from agent.generator.generator import ProblemGenerator


class TestProblemGenerator:
    def test_list_existing_problems(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a problem directory
            prob_dir = Path(tmpdir) / "hld" / "problems" / "twitter"
            prob_dir.mkdir(parents=True)
            (prob_dir / "README.md").write_text("# Twitter")

            # Save and restore REPO_PATH
            original = os.environ.get("REPO_PATH")
            try:
                os.environ["REPO_PATH"] = tmpdir
                # Force re-read of config by creating a new generator
                from agent.generator import generator as gen_mod
                gen_mod.settings.REPO_PATH = tmpdir
                gen = ProblemGenerator()
                gen.repo_path = Path(tmpdir)
                problems = gen.list_existing_problems()
                assert len(problems) == 1
                assert problems[0].name == "Twitter"
                assert problems[0].category == Category.HLD
            finally:
                if original:
                    os.environ["REPO_PATH"] = original
                else:
                    os.environ.pop("REPO_PATH", None)

    def test_filter_missing_exact_match(self):
        os.environ["REPO_PATH"] = "/tmp/nonexistent"
        gen = ProblemGenerator()
        trending = [TrendingProblem(name="Twitter", category=Category.HLD, source="test", url="http://test")]
        existing = [ExistingProblem(name="Twitter", category=Category.HLD, path="/hld/twitter", slug="twitter")]
        missing = gen.filter_missing(trending, existing, set())
        assert len(missing) == 0

    def test_filter_missing_no_match(self):
        os.environ["REPO_PATH"] = "/tmp/nonexistent"
        gen = ProblemGenerator()
        trending = [TrendingProblem(name="TikTok", category=Category.HLD, source="test", url="http://test")]
        existing = [ExistingProblem(name="Twitter", category=Category.HLD, path="/hld/twitter", slug="twitter")]
        missing = gen.filter_missing(trending, existing, set())
        assert len(missing) == 1

    def test_filter_missing_history_skip(self):
        os.environ["REPO_PATH"] = "/tmp/nonexistent"
        gen = ProblemGenerator()
        trending = [TrendingProblem(name="TikTok", category=Category.HLD, source="test", url="http://test")]
        existing = []
        history = {"tiktok"}
        missing = gen.filter_missing(trending, existing, history)
        assert len(missing) == 0

    def test_generate_hld(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="Test Service", category=Category.HLD, source="test", url="http://test")
            content = gen._generate_hld(prob)
            assert "# Test Service" in content
            assert "## Problem Statement" in content
            assert "## Staff-Level Design Considerations" in content

    def test_generate_lld(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="Parking Lot", category=Category.LLD, source="test", url="http://test")
            content = gen._generate_lld(prob)
            assert "# Parking Lot" in content
            assert "## Class Diagram" in content

    def test_generate_ds(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="Distributed Cache", category=Category.DISTRIBUTED_SYSTEMS, source="test", url="http://test")
            content = gen._generate_ds(prob)
            assert "# Distributed Cache" in content

    def test_generate_tradeoff(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="SQL vs NoSQL", category=Category.TRADEOFFS, source="test", url="http://test")
            content = gen._generate_tradeoff(prob)
            assert "# SQL vs NoSQL" in content
            assert "## When to Use SQL" in content
            assert "## When to Use NoSQL" in content

    def test_generate_java(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="Virtual Threads", category=Category.JAVA, source="test", url="http://test")
            content = gen._generate_java(prob)
            assert "# Virtual Threads" in content

    def test_generate_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="Test Service", category=Category.HLD, source="test", url="http://test")
            result = gen._generate_one(prob)
            assert result is not None
            assert result.path == "hld/problems/test-service/README.md"
            assert Path(tmpdir) / "hld" / "problems" / "test-service" / "README.md"

    def test_template_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["REPO_PATH"] = tmpdir
            gen = ProblemGenerator()
            prob = TrendingProblem(name="RAG System", category=Category.HLD, source="test", url="http://test")
            content = gen._generate_hld(prob)
            # RAG template has specific concepts
            assert "Vector embeddings" in content or "Semantic search" in content
