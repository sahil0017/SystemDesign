# Effective Java by Joshua Bloch (3rd Edition)

## Summary

90 best practices (items) for writing production-quality Java code. Covers language features, design patterns, concurrency, serialization, and more. Widely considered the most important Java book ever written.

## Key Items

### Generics and Type Safety
- Item 31: Don't use raw types
- Item 32: Eliminate unchecked warnings
- Item 33: Prefer lists to arrays
- Item 34: Prefer generic types
- Item 35: Exploit wildcards for API flexibility

### Lambdas and Streams
- Item 39: Prefer lambdas to anonymous classes
- Item 40: Prefer method references to lambdas
- Item 41: Favor the use of standard functional interfaces
- Item 42: Use streams appropriately

### Concurrency
- Item 86: Synchronize access to shared mutable data
- Item 87: Avoid excessive synchronization
- Item 88: Prefer executors and tasks to threads
- Item 89: Prefer concurrency utilities to wait and notify
- Item 90: Document thread safety

## Key Takeaways

- **Immutability**: Prefer immutable classes — they're simpler, safer, and more reusable
- **Builder pattern**: Use builders for classes with many constructor parameters
- **Enum over int constants**: Type-safe, extensible, and self-documenting
- **Try-with-resources**: Always use try-with-resources for resource management
- **Concurrency**: Use `java.util.concurrent` utilities instead of raw threads and wait/notify

## Why Read This Book

- The Java bible — every Java engineer should read it cover to cover
- Each item is self-contained — read selectively or cover to cover
- Updated for Java 8-17 features (lambdas, streams, var, records)

## Related Problems in This Repository

- [LLD - Design Patterns](../../lld/fundamentals/design-patterns.md)
- [Java - Concurrency Problems](../../java/problems/)
- [Blogs - Java Memory Model](../../blogs-articles/java-concurrency/java-memory-model.md)
