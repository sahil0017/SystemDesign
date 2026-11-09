# AtomicReferenceFieldUpdater

## Problem Statement

Design and implement a lock-free field updater using `AtomicReferenceFieldUpdater` that allows atomic updates to non-volatile, non-final fields of an object without synchronizing the entire object.

**Reference**: [AlgoMaster](https://algomaster.io/), [Java Concurrency in Practice](https://www.oreilly.com/library/view/java-concurrency-in-practice/9780595279092/)

## Requirements

### Functional Requirements
- **Atomic field update**: Update a specific field atomically using CAS (Compare-And-Swap).
- **Compare-and-set**: `compareAndSet(expected, update)` returns true if field was updated.
- **Get and set**: `get()`, `set()`, `getAndSet()` operations on the field.
- **Lazy set**: `lazySet()` for delayed visibility (write-buffering optimization).
- **Field access via reflection**: Use `newUpdater()` to create updater for a specific field.

### Non-Functional Requirements
- **Lock-free**: No synchronization; uses CAS instructions.
- **Performance**: Minimal overhead compared to direct field access.
- **Thread safety**: All operations are atomic and visible across threads.

## Key Design Decisions
- **Reflection-based**: Uses `sun.misc.Unsafe` or `VarHandle` (Java 9+) for field access.
- **Field constraints**: Target field must be `volatile`, non-static (for AtomicReferenceFieldUpdater), and non-final.
- **CAS loop**: Retry on failure; handles ABA problem via reference identity.

## Staff-Level Design Considerations

### When to Use
- **Partial object update**: When only one field needs atomic update, not the whole object.
- **Performance**: Avoids synchronizing the entire object; finer-grained than `synchronized`.
- **Staff insight**: `AtomicReferenceFieldUpdater` is useful when you can't replace the entire object reference but need atomic field updates. Common in cache entry updates, counter fields, and state machines.

### Alternatives
- **Volatile field**: Simpler but no CAS; only guarantees visibility.
- **AtomicReference**: Replace the entire object; more expensive for large objects.
- **synchronized**: Coarser-grained; blocks other threads.
- **Staff insight**: Prefer `AtomicReferenceFieldUpdater` when you need CAS on a field within a shared object. For Java 9+, consider `VarHandle` which provides a more flexible API.

### Pitfalls
- **Field must be volatile**: The updater requires the target field to be declared `volatile`.
- **Class loading**: The updater checks field accessibility at creation time; ensure the class is loaded.
- **ABA problem**: CAS doesn't detect intermediate changes; use `AtomicStampedReference` if needed.
- **Staff insight**: Always create the updater as a `static final` field to avoid reflection overhead on every access.
