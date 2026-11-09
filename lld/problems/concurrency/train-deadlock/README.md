# Train Deadlock (Concurrency)

## Problem Statement

Design a multi-threaded train track system where multiple trains move along shared track segments. Each train must acquire locks on track segments before moving and release them after leaving, without causing deadlocks when trains compete for the same segments.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Track segments**: Divided into numbered segments; each segment can hold only one train at a time.
- **Train movement**: Each train moves from segment to segment in a defined route.
- **Segment locking**: Train must lock the next segment before moving into it.
- **Route definition**: Each train has a predefined route (sequence of segments).
- **Collision prevention**: No two trains can occupy the same segment simultaneously.
- **Emergency stop**: Ability to halt all trains safely.

### Non-Functional Requirements
- **Deadlock-free**: System must never freeze due to circular waits.
- **Liveness**: Trains must eventually progress; no starvation.
- **Thread safety**: Each train runs in its own thread.
- **Scalability**: Support 100+ trains on 1K+ segments.

## Key Design Decisions
- **Lock ordering**: Assign global order to segments; always acquire in ascending order.
- **Try-lock with timeout**: If a segment is unavailable, wait with timeout and retry.
- **Rollback strategy**: If a train cannot acquire the next segment, release all held segments and retry.
- **Semaphore per segment**: Each segment has a binary semaphore (available/occupied).

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Train     │────►│ TrackSegment │────►│     Track    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - trainId    │     │ - segmentId  │     │ - segments   │
│ - route      │     │ - semaphore  │     │ - numSegments│
│ - currentSeg │     │ - occupiedBy │     ├──────────────┤
├──────────────┤     └──────────────┘     │ + acquire()  │
│ + move()     │                          │ + release()  │
│ + rollback() │                          │ + emergency  │
│ + stop()     │                          └──────────────┘
└──────────────┘
```

## Staff-Level Design Considerations

### Deadlock Scenario
- **Circular wait**: Train A holds S0, waits for S1. Train B holds S1, waits for S0 → deadlock.
- **Staff insight**: This is the classic dining philosophers problem. The same solutions apply: lock ordering, resource hierarchy, or wait-die/wound-wait schemes.

### Lock Ordering Solution
- **Global order**: Number segments 0..N-1. Always acquire locks in ascending order.
- **Staff insight**: Lock ordering breaks the circular wait condition. If Train A needs S0→S1 and Train B needs S0→S1, both acquire S0 first — no cycle possible.

### Try-Lock with Rollback
- **Non-blocking acquire**: Use `tryLock(timeout)` instead of `lock()`. If failed, release all held locks and retry.
- **Staff insight**: This is similar to database transaction rollback. The key is to release locks in reverse order of acquisition to prevent partial-lock deadlocks.

### Starvation Prevention
- **Fair locks**: Use fair `ReentrantLock` or `Semaphore` to ensure FIFO ordering.
- **Staff insight**: Without fairness, a train might never get a segment if other trains keep acquiring it. Fair locks add overhead but prevent starvation.
