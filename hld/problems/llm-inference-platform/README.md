# LLM Inference Serving Platform

## Problem Statement

Design an LLM inference serving platform that handles high-throughput model inference with GPU batching, continuous batching, speculative decoding, and multi-model management for production AI workloads.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Model management**: Deploy, version, and route traffic across multiple LLM models.
- **Continuous batching**: Dynamically batch incoming requests for GPU efficiency (vLLM-style).
- **Speculative decoding**: Use a small draft model to accelerate inference of a large target model.
- **Token streaming**: Stream responses token-by-token via Server-Sent Events (SSE).
- **Load balancing**: Distribute requests across GPU instances with model-aware scheduling.
- **Rate limiting**: Per-user and per-model rate limits with token-based quotas.
- **Observability**: Track latency, throughput, token usage, and GPU utilization.

### Non-Functional Requirements
- **Scale**: 10K+ concurrent requests; 1M+ tokens per second.
- **Latency**: Time-to-first-token (TTFT) < 500ms; token generation < 50ms/token.
- **Throughput**: 10x higher throughput with continuous batching vs single-request serving.
- **GPU utilization**: > 80% GPU memory and compute utilization under load.

## Key Design Decisions
- **Continuous batching**: Process requests at different stages (prefill/decode) in the same batch.
- **PagedAttention**: Manage KV cache with virtual memory paging (vLLM approach).
- **Speculative decoding**: Draft model proposes n tokens; target model verifies in one forward pass.
- **Model parallelism**: Tensor parallelism for large models across multiple GPUs.

## Architecture Overview

```
Client → API Gateway → Rate Limiter → Request Router
                                        → Model Scheduler (GPU-aware)
                                        → Inference Server (vLLM/TGI)
                                          → GPU Pool (Continuous Batching)
                                          → KV Cache Manager (PagedAttention)
                                        → Token Streamer (SSE)
```

## Staff-Level Design Considerations

### Continuous Batching
- **Problem**: Traditional batching waits for all requests to finish before accepting new ones.
- **Solution**: Insert new requests into the batch when prior requests finish decoding; mix prefill and decode steps.
- **Staff insight**: Continuous batching (Orca/vLLM) is the single biggest throughput improvement. It can 10x throughput vs naive batching by keeping the GPU fully utilized.

### PagedAttention for KV Cache
- **Problem**: KV cache grows linearly with sequence length; fixed allocation wastes memory.
- **Solution**: Treat KV cache as virtual memory with paging; allocate blocks on demand.
- **Staff insight**: PagedAttention reduces memory waste from 60-80% to < 5%. It's the key innovation in vLLM and is now standard in production LLM serving.

### Speculative Decoding
- **How it works**: A small draft model (e.g., 7B) proposes n tokens; the large model (e.g., 70B) verifies all n in one forward pass.
- **Speedup**: 1.5-2x faster when draft model accuracy is high; falls back to normal decoding when draft is poor.
- **Staff insight**: Speculative decoding is most effective when the draft model is well-tuned to the target model's distribution. Use distillation or prefix matching for best results.

### GPU Load Balancing
- **Model-aware scheduling**: Route requests to instances with the correct model loaded; avoid cold starts.
- **Preemption**: Evict low-priority requests when GPU memory is full; resume from saved KV cache.
- **Staff insight**: Model loading is the #1 cause of cold-start latency. Keep hot models pre-loaded on GPUs and use model warmup requests before routing live traffic.

### Token Streaming
- **SSE**: Stream tokens as they're generated; client renders in real-time.
- **Backpressure**: If client can't keep up, buffer tokens; drop oldest if buffer is full.
- **Staff insight**: Streaming is critical for UX. Even if the full response takes 10s, showing tokens at 50ms each makes it feel instant. Use SSE over WebSockets for simplicity and HTTP compatibility.
