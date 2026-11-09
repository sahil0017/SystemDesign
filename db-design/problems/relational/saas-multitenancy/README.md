# SaaS Multi-Tenancy Database Schema Design

## Problem Statement

Design a multi-tenant SaaS database schema that supports complete data isolation between tenants. Compare and implement three isolation strategies: separate database per tenant, shared database with separate schemas, and shared database with `tenant_id` column. Include tenant management, subscription billing, usage tracking, and tenant-specific configuration.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Tenant Management**: Create, configure, suspend, and delete tenants.
- **Tenant Users**: Each tenant has its own users, roles, and permissions.
- **Subscriptions**: Plans (free, pro, enterprise), billing cycles, upgrades/downgrades.
- **Usage Tracking**: API calls, storage used, seats consumed per tenant.
- **Tenant Config**: Custom domain, branding, feature flags, integrations.
- **Data Isolation**: Tenants cannot access each other's data under any circumstance.
- **Cross-tenant Admin**: Super-admin can view all tenants for support and billing.

### Non-Functional Requirements
- **Security**: Zero cross-tenant data leakage; enforce isolation at DB level.
- **Scalability**: Support 10K+ tenants on shared infrastructure.
- **Performance**: Tenant queries should not degrade due to other tenants' load.
- **Compliance**: GDPR right-to-be-deleted per tenant; SOC2 audit trail.
- **Cost efficiency**: Balance isolation vs infrastructure cost.

## Key Design Decisions

- **Row-level tenant_id**: Primary strategy for most tenants; separate DB for enterprise tenants.
- **Row-Level Security (RLS)**: PostgreSQL RLS policies enforce tenant isolation at query level.
- **Tenant context middleware**: Every query automatically includes `tenant_id` filter.
- **Usage aggregation**: Pre-aggregate daily usage to avoid real-time COUNT queries.
- **Soft delete for tenants**: Mark tenant as deleted; physical deletion after retention period.

## Schema Design

### Strategy Comparison

| Strategy | Isolation | Cost | Complexity | Best For |
|----------|-----------|------|------------|----------|
| Separate DB | Highest | Highest | Highest | Enterprise, compliance-heavy |
| Separate Schema | High | Medium | Medium | Mid-tier tenants |
| Shared Table + tenant_id | Medium | Lowest | Lowest | SMB, high-tenant-count |

### Core Tables (Shared Database with tenant_id Strategy)

```sql
-- Tenants
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    custom_domain VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'suspended', 'deleted'
    plan_id UUID NOT NULL,
    max_seats INT DEFAULT 5,
    max_storage_mb INT DEFAULT 1024,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    settings JSONB, -- {"theme": "dark", "language": "en", "timezone": "UTC"}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Subscription Plans
CREATE TABLE subscription_plans (
    plan_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- 'Free', 'Pro', 'Enterprise'
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2) NOT NULL,
    max_seats INT NOT NULL,
    max_storage_mb INT NOT NULL,
    features JSONB, -- {"api_access": true, "sso": false, "custom_domain": true}
    is_active BOOLEAN DEFAULT TRUE
);

-- Tenant Subscriptions
CREATE TABLE tenant_subscriptions (
    subscription_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'cancelled', 'past_due'
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id)
);

-- Tenant Users
CREATE TABLE tenant_users (
    user_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (tenant_id, email),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- Usage Metrics (daily aggregation)
CREATE TABLE usage_metrics (
    metric_id BIGINT PRIMARY KEY,
    tenant_id UUID NOT NULL,
    metric_date DATE NOT NULL,
    api_calls INT DEFAULT 0,
    storage_used_mb DECIMAL(10,2) DEFAULT 0,
    active_seats INT DEFAULT 0,
    events_processed INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (tenant_id, metric_date),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- Tenant Feature Flags
CREATE TABLE tenant_feature_flags (
    flag_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    feature_key VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    configured_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (tenant_id, feature_key),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

-- Audit Log (for SOC2 compliance)
CREATE TABLE audit_log (
    log_id BIGINT PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (user_id) REFERENCES tenant_users(user_id)
);

-- Application Data Example (tenant-scoped)
CREATE TABLE projects (
    project_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (owner_id) REFERENCES tenant_users(user_id)
);
```

### Row-Level Security Policies

```sql
-- Enable RLS on tenant-scoped tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their tenant's data
CREATE POLICY tenant_isolation ON projects
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY tenant_user_isolation ON tenant_users
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Super-admin bypass
CREATE POLICY super_admin_bypass ON projects
    USING (current_setting('app.is_super_admin') = 'true');
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `tenants` | Unique on `subdomain` | Route by subdomain |
| `tenants` | Unique on `api_key` | API authentication |
| `tenant_users` | `(tenant_id, email)` | Login lookup |
| `tenant_users` | `(tenant_id, role)` | Role-based access |
| `usage_metrics` | `(tenant_id, metric_date DESC)` | Usage history |
| `usage_metrics` | Unique `(tenant_id, metric_date)` | Prevent duplicate daily records |
| `audit_log` | `(tenant_id, created_at DESC)` | Audit trail per tenant |
| `audit_log` | `(tenant_id, user_id, created_at DESC)` | User activity audit |
| `projects` | `(tenant_id, created_at DESC)` | Tenant's projects list |
| `projects` | `(tenant_id, owner_id)` | User's projects |

## Staff-Level Design Considerations

### Isolation Strategy Selection
- **Shared table + tenant_id**: Best for 95% of tenants. Lowest cost, simplest ops.
- **Separate schema**: For mid-tier tenants needing stronger isolation without separate DB overhead.
- **Separate database**: For enterprise tenants with compliance requirements (HIPAA, PCI-DSS).
- **Staff insight**: Start with shared tables + RLS. Offer separate DB as an enterprise feature. Don't over-engineer isolation for tenants that don't need it.

### Row-Level Security (RLS)
- **Database-enforced isolation**: RLS policies prevent cross-tenant queries even if application code has bugs.
- **Staff insight**: RLS is a safety net, not the primary isolation mechanism. Always include `tenant_id` in application queries. RLS adds query overhead (~5-10%) — benchmark before enabling on high-throughput tables.

### Tenant Context Management
- **Request-scoped tenant**: Extract `tenant_id` from subdomain, JWT, or API key at the edge.
- **Staff insight**: Use middleware to set `tenant_id` in a request-local context. Every repository method receives `tenant_id` as a mandatory parameter. Never trust client-provided `tenant_id` — always derive it from authentication.

### Usage Tracking & Billing
- **Real-time counter**: Increment API call counter in Redis on each request.
- **Daily aggregation**: Batch job aggregates Redis counters to `usage_metrics` table nightly.
- **Staff insight**: Don't write to PostgreSQL on every API call for usage tracking. Use Redis counters with periodic flush. This reduces DB write load by 100x and provides sub-second usage queries.

### GDPR Right-to-Be-Deleted
- **Tenant deletion**: Set `status = 'deleted'`, schedule physical deletion after 30 days.
- **Staff insight**: Physical deletion requires cascading deletes across all tenant-scoped tables. Use a transactional job that deletes in dependency order: child tables → parent tables. Anonymize audit logs instead of deleting (compliance requirement).
