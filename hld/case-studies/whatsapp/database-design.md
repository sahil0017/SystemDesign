# WhatsApp - Database Design

## Database Strategy

- **PostgreSQL**: User data, groups, contacts (ACID transactions)
- **Cassandra**: Message storage (high write throughput, partition tolerance)
- **Redis**: Presence, session data, offline message queues, rate limiting
- **S3**: Media storage (photos, videos, audio, documents)

## PostgreSQL Schema

### Users
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    profile_picture_url VARCHAR(500),
    about TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

CREATE INDEX idx_users_phone ON users(phone_number);
```

### Groups
```sql
CREATE TABLE groups (
    group_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon_url VARCHAR(500),
    creator_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

CREATE TABLE group_members (
    group_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_group_members_user ON group_members(user_id);
```

### Contacts
```sql
CREATE TABLE contacts (
    user_id BIGINT NOT NULL,
    contact_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, contact_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (contact_id) REFERENCES users(user_id)
);
```

## Cassandra Schema (Messages)

### Messages Table
```sql
CREATE TABLE messages (
    chat_id BIGINT,           -- user_id for 1:1, group_id for groups
    timestamp TIMESTAMP,
    msg_id UUID,
    sender_id BIGINT,
    recipient_id BIGINT,      -- NULL for groups
    msg_type TEXT,            -- 'text', 'image', 'video', 'audio'
    content BLOB,             -- Encrypted content
    media_url TEXT,           -- S3 URL for media messages
    status TEXT,              -- 'sent', 'delivered', 'read'
    PRIMARY KEY (chat_id, timestamp, msg_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
   AND default_time_to_live = 2592000;  -- 30 days TTL
```

### Message Index for Recipient
```sql
CREATE TABLE recipient_messages (
    recipient_id BIGINT,
    timestamp TIMESTAMP,
    msg_id UUID,
    sender_id BIGINT,
    chat_id BIGINT,
    content BLOB,
    status TEXT,
    PRIMARY KEY (recipient_id, timestamp, msg_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
   AND default_time_to_live = 2592000;
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `presence:{user_id}` | String | Online/offline status | 30s |
| `session:{user_id}` | Hash | Session data (device, JWT) | 24h |
| `queue:{user_id}` | List | Offline message queue | 30 days |
| `prekey:{user_id}` | Hash | Signal Protocol pre-keys | No TTL |
| `rate:{phone}:{endpoint}` | String | Rate limit counter | 1min |
| `status:{user_id}` | Sorted Set | Active status updates | 24h |
| `status:{status_id}:views` | Set | Status viewers | 24h |

## Indexes Strategy

### PostgreSQL Indexes
- **Phone lookup**: `idx_users_phone` for authentication
- **Group membership**: `idx_group_members_user` for "user's groups" query
- **Contact discovery**: Composite index on `(user_id, contact_id)`

### Cassandra Partition Strategy
- **Partition key**: `chat_id` for messages (all messages in a chat on same partition)
- **Clustering key**: `timestamp DESC` for chronological ordering
- **TTL**: 30 days auto-expiration for message cleanup
- **Replication factor**: 3 for high availability

## Staff-Level Database Considerations

### Message Storage Strategy
- **30-day retention**: Messages auto-expire after 30 days using Cassandra TTL
- **Dual write**: Write to both `messages` and `recipient_messages` for efficient queries
- **Compression**: Use Snappy compression for encrypted message content

### Presence Management
- **Redis TTL**: 30-second TTL on presence keys; expired = offline
- **Pub/Sub**: Redis pub/sub for real-time presence broadcast to contacts
- **Last seen**: Persist last_seen in PostgreSQL for offline users

### Offline Message Queue
- **Redis List**: LPUSH on send; RPOP on recipient connect
- **Persistence**: Messages also stored in Cassandra for durability
- **Cleanup**: Remove from Redis after successful delivery acknowledgment
