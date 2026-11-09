# High-Level Design (HLD)

This section covers high-level design concepts and case studies for system design interviews.

**References**: [Educative.io](https://www.educative.io/courses/grokking-the-system-design-interview), [ByteByteGo](https://bytebytego.com/courses/system-design-interview), [AlgoMaster](https://algomaster.io/learn/system-design), [HelloInterview](https://www.hellointerview.com/learn/system-design)

## Contents

- [Fundamentals](fundamentals/) - Core HLD concepts
- [Diagrams](diagrams/) - Excalidraw diagrams for architecture, sequence flows, and deployment topologies
- [Case Studies](case-studies/) - Real-world system design examples
- [Problems](problems/) - Additional system design problems

## Diagrams

This project uses [Excalidraw](https://excalidraw.com) for creating HLD diagrams. Install the **Excalidraw Integration** plugin in IntelliJ IDEA to view and edit `.excalidraw` files directly in the IDE.

See [diagrams/README.md](diagrams/README.md) for setup instructions and conventions.

## Fundamentals

| Topic | Description |
|-------|-------------|
| [Scalability](fundamentals/scalability.md) | Horizontal vs vertical scaling, scaling strategies |
| [Load Balancing](fundamentals/load-balancing.md) | Load balancer algorithms, L4 vs L7 |
| [Caching](fundamentals/caching.md) | Cache strategies, CDN, cache invalidation |
| [Database Sharding](fundamentals/database-sharding.md) | Sharding strategies, shard allocation |
| [Replication](fundamentals/replication.md) | Master-slave, master-master replication |
| [Consistency](fundamentals/consistency.md) | CAP theorem, PACELC, consistency models |
| [Message Queues](fundamentals/message-queues.md) | Pub/sub, message brokers, event-driven architecture |
| [Rate Limiting](fundamentals/rate-limiting.md) | Rate limiting algorithms and strategies |

## Case Studies

- [URL Shortener](case-studies/url-shortener/) - Design a URL shortening service
- [WhatsApp](case-studies/whatsapp/) - Design a messaging platform
- [Instagram](case-studies/instagram/) - Design a photo sharing platform
- [Uber](case-studies/uber/) - Design a ride-sharing platform
- [YouTube](case-studies/youtube/) - Design a video streaming platform
- [Notification System](case-studies/notification-system/) - Design a notification service
- [E-commerce System](case-studies/ecommerce-system/) - Design an e-commerce platform
- [Payment System](case-studies/payment-system/) - Design a payment processing system

## Additional Problems (25 Problems)

| Problem | Key Concepts | Reference |
|---------|-------------|-----------|
| [Twitter](problems/twitter/) | Microblogging, fan-out on write, timeline service | Educative.io, ByteByteGo |
| [Dropbox](problems/dropbox/) | File storage, sync, chunked upload, conflict resolution | Educative.io |
| [Web Crawler](problems/web-crawler/) | URL frontier, politeness, deduplication, link graph | Educative.io |
| [News Feed](problems/news-feed/) | Fan-out strategies, feed ranking, media processing | Educative.io |
| [Search Autocomplete](problems/search-autocomplete/) | Trie, prefix indexing, trending suggestions | Educative.io |
| [Chat System](problems/chat-system/) | WebSocket, presence, offline delivery, read receipts | Educative.io |
| [Rate Limiter](problems/rate-limiter/) | Token bucket, sliding window, distributed counters | Educative.io |
| [Key-Value Store](problems/key-value-store/) | Consistent hashing, replication, Raft consensus | Educative.io |
| [ID Generator](problems/id-generator/) | Snowflake, UUID, database sequence, distributed | Educative.io |
| [Google Drive](problems/google-drive/) | Cloud storage, versioning, sharing, conflict resolution | Educative.io |
| [Google Maps](problems/google-maps/) | Geospatial indexing, routing, ETA, real-time traffic | Educative.io |
| [Message Queue](problems/message-queue/) | Pub/sub, ordering, persistence, consumer groups | Educative.io |
| [Metrics Monitoring](problems/metrics-monitoring/) | Time-series DB, aggregation, alerting, dashboards | Educative.io |
| [Ad Click Aggregation](problems/ad-click-aggregation/) | Real-time counting, deduplication, multi-dimensional | Educative.io |
| [Hotel Reservation](problems/hotel-reservation/) | Availability search, booking, payment, cancellation | Educative.io |
| [Email Service](problems/email-service/) | SMTP, queue, delivery tracking, bounce handling | Educative.io |
| [S3 Storage](problems/s3-storage/) | Object storage, multipart upload, versioning, CDN | Educative.io |
| [LeetCode](problems/leetcode/) | Code editor, compiler, test execution, submissions | Educative.io |
| [ChatGPT](problems/chatgpt/) | LLM inference, streaming, rate limiting, context window | Educative.io |
| [Google Docs](problems/google-docs/) | OT/CRDT, WebSocket, collaborative editing, versioning | Educative.io |
| [Ticketmaster](problems/ticketmaster/) | Virtual queue, seat locking, bot prevention, high-scale | Educative.io, ByteByteGo |
| [Deployment System](problems/deployment-system/) | Blue-green, canary, rollback, health checks | Educative.io |
| [Recommendation Engine](problems/recommendation-engine/) | Two-phase rec, feature store, real-time + batch | Educative.io, ByteByteGo |
| [IoT Pipeline](problems/iot-pipeline/) | MQTT, Kafka, time-series DB, tiered storage | Educative.io, ByteByteGo |
| [Streaming Analytics](problems/streaming-analytics/) | Flink, windowing, exactly-once, materialized views | Educative.io, ByteByteGo |
