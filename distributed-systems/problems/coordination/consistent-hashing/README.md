# Consistent Hashing

## Problem Statement

Design a consistent hashing system for distributing data across a dynamic set of nodes in a distributed system, minimizing data movement when nodes are added or removed.

**Reference**: ByteByteGo, AlgoMaster

## Requirements

### Functional Requirements
- **Data distribution**: Map keys to nodes using consistent hashing.
- **Node management**: Add and remove nodes with minimal data redistribution.
- **Virtual nodes**: Support virtual nodes for even data distribution.
- **Load balancing**: Ensure data is evenly distributed across nodes.

### Non-Functional Requirements
- **Scale**: 1,000+ nodes; 10B+ keys.
- **Efficiency**: O(log N) lookup; O(K log N) rebalancing where K is keys moved.

## Key Design Decisions
- **Hash ring**: Nodes placed on a ring by hash(node_id). Keys assigned to next clockwise node.
- **Virtual nodes**: Each physical node maps to 100-200 virtual nodes for even distribution.
- **Rebalancing**: On node add/remove, only keys between affected nodes are moved.

## Staff-Level Design Considerations

### Virtual Nodes
- **Even distribution**: Without virtual nodes, a small number of physical nodes can cause uneven distribution.
- **Staff insight**: Use 100-200 virtual nodes per physical node. This ensures each node owns approximately 1/N of the data, even with N=3.

### Alternatives
- **Range-based partitioning**: Split key space into ranges. Simpler but requires a metadata service.
- **Staff insight**: Consistent hashing is decentralized — any node can compute the mapping. Range-based requires a central coordinator. Choose based on your consistency and operational requirements.
