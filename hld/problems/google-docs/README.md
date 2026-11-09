# Google Docs

## Problem Statement

Design a real-time collaborative document editing system like Google Docs that supports multiple users editing the same document simultaneously, with conflict resolution, version history, and real-time synchronization.

**Reference**: Educative.io, HelloInterview

## Requirements

### Functional Requirements
- **Real-time editing**: Multiple users edit the same document simultaneously.
- **Conflict resolution**: Merge concurrent edits without data loss using Operational Transformation (OT) or CRDTs.
- **Cursor visibility**: Show other users' cursors and selections in real-time.
- **Version history**: Track document versions; allow rollback to any point in time.
- **Comments/Suggestions**: Add comments and suggestion mode for collaborative review.
- **Access control**: Share documents with view/edit/comment permissions.
- **Offline support**: Edit offline; sync changes when connection is restored.

### Non-Functional Requirements
- **Latency**: Edit propagation < 100ms for 95% of operations.
- **Scale**: 100+ concurrent editors per document; 1M+ active documents.
- **Consistency**: All users see the same document state within 1 second.
- **Reliability**: No data loss on network interruption or server crash.

## Key Design Decisions
- **Operational Transformation (OT)**: Transform concurrent operations to maintain consistency.
- **WebSocket**: Persistent bidirectional connection for real-time sync.
- **Document sharding**: Split large documents into segments for parallel processing.
- **Write-ahead log**: All operations logged for replay and version history.

## Architecture Diagram

```
┌──────────┐    WebSocket    ┌──────────────┐     ┌──────────────┐
│  Client  │◄──────────────►│  Presence    │────►│  Document    │
│ (Browser)│                │  Service     │     │  Service     │
└──────────┘                └──────────────┘     └──────┬───────┘
                                                        │
                                                 ┌──────┴───────┐
                                                 │   Storage    │
                                                 │ (Op Log +    │
                                                 │  Snapshots)  │
                                                 └──────────────┘
```

## Staff-Level Design Considerations

### OT vs CRDTs
- **OT**: Server-authoritative; transforms operations against a central version. Complex but proven (Google Docs uses OT).
- **CRDTs**: Conflict-free by design; no central authority. Simpler but higher bandwidth (send more data).
- **Staff insight**: OT is better for text editing (lower bandwidth). CRDTs are better for simple structures (counters, sets). For production, use a proven OT library like Yjs or Automerge.

### WebSocket vs HTTP Polling
- **WebSocket**: Single persistent connection; bidirectional; low latency.
- **Staff insight**: Don't use long-polling for real-time editing — it adds 100-1000ms latency per round-trip. WebSocket is the standard for collaborative editing. Use Server-Sent Events (SSE) as a fallback for read-only clients.

### Version History
- **Snapshot + op log**: Store periodic snapshots and the operation log between snapshots.
- **Staff insight**: Don't store a full snapshot for every edit — it's too much storage. Store a snapshot every N operations (e.g., 1000) and replay ops from the last snapshot. This balances storage cost and rollback performance.

### Offline Support
- **Local operation queue**: Buffer operations locally; sync when online.
- **Staff insight**: Offline editing requires the client to generate unique operation IDs and sequence numbers. On reconnect, the server applies OT to merge local ops with server ops. This is the hardest part of collaborative editing.
