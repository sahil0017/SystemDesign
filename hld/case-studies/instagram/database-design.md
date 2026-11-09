# Instagram - Database Design

## Database Strategy

- **PostgreSQL**: User data, relationships, post metadata (ACID transactions)
- **Cassandra/DynamoDB**: Feed storage, comments, likes (high write throughput)
- **Redis**: Session data, hot feed cache, counters, rate limiting
- **Elasticsearch**: User and hashtag search
- **S3**: Media storage (photos, videos, thumbnails)

## PostgreSQL Schema

### Users
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    profile_picture_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### Follow Relationships
```sql
CREATE TABLE follows (
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
);

CREATE INDEX idx_follows_following ON follows(following_id); -- For "who follows me"
CREATE INDEX idx_follows_follower ON follows(follower_id);   -- For "who do I follow"
```

### Posts
```sql
CREATE TABLE posts (
    post_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    caption TEXT,
    media_url VARCHAR(500) NOT NULL,
    media_type VARCHAR(20) NOT NULL, -- 'photo', 'video', 'carousel'
    thumbnail_url VARCHAR(500),
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);
```

### Comments
```sql
CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_comment_id BIGINT, -- For replies
    text TEXT NOT NULL,
    like_count BIGINT DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
);

CREATE INDEX idx_comments_post ON comments(post_id, created_at DESC);
CREATE INDEX idx_comments_user ON comments(user_id);
```

### Likes
```sql
CREATE TABLE likes (
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);

CREATE INDEX idx_likes_post ON likes(post_id);
```

### Notifications
```sql
CREATE TABLE notifications (
    notification_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    actor_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'like', 'comment', 'follow', 'mention'
    post_id BIGINT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (actor_id) REFERENCES users(user_id)
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read, created_at DESC);
```

## Cassandra Schema (Feed & High-Write Data)

### Feed Table
```sql
CREATE TABLE user_feed (
    user_id BIGINT,
    created_at TIMESTAMP,
    post_id BIGINT,
    actor_id BIGINT,
    caption TEXT,
    media_url TEXT,
    like_count BIGINT,
    comment_count BIGINT,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

### Comments Table (High Write)
```sql
CREATE TABLE post_comments (
    post_id BIGINT,
    created_at TIMESTAMP,
    comment_id BIGINT,
    user_id BIGINT,
    text TEXT,
    like_count BIGINT,
    PRIMARY KEY (post_id, created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `session:{session_id}` | Hash | User session data | 24h |
| `feed:{user_id}` | Sorted Set | Cached feed (post_id, score=timestamp) | 5min |
| `post:{post_id}:likes` | Set | Like set for a post | No TTL |
| `post:{post_id}:like_count` | String | Like counter | No TTL |
| `user:{user_id}:followers` | Set | Follower count | No TTL |
| `rate:{ip}:{endpoint}` | String | Rate limit counter | 1min |
| `story:{user_id}` | Sorted Set | Active stories | 24h |
| `story:{story_id}:views` | Set | Story viewers | 24h |

## Indexes Strategy

### PostgreSQL Indexes
- **Covering indexes** for frequent queries: `(user_id, created_at DESC) INCLUDE (post_id, caption)`
- **Partial indexes** for active data: `WHERE is_deleted = FALSE`
- **Composite indexes** for common query patterns: `(post_id, created_at DESC)`

### Cassandra Partition Strategy
- **Partition key**: `user_id` for feed (all feed items for a user on same partition)
- **Clustering key**: `created_at DESC` for chronological ordering
- **Replication factor**: 3 for high availability

## Staff-Level Database Considerations

### Read/Write Splitting
- **Primary**: All writes; consistency-sensitive reads (user's own data)
- **Replicas**: Feed reads, post detail reads, user profile reads
- **Lag-aware routing**: Route post-write reads to primary for 30s

### Caching Strategy
- **Hot posts**: Cache in Redis with 5min TTL + event-driven invalidation
- **User profiles**: Cache with 1h TTL; invalidate on profile update
- **Counters**: Redis for real-time; async sync to PostgreSQL

### Data Archival
- **Old comments**: Archive comments > 1 year to cold storage
- **Deleted posts**: Soft delete with 30-day grace period, then hard delete
- **Stories**: Auto-delete after 24h using Redis TTL + cleanup worker
