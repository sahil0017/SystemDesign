# Instagram - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via Bearer token except login/register. Rate limited per user tier.

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate session |

## User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}` | Get user profile |
| PUT | `/api/v1/users/{user_id}` | Update user profile |
| GET | `/api/v1/users/{user_id}/followers` | List followers (paginated) |
| GET | `/api/v1/users/{user_id}/following` | List following (paginated) |
| POST | `/api/v1/users/{user_id}/follow` | Follow a user |
| DELETE | `/api/v1/users/{user_id}/follow` | Unfollow a user |
| GET | `/api/v1/users/search?q={query}` | Search users |

## Media / Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/posts` | Create post (photo/video) |
| GET | `/api/v1/posts/{post_id}` | Get post details |
| PUT | `/api/v1/posts/{post_id}` | Update post caption |
| DELETE | `/api/v1/posts/{post_id}` | Delete post |
| GET | `/api/v1/users/{user_id}/posts` | List user's posts |
| POST | `/api/v1/media/upload` | Upload media (multipart) |

## Feed

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/feed` | Get user's news feed (paginated) |
| GET | `/api/v1/feed/{post_id}/related` | Get related posts |
| POST | `/api/v1/feed/{post_id}/seen` | Mark post as seen (for analytics) |

## Interactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/posts/{post_id}/like` | Like a post |
| DELETE | `/api/v1/posts/{post_id}/like` | Unlike a post |
| GET | `/api/v1/posts/{post_id}/likes` | List likes (paginated) |
| POST | `/api/v1/posts/{post_id}/comments` | Add comment |
| GET | `/api/v1/posts/{post_id}/comments` | List comments (paginated) |
| DELETE | `/api/v1/comments/{comment_id}` | Delete comment |
| POST | `/api/v1/posts/{post_id}/save` | Save post |
| DELETE | `/api/v1/posts/{post_id}/save` | Unsave post |

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | List notifications (paginated) |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| GET | `/api/v1/notifications/unread-count` | Get unread count |

## Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/stories` | Create story |
| GET | `/api/v1/stories` | Get user's stories |
| GET | `/api/v1/stories/{story_id}` | View story |
| POST | `/api/v1/stories/{story_id}/view` | Record story view |
| DELETE | `/api/v1/stories/{story_id}` | Delete story |

## Direct Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dm/conversations` | List conversations |
| GET | `/api/v1/dm/conversations/{id}` | Get conversation messages |
| POST | `/api/v1/dm/conversations/{id}/messages` | Send message |
| POST | `/api/v1/dm/conversations` | Start new conversation |
| WebSocket | `/ws/dm` | Real-time messaging |

## Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search/users?q={query}` | Search users |
| GET | `/api/v1/search/hashtags?q={query}` | Search hashtags |
| GET | `/api/v1/search/tags?q={query}` | Autocomplete suggestions |

## Staff-Level API Design Considerations

### Pagination
- Use **cursor-based pagination** (not offset) for feeds and timelines
- Return `next_cursor` and `has_more` in responses
- Cursor is base64-encoded timestamp + post ID for consistent ordering

### Versioning
- URL path versioning: `/api/v1/`, `/api/v2/`
- Maintain 2 major versions in parallel; deprecate with `Sunset` header

### Error Handling
- Standard error format: `{"error": {"code": "RATE_LIMITED", "message": "...", "retry_after": 30}}`
- Use appropriate HTTP status codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 429 (rate limited), 500 (server error)

### Response Optimization
- Support **field selection**: `?fields=id,caption,like_count` to reduce payload
- Use **ETag** headers for conditional requests and caching
- Compress responses with gzip/brotli
