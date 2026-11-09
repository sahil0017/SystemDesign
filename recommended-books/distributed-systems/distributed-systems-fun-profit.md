# Distributed Systems for Fun and Profit by Mikito Takada

## Summary

Free online book that explains distributed systems concepts with simple analogies and real-world examples. Covers replication, consistency, availability, message queues, and distributed coordination — accessible to engineers without a distributed systems background.

## Key Chapters

1. **Replication**: Why replicate? Primary-backup, multi-primary, conflict resolution
2. **Consistency**: Strong vs eventual consistency, trade-offs, real-world examples
3. **Availability**: CAP theorem, partition tolerance, designing for failure
4. **Message Queues**: Decoupling services, reliability, ordering guarantees
5. **Distributed Coordination**: Leader election, distributed locks, consensus

## Key Takeaways

- **Replication is about availability and performance**: More copies = faster reads and fault tolerance
- **Consistency and availability are trade-offs**: You can't have both during network partitions
- **Message queues decouple services**: Enable independent scaling and fault isolation
- **Distributed coordination is hard**: Use proven tools (ZooKeeper, Etcd) instead of building your own

## Why Read This Book

- Best introduction to distributed systems — read it in one sitting
- Free online at [applied-go.com](https://applied-go.com/)
- Simple analogies make complex concepts accessible

## Related Problems in This Repository

- [Distributed Systems - Problems](../../distributed-systems/problems/)
- [Blogs - CAP Theorem in Practice](../../blogs-articles/system-design/cap-theorem-practice.md)
- [Blogs - Raft Consensus](../../blogs-articles/distributed-systems/raft-consensus.md)
