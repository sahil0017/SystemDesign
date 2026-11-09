# Instagram

## Problem Statement

Design a photo and video sharing platform like Instagram that supports uploading media, building feeds, following users, liking/commenting on posts, and real-time notifications at scale (500M+ active users).

## Requirements

### Functional Requirements
- **User Management**: Sign up, login, profile management, follow/unfollow
- **Media Upload**: Photo and video upload with filters, cropping, and compression
- **Feed Generation**: Chronological and algorithmic news feed with infinite scroll
- **Interactions**: Like, comment, share, save posts; story views
- **Notifications**: Real-time notifications for likes, comments, follows, mentions
- **Search**: User and hashtag search with autocomplete
- **Direct Messaging**: Private 1:1 and group messaging with media sharing
- **Stories**: Ephemeral content that disappears after 24 hours

### Non-Functional Requirements
- **Scale**: 500M+ daily active users; 350M+ posts/day
- **Latency**: Feed load < 200ms p99; media upload < 2s for 10MB photo
- **Availability**: 99.99% uptime for core services
- **Storage**: Petabytes of media storage with CDN distribution
- **Consistency**: Feed can be eventually consistent; likes/comments need strong consistency
- **Global**: Multi-region deployment with data residency compliance

## Key Design Decisions
- **Feed Strategy**: Fan-out-on-write (push) for influencers with many followers; pull for low-activity users; hybrid for most users
- **Media Storage**: Object storage (S3) + CDN (CloudFront) with multi-resolution thumbnails
- **Database**: PostgreSQL for user data; Cassandra/DynamoDB for feed; Redis for caching and counters
- **Real-time**: WebSocket for notifications and DMs; Kafka for event streaming
- **Algorithmic Feed**: ML-based ranking model using engagement signals (likes, comments, dwell time)
