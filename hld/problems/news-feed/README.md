# News Feed System (Facebook Newsfeed)

## Problem Statement

Design a news feed system like Facebook's that delivers personalized content from friends, pages, and groups in real-time with ranking and engagement features.

**Reference**: Educative.io, ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Feed generation**: Chronological and algorithmic feed from connections and followed pages.
- **Content types**: Text posts, photos, videos, links, stories, and ads.
- **Engagement**: Like, comment, share, and react to posts.
- **Ranking**: Personalized post ranking based on user behavior and relationship strength.
- **Infinite scroll**: Paginated feed with lazy loading.
- **Real-time updates**: New posts appear in feed without refresh.

### Non-Functional Requirements
- **Scale**: 2B+ users; 10B+ posts/day; 500M+ daily active users.
- **Latency**: First page of feed < 200ms; subsequent pages < 500ms.
- **Personalization**: Unique feed per user based on ML ranking.

## Key Design Decisions
- **Hybrid fan-out**: Push for active users with few connections; pull for inactive users and celebrities.
- **Pre-computation**: Background jobs pre-rank feeds for top N posts per user.
- **Caching**: Multi-level caching (Redis → CDN) for hot feeds.
- **ML ranking**: Real-time scoring model that ranks posts by predicted engagement.

## Architecture Overview

```
Client → CDN → Load Balancer → Feed API
                                    → Pre-computed Feed (Redis)
                                    → Real-time Ranking Service
                                    → Post Service
                                    → Engagement Service
                                    
Post Creation → Kafka → Fan-out Service → User Timelines (Redis)
                          → Ranking Service → Pre-computed Feeds
```

## Staff-Level Design Considerations

### Feed Generation Strategy
- **Write-heavy fan-out**: Push to followers' timelines at write time. Cache last 300 posts per user.
- **Staff insight**: Facebook uses a hybrid approach. For users with < 1K connections, fan-out on write. For influencers, pull at read time and merge. The threshold is tuned based on observed latency.

### Ranking Algorithm
- **Feature extraction**: 10,000+ features per post (recency, relationship, media type, past engagement).
- **Staff insight**: Pre-compute rankings in batches (every 5 minutes). At read time, re-rank the top 100 using real-time features. This balances freshness and latency.

### Cache Strategy
- **Multi-level**: L1 = in-memory cache per server; L2 = Redis cluster; L3 = database.
- **Staff insight**: Feed data is highly personalized — you can't use a simple URL cache. Cache at the user level with short TTLs (30-60 seconds) and invalidate on new posts from connections.
