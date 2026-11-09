# Async I/O Server Design

## Problem Statement

Design a high-throughput non-blocking I/O server using Java NIO (Netty) that handles thousands of concurrent connections with minimal thread usage through event-driven architecture.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Non-blocking I/O**: Use Selector/NIO for multiplexing connections across few threads.
- **Event loop**: Single-threaded event loop per CPU core for handling I/O events.
- **Pipeline**: Chain handlers for decoding, business logic, and encoding.
- **Backpressure**: Control flow when downstream can't keep up with incoming data.
- **Connection management**: Handle connect, read, write, and close events.

### Non-Functional Requirements
- **Throughput**: Handle 10K+ concurrent connections with minimal threads.
- **Latency**: Sub-millisecond processing time per message.
- **Scalability**: Scale with CPU cores; add more event loops for more cores.

## Key Design Decisions
- **Netty framework**: Production-ready NIO framework with event loop group and pipeline.
- **Event loop model**: One event loop per CPU core; each connection assigned to one loop.
- **Zero-copy**: Use `CompositeBuffer` and `FileRegion` to avoid memory copies.
- **Thread model**: Boss group accepts connections; worker group handles I/O.

## Staff-Level Design Considerations

### Netty Architecture
- **BossEventLoopGroup**: Accepts incoming connections; typically 1 thread.
- **WorkerEventLoopGroup**: Handles I/O for accepted connections; N threads (one per core).
- **ChannelPipeline**: Chain of handlers that process inbound/outbound events.
- **ByteBuf**: Reference-counted buffer; must be released to avoid memory leaks.
- **Staff insight**: Netty's event loop model ensures that all I/O for a given connection is handled by the same thread. This eliminates synchronization for per-connection state and provides excellent cache locality.

### Thread Model
- **I/O threads**: Event loop threads handle only I/O; never block on CPU-intensive work.
- **Worker threads**: Offload CPU-intensive processing to a separate thread pool.
- **Rule**: Never block an event loop thread. If you must call a blocking API, submit to a worker pool.
- **Staff insight**: The #1 Netty mistake is blocking the event loop. If a handler calls a blocking method (DB query, HTTP call, sleep), it blocks all connections assigned to that event loop. Always offload blocking work to a separate thread pool.

### Zero-Copy Techniques
- **CompositeBuffer**: Merge multiple ByteBufs without copying data.
- **FileRegion**: Directly transfer file content to socket using `sendfile()`.
- **ByteBuf slicing**: Create a view of a buffer without copying.
- **Staff insight**: Zero-copy is critical for high-throughput servers. When serving static files, use `FileRegion` to let the OS transfer data directly from disk to network without copying through user space.

### Common Pitfalls
- **Blocking event loop**: Any blocking call in a handler stalls all connections on that loop.
- **ByteBuf leak**: Forgetting to release reference-counted buffers; causes direct memory leak.
- **Thread pool starvation**: Offloading too much work to a small thread pool; tasks queue up.
- **Staff insight**: Always use Netty's `ReferenceCountUtil.release()` in a finally block or use try-with-resources. Direct memory leaks from unreleased ByteBufs are hard to detect because they don't show up in heap dumps.
