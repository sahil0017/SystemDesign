# Google Maps (Proximity Service)

## Problem Statement

Design a proximity service like Google Maps that supports location storage, nearby place search, route planning, real-time traffic, and geocoding.

**Reference**: ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Place search**: Find nearby places by category, rating, and distance.
- **Geocoding**: Convert addresses to coordinates and vice versa.
- **Route planning**: Calculate optimal routes between points; support driving, walking, cycling.
- **Real-time traffic**: Live traffic data; ETA estimation.
- **Place details**: Business hours, photos, reviews, contact info.
- **Autocomplete**: Address and place name autocomplete.

### Non-Functional Requirements
- **Scale**: 1B+ places; 100M+ queries per day; global coverage.
- **Latency**: Nearby search < 200ms; route calculation < 1s.
- **Accuracy**: Location queries return results within 1% error margin.

## Key Design Decisions
- **Geospatial indexing**: QuadTree or GeoHash for efficient nearby queries.
- **H3 indexing**: Hexagonal grid for uniform spatial partitioning.
- **Graph database**: Road network as a graph; Dijkstra/A* for route finding.
- **Caching**: Cache popular queries and routes.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                            → Search Service (nearby places)
                            → Routing Service (pathfinding)
                            → Geocoding Service
                            → Traffic Service (real-time)
                            
Search Service → GeoHash Index (Redis/GeoDB)
Routing Service → Graph DB (road network) → A* Algorithm
Traffic Service → Kafka (GPS streams) → Aggregation Engine
```

## Staff-Level Design Considerations

### Geospatial Indexing
- **GeoHash**: Encode lat/lon into a string prefix. Nearby places share prefix. Query by prefix + bounding box filter.
- **Staff insight**: GeoHash has boundary problems — two points on opposite sides of a cell boundary may have very different hashes. Use H3 (hexagonal grid) for uniform neighbors, or combine GeoHash with a bounding box filter.

### Route Finding
- **A* algorithm**: Heuristic-based search that's faster than Dijkstra for point-to-point routing.
- **Staff insight**: Pre-compute contraction hierarchies (CH) for the road graph. This reduces route finding from O(E log V) to O(log V) with preprocessing. This is what OSRM (Open Source Routing Machine) uses.

### Real-Time Traffic
- **GPS aggregation**: Collect anonymized GPS data from users → Kafka → aggregate by road segment → compute average speed.
- **Staff insight**: Use a sliding window (5 minutes) to compute current speed per road segment. Compare with free-flow speed to determine congestion level. This is what Google Maps actually does.
