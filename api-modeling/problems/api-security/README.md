# API Security

## Problem Statement

Design comprehensive API security including OAuth 2.0, JWT authentication, API key management, CORS, CSRF protection, and rate limiting.

**Reference**: Educative.io, ByteByteGo

## Key Concepts

- **OAuth 2.0**: Authorization flows (Authorization Code, Client Credentials, PKCE)
- **JWT**: Stateless authentication with signed tokens
- **API Keys**: Simple authentication for service-to-service calls
- **CORS**: Cross-Origin Resource Sharing for browser security
- **CSRF**: Cross-Site Request Forgery protection

## Staff-Level Insight

> "Security is not a feature — it's a requirement."

- **Staff insight**: Use **OAuth 2.0 with PKCE** for public clients (SPAs, mobile). Use **Client Credentials** for service-to-service. Never store secrets in client-side code. Use **short-lived access tokens** (15min) with **refresh tokens** (7 days). Validate JWT signature on every request. Set **CORS** to specific origins, never `*` in production. Use **CSRF tokens** for cookie-based auth; not needed for Bearer tokens.
