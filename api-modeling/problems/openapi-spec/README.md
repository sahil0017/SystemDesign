# OpenAPI Specification

## Problem Statement

Design a contract-first API using OpenAPI 3.0 specification. Define paths, schemas, parameters, responses, and security for automated code generation and documentation.

**Reference**: Educative.io, ByteByteGo

## Key Concepts

- **Contract-first**: Define OpenAPI spec before implementation
- **Code generation**: Generate server stubs and client SDKs from spec
- **Documentation**: Auto-generated API docs (Swagger UI, Redoc)
- **Validation**: Validate requests/responses against spec

## Staff-Level Insight

> "OpenAPI spec is the single source of truth for your API."

- **Staff insight**: Use **OpenAPI 3.0** for REST APIs. Define spec first, then generate server stubs (OpenAPI Generator) and client SDKs. Host **Swagger UI** at `/api/docs` for interactive testing. Use **Spectral** for linting — enforce naming conventions, required fields, and response formats. Run spec validation in CI — reject PRs that break the contract.
