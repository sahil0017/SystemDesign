# Distributed Email Service

## Problem Statement

Design a distributed email service like SendGrid or Amazon SES that handles high-volume email sending, template management, delivery tracking, bounce handling, and spam prevention.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Email sending**: Send transactional and marketing emails at scale.
- **Templates**: Manage email templates with dynamic content and personalization.
- **Delivery tracking**: Track sent, delivered, opened, clicked, and bounced emails.
- **Bounce handling**: Classify bounces (hard/soft); suppress hard bounce addresses.
- **Spam prevention**: SPF, DKIM, DMARC support; content filtering.
- **Rate limiting**: Per-sender and per-domain rate limits to protect sender reputation.

### Non-Functional Requirements
- **Throughput**: 10M+ emails per day; 100K+ emails per second peak.
- **Latency**: Email acceptance < 100ms; delivery < 30s.
- **Deliverability**: 99%+ inbox rate; minimize spam folder placement.

## Key Design Decisions
- **Queue-based**: Async email processing with priority queues for transactional vs marketing.
- **SMTP relay**: Connect to ISP mail servers with connection pooling.
- **Tracking pixels**: Invisible 1x1 pixel for open tracking; URL rewriting for click tracking.
- **Reputation management**: Monitor sender IP reputation; rotate IPs to maintain deliverability.

## Architecture Overview

```
Client → API Gateway → Email Service
                            → Template Engine
                            → Email Queue (Kafka)
                            → SMTP Relay Pool
                            → Tracking Service
                            
Email Queue → Worker Pool → ISP Mail Servers
                    → Tracking DB (sent, delivered, opened, clicked)
                    → Bounce Handler → Suppression List
```

## Staff-Level Design Considerations

### Email Queue Design
- **Priority queues**: Transactional emails (password reset, order confirmation) have higher priority than marketing emails.
- **Staff insight**: Use separate Kafka topics for transactional and marketing emails. Transactional consumers have more instances to ensure low latency. Marketing emails are rate-limited to protect sender reputation.

### Deliverability
- **IP rotation**: Rotate sending IPs to distribute volume and isolate bad senders.
- **Staff insight**: Each IP has a reputation score. If one IP gets blacklisted, only that IP's queue is affected. Warm up new IPs gradually (start with 100 emails/hour, increase by 20% daily).

### Tracking
- **Open tracking**: Invisible 1x1 pixel that loads from your server when the email is opened.
- **Staff insight**: Not all email clients load images by default (Gmail doesn't). Open tracking is ~60% accurate. Click tracking uses URL rewriting — redirect through your server, log the click, then forward to the destination. This is 100% accurate.
