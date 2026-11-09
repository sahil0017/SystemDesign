# Cricinfo Scorecard (LLD)

## Problem Statement (Staff-Level)

Design a real-time cricket scorecard system (Cricinfo-like) that tracks matches, innings, overs, balls, runs, wickets, and player statistics with event sourcing and WebSocket-based real-time updates.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Match management**: Create matches with teams, venue, format (T20, ODI, Test), and schedule.
- **Innings tracking**: Track innings with batting and bowling teams; handle declarations and follow-ons.
- **Ball-by-ball updates**: Record each ball with runs, wickets, extras, and commentary.
- **Player statistics**: Track runs, balls faced, fours, sixes, strike rate for batsmen; overs, maidens, runs, wickets for bowlers.
- **Real-time updates**: Push scorecard updates to clients via WebSocket.
- **Historical data**: Store and query past match results and player records.

### Non-Functional Requirements
- **Scale**: 100+ concurrent matches; 1M+ viewers per match.
- **Latency**: Ball update to client < 500ms; scorecard load < 1s.
- **Consistency**: Scorecard must be accurate; no lost or duplicate ball events.
- **Availability**: 99.9% uptime; scorecard survives server restarts.

## Key Design Decisions
- **Event sourcing**: Each ball is an immutable event; scorecard is a projection of events.
- **WebSocket**: Real-time push for ball updates; fallback to polling for incompatible clients.
- **Aggregate pattern**: Match is an aggregate root; innings, overs, and balls are child entities.
- **CQRS**: Separate read model (denormalized scorecard) from write model (ball events).

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Match     │────►│   Innings    │────►│     Over     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - teams      │     │ - batsmen    │     │ - balls[]    │
│ - format     │     │ - bowlers    │     │ - runs       │
│ - innings[]  │     │ - overs[]    │     │ - wickets    │
└──────────────┘     │ - score      │     └──────────────┘
                     └──────────────┘
                          │
                     ┌────┴────┐
                     │  Ball   │
                     ├─────────┤
                     │ - runs  │
                     │ - type  │
                     └─────────┘
```

## Staff-Level Design Considerations

### Event Sourcing
- **Ball events**: Each ball is an immutable event (e.g., `{ball: "1.1", batsman: "Kohli", runs: 4, type: "FOUR"}`).
- **Replay**: Rebuild the entire scorecard by replaying all ball events from scratch.
- **Staff insight**: Event sourcing is the perfect fit for cricket. Every ball is a discrete event, and the scorecard is a derived state. This makes it easy to audit, replay, and debug. Store events in an append-only log (Kafka or a database table).

### Real-Time Updates
- **WebSocket**: Push ball events to connected clients in real-time.
- **Fan-out**: Use Redis Pub/Sub to broadcast events to multiple server instances.
- **Reconnection**: Clients can request missed events since their last known ball number.
- **Staff insight**: At 1M viewers, you need a hierarchical fan-out. Each server instance subscribes to match events via Redis Pub/Sub and pushes to its connected WebSocket clients. Use a message broker (Kafka) as the source of truth for event distribution.

### Scorecard Computation
- **Running totals**: Maintain running totals (runs, wickets, overs) as events are processed.
- **Player stats**: Update batsman and bowler stats on each ball event.
- **Denormalization**: Store a denormalized scorecard for fast reads; update it on each ball event.
- **Staff insight**: Never compute the scorecard from scratch on each read. Maintain a denormalized read model that's updated in real-time as events arrive. This is the CQRS pattern: writes go to the event store, reads come from the denormalized model.

### Match Formats
- **T20**: 20 overs per side; fixed innings.
- **ODI**: 50 overs per side; fixed innings.
- **Test**: Unlimited overs; declarations, follow-ons, draws.
- **Staff insight**: Use the strategy pattern for different match formats. Each format implements rules for innings, overs, and match result determination. This makes adding new formats (e.g., The Hundred) trivial.
