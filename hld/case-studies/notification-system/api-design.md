# Notification System - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via Bearer token. Supports bulk operations for high-volume sends.

## Send Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/notifications/send` | Send notification immediately |
| POST | `/api/v1/notifications/send-bulk` | Send to multiple users (max 1000) |
| POST | `/api/v1/notifications/schedule` | Schedule notification for later |
| POST | `/api/v1/notifications/recurring` | Create recurring notification |

### Send Request Body
```json
{
  "user_id": "u123",
  "template_id": "t456",
  "channel": "push|email|sms|in-app|all",
  "priority": "high|normal|low",
  "variables": { "name": "John", "order_id": "ORD-789" },
  "metadata": { "order_id": "ORD-789", "campaign": "promo-2024" }
}
```

## User Preferences

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/preferences` | Get notification preferences |
| PUT | `/api/v1/users/{user_id}/preferences` | Update preferences |
| POST | `/api/v1/users/{user_id}/opt-out` | Opt out of channel |
| POST | `/api/v1/users/{user_id}/opt-in` | Opt in to channel |

### Preferences Response
```json
{
  "user_id": "u123",
  "push": { "enabled": true, "quiet_hours": { "start": "22:00", "end": "07:00", "timezone": "America/New_York" } },
  "email": { "enabled": true, "frequency": "instant" },
  "sms": { "enabled": false },
  "in_app": { "enabled": true }
}
```

## Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/templates` | List templates |
| GET | `/api/v1/templates/{template_id}` | Get template details |
| POST | `/api/v1/templates` | Create template |
| PUT | `/api/v1/templates/{template_id}` | Update template |
| DELETE | `/api/v1/templates/{template_id}` | Delete template |
| POST | `/api/v1/templates/{template_id}/preview` | Preview with sample data |

## In-App Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/in-app` | List in-app notifications |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| GET | `/api/v1/notifications/unread-count` | Get unread count |
| DELETE | `/api/v1/notifications/{id}` | Delete notification |

## Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/delivery` | Delivery rates by channel |
| GET | `/api/v1/analytics/templates/{id}` | Template performance |
| GET | `/api/v1/analytics/users/{id}` | User notification stats |
| GET | `/api/v1/analytics/dashboard` | Overall dashboard metrics |

## Webhooks

| Event | Payload | Description |
|-------|---------|-------------|
| `notification.delivered` | `{notification_id, channel, delivered_at}` | Notification delivered |
| `notification.failed` | `{notification_id, channel, error}` | Delivery failed |
| `notification.opened` | `{notification_id, opened_at}` | Email/notification opened |
| `notification.clicked` | `{notification_id, url, clicked_at}` | Link clicked |
| `notification.opted_out` | `{user_id, channel, opted_out_at}` | User opted out |

## Staff-Level API Design Considerations

### Bulk Send
- **Max batch size**: 1000 users per request to prevent overload
- **Async processing**: Returns immediately; tracks via `batch_id`
- **Progress tracking**: `GET /api/v1/batches/{batch_id}/status`
- **Partial failure**: Continue sending even if some users fail

### Idempotency
- All send operations require `Idempotency-Key` header
- Same key returns original result without re-sending
- Key TTL: 24 hours
