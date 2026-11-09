# Web Crawler

## Problem Statement

Design a web crawler like Google's that discovers, downloads, and indexes web pages at scale, respecting robots.txt, managing politeness policies, and handling duplicate content.

**Reference**: Educative.io, ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **URL discovery**: Extract links from crawled pages; add to crawl queue.
- **Politeness**: Respect robots.txt; rate-limit per domain; avoid overloading servers.
- **Duplicate detection**: Skip already-crawled URLs; detect duplicate content.
- **Priority crawling**: Prioritize important pages (high PageRank, recently updated).
- **Storage**: Store page content, metadata, and extracted links.
- **Indexing**: Build inverted index for search.

### Non-Functional Requirements
- **Scale**: Billions of pages; petabytes of data; 10K+ crawler nodes.
- **Throughput**: 100M+ pages crawled per day.
- **Fault tolerance**: Continue crawling if individual nodes fail.

## Key Design Decisions
- **Distributed queue**: Sharded URL frontier with priority scheduling.
- **Bloom filter**: Fast duplicate URL detection across distributed nodes.
- **PageRank**: Prioritize high-importance pages for crawling.
- **Deduplication**: Content hash (MD5/SHA) to detect duplicate pages.

## Architecture Overview

```
URL Frontier (Priority Queue)
         │
         ▼
  ┌──────────────┐
  │  Crawler     │→ Download pages → Page Store (HDFS/S3)
  │  Nodes       │→ Extract links → URL Frontier (new URLs)
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │  Indexer     │→ Parse content → Inverted Index (Elasticsearch)
  └──────────────┘
```

## Staff-Level Design Considerations

### URL Frontier Design
- **Priority queue**: Score URLs by PageRank, freshness, and domain authority.
- **Staff insight**: Use a distributed priority queue (e.g., Redis ZSET or custom sharded heap). The frontier is the heart of the crawler — its design determines crawl quality.

### Duplicate Detection
- **Bloom filter**: Probabilistic data structure for URL deduplication. O(1) check, small false positive rate.
- **Staff insight**: A Bloom filter with 1% false positive rate for 1B URLs requires ~10GB of memory. This is much more efficient than a hash set (~50GB+).

### Politeness Policy
- **Per-domain rate limiting**: Token bucket per domain. Default: 1 request/second; respect robots.txt Crawl-delay.
- **Staff insight**: Without per-domain rate limiting, the crawler will DDoS small websites. This is both ethical and practical — blocked IPs hurt crawl coverage.
