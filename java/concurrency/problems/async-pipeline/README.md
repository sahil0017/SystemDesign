# Async Pipeline Design

## Problem Statement

Design an asynchronous pipeline that chains multiple stages of processing (e.g., fetch → transform → validate → store) where each stage runs concurrently on its own thread pool, enabling high-throughput data processing with backpressure.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Pipeline stages**: Chain multiple processing stages (map, filter, flatMap, reduce).
- **Per-stage executor**: Each stage runs on its own configurable thread pool.
- **Backpressure**: Downstream stages control the rate of upstream processing.
- **Error handling**: Propagate errors through the pipeline; support retry and fallback.
- **Completion**: Signal when all items have been processed through all stages.

### Non-Functional Requirements
- **Throughput**: Maximize processing rate by parallelizing stages.
- **Memory efficiency**: Bounded buffers between stages to prevent OOM.
- **Resilience**: Handle stage failures without stopping the entire pipeline.

## Key Design Decisions
- **BlockingQueue between stages**: Each stage reads from and writes to bounded queues.
- **CompletableFuture chaining**: Compose stages using thenApplyAsync with custom executors.
- **Backpressure via bounded queues**: When downstream queue is full, upstream blocks.
- **Graceful shutdown**: Signal end-of-stream and wait for all stages to complete.

## Staff-Level Design Considerations

### Pipeline Architecture
```
[Source] → [Queue1] → [Stage1] → [Queue2] → [Stage2] → [Queue3] → [Sink]
```
- Each stage is a consumer-producer: it reads from input queue, processes, and writes to output queue.
- Bounded queues between stages provide natural backpressure.
- **Staff insight**: This is the same pattern used in Kafka streams, Apache Flink, and Unix pipes. Bounded queues between stages prevent fast producers from overwhelming slow consumers.

### CompletableFuture Pipeline
```java
CompletableFuture<Result> pipeline = CompletableFuture
    .supplyAsync(() -> fetch(data), fetchExecutor)
    .thenApplyAsync(item -> transform(item), transformExecutor)
    .thenApplyAsync(item -> validate(item), validateExecutor)
    .thenAcceptAsync(item -> store(item), storeExecutor);
```
- **Staff insight**: Each `thenApplyAsync` runs on its own executor, enabling true parallelism. If all stages share the same executor, they compete for threads. Use separate executors for IO-bound and CPU-bound stages.

### Backpressure Strategies
- **Bounded queue**: Queue with max size; upstream blocks when full. Simple and effective.
- **Drop policy**: Drop oldest or newest items when queue is full. Prevents blocking but loses data.
- **Rate limiting**: Throttle upstream to match downstream processing rate.
- **Staff insight**: Bounded queues are the simplest and most effective backpressure mechanism. Size them based on the slowest stage's processing rate. A queue that's too large delays backpressure signaling; one that's too small causes unnecessary blocking.

### Common Pitfalls
- **Unbounded queues**: Between stages, causes OOM when downstream is slow.
- **Shared executor**: All stages compete for the same thread pool; IO-bound stages starve CPU-bound ones.
- **No error handling**: One failed item stops the entire pipeline.
- **Staff insight**: Always use bounded queues between pipeline stages. The queue size should be large enough to absorb short bursts but small enough to trigger backpressure quickly. A good starting point is 100-1000 items per queue, tuned based on stage processing rates.
