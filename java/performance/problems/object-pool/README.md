# Object Pool Design

## Problem Statement

Design an object pool that reuses expensive-to-create objects (e.g., StringBuilder, ByteBuffer, database result sets) to reduce allocation overhead and GC pressure in high-throughput applications.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Borrow/Return**: Acquire an object from the pool and return it when done.
- **Factory**: Create new objects when the pool is empty.
- **Validation**: Test object state before handing it out.
- **Eviction**: Remove idle objects to free memory.
- **Thread safety**: Multiple threads can borrow/return concurrently.

### Non-Functional Requirements
- **Performance**: Minimal overhead on borrow/return; faster than new object creation.
- **Memory efficiency**: Don't hold more objects than needed.
- **Correctness**: Returned objects are reset to clean state.

## Key Design Decisions
- **Blocking queue**: Store available objects in a bounded `LinkedBlockingQueue`.
- **Lazy creation**: Create objects on demand; don't pre-populate the pool.
- **Object validation**: Check object state before reuse; discard corrupted objects.
- **Soft references**: Use `SoftReference` for pool storage to allow GC under memory pressure.

## Staff-Level Design Considerations

### When to Use Object Pooling
- **Expensive creation**: Object construction involves I/O, network calls, or complex computation.
- **High allocation rate**: Thousands of objects per second; pooling reduces GC pressure.
- **Large objects**: ByteBuffer, large arrays; pooling reduces allocation and GC overhead.
- **Staff insight**: Don't pool cheap objects like String or Integer. The pool overhead (synchronization, queue management) exceeds the cost of creating a new object. Pool only when object creation is measurably expensive.

### Pool Design Patterns
- **Fixed pool**: Pre-create N objects; borrow/return from fixed set. Simple but wastes memory if unused.
- **Bounded pool**: Max N objects; create on demand up to limit. Best balance of performance and memory.
- **Unbounded pool**: Create objects on demand; cache for reuse. Risk of memory growth under high load.
- **Staff insight**: Always use a bounded pool. An unbounded pool defeats the purpose — it can grow indefinitely and cause OOM, just like not pooling at all.

### Common Poolable Objects
- **ByteBuffer**: Direct byte buffers for NIO; expensive to allocate and deallocate.
- **StringBuilder**: Reuse for string concatenation in hot paths.
- **HTTP client**: Apache HttpClient or OkHttp connections; reuse to avoid TCP handshake.
- **Database connections**: Managed by connection pool (HikariCP); don't implement manually.
- **ThreadLocal pooling**: Each thread has its own pool; eliminates synchronization overhead.
- **Staff insight**: ThreadLocal pooling is the highest-performance option. Each thread has its own pool, so there's no synchronization. This is how Netty and other high-performance frameworks pool objects.

### Common Pitfalls
- **State leakage**: Returned object retains state from previous use; always reset objects.
- **Pool exhaustion**: All objects borrowed; threads block. Set appropriate pool size.
- **Memory waste**: Pool holds objects that are never used; use idle eviction.
- **Staff insight**: The #1 object pool bug is state leakage. When an object is returned to the pool, it must be reset to a clean state. Otherwise, the next borrower sees stale data from the previous use. Always implement a `reset()` method and call it on return.
