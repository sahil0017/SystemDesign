# Stack Overflow

## Problem Statement

Design a Q&A platform like Stack Overflow where users can ask questions, provide answers, vote on content, add comments, and manage tags.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Questions**: Users can create questions with title, body, and tags.
- **Answers**: Multiple answers per question; self-answing allowed.
- **Voting**: Upvote/downvote on questions and answers; reputation system.
- **Comments**: Short comments on questions and answers.
- **Tags**: Categorize questions; tag-based search and filtering.
- **Accept answer**: Question author can mark one answer as accepted.
- **Search**: Full-text search across questions and answers.
- **User reputation**: Points earned from voting, accepted answers, badges.

### Non-Functional Requirements
- **Scale**: 10M+ questions; 50M+ answers; 100K+ concurrent users.
- **Latency**: Question page load < 500ms; search < 1s.
- **Consistency**: Vote counts eventually consistent; reputation updates near-real-time.

## Key Design Decisions
- **Entity model**: Question → Answers (1:N); Question/Answer → Comments (1:N).
- **Voting**: Separate vote table; denormalized vote count on questions/answers for read performance.
- **Reputation**: Event-driven updates via message queue to avoid blocking writes.
- **Search**: Elasticsearch for full-text search; tag index for tag-based queries.

## Class Diagram

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│   User   │────►│   Question   │────►│   Tag    │
├──────────┤     ├──────────────┤     ├──────────┤
│ - userId │     │ - questionId │     │ - tagId  │
│ - rep    │     │ - title      │     │ - name   │
└──────────┘     │ - body       │     └──────────┘
                 │ - voteCount  │
                 │ - acceptedAns│
                 └──────┬───────┘
                        │ has
                 ┌──────┴───────┐
                 │   Answer     │
                 ├──────────────┤
                 │ - answerId   │
                 │ - body       │
                 │ - voteCount  │
                 │ - isAccepted │
                 └──────────────┘
```

## Staff-Level Design Considerations

### Vote Count Consistency
- **Denormalization**: Store voteCount on Question/Answer for O(1) reads. Update asynchronously.
- **Staff insight**: Never count votes from the vote table on every read — it's O(n) and a scalability killer.

### Reputation System
- **Event-driven**: Publish reputation events on vote/accept; a reputation service aggregates and updates user scores.
- **Staff insight**: Use idempotent reputation updates to handle duplicate events. A vote +1 and undo -1 should be exactly-once.

### Search Strategy
- **Elasticsearch**: Full-text search with relevance scoring (BM25).
- **Staff insight**: For tag-based queries, a simple inverted index (tag → question IDs) is sufficient and faster than ES.
