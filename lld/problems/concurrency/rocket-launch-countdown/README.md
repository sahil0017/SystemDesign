# Rocket Launch Countdown (Concurrency)

## Problem Statement

Design a multi-threaded rocket launch countdown system where multiple subsystems (fuel, engines, navigation, communication) must complete their pre-launch checks concurrently. The launch proceeds only when all subsystems report ready, using synchronization primitives to coordinate the countdown and launch sequence.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Subsystem checks**: Each subsystem runs pre-launch checks in parallel.
- **Countdown**: Start countdown only when all subsystems report ready.
- **Synchronization**: All subsystems must reach the ready barrier before proceeding.
- **Abort mechanism**: Any subsystem can abort the launch if checks fail.
- **Launch sequence**: Execute launch steps in order after countdown completes.
- **Status reporting**: Real-time status of each subsystem and countdown.

### Non-Functional Requirements
- **Thread safety**: Subsystem status updates are visible to all threads.
- **No race conditions**: Launch fires only once, even if multiple subsystems signal ready.
- **Timeliness**: Countdown and launch proceed within specified time windows.
- **Reliability**: System handles subsystem failures gracefully.

## Key Design Decisions
- **CountDownLatch**: Wait for all subsystems to complete checks before starting countdown.
- **CyclicBarrier**: Synchronize subsystems at multiple checkpoints.
- **AtomicBoolean**: Single launch trigger to prevent double-launch.
- **Future/CompletableFuture**: Async subsystem checks with timeout.

## Class Diagram

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  RocketLaunch    │────►│  Subsystem       │────►│ LaunchSequence   │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ - subsystems     │     │ - name           │     │ - steps          │
│ - countdownLatch │     │ - status         │     │ - currentIndex   │
│ - launchTrigger  │     │ - checkFuture    │     ├──────────────────┤
│ - abortFlag      │     ├──────────────────┤     │ + execute()      │
├──────────────────┤     │ + check()        │     │ + rollback()     │
│ + startCountdown │     │ + abort()        │     └──────────────────┘
│ + launch()       │     │ + getStatus()    │
│ + abort()        │     └──────────────────┘
└──────────────────┘
```

## Staff-Level Design Considerations

### CountDownLatch for Pre-Launch
- **One-time barrier**: `CountDownLatch(N)` waits for N subsystems to count down.
- **Staff insight**: `CountDownLatch` is one-shot — it cannot be reset. Use `CyclicBarrier` if you need reusable synchronization (e.g., multiple test runs).

### CompletableFuture for Async Checks
- **Parallel execution**: Each subsystem check runs as a `CompletableFuture`.
- **Staff insight**: Use `CompletableFuture.allOf()` to wait for all checks. Use `orTimeout()` to abort if any check takes too long. Don't use raw threads — `CompletableFuture` provides composition, timeout, and exception handling.

### Atomic Launch Trigger
- **Compare-and-set**: `AtomicBoolean.compareAndSet(false, true)` ensures launch fires only once.
- **Staff insight**: Without CAS, two threads could both see `launchTrigger == false` and both fire the launch. CAS ensures only one thread wins.

### Abort Mechanism
- **Interrupt-based**: Abort interrupts all waiting threads and cancels pending futures.
- **Staff insight**: Use `CompletableFuture.cancel(true)` to interrupt running tasks. Check `Thread.interrupted()` in long-running checks for responsive aborts.
