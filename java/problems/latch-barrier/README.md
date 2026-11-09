# CountdownLatch & CyclicBarrier

## Problem Statement

Implement CountdownLatch (one-time barrier) and CyclicBarrier (reusable barrier) for thread synchronization.

**Reference**: AlgoMaster

## Requirements
- **CountdownLatch**: N threads wait until a counter reaches zero. One-time use.
- **CyclicBarrier**: N threads wait for each other at a barrier point. Reusable.
- **Timeout**: Support timeout on await.

## Key Design Decisions
- **CountdownLatch**: Atomic counter + wait/notify on counter reaching zero.
- **CyclicBarrier**: Generation-based barrier; reset on trip or manual reset.

## Staff-Level Design Considerations
- **Use case**: CountdownLatch for "wait for N tasks to complete." CyclicBarrier for "phase-based parallel computation."
- **Staff insight**: Phaser is the modern replacement for CyclicBarrier. It supports dynamic participant count and multiple phases. Use Phaser for new code.
