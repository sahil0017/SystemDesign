# Object-Oriented Programming

## Overview

OOP is a programming paradigm based on objects containing data and behavior. For staff engineers, OOP is about **modeling domain concepts accurately**, **managing complexity through abstraction**, and **enabling extensibility through polymorphism**.

## Four Pillars

### 1. Encapsulation
**Definition**: Bundling data (state) and methods (behavior) that operate on that data, restricting direct access.

```java
public class BankAccount {
    private double balance; // Encapsulated state
    
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount; // Controlled access
        }
    }
    
    public double getBalance() {
        return balance; // Read-only access
    }
}
```

**Staff Insight**: Encapsulation is not just about private fields — it's about **invariant protection**. Every public method must preserve the object's invariants.

### 2. Abstraction
**Definition**: Hiding implementation details and exposing only essential behavior.

```java
// Abstraction via interface
interface PaymentGateway {
    PaymentResult charge(double amount, Currency currency);
    PaymentResult refund(TransactionId id, double amount);
}

// Implementation hidden behind abstraction
class StripeGateway implements PaymentGateway { /* ... */ }
class AdyenGateway implements PaymentGateway { /* ... */ }
```

**Staff Insight**: Abstraction reduces cognitive load. Clients should understand **what** an object does, not **how** it does it.

### 3. Inheritance
**Definition**: Creating new classes based on existing ones, inheriting fields and methods.

```java
abstract class Notification {
    abstract void send(String recipient, String message);
    void log() { /* common logging */ }
}
class EmailNotification extends Notification {
    void send(String to, String msg) { /* email logic */ }
}
class SMSPublication extends Notification {
    void send(String phone, String msg) { /* SMS logic */ }
}
```

**Staff Insight**: **Favor composition over inheritance**. Inheritance creates tight coupling; composition is more flexible. Use inheritance only for "is-a" relationships that satisfy LSP.

### 4. Polymorphism
**Definition**: Same interface, different implementations — behavior determined at runtime.

```java
// Compile-time polymorphism (overloading)
void process(String data) { /* ... */ }
void process(int data) { /* ... */ }

// Runtime polymorphism (overriding)
List<Shape> shapes = List.of(new Circle(), new Rectangle());
for (Shape shape : shapes) {
    shape.draw(); // Different behavior per subtype
}
```

**Staff Insight**: Polymorphism enables the **Open/Closed Principle**. New behaviors are added by creating new subtypes, not modifying existing code.

## Key Concepts

### Classes and Objects
- **Class**: Blueprint defining structure and behavior
- **Object**: Instance of a class with actual state
- **Staff insight**: Classes should model **domain concepts**, not technical layers

### Interfaces vs Abstract Classes

| Feature | Interface | Abstract Class |
|---------|-----------|----------------|
| Multiple inheritance | Yes | No |
| State (fields) | Only constants | Instance fields |
| Constructor | No | Yes |
| Default methods | Java 8+ | Yes |
| Use when | Capability/role | Shared implementation |

**Staff insight**: Use **interfaces for capabilities** (Serializable, Comparable) and **abstract classes for shared implementation** (base framework classes).

### Composition vs Inheritance

```java
// Inheritance (tight coupling)
class Bird { void fly() { /* ... */ } }
class Penguin extends Bird { void fly() { throw new RuntimeException(); } } // LSP violation!

// Composition (loose coupling)
class Bird {
    private FlyBehavior flyBehavior; // Composition
    void performFly() { flyBehavior.fly(); }
}
class Penguin extends Bird {
    Penguin() { flyBehavior = new CannotFly(); } // Flexible
}
```

**Staff insight**: Composition enables **runtime behavior swapping**; inheritance is fixed at compile time.

### Access Modifiers

| Modifier | Class | Package | Subclass | World |
|----------|-------|---------|----------|-------|
| public | ✓ | ✓ | ✓ | ✓ |
| protected | ✓ | ✓ | ✓ | ✗ |
| package-private | ✓ | ✓ | ✗ | ✗ |
| private | ✓ | ✗ | ✗ | ✗ |

**Staff insight**: **Prefer package-private** over protected. Package-private limits visibility to the module; protected exposes to all subclasses globally.

### Immutability
```java
public final class Address {
    private final String street;
    private final String city;
    private final String zipCode;
    
    public Address(String street, String city, String zipCode) {
        this.street = Objects.requireNonNull(street);
        this.city = Objects.requireNonNull(city);
        this.zipCode = Objects.requireNonNull(zipCode);
    }
    // Getters only, no setters
}
```

**Staff insight**: **Prefer immutable objects** — thread-safe, cacheable, no unexpected state changes. Use `final` classes and fields.

## Staff-Level OOP Checklist

1. **Model domain, not infrastructure**: Classes should represent business concepts
2. **Prefer composition over inheritance**: More flexible, easier to test
3. **Program to interfaces**: Depend on abstractions, not implementations
4. **Make objects immutable by default**: Thread-safe, predictable behavior
5. **Keep classes small**: < 300 lines; single responsibility
6. **Limit method parameters**: < 3 parameters; use parameter objects or builders
7. **Avoid god objects**: Classes that know too much or do too much
