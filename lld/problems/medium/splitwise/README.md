# Splitwise

## Problem Statement (Staff-Level)

Design a group expense tracking and splitting application like Splitwise that handles multi-user groups, complex expense splitting (equal, unequal, percentage), debt optimization, multi-currency support, recurring expenses, and real-time balance synchronization. The system should support 1M+ users with 100K+ active groups and real-time balance updates.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Group management**: Create/join groups; member roles (admin/member); group categories
- **Expense tracking**: Add expenses with description, amount, category, receipt upload
- **Splitting methods**: Equal split, unequal split, percentage split, share-based split
- **Debt optimization**: Minimize number of transactions to settle all debts
- **Multi-currency**: Automatic currency conversion; exchange rate management
- **Recurring expenses**: Rent, utilities with automatic monthly splitting
- **Balance summary**: Owes/is owed by; group balance; individual balance
- **Notifications**: Expense added, debt settled, group invite, balance update

### Non-Functional Requirements
- **Scale**: 1M+ users; 100K+ active groups; 10K+ expenses/day
- **Latency**: Expense add < 500ms; balance calculation < 100ms
- **Consistency**: Strong consistency for balances; eventual for notifications
- **Accuracy**: Decimal precision for currency; no rounding errors in splits

## Key Design Decisions
- **Debt optimization**: Graph-based algorithm (minimum path cover) to minimize transactions
- **Balance tracking**: Directed graph where edges represent owes relationships
- **Currency**: Store amounts in cents (integer) to avoid floating-point errors
- **Concurrency**: Optimistic locking for expense updates; distributed lock for debt settlement

## Staff-Level Design Considerations

### Debt Optimization Algorithm
- **Graph model**: Users as nodes; debts as directed edges
- **Algorithm**: Topological sort + greedy settlement to minimize transactions
- **Staff insight**: Use **minimum path cover** algorithm — reduces N debts to N-1 transactions max

### Decimal Precision
- **Never use double**: Use `BigDecimal` or store in cents (integer) for currency
- **Rounding**: Round half-up for individual shares; adjust last person for remainder
- **Staff insight**: Floating-point errors are the #1 bug in financial systems. Use **integer arithmetic** for currency.
