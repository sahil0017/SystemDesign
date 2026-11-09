# API Design Tests

## Overview

Comprehensive test cases for validating API design patterns including REST conventions, error handling, pagination, versioning, and security.

## Test Categories

### 1. REST Convention Tests

```java
@Test
void testGetReturns200() {
    mockMvc.perform(get("/api/v1/products"))
        .andExpect(status().isOk());
}

@Test
void testPostReturns201() {
    mockMvc.perform(post("/api/v1/products")
            .contentType(MediaType.APPLICATION_JSON)
            .content(productJson))
        .andExpect(status().isCreated())
        .andExpect(header().exists("Location"));
}

@Test
void testDeleteReturns204() {
    mockMvc.perform(delete("/api/v1/products/{id}", "prod_123"))
        .andExpect(status().isNoContent());
}

@Test
void testNotFoundReturns404() {
    mockMvc.perform(get("/api/v1/products/{id}", "nonexistent"))
        .andExpect(status().isNotFound());
}
```

### 2. Pagination Tests

```java
@Test
void testCursorPagination() {
    var response = mockMvc.perform(get("/api/v1/products?limit=10"))
        .andExpect(status().isOk())
        .andReturn().getResponse().getContentAsString();
    
    JsonNode json = mapper.readTree(response);
    assertThat(json.get("data").isArray()).isTrue();
    assertThat(json.get("data").size()).isLessThanOrEqualTo(10);
    assertThat(json.get("pagination").get("next")).isNotNull();
}

@Test
void testPaginationConsistency() {
    // Verify cursor pagination returns consistent results
    // even when data changes between requests
}
```

### 3. Error Handling Tests

```java
@Test
void testValidationErrorReturns422() {
    mockMvc.perform(post("/api/v1/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .content(invalidOrderJson))
        .andExpect(status().isUnprocessableEntity())
        .andExpect(jsonPath("$.type").exists())
        .andExpect(jsonPath("$.title").exists())
        .andExpect(jsonPath("$.status").value(422))
        .andExpect(jsonPath("$.errors").isArray());
}

@Test
void testErrorResponseFollowsRfc7807() {
    // Verify error response matches RFC 7807 Problem Detail format
}
```

### 4. Idempotency Tests

```java
@Test
void testPutIsIdempotent() {
    // First PUT
    mockMvc.perform(put("/api/v1/products/{id}", "prod_123")
            .contentType(MediaType.APPLICATION_JSON)
            .content(updateJson))
        .andExpect(status().isOk());
    
    // Second PUT with same data
    mockMvc.perform(put("/api/v1/products/{id}", "prod_123")
            .contentType(MediaType.APPLICATION_JSON)
            .content(updateJson))
        .andExpect(status().isOk());
    
    // Verify product state is same after both requests
}

@Test
void testIdempotencyKey() {
    String idempotencyKey = UUID.randomUUID().toString();
    
    // First POST
    mockMvc.perform(post("/api/v1/orders")
            .header("Idempotency-Key", idempotencyKey)
            .contentType(MediaType.APPLICATION_JSON)
            .content(orderJson))
        .andExpect(status().isCreated());
    
    // Retry with same key
    mockMvc.perform(post("/api/v1/orders")
            .header("Idempotency-Key", idempotencyKey)
            .contentType(MediaType.APPLICATION_JSON)
            .content(orderJson))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.id").value(firstOrderId));
}
```

### 5. Security Tests

```java
@Test
void testUnauthorizedReturns401() {
    mockMvc.perform(get("/api/v1/orders"))
        .andExpect(status().isUnauthorized());
}

@Test
void testForbiddenReturns403() {
    mockMvc.perform(get("/api/v1/users/{id}", "other_user")
            .header("Authorization", "Bearer " + userToken))
        .andExpect(status().isForbidden());
}

@Test
void testRateLimitingReturns429() {
    for (int i = 0; i < 101; i++) {
        mockMvc.perform(get("/api/v1/products"))
            .andExpect(status().isOkay());
    }
    mockMvc.perform(get("/api/v1/products"))
        .andExpect(status().isTooManyRequests())
        .andExpect(header().exists("Retry-After"));
}
```

### 6. Versioning Tests

```java
@Test
void testV1ReturnsV1Format() {
    mockMvc.perform(get("/api/v1/products"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.data").exists());
}

@Test
void testV2ReturnsV2Format() {
    mockMvc.perform(get("/api/v2/products"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.items").exists()); // Different format
}

@Test
void testDeprecatedVersionReturnsHeader() {
    mockMvc.perform(get("/api/v1/products"))
        .andExpect(header().string("Deprecation", "true"))
        .andExpect(header().exists("Sunset"));
}
```

## Staff-Level Testing Insights

- **Test HTTP semantics**: Verify status codes, headers, and idempotency — not just business logic.
- **Test error formats**: Ensure all error responses follow RFC 7807 consistently.
- **Test pagination edge cases**: Empty results, last page, invalid cursor.
- **Staff insight**: Use **contract testing** (Pact) for microservices — verify that API changes don't break consumers. Use **OpenAPI validation** to ensure responses match the spec. Run these tests in CI on every PR.
