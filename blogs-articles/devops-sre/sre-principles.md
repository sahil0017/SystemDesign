# Site Reliability Engineering (SRE) Principles

## Overview

SRE is software engineering applied to infrastructure and operations. Coined by Google, SRE uses engineering practices to achieve reliability, scalability, and performance — replacing manual operations with automation and data-driven decision making.

## Core Concepts

### SLOs, SLIs, and SLAs

| Term | Definition | Example |
|------|-----------|---------|
| **SLI** (Service Level Indicator) | Measured metric of service quality | 99.5% of requests return 200 OK |
| **SLO** (Service Level Objective) | Target value for the SLI | 99.9% of requests return 200 OK |
| **SLA** (Service Level Agreement) | Contractual consequence of missing SLO | $100 credit if availability < 99.9% |

### Error Budget
- **Error budget** = 1 - SLO target
- Example: 99.9% SLO → 0.1% error budget → 43.8 minutes downtime/month
- **Purpose**: Quantify the trade-off between reliability and velocity
- **When budget is available**: Deploy features, take risks
- **When budget is exhausted**: Freeze features, focus on reliability

### The Golden Signal
1. **Latency**: Time to serve a request (use percentiles, not averages)
2. **Traffic**: Demand on the system (RPS, QPS)
3. **Errors**: Failed requests (4xx, 5xx, timeouts)
4. **Saturation**: How "full" the service is (CPU, memory, disk)

## Alerting Strategy

### Alert on Symptoms, Not Causes
```
❌ Alert: CPU > 80%          (cause — may not affect users)
✅ Alert: Error rate > 1%    (symptom — users are affected)
✅ Alert: P99 latency > 2s   (symptom — users experience slowness)
```

### Multi-Window Burn Rate
- **Fast burn**: Alert if error budget consumed in < 1 hour (critical)
- **Slow burn**: Alert if error budget consumed in < 6 hours (warning)
- Prevents both sudden outages and gradual degradation

## Blameless Postmortems

### Process
1. **Incident occurs**: Respond and resolve
2. **Postmortem meeting**: Within 48 hours of resolution
3. **Document**: Timeline, impact, root cause, action items
4. **Follow up**: Track action items to completion

### Key Principles
- **Blameless**: Focus on process, not people
- **Actionable**: Every postmortem produces concrete action items
- **Transparent**: Share postmortems with the entire organization
- **Staff insight**: A blameless culture leads to better incident prevention. If engineers fear blame, they hide mistakes — and the same incident happens again.

## Staff-Level Insights

### SLO Design
- Define SLOs from the **user's perspective**, not infrastructure metrics
- Use **percentiles** (P95, P99) instead of averages for latency SLOs
- **Staff insight**: Start with 1-2 SLOs per service. Too many SLOs dilute focus. Pick the metrics that matter most to users: availability and latency.

### Toil Reduction
- **Toil**: Manual, repetitive, automatable work
- SREs spend 50% on engineering, 50% on operations (including toil)
- **Staff insight**: If toil exceeds 50%, automate or hire. Common toil: manual deployments, password resets, log analysis. Automate with scripts, self-service tools, and better observability.

### Capacity Planning
- Use **traffic forecasting** based on historical growth trends
- Plan for **peak + 20%** headroom
- **Staff insight**: Don't capacity plan based on averages. Use P95 traffic from the last 30 days and add growth buffer. Auto-scaling handles spikes, but baseline capacity should cover sustained load.
