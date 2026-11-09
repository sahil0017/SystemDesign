# Distributed Secret Management

## Problem Statement

Design a distributed secret management system (HashiCorp Vault-like) that stores, retrieves, and rotates sensitive data (API keys, passwords, certificates) with encryption at rest, access control, audit logging, and dynamic secret generation.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Secret storage**: Store secrets with encryption at rest using AES-256-GCM.
- **Secret retrieval**: Authenticate and retrieve secrets with fine-grained access control.
- **Access control**: Role-based access control (RBAC) with path-based policies.
- **Secret rotation**: Automatic rotation of database credentials, API keys, and certificates.
- **Dynamic secrets**: Generate short-lived credentials on demand (e.g., database usernames).
- **Audit logging**: Immutable audit trail of all secret access and management operations.
- **Key management**: Encrypt secrets with a master key; support key rotation and unsealing.

### Non-Functional Requirements
- **Scale**: 1M+ secrets; 100K+ reads per second; 1K+ writes per second.
- **Latency**: Secret retrieval < 10ms (p95); write < 50ms.
- **Security**: AES-256-GCM encryption at rest; TLS 1.3 in transit; Shamir secret sharing for master key.
- **Availability**: 99.99% uptime with automatic failover and replication.

## Key Design Decisions
- **Encryption**: AES-256-GCM for data-at-rest encryption; TLS 1.3 for data-in-transit.
- **Master key**: Shamir secret sharing (split into N parts, K required to reconstruct).
- **Storage backend**: PostgreSQL/Consul for encrypted secret storage with replication.
- **Lease-based secrets**: Dynamic secrets expire after a lease TTL; auto-renew or revoke.

## Architecture Overview

```
Client → Auth Method (Kubernetes/AWS/LDAP) → Policy Engine
                    → Secret Engine (KV/Database/PKI)
                    → Storage Backend (Encrypted)
                    → Audit Logger (Immutable)
Master Key → Shamir Split → Unseal Keys → Key Unseal → Master Key (Memory)
```

## Staff-Level Design Considerations

### Encryption Architecture
- **Data encryption key (DEK)**: Each secret is encrypted with a unique DEK using AES-256-GCM.
- **Key encryption key (KEK)**: DEKs are encrypted with a KEK, which is encrypted with the master key.
- **Master key**: Never stored at rest; split using Shamir secret sharing and held in memory.
- **Staff insight**: The encryption key hierarchy (DEK → KEK → Master Key) is critical. It enables key rotation without re-encrypting all secrets. Rotate the KEK, re-encrypt DEKs, and all secrets remain protected. This is the standard pattern in all secret management systems.

### Shamir Secret Sharing
- **Split**: Master key is split into N shares; K shares are required to reconstruct (e.g., 5-of-7).
- **Unsealing**: On startup, K operators provide their shares to reconstruct the master key in memory.
- **Staff insight**: Shamir secret sharing ensures no single person can access secrets alone. In production, automate unsealing with cloud KMS (AWS KMS, GCP KMS) — the KMS holds the shares, and Vault unseals itself on startup. Manual unsealing is only for air-gapped environments.

### Dynamic Secrets
- **Database secrets**: Generate a new database user with specific privileges; set TTL to 1 hour.
- **AWS secrets**: Generate temporary IAM credentials using STS; set TTL to 1 hour.
- **Auto-renewal**: Client renews the lease before expiry; revoke on TTL expiry.
- **Staff insight**: Dynamic secrets are the most secure approach. Since credentials expire automatically, a leaked credential is only useful for the remaining TTL. Use dynamic secrets for all database connections and cloud API access. Static secrets should only be used when dynamic is not supported.

### Access Control
- **Path-based policies**: Define policies per secret path (e.g., `path "secret/data/prod/*" { capabilities = ["read"] }`).
- **Authentication methods**: Support multiple auth methods (Kubernetes, AWS, LDAP, JWT).
- **Staff insight**: Use the principle of least privilege. Each service should only have access to the secrets it needs, not all secrets. In Kubernetes, use the auth method to map service accounts to Vault policies automatically.

### Audit Logging
- **Immutable log**: All operations (auth, read, write, delete) are logged to an append-only storage.
- **Signed entries**: Each audit entry is cryptographically signed to prevent tampering.
- **Staff insight**: Audit logging is a compliance requirement (SOC2, PCI-DSS). Make the audit log immutable and tamper-evident. Use a write-once storage (e.g., S3 with object lock) for the audit backend.
