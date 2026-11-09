# Clean Code by Robert C. Martin

## Summary

Principles of writing clean, maintainable code with examples in Java. Covers meaningful names, functions, formatting, comments, error handling, and unit tests. A foundational book for software craftsmanship.

## Key Principles

### Names
- Use intention-revealing names
- Avoid disinformation (don't use misleading names)
- Make meaningful distinctions (don't use number suffixes unnecessarily)

### Functions
- Do one thing and do it well
- Keep functions small (< 20 lines ideal)
- Few arguments (0-2 preferred, max 3)
- No side effects

### Formatting
- Vertical openness: related code should be close together
- Vertical density: unrelated code should be separated
- Team consistency: follow team conventions

### Comments
- Comments explain **why**, not **what**
- Good code is self-documenting
- Avoid redundant comments

### Error Handling
- Use exceptions, not error codes
- Provide context in exceptions
- Don't return null — return empty collections or throw exceptions

## Key Takeaways

- **Code is read more than it's written**: Write code for human readers, not just machines
- **SOLID principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Boy Scout Rule**: Leave the code cleaner than you found it
- **Unit tests are documentation**: Tests describe expected behavior

## Why Read This Book

- Foundation for writing code that others can read and maintain
- Applicable to any programming language
- Essential for team-based software development

## Related Problems in This Repository

- [LLD - SOLID Principles](../../lld/fundamentals/solid-principles.md)
- [Blogs - Code Review Best Practices](../../blogs-articles/career-growth/code-review.md)
