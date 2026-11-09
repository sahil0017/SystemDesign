"""Tests for fuzzy matching utilities."""

import pytest
from agent.generator.fuzzy import levenshtein_distance, similarity_ratio, normalize_name


class TestLevenshteinDistance:
    def test_identical_strings(self):
        assert levenshtein_distance("abc", "abc") == 0

    def test_empty_strings(self):
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("", "abc") == 3

    def test_single_edit(self):
        assert levenshtein_distance("cat", "bat") == 1
        assert levenshtein_distance("cat", "cats") == 1
        assert levenshtein_distance("cat", "at") == 1

    def test_completely_different(self):
        assert levenshtein_distance("abc", "xyz") == 3

    def test_case_sensitive(self):
        assert levenshtein_distance("ABC", "abc") > 0


class TestSimilarityRatio:
    def test_identical(self):
        assert similarity_ratio("abc", "abc") == 1.0

    def test_empty(self):
        assert similarity_ratio("", "abc") == 0.0
        assert similarity_ratio("", "") == 0.0

    def test_similar_names(self):
        # "url-shortener" vs "url-shorter" should be very similar
        ratio = similarity_ratio("url-shortener", "url-shorter")
        assert ratio > 0.8

    def test_different_names(self):
        ratio = similarity_ratio("twitter", "linkedin")
        assert ratio < 0.5

    def test_case_insensitive(self):
        ratio = similarity_ratio("Twitter", "twitter")
        assert ratio == 1.0


class TestNormalizeName:
    def test_basic_normalization(self):
        assert normalize_name("URL Shortener") == "url-shortener"
        assert normalize_name("Chat System") == "chat-system"

    def test_remove_prefixes(self):
        assert normalize_name("Design Twitter") == "twitter"
        assert normalize_name("Build Netflix") == "netflix"
        assert normalize_name("Implement Uber") == "uber"

    def test_replace_separators(self):
        assert normalize_name("Chat System") == "chat-system"
        assert normalize_name("Chat_System") == "chat-system"
        assert normalize_name("chat-system") == "chat-system"

    def test_strip_dashes(self):
        assert normalize_name("---test---") == "test"

    def test_whitespace(self):
        assert normalize_name("  URL Shortener  ") == "url-shortener"
