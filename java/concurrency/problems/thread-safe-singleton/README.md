# Thread-Safe Singleton

## Problem Statement

Design a thread-safe singleton pattern in Java that ensures exactly one instance is created, even under concurrent access, while balancing performance, lazy initialization, and serialization safety.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Single instance**: Exactly one instance of the class throughout the JVM lifecycle.
- **Lazy initialization**: Create the instance only when first accessed.
- **Thread safety**: No race conditions during instance creation.
- **Serialization safety**: Deserialization returns the existing singleton instance.
- **Reflection safety**: Prevent reflection from creating new instances.

### Non-Functional Requirements
- **Performance**: Minimal overhead on subsequent accesses after initialization.
- **Memory efficiency**: No unnecessary object creation.
- **Correctness**: Works correctly under high concurrency.

## Key Design Decisions
- **Bill Pugh (holder pattern)**: Uses inner class for lazy, thread-safe initialization without synchronization.
- **Enum singleton**: Most robust approach; prevents serialization and reflection attacks.
- **Double-checked locking**: Uses volatile + synchronized for lazy initialization with performance.

## Staff-Level Design Considerations

### Singleton Implementations Compared

| Approach | Thread-safe | Lazy | Performance | Reflection-safe | Serialization-safe |
|----------|-------------|------|-------------|-----------------|-------------------|
| Eager | ✓ | ✗ | O(1) | ✗ | ✗ |
| Synchronized | ✓ | ✓ | Slow (lock) | ✗ | ✗ |
| Double-checked | ✓ | ✓ | O(1) after init | ✗ | ✗ |
| Bill Pugh | ✓ | ✓ | O(1) | ✗ | ✗ |
| Enum | ✓ | ✗ | O(1) | ✓ | ✓ |

- **Staff insight**: The enum singleton is the most robust approach (effective Java Item 3). It's thread-safe, lazy (enum constants are loaded on first use), and immune to both serialization and reflection attacks. Use enum singleton unless you need a class that extends another class.

### Bill Pugh (Holder) Pattern
```java
public class Singleton {
    private Singleton() {}
    
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```
- **Staff insight**: The holder pattern is the best non-enum approach. The inner class is not loaded until `getInstance()` is called, ensuring lazy initialization. The JVM guarantees that class initialization is thread-safe, so no synchronization is needed.

### Double-Checked Locking
```java
public class Singleton {
    private static volatile Singleton instance;
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```
- **Staff insight**: The `volatile` keyword is essential. Without it, the JVM may reorder the instance assignment and constructor execution, causing another thread to see a partially constructed object. With `volatile`, the happens-before relationship ensures the instance is fully constructed before another thread sees it.

### Common Pitfalls
- **Missing volatile**: In double-checked locking, causes partially constructed objects.
- **Serialization**: Default deserialization creates a new instance; implement `readResolve()`.
- **Reflection**: `setAccessible(true)` bypasses private constructor; use enum or check in constructor.
- **Multiple classloaders**: Each classloader creates its own singleton; use a shared classloader.
- **Staff insight**: In modern Java applications, prefer dependency injection frameworks (Spring) over singletons. They manage lifecycle, testing, and configuration more flexibly. Use singletons only for true global state (e.g., logger, configuration).
