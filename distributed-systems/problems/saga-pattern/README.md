# Saga Pattern

## Overview

Saga pattern manages distributed transactions across multiple services. For staff engineers, Saga is the **standard approach** for maintaining data consistency in microservices where ACID transactions span service boundaries.

## Types

### Choreography
- Each service publishes events
- Other services react to events
- Decoupled but hard to trace
- **Staff insight**: Use for **simple, well-understood flows** (3-4 steps). Hard to debug at scale.

### Orchestration
- Central coordinator manages flow
- Clear flow control
- Single point of failure
- **Staff insight**: Use for **complex workflows** with clear state machines. Easier to debug and monitor.

## Key Concepts

- **Compensating Transaction**: Undo completed transaction
- **Forward Recovery**: Retry failed step
- **Backward Recovery**: Compensate completed steps
- **Saga state**: Tracks progress of the saga; store in database for recovery
- **Timeout**: Max duration for saga completion; cancel and compensate on timeout

## Implementation

1. Start saga
2. Execute local transaction
3. Publish event / call next service
4. On success: proceed to next step
5. On failure: execute compensating transactions in reverse order

## Example: E-commerce Order Saga

```
1. Create Order (pending) → 2. Reserve Inventory → 3. Process Payment → 4. Ship Order
   ↓                              ↓                      ↓                    ↓
  Compensate:                 Compensate:            Compensate:          Compensate:
  Cancel Order                Release Inventory      Refund Payment        Cancel Shipment
```

- **Step 1 fails**: No compensation needed
- **Step 2 fails**: Compensate step 1 (cancel order)
- **Step 3 fails**: Compensate steps 2, 1 (release inventory, cancel order)
- **Step 4 fails**: Compensate steps 3, 2, 1 (refund, release, cancel)

## Key Design Decisions

### Compensation Design
- **Idempotent**: Same compensation can be executed multiple times safely
- **May fail**: Compensation itself may fail; need retry and alerting
- **Staff insight**: Design compensations as **best-effort**. If compensation fails, alert for manual intervention.

### Saga State Management
- **Persistent state**: Store saga progress in database for recovery
- **Event sourcing**: Store saga events; reconstruct state by replay
- **Staff insight**: Use **event sourcing** for sagas — full audit trail and easy debugging.

## Staff-Level Saga Checklist

1. **Use orchestration for complex sagas**: Centralized control; easier to debug
2. **Make compensations idempotent**: Same compensation can be retried safely
3. **Store saga state persistently**: Recover from crashes; full audit trail
4. **Set saga timeouts**: Cancel and compensate on timeout
5. **Handle compensation failures**: Alert for manual intervention
6. **Use event sourcing**: Full audit trail; easy debugging and replay
7. **Monitor saga progress**: Track duration, failure rate, compensation rate
8. **Test failure scenarios**: Simulate step failures and compensation failures
4. On failure, execute compensating transaction
5. Complete saga

## Tools

- Temporal
- Camunda
- AWS Step Functions
- Azure Durable Functions
