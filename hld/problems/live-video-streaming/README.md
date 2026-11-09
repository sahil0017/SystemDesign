# Live Video Streaming Platform

## Problem Statement

Design a live video streaming platform (Twitch-like) that handles video ingestion, real-time transcoding, low-latency delivery via CDN, chat integration, and viewer scaling for 1M+ concurrent viewers per stream.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Video ingestion**: Accept RTMP ingest from broadcasters; support multiple bitrates.
- **Transcoding**: Real-time transcoding to multiple resolutions (360p to 1080p) and bitrates.
- **Adaptive bitrate streaming**: Deliver HLS/DASH streams with automatic quality switching.
- **CDN distribution**: Multi-CDN strategy for global low-latency delivery.
- **Live chat**: Real-time chat with moderation, emotes, and subscriber perks.
- **VOD storage**: Record and store streams for on-demand playback.
- **Analytics**: Real-time viewer count, drop-off rates, and engagement metrics.

### Non-Functional Requirements
- **Scale**: 100K+ concurrent streams; 1M+ viewers per stream.
- **Latency**: Live streaming latency < 5s (LL-HLS) or < 2s (WebRTC mode).
- **Availability**: 99.99% uptime for ingest; automatic failover for CDN.
- **Quality**: Sub-second rebuffering; seamless bitrate switching.

## Key Design Decisions
- **Ingest protocol**: RTMP for broadcaster ingest (industry standard); WebRTC for ultra-low-latency.
- **Transcoding**: GPU-based transcoding (NVENC) for cost efficiency; one-pass H.264.
- **Delivery protocol**: HLS for compatibility; LL-HLS for low latency; WebRTC for interactive streams.
- **Multi-CDN**: Use primary + backup CDN with active health checking and automatic failover.

## Architecture Overview

```
Broadcaster → RTMP Ingest → Transcoding Cluster (GPU)
                                    → Origin Server (HLS/DASH)
                                    → Multi-CDN → Viewer (Adaptive Bitrate)
                                    → VOD Storage (S3)
Chat → WebSocket Gateway → Chat Service → Moderation → Redis Pub/Sub
```

## Staff-Level Design Considerations

### Ingest and Transcoding
- **RTMP ingest**: Industry standard for OBS, Streamlabs, etc. Accept on multiple edge ingest servers.
- **GPU transcoding**: Use NVENC (NVIDIA) for 10x throughput vs software x264 at similar quality.
- **Ladder encoding**: Transcode to 5-6 bitrate ladders (360p, 480p, 720p, 720p60, 1080p, 1080p60).
- **Staff insight**: Transcoding is the most expensive part of streaming. Use GPU instances (p3/g4 on AWS) and pack multiple streams per GPU. A single A100 can transcode 100+ 1080p streams simultaneously.

### Adaptive Bitrate Streaming
- **HLS**: Segment video into 6-second TS/fMP4 chunks; manifest file lists available bitrates.
- **LL-HLS**: Use 2-second segments with block-based updates for < 5s latency.
- **Client logic**: Viewer client adapts bitrate based on buffer health and network conditions.
- **Staff insight**: HLS is the standard for a reason — it works everywhere. Use LL-HLS (Low-Latency HLS) introduced by Apple for < 5s latency. For < 2s latency, use WebRTC, but it's more complex and less compatible.

### Multi-CDN Strategy
- **Primary CDN**: Route 80% of traffic to the primary CDN (e.g., CloudFront).
- **Backup CDN**: Route 20% to a secondary CDN (e.g., Fastly) for redundancy.
- **Health checking**: Monitor CDN origin-pull latency; switch traffic on failure.
- **Staff insight**: Single-CDN is a single point of failure. Multi-CDN with DNS-based routing (GeoDNS) ensures availability during CDN outages. Fastly is popular for backup because of its instant purging and edge compute.

### Live Chat at Scale
- **WebSocket**: Persistent connections for real-time bidirectional chat.
- **Redis Pub/Sub**: Fan-out chat messages to all viewers of a stream.
- **Moderation**: Keyword filtering, rate limiting, and auto-ban for spam.
- **Staff insight**: Chat is the engagement driver. At 1M viewers, you're processing 100K+ messages/sec. Use a hierarchical pub/sub: one WebSocket server per shard, with Redis as the message bus. Drop messages (not error) during overload to keep the system stable.

### VOD and Storage
- **Recording**: Concatenate HLS segments during the stream; store in S3.
- **Post-processing**: After the stream, transcode to higher-quality VOD format.
- **Lifecycle**: Move old VODs to cold storage (S3 Glacier) after 90 days.
- **Staff insight**: VOD is a revenue driver (re-watches, clips). Store raw segments during the stream and assemble post-stream to avoid adding latency to the live path.
