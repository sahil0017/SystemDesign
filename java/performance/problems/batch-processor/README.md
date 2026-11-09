# Batch Processing Design

## Problem Statement

Design a batch processing system that processes large datasets efficiently in chunks, balancing throughput, memory usage, and error handling for ETL (Extract-Transform-Load) pipelines.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Chunk processing**: Split large datasets into manageable batches.
- **Parallel execution**: Process multiple batches concurrently using thread pools.
- **Error handling**: Retry failed batches; skip or log irrecoverable errors.
- **Progress tracking**: Monitor batch completion percentage and throughput.
- **Checkpointing**: Save progress to resume from last checkpoint on failure.

### Non-Functional Requirements
- **Memory efficiency**: Process data in streams/chunks; don't load entire dataset.
- **Throughput**: Maximize processing rate with parallel execution.
- **Fault tolerance**: Resume from last checkpoint after failure.

## Key Design Decisions
- **Chunk size**: Balance between memory usage and processing overhead.
- **Thread pool**: Size based on CPU cores for CPU-bound work; IO-bound formula for IO work.
- **CompletableFuture**: Compose async batch processing with error handling.
- **Checkpoint file**: Persist processed record count for resume capability.

## Staff-Level Design Considerations

### Chunk Size Optimization
- **Too small**: High overhead per chunk; more I/O operations; lower throughput.
- **Too large**: High memory usage; longer GC pauses; harder to parallelize.
- **Sweet spot**: 1000-10000 records per chunk for most workloads.
- **Staff insight**: Profile with different chunk sizes. The optimal chunk size depends on record size, available memory, and processing complexity. Start with 5000 records and adjust based on memory and throughput metrics.

### Parallel Processing Strategy
```java
ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
List<CompletableFuture<Void>> futures = batches.stream()
    .map(batch -> CompletableFuture.runAsync(() -> process(batch), executor))
    .collect(Collectors.toList());
CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
```
- **Staff insight**: For CPU-bound processing, use N threads (number of cores). For IO-bound processing, use N × (1 + W/C) threads. Use `CompletableFuture.allOf()` to wait for all batches to complete.

### Error Handling Patterns
- **Retry with backoff**: Retry failed batches with exponential backoff and jitter.
- **Dead letter queue**: Move irrecoverable records to a separate queue for manual processing.
- **Partial success**: Continue processing other batches when one fails.
- **Checkpoint**: Save progress after each successful batch; resume from last checkpoint.
- **Staff insight**: Never fail the entire batch job because of one bad record. Use a dead letter queue pattern — process good records, log bad ones, and continue. This ensures maximum data throughput even with dirty input.

### Common Pitfalls
- **Loading all data**: Reading entire file into memory causes OOM for large files.
- **No checkpointing**: Restarting from scratch after failure wastes time and resources.
- **Thread pool too large**: Exceeds available resources; context switching overhead.
- **Staff insight**: Always use streaming APIs (BufferedReader, InputStream) instead of loading entire files into memory. For files, process line by line or in fixed-size chunks. For databases, use cursor-based pagination or keyset pagination.
