# Distributed Task Scheduler

## Problem Statement

Design a distributed task scheduler that executes scheduled jobs (like cron, one-time tasks, and recurring workflows) across a cluster of workers. The system must ensure exactly-once execution, handle worker failures, support task dependencies (DAGs), and provide monitoring and retry capabilities.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Cron scheduling**: Support standard cron expressions for recurring tasks.
- **One-time tasks**: Schedule tasks for specific future execution times.
- **Task dependencies**: Define DAG-based workflows where tasks depend on other task completions.
- **Retry policy**: Configurable retry with exponential backoff, max attempts, and dead letter queue.
- **Worker management**: Register/deregister workers, health checks, graceful shutdown.
- **Task isolation**: Run tasks in isolated environments (containers, separate processes).
- **Monitoring**: Track task status, execution time, success/failure rates, worker utilization.

### Non-Functional Requirements
- **Exactly-once execution**: Tasks execute exactly once despite failures and retries.
- **Fault tolerance**: System continues operating when individual workers fail.
- **Scalability**: Handle 1M+ scheduled tasks and 10K+ concurrent workers.
- **Low latency**: Task dispatch to worker in < 100ms after scheduled time.

## Key Design Decisions
- **Leader-based scheduling**: One leader node assigns tasks; prevents duplicate execution.
- **Heartbeat mechanism**: Workers send heartbeats; leader detects failures and reassigns.
- **Idempotent tasks**: Task design ensures safe retry without side effects.
- **DAG execution**: Topological sort determines execution order; parallel independent tasks.

## Architecture

```
Scheduler Leader          Worker Pool              Task Store
      |                       |                        |
      |-- assign task ------>|                        |
      |                       |-- execute task ------->|
      |<-- heartbeat ---------|                        |
      |                       |-- result ------------->|
      |<-- task complete ------|                        |
      |                       |                        |
      |-- (worker fails)      |                        |
      |-- reassign task ----->| (new worker)           |
```

## Staff-Level Design Considerations

### Leader Election
- **ZooKeeper/Etcd**: Use distributed lock for leader election with automatic failover.
- **Database-based**: Use `SELECT ... FOR UPDATE` on a scheduler table for leader lock.
- **Staff insight**: Leader failover should take < 5 seconds. During failover, scheduled tasks may be delayed briefly. Design tasks to tolerate slight delays (e.g., a task scheduled for 10:00:00 running at 10:00:05 is acceptable).

### Exactly-Once Semantics
- **Idempotency keys**: Each task execution has a unique idempotency key stored in the task store.
- **Fencing tokens**: Leader assigns monotonically increasing tokens; workers reject stale tokens.
- **Staff insight**: True exactly-once is impossible in distributed systems. Achieve **effective exactly-once** by making tasks idempotent and using fencing tokens to prevent duplicate execution during leader failover.

### Worker Failure Handling
- **Heartbeat timeout**: Leader marks worker as failed after N missed heartbeats.
- **Task reassignment**: Failed worker's tasks are reassigned to available workers.
- **Graceful shutdown**: Worker completes current task before deregistering.
- **Staff insight**: Set heartbeat interval to **1/3 of task timeout**. If a task takes 60 seconds, heartbeat every 20 seconds. This ensures the leader detects failure quickly without excessive heartbeat traffic.

### DAG Execution
- **Topological sort**: Determine execution order; execute independent tasks in parallel.
- **State tracking**: Track each node's state (pending, running, completed, failed).
- **Staff insight**: For large DAGs (1000+ nodes), use **lazy evaluation** — only compute the next batch of ready tasks, not the entire DAG upfront. This reduces memory usage and allows dynamic DAG modification.

### Resource Management
- **Worker capacity**: Track CPU, memory, and custom resource limits per worker.
- **Task prioritization**: Priority queue for task assignment; high-priority tasks preempt low-priority.
- **Staff insight**: Use **bin packing** for task-to-worker assignment. Assign tasks to workers that have the most available resources, not just any available worker. This maximizes cluster utilization and reduces the number of active workers (cost savings).
