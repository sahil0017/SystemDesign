# Warehouse Packing Simulation (Concurrency)

## Problem Statement

Design a multi-threaded warehouse packing simulation where multiple workers concurrently pack items into boxes and pallets. Each box and pallet has weight and volume constraints, and items must be assigned without exceeding limits or duplicating assignments. Workers coordinate to optimize packing efficiency.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Item**: Each item has weight, volume, fragility, and destination.
- **Box**: Each box has max weight, max volume, and item list.
- **Pallet**: Each pallet holds multiple boxes with weight and height constraints.
- **Packing**: Workers concurrently assign items to boxes and boxes to pallets.
- **Constraint checking**: Weight, volume, and height limits must never be exceeded.
- **Optimization**: Maximize box and pallet utilization.
- **Fragility handling**: Fragile items must be placed on top, not at the bottom.

### Non-Functional Requirements
- **Thread safety**: No double-assignment of items; no constraint violations.
- **Atomic updates**: Item assignment and constraint check are atomic.
- **Scalability**: Support 50+ workers, 1K+ boxes, and 10K+ items.
- **Fairness**: Workers don't starve waiting for box locks.

## Key Design Decisions
- **Lock per box**: Fine-grained locking — each box has its own lock.
- **Atomic compare-and-swap**: Item assignment uses CAS to prevent double-assignment.
- **3D bin packing**: Algorithm to optimize box and pallet utilization.
- **Semaphore**: Limit concurrent workers per pallet to avoid contention.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Item      │────►│     Box      │────►│   Pallet     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - itemId     │     │ - boxId      │     │ - palletId   │
│ - weight     │     │ - maxWeight  │     │ - maxWeight  │
│ - volume     │     │ - currentWgt │     │ - maxHeight  │
│ - fragility  │     │ - items      │     │ - boxes      │
│ - assignedTo │     │ - lock       │     │ - lock       │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Staff-Level Design Considerations

### Fine-Grained Locking
- **Per-box lock**: Each box has its own `ReentrantLock`; workers packing different boxes don't block.
- **Staff insight**: A global lock would serialize all packing — terrible throughput. Per-box locks allow parallel packing of different boxes. For pallet-level operations, use a separate per-pallet lock.

### Double-Assignment Prevention
- **CAS on item**: Use `AtomicReference.compareAndSet(null, box)` to assign an item.
- **Staff insight**: Two workers might both pick the same item. CAS ensures only one succeeds. The loser picks the next item from the queue.

### 3D Bin Packing
- **Bottom-left heuristic**: Place items starting from the bottom-left corner of the box.
- **Staff insight**: 3D bin packing is NP-hard. Use heuristics like bottom-left, first-fit decreasing, or genetic algorithms. For real-world warehouses, use specialized libraries like OR-Tools.

### Fragility Handling
- **Layer-based packing**: Fragile items are placed in the top layer; heavy items at the bottom.
- **Staff insight**: This is a constraint satisfaction problem. Use a priority queue where fragile items have lower priority for bottom placement. Validate constraints before finalizing each box.
