"""Problem-specific content templates keyed by keywords."""

# Problem-specific content templates
PROBLEM_TEMPLATES = {
    # HLD templates
    "rag": {
        "concepts": ["Vector embeddings", "Semantic search", "Retrieval-augmented generation", "LLM integration"],
        "architecture": "Client → API Gateway → RAG Service\n"
                        "                        → Embedding Model (GPU)\n"
                        "                        → Vector DB (Milvus/Pinecone)\n"
                        "                        → LLM Service\n"
                        "                        → Document Store",
    },
    "llm": {
        "concepts": ["Model serving", "GPU batching", "Speculative decoding", "Continuous batching"],
        "architecture": "Client → API Gateway → LLM Router\n"
                        "                        → Model Server (vLLM/TGI)\n"
                        "                        → GPU Pool\n"
                        "                        → Token Counter\n"
                        "                        → Cache (Redis)",
    },
    "fraud": {
        "concepts": ["Real-time scoring", "ML model serving", "Rule engine", "Stream processing"],
        "architecture": "Transaction → Kafka → Fraud Detector\n"
                        "                        → Rule Engine\n"
                        "                        → ML Model Server\n"
                        "                        → Alert System\n"
                        "                        → Blocklist DB",
    },
    "flash sale": {
        "concepts": ["Thundering herd", "Queue-based throttling", "Inventory reservation", "Fairness"],
        "architecture": "Client → CDN → API Gateway → Queue\n"
                        "                        → Worker Pool\n"
                        "                        → Inventory Service\n"
                        "                        → Payment Service",
    },
    "streaming": {
        "concepts": ["Ingest", "Transcoding", "Adaptive bitrate", "CDN distribution"],
        "architecture": "Streamer → Ingest Server → Transcoder Farm\n"
                        "                        → Origin Storage\n"
                        "                        → Multi-CDN\n"
                        "                        → Client (HLS/DASH)",
    },
    "ad": {
        "concepts": ["Real-time bidding", "Auction engine", "Budget pacing", "Impression tracking"],
        "architecture": "Publisher → Ad Server → Auction Engine\n"
                        "                        → Bidder Pool\n"
                        "                        → Creative Store\n"
                        "                        → Analytics Pipeline",
    },
    "wallet": {
        "concepts": ["Double-entry bookkeeping", "Idempotency", "Fraud detection", "Multi-currency"],
        "architecture": "Client → API Gateway → Wallet Service\n"
                        "                        → Ledger DB\n"
                        "                        → Fraud Check\n"
                        "                        → Notification Service",
    },
    "workflow": {
        "concepts": ["DAG execution", "Fault tolerance", "Retry policies", "State management"],
        "architecture": "Client → API Gateway → Workflow Engine\n"
                        "                        → Task Queue\n"
                        "                        → Worker Pool\n"
                        "                        → State Store\n"
                        "                        → Event Log",
    },
    # LLD templates
    "text editor": {
        "concepts": ["Gap buffer", "Command pattern", "Undo/redo", "OT/CRDT"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│   Document   │────►│    Buffer    │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - history    │     │ - gapStart   │\n"
                         "│ - cursor     │     │ - gapLength  │\n"
                         "└──────────────┘     └──────────────┘\n"
                         "          │\n"
                         "   ┌──────┴──────┐\n"
                         "   │  Command    │\n"
                         "   ├─────────────┤\n"
                         "   │ - undo/redo │\n"
                         "   └─────────────┘",
    },
    "snake": {
        "concepts": ["State machine", "Deque", "Collision detection", "Grid management"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│     Game     │────►│     Grid     │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - snake      │     │ - cells      │\n"
                         "│ - food       │     │ - obstacles  │\n"
                         "└──────────────┘     └──────────────┘",
    },
    "splitwise": {
        "concepts": ["Expense splitting", "Debt simplification", "Graph algorithms", "Balances"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│   Group      │────►│   Expense    │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - members    │     │ - amount     │\n"
                         "│ - balances   │     │ - splitType  │\n"
                         "└──────────────┘     └──────────────┘",
    },
    # Distributed systems templates
    "vector": {
        "concepts": ["HNSW/IVF-PQ", "ANN search", "Sharding", "Metadata filtering"],
        "architecture": "Client → API Gateway → Vector Service\n"
                        "                        → Index Shards\n"
                        "                        → Metadata Store\n"
                        "                        → Embedding Pipeline",
    },
    "feature store": {
        "concepts": ["Online/offline storage", "Point-in-time correctness", "Training-serving skew"],
        "architecture": "ML Pipeline → Feature Writer → Online Store (Redis)\n"
                        "                        → Offline Store (Parquet)\n"
                        "                        → Feature Registry",
    },
    "secret": {
        "concepts": ["AES-256-GCM", "Shamir sharing", "Dynamic secrets", "RBAC"],
        "architecture": "Client → API Gateway → Vault Service\n"
                        "                        → Encryption Engine\n"
                        "                        → Secret Backend\n"
                        "                        → Audit Log",
    },
}

# Markdown templates for each category
HLD_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Architecture Overview

```
{architecture}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

LLD_TEMPLATE = """# {name}

## Problem Statement (Staff-Level)

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Class Diagram

```
{class_diagram}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

DS_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Architecture Overview

```
{architecture}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

TRADEOFF_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## When to Use {option_a}
{when_a}

## When to Use {option_b}
{when_b}

## Decision Framework
{decision_framework}

## Staff-Level Insights
{staff_insights}
"""

JAVA_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Key Concepts
{key_concepts}

## Implementation
{implementation}

## Staff-Level Design Considerations

{staff_considerations}
"""
