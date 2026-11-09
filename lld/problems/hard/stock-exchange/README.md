# Online Stock Exchange

## Problem Statement

Design an online stock exchange system that supports order placement, order matching, trade execution, portfolio management, and real-time market data.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Order types**: Market, Limit, Stop-Loss, Stop-Limit orders with buy/sell sides.
- **Order matching**: Match buy and sell orders based on price-time priority.
- **Order book**: Maintain bid-ask spread; visible depth of market.
- **Trade execution**: Execute matched orders; generate trade records.
- **Portfolio**: Track user holdings, cash balance, and P&L.
- **Market data**: Real-time price updates; historical OHLCV data.
- **Cancellation**: Cancel pending orders; partial fills.

### Non-Functional Requirements
- **Latency**: Order to execution < 1ms for market makers; < 10ms for retail.
- **Throughput**: 100K+ orders per second during market open.
- **Consistency**: Strong consistency for order matching; no duplicate trades.

## Key Design Decisions
- **Matching engine**: Price-time priority algorithm; best bid matches best ask.
- **Order book**: Two heaps (max-heap for bids, min-heap for asks) for O(log n) matching.
- **Event-driven**: Orders, trades, and cancellations as events in a processing pipeline.
- **Idempotency**: Order IDs are unique and idempotent for retry safety.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│    Order     │────►│    Trade     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - orderId    │     │ - tradeId    │
│ - portfolio  │     │ - symbol     │     │ - symbol     │
│ - cash       │     │ - side       │     │ - price      │
└──────────────┘     │ - type       │     │ - quantity   │
                     │ - price      │     │ - buyerId    │
                     │ - quantity   │     │ - sellerId   │
                     │ - status     │     └──────────────┘
                     └──────────────┘
                          │
                     ┌────┴────┐
                     │MatchingEngine│
                     ├─────────────┤
                     │ - orderBook │
                     │ + match()   │
                     └─────────────┘
```

## Staff-Level Design Considerations

### Matching Engine Algorithm
- **Price-time priority**: Best price first, then earliest time. This is the standard exchange algorithm.
- **Staff insight**: Use two priority queues (max-heap for bids, min-heap for asks). When a new order arrives, check if it crosses the spread. If yes, match and execute. This is O(log n) per order.

### Order Book Data Structure
- **Price levels**: Group orders by price level. Each level is a FIFO queue of orders.
- **Staff insight**: A simple heap doesn't support efficient cancellation. Use a price-level map (HashMap<Price, Queue<Order>>) for O(1) access to any price level.

### Latency Optimization
- **Lock-free structures**: Use atomic operations and lock-free queues for the hot path.
- **Staff insight**: In HFT (High-Frequency Trading), every nanosecond counts. Use ring buffers, memory-mapped files, and kernel-bypass networking. For LLD, mentioning these shows depth.
