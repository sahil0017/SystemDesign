# REST vs gRPC

## Trade-off Overview

REST (JSON over HTTP) and gRPC (Protocol Buffers over HTTP/2) are the two dominant service communication protocols, each with different trade-offs in performance, ecosystem, and developer experience.

## REST (JSON/HTTP)
- **Pros**: Universal support, human-readable, easy debugging, caching, CDN-friendly.
- **Cons**: Verbose JSON, HTTP/1.1 overhead, no built-in contracts.
- **Use when**: Public APIs, browser clients, web services, caching needed.

## gRPC (Protobuf/HTTP2)
- **Pros**: Binary serialization (smaller/faster), HTTP/2 multiplexing, strong contracts, streaming.
- **Cons**: No browser support, harder debugging, limited ecosystem.
- **Use when**: Internal microservices, high-throughput, bidirectional streaming.

## Staff-Level Insight

> "REST for external APIs, gRPC for internal services."

- **Staff insight**: Use **REST/JSON for public APIs** — every language and tool supports it. Use **gRPC for internal microservices** — Protobuf contracts prevent breaking changes, HTTP/2 multiplexing reduces latency, and binary serialization is 3-10x smaller than JSON. Use **gRPC-Gateway** to expose gRPC services as REST for external clients. Define Protobuf contracts first — they serve as the API specification.
