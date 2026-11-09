# API Versioning Fundamentals

## Why Version APIs?

As your application evolves, you'll need to make changes to your API. Versioning ensures that existing clients continue to work while new clients can use the updated API.

## Versioning Strategies

### 1. URI Versioning (Most Common)
```
/v1/users
/v2/users
```
**Pros**: Simple, explicit, easy to cache, works with any HTTP client.
**Cons**: URL clutter, violates pure REST (resource identity changes).

### 2. Header Versioning
```
GET /users
Accept: application/vnd.myapi.v1+json
```
**Pros**: Clean URLs, follows HTTP standards.
**Cons**: Harder to debug, requires custom headers, caching complexity.

### 3. Query Parameter Versioning
```
GET /users?version=1
GET /users?version=2
```
**Pros**: Easy to implement, explicit.
**Cons**: Not RESTful, caching issues, version can be accidentally omitted.

### 4. Content Negotiation (Accept Header)
```
GET /users
Accept: application/vnd.myapi.v2+json
```
**Pros**: Uses standard HTTP mechanism, clean URLs.
**Cons**: Complex to implement, harder to test, caching challenges.

## Recommendation

| Strategy | Internal APIs | Public APIs | Mobile Apps |
|----------|--------------|-------------|-------------|
| URI Versioning | ✅ Best | ✅ Best | ✅ Best |
| Header Versioning | ⚠️ OK | ❌ Avoid | ❌ Avoid |
| Query Parameter | ❌ Avoid | ❌ Avoid | ❌ Avoid |
| Content Negotiation | ⚠️ OK | ⚠️ OK | ❌ Avoid |

**URI versioning** is recommended for most cases due to simplicity and explicitness.

## Version Lifecycle

### Phases
1. **Active**: Current version, receives new features and bug fixes
2. **Maintenance**: Security fixes only, no new features
3. **Deprecated**: Warning headers returned, migration guide provided
4. **Sunset**: Returns 410 Gone, traffic redirected to latest version

### Deprecation Headers
```
Deprecation: true
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## Breaking vs Non-Breaking Changes

### Non-Breaking (No Version Bump)
- Adding new optional fields to response
- Adding new optional query parameters
- Adding new endpoints
- Adding new enum values (if client handles unknown values)

### Breaking (Version Bump Required)
- Removing or renaming fields
- Changing field types (string → integer)
- Making optional fields required
- Changing error response format
- Removing endpoints

## Staff-Level Insights

### Version Strategy
- Start with **v1** from day one — avoids the `/users` vs `/v1/users` migration later
- Support **at least 2 versions** simultaneously during transition
- Set a clear **sunset date** (6-12 months) when deprecating a version

### Backward Compatibility
- Design APIs to be **backward compatible by default**
- Use **default values** for new fields so old clients don't break
- Test with **oldest supported version** client in CI pipeline

### Migration Strategy
- Provide **migration guide** with code examples for each version change
- Use **feature flags** to gradually roll out new version behavior
- Monitor **version adoption metrics** to know when to sunset old versions
