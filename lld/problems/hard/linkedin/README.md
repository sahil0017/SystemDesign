# LinkedIn

## Problem Statement

Design a professional networking platform like LinkedIn that supports user profiles, connections, job postings, messaging, news feed, and skill endorsements.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **User profile**: Professional profile with experience, education, skills, and certifications.
- **Connections**: Send, accept, decline connection requests; 1st/2nd/3rd-degree network.
- **News feed**: Posts from connections; company updates; industry news.
- **Jobs**: Post jobs, apply to jobs, save jobs; recruiter tools.
- **Messaging**: Direct messaging between connections; InMail for non-connections.
- **Skills/Endorsements**: Add skills; endorse connections' skills.
- **Groups**: Professional groups with discussions and events.

### Non-Functional Requirements
- **Scale**: 1B+ users; 50B+ connections; 100M+ daily active users.
- **Latency**: Feed load < 500ms; profile load < 300ms.
- **Graph queries**: Degree-of-separation queries in < 1s.

## Key Design Decisions
- **Graph model**: User connections as a directed graph; BFS for degree-of-separation.
- **Feed strategy**: Fan-out-on-write with hybrid pull for high-degree users.
- **Job matching**: Rule-based matching between job requirements and user profiles.
- **Caching**: Aggressive profile caching; profiles are read-heavy and write-light.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│ Connection   │────►│    Post      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - fromUser   │     │ - postId     │
│ - profile    │     │ - toUser     │     │ - authorId   │
│ - skills     │     │ - status     │     │ - content    │
└──────────────┘     │ - degree     │     │ - visibility │
                     └──────────────┘     └──────────────┘
```

## Staff-Level Design Considerations

### Degree-of-Separation
- **BFS from both ends**: Bidirectional BFS to find shortest path between two users.
- **Staff insight**: Standard BFS is O(V+E). Bidirectional BFS reduces it to O(d^(b/2)) where d is branching factor and b is path length. For LinkedIn's average degree of 4, this is 100x faster.

### Connection Graph Storage
- **Adjacency list**: Store connections in a graph database or wide-column store (Cassandra).
- **Staff insight**: LinkedIn uses a custom graph database. For LLD, Cassandra with user ID as partition key and connection list as a set works well.

### Feed Personalization
- **Scoring model**: Rank posts by relevance (recency, relationship strength, engagement).
- **Staff insight**: Pre-compute top N posts per user in a background job. Serve from cache. Re-rank in real-time based on user's current context.
