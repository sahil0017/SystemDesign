# CDN vs Origin Server

## Trade-off Overview

CDN (Content Delivery Network) caches content at edge locations near users. Origin server is the central source of truth for content.

## CDN
- **Pros**: Low latency (edge cache hit), reduces origin load, DDoS protection.
- **Cons**: Cache invalidation complexity, cost at scale, stale content risk.
- **Use when**: Static assets, media, globally distributed users.

## Origin Server
- **Pros**: Always fresh data, full control, no cache invalidation.
- **Cons**: High latency for distant users, single point of overload.
- **Use when**: Dynamic content, personalized data, real-time updates.

## Staff-Level Insight

> "CDN for static, origin for dynamic. Use cache-control headers wisely."

- **Staff insight**: Use **CDN for static assets** (images, CSS, JS, videos) with long TTL (1 year + cache busting). Use **origin for dynamic content** (user profiles, real-time data). For semi-dynamic content (product catalog), use **CDN with short TTL** (5-30 min) and purge on update. Set `Cache-Control` headers correctly: `public, max-age=31536000, immutable` for versioned assets; `private, no-cache` for personalized content.
