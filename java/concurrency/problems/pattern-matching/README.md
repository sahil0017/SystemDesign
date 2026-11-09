# Pattern Matching (Java 16+)

## Problem Statement

Explore Java 16+ pattern matching for instanceof, demonstrating how to write cleaner, more type-safe code by eliminating explicit casts and reducing boilerplate in conditional type checking.

**Reference**: Java 16 JEP 394, Java 17 JEP 420, Effective Java (3rd Edition)

## Requirements

### Learning Objectives
- **Pattern matching for instanceof**: Replace explicit casts with pattern variables.
- **Type-safe binding**: Compiler-enforced type safety with pattern variables.
- **Scope rules**: Understand pattern variable scope in if/else and logical operators.
- **Migration strategy**: Convert legacy instanceof + cast code to pattern matching.

### Key Concepts
- **Pattern variables**: Type-safe variable binding in instanceof checks.
- **Definite assignment**: Compiler tracks pattern variable assignment for scope.
- **Negated patterns**: How pattern variables work with `!` and `&&`/`||`.
- **Null safety**: Pattern matching with null values.

## Code Examples

### Before: Traditional instanceof + Cast

```java
// Verbose and error-prone
public String format(Object obj) {
    if (obj instanceof String) {
        String s = (String) obj;  // Explicit cast required
        return "String: " + s;
    } else if (obj instanceof Integer) {
        Integer i = (Integer) obj;  // Explicit cast required
        return "Integer: " + i;
    } else if (obj instanceof List) {
        List<?> list = (List<?>) obj;  // Raw type cast
        return "List of size: " + list.size();
    }
    return "Unknown: " + obj;
}
```

### After: Pattern Matching for instanceof

```java
// Clean and type-safe
public String format(Object obj) {
    if (obj instanceof String s) {
        return "String: " + s;  // s is automatically typed and cast
    } else if (obj instanceof Integer i) {
        return "Integer: " + i;
    } else if (obj instanceof List<?> list) {
        return "List of size: " + list.size();
    }
    return "Unknown: " + obj;
}
```

### Advanced Patterns

```java
// Pattern variables with logical operators
if (obj instanceof String s && s.length() > 10) {
    System.out.println("Long string: " + s);
}

// Negated pattern
if (!(obj instanceof String s)) {
    throw new IllegalArgumentException("Expected String");
}
// s is NOT in scope here

// Pattern with collections
if (obj instanceof List<String> list && list.size() > 0) {
    System.out.println("First element: " + list.get(0));
}

// Refactoring equals() method
@Override
public boolean equals(Object obj) {
    return obj instanceof Person p
        && this.name.equals(p.name)
        && this.age == p.age;
}
```

## Staff-Level Design Considerations

### Benefits of Pattern Matching
- **Eliminates casts**: No explicit casting after instanceof; compiler handles it.
- **Type safety**: Compiler enforces type correctness; no ClassCastException risk.
- **Readability**: Code reads like natural language: "if obj is a String s".
- **Refactoring friendly**: Adding new types requires changes in one place.
- **Staff insight**: Pattern matching reduces boilerplate by 30-50% in type-checking code. It's the most impactful Java 16+ feature for everyday coding. Use it in every instanceof check.

### Scope Rules
- **Positive check**: Pattern variable is in scope if the check passes.
- **Negated check**: Pattern variable is NOT in scope after `!`.
- **Logical AND**: Pattern variable is in scope after `&&` if both conditions pass.
- **Logical OR**: Pattern variable is NOT in scope after `||` (ambiguous).
- **Staff insight**: The scope rules are subtle. Use the DRY principle: if you need the variable in both branches, extract it before the if statement. The compiler's definite assignment analysis catches most mistakes.

### Migration Strategy
- **Search and replace**: Find all `instanceof` checks and add pattern variables.
- **Remove casts**: Delete explicit casts that follow instanceof checks.
- **Test**: Run existing tests to verify behavior is unchanged.
- **Staff insight**: Migration is mechanical and safe. The compiler guarantees that pattern matching produces the same bytecode as instanceof + cast. Use IDE refactoring tools (IntelliJ has a "Replace with pattern matching" action) for bulk migration.

### Combining with Switch Patterns
- **Progressive migration**: Start with instanceof pattern matching (Java 16), then migrate to switch patterns (Java 21).
- **Full power**: Switch patterns with record destructuring provide the most expressive pattern matching.
- **Staff insight**: Use instanceof pattern matching on Java 16-20. On Java 21+, prefer switch patterns for multi-type checks. Switch patterns are more concise and the compiler checks exhaustiveness.
