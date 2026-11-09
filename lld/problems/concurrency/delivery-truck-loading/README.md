# Delivery Truck Loading (Concurrency)

## Problem Statement

Design a multi-threaded delivery truck loading system where multiple workers concurrently load packages onto trucks. Each truck has weight and volume constraints, and packages must be assigned without exceeding limits or duplicating assignments.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Package**: Each package has weight, volume, destination, and priority.
- **Truck**: Each truck has max weight, max volume, and assigned route.
- **Loading**: Workers concurrently assign packages to trucks.
- **Constraint checking**: Weight and volume limits must never be exceeded.
- **Optimization**: Bin packing algorithm to maximize truck utilization.
- **Tracking**: Real-time status of each truck's loading progress.

### Non-Functional Requirements
- **Thread safety**: No double-assignment of packages; no constraint violations.
- **Atomic updates**: Package assignment and constraint check are atomic.
- **Scalability**: Support 100+ trucks and 10K+ packages.
- **Fairness**: Workers don't starve waiting for truck locks.

## Key Design Decisions
- **Lock per truck**: Fine-grained locking — each truck has its own lock.
- **Atomic compare-and-swap**: Package assignment uses CAS to prevent double-assignment.
- **Bin packing**: First-fit decreasing algorithm for volume optimization.
- **Semaphore**: Limit concurrent workers per truck to avoid contention.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Package     │────►│    Truck     │────►│   Worker     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - packageId  │     │ - truckId    │     │ - workerId   │
│ - weight     │     │ - maxWeight  │     ├──────────────┤
│ - volume     │     │ - currentWgt │     │ + load()     │
│ - destination│     │ - currentVol │     │ + assign()   │
│ - assignedTo │     │ - lock       │     └──────────────┘
└──────────────┘     ├──────────────┤
                     │ + addPackage │
                     │ + getStatus  │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Fine-Grained Locking
- **Per-truck lock**: Each truck has its own `ReentrantLock`; workers loading different trucks don't block.
- **Staff insight**: A global lock would serialize all loading — terrible throughput. Per-truck locks allow parallel loading of different trucks.

### Double-Assignment Prevention
- **CAS on package**: Use `AtomicReference.compareAndSet(null, truck)` to assign a package.
- **Staff insight**: Two workers might both pick the same package. CAS ensures only one succeeds. The loser picks the next package.

### Bin Packing Optimization
- **First-fit decreasing**: Sort packages by size (descending); place each in the first truck that fits.
- **Staff insight**: Bin packing is NP-hard. First-fit decreasing gives a ~11% approximation ratio. For real-world use, use genetic algorithms or simulated annealing for better utilization.

### Constraint Checking
- **Atomic check-and-update**: Check weight/volume and update atomically within the truck lock.
- **Staff insight**: Never check constraints outside the lock — another thread might modify the truck state between check and update. Hold the lock for the entire check-and-update operation.
