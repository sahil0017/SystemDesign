# ATM

## Problem Statement

Design an ATM (Automated Teller Machine) system that supports cash withdrawal, deposit, balance inquiry, fund transfer, and PIN management with proper security and transaction handling.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Authentication**: PIN-based authentication with card number; lock account after 3 failed attempts.
- **Cash withdrawal**: Withdraw cash in denominations; check balance and daily limits.
- **Cash deposit**: Accept cash and credits; validate denomination.
- **Balance inquiry**: Display current account balance and recent transactions.
- **Fund transfer**: Transfer between accounts; validate source and destination.
- **PIN change**: Allow users to change their PIN with old PIN verification.
- **Transaction history**: Last 10 transactions displayed on receipt.

### Non-Functional Requirements
- **Security**: PIN encrypted at rest; TLS for communication; session timeout after 2 minutes.
- **Availability**: 99.9% uptime; graceful degradation when bank backend is down.
- **Concurrency**: Handle multiple ATMs processing transactions simultaneously.
- **Audit**: All transactions logged with timestamp, ATM ID, and user ID.

## Key Design Decisions
- **State machine**: Idle → Authenticated → Transaction → Receipt → Idle.
- **Strategy pattern**: Different transaction types (Withdraw, Deposit, Transfer) as strategies.
- **Denomination management**: Greedy algorithm for optimal cash dispensing.
- **Transaction isolation**: Each transaction is atomic; rollback on failure.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     ATM      │────►│   BankScreen │     │   Card       │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - atmId      │     │ - session    │     │ - cardNum    │
│ - cashDisp   │     │ - user       │     │ - pinHash    │
│ - keypad     │     └──────────────┘     │ - account    │
└──────────────┘                          └──────────────┘
       │
       │ processes
┌──────┴───────┐
│ Transaction  │◄── Abstract
├──────────────┤
│ + execute()  │
└──────┬───────┘
       │
       ├─► WithdrawalTransaction
       ├─► DepositTransaction
       ├─► BalanceInquiry
       └─► FundTransfer
```

## Staff-Level Design Considerations

### Cash Dispensing Algorithm
- **Greedy approach**: Use largest denominations first. Works for standard currency sets.
- **Staff insight**: Greedy doesn't work for arbitrary denominations (e.g., {1, 3, 4} to make 6). Use DP for general case, but greedy is fine for real-world currency.

### Security
- **PIN storage**: Never store plain-text PINs. Use bcrypt or PBKDF2 with salt.
- **Staff insight**: Hash the PIN, don't encrypt it. Encryption is reversible; hashing is not. This is a common interview trap.

### Transaction Atomicity
- **ACID**: Each transaction is a single atomic operation. Use database transactions with proper isolation level.
- **Staff insight**: Use SERIALIZABLE isolation for fund transfers to prevent lost updates. READ COMMITTED is insufficient.
