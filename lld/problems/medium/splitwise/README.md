# Splitwise (LLD)

## Problem Statement (Staff-Level)

Design a Splitwise-like expense splitting system that manages users, groups, shared expenses, and debt simplification using graph algorithms to minimize the number of transactions needed to settle all balances.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **User management**: Create and manage user profiles.
- **Group management**: Create groups with members; manage group expenses.
- **Expense tracking**: Add expenses with amount, payer, and split details (equal, unequal, percentage).
- **Balance calculation**: Compute per-user balances within groups and across all groups.
- **Debt simplification**: Minimize the number of transactions to settle all debts using graph algorithms.
- **Transaction history**: Track all payments and settlements.
- **Notifications**: Notify users of new expenses, splits, and settlement requests.

### Non-Functional Requirements
- **Scale**: 10M+ users; 100M+ expenses; 1K+ transactions per second.
- **Latency**: Balance query < 100ms; debt simplification < 1s for 100-member groups.
- **Consistency**: Balances must be accurate; no double-counting of expenses.
- **Extensibility**: Support pending expenses, expense categories, and receipt uploads.

## Key Design Decisions
- **Directed graph**: Represent debts as a directed graph where edges owe amounts.
- **Debt simplification**: Use a greedy algorithm (or DFS) to minimize transactions.
- **Double-entry**: Each expense creates credits and debits; balance is a derived sum.
- **Aggregate balance**: Per-group and cross-group balance aggregation.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Group     │────►│   Expense    │────►│  ExpenseSplit│
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - members    │     │ - payer      │     │ - user       │
│ - expenses[] │     │ - amount     │     │ - amount     │
│ - balance    │     │ - splits[]   │     │ - type       │
└──────────────┘     │ - category   │     └──────────────┘
                     └──────────────┘
                          │
                     ┌────┴────┐
                     │ User    │
                     ├─────────┤
                     │ - name  │
                     │ - owes  │
                     │ - owed  │
                     └─────────┘
```

## Staff-Level Design Considerations

### Debt Simplification Algorithm
- **Problem**: With N users, there can be O(N²) debts. Find the minimum set of transactions to settle all balances.
- **Approach**: Compute net balance per user. Use DFS/greedy to pair positive and negative balances.
- **Algorithm**: 
  1. Compute net balance for each user (sum of all owed - sum of all owes).
  2. Separate into positive (owed) and negative (owes) lists.
  3. Greedily match the largest positive with the largest negative.
- **Staff insight**: The optimal solution is NP-hard (set partitioning). The greedy approach gives a near-optimal solution in O(n log n). For practical group sizes (< 100), it's fast and produces minimal transactions.

### Balance Calculation
- **Per-group balance**: Track net balance per user per group.
- **Aggregate balance**: Sum across all groups for a global view.
- **Incremental update**: Update balances on expense add/modify/delete; don't recompute from scratch.
- **Staff insight**: Never recompute balances from all expenses on each query. Maintain a denormalized balance table that's updated atomically with expense changes. This is the materialized view pattern.

### Split Types
- **Equal split**: Simplest; amount / number of users.
- **Unequal split**: Custom amount per user; sum must equal total.
- **Percentage split**: Percentage per user; sum must equal 100%.
- **Exclude payer**: Option to exclude the payer from the split.
- **Staff insight**: Validate that split amounts sum to the total expense amount. Use a transaction to ensure atomicity: create expense + splits + balance updates in one ACID transaction.

### Pending Expenses
- **Use case**: User A pays $100 at dinner; adds the expense later. Mark as pending until confirmed.
- **Workflow**: Pending → Confirmed (all users agree) / Disputed (resolution needed).
- **Staff insight**: Pending expenses add complexity but are essential for real-world use. Use a state machine for expense states (Pending → Confirmed / Disputed → Resolved). Don't include pending expenses in balance calculations until confirmed.
