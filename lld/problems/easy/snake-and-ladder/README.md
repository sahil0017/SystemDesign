# Snake and Ladder

## Problem Statement (Staff-Level)

Design a multiplayer Snake and Ladder game engine that supports 2-6 players, multiple board configurations, AI opponents, real-time multiplayer over network, move validation, game state persistence, and tournament mode. The system should handle 10K+ concurrent games with real-time synchronization.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Board configuration**: Customizable board size (10x10 default); configurable snakes/ladders
- **Multiplayer**: 2-6 players; local and online multiplayer
- **AI opponents**: Difficulty levels (easy, medium, hard) with strategy-based moves
- **Dice mechanics**: Random dice roll; special rules (roll 6 = extra turn)
- **Move validation**: Snake/ladder transitions; win condition (exact roll to reach 100)
- **Game state**: Save/resume; undo last move; spectator mode
- **Tournament**: Bracket-based elimination; leaderboard; rankings
- **Real-time sync**: WebSocket-based state synchronization for online play

### Non-Functional Requirements
- **Scale**: 10K+ concurrent games; 100K+ players
- **Latency**: Move processing < 100ms; state sync < 200ms
- **Fairness**: Cryptographically secure random dice; anti-cheat validation
- **Persistence**: Game state saved every move; resume after disconnect

## Key Design Decisions
- **Board representation**: Graph with nodes (cells) and edges (snakes/ladders)
- **Game state**: Immutable state objects; state machine for game flow
- **Concurrency**: Actor model per game; message-based communication
- **Network**: WebSocket for real-time; operational transforms for conflict resolution

## Staff-Level Design Considerations

### Board as Graph
- **Nodes**: Cells 1-100; **Edges**: Normal moves + snake/ladder shortcuts
- **Pathfinding**: BFS for shortest path analysis (AI strategy)
- **Staff insight**: Model board as **directed graph** — enables advanced AI and analytics

### Game State Management
- **Immutable state**: Each move creates new state; enables undo and replay
- **State machine**: `WAITING → PLAYING → PAUSED → FINISHED`
- **Staff insight**: Use **Event Sourcing** — store moves as events; reconstruct state by replay
