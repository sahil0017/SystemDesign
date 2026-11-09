# Notification Service

## Problem Statement (Staff-Level)

Design a notification service that handles multi-channel delivery (push, email, SMS, in-app), user preferences, templating, scheduling, rate limiting, delivery tracking, and real-time analytics. The system should support 1B+ notifications/day with 99.99% delivery rate and sub-2-second push notification latency.

**Reference**: AlgoMaster, HelloInterview, LLD Coding, ByteByteGo

## Requirements

### Functional Requirements
- **Multi-channel**: Push (FCM/APNs), email (SES/SendGrid), SMS (Twilio), in-app (WebSocket)
- **User preferences**: Per-channel opt-in/opt-out; quiet hours; notification frequency
- **Templating**: Dynamic templates with variables; localization; A/B testing
- **Scheduling**: Immediate send; scheduled send; recurring notifications
- **Prioritization**: High (urgent), normal, low (promotional) with different delivery strategies
- **Batching**: Group notifications into digest (e.g., daily summary)
- **Delivery tracking**: Sent, delivered, opened, clicked, failed with retry logic
- **Analytics**: Delivery rates, open rates, click-through rates, unsubscribe rates

### Non-Functional Requirements
- **Scale**: 1B+ notifications/day; 100K+ notifications/sec peak
- **Latency**: Push < 2s; email < 30s; SMS < 10s; in-app < 500ms
- **Availability**: 99.99% uptime for high-priority; 99.9% for promotional
- **Reliability**: At-least-once delivery with idempotent sends

## Key Design Decisions
- **Event-driven**: Kafka for notification events; decoupled producers and consumers
- **Channel adapters**: Pluggable channel providers (FCM, SES, Twilio, WebSocket)
- **Database**: PostgreSQL for user preferences and templates; Cassandra for delivery logs
- **Cache (Redis)**: User preferences cache, rate limiting, deduplication

## Staff-Level Design Considerations

### Rate Limiting
- **Per-user**: Max N notifications per hour per channel to prevent spam
- **Per-template**: Max N sends per minute to prevent blast errors
- **Staff insight**: Use **token bucket** in Redis for distributed rate limiting

### Retry Strategy
- **Exponential backoff**: 1s, 5s, 30s, 5min, 30min before dead letter queue
- **Idempotent sends**: Same notification_id sent only once per channel
- **Staff insight**: Different channels have different retry semantics. Push is fire-and-forget; email needs webhook confirmation.
