# Jigsaw Puzzle Builder (Concurrency)

## Problem Statement

Design a multi-threaded jigsaw puzzle builder where multiple threads concurrently attempt to place puzzle pieces. Each piece must be placed exactly once at the correct position, and threads must coordinate to avoid conflicts when multiple pieces compete for adjacent positions.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Puzzle grid**: 2D grid of fixed dimensions (e.g., 50x50 pieces).
- **Puzzle piece**: Each piece has a unique ID, shape (edges), and color/image data.
- **Placement**: Threads attempt to place pieces by matching edge shapes with neighbors.
- **Validation**: Verify that a piece fits at a position by checking all adjacent edges.
- **Progress tracking**: Track number of placed pieces and completion percentage.
- **Completion detection**: Signal when all pieces are placed.

### Non-Functional Requirements
- **Thread safety**: No piece is placed twice; no two pieces occupy the same position.
- **Deadlock-free**: Threads don't wait indefinitely for positions.
- **Scalability**: Support 100+ threads working on a large puzzle.
- **Efficiency**: Maximize parallel placement; minimize idle threads.

## Key Design Decisions
- **Lock per position**: Fine-grained locking on grid positions to minimize contention.
- **Atomic placement**: Use CAS to place a piece atomically.
- **Work queue**: Unplaced pieces in a shared queue; threads pull pieces and find positions.
- **CountDownLatch**: Signal when all pieces are placed.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ PuzzlePiece  │────►│  PuzzleGrid  │────►│  Worker      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - pieceId    │     │ - rows       │     │ - threadId   │
│ - edges      │     │ - cols       │     ├──────────────┤
│ - color      │     │ - cells      │     │ + place()    │
│ - placed     │     │ - lockMap    │     │ + findPos()  │
└──────────────┘     ├──────────────┤     └──────────────┘
                     │ + place()    │
                     │ + validate() │
                     │ + isComplete │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Fine-Grained Locking
- **Per-cell lock**: Each grid cell has its own lock; placing pieces in different areas doesn't block.
- **Staff insight**: A global lock would serialize all placement. Per-cell locks allow true parallelism. Use `ConcurrentHashMap<Point, ReentrantLock>` for dynamic lock management.

### Atomic Piece Placement
- **CAS on piece**: `AtomicReference.compareAndSet(null, piece)` ensures a piece is placed only once.
- **Staff insight**: Two threads might both find the same position for the same piece. CAS ensures only one succeeds. The loser tries the next piece.

### Edge Matching Strategy
- **Neighbor validation**: Check all 4 adjacent edges before placing.
- **Staff insight**: For corner/edge pieces, fewer neighbors need checking. Optimize by checking only existing neighbors — don't wait for pieces that haven't been placed yet.

### Completion Detection
- **CountDownLatch**: Initialize with total piece count; count down on each successful placement.
- **Staff insight**: `CountDownLatch.await()` blocks until all pieces are placed. Use a timeout to detect stuck puzzles (e.g., if a piece's position is locked by a slow thread).
