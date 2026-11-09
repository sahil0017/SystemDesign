# Exchanger (Two-Thread Data Swap)

## Problem Statement

Implement and understand Java's `Exchanger` — a synchronization point where two threads can exchange objects. One thread's output becomes the other thread's input, enabling efficient pipeline processing, buffer swapping, and producer-consumer patterns with bidirectional data flow.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Exchange**: Two threads swap objects at a synchronization point.
- **Blocking**: Thread blocks until partner arrives with data.
- **Timeout**: Exchange with timeout to prevent indefinite blocking.
- **Type safety**: Generic exchange of specific object types.

### Non-Functional Requirements
- **Fairness**: Threads are served in FIFO order.
- **No data copying**: Exchange references, not data copies.
- **Low latency**: Exchange completes in microseconds.

## Key Design Decisions
- **Meeting point**: Exchanger is a single synchronization point for pairs.
- **Memory barrier**: Exchange provides happens-before guarantee for swapped data.
- **Buffer swapping**: Ideal for double-buffering patterns.

## Implementation

```java
public class BufferExchanger {
    private final Exchanger<List<String>> exchanger = new Exchanger<>();
    private final int bufferSize = 1000;

    // Producer: fills buffer and exchanges with consumer
    public void producer() {
        List<String> workingBuffer = new ArrayList<>(bufferSize);

        while (!Thread.currentThread().isInterrupted()) {
            // Fill buffer with data
            for (int i = 0; i < bufferSize; i++) {
                workingBuffer.add(generateData());
            }

            try {
                // Exchange full buffer for empty buffer
                workingBuffer = exchanger.exchange(workingBuffer);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    // Consumer: processes buffer and exchanges back to producer
    public void consumer() {
        List<String> workingBuffer = new ArrayList<>(bufferSize);

        while (!Thread.currentThread().isInterrupted()) {
            try {
                // Exchange empty buffer for full buffer
                workingBuffer = exchanger.exchange(workingBuffer);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }

            // Process data
            for (String data : workingBuffer) {
                processData(data);
            }

            // Clear buffer for reuse
            workingBuffer.clear();
        }
    }
}
```

## Staff-Level Design Considerations

### Exchanger Use Cases
- **Buffer swapping**: Producer fills buffer, consumer processes — swap without copying.
- **Pipeline processing**: Stage 1 output becomes Stage 2 input and vice versa.
- **Connection pooling**: Exchange idle connections for active connections.
- **Staff insight**: Exchanger is ideal for **double-buffering** patterns. Instead of copying data between producer and consumer, swap the buffer references. This is zero-copy and eliminates allocation overhead. Use pre-allocated buffers that are cleared and reused.

### Exchanger vs BlockingQueue
- **BlockingQueue**: One-way data flow; producer puts, consumer takes.
- **Exchanger**: Two-way data flow; both threads give and receive simultaneously.
- **Staff insight**: Use **BlockingQueue** for standard producer-consumer. Use **Exchanger** when both threads need to swap data (e.g., producer gives data and gets an empty buffer back). Exchanger is more efficient for bidirectional exchange because it's a single atomic operation instead of two queue operations.

### Performance Considerations
- **Zero-copy**: Exchange references, not data — O(1) operation.
- **Buffer reuse**: Pre-allocate buffers; clear and reuse — no GC pressure.
- **Staff insight**: The key benefit of Exchanger is **eliminating buffer allocation**. In a BlockingQueue pattern, each batch creates a new collection. With Exchanger, two pre-allocated buffers are swapped indefinitely. For high-throughput pipelines (1M+ records/sec), this eliminates GC pressure from buffer allocation — a common bottleneck in streaming systems.

### Timeout Handling
- **exchange(V, long timeout, TimeUnit)**: Prevents indefinite blocking.
- **Staff insight**: Always use **timeout-based exchange** in production. If the partner thread crashes, the waiting thread hangs forever with blocking exchange. With timeout, the thread can detect partner failure, log a warning, and decide whether to retry or shut down. Set timeout to 2-3x the expected processing time.
