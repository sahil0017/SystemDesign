# Thread Dump Analysis

## Problem Statement

Design a systematic approach to analyzing Java thread dumps to diagnose performance issues including deadlocks, thread starvation, high CPU usage, and blocking I/O.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Thread dump capture**: Generate thread dumps using jstack, jcmd, or SIGQUIT.
- **Thread state analysis**: Identify threads in RUNNABLE, BLOCKED, WAITING, and TIMED_WAITING states.
- **Deadlock detection**: Find circular lock dependencies between threads.
- **CPU profiling**: Correlate thread dumps with CPU usage to find hot threads.
- **Stack trace analysis**: Read call stacks to identify what each thread is doing.

### Non-Functional Requirements
- **Production safety**: Non-intrusive thread dump capture that doesn't impact application.
- **Automation**: Automated thread dump collection during incidents.
- **Actionable insights**: Clear identification of root cause and fix recommendations.

## Key Design Decisions
- **jcmd for capture**: `jcmd <pid> Thread.print` — safest and most feature-rich method.
- **Multiple dumps**: Take 3-4 dumps 10 seconds apart to identify persistent patterns.
- **Tool analysis**: Use JMC, TDA (Thread Dump Analyzer), or online tools for automated analysis.
- **Correlation**: Cross-reference thread dumps with CPU metrics and GC logs.

## Staff-Level Design Considerations

### Thread States and What They Mean
- **RUNNABLE**: Thread is executing or ready to execute. High CPU if persistently RUNNABLE.
- **BLOCKED**: Thread is waiting to acquire a monitor lock. Indicates lock contention.
- **WAITING**: Thread is waiting indefinitely (Object.wait, LockSupport.park, Thread.join).
- **TIMED_WAITING**: Thread is waiting with a timeout (Thread.sleep, wait(timeout), parkNanos).
- **NEW/TERMINATED**: Thread not yet started or already finished.
- **Staff insight**: In a healthy application, most threads should be WAITING or TIMED_WAITING (idle in thread pool). If many threads are BLOCKED, you have lock contention. If many are RUNNABLE with high CPU, you have a compute bottleneck.

### Deadlock Detection
- **Pattern**: Thread A holds lock 1, waits for lock 2. Thread B holds lock 2, waits for lock 1.
- **jcmd detection**: `jcmd <pid> Thread.print` automatically detects and reports deadlocks.
- **jstack detection**: `jstack <pid>` shows "Found one Java-level deadlock" section.
- **Fix**: Acquire locks in consistent order; use tryLock with timeout; reduce lock scope.
- **Staff insight**: Take multiple thread dumps to confirm a deadlock. A single dump might show a transient state that resolves quickly. If the same BLOCKED pattern appears in 3+ dumps, it's likely a deadlock.

### Common Thread Dump Patterns
- **High CPU**: Many RUNNABLE threads in compute-intensive methods. Look for infinite loops or excessive computation.
- **Lock contention**: Many BLOCKED threads waiting on the same monitor. Look for synchronized blocks or ReentrantLock.
- **Thread pool exhaustion**: All pool threads BLOCKED or WAITING on external calls (DB, HTTP). No available threads for new requests.
- **GC pressure**: Many threads BLOCKED during Stop-The-World GC pause.
- **Staff insight**: The most common production issue is thread pool exhaustion. When all threads are blocked waiting for a slow downstream service, the application appears hung. Fix by adding timeouts, increasing pool size, or circuit-breaking the slow dependency.

### Analysis Workflow
1. **Capture**: Take 3 thread dumps 10 seconds apart during the issue.
2. **Compare**: Identify threads that are consistently in the same state across all dumps.
3. **Categorize**: Count threads by state (RUNNABLE, BLOCKED, WAITING, TIMED_WAITING).
4. **Investigate**: For persistent BLOCKED threads, find the lock owner and its stack trace.
5. **Correlate**: Cross-reference with CPU metrics, GC logs, and application logs.
- **Staff insight**: Always take multiple thread dumps. A single snapshot can be misleading — threads change state rapidly. Persistent patterns across multiple dumps indicate real issues.
