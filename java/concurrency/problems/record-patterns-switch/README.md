# Record Patterns & Switch (Java 16+)

## Problem Statement

Explore Java 16+ record patterns and pattern matching for switch expressions, demonstrating how to write cleaner, more expressive code for type-safe data processing and complex conditional logic.

**Reference**: Java 16-21 JEPs, Effective Java (3rd Edition)

## Requirements

### Learning Objectives
- **Record patterns**: Understand record patterns for destructuring record instances.
- **Pattern matching for switch**: Replace instanceof chains with switch expressions.
- **Guarded patterns**: Add additional conditions to pattern cases.
- **Nested patterns**: Combine multiple pattern types in nested structures.
- **Migration strategy**: Convert legacy instanceof/equals chains to pattern matching.

### Key Concepts
- **Records**: Immutable data carriers with automatic equals, hashCode, and toString.
- **Pattern variables**: Type-safe variable binding in pattern matches.
- **Exhaustiveness**: Compiler checks that all cases are covered.
- **Null handling**: Pattern matching with null values.

## Code Examples

### Record Patterns

```java
// Define records
record Point(int x, int y) {}
record Circle(Point center, int radius) {}
record Rectangle(Point topLeft, Point bottomRight) {}

// Before: Manual casting and getter calls
void printShapeArea(Object obj) {
    if (obj instanceof Circle) {
        Circle c = (Circle) obj;
        System.out.println(Math.PI * c.radius() * c.radius());
    } else if (obj instanceof Rectangle) {
        Rectangle r = (Rectangle) obj;
        // Complex area calculation...
    }
}

// After: Record patterns with destructuring
void printShapeArea(Object obj) {
    switch (obj) {
        case Circle(var center, var radius) ->
            System.out.println(Math.PI * radius * radius);
        case Rectangle(var topLeft, var bottomRight) ->
            System.out.println(calculateArea(topLeft, bottomRight));
        case null, default -> System.out.println("Unknown shape");
    }
}
```

### Nested Patterns

```java
// Check if a shape is a circle at the origin
boolean isCircleAtOrigin(Object obj) {
    return obj instanceof Circle(Point(0, 0), var radius) && radius > 0;
}

// Guarded patterns
String describeShape(Object obj) {
    return switch (obj) {
        case Circle(var center, var radius)
                when radius > 100 -> "Large circle at " + center;
        case Circle(var center, var radius) -> "Small circle at " + center;
        case Rectangle(var p1, var p2) -> "Rectangle from " + p1 + " to " + p2;
        case null -> "Null shape";
        default -> "Unknown type: " + obj.getClass();
    };
}
```

## Staff-Level Design Considerations

### When to Use Pattern Matching
- **Replace instanceof chains**: Any chain of instanceof checks is a candidate for switch patterns.
- **Data processing**: Pattern matching excels at processing hierarchical data (ASTs, JSON, shapes).
- **Visitor pattern alternative**: For simple type-based dispatch, switch patterns can replace the visitor pattern.
- **Staff insight**: Pattern matching reduces boilerplate by 50-70% in type-checking code. It's more readable and less error-prone than manual casting. Use it aggressively in data processing code.

### Migration Strategy
- **Start with instanceof**: Migrate `if (obj instanceof Type)` to `if (obj instanceof Type var x)` first.
- **Then switch**: Convert instanceof chains to switch expressions.
- **Add guards**: Replace nested if conditions with guarded patterns.
- **Staff insight**: Migrate incrementally. Start with the simplest pattern matching (instanceof with variable binding) and progress to full switch expressions. The compiler's exhaustiveness check catches missing cases automatically.

### Limitations
- **Records only**: Record patterns only work with record types, not regular classes.
- **Performance**: Pattern matching has slight overhead vs direct instanceof (negligible in most cases).
- **Refactoring**: IDE support for refactoring pattern matching is still maturing.
- **Staff insight**: Pattern matching is a Java 16+ feature. If you're on Java 11 LTS, you'll need to upgrade to Java 17 LTS (or later) to use it. Java 17 LTS is the minimum recommended version for new projects in 2024+.
