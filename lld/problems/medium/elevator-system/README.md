# Elevator System

## Problem Statement (Staff-Level)

Design an elevator system for a 50-story building with 8 elevators that handles peak-hour traffic, emergency situations, energy optimization, and real-time dispatch. The system must minimize wait time (<30s p95), handle 500+ floor requests/minute, and support accessibility features.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Multiple elevators**: 8 elevators with different capacities (standard, express, freight)
- **Dispatch algorithm**: Optimize for minimum wait time and energy usage
- **Peak-hour handling**: Express mode (skip floors), bank grouping (up/down zones)
- **Emergency mode**: Fire alarm, power failure, manual override
- **Accessibility**: Braille buttons, voice announcements, wheelchair mode
- **Destination dispatch**: Passengers enter destination; system assigns optimal elevator
- **Real-time status**: Floor display, direction indicator, ETA estimation
- **Maintenance mode**: Scheduled maintenance, fault detection, self-diagnosis

### Non-Functional Requirements
- **Scale**: 50 floors; 8 elevators; 500+ requests/minute during peak
- **Latency**: Wait time < 30s p95; dispatch decision < 100ms
- **Availability**: 99.999% uptime; graceful degradation on elevator failure
- **Safety**: Emergency stop, overload detection, door obstruction sensor
- **Energy**: Minimize idle time; regenerative braking; sleep mode

## Key Design Decisions
- **Dispatch algorithm**: Modified SCAN (elevator algorithm) + destination dispatch
- **Bank grouping**: Express elevators (lobby → top floors); local elevators (zone-based)
- **Concurrency**: Thread-per-elevator with shared request queue
- **State machine**: Each elevator has explicit states (idle, moving, door_open, emergency)

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Building   │────►│  ElevatorBank│────►│   Elevator   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - banks      │     │ - elevators  │     │ - capacity   │
│ - dispatcher │     │ - bankType   │     │ - currentFlr │
└──────────────┘     └──────────────┘     │ - direction  │
           │                               │ - state      │
    ┌──────┴──────┐                        └──────────────┘
    │ Dispatcher  │
    ├─────────────┤
    │ - algo      │
    │ - requestQ  │
    └─────────────┘
```

## Staff-Level Design Considerations

### Dispatch Algorithm
- **SCAN (Elevator)**: Sweep up/down; simple but suboptimal
- **LOOK**: Variant of SCAN; reverse at last request
- **Destination dispatch**: Assign elevator at entry; minimize stops
- **Staff insight**: Use **destination dispatch** for high-rise buildings — reduces stops by 40%

### Concurrency Model
- **Thread-per-elevator**: Each elevator runs in its own thread
- **Shared request queue**: Thread-safe queue with priority (emergency > normal)
- **Staff insight**: Use **lock-free queue** (ConcurrentLinkedQueue) for request dispatch

### State Machine
- States: `IDLE → MOVING_UP/MOVING_DOWN → DOOR_OPEN → DOOR_CLOSED → EMERGENCY`
- **Staff insight**: Use **State pattern** for clean state transitions; avoid if-else chains
