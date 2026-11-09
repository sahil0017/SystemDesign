# Phaser (Dynamic Barrier)

## Problem Statement

Implement a Phaser — a dynamic phase-based synchronization barrier in Java. Unlike CountDownLatch (one-time use) and CyclicBarrier (fixed parties), Phaser supports dynamic registration/deregistration of parties and multiple phases of synchronization.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Party registration**: Dynamically add and remove parties at any time.
- **Phase management**: Advance through multiple synchronization phases.
- **Arrive and await**: Parties arrive at barrier and wait for all others.
- **Arrive and advance**: Parties arrive and proceed without waiting.
- **Force termination**: Force all parties to terminate the phaser.
- **Hierarchical phasers**: Link phasers for large-scale coordination.

### Non-Functional Requirements
- **Scalability**: Support 10K+ parties efficiently.
- **Low overhead**: Registration and arrival in O(1) time.
- **No deadlock**: Handle parties that deregister mid-phase.

## Key Design Decisions
- **Atomic operations**: Use CAS for lock-free party count management.
- **Tree structure**: Hierarchical phasers for large party counts.
- **Phase wrapping**: Phase number wraps around to prevent overflow.
- **Unregistration**: Negative party count indicates unregistered parties.

## Implementation

```java
public class SimplePhaser {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition condition = lock.newCondition();
    private int registeredParties;
    private int arrivedParties;
    private int phase;

    public SimplePhaser(int parties) {
        this.registeredParties = parties;
    }

    public void register() {
        lock.lock();
        try {
            registeredParties++;
        } finally {
            lock.unlock();
        }
    }

    public void unregister() {
        lock.lock();
        try {
            registeredParties--;
            condition.signalAll();
        } finally {
            lock.unlock();
        }
    }

    public int arriveAndAwaitAdvance() throws InterruptedException {
        lock.lockInterruptibly();
        try {
            arrivedParties++;
            if (arrivedParties == registeredParties) {
                phase++;
                arrivedParties = 0;
                condition.signalAll();
            } else {
                while (arrivedParties < registeredParties) {
                    condition.await();
                }
            }
            return phase;
        } finally {
            lock.unlock();
        }
    }
}
```

## Staff-Level Design Considerations

### Phaser vs CyclicBarrier vs CountDownLatch
- **CountDownLatch**: One-time use, fixed count, no reset — for one-time startup.
- **CyclicBarrier**: Fixed parties, reusable, all-or-nothing — for fixed-size parallel algorithms.
- **Phaser**: Dynamic parties, multiple phases, flexible — for evolving workloads.
- **Staff insight**: Use **CountDownLatch** for "wait for N tasks to complete." Use **CyclicBarrier** for "N threads meet at checkpoint, repeat." Use **Phaser** for "dynamic number of workers in multi-phase algorithm" (e.g., iterative map-reduce where workers join/leave).

### Use Cases
- **Parallel algorithms**: Multi-phase computation where workers process data in stages.
- **Game servers**: Synchronize game ticks with dynamic player count.
- **Batch processing**: Process data in phases with dynamic worker pool.
- **Staff insight**: Phaser is ideal for **iterative algorithms** — e.g., training a ML model where each epoch is a phase, and workers can join/leave between epochs. CyclicBarrier can't handle dynamic worker count; CountDownLatch can't handle multiple phases.

### Hierarchical Phasers
- **Parent-child**: Link phasers in a tree for large-scale coordination.
- **Scalability**: Each phaser handles up to INT_MAX parties; tree handles unlimited.
- **Staff insight**: Use **hierarchical phasers** when you have >10K parties. A single phaser with millions of parties has contention on the arrival point. A tree of phasers (e.g., 1000 phasers with 100 parties each, linked to a parent) distributes the contention. Java's `Phaser.onAdvance` callback enables this pattern.

### Termination Handling
- **Force termination**: Abort all waiting parties when error occurs.
- **Graceful shutdown**: Deregister all parties and advance to termination.
- **Staff insight**: Always call **`forceTerminate()`** on error paths. If a worker throws an exception, the phaser can hang forever waiting for it. Catch exceptions in worker threads, force-terminate the phaser, and handle cleanup. This prevents resource leaks in production systems.
