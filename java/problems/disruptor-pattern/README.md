# Disruptor Pattern (Lock-Free Ring Buffer)

## Problem Statement

Implement the Disruptor pattern — a high-performance lock-free ring buffer for inter-thread communication. The Disruptor eliminates cache line false sharing, uses pre-allocated memory, and achieves millions of operations per second by avoiding locks and garbage collection.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Ring buffer**: Fixed-size circular buffer for event storage.
- **Sequence numbers**: Monotonic sequence for ordering and progress tracking.
- **Producer**: Publish events to the ring buffer without locks.
- **Consumer**: Process events in order with dependency support.
- **Wait strategy**: Configurable strategy for consumers waiting for events.
- **Event factories**: Pre-allocate event objects to avoid GC.

### Non-Functional Requirements
- **Throughput**: 1M+ operations per second on a single core.
- **Latency**: P99 latency < 1 microsecond per event.
- **No locks**: Use CAS operations instead of synchronized blocks.
- **No GC**: Pre-allocated buffer avoids allocation during processing.

## Key Design Decisions
- **CAS sequence**: AtomicLong with CAS for lock-free sequence management.
- **Cache line padding**: Prevent false sharing between sequence and data.
- **Wait strategies**: Busy-spin, yielding, sleeping, or blocking based on latency needs.
- **Pre-allocation**: Ring buffer and events allocated once, reused indefinitely.

## Implementation

```java
public class Disruptor<E> {
    private final E[] ringBuffer;
    private final AtomicLong producerSequence = new AtomicLong(-1);
    private final AtomicLong consumerSequence = new AtomicLong(-1);
    private final int bufferSize;

    public Disruptor(int bufferSize, EventFactory<E> factory) {
        this.bufferSize = bufferSize;
        this.ringBuffer = new Event[bufferSize];
        for (int i = 0; i < bufferSize; i++) {
            ringBuffer[i] = factory.create();
        }
    }

    public long publish(E event) {
        long sequence;
        do {
            sequence = producerSequence.get();
        } while (!producerSequence.compareAndSet(sequence, sequence + 1));

        int index = (int) (sequence % bufferSize);
        ringBuffer[index] = event;
        return sequence;
    }

    public E poll() {
        long sequence = consumerSequence.get();
        if (sequence >= producerSequence.get()) {
            return null; // No events available
        }
        consumerSequence.incrementAndGet();
        int index = (int) (sequence % bufferSize);
        return ringBuffer[index];
    }
}
```

## Staff-Level Design Considerations

### Cache Line False Sharing
- **Problem**: Producer and consumer sequences on same cache line cause invalidation.
- **Solution**: Pad sequences to separate cache lines (128 bytes).
- **Staff insight**: Use `@Contended` (Java 8+) or manual padding with unused long fields. False sharing can reduce throughput by 10x. The LMAX Disruptor benchmarks show 1M ops/sec with padding vs 100K ops/sec without.

### Wait Strategies
- **Busy-spin**: Tight loop checking sequence — lowest latency, highest CPU.
- **Yielding**: Thread.yield() in loop — balances latency and CPU.
- **Blocking**: Wait/notify — lowest CPU, highest latency.
- **Staff insight**: Use **busy-spin for trading systems** (latency < 1μs matters). Use **yielding for general-purpose** systems. Use **blocking for batch processing** (throughput matters, not latency). Make wait strategy configurable per use case.

### When to Use Disruptor
- **High-frequency trading**: Microsecond latency requirements.
- **Log processing**: Log4j2 uses Disruptor for async logging.
- **Event sourcing**: High-throughput event ingestion.
- **Staff insight**: **Don't use Disruptor for general-purpose queues**. It's complex and only beneficial when you need >1M ops/sec with <1μs latency. For most use cases, `ArrayBlockingQueue` or `LinkedBlockingQueue` is sufficient and simpler. Use Disruptor only when profiling shows queue contention as the bottleneck.

### Memory Barriers
- **Visibility**: CAS operations provide acquire-release semantics.
- **Ordering**: Ensure event is written before sequence is incremented.
- **Staff insight**: Use `VarHandle` (Java 9+) with `SET_PLAIN` for data writes and `compareAndSet` with full fence for sequence. This ensures the event is visible to consumers before the sequence advances, without expensive full memory barriers on every write.
