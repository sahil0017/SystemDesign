# Designing a News Feed

## Overview

A news feed aggregates content from followed users, pages, and topics into a personalized timeline. Services like Facebook, Twitter, and Instagram serve billions of feed requests daily with sub-200ms latency.

## Feed Generation Strategies

### 1. Pull Model (Fan-in on Read)
```
User reads feed → Query posts from all followed users → Sort and return
```
- **Pros**: Always fresh content, simple to implement, low write cost
- **Cons**: Slow read for users with many follows, O(N) queries per request
- **Best for**: Users with few follows, low-activity platforms

### 2. Push Model (Fan-out on Write)
```
User writes post → Copy post to all followers' feeds → Serve from feed table
```
- **Pros**: Fast reads, pre-computed feed, easy pagination
- **Cons**: Expensive write for popular users, storage amplification
- **Best for**: High-activity platforms, users with many followers

### 3. Hybrid Model (Recommended)
```
Popular users → Push model (pre-compute feed)
Normal users → Pull model (compute on read)
```
- **Pros**: Balances read/write cost, handles viral content
- **Cons**: Complexity in determining threshold, consistency challenges
- **Best for**: Production systems like Facebook and Twitter

## Feed Ranking

### Scoring Algorithm
```
score = w1 * recency + w2 * relationship + w3 * engagement + w4 * content_type
```
- **Recency**: Newer posts ranked higher (exponential decay)
- **Relationship**: Posts from close friends ranked higher
- **Engagement**: Posts with more likes/comments ranked higher
- **Content type**: Video/images may be weighted differently

### Real-Time vs Batch Ranking
- **Real-time**: Score posts at write time for push model
- **Batch**: Re-score feed periodically for pull model with ML models
- **Hybrid**: Initial score at write, ML re-ranking asynchronously

## Media Processing

### Image Pipeline
```
Upload → Resize (thumbnails, medium, large) → Compress → CDN → Serve
```
- **Async processing**: Use message queue for image processing
- **Multiple sizes**: Generate thumbnails for feed, full size for detail view
- **CDN caching**: Cache processed images at edge for global delivery

## Staff-Level Insights

### Feed Cursor Pagination
- Use **cursor-based pagination** instead of offset for consistent results
- Cursor encodes timestamp and post ID for efficient DB queries
- Handle new posts appearing during pagination smoothly

### Handling Celebrity Posts
- Celebrities with millions of followers cause **fan-out storms**
- Use **async fan-out** with message queue to distribute write load
- Pre-compute feeds in batches during off-peak hours

### Feed Freshness vs Performance
- **Stale feed cache**: Cache feed for N seconds to reduce DB load
- **Real-time updates**: Use WebSocket to push new posts to active users
- **Pull refresh**: Allow clients to explicitly refresh for latest content
