# Search Autocomplete System

## Problem Statement

Design a search autocomplete system like Google's that provides real-time suggestions as users type, with support for trending queries, personalization, and fast response times.

**Reference**: ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Suggestions**: Return top N suggestions for a given prefix in real-time.
- **Ranking**: Rank suggestions by popularity, recency, and user history.
- **Trending**: Highlight trending queries in suggestions.
- **Personalization**: Boost suggestions based on user's search history and location.
- **Categorization**: Group suggestions by categories (news, shopping, maps).

### Non-Functional Requirements
- **Scale**: 1B+ users; 10B+ searches/day; 100M+ unique queries.
- **Latency**: < 200ms response time for any prefix.
- **Throughput**: 1M+ autocomplete requests per second.

## Key Design Decisions
- **Trie data structure**: Prefix tree for O(k) prefix lookup where k = query length.
- **Distributed trie**: Sharded by prefix; each shard serves a subset of prefixes.
- **Caching**: LRU cache for hot prefixes; CDN for static suggestions.
- **Count tracking**: Each trie node stores search count for ranking.

## Architecture Overview

```
Client → CDN → Load Balancer → Autocomplete API
                                        → Trie Service (distributed trie)
                                        → Personalization Service
                                        → Trending Service
                                        
Search Service → Kafka → Query Counter → Trie Update (async)
```

## Staff-Level Design Considerations

### Trie Design
- **Compressed trie**: Use a radix tree (compressed trie) to reduce memory. Common prefixes share nodes.
- **Staff insight**: A naive trie for 100M queries with average length 10 requires ~10B nodes. A radix tree reduces this by 5-10x by compressing single-child paths.

### Distributed Architecture
- **Sharding by prefix**: First 2 characters determine the shard. "ap" → shard 1, "be" → shard 2.
- **Staff insight**: 2-character prefixes give 676 shards (26×26), which is a good balance. Too few shards = hot partitions. Too many = management overhead.

### Ranking Strategy
- **Global + personal**: Merge global popularity (pre-computed) with personal history (real-time).
- **Staff insight**: Don't personalize in real-time for all users — it's too expensive. Pre-compute top 100 global suggestions per prefix. At query time, merge with the user's last 10 searches. This is O(1) personalization.
