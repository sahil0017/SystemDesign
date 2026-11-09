# Multiplayer Game Sync (Concurrency)

## Problem Statement

Design a multi-threaded multiplayer game synchronization system (like "Among Us" or MOBA games) where multiple player threads update game state concurrently. The system must maintain consistency, handle conflicts, and ensure all players see a synchronized game world.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Game state**: Shared world state (player positions, objects, events).
- **Player actions**: Each player thread sends actions (move, attack, interact).
- **State synchronization**: Broadcast state updates to all connected players.
- **Conflict resolution**: Handle conflicting actions from multiple players on the same resource.
- **Game ticks**: Fixed-rate game loop (e.g., 20 ticks/sec) for deterministic updates.
- **Snapshot**: Periodic state snapshots for new players joining mid-game.

### Non-Functional Requirements
- **Thread safety**: Concurrent player actions don't corrupt game state.
- **Low latency**: State updates broadcast within 50ms.
- **Consistency**: All players see the same game state within one tick.
- **Scalability**: Support 100+ players in a single game session.

## Key Design Decisions
- **Copy-on-write**: Game state is immutable; each tick creates a new snapshot.
- **Lock-free queue**: Player actions are collected in a `ConcurrentLinkedQueue` per tick.
- **ReadWriteLock**: Multiple readers (state queries) vs single writer (tick update).
- **Event bus**: Decouple action processing from state updates.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Player     │────►│  GameState   │────►│    World     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - playerId   │     │ - tick       │     │ - entities   │
│ - position   │     │ - snapshot   │     │ - objects    │
│ - actionQ    │     │ - lock       │     ├──────────────┤
├──────────────┤     ├──────────────┤     │ + update()   │
│ + sendAction │     │ + applyTick()│     │ + snapshot() │
│ + update()   │     │ + getSnapshot│     └──────────────┘
└──────────────┘     └──────────────┘
```

## Staff-Level Design Considerations

### Copy-on-Write for Game State
- **Immutable snapshots**: Each tick creates a new immutable state; readers always see consistent state.
- **Staff insight**: This eliminates read-write conflicts. Readers never block writers, and writers never block readers. The trade-off is memory — old snapshots must be garbage collected.

### Lock-Free Action Collection
- **ConcurrentLinkedQueue**: Players enqueue actions without locking.
- **Staff insight**: `ConcurrentLinkedQueue` uses CAS operations internally. It's lock-free but not wait-free — under extreme contention, threads may spin. For game ticks, this is acceptable.

### Game Tick Synchronization
- **CyclicBarrier**: All player threads sync at each tick boundary.
- **Staff insight**: `CyclicBarrier` ensures all threads reach the tick boundary before processing. Alternatively, use a `ScheduledExecutorService` with a fixed-rate timer for the game loop.

### Conflict Resolution
- **Last-write-wins**: Later actions in a tick override earlier ones.
- **Staff insight**: For deterministic games, use operational transformation (OT) or CRDTs. For real-time games, last-write-wins with interpolation is the practical choice.
