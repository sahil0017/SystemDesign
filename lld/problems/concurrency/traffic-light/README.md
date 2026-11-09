# Traffic Light (Concurrency)

## Problem Statement

Design a multi-threaded traffic signal control system where multiple intersections operate concurrently. Each intersection has traffic lights that cycle through states (Red, Yellow, Green) while handling emergency vehicle preemption, pedestrian crossings, and sensor-based adaptive timing.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Intersection**: Multiple intersections, each with 4-direction traffic lights.
- **Signal cycle**: Red → Green → Yellow → Red for each direction.
- **Opposite direction sync**: Opposite directions share the same signal state.
- **Emergency preemption**: Emergency vehicles can request immediate green light.
- **Pedestrian crossing**: Pedestrian buttons trigger walk/don't-walk signals.
- **Sensor-based timing**: Adaptive timing based on traffic density sensors.
- **Timer management**: Configurable duration for each signal state.

### Non-Functional Requirements
- **Thread safety**: Each intersection runs in its own thread; shared state is protected.
- **No race conditions**: Signal transitions are atomic.
- **Responsiveness**: Emergency preemption within 1 second.
- **Scalability**: Support 100+ intersections operating concurrently.

## Key Design Decisions
- **State pattern**: Each signal state (Red, Yellow, Green) is a separate class with transition logic.
- **Observer pattern**: Sensors, emergency services, and pedestrian buttons observe signal changes.
- **Semaphore**: Control access to shared resources (e.g., emergency channel).
- **ScheduledExecutorService**: Timer-based state transitions.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Intersection │────►│ TrafficLight │────►│    Signal    │◄── Interface
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - id         │     │ - direction  │     │ + display()  │
│ - lights     │     │ - signal     │     │ + next()     │
│ - controller │     │ - timer      │     └──────┬───────┘
├──────────────┤     └──────────────┘            │
│ + change()   │                      ┌──────────┼──────────┐
│ + emergency  │                      │          │          │
└──────────────┘                 ┌─────┴──┐ ┌────┴──┐ ┌────┴──┐
                                 │  Red   │ │Yellow │ │ Green │
                                 └────────┘ └───────┘ └───────┘
```

## Staff-Level Design Considerations

### State Machine Thread Safety
- **Atomic transitions**: Use `volatile` or `AtomicReference` for current signal state.
- **Staff insight**: Signal transitions must be visible to all threads immediately. Without `volatile`, a thread might see a stale signal state, causing accidents.

### Emergency Preemption
- **Interrupt mechanism**: Use `interrupt()` on the signal thread to break current cycle.
- **Staff insight**: Don't use busy-waiting for emergency requests. Use a `BlockingQueue` where emergency requests are enqueued and processed immediately.

### Adaptive Timing
- **Sensor data**: Threads read sensor data concurrently; use `ConcurrentHashMap` for sensor readings.
- **Staff insight**: Sensor data is eventually consistent. Don't block signal transitions waiting for fresh sensor data — use the last known good value.

### Timer Management
- **ScheduledExecutorService**: Schedule next state transition; cancel on emergency.
- **Staff insight**: Don't use `Thread.sleep()` for timing — it blocks the thread and can't be cancelled precisely. Use `ScheduledExecutorService.schedule()` for cancellable timers.
