# Event Loop Design

## Problem Statement

Design an event loop that processes I/O events and tasks on a single thread, enabling high-throughput non-blocking I/O without thread contention, similar to Netty's NioEventLoop or Node.js's event loop.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Event selection**: Use Selector to multiplex multiple channels on a single thread.
- **Task queue**: Process non-I/O tasks alongside I/O events.
- **Event handlers**: Register callbacks for read, write, connect, and accept events.
- **Scheduled tasks**: Schedule tasks to run after a delay or at fixed intervals.
- **Shutdown**: Graceful shutdown with pending task completion.

### Non-Functional Requirements
- **Single-threaded**: All events for a loop are handled by one thread; no synchronization needed.
- **Throughput**: Handle 10K+ connections per event loop.
- **Latency**: Sub-millisecond event processing time.

## Key Design Decisions
- **Selector-based**: Java NIO Selector for multiplexing I/O events.
- **Task queue**: `LinkedBlockingQueue` for non-I/O tasks submitted to the event loop.
- **Event loop thread**: Single thread runs the loop; never blocks on CPU-intensive work.
- **Key attachment**: Attach handler objects to SelectorKeys for event routing.

## Staff-Level Design Considerations

### Event Loop Architecture
- **Select phase**: Block on `selector.select(timeout)` waiting for I/O events.
- **I/O phase**: Process selected keys (read, write, accept, connect).
- **Task phase**: Process pending tasks from the task queue.
- **Staff insight**: The event loop's single-threaded design is its greatest strength. Since all events for a given connection are handled by the same thread, you never need synchronization for per-connection state. This eliminates lock contention and provides excellent cache locality.

### Task Queue Management
- **Immediate tasks**: `execute(Runnable)` adds to the head of the queue; processed in the next iteration.
- **Scheduled tasks**: `schedule(Runnable, delay)` adds to a delayed queue; moved to task queue when due.
- **External tasks**: Tasks submitted from outside the event loop thread go to a separate queue.
- **Staff insight**: Never submit a blocking task to an event loop. If you must call a blocking API (DB query, HTTP call), submit it to a separate worker thread pool. The event loop should only handle non-blocking I/O and fast CPU tasks.

### Selector Optimization
- **Re-registration**: When a channel's interest ops change, update the SelectorKey.
- **Empty select**: Handle spurious wakeups where select() returns 0 with no events.
- **Cancel cleanup**: Call `selector.selectNow()` to cancel cancelled keys and prevent memory leaks.
- **Staff insight**: The "selector wakeup bug" is a known issue in Java NIO where select() returns immediately without events, causing 100% CPU usage. Always add a small timeout (e.g., 1ms) to select() and check for empty selections. If you see many empty selects in a row, increase the timeout.

### Common Pitfalls
- **Blocking the loop**: Any blocking call stalls all connections on that loop.
- **Too many connections per loop**: One event loop per CPU core is the standard model.
- **Task queue growth**: Unbounded task queue causes memory growth; use bounded queue with backpressure.
- **Staff insight**: The event loop model is the foundation of all high-performance I/O servers (Netty, Node.js, Nginx). Understanding it is essential for building scalable network services. The key rule is: never block the event loop thread.
