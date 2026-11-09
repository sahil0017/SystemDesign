# Consistent Hashing

## Overview

Consistent hashing is a hashing technique that minimizes key redistribution when nodes are added or removed from a distributed system. It's used by Netflix for CDN, DynamoDB for data partitioning, and Redis Cluster for key distribution.

## The Problem with Regular Hashing

With standard hashing (`key % num_nodes`), adding or removing a node requires rebalancing **all keys**:
```
3 nodes: key % 3 → keys distributed across 0, 1, 2
Add 4th node: key % 4 → ALL keys move to new positions
```
This causes cache misses, network storms, and service disruption.

## How Consistent Hashing Works

### The Hash Ring
1. Hash function maps keys and nodes to a ring (0 to 2^32 - 1)
2. Each key is assigned to the **next clockwise node** on the ring
3. When a node is added/removed, only keys between the affected nodes are redistributed

```
Ring:  0 ---- NodeA ---- Key1 ---- NodeB ---- Key2 ---- NodeC ---- 2^32
Key1 → NodeB (next clockwise)
Key2 → NodeC (next clockwise)
```

### Virtual Nodes
- Each physical node maps to **multiple virtual nodes** on the ring
- Improves distribution uniformity (avoid hotspots)
- Typical: 100-150 virtual nodes per physical node

```
Physical Node A → VN-A1, VN-A2, VN-A3, ... VN-A100
Physical Node B → VN-B1, VN-B2, VN-B3, ... VN-B100
```

## Real-World Use Cases

### Netflix CDN
- Content is hashed to edge servers on a consistent ring
- Adding/removing edge servers only affects affected content
- Virtual nodes ensure even distribution across servers

### DynamoDB
- Uses **consistent hashing with replicas**
- Each item replicated to N nodes spread across the ring
- Token ranges determine which nodes own which data

### Redis Cluster
- 16,384 hash slots distributed across nodes
- Keys mapped to slots via `CRC16(key) % 16384`
- Reshuffling moves slots, not individual keys

## Staff-Level Insights

### Choosing Hash Function
- Use **SHA-1** or **MD5** for uniform distribution
- Avoid simple hash functions that create clustering
- **Staff insight**: The hash function quality directly impacts data distribution. Test with your actual key distribution — real-world keys often have patterns that create hotspots.

### Handling Node Failures
- When a node fails, its keys are automatically served by the next node on the ring
- Use **replication** so keys exist on multiple nodes
- **Staff insight**: Consistent hashing alone doesn't provide fault tolerance. Combine it with replication (store each key on N nodes) for high availability.

### Rebalancing Strategy
- **Async rebalancing**: Move keys gradually to avoid network storms
- **Rate limiting**: Limit key migration rate to prevent performance impact
- **Staff insight**: When adding/removing nodes, rebalance gradually over hours, not minutes. A sudden key migration can overwhelm the network and cause temporary degradation.
