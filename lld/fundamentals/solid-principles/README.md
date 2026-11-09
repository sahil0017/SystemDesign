# SOLID Principles

## Overview

SOLID is an acronym for five fundamental object-oriented design principles that help create maintainable, extensible, and testable software. For staff engineers, SOLID is not just about following rules — it's about **managing complexity**, **reducing coupling**, and **enabling independent team development**.

## Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change — i.e., one responsibility.

### Example (Bad → Good)
```java
// BAD: User class handles multiple responsibilities
class User {
    void saveToDatabase() { /* persistence */ }
    void sendEmail() { /* notification */ }
    void validate() { /* validation */ }
    void generateReport() { /* reporting */ }
}

// GOOD: Separated responsibilities
class User { /* domain logic only */ }
class UserRepository { void save(User user) { } }
class EmailService { void sendWelcome(User user) { } }
class UserValidator { boolean validate(User user) { } }
```

### Staff Insight
- **One reason to change** = one business capability. If a class changes for both billing and reporting, it violates SRP.
- **Micro-SRP anti-pattern**: Don't split responsibilities so finely that you create 100 tiny classes. Balance cohesion with practicality.
- **Symmetric Coupling Principle**: If two methods always change together, they belong in the same class.

## Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension, closed for modification.

### Example (Bad → Good)
```java
// BAD: Modifying class to add new payment types
class PaymentProcessor {
    void process(String type, double amount) {
        if (type.equals("credit_card")) { /* ... */ }
        else if (type.equals("paypal")) { /* ... */ }
        else if (type.equals("crypto")) { /* ... */ } // Requires modification
    }
}

// GOOD: Extending via polymorphism
interface PaymentMethod { void pay(double amount); }
class CreditCardPayment implements PaymentMethod { /* ... */ }
class PayPalPayment implements PaymentMethod { /* ... */ }
class CryptoPayment implements PaymentMethod { /* ... */ } // New type = new class, no modification

class PaymentProcessor {
    void process(PaymentMethod method, double amount) {
        method.pay(amount); // Closed for modification, open for extension
    }
}
```

### Staff Insight
- **Achieved via**: Abstraction (interfaces/abstract classes), polymorphism, dependency injection
- **Not absolute**: Some modification is inevitable. OCP means minimizing changes to existing tested code.
- **Strategy pattern** is the most common OCP implementation.

## Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

### Example (Bad → Good)
```java
// BAD: Rectangle/Square classic violation
class Rectangle {
    void setWidth(int w) { width = w; }
    void setHeight(int h) { height = h; }
}
class Square extends Rectangle {
    void setWidth(int w) { width = w; height = w; } // Breaks Rectangle behavior
    void setHeight(int h) { width = h; height = h; }
}

// GOOD: Common abstraction
interface Shape { double area(); double perimeter(); }
class Rectangle implements Shape { /* independent width/height */ }
class Square implements Shape { /* equal sides */ }
```

### Staff Insight
- **Preconditions cannot be strengthened** in subclasses
- **Postconditions cannot be weakened** in subclasses
- **Invariants must be preserved** — subclass must maintain base class contracts
- **Composition over inheritance**: When LSP is hard to satisfy, prefer composition

## Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

### Example (Bad → Good)
```java
// BAD: Fat interface forces unnecessary implementations
interface Worker {
    void work();
    void eat();
    void sleep();
}
class RobotWorker implements Worker {
    void work() { /* ... */ }
    void eat() { throw new UnsupportedOperationException(); } // Forced to implement
    void sleep() { throw new UnsupportedOperationException(); }
}

// GOOD: Segregated interfaces
interface Workable { void work(); }
interface Eatable { void eat(); }
interface Sleepable { void sleep(); }
class HumanWorker implements Workable, Eatable, Sleepable { /* ... */ }
class RobotWorker implements Workable { /* only what it needs */ }
```

### Staff Insight
- **Java 8 default methods** partially mitigate ISP but don't eliminate the design problem
- **Micro-interfaces** can lead to interface explosion. Balance granularity with practicality.
- **Role interfaces**: Each interface represents a distinct role/capability

## Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

### Example (Bad → Good)
```java
// BAD: High-level depends on low-level
class OrderService {
    private MySQLDatabase db = new MySQLDatabase(); // Tight coupling
    void saveOrder(Order order) { db.save(order); }
}

// GOOD: Both depend on abstraction
interface OrderRepository { void save(Order order); }
class MySQLOrderRepository implements OrderRepository { /* ... */ }
class MockOrderRepository implements OrderRepository { /* for testing */ }

class OrderService {
    private final OrderRepository repository; // Depends on abstraction
    OrderService(OrderRepository repository) { this.repository = repository; } // DI
    void saveOrder(Order order) { repository.save(order); }
}
```

### Staff Insight
- **Dependency Injection** is the primary mechanism for achieving DIP
- **Inversion of Control (IoC) containers** (Spring, Guice) automate DI wiring
- **Interface ownership**: The consumer (high-level module) should define the interface, not the provider

## Staff-Level SOLID Checklist

1. **SRP**: Does each class have one clear responsibility? Would you describe it in one sentence?
2. **OCP**: Can you add new features without modifying existing tested code?
3. **LSP**: Can you replace any subclass with its parent without breaking behavior?
4. **ISP**: Do any clients implement methods they never call?
5. **DIP**: Do high-level modules depend on concrete implementations or abstractions?
6. **Balance**: SOLID is a guideline, not a law. Over-engineering for SOLID can be worse than mild violations.
7. **Refactor incrementally**: Apply SOLID during refactoring, not greenfield design. Production feedback reveals true responsibilities.
