# Building Microservices by Sam Newman

## Summary

Comprehensive guide to microservices architecture, covering decomposition strategies, inter-service communication, data management, deployment, and testing. Addresses the practical challenges of adopting microservices and provides patterns for common problems.

## Key Topics

- **Decomposition**: How to split monoliths into services (by business capability, by noun, by strangler fig)
- **Communication**: Synchronous (REST, gRPC) vs asynchronous (message queues, event sourcing)
- **Data Management**: Database per service, saga pattern, CQRS, event sourcing
- **Deployment**: CI/CD for microservices, containerization, orchestration
- **Testing**: Contract testing, consumer-driven contracts, integration testing
- **Operations**: Monitoring, logging, distributed tracing, service discovery

## Key Takeaways

- **Microservices are not a silver bullet**: They add operational complexity — only adopt when the benefits outweigh the costs
- **Decomposition is hard**: Use domain-driven design (bounded contexts) to identify service boundaries
- **Data consistency is challenging**: Embrace eventual consistency and design compensation logic
- **Operations matter**: Microservices require robust CI/CD, monitoring, and automation

## Why Read This Book

- Practical guide for teams adopting microservices
- Covers pitfalls and anti-patterns with real-world examples
- Provides actionable patterns for common microservices challenges

## Related Problems in This Repository

- [HLD - E-commerce System](../../hld/case-studies/ecommerce-system/)
- [Blogs - Microservices Patterns](../../blogs-articles/system-design/microservices-patterns.md)
- [Trade-offs - Monolith vs Microservices](../../tradeoffs/monolith-vs-microservices/)
