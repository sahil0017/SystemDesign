# WhatsApp - API Design

## API Overview

RESTful API for non-real-time operations (profile, groups, media). Real-time messaging uses MQTT protocol. All endpoints require authentication via phone number + JWT.

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/send-otp` | Send OTP to phone number |
| POST | `/api/v1/auth/verify-otp` | Verify OTP, return JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate session |

## User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update profile (name, photo) |
| GET | `/api/v1/users/{user_id}` | Get user profile |
| POST | `/api/v1/users/contacts/upload` | Upload contact list for discovery |
| GET | `/api/v1/users/contacts` | Get WhatsApp contacts |

## Messaging (REST for sync operations)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chats` | List conversations |
| GET | `/api/v1/chats/{chat_id}/messages` | Get message history (paginated) |
| POST | `/api/v1/chats/{chat_id}/archive` | Archive chat |
| DELETE | `/api/v1/chats/{chat_id}/messages/{msg_id}` | Delete message for me |
| POST | `/api/v1/messages/{msg_id}/star` | Star a message |

> Note: Real-time message sending uses MQTT, not REST.

## Groups

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/groups` | Create group |
| GET | `/api/v1/groups` | List user's groups |
| GET | `/api/v1/groups/{group_id}` | Get group info |
| PUT | `/api/v1/groups/{group_id}` | Update group name/icon |
| POST | `/api/v1/groups/{group_id}/participants` | Add participants |
| DELETE | `/api/v1/groups/{group_id}/participants/{user_id}` | Remove participant |
| POST | `/api/v1/groups/{group_id}/admins/{user_id}` | Promote to admin |
| DELETE | `/api/v1/groups/{group_id}/admins/{user_id}` | Demote from admin |
| DELETE | `/api/v1/groups/{group_id}` | Delete group |

## Media

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/media/upload` | Upload media (multipart) |
| GET | `/api/v1/media/{media_id}/url` | Get media download URL (signed) |
| DELETE | `/api/v1/media/{media_id}` | Delete media |

## Status/Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/status` | Create status update |
| GET | `/api/v1/status` | Get user's statuses |
| GET | `/api/v1/status/{status_id}/views` | Get status viewers |
| DELETE | `/api/v1/status/{status_id}` | Delete status |

## MQTT Topics (Real-time)

| Topic | Direction | Description |
|-------|-----------|-------------|
| `msg/{sender_id}/{recipient_id}` | Publish | Send 1:1 message |
| `msg/group/{group_id}` | Publish | Send group message |
| `presence/{user_id}` | Publish/Subscribe | Online/offline status |
| `receipt/{user_id}` | Publish | Delivery/read receipts |
| `call/{user_id}/invite` | Publish | Call invitation |
| `call/{user_id}/accept` | Publish | Accept call |
| `call/{user_id}/reject` | Publish | Reject call |

## Staff-Level API Design Considerations

### MQTT QoS Levels
- **QoS 0** (At most once): Presence updates, typing indicators
- **QoS 1** (At least once): Messages, read receipts — default for messaging
- **QoS 2** (Exactly once): Critical operations (group admin changes)

### Message Format (MQTT Payload)
```json
{
  "msg_id": "uuid-v4",
  "type": "text|image|video|audio|document|location|contact",
  "content": "encrypted payload",
  "timestamp": 1609459200,
  "ttl": 2592000,
  "metadata": {
    "caption": "encrypted",
    "file_size": 1048576,
    "mime_type": "image/jpeg"
  }
}
```

### Security
- **TLS 1.3** for all connections (MQTT and REST)
- **End-to-end encryption**: Signal Protocol on client side
- **Pre-key bundle**: Stored on server for async key exchange
- **Session rotation**: Periodic key rotation for forward secrecy
