# YouTube - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via Bearer token except public video playback and search. Rate limited per user tier.

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate session |

## Videos

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/videos` | Create video (initiate upload) |
| GET | `/api/v1/videos/{video_id}` | Get video details |
| PUT | `/api/v1/videos/{video_id}` | Update video metadata |
| DELETE | `/api/v1/videos/{video_id}` | Delete video |
| GET | `/api/v1/videos/{video_id}/stream` | Get streaming manifest URL |
| POST | `/api/v1/videos/upload/{upload_id}` | Upload video chunk (multipart) |
| GET | `/api/v1/channels/{channel_id}/videos` | List channel videos |

## Playback

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/playback/{video_id}/manifest` | Get HLS/DASH manifest |
| POST | `/api/v1/playback/{video_id}/watch` | Record watch event |
| POST | `/api/v1/playback/{video_id}/seek` | Record seek event |

## Channels

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/channels/{channel_id}` | Get channel details |
| PUT | `/api/v1/channels/{channel_id}` | Update channel |
| GET | `/api/v1/channels/{channel_id}/subscribers` | List subscribers |
| POST | `/api/v1/channels/{channel_id}/subscribe` | Subscribe |
| DELETE | `/api/v1/channels/{channel_id}/subscribe` | Unsubscribe |
| GET | `/api/v1/users/me/subscriptions` | My subscriptions |

## Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/videos/{video_id}/comments` | List comments |
| POST | `/api/v1/videos/{video_id}/comments` | Add comment |
| PUT | `/api/v1/comments/{comment_id}` | Update comment |
| DELETE | `/api/v1/comments/{comment_id}` | Delete comment |
| POST | `/api/v1/comments/{comment_id}/like` | Like comment |
| GET | `/api/v1/comments/{comment_id}/replies` | List replies |

## Interactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/videos/{video_id}/like` | Like video |
| DELETE | `/api/v1/videos/{video_id}/like` | Unlike video |
| POST | `/api/v1/videos/{video_id}/dislike` | Dislike video |
| POST | `/api/v1/videos/{video_id}/save` | Save to playlist |

## Search & Recommendations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search?q={query}` | Search videos |
| GET | `/api/v1/search/suggestions?q={query}` | Autocomplete |
| GET | `/api/v1/recommendations` | Personalized recommendations |
| GET | `/api/v1/recommendations/trending` | Trending videos |
| GET | `/api/v1/recommendations/{video_id}/related` | Related videos |

## Live Streaming

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/live_streams` | Create live stream |
| GET | `/api/v1/live_streams/{stream_id}` | Get stream info |
| POST | `/api/v1/live_streams/{stream_id}/start` | Start streaming |
| POST | `/api/v1/live_streams/{stream_id}/stop` | Stop streaming |
| GET | `/api/v1/live_streams/{stream_id}/chat` | Get live chat messages |
| WebSocket | `/ws/live/{stream_id}/chat` | Real-time chat |

## Analytics (Creator)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/videos/{video_id}` | Video analytics |
| GET | `/api/v1/analytics/channel` | Channel analytics |
| GET | `/api/v1/analytics/revenue` | Revenue report |

## Staff-Level API Design Considerations

### Upload API
- **Multi-part upload**: Initiate → upload chunks → complete
- **Resumable uploads**: Support pause/resume with chunk-level retry
- **Signed URLs**: Generate presigned S3 URLs for direct-to-storage upload
- **Progress tracking**: Poll upload status via `GET /videos/{video_id}/upload-status`

### Streaming Manifest Response
```json
{
  "video_id": "v123",
  "hls_manifest": "https://cdn.example.com/v123/playlist.m3u8",
  "dash_manifest": "https://cdn.example.com/v123/manifest.mpd",
  "qualities": ["144p", "240p", "360p", "480p", "720p", "1080p"],
  "duration": 300,
  "thumbnail": "https://cdn.example.com/v123/thumb.jpg"
}
```
