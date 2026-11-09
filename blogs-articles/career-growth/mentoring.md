# Mentoring Engineers

## Overview

Mentoring is one of the highest-leverage activities a senior or staff engineer can do. Effective mentoring accelerates engineer growth, improves team velocity, and builds organizational resilience by reducing knowledge silos.

## Mentoring Framework

### Levels of Mentoring
| Level | Approach | Example |
|-------|----------|---------|
| **Directing** | Tell them what to do | "Use a HashMap here for O(1) lookup" |
| **Coaching** | Guide them to the answer | "What's the time complexity of this lookup?" |
| **Supporting** | Encourage their decision | "What trade-offs did you consider?" |
| **Delegating** | Trust their judgment | "You own this design — I'm here if you need me" |

### Adapt to the Mentee
- **Junior engineers**: More directing and coaching
- **Mid-level engineers**: More coaching and supporting
- **Senior engineers**: More supporting and delegating

## Effective Coaching Techniques

### Socratic Method
- Ask questions instead of giving answers
- "What happens if this service is down?"
- "How would this scale to 10x traffic?"
- "What's the failure mode here?"

### Code Review as Mentoring
- Use PRs as teaching opportunities
- Explain the "why" behind suggestions
- Point out patterns and anti-patterns
- Celebrate good design decisions

### Pair Programming
- Driver/navigator roles switch frequently
- Focus on problem-solving, not typing
- Use for complex bugs and design discussions

## Common Mentoring Scenarios

### Helping with Debugging
```
Mentee: "This test is failing and I don't know why."
Mentor: "What did you expect to happen?"
Mentee: "The user should be created."
Mentor: "What actually happened?"
Mentee: "Null pointer exception on line 42."
Mentor: "What could be null there? How can you verify?"
```

### Career Growth Conversations
- Discuss strengths and areas for improvement
- Set specific, measurable goals
- Identify projects that build needed skills
- Provide visibility opportunities (tech talks, cross-team projects)

### Handling Imposter Syndrome
- Normalize the feeling — everyone experiences it
- Point to concrete achievements and growth
- Share your own struggles and how you overcame them
- **Staff insight**: Imposter syndrome often means you're growing. If you felt completely comfortable, you wouldn't be learning.

## Staff-Level Insights

### Invest in Mentoring Early
- The first 90 days of a new engineer determine their trajectory
- Assign a buddy for the first month
- Schedule regular 1:1s for the first 6 months
- **Staff insight**: A well-mentored junior engineer becomes productive 2-3 months faster. The investment pays for itself many times over.

### Create Growth Paths
- Help mentees understand the skills needed for the next level
- Provide stretch assignments that build those skills
- Advocate for mentees in promotion reviews
- **Staff insight**: Your success as a mentor is measured by your mentee's independence. The goal is to make yourself unnecessary. If they still need you after a year, you haven't mentored effectively.

### Build a Mentoring Culture
- Encourage peer mentoring within the team
- Create documentation and onboarding materials
- Host tech talks and brown-bag sessions
- **Staff insight**: Don't be the only mentor. Train senior engineers to mentor mid-level, and mid-level to mentor junior. This creates a self-sustaining growth culture that doesn't depend on you.
