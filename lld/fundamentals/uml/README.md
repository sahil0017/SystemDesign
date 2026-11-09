# UML (Unified Modeling Language)

## Overview

UML is a standardized visual language for modeling software systems. For staff engineers, UML is not about drawing every diagram — it's about **communicating design decisions**, **documenting architecture**, and **aligning team understanding** before coding.

## Most Important Diagrams for Staff Engineers

### 1. Class Diagram (Most Used)
**Purpose**: Show classes, attributes, methods, and relationships.

```
┌─────────────────┐       ┌─────────────────┐
│    <<interface>> │       │    OrderService  │
│   PaymentMethod  │       ├─────────────────┤
├─────────────────┤       │ - orderRepo      │
│ +pay(): Result   │◄──────│ - paymentGateway │
│ +refund(): void  │  uses │─────────────────│
└─────────────────┘       │ +createOrder()   │
       ▲                  │ +cancelOrder()   │
       │ implements       └─────────────────┘
┌──────┴──────────┐
│ CreditCardPay    │
├─────────────────┤
│ - cardNumber     │
│ - expiryDate     │
└─────────────────┘
```

**Relationships**:
- **Inheritance** (`▲`): "is-a" relationship
- **Composition** (◆—): Strong ownership; parts can't exist without whole
- **Aggregation** (◇—): Weak ownership; parts can exist independently
- **Association** (——): Usage relationship
- **Dependency** (-.-): Temporary usage

### 2. Sequence Diagram (Most Used)
**Purpose**: Show object interactions over time for a specific use case.

```
User         API Gateway      OrderService     PaymentGateway    Database
 │                │                 │                  │            │
 │──Create Order──│                 │                  │            │
 │                │──Validate───────│                  │            │
 │                │                 │──Check Stock─────│            │
 │                │                 │                  │──Query─────│
 │                │                 │                  │◄─Result────│
 │                │                 │──Authorize───────│            │
 │                │                 │                  │──Charge────│
 │                │                 │                  │◄─Success───│
 │                │                 │◄─Result──────────│            │
 │                │◄─Order Created──│                  │            │
 │◄─201 Created──│                 │                  │            │
```

**Staff Insight**: Sequence diagrams reveal **cross-cutting concerns** (auth, logging, validation) and **failure paths** that code alone doesn't show.

### 3. State Machine Diagram
**Purpose**: Show object states and transitions.

```
       [Place Order]
          │
          ▼
    ┌──────────┐  Payment     ┌──────────┐  Ship      ┌──────────┐
    │  Pending │─────────────►│ Confirmed │───────────►│  Shipped │
    └──────────┘              └──────────┘             └──────────┘
         │                        │                          │
         │ Cancel                 │ Refund                   │ Deliver
         ▼                        ▼                          ▼
    ┌──────────┐            ┌──────────┐                ┌──────────┐
    │ Cancelled │            │ Refunded │                │Delivered │
    └──────────┘            └──────────┘                └──────────┘
```

**Staff Insight**: State machines prevent **invalid state transitions** and make business rules explicit.

### 4. Component Diagram
**Purpose**: Show high-level system components and their dependencies.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Web App    │────►│  API Server │────►│  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                         │
                    ┌────┴─────┐
                    │          │
               ┌────┴──┐  ┌───┴────┐
               │ Redis │  │ Kafka  │
               └───────┘  └────────┘
```

## Class Diagram Notation

| Symbol | Meaning | Example |
|--------|---------|---------|
| `+` | Public | `+getName(): String` |
| `-` | Private | `-balance: double` |
| `#` | Protected | `#calculateTax(): double` |
| `▲` | Inheritance | `Dog ▲ Animal` |
| `◆—` | Composition | `Order ◆ OrderItem` |
| `◇—` | Aggregation | `Department ◇ Employee` |
| `⟨⟩` | Stereotype | `⟨interface⟩`, `⟨abstract⟩` |

## Staff-Level UML Checklist

1. **Class diagrams**: Use for LLD interviews to show domain model and relationships
2. **Sequence diagrams**: Use for HLD to show request flow across services
3. **State diagrams**: Use for complex state machines (order lifecycle, workflow)
4. **Don't over-model**: UML is a communication tool, not a deliverable
5. **Focus on what matters**: Model the complex parts; skip the obvious
6. **Use PlantUML or Mermaid**: Text-based diagrams that version-control well
7. **Update with code**: Outdated diagrams are worse than no diagrams
