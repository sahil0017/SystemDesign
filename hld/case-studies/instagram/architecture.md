# Instagram - Architecture

## System Components

1. **API Gateway**: Entry point for all client requests; authentication, rate limiting, request routing
2. **User Service**: User registration, authentication, profile management, follow relationships
3. **Media Service**: Photo/video upload, processing (resize, compress, filter), metadata extraction
4. **Feed Service**: Feed generation (push/pull/hybrid), feed caching, algorithmic ranking
5. **Interaction Service**: Likes, comments, shares, saves with real-time counters
6. **Notification Service**: Push notifications, in-app notifications, email/SMS
7. **Search Service**: User search, hashtag search, autocomplete with Elasticsearch
8. **Direct Message Service**: Real-time 1:1 and group messaging with WebSocket
9. **Story Service**: Ephemeral content with 24-hour TTL, view tracking
10. **Analytics Service**: Engagement metrics, A/B testing, usage analytics
11. **Object Storage (S3)**: Media storage with multi-resolution thumbnails
12. **CDN (CloudFront)**: Global media distribution with edge caching
13. **Database (PostgreSQL)**: User data, relationships, post metadata
14. **NoSQL (Cassandra/DynamoDB)**: Feed storage, comments, likes at scale
15. **Cache (Redis)**: Session data, hot feed cache, counters, rate limiting
16. **Message Queue (Kafka)**: Event streaming for fan-out, notifications, analytics

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    CDN (CloudFront)                  │
                    │         Static assets + Media thumbnails             │
                    └─────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │  User  │  │  Media   │  │   Feed   │  │Interact. │  │Notificat.│  │ Search │
   │Service │  │ Service  │  │ Service  │  │  Service │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Event streaming for fan-out, analytics       │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │ Cassandra│  │   Redis  │  │   S3     │  │ Elastic- │  │  DM    │
   │(Users,   │  │(Feed,    │  │(Cache,   │  │(Media)   │  │search    │  │Service │
   │ Relat.)  │  │ Comments)│  │ Counters)│  │          │  │(Search)  │  │(WS)    │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Media Upload Flow
- Client uploads photo/video → Media Service
- Media Service stores original in S3
- Async worker generates thumbnails (multiple resolutions)
- Thumbnails stored in S3 and pushed to CDN
- Post metadata saved to PostgreSQL
- **Fan-out**: Post IDs pushed to followers' feeds via Kafka
- Feed Service updates cached feeds in Redis/Cassandra

### 2. Feed Generation Flow
- **Push model (fan-out-on-write)**: When user posts, push post ID to all followers' feed queues
- **Pull model**: On feed request, fetch recent posts from followed users
- **Hybrid model**: Push for users with < 1K followers; pull for influencers with > 100K followers
- Feed Service merges push + pull results, applies ML ranking model
- Return paginated feed with media URLs from CDN

### 3. Like/Comment Flow
- Client sends like/comment → Interaction Service
- Write to Cassandra (high-write throughput)
- Increment counter in Redis (fast reads)
- Publish event to Kafka for notification and analytics
- Notification Service sends push notification to post owner

### 4. Notification Flow
- Kafka consumer processes interaction events
- Notification Service aggregates and deduplicates
- Push via Firebase/APNs for mobile; WebSocket for web
- Store notification history in database for sync

## Staff-Level Design Considerations

### Feed Strategy Trade-offs
- **Push**: Fast feed read; expensive write for influencers (1M+ followers)
- **Pull**: Fast write; expensive feed read for users who follow many active users
- **Hybrid**: Optimal — push for normal users, pull for influencers, merge at read time

### Media Processing Pipeline
- Use **async workers** for thumbnail generation to avoid blocking upload
- Generate **multiple resolutions** (150px, 640px, 1080px) for different devices
- Use **WebP/AVIF** format for 30-50% smaller file sizes
- Implement **progressive loading** — show low-res placeholder while high-res loads

### Consistency Model
- **Feed**: Eventual consistency acceptable (seconds of delay OK)
- **Likes/Comments**: Strong consistency for user's own actions (read-your-writes)
- **Counters**: Eventually consistent; use Redis for fast reads, async sync to DB
