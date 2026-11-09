# WhatsApp

## Problem Statement

Design a real-time messaging platform like WhatsApp that supports 1:1 and group messaging, media sharing, read receipts, online status, end-to-end encryption, and voice/video calls at scale (2B+ users, 100B+ messages/day).

## Requirements

### Functional Requirements
- **User Management**: Phone number-based registration, profile management, contact discovery
- **1:1 Messaging**: Real-time text messages with delivery/read receipts
- **Group Messaging**: Create groups, add/remove members, admin controls, group media
- **Media Sharing**: Photos, videos, documents, voice messages with compression
- **Status/Stories**: Ephemeral status updates visible for 24 hours
- **Read Receipts**: Delivered (one check), read (blue checks), online status
- **End-to-End Encryption**: Signal Protocol for message encryption
- **Voice/Video Calls**: P2P and group calls with WebRTC
- **Message Types**: Text, image, video, audio, document, location, contact

### Non-Functional Requirements
- **Scale**: 2B+ users; 100B+ messages/day; 50M+ messages/sec peak
- **Latency**: Message delivery < 1 second p99; end-to-end < 2 seconds
- **Availability**: 99.99% uptime; messages never lost
- **Offline Support**: Messages queued and delivered when recipient comes online
- **Encryption**: End-to-end encryption (Signal Protocol) for all messages
- **Global**: Multi-region deployment with low latency worldwide
- **Battery Efficiency**: Minimize battery drain on mobile devices

## Key Design Decisions
- **Protocol**: MQTT for messaging (lightweight, persistent connections, QoS levels)
- **Encryption**: Signal Protocol (Double Ratchet) for end-to-end encryption
- **Message Storage**: Messages stored on server for 30 days for offline delivery, then deleted
- **Presence**: Redis for online/offline status with pub/sub for real-time updates
- **Database**: Cassandra for message storage (high write throughput); PostgreSQL for user data
- **Push Notifications**: FCM/APNs for offline users; WebSocket for online users
- **Media**: Async upload to S3 + CDN; progressive download with thumbnails
