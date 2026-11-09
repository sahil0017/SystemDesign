# Snake Game

## Problem Statement (Staff-Level)

Design a Snake game system with a game board, snake movement, food generation, collision detection, score tracking, and game states (menu, playing, paused, game over) using state machine and strategy patterns.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Game board**: Grid-based board with configurable size (e.g., 20x20 to 100x100).
- **Snake movement**: Directional movement (up/down/left/right); snake grows when eating food.
- **Food generation**: Random food placement on empty cells; multiple food types with different points.
- **Collision detection**: Wall collision, self-collision, and food collision.
- **Score tracking**: Points for food eaten; high score persistence.
- **Game states**: Menu, playing, paused, game over with state transitions.
- **Speed control**: Game speed increases as score increases; configurable difficulty.

### Non-Functional Requirements
- **Scale**: Board size up to 1000x1000; snake length up to 10,000 cells.
- **Latency**: Movement update < 16ms (60 FPS); collision detection < 1ms.
- **Extensibility**: Support power-ups, obstacles, and multiplayer modes.

## Key Design Decisions
- **State machine**: Game states (Menu, Playing, Paused, GameOver) with explicit transitions.
- **Deque for snake**: O(1) add at head (new position) and remove from tail (old position).
- **2D array for board**: O(1) cell access for collision detection.
- **Strategy pattern**: Different movement strategies (AI, keyboard, touch).

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   GameEngine │────►│    Board     │────►│     Cell     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - state      │     │ - grid[][]   │     │ - x, y       │
│ - snake      │     │ - width      │     │ - type       │
│ - score      │     │ - height     │     └──────────────┘
└──────────────┘     └──────────────┘
           │
    ┌──────┴──────┐
    │    Snake    │
    ├─────────────┤
    │ - body      │  (Deque<Point>)
    │ - direction │
    └─────────────┘
```

## Staff-Level Design Considerations

### Snake Representation
- **Deque**: Store snake body as a deque of points. Add head on movement, remove tail (unless eating).
- **Collision optimization**: Use a HashSet of snake body positions for O(1) self-collision check.
- **Staff insight**: A simple array is O(n) for collision detection. With a snake length of 10,000, that's 10,000 checks per frame. A HashSet reduces it to O(1). Maintain the HashSet in sync with the deque.

### State Machine
- **States**: Menu → Playing → Paused → Playing → GameOver → Menu.
- **Transitions**: Explicit and validated; no invalid transitions (e.g., GameOver → Playing without reset).
- **Staff insight**: The state machine pattern makes the game logic clean and extensible. Each state can have its own update/render logic. Use an enum for states and a switch/map for transitions.

### Food Generation
- **Random placement**: Pick a random cell; reject if occupied by snake (retry).
- **Efficiency**: When snake covers > 50% of the board, maintain a list of empty cells for O(1) food placement.
- **Staff insight**: Naive random placement with retry degrades as the board fills. When the snake is long, use a Fisher-Yates shuffle on empty cells for guaranteed O(1) placement.

### Extensibility
- **Power-ups**: Speed boost, ghost mode (pass through walls), shrink.
- **Obstacles**: Static walls on the board that act like self-collision.
- **Multiplayer**: Two snakes on one board; last alive wins.
- **Staff insight**: Design the board as a grid of cells with types (empty, food, obstacle, power-up). This makes adding new cell types trivial. Use the strategy pattern for different game modes (single, multiplayer, AI).
