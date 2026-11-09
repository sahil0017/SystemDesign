# ChatGPT-like System

## Problem Statement

Design a scalable conversational AI system like ChatGPT that supports real-time chat, streaming responses, conversation history, model versioning, rate limiting, and usage analytics.

**Reference**: Educative.io

## Requirements

### Functional Requirements
- **Chat interface**: Real-time conversational interface with streaming responses.
- **Conversation history**: Store and retrieve past conversations; continue from previous context.
- **Model selection**: Support multiple model versions (GPT-3.5, GPT-4, etc.) with different capabilities.
- **Rate limiting**: Per-user and per-organization rate limits; token-based quotas.
- **Usage analytics**: Track token usage, response times, and model performance.
- **Content moderation**: Filter harmful inputs and outputs; flag policy violations.

### Non-Functional Requirements
- **Scale**: 100M+ users; 1B+ conversations; 100K+ concurrent sessions.
- **Latency**: First token < 1s; streaming tokens at 50+ tokens/second.
- **Availability**: 99.9% uptime; graceful degradation during model overload.

## Key Design Decisions
- **Streaming**: Server-Sent Events (SSE) for token streaming to client.
- **Conversation storage**: NoSQL database for conversation history with user-based partitioning.
- **Model gateway**: Abstraction layer for model selection, load balancing, and fallback.
- **Token counting**: Track input/output tokens for billing and rate limiting.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                                → Chat Service
                                → Model Gateway
                                → Conversation Store
                                
Model Gateway → Model Cluster (GPU servers)
                    → Token Counter → Usage DB
                    → Content Moderation Service
                    → SSE Stream → Client
```

## Staff-Level Design Considerations

### Streaming Architecture
- **Server-Sent Events**: HTTP connection stays open; server pushes tokens as they're generated.
- **Staff insight**: SSE is simpler than WebSocket for unidirectional streaming. The client opens a single HTTP connection and receives tokens as they're generated. For bidirectional chat (client can interrupt), use WebSocket.

### Model Gateway Design
- **Load balancing**: Distribute requests across GPU instances. Route by model version and capacity.
- **Staff insight**: Use a queue-based dispatcher. Requests are queued and dispatched to available GPU instances. This smooths out traffic spikes and prevents GPU overload. Implement fallback: if GPT-4 is overloaded, fall back to GPT-3.5 with a warning.

### Context Management
- **Token budget**: Each model has a max context window (e.g., 128K tokens for GPT-4). Truncate old messages when context is full.
- **Staff insight**: Use a sliding window of recent messages. When the context is full, summarize older messages and include the summary. This preserves context while staying within token limits. This is what ChatGPT actually does.
