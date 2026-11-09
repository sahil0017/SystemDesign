# Double-Checked Locking

## Problem Statement

Implement a thread-safe singleton and lazy initialization pattern using double-checked locking in Java. Understand the memory visibility issues with this pattern and how to correctly implement it using the `volatile` keyword.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Lazy initialization**: Instance is created only when first accessed.
- **Thread safety**: Only one instance is created even under concurrent access.
- **Performance**: Avoid synchronization overhead after initialization.
- **Memory safety**: Ensure the instance is fully constructed before other threads see it.

### Non-Functional Requirements
- **Lock-free reads**: After initialization, reads should not acquire any lock.
- **JVM compatibility**: Work correctly on Java 5+ with the JSR-133 memory model.

## Key Design Decisions
- **volatile keyword**: Prevents instruction reordering during construction.
- **synchronized block**: Only acquired when instance is null.
- **Local variable**: Read instance into local variable to avoid multiple memory reads.

## Implementation

```java
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {} // Prevent direct instantiation

    public static Singleton getInstance() {
        if (instance == null) {                    // First check (no lock)
            synchronized (Singleton.class) {       // Acquire lock
                if (instance == null) {            // Second check (with lock)
                    instance = new Singleton();    // Initialize
                }
            }
        }
        return instance;
        }
}
```

## Staff-Level Design Considerations

### Why volatile is Required
- **Instruction reordering**: Without `volatile`, the JVM may reorder `new Singleton()` into: (1) allocate memory, (2) assign reference, (3) call constructor. Another thread can see the non-null reference before construction completes.
- **Memory visibility**: `volatile` ensures the write to `instance` happens-before any subsequent read.
- **Staff insight**: In Java 5+, `volatile` prevents both reordering and ensures visibility. In Java 1.5-, double-checked locking was broken even with `volatile`. Always use Java 5+ or prefer alternative patterns.

### Alternatives to Double-Checked Locking
- **Eager initialization**: `private static final Singleton INSTANCE = new Singleton();` — simplest, thread-safe by class loading.
- **Bill Pugh (holder pattern)**: Use inner class for lazy initialization — thread-safe by JLS guarantee.
- **Enum singleton**: `public enum Singleton { INSTANCE; }` — serialization-safe, reflection-safe.
- **Staff insight**: Prefer **enum singleton** for simple cases — it's the most robust (Effective Java, Item 3). Use **holder pattern** for lazy initialization with complex constructors. Use double-checked locking only when you need lazy initialization of non-static fields.

### Bill Pugh Holder Pattern

```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE; // Lazy: Holder class loads on first access
    }
}
```

- **Thread-safe**: Class loading is synchronized by the JVM.
- **Lazy**: `Holder` class loads only when `getInstance()` is called.
- **No volatile needed**: `final` field ensures safe publication.
- **Staff insight**: This is the **preferred lazy singleton pattern** — no volatile, no synchronized, no double-check. The JVM guarantees that `static final` fields are safely published after class initialization completes.
