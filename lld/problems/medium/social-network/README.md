# Social Network (Facebook-like)

## Problem Statement

Design a social networking service like Facebook that supports user profiles, friend connections, news feed, posts with media, comments, likes, groups, and real-time notifications.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **User profile**: Create and manage profile with photo, bio, and personal information.
- **Friend system**: Send, accept, decline friend requests; unfriend; block users.
- **News feed**: Chronological and algorithmic feed of posts from friends and followed pages.
- **Posts**: Create posts with text, photos, videos; edit and delete posts.
- **Comments/Likes**: Like and comment on posts; nested comments.
- **Groups**: Create and join groups; group-specific posts and discussions.
- **Notifications**: Real-time notifications for likes, comments, friend requests, mentions.
- **Messaging**: Direct messaging between friends.

### Non-Functional Requirements
- **Scale**: 1B+ users; 10B+ posts; 100M+ active daily users.
- **Latency**: Feed load < 500ms; post creation < 1s.
- **Availability**: 99.9% uptime; graceful degradation during peak load.

## Key Design Decisions
- **Feed strategy**: Fan-out-on-write for active users; pull-on-read for inactive users.
- **Graph model**: User-friend relationships as a graph; adjacency list for friend queries.
- **Media storage**: Blob storage (S3) for photos/videos; CDN for delivery.
- **Notifications**: Event-driven pub/sub system for real-time notifications.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│     Post     │────►│   Comment    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - postId     │     │ - commentId  │
│ - name       │     │ - content    │     │ - text       │
│ - profilePic │     │ - authorId   │     │ - authorId   │
└──────────────┘     │ - mediaList  │     │ - parentId   │
                     │ - likeCount  │     └──────────────┘
                     └──────┬───────┘
                            │
                     ┌──────┴───────┐
                     │   Media      │
                     ├──────────────┤
                     │ - mediaId    │
                     │ - url        │
                     │ - type       │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Feed Generation Strategy
- **Fan-out-on-write**: When a user posts, push to all friends' feeds. Fast reads, expensive writes for influencers.
- **Pull-on-read**: Generate feed at query time by fetching friends' posts. Slow reads, cheap writes.
- **Staff insight**: Hybrid approach — fan-out for users with < 1K friends, pull for influencers. This is what Facebook actually uses.

### Friend Graph Storage
- **Adjacency list**: Store friendships as directed edges. A→B and B→A for mutual friends.
- **Staff insight**: For "mutual friends" queries, use graph databases (Neo4j) or pre-compute intersections in Redis.

### Notification Scaling
- **Pub/sub**: Publish events (like, comment, mention) to a notification service.
- **Staff insight**: Batch notifications. If 100 people like a post in 1 minute, send 1 notification ("100 people liked your post"), not 100.
