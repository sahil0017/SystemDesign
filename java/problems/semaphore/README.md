# Semaphore

## Problem Statement

Implement a counting semaphore that controls access to a resource with a fixed number of permits.

**Reference**: AlgoMaster

## Requirements
- **Permits**: Fixed number of permits. acquire() blocks if no permits available.
- **Release**: release() returns a permit.
- **Fairness**: Optional fair mode (FIFO ordering).

## Key Design Decisions
- **Atomic counter**: Count of available permits.
- **Wait queue**: Threads waiting for permits.

## Staff-Level Design Considerations
- **Use case**: Limit concurrent access to a resource pool (e.g., database connections).
- **Staff insight**: Semaphore with 1 permit = Mutex. Use Semaphore for N permits. Java's `Semaphore` uses a FIFO queue for fair mode. Non-fair mode allows barging (faster but less fair).
