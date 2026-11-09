# Site Reliability Engineering by Google

## Summary

Google's approach to production operations, written by Google SREs. Covers SLOs, error budgets, incident management, monitoring, automation, and capacity planning. Defines modern SRE practices used by companies worldwide.

## Key Chapters

1. **SRE Overview**: What SRE is, the 50/50 rule, toil management
2. **Service Level Objectives**: Defining SLIs, SLOs, and SLAs; error budgets
3. **Monitoring and Alerting**: Metrics, dashboards, alerting on symptoms
4. **Automation**: Reducing toil through automation, self-healing systems
5. **Capacity Planning**: Forecasting, stress testing, performance testing
6. **Incident Management**: Response, communication, postmortems
7. **Workload Management**: Load balancing, scheduling, resource allocation

## Key Takeaways

- **SLOs drive reliability**: Define measurable objectives from the user's perspective
- **Error budgets balance reliability and velocity**: When budget is available, deploy features; when exhausted, focus on reliability
- **Automate toil**: If you do it twice, automate it
- **Blameless postmortems**: Focus on process improvement, not individual blame
- **Alert on symptoms**: Alert on user-facing impact, not infrastructure metrics

## Why Read This Book

- Defines modern SRE practices — the industry standard
- Free online from Google at [sre.google/sre-book](https://sre.google/sre-book/)
- Practical advice from the team that coined the term "SRE"

## Related Problems in This Repository

- [Blogs - SRE Principles](../../blogs-articles/devops-sre/sre-principles.md)
- [Blogs - Incident Management](../../blogs-articles/devops-sre/incident-management.md)
- [Blogs - Observability](../../blogs-articles/devops-sre/observability.md)
