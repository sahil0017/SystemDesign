# Library Management System

## Problem Statement (Staff-Level)

Design a library management system that handles book cataloging, member management, borrowing/returning, reservations, fines, inter-library loans, and digital resources. The system should support 100K+ books, 50K+ members, and concurrent check-in/check-out operations with real-time availability tracking.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Book catalog**: Search by title, author, ISBN, genre; filter by availability
- **Member management**: Registration, membership tiers (student, faculty, public)
- **Borrowing**: Check-out with due dates; renewal; hold/reservation queue
- **Returns**: Check-in with damage assessment; late fee calculation
- **Reservations**: Queue-based holds; notification when available; expiry
- **Fines**: Late return fees; lost book charges; waiver system
- **Inter-library loans**: Request books from partner libraries; tracking
- **Digital resources**: E-books, journals with license management

### Non-Functional Requirements
- **Scale**: 100K+ books; 50K+ members; 1K+ concurrent operations
- **Latency**: Search < 500ms; check-out < 2s; fine calculation < 100ms
- **Availability**: 99.9% uptime; offline mode for library terminals
- **Concurrency**: Prevent double-checkout of same copy

## Key Design Decisions
- **Search**: Elasticsearch for full-text search; PostgreSQL for transactions
- **Concurrency**: Optimistic locking for book copies; distributed lock for reservations
- **Fine engine**: Strategy pattern for different fine rules by membership tier

## Staff-Level Design Considerations

### Reservation Queue
- **FIFO queue** with priority (faculty > student > public)
- **Notification**: Email/SMS when book is available; 48h pickup window
- **Staff insight**: Use **priority queue** for fair but tiered reservation system

### Concurrency Control
- **Optimistic locking**: Version column on BookCopy; retry on conflict
- **Staff insight**: Double-checkout is the #1 bug. Use **atomic compare-and-swap**
