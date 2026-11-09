# Custom Collection Framework

## Problem Statement

Design a custom collection framework that implements the Java Collections interfaces (Collection, List, Set, Map) with custom behavior such as size limits, automatic cleanup, or domain-specific operations.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Implement Collection interface**: Support add, remove, contains, size, isEmpty, iterator.
- **Implement Map interface**: Support put, get, remove, keySet, values, entrySet.
- **Custom behavior**: Size limits, TTL-based expiration, or domain-specific constraints.
- **Iterator**: Fail-fast or weakly consistent iterator depending on thread safety needs.
- **Bulk operations**: addAll, removeAll, retainAll, clear.

### Non-Functional Requirements
- **Performance**: Match or exceed standard collection performance for the use case.
- **Memory efficiency**: Minimal overhead for custom behavior.
- **Correctness**: Proper equals, hashCode, and toString implementations.

## Key Design Decisions
- **Decorator pattern**: Wrap existing collections and add custom behavior.
- **Composition over inheritance**: Prefer wrapping over extending standard collections.
- **Interface implementation**: Implement Java Collection interfaces for interoperability.
- **Custom iterator**: Implement Iterator interface with proper hasNext/next/remove logic.

## Staff-Level Design Considerations

### Design Patterns for Collections
- **Decorator**: Wrap HashMap/ArrayList and add behavior (size limit, logging, validation).
- **Composite**: Tree-like structures where leaves and branches share an interface.
- **Flyweight**: Share common state among many objects; useful for domain-specific collections.
- **Staff insight**: Prefer composition over inheritance. Extending HashMap or ArrayList can break internal invariants. Wrapping with a decorator is safer and more flexible.

### Implementing equals and hashCode
- **Collection equals**: Two collections are equal if they contain the same elements, regardless of order or type.
- **Map equals**: Two maps are equal if they have the same key-value mappings.
- **Staff insight**: When implementing custom collections, delegate equals/hashCode to the backing collection. Don't reimplement — the Java spec defines precise rules for collection equality.

### Iterator Implementation
- **Fail-fast**: Throw ConcurrentModificationException on structural modification during iteration.
- **Weakly consistent**: See a snapshot of the collection; no exception on modification.
- **Snapshot iterator**: Copy the collection at iterator creation; safe but memory-intensive.
- **Staff insight**: For thread-safe collections, always use weakly consistent iterators. Fail-fast iterators don't work correctly in concurrent scenarios because the modification count can change between calls.

### Common Pitfalls
- **Not implementing Serializable**: Collections should be serializable for caching and distributed systems.
- **Broken equals/hashCode**: Custom collections must follow the general contract.
- **Memory leaks**: Holding strong references to removed elements; use WeakReference if needed.
- **Staff insight**: When designing custom collections, always consider serialization, equals/hashCode correctness, and iterator behavior. These are the most common sources of bugs in custom collection implementations.
