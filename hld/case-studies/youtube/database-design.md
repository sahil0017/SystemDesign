# YouTube - Database Design

## Database Strategy

- **PostgreSQL**: User data, channels, subscriptions (ACID transactions)
- **Cassandra**: Video metadata, comments, likes (high write throughput)
- **Redis**: Hot video cache, view counters, session data, trending
- **Elasticsearch**: Video search by title, description, tags
- **S3/GCS**: Raw and transcoded video storage

## PostgreSQL Schema

### Users & Channels
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    profile_picture_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE channels (
    channel_id BIGINT PRIMARY KEY,
    owner_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    profile_picture_url VARCHAR(500),
    banner_url VARCHAR(500),
    subscriber_count BIGINT DEFAULT 0,
    video_count BIGINT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE subscriptions (
    subscriber_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (subscriber_id, channel_id),
    FOREIGN KEY (subscriber_id) REFERENCES users(user_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

CREATE INDEX idx_subscriptions_channel ON subscriptions(channel_id);
```

## Cassandra Schema (Video Metadata & Comments)

### Videos
```sql
CREATE TABLE videos (
    video_id UUID PRIMARY KEY,
    channel_id BIGINT,
    title TEXT,
    description TEXT,
    thumbnail_url TEXT,
    duration INT,
    status TEXT, -- 'processing', 'ready', 'failed'
    view_count BIGINT,
    like_count BIGINT,
    dislike_count BIGINT,
    comment_count BIGINT,
    created_at TIMESTAMP,
    tags SET<TEXT>,
    categories SET<TEXT>
);

CREATE INDEX idx_videos_channel ON videos(channel_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at);
```

### Video Qualities
```sql
CREATE TABLE video_qualities (
    video_id UUID,
    resolution TEXT,
    bitrate INT,
    codec TEXT,
    hls_url TEXT,
    dash_url TEXT,
    file_size BIGINT,
    PRIMARY KEY (video_id, resolution)
);
```

### Comments
```sql
CREATE TABLE video_comments (
    video_id UUID,
    created_at TIMESTAMP,
    comment_id UUID,
    user_id BIGINT,
    parent_comment_id UUID,
    text TEXT,
    like_count BIGINT,
    PRIMARY KEY (video_id, created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

### Watch History
```sql
CREATE TABLE watch_history (
    user_id BIGINT,
    watched_at TIMESTAMP,
    video_id UUID,
    watch_duration INT,
    completion_pct DECIMAL(5,2),
    PRIMARY KEY (user_id, watched_at, video_id)
) WITH CLUSTERING ORDER BY (watched_at DESC);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `video:{video_id}` | Hash | Hot video metadata cache | 5min |
| `video:{video_id}:views` | String | View counter (async sync to DB) | No TTL |
| `video:{video_id}:likes` | Set | Like set for a video | No TTL |
| `trending:global` | Sorted Set | Trending videos (score=view_count) | 1h |
| `trending:{country}` | Sorted Set | Country-specific trending | 1h |
| `session:{user_id}` | Hash | Session data | 24h |
| `upload:{upload_id}` | Hash | Upload progress tracking | 1h |
| `rate:{user_id}:{endpoint}` | String | Rate limit counter | 1min |

## Elasticsearch Schema

### Video Index
```json
{
  "mappings": {
    "properties": {
      "video_id": { "type": "keyword" },
      "title": { "type": "text", "analyzer": "standard" },
      "description": { "type": "text", "analyzer": "standard" },
      "channel_name": { "type": "text" },
      "tags": { "type": "keyword" },
      "view_count": { "type": "long" },
      "created_at": { "type": "date" },
      "category": { "type": "keyword" }
    }
  }
}
```

## Indexes Strategy

### Cassandra Partition Strategy
- **Partition key**: `video_id` for video metadata (all qualities for a video)
- **Clustering key**: `resolution` for quality selection
- **Comments**: Partition by `video_id`, cluster by `created_at DESC`
- **Watch history**: Partition by `user_id`, cluster by `watched_at DESC`

### Elasticsearch
- **Full-text search**: Title and description with standard analyzer
- **Faceted search**: By category, upload date, view count
- **Autocomplete**: Edge n-gram analyzer for type-ahead suggestions

## Staff-Level Database Considerations

### View Count Management
- **Redis counter**: Increment on each view; async batch sync to Cassandra every 5min
- **Deduplication**: Track unique viewers per video in Redis Bloom filter
- **Staff insight**: Never write view count to DB on every view — use **async batch writes**

### Transcoding Status
- **Status tracking**: Store in Redis during processing; sync to Cassandra on completion
- **Webhook notification**: Notify creator when transcoding completes
- **Failure handling**: Retry transcoding up to 3 times; alert on persistent failure

### Storage Lifecycle
- **Raw video**: S3 Standard → S3 Glacier after 30 days
- **Transcoded segments**: S3 Standard with multi-region replication
- **Thumbnails**: CDN-cached with long TTL (1 year)
