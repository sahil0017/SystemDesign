# Call Center Queue (Concurrency)

## Problem Statement

Design a multi-threaded call center queue system where incoming calls are distributed among available agents based on priority, skill matching, and wait time. Multiple threads handle call arrivals, agent availability changes, and call routing concurrently.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Call arrival**: New calls enter the queue with priority and required skill set.
- **Agent pool**: Agents with different skills; can be idle, busy, or on break.
- **Call routing**: Match calls to agents based on skill, priority, and FIFO within same priority.
- **Wait time tracking**: Track how long each call has waited; escalate if threshold exceeded.
- **Call transfer**: Transfer a call from one agent to another.
- **Statistics**: Real-time metrics (avg wait time, active calls, agent utilization).

### Non-Functional Requirements
- **Thread safety**: Concurrent call arrivals and agent state changes are safe.
- **No lost calls**: Every call is eventually routed to an agent.
- **Low latency**: Call routing decision < 100ms.
- **Scalability**: Support 1K+ concurrent calls and 500+ agents.

## Key Design Decisions
- **Priority queue**: Calls ordered by priority and arrival time.
- **BlockingQueue**: Agents wait on a queue for incoming calls.
- **ReadWriteLock**: Read agent stats concurrently; exclusive lock for state changes.
- **Observer pattern**: Notify monitoring system of queue depth changes.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Call      │────►│ CallCenter   │────►│    Agent     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - callId     │     │ - callQueue  │     │ - agentId    │
│ - priority   │     │ - agentPool  │     │ - skills     │
│ - skills     │     │ - stats      │     │ - status     │
│ - arrivalTime│     ├──────────────┤     ├──────────────┤
└──────────────┘     │ + enqueue()  │     │ + takeCall() │
                     │ + route()    │     │ + release()  │
                     │ + getStats() │     └──────────────┘
                     └──────────────┘
```

## Staff-Level Design Considerations

### Priority Queue Thread Safety
- **Concurrent priority queue**: Use `PriorityBlockingQueue` for thread-safe ordering.
- **Staff insight**: `PriorityBlockingQueue` doesn't support null and doesn't guarantee FIFO for equal-priority elements. For strict FIFO within same priority, include timestamp in the comparator.

### Agent Call Distribution
- **Work-stealing**: When an agent becomes free, it pulls the highest-priority call from the queue.
- **Staff insight**: This is the producer-consumer pattern. Calls are produced by the queue system and consumed by agents. Use `BlockingQueue.take()` for agents to wait efficiently without busy-polling.

### Escalation Mechanism
- **Delayed queue**: Use `DelayQueue` to track calls that exceed wait time threshold.
- **Staff insight**: Don't poll the queue to check wait times — it's O(n). Use `DelayQueue` which efficiently retrieves elements whose delay has expired.

### Statistics Collection
- **Atomic counters**: Use `AtomicLong` and `LongAdder` for concurrent statistics.
- **Staff insight**: `LongAdder` outperforms `AtomicLong` under high contention because it uses striped counters. Use `LongAdder` for metrics, `AtomicLong` for state.
