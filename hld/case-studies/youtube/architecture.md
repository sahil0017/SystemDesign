# YouTube - Architecture

## System Components

1. **API Gateway**: Entry point; authentication, rate limiting, request routing
2. **Upload Service**: Multi-part video upload with resumable uploads
3. **Transcoding Service**: Async video processing pipeline (FFmpeg) for multiple resolutions
4. **Video Service**: Video metadata, playback URLs, quality selection
5. **Recommendation Service**: ML-based personalized video recommendations
6. **Search Service**: Video search with Elasticsearch
7. **Comment Service**: Video comments, replies, moderation
8. **Live Streaming Service**: RTMP ingest, HLS/DASH output, real-time chat
9. **Analytics Service**: View counts, watch time, engagement metrics
10. **Ad Service**: Ad insertion, targeting, revenue tracking
11. **Notification Service**: Subscriber notifications, trending alerts
12. **Object Storage (S3/GCS)**: Raw and transcoded video storage
13. **CDN (CloudFront/Akamai)**: Global video distribution with edge caching
14. **Database (Cassandra)**: Video metadata, comments, likes at scale
15. **Database (PostgreSQL)**: User data, channels, subscriptions
16. **Cache (Redis)**: Hot video cache, view counters, session data
17. **Message Queue (Kafka)**: Transcoding jobs, analytics events, notifications

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                      CDN                            │
                    │         Transcoded video segments (HLS/DASH)         │
                    └─────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │Upload  │  │   Video  │  │Recommend │  │  Search  │  │ Comment  │  │   Ad   │
   │Service │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Transcoding jobs, analytics, notifications   │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │ Cassandra│  │   Redis  │  │ S3/GCS   │  │ Elastic- │  │Transcode│
   │(Users,   │  │(Video    │  │(Cache,   │  │(Video    │  │search    │  │Service │
   │Channels) │  │ metadata)│  │ Counters)│  │ storage) │  │(Search)  │  │(FFmpeg) │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Video Upload & Transcoding Flow
- Creator uploads video via multi-part upload → Upload Service
- Upload Service stores raw video in S3/GCS
- Upload Service publishes transcoding job to Kafka
- Transcoding Service consumes job → runs FFmpeg pipeline
- FFmpeg generates multiple resolutions: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p
- Each resolution split into 2-10 second segments (.ts files)
- Manifest files (.m3u8 for HLS, .mpd for DASH) generated
- Transcoded segments stored in S3 and pushed to CDN
- Video metadata updated in Cassandra with status = "ready"

### 2. Video Playback Flow
- User requests video → Video Service
- Video Service fetches video metadata from Cassandra/Redis
- Returns manifest URL (HLS/DASH) from CDN
- Player fetches manifest → selects initial quality based on bandwidth
- Player requests video segments from CDN
- **Adaptive bitrate**: Player switches quality based on real-time bandwidth
- Analytics Service tracks watch time, drop-off points, quality switches

### 3. Recommendation Flow
- User opens homepage → Recommendation Service
- Service fetches user's watch history, subscriptions, likes
- ML model scores candidate videos (collaborative filtering + content-based)
- Top 50 videos ranked and returned
- On video page: "Up Next" sidebar with contextual recommendations
- **Staff insight**: Use **two-tower model** — user tower + item tower → similarity score

### 4. Live Streaming Flow
- Streamer connects via RTMP → Live Streaming Service
- Service transcodes in real-time to multiple resolutions
- HLS segments generated every 2-6 seconds
- Segments pushed to CDN for global distribution
- Viewers connect via HLS player with 10-30 second delay
- Real-time chat via WebSocket with rate limiting

## Staff-Level Design Considerations

### Adaptive Bitrate Streaming
- **HLS**: Apple standard; .m3u8 manifest; .ts segments; wider compatibility
- **DASH**: Open standard; .mpd manifest; .m4s segments; more flexible
- **Segment size**: 2-10 seconds; smaller = faster quality switch, more HTTP overhead
- **Staff insight**: Use **both HLS and DASH** for maximum compatibility. Segment size of 4-6 seconds is the sweet spot.

### CDN Strategy
- **Multi-CDN**: Primary (CloudFront) + fallback (Akamai, Cloudflare)
- **Origin shield**: Intermediate cache layer between edge and origin
- **Prefetching**: Popular videos pre-cached to edge before demand spike
- **Staff insight**: At YouTube scale, **90%+ of traffic is served from edge**. Origin only handles cache misses and new uploads.

### Transcoding Pipeline
- **Async processing**: Upload returns immediately; transcoding happens in background
- **Priority queue**: Verified creators and trending videos get priority
- **GPU acceleration**: Use GPU for H.264/VP9/AV1 encoding (10x faster)
- **Staff insight**: Use **AV1 codec** for 30% better compression than H.264 at same quality. Transcode to H.264 (compatibility) + VP9/AV1 (efficiency).

### Storage Optimization
- **Raw video**: Stored in cold storage after transcoding completes
- **Transcoded segments**: Hot storage with multi-region replication
- **Lifecycle policy**: Delete raw video after 30 days; keep transcoded indefinitely
- **Staff insight**: Use **object storage lifecycle policies** to auto-transition to cheaper storage tiers.
