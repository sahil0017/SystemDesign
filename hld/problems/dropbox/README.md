# Dropbox (File Storage and Sync)

## Problem Statement

Design a cloud file storage and synchronization service like Dropbox that supports file upload/download, real-time sync across devices, versioning, sharing, and conflict resolution.

**Reference**: Educative.io, HelloInterview

## Requirements

### Functional Requirements
- **File operations**: Upload, download, delete, rename, and move files/folders.
- **Sync**: Automatic sync across multiple devices; incremental sync for changes.
- **Versioning**: Keep file history; restore previous versions.
- **Sharing**: Share files/folders with links or specific users; permission levels.
- **Conflict resolution**: Detect and resolve conflicts when same file is edited on multiple devices.
- **Trash**: Soft delete with 30-day recovery window.

### Non-Functional Requirements
- **Scale**: 500M+ users; 10B+ files; 10PB+ storage.
- **Latency**: File upload < 2s (1MB file); download start < 500ms.
- **Consistency**: Eventual consistency for sync; strong consistency for single-device operations.

## Key Design Decisions
- **Block-level deduplication**: Split files into blocks; store unique blocks once. Saves storage and bandwidth.
- **Content-addressable storage**: Use file hash as storage key for deduplication.
- **Sync protocol**: Delta sync — only transfer changed blocks, not entire files.
- **Metadata vs content**: Separate metadata service (fast) from content storage (large objects).

## Architecture Overview

```
Client → Load Balancer → API Gateway
                            → Metadata Service (file tree, permissions)
                            → Content Service (block storage)
                            → Sync Service (change detection)
                            
Metadata Service → PostgreSQL (file metadata, user info)
Content Service → S3/GCS (block storage)
Sync Service → Kafka (change events) → Device Notification
```

## Staff-Level Design Considerations

### Block-Level Deduplication
- **Content-defined chunking**: Split files into variable-size blocks using rolling hash (Rabin fingerprint).
- **Staff insight**: This is the key to Dropbox's efficiency. If two users upload the same 1GB file, it's stored once. A 1MB edit to a 1GB file transfers only the changed blocks.

### Conflict Resolution
- **Last-write-wins with merge**: For text files, use diff3 merge. For binary files, keep both versions.
- **Staff insight**: Never silently overwrite. Always preserve both versions and let the user decide. Dropbox's "conflicted copy" approach is the right one.

### Sync Efficiency
- **Change journal**: Maintain a write-ahead log of all changes. Clients sync by replaying changes since last sync.
- **Staff insight**: This is the same pattern as database replication. The change journal is the source of truth for what's changed, not a diff of the current state.
