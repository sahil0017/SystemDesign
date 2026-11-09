# Bank Transaction (Concurrency)

## Problem Statement

Design a thread-safe bank account system where multiple threads (ATM users, online banking, mobile app) can concurrently perform deposits, withdrawals, and transfers without race conditions, deadlocks, or inconsistent balances.

**Reference**: LLD Coding, AlgoMaster

## Requirements

### Functional Requirements
- **Deposit**: Add money to an account from any thread.
- **Withdraw**: Remove money from an account; prevent overdraft unless allowed.
- **Transfer**: Move money between two accounts atomically.
- **Balance inquiry**: Read current balance without blocking writes entirely.
- **Transaction history**: Log all transactions with timestamps and thread IDs.
- **Overdraft protection**: Configurable per account; reject or allow negative balance.

### Non-Functional Requirements
- **Thread safety**: No race conditions on shared balance.
- **Deadlock-free**: No circular waits during transfers between accounts.
- **Consistency**: Balance never goes negative (unless overdraft allowed).
- **Throughput**: Handle 10K+ transactions per second under high contention.

## Key Design Decisions
- **Lock ordering**: Always lock accounts in consistent order (e.g., by account ID) to prevent deadlocks.
- **ReadWriteLock**: Use for balance inquiries (shared read) vs deposits/withdrawals (exclusive write).
- **Atomic operations**: Use `AtomicLong` for balance when simple increment/decrement suffices.
- **Transaction log**: Append-only log for audit trail; write-ahead before modifying balance.

## Class Diagram

```
┌──────────────────┐     ┌──────────────────┐
│   BankAccount    │────►│  Transaction     │
├──────────────────┤     ├──────────────────┤
│ - accountId      │     │ - transactionId  │
│ - balance: Atomic│     │ - type           │
│ - lock: Reentrant│     │ - amount         │
│ - overdraftLimit │     │ - timestamp      │
├──────────────────┤     │ - threadId       │
│ + deposit()      │     └──────────────────┘
│ + withdraw()     │
│ + transfer()     │
│ + getBalance()   │
└──────────────────┘
```

## Staff-Level Design Considerations

### Deadlock Prevention
- **Lock ordering**: Always acquire locks in ascending order of account ID. This breaks circular wait — one of the four Coffman conditions for deadlock.
- **Staff insight**: Never use `synchronized` on individual account objects for transfers. Use explicit `ReentrantLock` with ordered acquisition.

### ReadWriteLock for Balance
- **Shared reads**: Multiple threads can read balance simultaneously.
- **Exclusive writes**: Only one thread can modify balance at a time.
- **Staff insight**: `ReadWriteLock` improves throughput for read-heavy workloads (balance inquiries >> transactions). But beware writer starvation — use fair mode if needed.

### Atomic vs Synchronized
- **AtomicLong**: Lock-free CAS operations for simple balance updates. No deadlock risk.
- **Staff insight**: `AtomicLong` works for single-account operations. For compound operations (withdraw + transfer), you still need locks. Don't overuse atomics — they don't solve multi-object consistency.

### Transaction Isolation
- **Write-ahead log**: Record transaction before modifying balance. Enables recovery on crash.
- **Staff insight**: This is the same pattern as database WAL (Write-Ahead Logging). In production, use a real database with ACID transactions, not in-memory locks.
