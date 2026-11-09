# Google Drive

## Problem Statement

Design a cloud storage and file sharing service like Google Drive that supports file upload/download, real-time collaboration, versioning, trash, and sharing with permissions.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **File operations**: Upload, download, delete, rename, move files and folders.
- **Real-time collaboration**: Multiple users editing documents simultaneously.
- **Versioning**: Automatic version history; restore previous versions.
- **Sharing**: Share files/folders with links or specific users; view/edit/comment permissions.
- **Trash**: Soft delete with 30-day recovery; permanent delete.
- **Search**: Full-text search across files and document content.
- **Storage quota**: Per-user storage limits; usage tracking.

### Non-Functional Requirements
- **Scale**: 2B+ users; 10B+ files; 10PB+ storage.
- **Latency**: File upload < 2s (1MB); document open < 1s.
- **Consistency**: Strong consistency for metadata; eventual for collaboration.

## Key Design Decisions
- **Chunked upload**: Large files split into chunks for resumable uploads.
- **Operational Transformation (OT)**: Real-time collaboration using OT algorithm.
- **Content addressing**: Store files by content hash for deduplication.
- **Metadata separation**: Fast metadata service separate from content storage.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                            → Metadata Service (file tree, permissions)
                            → Content Service (chunked storage)
                            → Collaboration Service (OT engine)
                            → Search Service (Elasticsearch)
                            
Metadata Service → PostgreSQL
Content Service → GCS/S3 (chunked storage)
Collaboration → WebSocket → OT Engine → Document Store
```

## Staff-Level Design Considerations

### Real-Time Collaboration
- **Operational Transformation**: Transform concurrent edits to maintain consistency. Each operation is transformed against all other operations.
- **Staff insight**: OT is complex but battle-tested (Google Docs, Etherpad). Alternative: CRDTs (Conflict-free Replicated Data Types) which are simpler but have different semantics. For LLD, mention OT as the primary approach and CRDTs as an alternative.

### Chunked Upload
- **Resumable uploads**: Split files into 5-10MB chunks. Each chunk is uploaded independently and assembled server-side.
- **Staff insight**: This handles network failures gracefully. If upload fails at 80%, only the remaining 20% needs to be re-uploaded. Use a unique upload session ID to track chunk assembly.

### Storage Deduplication
- **Content-defined chunking**: Use Rabin fingerprint for variable-size chunks. Identical chunks are stored once.
- **Staff insight**: This saves significant storage. If 100 users upload the same 1GB video, it's stored once. Reference counting tracks how many users reference each chunk.
