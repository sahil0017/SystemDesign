# Designing a Chat System

## Overview

A chat system enables real-time messaging between users or groups. Services like WhatsApp, Slack, and Discord handle billions of messages daily with real-time delivery, read receipts, and offline support.

## Key Components

### 1. Real-Time Communication
- **WebSocket**: Persistent connection for bidirectional real-time messaging
- **Connection management**: Handle connect, disconnect, reconnection with heartbeat
- **Fallback**: HTTP long-polling for environments that don't support WebSocket

### 2. Message Delivery
```
Sender → API → Message Store → WebSocket Push → Recipient
```
- **Online recipient**: Deliver via WebSocket immediately
- **Offline recipient**: Store in database, deliver on next connection
- **Delivery guarantees**: At-least-once delivery with idempotency keys

### 3. Message Storage
- **Schema**: `message_id, conversation_id, sender_id, content, timestamp, status`
- **Database**: Cassandra/DynamoDB for write-heavy workload
- **Pagination**: Cursor-based pagination for message history

### 4. Presence System
- **Online status**: Track connected users via Redis with TTL
- **Typing indicator**: WebSocket event with short TTL
- **Last seen**: Store timestamp on disconnect

## Conversation Models

### Direct Message (1:1)
- Conversation ID derived from sorted user IDs: `min(id1,id2):max(id1,id2)`
- Deduplicate conversations on the server side

### Group Chat
- Separate `conversation_members` table for membership
- Admin roles for group management (add/remove members)
- Rate limiting per user to prevent spam

## Scalability Considerations

### Connection Scaling
- **Stateless WebSocket servers**: Store session state in Redis
- **Sticky sessions**: Route user to same server for WebSocket connection
- **Horizontal scaling**: Add more servers behind load balancer

### Message Ordering
- **Per-conversation ordering**: Use sequence number or timestamp
- **Eventual consistency**: Messages may arrive out of order; client reorders
- **Vector clocks**: For complex ordering in group chats

## Staff-Level Insights

### Offline Message Sync
- On reconnect, fetch messages since `last_seen_timestamp`
- Limit sync window (e.g., last 7 days) to prevent large payloads
- Use **delta sync** with message IDs for efficient updates

### Message Retention
- Store all messages in hot storage for N days
- Archive older messages to cold storage (S3)
- Provide search within retention window using Elasticsearch

### End-to-End Encryption
- Use **Signal Protocol** for E2E encryption
- Key exchange via Diffie-Hellman on first message
- Server never sees plaintext messages — only encrypted blobs
