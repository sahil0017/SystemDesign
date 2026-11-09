# YouTube

## Problem Statement

Design a video streaming platform like YouTube that supports video upload, transcoding, storage, CDN distribution, personalized recommendations, comments, likes, and real-time live streaming at scale (500 hours of video uploaded per minute, 2B+ users).

## Requirements

### Functional Requirements
- **User Management**: Channel creation, subscriber management, content creator tools
- **Video Upload**: Multi-part upload for large files (up to 128GB or 16 hours)
- **Video Transcoding**: Automatic conversion to multiple resolutions (144p to 4K) and formats
- **Video Playback**: Adaptive bitrate streaming (HLS/DASH) with quality switching
- **Search**: Video search by title, description, tags with autocomplete
- **Recommendations**: Personalized video recommendations based on watch history
- **Comments & Likes**: Video comments, replies, likes/dislikes, community tab
- **Live Streaming**: Real-time streaming with chat, super chats, viewer count
- **Monetization**: Ad insertion, channel memberships, Super Chat, YouTube Premium

### Non-Functional Requirements
- **Scale**: 500 hours/min uploaded; 2B+ users; petabytes of video storage
- **Latency**: Video start < 2 seconds; seek < 1 second; search < 500ms
- **Availability**: 99.99% uptime for playback; 99.9% for upload
- **Storage**: Exabytes of video storage with multi-region replication
- **Bandwidth**: TB/hour of video streaming bandwidth via CDN
- **Global**: Multi-region CDN with edge caching for low-latency playback

## Key Design Decisions
- **Video Storage**: Object storage (S3/GCS) with multi-region replication
- **Transcoding**: Async pipeline with FFmpeg; multiple resolutions (144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p)
- **Streaming Protocol**: HLS (HTTP Live Streaming) and DASH (Dynamic Adaptive Streaming over HTTP)
- **CDN**: Multi-CDN strategy (CloudFront, Akamai, Cloudflare) with origin shield
- **Database**: Cassandra for video metadata; PostgreSQL for user data; Redis for caching
- **Recommendations**: ML-based collaborative filtering + content-based filtering
- **Live Streaming**: RTMP ingest → HLS/DASH output → CDN distribution
