# Design Patterns

## Overview

Design patterns are reusable solutions to common software design problems. For staff engineers, patterns are not dogma — they are a **shared vocabulary** for discussing architecture and a **catalog of proven solutions** that reduce reinvention.

## Creational Patterns

| Pattern | Purpose | When to Use | Staff Insight |
|---------|---------|-------------|---------------|
| **Singleton** | Ensure one instance | Shared resources (DB connection pool, config) | Prefer dependency injection over global singletons; testability suffers |
| **Factory Method** | Defer object creation to subclasses | Framework extension points | Use when product creation logic varies by context |
| **Abstract Factory** | Create families of related objects | Cross-platform UI, multi-theme apps | Use when you need to guarantee compatibility across product families |
| **Builder** | Construct complex objects step-by-step | Objects with many optional parameters | Prefer over telescoping constructors; immutable objects |
| **Prototype** | Clone existing objects | Expensive object creation | Use with `clone()` or copy constructors; watch for deep vs shallow copy |

### Builder Pattern Example
```java
// Telescoping constructor anti-pattern
new User("John", "john@email.com", null, null, 25, null, true);

// Builder pattern
User user = new User.Builder()
    .name("John")
    .email("john@email.com")
    .age(25)
    .active(true)
    .build();
```

## Structural Patterns

| Pattern | Purpose | When to Use | Staff Insight |
|---------|---------|-------------|---------------|
| **Adapter** | Make incompatible interfaces work together | Legacy integration, third-party APIs | Prefer over modifying existing interfaces |
| **Bridge** | Decouple abstraction from implementation | Multiple dimensions of variation | Use instead of deep inheritance hierarchies |
| **Composite** | Treat individual and composite objects uniformly | Tree structures (file systems, UI components) | Use for recursive structures with uniform operations |
| **Decorator** | Add behavior dynamically | Logging, caching, compression wrappers | Prefer over subclassing for adding responsibilities |
| **Facade** | Simplify complex subsystem API | Library wrappers, API gateways | Reduces client complexity; doesn't add new behavior |
| **Flyweight** | Share fine-grained objects efficiently | Many similar objects (characters, icons) | Use when memory is constrained; separate intrinsic/extrinsic state |
| **Proxy** | Control access to an object | Lazy loading, access control, caching | Virtual proxy for lazy init; protection proxy for access control |

## Behavioral Patterns

| Pattern | Purpose | When to Use | Staff Insight |
|---------|---------|-------------|---------------|
| **Chain of Responsibility** | Pass request along handler chain | Middleware, approval workflows | Avoid long chains; ensure request is handled |
| **Command** | Encapsulate request as object | Undo/redo, queuing, logging | Use for actionable requests; enables serialization |
| **Iterator** | Traverse collection without exposing structure | Custom collections, lazy loading | Java's `Iterable` interface is built-in iterator |
| **Mediator** | Centralize complex communication | UI components, chat systems | Reduces coupling but mediator can become god object |
| **Memento** | Capture object state for restoration | Undo/redo, save/load state | Use for snapshot-based state management |
| **Observer** | Notify dependents of state changes | Event systems, pub/sub, reactive | Use for 1:N dependencies; avoid circular notifications |
| **State** | Change behavior based on internal state | State machines, workflow engines | Use when object behavior changes based on state |
| **Strategy** | Swap algorithms at runtime | Payment methods, sorting algorithms | Prefer over conditionals; enables open/closed principle |
| **Template Method** | Define algorithm skeleton, defer steps | Framework hooks, boilerplate reduction | Use for fixed algorithm with variable steps |
| **Visitor** | Add operations without modifying classes | AST traversal, report generation | Use when operations change frequently but structure is stable |

## Most Important Patterns for Staff Engineers

1. **Strategy**: Replace conditionals with polymorphism — most used in production
2. **Observer**: Event-driven architecture foundation — essential for async systems
3. **Factory/Builder**: Object creation — used in every non-trivial codebase
4. **Decorator**: Cross-cutting concerns — logging, caching, security
5. **Command**: Action encapsulation — undo/redo, job queues, audit trails
6. **Adapter**: Integration — legacy systems, third-party APIs
7. **Facade**: Simplification — complex subsystems, library wrappers

## Staff-Level Pattern Checklist

1. **Don't force patterns**: Use patterns when they naturally fit, not because you should
2. **Prefer composition over inheritance**: More flexible, easier to test
3. **Know the trade-offs**: Every pattern adds indirection; measure complexity vs benefit
4. **Combine patterns**: Strategy + Factory, Observer + Command, Decorator + Proxy
5. **Language features replace patterns**: Java 8+ lambdas replace Strategy/Command; records replace Builder
6. **Document pattern usage**: Make architectural decisions explicit in code comments
