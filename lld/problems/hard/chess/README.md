# Chess

## Problem Statement (Staff-Level)

Design a multiplayer chess game engine that supports standard chess rules, move validation with all special moves (castling, en passant, promotion), AI opponent with minimax + alpha-beta pruning, real-time online multiplayer, game state persistence, PGN import/export, and tournament mode. The system should handle 10K+ concurrent games with real-time synchronization.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Board representation**: 8x8 grid; piece positioning; FEN notation support
- **Move validation**: Legal move generation; check/checkmate/stalemate detection
- **Special moves**: Castling (kingside/queenside), en passant, pawn promotion
- **AI opponent**: Minimax with alpha-beta pruning; piece-square tables; opening book
- **Online multiplayer**: Real-time move sync; turn timer; disconnect handling
- **Game state**: Save/resume; undo/redo; PGN import/export; game replay
- **Tournament**: Swiss/German system; ELO ratings; leaderboard
- **Analysis engine**: Post-game analysis; blunder detection; engine evaluation

### Non-Functional Requirements
- **Scale**: 10K+ concurrent games; 100K+ players
- **Latency**: Move validation < 10ms; AI move (depth 3) < 500ms
- **Fairness**: Server-side move validation; anti-cheat (engine detection)
- **Persistence**: Game state saved every move; PGN format for portability

## Key Design Decisions
- **Board representation**: 2D array or bitboard for efficient move generation
- **Move generation**: Template-based legal move generation; bitboard optimization
- **AI algorithm**: Minimax + alpha-beta + transposition table + quiescence search
- **Network**: WebSocket for real-time; server-authoritative game state

## Staff-Level Design Considerations

### Bitboard Representation
- **64-bit integers**: Each piece type has a bitboard; fast bitwise operations
- **Move generation**: Precomputed attack tables; magic bitboards for sliders
- **Staff insight**: Bitboards enable **100x faster move generation** than 2D arrays

### Move Validation
- **Server-authoritative**: All moves validated on server; client is just a view
- **Check detection**: King under attack check after every move
- **Staff insight**: Use **Command pattern** for moves — enables undo/redo and replay
