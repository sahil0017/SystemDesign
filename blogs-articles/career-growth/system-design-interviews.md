# System Design Interviews

## Overview

System design interviews assess your ability to design large-scale distributed systems. Unlike coding interviews, there's no single correct answer — interviewers evaluate your thought process, trade-off analysis, and communication skills.

## Interview Framework

### 1. Requirements Gathering (5 minutes)
- Clarify functional requirements (what should the system do?)
- Estimate scale (DAU, QPS, data size, storage needs)
- Identify non-functional requirements (latency, availability, consistency)

### 2. High-Level Design (10 minutes)
- Draw key components: client, LB, services, databases, cache
- Define data flow between components
- Choose storage strategy (SQL, NoSQL, cache)

### 3. Deep Dive (15 minutes)
- Dive into 2-3 components in detail
- Discuss API design, data models, and algorithms
- Address scalability, fault tolerance, and consistency

### 4. Trade-offs and Optimization (5 minutes)
- Identify bottlenecks and single points of failure
- Discuss alternatives and why you chose your approach
- Propose improvements and future enhancements

## Common Questions

| Question | Key Concepts |
|----------|-------------|
| Design URL Shortener | Base62 encoding, redirect, analytics |
| Design Twitter/News Feed | Fan-out, push/pull, ranking |
| Design Uber | Geospatial indexing, matching, surge pricing |
| Design YouTube | Transcoding, CDN, adaptive bitrate |
| Design Chat System | WebSocket, presence, offline delivery |
| Design Rate Limiter | Token bucket, sliding window, distributed |

## Estimation Cheat Sheet

### Traffic Estimation
```
DAU = 100 million
Active hours = 12 hours/day
Requests per user = 30/day
Total requests = 100M × 30 = 3B/day
QPS = 3B / (12 × 3600) ≈ 70,000
```

### Storage Estimation
```
Tweet size = 140 bytes + metadata ≈ 500 bytes
Tweets per day = 500 million
Daily storage = 500M × 500B ≈ 250 GB
Yearly storage = 250 GB × 365 ≈ 90 TB
```

## Staff-Level Insights

### Communicate Your Thinking
- Talk through your design as you go — don't stay silent
- Ask clarifying questions before diving in
- **Staff insight**: Interviewers care more about your process than your answer. A mediocre design with clear reasoning beats a perfect design with no explanation.

### Start Simple, Then Scale
- Begin with a simple design that works
- Identify bottlenecks and add complexity incrementally
- **Staff insight**: Don't jump to microservices and sharding immediately. Start with a monolith and a single database, then add components as you identify needs. This shows you understand when complexity is justified.

### Know Your Numbers
- Memorize common benchmarks: HTTP request size, DB query latency, cache hit rates
- Practice back-of-envelope calculations
- **Staff insight**: You don't need exact numbers, but you need reasonable estimates. If you say "this handles 1M QPS" without justification, you'll lose credibility. Show your math.

### Practice with Real Systems
- Study how real systems work (blog posts, architecture docs)
- Understand trade-offs in production systems
- **Staff insight**: Read engineering blogs from companies like Netflix, Uber, and AWS. Understanding real-world trade-offs is more valuable than memorizing interview answers.
