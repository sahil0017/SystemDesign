# CricInfo (Cricket Scorecard System)

## Problem Statement

Design a live cricket scorecard system like CricInfo that provides real-time scores, ball-by-ball commentary, player statistics, match schedules, and historical data.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Live scores**: Real-time updates for runs, wickets, overs, and run rate.
- **Ball-by-ball**: Commentary for each ball delivery with event type (run, wicket, wide, no-ball).
- **Player stats**: Batting and bowling statistics; career averages; strike rates.
- **Match schedule**: Upcoming matches, series, and tournaments.
- **Scorecard**: Full match scorecard with innings breakdown, fall of wickets, partnerships.
- **Historical data**: Archive of past matches; record queries (most runs, best bowling).
- **Multi-match support**: Handle multiple simultaneous matches (IPL + international).

### Non-Functional Requirements
- **Real-time**: Score updates < 1s latency; WebSocket push to clients.
- **Scale**: 100M+ concurrent viewers during World Cup finals.
- **Reliability**: 99.99% uptime during live matches; no lost updates.

## Key Design Decisions
- **Event sourcing**: Each ball delivery is an immutable event; replay events to reconstruct state.
- **WebSocket**: Push-based updates for real-time score changes.
- **Caching**: Aggressive caching of scorecard state; CDN for static match data.
- **Write optimization**: Single writer per match to ensure consistency.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Match     │────►│    Innings   │────►│   Delivery   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - matchId    │     │ - inningsNum │     │ - ballNum    │
│ - format     │     │ - teamBatting│     │ - batsman    │
│ - status     │     │ - teamBowling│     │ - bowler     │
│ - teams      │     │ - runs       │     │ - runs       │
└──────────────┘     │ - wickets    │     │ - wicket     │
                     └──────────────┘     │ - commentary │
                                          └──────────────┘
```

## Staff-Level Design Considerations

### Event Sourcing for Scores
- **Immutable events**: Each ball is an event (matchId, over, ball, batsman, bowler, runs, wicket).
- **Staff insight**: Event sourcing is perfect for cricket. You can replay events to reconstruct any point in the match. This is the same pattern used in financial trading systems.

### Real-Time Updates
- **WebSocket**: Server pushes ball-by-ball updates to connected clients.
- **Staff insight**: For 100M+ viewers, use a pub/sub backend (Kafka → WebSocket gateway). The score entry system publishes to Kafka; gateways fan out to WebSocket connections.

### Player Statistics
- **Pre-computed aggregates**: Maintain running totals for player stats, updated on each delivery.
- **Staff insight**: Never compute career averages from raw delivery data on every request. Maintain materialized views that update incrementally.
