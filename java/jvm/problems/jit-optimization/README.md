# JIT Optimization

## Problem Statement

Design a strategy for understanding and leveraging Java's Just-In-Time (JIT) compiler optimizations to improve application performance, including method inlining, escape analysis, lock elimination, and array bounds check elimination.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **JIT monitoring**: Enable compilation logging with `-XX:+PrintCompilation`.
- **Inlining analysis**: Identify which methods are inlined and why some are not.
- **Escape analysis**: Understand when objects are stack-allocated vs heap-allocated.
- **Lock elimination**: Detect when JIT removes unnecessary synchronization.
- **Tiered compilation**: Understand C1 (client) vs C2 (server) compiler trade-offs.

### Non-Functional Requirements
- **Performance**: Leverage JIT optimizations for maximum throughput.
- **Predictability**: Understand when and how JIT compiles methods.
- **Benchmarking**: Use JMH with proper warm-up to account for JIT compilation.

## Key Design Decisions
- **Tiered compilation**: JVM uses C1 for fast compilation and C2 for aggressive optimization.
- **HotSpot detection**: Methods are compiled when invocation count exceeds threshold.
- **Inlining**: JIT inlines small methods to eliminate call overhead; respects `@CompiledInline`.
- **Escape analysis**: If object doesn't escape method, JIT allocates on stack or eliminates allocation.

## Staff-Level Design Considerations

### JIT Compilation Pipeline
1. **Interpretation**: Bytecode is interpreted by the interpreter.
2. **Profiling**: JVM counts method invocations and back-edges (loop iterations).
3. **C1 compilation**: When count exceeds threshold, C1 compiles the method quickly with basic optimizations.
4. **C2 compilation**: For very hot methods, C2 applies aggressive optimizations (inlining, vectorization).
5. **Deoptimization**: If assumptions change (e.g., new subclass loaded), JIT reverts to interpretation.
- **Staff insight**: The JVM starts interpreting code and gradually compiles hot paths. This is why Java applications have a warm-up period — the JIT needs time to profile and compile.

### Key JIT Optimizations
- **Method inlining**: Replace method call with method body; eliminates call overhead and enables further optimizations.
- **Escape analysis**: If object doesn't escape the method, allocate on stack or eliminate entirely (scalar replacement).
- **Lock elimination**: If monitor can't be contested (escape analysis proves single-threaded access), remove synchronization.
- **Array bounds check elimination**: If loop index is proven to be within bounds, remove checks.
- **Dead code elimination**: Remove code that has no observable effect.
- **Staff insight**: Method inlining is the most impactful JIT optimization. It not only eliminates call overhead but also enables all other optimizations by exposing the full code path.

### Controlling JIT Behavior
- **-XX:+PrintCompilation**: Log which methods are compiled and by which compiler.
- **-XX:CompileThreshold**: Set invocation count threshold for compilation (default 10,000 for C1, 10,000 for C2).
- **-XX:InlineSmallCode**: Control inlining size threshold.
- **-XX:-UseCompiler**: Disable JIT compilation (for testing interpreted performance).
- **@CompiledInline / @DontInline**: Hint the JIT compiler (via JMH or custom annotations).
- **Staff insight**: Never use `System.nanoTime()` for benchmarks — the JIT hasn't compiled the code yet. Always use JMH with proper warm-up iterations to ensure JIT compilation before measuring.

### Common Pitfalls
- **Warm-up bias**: Measuring interpreted code instead of compiled code.
- **Dead code in benchmarks**: JIT eliminates code that has no observable effect; use JMH Blackhole.
- **Reflection overhead**: Reflection bypasses JIT inlining; use MethodHandle or generated code.
- **Staff insight**: The #1 benchmarking mistake is not accounting for JIT warm-up. JMH handles this automatically with warm-up iterations. Never write manual benchmarks with `System.nanoTime()`.
