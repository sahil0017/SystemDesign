# Push vs Pull

## Trade-off Overview

Push (server sends data to client) vs Pull (client requests data from server) represents a fundamental choice in data delivery architecture.

## Push (Server-Sent Events, WebSockets, Kafka)
- **Pros**: Real-time delivery, low latency, server controls timing.
- **Cons**: Server must maintain connections, harder to scale, client must handle stream.
- **Use when**: Real-time updates (chat, notifications, live data).

## Pull (REST, HTTP polling)
- **Pros**: Simple, stateless, client controls timing, easy to cache.
- **Cons**: Latency (polling interval), wasted requests when no data.
- **Use when**: On-demand data, infrequent updates, cacheable content.

## Staff-Level Insight

> "Push for real-time, pull for on-demand. Long-polling bridges the gap."

- **Staff insight**: Use **WebSockets** for bidirectional real-time (chat, gaming). Use **Server-Sent Events** for unidirectional push (notifications, stock prices). Use **long-polling** when WebSocket is not available (firewall restrictions). For most APIs, **pull with caching** is simpler and more reliable than push.
