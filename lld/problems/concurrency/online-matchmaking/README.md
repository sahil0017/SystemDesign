# Online Matchmaking (Concurrency)

## Problem Statement

Design a real-time online matchmaking system (like gaming or dating apps) where multiple threads concurrently search for matching users based on criteria (skill level, location, preferences). Matches must be found quickly without race conditions when two users compete for the same match.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **User profile**: Each user has skills, preferences, location, and status (searching/matched/in-game).
- **Match criteria**: Configurable matching rules (skill range, distance, preferences).
- **Match queue**: Users enter a queue when searching; system finds compatible matches.
- **Match notification**: Notify both users when a match is found.
- **Timeout**: If no match is found within N seconds, re-queue the user.
- **Cancellation**: User can cancel search at any time.

### Non-Functional Requirements
- **Thread safety**: No double-matching (one user matched to two opponents simultaneously).
- **Low latency**: Match found within 5 seconds for 95% of users.
- **Scalability**: Support 10K+ concurrent searchers.
- **Fairness**: Users who wait longer get priority matching.

## Key Design Decisions
- **Concurrent hash map**: Store searching users indexed by criteria for fast lookup.
- **Lock per bucket**: Fine-grained locking to minimize contention.
- **Timeout mechanism**: `DelayQueue` for users who exceed match timeout.
- **Atomic state transition**: User status changes from SEARCHING → MATCHED atomically.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│ MatchMaker   │────►│  MatchQueue  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - searchers  │     │ - queue      │
│ - skills     │     │ - criteria   │     │ - timeout    │
│ - status     │     ├──────────────┤     └──────────────┘
│ - prefs      │     │ + search()   │
└──────────────┘     │ + match()    │
                     │ + cancel()   │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Double-Match Prevention
- **Atomic compare-and-set**: Use `AtomicReference.compareAndSet()` for status transition.
- **Staff insight**: The race condition occurs when two threads both find the same user as a match. Only one should succeed. CAS ensures only one thread wins the transition from SEARCHING → MATCHED.

### Indexing Strategy
- **Multi-index**: Maintain separate indexes by skill level, location, and preferences.
- **Staff insight**: Don't scan all users to find a match — it's O(n). Use indexed lookups (ConcurrentHashMap per criteria) for O(1) candidate retrieval.

### Timeout Handling
- **DelayQueue**: Users are added with a timeout; when expired, they're re-queued with relaxed criteria.
- **Staff insight**: This is the same pattern as session expiration. Don't use a separate timer thread — `DelayQueue` is efficient and thread-safe.

### Fairness
- **FIFO within criteria**: Users who search longer get matched first.
- **Staff insight**: Use arrival timestamp in the matching comparator. Without it, newer users might be matched before older ones, leading to unfair wait times.
