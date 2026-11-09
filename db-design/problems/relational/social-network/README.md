# Social Network Database Schema Design

## Problem Statement

Design a comprehensive database schema for a social network platform (like Facebook/Instagram) that supports users, posts, comments, likes, followers, friend requests, groups, and notifications. The schema must handle fan-out for news feeds, graph queries for "friends of friends," and real-time notification delivery at scale.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Users**: Profile, avatar, bio, account settings.
- **Posts**: Text, images, videos, location, visibility (public/friends/private).
- **Comments & Replies**: Nested comment threads on posts.
- **Likes**: Like/unlike posts and comments.
- **Followers**: Follow/unfollow, follower/following counts.
- **Friend Requests**: Send, accept, reject, cancel requests.
- **Groups**: Create groups, join/leave, group posts, members, admins.
- **Notifications**: Post likes, comments, new followers, friend requests, mentions.

### Non-Functional Requirements
- **Read scalability**: Feed reads >> writes; support caching and denormalization.
- **Write scalability**: Handle 100K posts/second during peak events.
- **Graph queries**: "Friends of friends" and "mutual friends" queries in < 100ms.
- **Notification delivery**: Real-time notifications within 1 second.
- **Data retention**: Soft delete for posts; GDPR compliance for user data.

## Key Design Decisions

- **Denormalized counts**: Store follower_count, following_count, post_count instead of COUNT queries.
- **Fan-out on write**: When a user with < 10K followers posts, write to followers' feed tables immediately.
- **Fan-out on read**: When a user with >= 10K followers posts, aggregate feed at read time.
- **Soft deletes**: Use `is_deleted` flags for posts and comments.
- **Notification deduplication**: Unique constraint on (user_id, notification_type, reference_id).

## Schema Design

### Core Tables

```sql
-- Users
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,
    follower_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    post_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Posts
CREATE TABLE posts (
    post_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content TEXT,
    media_urls TEXT[],
    location VARCHAR(255),
    visibility VARCHAR(20) DEFAULT 'public', -- 'public', 'friends', 'private'
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Comments
CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_comment_id BIGINT,
    content TEXT NOT NULL,
    like_count INT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
);

-- Likes
CREATE TABLE likes (
    like_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    target_type VARCHAR(20) NOT NULL, -- 'post', 'comment'
    target_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, target_type, target_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Followers
CREATE TABLE followers (
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
);

-- Friend Requests
CREATE TABLE friend_requests (
    request_id BIGINT PRIMARY KEY,
    from_user_id BIGINT NOT NULL,
    to_user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'accepted', 'rejected', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (from_user_id, to_user_id),
    FOREIGN KEY (from_user_id) REFERENCES users(user_id),
    FOREIGN KEY (to_user_id) REFERENCES users(user_id)
);

-- Groups
CREATE TABLE groups (
    group_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    privacy VARCHAR(20) DEFAULT 'public', -- 'public', 'private', 'secret'
    member_count INT DEFAULT 0,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE group_members (
    group_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20) DEFAULT 'member', -- 'admin', 'member'
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Notifications
CREATE TABLE notifications (
    notification_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    actor_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'like', 'comment', 'follow', 'friend_request', 'mention'
    reference_id BIGINT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (actor_id) REFERENCES users(user_id)
);

-- News Feed (denormalized for fast reads)
CREATE TABLE news_feed (
    feed_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `posts` | `(user_id, created_at DESC)` | User's posts timeline |
| `posts` | `(visibility, created_at DESC)` | Public feed aggregation |
| `comments` | `(post_id, created_at DESC)` | Comments on a post |
| `comments` | `(parent_comment_id, created_at)` | Reply threads |
| `likes` | Unique `(user_id, target_type, target_id)` | Prevent duplicate likes |
| `followers` | `(following_id, created_at)` | Get followers of a user |
| `followers` | `(follower_id, created_at)` | Get who a user follows |
| `notifications` | `(user_id, is_read, created_at DESC)` | User's notification inbox |
| `news_feed` | `(user_id, created_at DESC)` | User's news feed |
| `groups` | `(created_by)` | User's created groups |

## Staff-Level Design Considerations

### Fan-Out Strategy
- **Hybrid approach**: Fan-out on write for users with < 10K followers; fan-out on read for celebrities.
- **Staff insight**: Pure fan-out on write causes thundering herd when celebrities post. Pure fan-out on read is slow for users with many followers. The hybrid threshold (10K) balances write amplification vs read latency.

### Denormalized Counts
- **Materialized counters**: `follower_count`, `following_count`, `like_count` updated on every follow/like.
- **Staff insight**: Never use `SELECT COUNT(*)` on production tables with millions of rows. Maintain counters via triggers or application logic. Accept eventual consistency — counters may be off by a few during high write throughput.

### Graph Queries
- **Mutual friends**: Self-join on `followers` table: `SELECT f1.following_id FROM followers f1 JOIN followers f2 WHERE f1.follower_id = :user1 AND f2.follower_id = :user2 AND f1.following_id = f2.following_id`.
- **Staff insight**: For deep graph traversal (degree of separation), use a graph database (Neo4j) or pre-compute closeness centrality. PostgreSQL is not optimized for multi-hop graph queries.

### Notification Deduplication
- **Unique constraint**: Prevent duplicate notifications for the same event.
- **Staff insight**: Batch notifications when an action triggers many (e.g., "50 people liked your post" instead of 50 separate notifications). Use a time window (5 min) to aggregate same-type notifications.

### Soft Deletes & GDPR
- **Soft delete**: `is_deleted = TRUE` keeps data for analytics and audit.
- **Staff insight**: GDPR "right to be forgotten" requires physical deletion. Implement a two-tier approach: soft delete for 30 days (recovery window), then physical deletion. Anonymize remaining data for analytics.
