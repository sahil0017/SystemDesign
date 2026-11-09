# WhatsApp - Architecture

## System Components

1. **API Gateway**: Entry point for all client requests; authentication, rate limiting
2. **User Service**: Registration, authentication, profile management, contact discovery
3. **Message Service**: Core messaging engine; message routing, delivery, persistence
4. **Presence Service**: Online/offline status tracking with real-time updates
5. **Group Service**: Group creation, member management, admin controls
6. **Media Service**: Media upload, processing, storage, CDN distribution
7. **Notification Service**: Push notifications for offline users (FCM/APNs)
8. **Call Service**: WebRTC signaling for voice/video calls
9. **Status Service**: Ephemeral status updates with 24-hour TTL
10. **Encryption Service**: Signal Protocol key management and key exchange
11. **MQTT Broker**: Persistent connections for real-time messaging (EMQX/Mosquitto)
12. **Database (Cassandra)**: Message storage with high write throughput
13. **Database (PostgreSQL)**: User data, groups, contacts
14. **Cache (Redis)**: Presence, session data, message queue for offline users
15. **Object Storage (S3)**: Media storage with CDN distribution

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    CDN (CloudFront)                  │
                    │         Media thumbnails and static assets           │
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
   │  User  │  │ Message  │  │ Presence │  │  Group   │  │  Media   │  │  Call  │
   │Service │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                  MQTT Broker                         │
                    │         Persistent connections, QoS, Pub/Sub         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │ Cassandra│  │   Redis  │  │   S3     │  │ FCM/APNs │  │Encrypt.│
   │(Users,   │  │(Messages)│  │(Presence,│  │(Media)   │  │(Push     │  │Service │
   │ Groups)  │  │          │  │ Queue)   │  │          │  │ Notif.)  │  │        │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Message Sending Flow
- Sender composes message → client encrypts with Signal Protocol
- Message sent via MQTT to Message Service
- Message Service checks recipient presence in Redis
- **If online**: Route directly via MQTT to recipient (real-time)
- **If offline**: Store in Cassandra; queue in Redis; send push notification via FCM/APNs
- Update delivery status: sent → delivered → read

### 2. Message Delivery Flow (Offline Recipient)
- Recipient comes online → connects via MQTT
- MQTT broker delivers queued messages from Redis
- Client decrypts and displays messages
- Send read receipt back to sender via MQTT
- Delete message from Redis queue after successful delivery

### 3. Group Message Flow
- Sender sends message to group → Group Service
- Group Service fetches member list from PostgreSQL
- Message Service publishes to each member via MQTT
- Each member receives message independently
- Group metadata (name, icon, admins) cached in Redis

### 4. Presence Flow
- Client connects via MQTT → publishes presence to Redis
- Redis pub/sub notifies contacts of status change
- Presence stored with TTL (30s); expires = offline
- "Last seen" timestamp stored in Redis for offline users

## Staff-Level Design Considerations

### MQTT vs WebSocket
- **MQTT**: Lightweight, QoS levels, persistent sessions, ideal for mobile
- **WebSocket**: Full-duplex, HTTP-compatible, heavier overhead
- **Choice**: MQTT for messaging; WebSocket for calls (WebRTC signaling)

### Message Persistence
- Store messages for **30 days** for offline delivery
- After 30 days, delete from Cassandra (TTL-based)
- Use **Cassandra TTL** for automatic expiration

### End-to-End Encryption
- **Signal Protocol**: Double Ratchet algorithm for forward secrecy
- **Key exchange**: X3DH (Extended Triple Diffie-Hellman)
- **Server never sees plaintext**: Encryption/decryption on client only
- **Pre-keys**: Server stores pre-keys for async key exchange

### Scalability
- **MQTT brokers**: Horizontal scaling with partitioning by user ID
- **Cassandra**: Partition by sender_id + timestamp for message writes
- **Redis**: Cluster mode for presence and message queues
