# Scheduling & Task Execution

Distributed systems for executing scheduled jobs, managing task dependencies, and coordinating recurring workflows across a cluster of workers.

## Problems (2)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Distributed Scheduler](distributed-scheduler/) | Cron-like scheduler with DAG workflows and worker management | Cron, DAG workflows, worker management, exactly-once |
| [Distributed Task Scheduler](distributed-task-scheduler/) | Airflow-like task orchestration with retries and monitoring | DAG execution, idempotency, leader-based scheduling, retries |

## When to Use

- **Distributed Scheduler**: When you need reliable cron-like job execution across multiple workers (e.g., nightly reports, data cleanup, cache warming, bill generation).
- **Distributed Task Scheduler**: When you need complex workflow orchestration with dependencies between tasks (e.g., ETL pipelines, ML training workflows, multi-step data processing).

## Cross-References

- **Topics**: [Idempotency](../../idempotency/) for safe task retries, [Saga Pattern](../../saga-pattern/) for multi-step workflows
- **Related**: [Leader Election](../coordination/leader-election/) ensures only one scheduler coordinator runs at a time. [Distributed Tracing](../observability/distributed-tracing/) tracks task execution flow.
