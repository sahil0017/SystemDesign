# Compression vs CPU

## Trade-off Overview

Compressing data reduces bandwidth and storage but consumes CPU for compression/decompression. The trade-off depends on whether your system is bandwidth-bound or CPU-bound.

## Compression (gzip, Brotli, Zstd)
- **Pros**: Reduced bandwidth (60-90% savings), faster network transfer, less storage.
- **Cons**: CPU overhead for compress/decompress, added latency.
- **Use when**: Bandwidth is the bottleneck, large payloads, slow networks.

## No Compression
- **Pros**: Zero CPU overhead, lower latency, simpler pipeline.
- **Cons**: Higher bandwidth usage, slower transfer over slow networks.
- **Use when**: CPU is the bottleneck, small payloads, fast networks (LAN).

## Staff-Level Insight

> "Compress for external APIs, skip for internal microservices on fast networks."

- **Staff insight**: Use **gzip for external APIs** (reduces bandwidth cost and improves user experience). Use **no compression for internal gRPC** on fast networks (CPU savings outweigh bandwidth). Use **Zstd** for best compression/CPU ratio. For APIs, set `Content-Encoding: gzip` and let the HTTP client handle decompression — don't compress in application code.
