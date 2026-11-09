# Common Utilities

This package contains reusable code utilities, base classes, and shared abstractions for LLD problem implementations.

## Purpose

The `common` package serves as a **shared foundation** for all LLD problem implementations. Instead of duplicating boilerplate code across problems, common patterns are extracted here for reuse.

## What Goes Here

### Base Classes & Interfaces
- **Entity**: Base class with `id`, `createdAt`, `updatedAt` fields
- **Repository<T>**: Generic repository interface for CRUD operations
- **Observer**: Base observer interface for event-driven patterns
- **State**: Base state interface for state machine implementations

### Enums & Constants
- **Status**: Common status enums (Active, Inactive, Pending, etc.)
- **Role**: User roles (Admin, User, Guest)
- **Priority**: Priority levels (Low, Medium, High, Critical)

### Utility Classes
- **IdGenerator**: Snowflake-based distributed ID generation
- **Validator**: Input validation utilities
- **Logger**: Structured logging facade
- **EventBus**: In-memory pub/sub event bus for testing

### Data Structures
- **LRUCache<K,V>**: Reusable LRU cache implementation
- **BlockingQueue<T>**: Thread-safe blocking queue
- **IntervalTree**: Interval tree for range queries

## Why a Common Package?

1. **DRY (Don't Repeat Yourself)**: Avoid duplicating entity base classes, ID generators, and utility methods across 49+ LLD problems.
2. **Consistency**: All problems use the same ID generation strategy, logging format, and validation patterns.
3. **Testability**: Common test utilities (mock repositories, test data generators) are shared.
4. **Real-world pattern**: In production codebases, shared libraries contain common abstractions. This mirrors that structure.

## What Does NOT Go Here

- **Problem-specific logic**: Each problem's unique business logic stays in its own module.
- **Design pattern implementations**: Strategy, Observer, Factory implementations are problem-specific and demonstrate the pattern.
- **Database schemas**: Database design is covered in the `db-design/` module.

## Usage Example

```java
// In any LLD problem, import common utilities:
import common.entity.BaseEntity;
import common.util.IdGenerator;
import common.cache.LRUCache;

// Extend base entity
public class User extends BaseEntity {
    private String email;
    private String name;
    // ... problem-specific fields
}

// Use shared ID generator
public class UserRepository {
    private final IdGenerator idGen = new IdGenerator();
    
    public User createUser(String email) {
        User user = new User();
        user.setId(idGen.nextId());
        user.setEmail(email);
        // ...
    }
}
```

## Directory Structure

```
common/
├── README.md              # This file
├── entity/
│   └── BaseEntity.java    # Base entity with id, timestamps
├── repository/
│   └── Repository.java    # Generic repository interface
├── util/
│   ├── IdGenerator.java   # Snowflake ID generator
│   ├── Validator.java     # Input validation
│   └── Logger.java        # Structured logging
├── cache/
│   └── LRUCache.java      # Reusable LRU cache
├── event/
│   ├── EventBus.java      # In-memory pub/sub
│   └── Observer.java      # Observer interface
└── enums/
    ├── Status.java        # Common status enum
    ├── Role.java          # User roles
    └── Priority.java      # Priority levels
```

## Staff-Level Insight

In a real codebase, the `common` package would be a **separate Maven/Gradle module** published to an internal artifact repository. This ensures:
- Versioned releases of shared utilities
- Independent testing and CI/CD
- Clear dependency boundaries between modules
- Prevents circular dependencies between problem modules

For this repository, it's a single package for simplicity, but the conceptual separation remains.
