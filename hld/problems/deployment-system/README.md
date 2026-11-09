# Deployment System

## Problem Statement

Design a code deployment system that automates building, testing, and rolling out software across large-scale distributed infrastructure. Support strategies like blue-green, canary, and rolling deployments with automatic rollback on failure.

**Reference**: Educative.io

## Requirements

### Functional Requirements
- **Build**: Compile code, run tests, and create deployable artifacts.
- **Versioning**: Tag and version each deployment artifact.
- **Deployment strategies**: Blue-green, canary, rolling, and shadow deployments.
- **Health checks**: Verify deployed services are healthy before traffic shift.
- **Rollback**: Automatically revert to previous version on failure.
- **Rollout control**: Gradual traffic shift (1% → 5% → 25% → 50% → 100%).
- **Notification**: Alert on deployment start, success, failure, and rollback.

### Non-Functional Requirements
- **Scale**: Deploy to 10K+ servers across multiple regions.
- **Downtime**: Zero-downtime deployments for critical services.
- **Reliability**: 99.99% deployment success rate; automatic rollback on failure.
- **Audit**: Complete deployment history with who, what, when, and why.

## Key Design Decisions
- **Artifact registry**: Store built artifacts with version tags (Docker registry, Maven repo).
- **Configuration management**: Infrastructure as code (Terraform, Ansible) for reproducible deployments.
- **Feature flags**: Decouple deployment from release; enable features gradually.
- **Metrics-driven rollback**: Monitor error rates, latency, and CPU; auto-rollback on anomaly.

## Architecture Diagram

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Git     │───►│  CI/CD       │───►│  Artifact    │───►│  Deployment  │
│  Repo    │    │  Pipeline    │    │  Registry    │    │  Controller  │
└──────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                               │
                                                    ┌──────────┼──────────┐
                                                    │          │          │
                                             ┌──────┴┐  ┌─────┴──┐ ┌────┴────┐
                                             │ Blue  │  │ Canary │ │ Rolling │
                                             │Green  │  │ Deploy │ │ Deploy  │
                                             └───────┘  └────────┘ └─────────┘
```

## Staff-Level Design Considerations

### Blue-Green vs Canary
- **Blue-green**: Two identical environments; switch traffic instantly. Fast rollback but expensive (2x infrastructure).
- **Canary**: Gradual rollout to a small subset; monitor before full rollout. Cheaper but slower.
- **Staff insight**: Use blue-green for critical services where downtime is unacceptable. Use canary for most services to catch issues early. Use feature flags to decouple deployment from release.

### Health Check Strategy
- **Multi-level checks**: Liveness (is it running?), readiness (can it serve traffic?), startup (is it initializing?).
- **Staff insight**: Don't rely on a single health check. Use synthetic transactions that exercise the actual business logic. A service can be "up" but broken — check the real user journey.

### Metrics-Driven Rollback
- **Error rate threshold**: Auto-rollback if error rate exceeds 5% baseline.
- **Staff insight**: Use statistical anomaly detection, not fixed thresholds. A 5% error rate might be normal for a new feature. Compare against the previous version's error rate, not an absolute value.

### Database Migrations
- **Expand-contract pattern**: Add new columns/tables first (expand); migrate data; remove old columns (contract).
- **Staff insight**: Never drop a column that's still in use. The expand-contract pattern ensures backward compatibility during deployment. Use feature flags to control when the new code path is active.
