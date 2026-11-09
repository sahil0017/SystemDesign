# Real-Time Chat Database Schema Design

## Problem Statement

Design a NoSQL schema for a real-time chat application (like WhatsApp/Slack) with users, conversations (1:1 and group), messages, read receipts, and typing indicators. Support message ordering, delivery status, offline message sync, and efficient pagination for message history.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Users**: Profile, status, avatar, last seen.
- **Conversations**: 1:1 chats and group chats with members, admin, settings.
- **Messages**: Text, media, reactions, edits, deletions.
- **Delivery Status**: Sent → delivered → read per recipient.
- **Read Receipts**: Per-user read cursor in each conversation.
- **Typing Indicators**: Real-time typing status per user per conversation.
- **Offline Sync**: Fetch messages since last seen cursor.
- **Search**: Full-text search within a conversation.

### Non-Functional Requirements
- **Write throughput**: 100K messages/second globally.
- **Read latency**: Message history load in < 100ms.
- **Message ordering**: Strict ordering within a conversation.
- **Scalability**: 100M+ users, 1B+ conversations.
- **GDPR**: Message deletion on user request.

## Key Design Decisions

- **Partition by conversation_id**: All messages for a conversation in one partition.
- **Clustering by timestamp + message_id**: Ensures strict ordering and deduplication.
- **Read receipts as per-user cursor**: Store last read message_id per user per conversation.
- **Soft delete for messages**: Mark as deleted; physically remove after retention period.
- **Typing indicators in Redis**: TTL-based ephemeral data.

## Schema Design (Cassandra)

### Users

```cql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    avatar_url TEXT,
    status_text TEXT,
    is_online BOOLEAN,
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP
);
```

### Conversations

```cql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    type TEXT, -- 'direct', 'group'
    name TEXT, -- Group name
    avatar_url TEXT,
    created_by TEXT,
    created_at TIMESTAMP,
    settings MAP<TEXT, TEXT> -- {"mute": "true", "announcement_only": "false"}
);
```

### Conversation Members

```cql
CREATE TABLE conversation_members (
    conversation_id TEXT,
    user_id TEXT,
    role TEXT, -- 'admin', 'member'
    joined_at TIMESTAMP,
    last_read_message_id TEXT,
    last_read_at TIMESTAMP,
    is_muted BOOLEAN,
    PRIMARY KEY (conversation_id, user_id)
);

-- Reverse index: user's conversations
CREATE TABLE user_conversations (
    user_id TEXT,
    conversation_id TEXT,
    conversation_type TEXT,
    conversation_name TEXT,
    last_message_at TIMESTAMP,
    unread_count INT,
    PRIMARY KEY (user_id, conversation_id)
);
```

### Messages

```cql
CREATE TABLE messages (
    conversation_id TEXT,
    timestamp TIMESTAMP,
    message_id TEXT,
    sender_id TEXT,
    content TEXT,
    message_type TEXT, -- 'text', 'image', 'video', 'file', 'system'
    media_urls LIST<TEXT>,
    reactions MAP<TEXT, SET<TEXT>>, -- {"👍": ["user1", "user2"]}
    edited_at TIMESTAMP,
    is_deleted BOOLEAN,
    PRIMARY KEY ((conversation_id), timestamp, message_id)
) WITH CLUSTERING ORDER BY (timestamp ASC, message_id ASC);
```

### Message Delivery Status

```cql
CREATE TABLE message_delivery (
    conversation_id TEXT,
    message_id TEXT,
    recipient_id TEXT,
    status TEXT, -- 'sent', 'delivered', 'read'
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    PRIMARY KEY ((conversation_id, message_id), recipient_id)
);
```

### Unread Count per User (denormalized)

```cql
CREATE TABLE user_unread_counts (
    user_id TEXT,
    conversation_id TEXT,
    unread_count COUNTER,
    PRIMARY KEY (user_id, conversation_id)
);
```

### Message Search Index

```cql
CREATE TABLE message_search_index (
    conversation_id TEXT,
    search_vector TEXT, -- tsvector or inverted index
    message_id TEXT,
    sender_id TEXT,
    snippet TEXT,
    timestamp TIMESTAMP,
    PRIMARY KEY ((conversation_id), search_vector, message_id)
);
```

### Redis Data Structures (Ephemeral)

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `typing:{conversation_id}:{user_id}` | String | User is typing | 10s |
| `user:online:{user_id}` | String | Online status | 30s |
| `conversation:unread:{user_id}:{conv_id}` | String | Real-time unread count | No TTL |
| `message:cursor:{user_id}:{conv_id}` | String | Last synced message ID | 30 days |

## Indexes Strategy

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `messages` | `conversation_id, (timestamp, message_id)` | Message history ordered by time |
| `conversation_members` | `(conversation_id, user_id)` | Get members of a group |
| `user_conversations` | `(user_id, conversation_id)` | User's conversation list |
| `message_delivery` | `(conversation_id, message_id), recipient_id` | Delivery status per recipient |
| `user_unread_counts` | `(user_id, conversation_id)` | Unread counter per conversation |
| `message_search_index` | `conversation_id, search_vector, message_id` | Full-text search within conversation |

## Staff-Level Design Considerations

### Message Ordering
- **Timestamp + message_id**: Composite clustering key ensures strict ordering.
- **Staff insight**: Use a server-assigned timestamp, not client timestamp, to prevent clock skew issues. The `message_id` (UUID) as secondary clustering key handles concurrent messages with the same timestamp.

### Offline Sync Strategy
- **Cursor-based pagination**: Client sends `last_seen_message_id`; server returns messages after that cursor.
- **Staff insight**: Don't use offset-based pagination for chat — messages are inserted continuously, causing skipped/duplicate items. Use keyset pagination: `WHERE timestamp > :last_ts AND message_id > :last_id LIMIT 50`.

### Read Receipts
- **Per-user cursor**: `last_read_message_id` in `conversation_members` table.
- **Staff insight**: Update read cursor on message view, not on every scroll. Batch read receipt updates (e.g., mark all messages before the top-visible message as read). Use `user_unread_counts` counter for real-time badge counts.

### Group Conversation Scaling
- **Write amplification**: Each group message writes to `messages` + `message_delivery` for each member.
- **Staff insight**: For groups with 100+ members, don't write `message_delivery` for each member — it's O(N) write amplification. Instead, track read cursors and compute delivery status on read. Use `message_delivery` table only for small groups (< 20 members).

### Message Deletion & GDPR
- **Soft delete**: `is_deleted = TRUE` removes content; keeps metadata for ordering.
- **Staff insight**: "Delete for everyone" sets `is_deleted = TRUE` and clears `content`. On read, skip deleted messages. For GDPR physical deletion, tombstone the row and remove from search index. Cassandra tombstones are compacted away eventually.
