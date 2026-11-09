# Traffic Signal Control System

## Problem Statement

Design a traffic signal control system that manages traffic lights at intersections, supports timed and sensor-based modes, handles emergency vehicle preemption, and provides real-time monitoring.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Signal management**: Control multiple signals at an intersection (Red, Yellow, Green).
- **Timed mode**: Predefined timing cycles for each direction.
- **Sensor-based mode**: Adjust timing based on real-time traffic density from sensors.
- **Emergency preemption**: Override normal cycle for emergency vehicles (ambulance, fire truck).
- **Pedestrian crossing**: Walk/Don't Walk signals with countdown timer.
- **Night mode**: Flashing yellow during low-traffic hours.
- **Monitoring dashboard**: Real-time view of all intersections and signal states.

### Non-Functional Requirements
- **Reliability**: 99.99% uptime; fail-safe to flashing yellow on system failure.
- **Latency**: Signal change < 100ms; emergency preemption < 50ms.
- **Concurrency**: Coordinate adjacent intersections to prevent conflicting signals.

## Key Design Decisions
- **State machine**: Each signal follows Red → Green → Yellow → Red cycle.
- **Strategy pattern**: Timed vs sensor-based vs emergency modes as strategies.
- **Observer pattern**: Dashboard and analytics observe signal state changes.
- **Priority queue**: Emergency requests have highest priority; interrupt current cycle.

## Class Diagram

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│   Intersection   │────►│    Signal    │────►│   Sensor     │
├──────────────────┤     ├──────────────┤     ├──────────────┤
│ - intersectionId │     │ - signalId   │     │ - sensorId   │
│ - signals        │     │ - direction  │     │ - type       │
│ - controller     │     │ - state      │     │ - density    │
└──────────────────┘     │ - timer      │     └──────────────┘
                         └──────────────┘
                               │
                         ┌─────┴──────┐
                         │ Controller │◄── Abstract
                         ├────────────┤
                         │ + control()│
                         └─────┬──────┘
                               │
                    ┌──────────┼──────────┐
                    ┌──────────┴──┐ ┌─────┴──────────┐
                    │ TimedCtrl   │ │ SensorBasedCtrl│
                    └─────────────┘ └────────────────┘
```

## Staff-Level Design Considerations

### Signal Coordination
- **Green wave**: Coordinate adjacent intersections to create a continuous green path.
- **Staff insight**: This is a classic optimization problem. Use dynamic programming to find optimal offset timing between intersections.

### Emergency Preemption
- **Priority interrupt**: Emergency vehicle signal preempts all other logic.
- **Staff insight**: Use a priority queue where emergency requests have priority 0. Normal cycle changes have priority 10. This ensures O(1) emergency response.

### Fail-Safe Design
- **Default state**: On power loss or system failure, signals default to flashing yellow (4-way stop behavior).
- **Staff insight**: Safety-critical systems always need a fail-safe default. Never leave signals in an undefined state.
