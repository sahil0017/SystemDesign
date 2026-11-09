# Chat System (WhatsApp/Messenger)

## Problem Statement

Design a real-time chat messaging system like WhatsApp or Facebook Messenger that supports one-on-one and group messaging, media sharing, read receipts, and offline message delivery.

**Reference**: ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Direct messaging**: Real-time 1:1 messaging with message history.
- **Group chat**: Create groups; add/remove members; admin controls.
- **Media sharing**: Send images, videos, documents, and voice messages.
- **Message status**: Delivered, read receipts; typing indicators.
- **Offline support**: Store messages for offline users; deliver on reconnect.
- **Search**: Search message history by keyword, date, or sender.

### Non-Functional Requirements
- **Scale**: 2B+ users; 10B+ messages/day; 500M+ concurrent connections.
- **Latency**: Message delivery < 500ms; group fan-out < 1s.
- **Availability**: 99.99% uptime; messages never lost.

## Key Design Decisions
- **WebSocket**: Persistent connections for real-time bidirectional communication.
- **Message store**: Append-only log per conversation; partitioned by conversation ID.
- **Presence service**: Track online/offline status; last seen timestamp.
- **Media storage**: CDN for media files; thumbnails for preview.

## Architecture Overview

```
Client → WebSocket Gateway → Message Service
                                    → Message Store (Cassandra)
                                    → Presence Service (Redis)
                                    → Media Service (S3 + CDN)
                                    
Message Service → Kafka → Fan-out Service → Recipient WebSocket Gateways
```

## Staff-Level Design Considerations

### WebSocket Connection Management
- **Stateless gateways**: WebSocket gateways are stateless; connection state is in Redis.
- **Staff insight**: This allows horizontal scaling. When a client reconnects, any gateway can serve them. The gateway looks up the user's connection info in Redis and subscribes to their message topic.

### Message Delivery
- **Store-and-forward**: Messages are stored before delivery. If a recipient is offline, the message is queued and delivered on reconnect.
- **Staff insight**: Use a message queue (Kafka) with per-user topics. The gateway subscribes to the user's topic and pushes messages via WebSocket. This decouples producers from consumers.

### Group Chat Fan-out
- **Async fan-out**: When a message is sent to a group, publish to Kafka. A fan-out service writes to each member's message queue.
- **Staff insight**: Don't fan out synchronously — it's O(n) and blocks the sender. Async fan-out with Kafka ensures the sender gets an immediate acknowledgment.
