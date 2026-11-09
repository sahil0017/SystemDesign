# LeetCode System

## Problem Statement

Design an online coding platform like LeetCode that supports problem management, code submission, automated testing, leaderboards, and contest features.

**Reference**: Educative.io, HelloInterview

## Requirements

### Functional Requirements
- **Problem management**: Create problems with description, examples, constraints, and test cases.
- **Code editor**: In-browser code editor with syntax highlighting and auto-completion.
- **Submission**: Submit code in multiple languages (Java, Python, C++, Go, etc.).
- **Testing**: Run code against hidden and visible test cases; report pass/fail with execution time and memory.
- **Leaderboard**: Rank users by problems solved, contest score, and streak.
- **Contests**: Time-limited coding competitions with real-time ranking.

### Non-Functional Requirements
- **Scale**: 10M+ users; 100K+ submissions per day; 100+ programming languages.
- **Latency**: Submission result < 30s; problem page load < 1s.
- **Security**: Sandboxed execution; no access to host system; resource limits.

## Key Design Decisions
- **Sandboxed execution**: Docker containers for isolated code execution with resource limits.
- **Submission queue**: Async processing with Kafka; workers pick up submissions and execute.
- **Test case management**: Hidden test cases stored securely; encrypted at rest.
- **Language runners**: Pre-built Docker images for each supported language.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                            → Problem Service
                            → Submission Service
                            → Leaderboard Service
                            
Submission Service → Kafka → Worker Pool
                                    → Docker Sandbox (execute code)
                                    → Result Service (store results)
                                    → WebSocket (push results to client)
```

## Staff-Level Design Considerations

### Sandboxed Execution
- **Docker containers**: Each submission runs in an isolated container with CPU, memory, and time limits.
- **Staff insight**: Use cgroups for resource limits (CPU: 10s, memory: 256MB). Use seccomp profiles to restrict system calls. Never trust user code — assume it's malicious.

### Submission Queue Design
- **Async processing**: Submissions are queued and processed by a pool of workers. Each worker runs one submission at a time.
- **Staff insight**: Use Kafka with per-language topics. This allows scaling Python workers independently from C++ workers. The result is pushed to the client via WebSocket when ready.

### Anti-Cheating for Contests
- **Plagiarism detection**: Compare submission patterns, variable names, and solution structure.
- **Staff insight**: Use a combination of AST (Abstract Syntax Tree) comparison and string similarity (Levenshtein distance). For contests, restrict access to external resources by running in an isolated network namespace.
