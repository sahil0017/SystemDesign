# Distributed Task Scheduler

## Problem Statement

Design a distributed task scheduler like Apache Airflow or Cron that supports scheduling recurring and one-time tasks, managing task dependencies, handling failures with retries, and providing execution monitoring.

**Reference**: AlgoMaster, ByteByteGo

## Requirements

### Functional Requirements
- **Task scheduling**: Cron-based scheduling; one-time delayed execution.
- **Dependencies**: DAG-based task dependencies; execute in topological order.
- **Retry policy**: Configurable retry count, backoff strategy (exponential, linear).
- **Worker management**: Distribute tasks across worker nodes; load balancing.
- **Monitoring**: Track task status, execution time, and failure rates.

### Non-Functional Requirements
- **Scale**: 100K+ scheduled tasks; 1,000+ worker nodes.
- **Reliability**: No lost tasks; exactly-once execution where possible.
- **Latency**: Task dispatch < 1s after scheduled time.

## Key Design Decisions
- **Central scheduler**: Single source of truth for task scheduling; replicated for HA.
- **Pull-based dispatch**: Workers poll for tasks; scheduler assigns based on capacity.
- **DAG execution**: Topological sort for dependency resolution; parallel execution of independent tasks.
- **Idempotency**: Tasks are idempotent to handle retries safely.

## Staff-Level Design Considerations

### Exactly-Once Execution
- **Deduplication**: Track executed task IDs in a durable store. Before executing, check if already completed.
- **Staff insight**: True exactly-once is impossible in distributed systems. Use at-least-once + idempotent tasks. The task ID is the deduplication key.

### Leader-Based Scheduling
- **Single scheduler**: One scheduler instance is the leader; others are standbys. Leader election via Raft.
- **Staff insight**: Multiple schedulers cause duplicate task assignment. Use a leader-based approach with automatic failover. The leader holds the schedule in memory and persists to a durable store.
