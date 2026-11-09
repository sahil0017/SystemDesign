"""ML-based problem classifier.

Old approach: a hardcoded keyword dict decides category — misses anything
not explicitly listed ("e-mail service", "wallet app", "queueing system").

This module trains a small scikit-learn pipeline (TF-IDF character n-grams +
LogisticRegression) at agent startup on a corpus built from the keyword
database plus per-class seed phrases and light augmentation. It is fast
(< 1s train), dependency-light, and falls back to the keyword map when
sklearn isn't available or confidence is low.

Usage:
    clf = ProblemClassifier()
    clf.fit()                                  # trains in-memory
    clf.predict_category("Email Service")      # -> Category
    clf.predict_with_confidence("Banana brain interface")
"""

import logging
import re
from typing import Optional, Tuple

from agent.core.models import Category

logger = logging.getLogger("agent.ml_classifier")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# Seed phrases per category (used to bootstrap training data). These
# complement the keyword database with paraphrases and near-miss examples.
SEED_PHRASES = {
    Category.HLD: [
        "design url shortener", "paste bin service", "short link service",
        "video streaming platform", "movie streaming", "OTT platform",
        "social network feed", "microblogging service", "tweet timeline",
        "photo sharing app", "story feed", "ride hailing app", "cab dispatch",
        "food ordering platform", "grocery delivery", "hotel booking site",
        "airline reservation", "ticket booking", "chat messenger", "voice call app",
        "notification service", "push notification infra", "payment gateway",
        "billing system", "subscription billing", "digital wallet service",
        "e commerce backend", "shopping cart", "inventory system",
        "search autocomplete", "typeahead suggestions", "web crawler infra",
        "distributed file storage", "cloud drive", "object storage",
        "cdn edge cache", "content delivery", "dns resolution",
        "load balancer", "reverse proxy", "api gateway",
        "rate limiter service", "throttling service", "leaderboard",
        "ad click tracker", "campaign manager", "recommendation engine",
        "news feed ranking", "live comment streaming", "watch party",
        "pastebin", "bit ly", "tiny url", "meeting scheduler", "calendar invite",
        "poll voting system", "qa forum", "discussion board",
        "code review tool", "collaborative editor", "shared whiteboard",
        "game leaderboard", "lottery system", "voting machine",
        "stock trading platform", "crypto exchange", "mint nft",
        "i o t device telemetry", "sensor data ingest", "metrics platform",
        "log collector", "trace collector", "alerting pipeline",
        "feature flag service", "experiment platform", "ab testing infra",
        "ml model registry", "training pipeline", "inference serving",
        "vector embedding store", "semantic retrieval", "rag chatbot",
        "llm gateway", "prompt store", "token billing",
        "fraud scoring", "risk engine", "kyc verification",
        "delivery tracking", "shipment logistics", "warehouse robotics",
        "parking garage system", "ev charging network", "bike sharing",
        "electric scooter fleet", "drone delivery", "autonomous fleet",
    ],
    Category.LLD: [
        "parking lot design", "multi level parking", "vehicle parking",
        "lru eviction", "least recently used policy", "cache eviction policy",
        "tic tac toe board", "noughts crosses", "snake game logic",
        "board game engine", "dice game", "card game dealer",
        "vending machine controller", "snack dispenser", "coffee maker",
        "atm machine", "cash withdraw", "bank teller kiosk",
        "elevator bank", "lift controller", "floor scheduling",
        "hotel room booking", "reservation desk", "housekeeping roster",
        "library catalog", "book lending", "return desk",
        "restaurant order", "kitchen ticket", "bill splitting",
        "movie seat selection", "cinema screen", "theater seating",
        "expense manager", "group settle up", "iou tracker",
        "task planner", "todo service", "kanban board",
        "logging library", "log appender", "logger hierarchy",
        "pub sub broker", "observer notification", "event bus",
        "music player", "playlist manager", "audio streaming client",
        "file zipper", "compression util", "unix tar",
        "chess engine", "move validator", "checkmate detector",
        "traffic signal", "intersection control", "pedestrian crossing",
        "online auction", "proxy bidder", "bid sniping",
        "car rental desk", "vehicle fleet", "cab booking app",
        "bike rental system", "scooter rental", "bicycle share dock",
        "queueing system design", "waiting line management", "token counter queue",
        "course enrollment", "prerequisite chain", "class registration",
        "call center routing", "customer support queue", "agent dispatcher",
        "matchmaking lobby", "game room finder", "multiplayer pairing",
        "concurrent hash map", "striped lock map", "thread safe map",
        "blocking queue impl", "bounded buffer", "producer consumer queue",
        "thread pool executor", "worker pool", "task runner",
        "bloom filter", "probabilistic set", "membership test",
        "countdown latch", "cyclic barrier", "phase synchronizer",
        "rate limiting middleware", "token bucket limiter", "sliding window counter",
        "read write lock", "reentrant mutex", "fairness policy",
        "printer spooler", "job scheduler daemon", "batch processor",
    ],
    Category.DISTRIBUTED_SYSTEMS: [
        "distributed lock manager", "mutual exclusion cluster", "lease service",
        "leader election", "raft consensus", "bully algorithm",
        "consistent hash ring", "virtual nodes", "hash partitioning",
        "replicated cache", "cluster cache", "memcached ring",
        "config center", "service registry", "feature toggle store",
        "session replication", "sticky session store", "single sign on",
        "vector database cluster", "ann index", "embedding shard",
        "feature store infra", "online features", "point in time join",
        "event store", "append only log", "event sourcing infra",
        "cqrs read model", "command handler", "projection builder",
        "circuit breaker middleware", "failure detector", "bulkhead isolation",
        "global rate limiter", "redis lua limiter", "quota service",
        "distributed trace", "span collector", "opentelemetry backend",
        "metrics tsdb", "time series store", "prometheus scale",
        "snowflake id", "sony flake", "uuid generator service",
        "inverted index cluster", "elastic search cluster", "search shard",
        "blob storage", "erasure coded store", "multipart upload",
        "secrets vault", "hsm service", "credential broker",
        "cron orchestrator", "workflow scheduler", "airflow like",
        "task queue cluster", "job runner fleet", "batch executor",
        "idempotency store", "dedupe cache", "exactly once ingest",
        "outbox relay", "cdc connector", "debezium pipeline",
        "saga orchestrator", "compensation manager", "tx coordinator",
        "gossip protocol", "member list", "heartbeat monitor",
        "quorum kv", "write ahead replicated store", "multi leader",
    ],
    Category.TRADEOFFS: [
        "sql versus nosql", "relational vs document", "postgres vs mongo",
        "monolith or microservices", "service oriented vs modular monolith",
        "rest versus graphql", "grpc vs rest api", "soap vs rest",
        "sync versus async processing", "blocking vs non blocking",
        "batch versus streaming", "lambda vs kappa architecture",
        "push vs pull model", "websocket vs polling", "sse vs websocket",
        "strong vs eventual consistency", "cap theorum choices",
        "sharding vs replication", "partition vs replica",
        "buy vs build platform", "vendor vs in house",
        "edge compute vs cloud", "cdn vs origin",
        "serverless vs containers", "vm vs kubernetes",
        "columnar vs row store", "olap vs oltp",
        "denormalization vs normalization", "read heavy vs write heavy",
        "eager versus lazy loading", "prefetch vs on demand",
        "compression tradeoff cpu", "gzip vs brotli",
        "graphql federation", "schema first vs code first",
    ],
    Category.JAVA: [
        "custom thread pool java", "executorservice internals",
        "producer consumer java", "wait notify pattern",
        "readwrite lock java", "stampedlock usage",
        "countdownlatch example", "cyclicbarrier reuse", "phaser advanced",
        "blocking queue implementation", "arrayblockingqueue vs linked",
        "semaphore permits", "binary semaphore",
        "ttl cache java", "expiring map", "caffeine cache internals",
        "rate limiter java", "guava ratelimiter", "resilience4j",
        "double checked locking", "singleton thread safety", "volatile keyword",
        "actor model java", "akka basics", "mailbox pattern",
        "disruptor ring buffer", "mechanical sympathy", "false sharing padding",
        "virtual threads loom", "structured concurrency java",
        "record patterns java", "sealed classes", "pattern matching switch",
        "string concat performance", "stringbuilder vs plus",
        "stream parallel pitfalls", "collectors grouping",
        "jvm gc tuning", "g1 heap settings", "zgc shenandoah",
        "jit warmup", "tiered compilation", "escape analysis",
        "jmh benchmark", "allocation profiling", "jfr flight recorder",
        "hashmap internals", "concurrent hashmap segments", "treeify bins",
        "arraylist vs linkedlist", "fail fast iterator",
        "completablefuture chaining", "thenapply vs thencompose",
        "fork join pool", "work stealing deque",
        "atomic reference cas", "longadder vs atomiclong",
    ],
}


class ProblemClassifier:
    """TF-IDF + LogisticRegression category classifier with keyword fallback."""

    def __init__(self, keyword_db: Optional[dict] = None):
        # keyword_db maps "problem keyword" -> (Category, [aliases...])
        self.keyword_db = keyword_db or {}
        self.pipeline = None
        self._trained = False

    # ------------------------------------------------------------------ #
    #  Training data construction
    # ------------------------------------------------------------------ #
    def _build_corpus(self) -> Tuple[list, list]:
        texts, labels = [], []

        # 1. Seed phrases (hand-curated paraphrases)
        for cat, phrases in SEED_PHRASES.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(cat.value)

        # 2. Keyword database entries: keyword itself + every alias
        for kw, (cat, aliases) in self.keyword_db.items():
            texts.append(kw.replace("-", " "))
            labels.append(cat.value)
            for alias in aliases:
                texts.append(alias.lower())
                labels.append(cat.value)

        # 3. Light augmentation: drop suffix words and swap word order so the
        #    model generalizes beyond the exact seeds.
        aug_texts, aug_labels = [], []
        for t, lab in zip(texts, labels):
            words = t.split()
            if len(words) > 2:
                aug_texts.append(" ".join(words[:-1]))
                aug_labels.append(lab)
                aug_texts.append(" ".join(reversed(words)))
                aug_labels.append(lab)
                aug_texts.append(f"design {t}")
                aug_labels.append(lab)
                aug_texts.append(f"build a {t}")
                aug_labels.append(lab)
        texts.extend(aug_texts)
        labels.extend(aug_labels)
        return texts, labels

    # ------------------------------------------------------------------ #
    #  Train / predict
    # ------------------------------------------------------------------ #
    def fit(self) -> bool:
        """Train in-memory. Returns True when the ML path is usable."""
        if not SKLEARN_AVAILABLE:
            logger.info("scikit-learn not installed; using keyword fallback")
            return False
        try:
            texts, labels = self._build_corpus()
            self.pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(
                    analyzer="char_wb", ngram_range=(2, 4), lowercase=True,
                    min_df=1, sublinear_tf=True,
                )),
                ("clf", LogisticRegression(max_iter=1000, C=4.0)),
            ])
            self.pipeline.fit(texts, labels)
            self._trained = True
            logger.info("ML classifier trained on %d samples (%d classes)",
                        len(texts), len(set(labels)))
            return True
        except Exception as exc:
            logger.warning("Classifier training failed: %s", exc)
            self._trained = False
            return False

    def predict_with_confidence(self, name: str) -> Tuple[Optional[Category], float]:
        """Return (category, confidence) or (None, 0.0) if unusable."""
        if not self._trained or self.pipeline is None:
            return None, 0.0
        try:
            proba = self.pipeline.predict_proba([name])[0]
            idx = int(np.argmax(proba))
            label = self.pipeline.classes_[idx]
            conf = float(proba[idx])
            return Category(label), conf
        except Exception as exc:
            logger.debug("Prediction failed for %r: %s", name, exc)
            return None, 0.0

    def predict_category(self, name: str, min_confidence: float = 0.45) -> Optional[Category]:
        """ML prediction with a floor; below the floor return None so callers
        can apply their own fallback (e.g. keyword db, default to HLD)."""
        cat, conf = self.predict_with_confidence(name)
        if cat and conf >= min_confidence:
            logger.debug("ML classified %r -> %s (%.2f)", name, cat.value, conf)
            return cat
        return None

    @property
    def is_trained(self) -> bool:
        return self._trained
