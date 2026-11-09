# Twitter / Social Media Feed

## Problem Statement

Design a microblogging platform like Twitter that supports tweet creation, timelines, retweets, likes, followers, trending topics, and real-time updates.

**Reference**: Educative.io, ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Tweets**: Create, edit, delete tweets (280 char limit); attach media.
- **Timelines**: Home timeline (followers' tweets), user timeline, and list timelines.
- **Retweets/Likes**: Retweet with or without comment; like/unlike tweets.
- **Followers**: Follow/unfollow users; mute and block.
- **Trending**: Real-time trending topics by hashtag and geography.
- **Search**: Full-text search across tweets; filter by date, user, engagement.
- **Notifications**: Real-time notifications for mentions, retweets, likes, new followers.

### Non-Functional Requirements
- **Scale**: 500M+ users; 500M+ tweets/day; 100M+ active daily users.
- **Latency**: Timeline load < 200ms; tweet creation < 500ms.
- **Availability**: 99.99% uptime; write-available even during partial outages.

## Key Design Decisions
- **Fan-out on write**: Push tweets to followers' timelines on write. Hybrid pull for celebrities.
- **Write-heavy optimization**: Append-only tweet storage; partitioned by user ID.
- **Trending computation**: Stream processing (Kafka + Flink) for real-time hashtag aggregation.
- **Caching**: Redis cache for hot timelines; CDN for media.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                              → Tweet Service (write)
                              → Timeline Service (read)
                              → Notification Service
                              → Search Service (Elasticsearch)
                              
Tweet Service → Kafka → Timeline Fan-out → Redis (user timelines)
                    → Media Service → S3/CDN
                    → Notification Service
```

## Staff-Level Design Considerations

### Fan-out Strategy
- **Push for normal users**: When a user with < 10K followers tweets, fan out to all followers' timelines.
- **Pull for celebrities**: When a user with > 10K followers tweets, don't fan out. Pull their tweets at timeline read time.
- **Staff insight**: This hybrid approach is what Twitter actually uses. Pure fan-out breaks for celebrities (Kanye tweeting = 50M writes). Pure pull is too slow for normal users.

### Timeline Storage
- **Redis sorted set**: Each user's timeline is a sorted set scored by tweet timestamp. O(log n) insert, O(log n) range query.
- **Staff insight**: Store the last 1K tweets per timeline in Redis. For "load more," query the tweet store directly. This keeps memory bounded.

### Trending Topics
- **Stream processing**: Kafka stream of tweets → Flink job that counts hashtags per window → Redis for serving.
- **Staff insight**: Use a sliding window (e.g., 15 minutes) with 1-minute increments. This smooths out spikes and gives a more accurate trending picture.
