# S3-like Object Storage

## Problem Statement

Design a distributed object storage system like Amazon S3 that supports storing and retrieving billions of objects with high durability, availability, and scalability.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Object operations**: Put, get, delete, and list objects.
- **Buckets**: Namespace for objects; bucket-level permissions and policies.
- **Metadata**: User-defined metadata; system metadata (content-type, size, ETag).
- **Versioning**: Optional object versioning; restore previous versions.
- **Lifecycle policies**: Auto-transition to infrequent access or archive; auto-expiration.
- **Presigned URLs**: Time-limited URLs for secure object access without credentials.

### Non-Functional Requirements
- **Durability**: 11 nines (99.999999999%) — lose less than 2 objects per year per 10B.
- **Availability**: 99.99% for standard storage.
- **Scale**: 10B+ objects; 100PB+ total storage; 100K+ requests per second.

## Key Design Decisions
- **Erasure coding**: Split objects into data and parity chunks for durability with less overhead than replication.
- **Flat namespace**: All objects in a flat key space; no hierarchical directories.
- **Consistent hashing**: Distribute objects across storage nodes using consistent hashing.
- **Async replication**: Replicate chunks to multiple availability zones.

## Architecture Overview

```
Client → Load Balancer → API Gateway
                            → Metadata Service (object metadata)
                            → Data Service (chunk storage)
                            → Erasure Coding Engine
                            
Data Service → Storage Nodes (consistent hash ring)
                    → Replication to AZ-2, AZ-3
                    → Background: Integrity Check → Repair
```

## Staff-Level Design Considerations

### Erasure Coding vs Replication
- **Erasure coding**: Split object into K data chunks + M parity chunks. Can survive M chunk losses. Storage overhead: (K+M)/K.
- **Replication**: Store N copies. Storage overhead: N.
- **Staff insight**: With EC(10,4), you get 4-fault tolerance with 1.4x storage overhead vs 4x for replication. This is why S3 uses erasure coding for standard storage and replication for frequently accessed data.

### Flat Namespace
- **No directories**: S3 prefixes look like directories but are just keys. "photos/2024/jan/img.jpg" is a single string key.
- **Staff insight**: This simplifies the storage layer. Listing "directories" is a prefix scan on the key index. For large buckets, use continuation tokens for pagination.

### Data Integrity
- **Background scanner**: Continuously verify object checksums. Repair corrupted chunks from parity or replicas.
- **Staff insight**: Bit rot is real. Hard drives silently corrupt data ~1% of the time. S3 runs a background integrity checker that scans all objects and repairs any corruption. This is how S3 achieves 11 nines of durability.
