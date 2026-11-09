# Actor Model Implementation

## Problem Statement

Implement the Actor Model concurrency pattern in Java where actors are isolated entities that communicate exclusively through asynchronous message passing. Each actor processes one message at a time, eliminating the need for explicit locks and preventing race conditions.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Actor lifecycle**: Create, start, stop, and supervise actors.
- **Message passing**: Send asynchronous messages between actors.
- **Mailbox**: Each actor has a FIFO mailbox for incoming messages.
- **Supervision**: Parent actors monitor children; define restart strategies.
- **Actor refs**: Actors communicate via references, not direct object access.
- **Dynamic creation**: Actors can create child actors at runtime.

### Non-Functional Requirements
- **No shared state**: Actors never share mutable state with other actors.
- **Message ordering**: Messages from one sender to one receiver are processed in order.
- **Fault isolation**: Actor failure doesn't affect other actors.

## Key Design Decisions
- **Single-threaded processing**: Each actor processes messages sequentially on one thread.
- **Thread pool**: Actor system uses a shared thread pool for message processing.
- **Supervision hierarchy**: Parent-child tree with defined restart strategies.
- **Immutable messages**: Messages are immutable value objects.

## Implementation

```java
public abstract class Actor {
    private final Mailbox mailbox = new Mailbox();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    public void tell(Object message) {
        mailbox.send(message);
        executor.submit(this::processMessages);
    }

    private void processMessages() {
        while (!mailbox.isEmpty()) {
            Object message = mailbox.receive();
            onReceive(message);
        }
    }

    protected abstract void onReceive(Object message);
}
```

## Staff-Level Design Considerations

### Actor vs Thread
- **One actor per thread**: Simple but doesn't scale — threads are expensive.
- **Many actors per thread pool**: Efficient — actors are lightweight objects.
- **Staff insight**: Use a **shared thread pool** for all actors. Each actor gets a single-threaded executor from the pool. Akka uses this approach: thousands of actors share a small thread pool. Actors are scheduled like tasks, not bound to dedicated threads.

### Message Design
- **Immutable messages**: Messages are value objects with no mutable state.
- **No response**: Actor model is fire-and-forget; use ask pattern for requests.
- **Staff insight**: Design messages as **records** (Java 16+) — immutable by default. Never pass mutable objects as messages. If you need a response, use the **ask pattern** (send message + return CompletableFuture) or send a reply-to actor ref.

### Supervision Strategies
- **Restart**: Restart failed actor with fresh state — default strategy.
- **Stop**: Stop failed actor and notify parent — for unrecoverable failures.
- **Escalate**: Let parent decide — for complex failure scenarios.
- **Staff insight**: Use **"let it crash" philosophy** — don't catch exceptions in actors; let them fail and let supervision handle recovery. Define restart limits (e.g., 10 restarts in 60 seconds) to prevent restart loops. This is how Erlang/Elixir and Akka achieve fault tolerance.

### When to Use Actors
- **Event-driven systems**: Chat servers, game servers, IoT platforms.
- **Concurrent state machines**: Each actor is a state machine processing events.
- **Staff insight**: Actors excel at **concurrent stateful processing** where each entity has independent state. Don't use actors for simple CRUD — use REST + DB. Use actors when you need concurrent state management without locks (e.g., game state, chat sessions, order processing).
