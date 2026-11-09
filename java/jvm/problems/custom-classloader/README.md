# Custom ClassLoader

## Problem Statement

Design a custom ClassLoader in Java that loads classes from non-standard sources (e.g., network, database, encrypted files) and supports class isolation, hot reloading, and plugin architectures.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Load classes from custom source**: Read bytecode from network, database, or encrypted storage.
- **Delegation model**: Follow parent-first delegation; delegate to parent ClassLoader first.
- **Class isolation**: Loaded classes are isolated from other ClassLoaders.
- **Hot reloading**: Reload classes without restarting the JVM.
- **Resource loading**: Support `getResource()` and `getResources()` for custom sources.

### Non-Functional Requirements
- **Security**: Validate class bytecode before loading; prevent malicious code execution.
- **Performance**: Cache loaded classes; avoid redundant loading.
- **Memory management**: Support ClassLoader unloading to prevent memory leaks.

## Key Design Decisions
- **Extend ClassLoader**: Override `findClass()` and `findResource()` methods.
- **defineClass**: Use `defineClass(byte[] b, int off, int len)` to convert bytecode to Class.
- **Parent delegation**: Call `parent.loadClass()` first; fall back to custom loading.
- **Cache**: Use HashMap to cache loaded classes by name.

## Staff-Level Design Considerations

### ClassLoader Hierarchy
- **Bootstrap**: Loads core Java classes (rt.jar, java.base module).
- **Platform**: Loads Java platform classes (Java 9+ modules).
- **Application**: Loads classes from classpath.
- **Custom**: Loads classes from custom sources.
- **Staff insight**: Each ClassLoader has a parent. When loading a class, it delegates to the parent first. This prevents duplicate loading of core classes and ensures security.

### Hot Reloading Pattern
```java
// Create new ClassLoader for each reload
CustomClassLoader newLoader = new CustomClassLoader(parent);
Class<?> clazz = newLoader.loadClass("com.example.Plugin");
Object instance = clazz.getDeclaredConstructor().newInstance();
// Old ClassLoader becomes garbage and is unloaded
oldLoader = null;  // Allow GC to collect old classes
```
- **Staff insight**: To reload a class, you must create a new ClassLoader. The old ClassLoader must become unreachable so the GC can collect it along with all its loaded classes.

### Common Use Cases
- **Plugin systems**: Load plugins from external directories; isolate plugin classes.
- **OSGi/Tomcat**: Each web app has its own ClassLoader for class isolation.
- **Dynamic code execution**: Load and execute user-provided code (e.g., Groovy scripts, rules engines).
- **Encryption**: Load encrypted classes by decrypting bytecode before `defineClass()`.
- **Staff insight**: Tomcat uses a hierarchical ClassLoader per web app. Shared classes (Servlet API) are loaded by the parent; app-specific classes by the child. This prevents class conflicts between web apps.

### Common Pitfalls
- **ClassCastException**: Same class loaded by different ClassLoaders is considered a different class.
- **Memory leaks**: ClassLoader holds strong references to loaded classes; ensure ClassLoader can be GC'd.
- **Breaking delegation**: Loading a class that should be loaded by the parent causes conflicts.
- **Staff insight**: The most common ClassLoader bug is ClassCastException when the same class is loaded by two different ClassLoaders. Always follow the parent-first delegation model unless you have a specific reason not to.
