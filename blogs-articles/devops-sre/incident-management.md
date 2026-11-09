# Incident Management

## Overview

Incident management is the process of detecting, responding to, and resolving production incidents. Effective incident management minimizes user impact, accelerates resolution, and prevents recurrence through systematic learning.

## Incident Lifecycle

### 1. Detection
- **Monitoring alerts**: Automated detection via metrics, logs, traces
- **User reports**: Customer support tickets, social media complaints
- **Synthetic monitoring**: Health checks from external locations

### 2. Triage
- **Severity classification**:
  - **SEV1**: Complete service outage, affecting all users
  - **SEV2**: Major degradation, affecting many users
  - **SEV3**: Partial degradation, affecting some users
  - **SEV4**: Minor issue, workaround available
- **Assign incident commander**: Single person coordinates response

### 3. Response
- **Communicate**: Notify stakeholders, post status page updates
- **Mitigate**: Restore service first (rollback, scale up, disable feature)
- **Diagnose**: Find root cause after service is restored
- **Fix**: Implement permanent fix and deploy

### 4. Resolution
- **Verify**: Confirm service is fully restored
- **Communicate**: Update stakeholders, close incident
- **Postmortem**: Document timeline, root cause, and action items

## Roles

### Incident Commander (IC)
- Coordinates the response effort
- Makes decisions about mitigation strategy
- Communicates with stakeholders
- **Not** the person fixing the issue

### Communicator
- Updates status page and stakeholders
- Provides regular updates (every 30-60 minutes)
- Manages external communication

### SWE On-Call
- Investigates and implements fixes
- Provides technical context to IC

## Postmortem Process

### Timeline
```
10:00 - Incident detected
10:05 - IC assigned, bridge call started
10:15 - Rollback initiated
10:30 - Service restored
10:45 - Root cause identified: DB connection pool exhaustion
11:00 - Incident resolved, postmortem scheduled
```

### Root Cause Analysis
- **5 Whys**: Ask "why" 5 times to find the underlying cause
- **Fishbone diagram**: Categorize causes (people, process, technology)
- Focus on **systemic** causes, not individual mistakes

### Action Items
- **Preventive**: Prevent the same incident from recurring
- **Detective**: Improve detection (faster alerts, better monitoring)
- **Responsive**: Improve response (runbooks, automation)

## Staff-Level Insights

### Mitigate First, Diagnose Later
- **Rollback** is the fastest mitigation — revert the last change
- **Disable** the problematic feature via feature flag
- **Scale up** to handle increased load temporarily
- **Staff insight**: Don't try to debug in production during an incident. Restore service first (rollback, disable, scale), then diagnose in a calm environment. Every minute of outage costs more than a rollback.

### Runbooks
- Document common incident responses as runbooks
- Include step-by-step instructions for mitigation
- Test runbooks regularly via game days
- **Staff insight**: A runbook should be executable by an engineer who hasn't worked on the service. If it requires tribal knowledge, it's not a runbook — it's a hint.

### Game Days
- Simulate real incidents in production-like environments
- Practice incident response, communication, and mitigation
- Build muscle memory for real incidents
- **Staff insight**: Run game days quarterly. Teams that practice incident response resolve incidents 50% faster. Chaos engineering (randomly killing services) is a form of game day that builds resilience.

### On-Call Best Practices
- **Fair rotation**: Rotate on-call among team members
- **Compensation**: Provide on-call compensation or time off
- **Alert quality**: Only page for actionable, user-impacting issues
- **Staff insight**: If your on-call engineer gets paged more than 2-3 times per week, your alerting is broken. Consolidate alerts, raise thresholds, and fix the underlying issues to reduce page frequency.
