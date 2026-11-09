# Online Auction System

## Problem Statement

Design an online auction system like eBay that supports item listings, bidding, auction timers, winner determination, and payment processing.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Item listing**: Sellers create listings with description, starting price, reserve price, and duration.
- **Bidding**: Place bids; auto-bid (proxy bidding) with maximum bid; bid increments.
- **Auction types**: English auction (ascending), Dutch auction (descending), fixed-price.
- **Timer**: Countdown timer; soft close (extend if bid in last N seconds).
- **Winner determination**: Highest bidder wins when timer expires; notify winner and loser.
- **Payment**: Process payment from winner to seller; escrow support.
- **Feedback**: Rating and review system for buyers and sellers.

### Non-Functional Requirements
- **Scale**: 1M+ active auctions; 100K+ concurrent bidders.
- **Latency**: Bid placement < 200ms; auction results < 1s after expiry.
- **Reliability**: No lost bids; accurate winner determination.

## Key Design Decisions
- **Proxy bidding**: Store maximum bid; system auto-bids on behalf of user up to their max.
- **Scheduler**: Time-wheel or delayed queue for auction expiry processing.
- **Concurrency**: Optimistic locking on current bid; reject stale bids.
- **Soft close**: Extend auction by N seconds if bid placed in last N seconds (prevents sniping).

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│   Auction    │────►│     Bid      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - auctionId  │     │ - bidId      │
│ - name       │     │ - itemId     │     │ - bidderId   │
│ - feedback   │     │ - currentBid │     │ - amount     │
└──────────────┘     │ - maxBid     │     │ - timestamp  │
                     │ - status     │     └──────────────┘
                     │ - endTime    │
                     │ - softClose  │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Proxy Bidding Algorithm
- **Auto-bid logic**: When a new bid comes in, compare with stored max bids. If user's max > current, set current to min(user's max, current + increment).
- **Staff insight**: This is the same algorithm eBay uses. The key insight is that you never reveal the full max bid — only the minimum needed to win.

### Auction Expiry Processing
- **Delayed queue**: Use a priority queue ordered by end time. When the top auction expires, process it.
- **Staff insight**: For 1M+ auctions, a simple cron job checking every second is inefficient. Use a time-wheel data structure or Redis ZSET with scores as expiry times.

### Soft Close (Anti-Sniping)
- **Extension rule**: If a bid is placed in the last N seconds, extend the auction by N seconds.
- **Staff insight**: This prevents last-second sniping. Implement with a volatile endTime field that updates on late bids. Use a distributed lock to prevent race conditions on the final bid.
