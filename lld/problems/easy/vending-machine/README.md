# Vending Machine

## Problem Statement (Staff-Level)

Design a vending machine system that handles product inventory, coin/bill/payment processing, change dispensing, product dispensing, restocking, and real-time monitoring. The system should support 100+ products, multiple payment methods, offline operation, and remote monitoring for a network of 10K+ machines.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Product inventory**: Slot-based inventory; stock tracking; low-stock alerts
- **Payment processing**: Coins, bills, credit card, mobile payment, contactless
- **Change dispensing**: Optimal change calculation; coin/bill denomination management
- **Product dispensing**: Motor control; jam detection; failed dispensing refund
- **Restocking**: Restock workflow; inventory sync; price updates
- **Pricing**: Dynamic pricing; promotional discounts; combo deals
- **Monitoring**: Real-time status; sales analytics; fault detection; remote diagnostics
- **Offline mode**: Operate without network; sync when connected

### Non-Functional Requirements
- **Scale**: 10K+ machines; 100+ products per machine; 1K+ transactions/day per machine
- **Latency**: Payment processing < 2s; product dispensing < 5s
- **Availability**: 99.9% uptime; offline mode for network outage
- **Security**: Payment security; tamper detection; anti-fraud

## Key Design Decisions
- **State machine**: Idle → Selecting → Payment → Dispensing → Change → Idle
- **Payment processing**: Strategy pattern for different payment methods
- **Change calculation**: Greedy algorithm for optimal change (standard denominations)
- **Inventory**: Slot-based with product mapping; real-time stock tracking

## Staff-Level Design Considerations

### State Machine Design
- **Explicit states**: `IDLE, SELECTED, PAYING, PAID, DISPENSING, CHANGE_RETURN, ERROR`
- **Transition validation**: Only valid transitions allowed; error recovery to safe state
- **Staff insight**: Use **State pattern** — each state is a class with explicit transition logic

### Change Dispensing Algorithm
- **Greedy algorithm**: Optimal for standard denominations (1, 5, 10, 25 cents)
- **Edge case**: Non-standard denominations require dynamic programming
- **Staff insight**: Greedy works for **canonical coin systems**; use DP for arbitrary denominations
