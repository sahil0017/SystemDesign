# Restaurant Management System

## Problem Statement

Design a restaurant management system that handles table reservations, order management, kitchen workflow, billing, and inventory tracking.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Table management**: Table layout, status (Available, Reserved, Occupied, Clean), capacity.
- **Reservations**: Book tables by date, time, party size; waitlist when fully booked.
- **Order management**: Take orders from tables; modify orders; split bills.
- **Kitchen display**: Send orders to kitchen; track preparation status; priority ordering.
- **Menu management**: Items with categories, prices, availability, and modifiers.
- **Billing**: Generate bills; apply discounts; support multiple payment methods.
- **Inventory**: Track ingredient stock; auto-deduct on order; low-stock alerts.

### Non-Functional Requirements
- **Scale**: 50+ tables; 200+ orders per hour during peak; 10+ kitchen stations.
- **Latency**: Order placement < 1s; bill generation < 2s.
- **Real-time**: Kitchen receives orders in real-time; table status updates instantly.

## Key Design Decisions
- **State machine**: Table states: Available → Reserved → Occupied → Billed → Dirty → Available.
- **Observer pattern**: Kitchen observes new orders; manager observes revenue metrics.
- **Command pattern**: Orders as commands with undo support (cancel before kitchen starts).
- **Priority queue**: Kitchen orders prioritized by wait time and VIP status.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Customer   │────►│   Order      │────►│  OrderItem   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - customerId │     │ - orderId    │     │ - menuItem   │
│ - name       │     │ - tableId    │     │ - quantity   │
│ - partySize  │     │ - status     │     │ - modifiers  │
└──────────────┘     │ - totalPrice │     │ - specialIns │
                     └──────────────┘     └──────────────┘
                          │
                     ┌────┴────┐
                     │  Table  │────►│  MenuItem  │
                     ├─────────┤     ├────────────┤
                     │ - tableId│     │ - itemId   │
                     │ - capacity│    │ - name     │
                     │ - status │     │ - price    │
                     └─────────┘     │ - category │
                                     └────────────┘
```

## Staff-Level Design Considerations

### Kitchen Workflow
- **Priority queue**: Orders with longest wait time get highest priority. VIP tables get a boost.
- **Staff insight**: Use a heap-based priority queue. When an order is modified, remove and re-insert with updated priority. This is O(log n).

### Bill Splitting
- **Equal, by item, or custom**: Support multiple split strategies.
- **Staff insight**: By-item splitting requires tracking which customer ordered which item. Store customer-to-item mapping at the table level. This is a common real-world requirement.

### Inventory Deduction
- **Event-driven**: When an order is confirmed (not placed), deduct ingredients.
- **Staff insight**: Deduct on confirmation, not placement. Orders are cancelled frequently before the kitchen starts. Deducting too early causes false low-stock alerts.
