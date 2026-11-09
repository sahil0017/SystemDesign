# String Optimization

## Problem Statement

Design strategies for optimizing string operations in Java including concatenation, parsing, formatting, and internationalization to minimize memory allocation and CPU usage in performance-critical code paths.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Concatenation**: Compare String +, StringBuilder, and String.join performance.
- **Parsing**: Efficiently parse and tokenize strings without excessive allocation.
- **Formatting**: Use String.format vs StringBuilder vs custom formatting.
- **Interning**: Use String.intern() for deduplication of repeated strings.
- **Substring**: Avoid hidden array copies in substring operations.

### Non-Functional Requirements
- **Memory efficiency**: Minimize temporary string allocations.
- **Performance**: Reduce CPU time in string-heavy operations.
- **Correctness**: Handle Unicode and edge cases properly.

## Key Design Decisions
- **StringBuilder**: Reusable buffer for string concatenation in loops.
- **String.valueOf()**: Convert primitives to strings without boxing.
- **String.join()**: Java 8+ for joining collections; cleaner than StringBuilder.
- **Avoid String.format()**: Expensive for high-frequency formatting; use StringBuilder.

## Staff-Level Design Considerations

### String Concatenation Performance
- **String +**: Compiler converts to StringBuilder for simple cases; creates new StringBuilder per line.
- **StringBuilder**: Reusable; best for loops and complex concatenation.
- **String.join()**: Clean API for joining collections; uses StringBuilder internally.
- **String.concat()**: Creates new string; good for appending a single string.
- **Staff insight**: In a loop, `s += item` creates a new StringBuilder on each iteration. Always use a single StringBuilder outside the loop. The difference is O(n²) vs O(n) for n concatenations.

### Memory Optimization
- **String pooling**: Literal strings are automatically interned; "hello" == "hello" is true.
- **String.intern()**: Manually add strings to the pool; useful for deduplication.
- **String.valueof()**: For primitives, avoids boxing overhead of Integer.toString().
- **CharSequence**: Use CharSequence interface to avoid creating String from char arrays.
- **Staff insight**: String.intern() stores strings in metaspace (Java 7+), not heap. Be careful with interning large numbers of unique strings — it can cause Metaspace OOM. Use it only when you expect many duplicates.

### String.format() Overhead
- **Cost**: String.format() parses the format string, creates a Formatter, and allocates a StringBuilder. It's 10-100× slower than StringBuilder.
- **Alternative**: Use StringBuilder.append() for high-frequency formatting.
- **When to use**: Use String.format() for log messages and user-facing strings where readability matters.
- **Staff insight**: Never use String.format() in hot paths (loops, request handlers). It's one of the most common performance anti-patterns in Java. Replace with StringBuilder or a custom formatter.

### Common Pitfalls
- **String in loops**: `s += item` in a loop is O(n²); use StringBuilder.
- **substring() memory leak**: In Java 6 and earlier, substring shared the char array. Fixed in Java 7+, but be aware of legacy code.
- **Excessive toString()**: Calling toString() on every object creates garbage; cache if called frequently.
- **Staff insight**: The most impactful string optimization is using StringBuilder in loops. A loop that concatenates 1000 strings with += creates 1000 temporary StringBuilder and String objects. Using a single StringBuilder reduces this to 1 allocation.
