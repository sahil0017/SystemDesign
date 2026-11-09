# Code Review Best Practices

## Overview

Code review is the primary mechanism for maintaining code quality, sharing knowledge, and catching bugs before they reach production. Effective code review balances thoroughness with speed to avoid becoming a bottleneck.

## For Reviewers

### What to Look For
1. **Correctness**: Does the code do what it's supposed to do?
2. **Readability**: Can another engineer understand this code in 6 months?
3. **Testing**: Are edge cases covered? Are tests meaningful?
4. **Performance**: Are there obvious performance issues?
5. **Security**: Are there injection, authentication, or data exposure risks?
6. **Consistency**: Does the code follow project conventions?

### Review Checklist
```
□ Does the PR description explain the "why"?
□ Is the change scope reasonable (< 400 lines)?
□ Are tests added/updated for the change?
□ Is error handling comprehensive?
□ Are there no obvious performance anti-patterns?
□ Is the code readable and well-named?
□ Are there no security issues?
□ Does the code follow project conventions?
```

### Giving Feedback
- **Be specific**: "This method is too long" → "Consider extracting lines 15-30 into a helper method"
- **Be kind**: Frame comments as questions, not commands
- **Prioritize**: Distinguish must-fix from nice-to-have
- **Suggest, don't dictate**: "Have you considered..." instead of "You should..."

## For Authors

### Writing Good PRs
- **Small PRs**: < 400 lines of code; one logical change per PR
- **Clear description**: What changed, why, and how to test
- **Self-review**: Review your own code before requesting review
- **Address concerns**: Respond to every comment, even if you disagree

### Handling Feedback
- Don't take criticism personally — it's about the code, not you
- Ask for clarification if a comment is unclear
- Discuss disagreements in person, not in comments
- **Staff insight**: If you receive the same comment on multiple PRs, fix the root cause (template, linting rule, or personal habit).

## Staff-Level Insights

### PR Size Matters
- **Small PRs** (< 200 lines): Reviewed in < 30 minutes, higher quality
- **Medium PRs** (200-400 lines): Reviewed in 1 hour, acceptable
- **Large PRs** (> 400 lines): Reviewed poorly, bugs slip through
- **Staff insight**: If a PR is too large, split it. A 1,000-line PR will either be rubber-stamped or cause review fatigue. Break it into 3-5 smaller PRs with clear dependencies.

### Automated Checks
- Use **linters** and **formatters** to catch style issues automatically
- Use **CI pipelines** to run tests on every PR
- Use **code coverage** tools to ensure tests are meaningful
- **Staff insight**: Don't waste human review time on style issues. Configure pre-commit hooks and CI to catch formatting, linting, and basic style issues automatically. Human reviewers should focus on logic, architecture, and edge cases.

### Review SLA
- Target **< 4 hours** for first review
- Target **< 24 hours** for PR merge (after feedback)
- Set team expectations and track review time metrics
- **Staff insight**: Slow code review kills developer velocity. If your team's average review time exceeds 4 hours, you have a process problem. Assign review duty, limit WIP PRs, and make review a daily priority.
