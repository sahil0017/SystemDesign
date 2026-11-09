# Distributed Configuration Management

## Problem Statement

Design a distributed configuration management system (like Consul, Etcd, or Spring Cloud Config) that stores, distributes, and updates configuration across microservices. The system must support real-time config updates without restart, versioning, encryption, and environment-specific overrides.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Centralized storage**: Single source of truth for all service configurations.
- **Real-time updates**: Push config changes to services without restart via long-polling or WebSocket.
- **Versioning**: Track config history; support rollback to previous versions.
- **Environment overrides**: Different configs for dev, staging, production environments.
- **Encryption**: Encrypt sensitive values (passwords, API keys) at rest and in transit.
- **Validation**: Schema validation before applying config changes.
- **Access control**: RBAC for who can view/modify configurations.

### Non-Functional Requirements
- **High availability**: Config service available 99.99% of the time.
- **Low latency**: Config fetch in < 100ms on service startup.
- **Consistency**: Strong consistency for config reads — all instances see the same config.
- **Scalability**: Support 10K+ services and 1M+ config keys.

## Key Design Decisions
- **Etcd/Consul backend**: Use strongly consistent KV store for config storage.
- **Long-polling**: Services poll for changes; server holds request until change detected.
- **Local cache**: Services cache config locally; continue operating if config service is down.
- **Watch mechanism**: Config service notifies clients of changes via watch API.

## Architecture

```
Config Service (Etcd Cluster)
      |
      +-- Long-poll --> Service Instance A --> Local Cache --> Use Config
      +-- Long-poll --> Service Instance B --> Local Cache --> Use Config
      +-- Long-poll --> Service Instance C --> Local Cache --> Use Config
      |
      +-- Admin API --> Config Dashboard --> Write Config --> Validate --> Store
```

## Staff-Level Design Considerations

### Consistency Model
- **Strong consistency**: Etcd/Consul use Raft — all reads return the latest written value.
- **Eventual consistency**: Consul supports eventual consistency for read scalability.
- **Staff insight**: Use **strong consistency** for config — services must not see stale config that causes incorrect behavior. The performance cost of Raft consensus is negligible for config reads (config changes rarely; reads are cached).

### Config Update Strategy
- **Push model**: Config service pushes changes to clients via long-polling or WebSocket.
- **Pull model**: Services poll config service periodically.
- **Staff insight**: Use **long-polling** — client sends request, server holds it open until config changes or timeout (30s). This gives near-real-time updates without WebSocket complexity. On timeout, client re-polls. This is how Spring Cloud Config and Consul clients work.

### Local Cache Strategy
- **Startup cache**: Service loads config on startup and caches locally.
- **Fail-open**: If config service is down, use cached config and continue operating.
- **Staff insight**: **Never fail service startup** because config service is temporarily down. Cache config locally with a generous TTL. Log a warning if config service is unreachable but use the last known good config. This prevents cascading failures.

### Sensitive Data Handling
- **Encryption at rest**: Encrypt secrets in the config store using KMS (AWS KMS, HashiCorp Vault).
- **Encryption in transit**: TLS for all config service communication.
- **Secret rotation**: Integrate with secret rotation services for automatic credential updates.
- **Staff insight**: **Never store plaintext secrets** in config. Use a secrets manager (Vault, AWS Secrets Manager) and reference secrets by path/ARN in config. The config service stores references, not actual secrets. Services resolve secrets at runtime from the secrets manager.

### Config Validation
- **Schema validation**: JSON Schema or Protobuf validation before applying config changes.
- **Canary deployment**: Apply config to 1 instance first; verify health; then roll out to all.
- **Staff insight**: Use **canary config deployment** — apply changes to a single instance first, verify health checks pass, then roll out to the rest. A bad config can take down all instances simultaneously; canary deployment limits blast radius.
