# Cache Control Headers

Cache-Control is an HTTP header used to specify browser caching policies in both client requests and server responses.

## Common Cache-Control Directives

### Response Directives (from server to client)

```
Cache-Control: max-age=3600           # Cache for 3600 seconds (1 hour)
Cache-Control: no-store              # Don't cache at all
Cache-Control: no-cache              # Must revalidate with server before using cached version
Cache-Control: private               # Only browser can cache, not intermediaries
Cache-Control: public                # Any cache can store the response
Cache-Control: must-revalidate       # Must verify cache validity before using
Cache-Control: s-maxage=3600         # Shared cache (CDN) max age
```

### Request Directives (from client to server)

```
Cache-Control: no-cache              # Client wants fresh content
Cache-Control: max-age=0             # Force revalidation of cached content
Cache-Control: max-stale=3600        # Accept stale content up to 1 hour
Cache-Control: min-fresh=600         # Content must be fresh for at least 600 seconds
```

## Common Use Cases and Examples

### Dynamic Content (e.g., API responses)

```
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
```
Ensures content is always fresh
Prevents storing sensitive information
Forces revalidation

### Static Assets (e.g., images, CSS, JS)

```
Cache-Control: public, max-age=31536000
```
Caches for one year
Suitable for content with version numbers or hashes
Improves loading performance

### Private User Data

```
Cache-Control: private, no-cache, must-revalidate
```

Only browser can cache
Must verify with server before using
Protects sensitive information

### CDN Optimization

```
Cache-Control: public, max-age=3600, s-maxage=86400
```
Browser caches for 1 hour
CDN caches for 24 hours
Different rules for browser and CDN

### Combinations and Special Cases

#### Multiple Directives

```
Cache-Control: private, max-age=600, must-revalidate
```
Private cache only
Cache for 10 minutes
Must verify if stale

#### API Version Control

```
Cache-Control: public, max-age=3600, stale-while-revalidate=60
```
Public caching allowed
Cache for 1 hour
Can use stale content while revalidating for 60 seconds

#### No Caching with Explantion

```
Cache-Control: no-store, no-cache, max-age=0, must-revalidate, proxy-revalidate
```
Pragma: no-cache
Expires: 0
Comprehensive no-cache policy
Backwards compatibility (Pragma)
Multiple layers of protection

### In API Gateway Context

When using these headers in API Gateway:

#### Default Caching

```
Cache-Control: max-age=300
```
Standard 5-minute cache

#### Sensitive Endpoints

```
Cache-Control: private, no-cache, must-revalidate
```
Ensures fresh content for private data

#### Public API Responses

```
Cache-Control: public, max-age=3600, s-maxage=7200
```
Browser cache: 1 hour
API Gateway cache: 2 hours

#### Invalidation Control

```
Cache-Control: no-cache
```
Forces revalidation
Can be ignored based on API Gateway settings

### Best Practices

#### Security-Sensitive Content

Always use private and no-store for sensitive data
Include must-revalidate to prevent using stale data

#### Performance Optimization

Use longer max-age for static content
Implement stale-while-revalidate for better user experience

#### CDN Integration

Use s-maxage for CDN-specific rules
Consider stale-if-error for fault tolerance

#### API Versioning

Include version numbers in URLs or headers
Use appropriate cache controls based on version stability
These headers, when properly configured in API Gateway, help control caching behavior across the entire request-response chain, from client through CDN to API Gateway and back.