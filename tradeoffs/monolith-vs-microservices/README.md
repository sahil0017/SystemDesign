# Monolith vs Microservices

## Trade-off Overview

Choosing between a monolithic architecture and microservices is one of the most impactful decisions for a system. Monoliths are simpler to build and deploy; microservices offer independent scaling and team autonomy but add significant operational complexity.

## Monolith

### Characteristics
- **Single codebase**: All modules in one repository and deployment unit.
- **Shared database**: All components access the same database.
- **In-process calls**: Communication via method calls, not network calls.
- **Single deployment**: Build, test, and deploy as one unit.

### Pros
- **Simplicity**: Easy to develop, test, debug, and deploy.
- **Performance**: In-process calls are faster than network calls.
- **Transactions**: ACID transactions across all modules.
- **Operational cost**: One server to monitor, scale, and maintain.

### Cons
- **Scaling**: Must scale the entire application, not just busy modules.
- **Technology lock-in**: Entire application uses one tech stack.
- **Deployment risk**: Change in any module requires full redeployment.
- **Team coordination**: Multiple teams working on same codebase causes conflicts.

## Microservices

### Characteristics
- **Independent services**: Each service owns its domain and data.
- **Separate databases**: Each service has its own database (database per service).
- **Network communication**: Services communicate via REST, gRPC, or messages.
- **Independent deployment**: Each service is built, tested, and deployed separately.

### Pros
- **Independent scaling**: Scale only the services that need it.
- **Technology diversity**: Each service can use the best tech for its domain.
- **Team autonomy**: Teams own services end-to-end; no coordination needed.
- **Fault isolation**: Service failure doesn't bring down the entire system.

### Cons
- **Distributed complexity**: Network failures, latency, partial failures.
- **Data consistency**: No ACID across services; use Saga or outbox pattern.
- **Operational overhead**: Monitor, deploy, and scale N services independently.
- **Debugging**: Distributed tracing needed to follow requests across services.

## Decision Framework

| Factor | Choose Monolith When... | Choose Microservices When... |
|--------|------------------------|-----------------------------|
| Team size | < 10 developers | 10+ developers, multiple teams |
| Scale | Predictable, uniform load | Varying load across modules |
| Deployment | Infrequent, coordinated releases | Frequent, independent releases |
| Complexity | Simple domain, few integrations | Complex domain, many bounded contexts |
| Ops maturity | Small ops team, limited automation | Mature DevOps, Kubernetes, CI/CD |

## Staff-Level Insight

> "Start with a monolith. Extract services when you have a proven reason to do so."

- **Modular monolith**: Structure code as modules with clear boundaries; extract to services later.
- **Amazon rule**: "Two-pizza teams" — each service owned by a team that can be fed with two pizzas.
- **Staff insight**: **80% of startups should start with a monolith**. Microservices add complexity that young teams can't handle. Extract services when: (1) a module scales differently from the rest, (2) a team wants to use a different tech stack, or (3) deployment frequency requirements differ. Don't extract services prematurely — a well-structured monolith is better than a poorly-designed microservice system.
