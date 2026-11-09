# URL Shortener

## Problem Statement

Design a URL shortening service like bit.ly that takes a long URL and returns a short URL.

## Requirements

### Functional Requirements
- Given a long URL, generate a short URL
- Redirect short URL to the original long URL
- Allow custom short URLs
- Track analytics (clicks, referrers, etc.)
- Expire URLs after a certain period

### Non-Functional Requirements
- High availability
- Low latency redirects
- Handle millions of URLs
- Scalable read/write operations

## Key Design Decisions

- URL encoding algorithm
- Database choice
- Caching strategy
- Analytics collection
