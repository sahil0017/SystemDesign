# Notification System - Architecture

## System Components

1. **API Gateway**: Entry point; authentication, rate limiting, request routing
2. **Notification Service**: Core orchestration — create, route, track notifications
3. **Preference Service**: User notification preferences, opt-in/opt-out, quiet hours
4. **Template Service**: Template management, variable substitution, localization
5. **Push Service**: FCM/APNs integration for mobile push notifications
6. **Email Service**: SES/SendGrid integration for email delivery
7. **SMS Service**: Twilio integration for SMS delivery
8. **In-App Service**: WebSocket-based in-app notification delivery
9. **Scheduler Service**: Scheduled and recurring notifications with cron-like scheduling
10. **Analytics Service**: Delivery rates, open rates, click-through rates
11. **Database (PostgreSQL)**: User preferences, templates, notification definitions
12. **Database (Cassandra)**: Delivery logs, analytics events (high write throughput)
13. **Cache (Redis)**: Preference cache, rate limiting, deduplication
14. **Message Queue (Kafka)**: Notification events, delivery status updates
15. **Dead Letter Queue**: Failed notifications after max retries

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │Notification│  │Preference│  │ Template │  │Scheduler │  │Analytics │  │  In-App│
   │  Service   │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │                │              │              │              │             │
        └────────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Notification events, delivery status         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │  Push    │  │  Email   │  │   SMS    │  │PostgreSQL│  │ Cassandra│  │   Redis│
   │ (FCM/    │  │ (SES/    │  │(Twilio)  │  │(Prefs,   │  │(Delivery │  │(Cache, │
   │  APNs)   │  │ SendGrid)│  │          │  │Templates)│  │ logs)    │  │Rate lim)│
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Notification Creation Flow
- Service publishes notification event to Kafka topic `notifications.create`
- Notification Service consumes event → fetches user preferences from Redis/PostgreSQL
- Checks user opt-in status, quiet hours, and rate limits
- If allowed: routes to appropriate channel services based on priority and preference
- If blocked: logs reason (opted out, quiet hours, rate limited)

### 2. Push Notification Flow
- Push Service receives notification → selects FCM or APNs based on device
- Applies template with variable substitution
- Sends to FCM/APNs with retry logic (exponential backoff, max 3 retries)
- On success: updates status to "delivered" in Cassandra
- On failure: retries or moves to dead letter queue after max retries

### 3. Email Notification Flow
- Email Service receives notification → renders template (HTML + text)
- Sends via SES/SendGrid with tracking pixels and unsubscribe link
- Delivery status tracked via webhooks from email provider
- Open/click events tracked via tracking pixel and URL redirects

### 4. In-App Notification Flow
- In-App Service receives notification → stores in PostgreSQL
- If user online: pushes via WebSocket in real-time
- If user offline: available on next app open via API
- Read status tracked when user views notification

## Staff-Level Design Considerations

### Rate Limiting
- **Per-user**: Max N notifications per hour per channel to prevent spam
- **Per-template**: Max N sends per minute to prevent blast errors
- **Global**: System-wide rate limit to protect downstream providers
- **Staff insight**: Use **token bucket** in Redis for distributed rate limiting

### Retry Strategy
- **Exponential backoff**: 1s, 5s, 30s, 5min, 30min before DLQ
- **Idempotent sends**: Same notification_id sent only once per channel
- **Dead letter queue**: Failed notifications after max retries for manual review
- **Staff insight**: Different channels have different retry semantics. Push is fire-and-forget; email needs webhook confirmation.

### Quiet Hours & Preferences
- **Timezone-aware**: Store user timezone; evaluate quiet hours in user's local time
- **Preference cache**: Redis cache with 5min TTL; fallback to PostgreSQL
- **Priority override**: High-priority notifications bypass quiet hours
- **Staff insight**: Use **cron-like expressions** for scheduling with timezone support

### Analytics
- **Delivery rate**: Delivered / Sent per channel per template
- **Open rate**: Opened / Delivered (email with tracking pixel)
- **Click-through rate**: Clicked / Opened
- **Unsubscribe rate**: Unsubscribed / Sent
- **Staff insight**: Use **real-time analytics** with Kafka Streams for live dashboards
