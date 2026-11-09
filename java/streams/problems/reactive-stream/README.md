# Reactive Stream Design

## Problem Statement

Design a reactive stream processing system that handles backpressure, error propagation, and non-blocking data flow for real-time event processing in Java applications.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Backpressure**: Downstream controls the rate of upstream data production.
- **Non-blocking**: All operations are non-blocking; no thread waiting.
- **Error handling**: Propagate errors through the stream without crashing.
- **Operators**: Map, filter, flatMap, reduce, window, and buffer operators.
- **Subscription**: Reactive subscription model with onSubscribe, onNext, onError, onComplete.

### Non-Functional Requirements
- **Resilience**: Handle slow consumers without dropping data or OOM.
- **Scalability**: Process millions of events per second with minimal resources.
- **Composability**: Chain operators declaratively for complex pipelines.

## Key Design Decisions
- **Reactive Streams spec**: Implement the 4-interface spec (Publisher, Subscriber, Subscription, Processor).
- **Project Reactor**: Use Reactor (Spring WebFlux) or RxJava for production reactive streams.
- **Backpressure strategy**: Bounded elastic buffer; drop oldest when full.
- **Virtual threads**: Java 21+ virtual threads as an alternative to reactive programming.

## Staff-Level Design Considerations

### Reactive Streams Specification
- **Publisher**: Emits data items; manages subscriber subscriptions.
- **Subscriber**: Receives data; implements onSubscribe, onNext, onError, onComplete.
- **Subscription**: Controls the flow; request(n) for backpressure, cancel() to stop.
- **Processor**: Both Publisher and Subscriber; acts as a bridge or operator.
- **Staff insight**: The key to reactive streams is backpressure. The downstream subscriber calls `subscription.request(n)` to tell the upstream how many items it can handle. This prevents fast producers from overwhelming slow consumers.

### Backpressure Strategies
- **Bounded buffer**: Queue with max size; blocks or drops when full.
- **Drop latest**: Drop new items when buffer is full; keep old data.
- **Drop oldest**: Drop old items when buffer is full; keep new data.
- **Error**: Signal error when buffer is full; stops the stream.
- **Latest**: Keep only the latest item; discard intermediate items.
- **Staff insight**: Choose backpressure strategy based on data semantics. For metrics, drop oldest (latest value matters most). For financial transactions, use bounded buffer (no data loss). For chat messages, drop oldest (latest message matters most).

### Reactive vs Virtual Threads
- **Reactive streams**: Non-blocking; complex code; steep learning curve; best for high I/O concurrency.
- **Virtual threads**: Blocking code style; simple; Java 21+; best for moderate I/O concurrency.
- **When to use reactive**: When you need 10K+ concurrent connections with minimal threads (e.g., WebSocket server).
- **When to use virtual threads**: When you want simple blocking code with good throughput (e.g., REST API).
- **Staff insight**: Java 21 virtual threads have reduced the need for reactive programming in many scenarios. Virtual threads let you write simple blocking code that scales to 100K+ concurrent connections. Use reactive streams only when you need the fine-grained backpressure control or are already invested in the reactive ecosystem (Spring WebFlux, Project Reactor).

### Common Pitfalls
- **Blocking in reactive chain**: Calling a blocking method in a reactive operator defeats non-blocking design.
- **Ignoring backpressure**: Not implementing request(n) properly causes OOM under high load.
- **Error swallowing**: Not handling onError crashes the stream silently.
- **Staff insight**: The #1 reactive programming mistake is calling blocking code (DB query, HTTP call) inside a reactive operator. This blocks the event loop thread and defeats the purpose of reactive programming. Use non-blocking alternatives or offload to a bounded elastic scheduler.
