# Rate Limiter (Concurrency)

## Problem Statement

Implement thread-safe rate limiters using Token Bucket and Sliding Window algorithms for controlling request throughput.

**Reference**: AlgoMaster

## Requirements
- **Token Bucket**: Refill tokens at fixed rate; consume on each request.
- **Sliding Window**: Track requests in time window; reject if count exceeds limit.
- **Thread safety**: Safe for concurrent access from multiple threads.

## Key Design Decisions
- **Token Bucket**: `AtomicLong` for token count; periodic refill via scheduled executor.
- **Sliding Window**: `ConcurrentLinkedQueue` of timestamps; remove expired on each check.

## Staff-Level Design Considerations
- **Staff insight**: Token bucket allows bursts (up to bucket size). Sliding window is smoother but uses more memory. For API rate limiting, use token bucket. For precise per-second limits, use sliding window.
