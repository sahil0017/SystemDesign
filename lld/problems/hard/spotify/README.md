# Spotify

## Problem Statement

Design a music streaming service like Spotify that supports user accounts, playlists, music search, streaming, recommendations, and social features.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **User management**: Sign up, login, profile management, premium/free tiers.
- **Music library**: Browse songs, albums, artists; search by name, genre, mood.
- **Playlists**: Create, edit, share playlists; follow other users' playlists.
- **Streaming**: Play songs with play/pause/seek; offline download for premium users.
- **Recommendations**: "Discover Weekly," "Daily Mix," and "Because you listened to" suggestions.
- **Social**: Follow friends, see what they're listening to, share songs.
- **Podcasts**: Support podcast subscriptions and episodes.

### Non-Functional Requirements
- **Scale**: 500M+ users; 100M+ songs; 50M+ concurrent streams.
- **Latency**: Song start < 500ms; search < 1s; playlist load < 2s.
- **Availability**: 99.99% uptime for streaming; CDN for global delivery.

## Key Design Decisions
- **CDN**: Cache music files at edge locations for low-latency streaming.
- **Recommendation engine**: Collaborative filtering + content-based filtering hybrid.
- **Playlist storage**: Denormalized playlist snapshots for fast reads.
- **Streaming protocol**: HLS/DASH for adaptive bitrate streaming.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│  Playlist    │────►│    Song      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - playlistId │     │ - songId     │
│ - name       │     │ - name       │     │ - title      │
│ - tier       │     │ - isPublic   │     │ - artist     │
└──────────────┘     │ - songList   │     │ - album      │
                     └──────────────┘     │ - duration   │
                                          │ - audioUrl   │
                                          └──────────────┘
```

## Staff-Level Design Considerations

### Streaming Architecture
- **Adaptive bitrate**: Multiple quality levels (128kbps, 256kbps, 320kbps). Client adapts based on bandwidth.
- **Staff insight**: Use HLS (HTTP Live Streaming) with segmented .ts files. This is the industry standard for audio/video streaming.

### Recommendation System
- **Collaborative filtering**: "Users who liked X also liked Y." Matrix factorization (SVD) for scalability.
- **Content-based**: "Similar to songs you liked." Audio features (tempo, key, energy) from ML models.
- **Staff insight**: Hybrid approach is best. Collaborative filtering suffers from cold-start for new songs. Content-based fills the gap.

### Playlist Performance
- **Denormalization**: Store playlist as a snapshot (array of song IDs) rather than querying a join table.
- **Staff insight**: Playlists are read-heavy. Denormalize writes (update snapshot on add/remove) for O(1) reads.
