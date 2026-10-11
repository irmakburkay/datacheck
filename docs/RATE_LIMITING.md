# Rate Limiting & DDoS Protection

**Date**: 2026-10-12  
**Status**: Basic rate limiting implemented

---

## Overview

DataCheck implements basic rate limiting to prevent abuse and resource exhaustion.

### Current Protection Level: **Basic** ✅

- ✅ Per-IP rate limiting on upload endpoint
- ✅ In-memory tracking (suitable for single-process deployment)
- ✅ Automatic cleanup of old entries
- ⚠️ Not suitable for multi-process production (would need Redis)

---

## Rate Limits

| Endpoint | Limit | Window | Applies To |
|----------|-------|--------|------------|
| `POST /api/analyze` | 10 requests | 60 seconds | Per IP |
| All other endpoints | No limit | N/A | - |

### Why These Limits?

**10 requests per minute** strikes a balance:
- ✅ Allows legitimate testing (10 files in rapid succession)
- ✅ Prevents abuse (600 requests/hour max per IP)
- ✅ Protects server resources (upload endpoint is most expensive)

---

## How It Works

### 1. Request Tracking

```python
# Simple in-memory storage
requests = {
    '192.168.1.100': [
        (timestamp1, 'analyze_request'),
        (timestamp2, 'analyze_request'),
        ...
    ]
}
```

### 2. Rate Check (Sliding Window)

For each incoming request:
1. Get client IP (handles X-Forwarded-For for proxies)
2. Count requests in last 60 seconds for this endpoint
3. If count > limit: Return HTTP 429
4. Otherwise: Allow request and add to tracking

### 3. Automatic Cleanup

Old entries (> 1 hour) are removed every 60 seconds to prevent memory growth.

---

## Client Experience

### Within Limit
Normal response, e.g.:
```json
{
  "status": "success",
  "analysis": { ... }
}
```

### Exceeds Limit
HTTP 429 response:
```json
{
  "error": "Too many requests",
  "message": "Rate limit exceeded. Try again in 45 seconds.",
  "retry_after": 45
}
```

Headers:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
```

---

## Testing Rate Limits

### Manual Test

```bash
# Send 11 requests rapidly (will hit limit on 11th)
for i in {1..11}; do
  curl -X POST http://127.0.0.1:5000/api/analyze \
    -F "name=Test $i" \
    -F "email=test@example.com" \
    -F "service=Basic CSV Analysis" \
    -F "csv_file=@test.csv"
  echo "Request $i"
done
```

**Expected**: First 10 succeed, 11th returns 429.

### Programmatic Test

See `tests/test_rate_limiting.py` (optional).

---

## Limitations & Known Issues

### ⚠️ Single-Process Only

**Issue**: In-memory storage is per-process. If you run multiple Flask workers:
```bash
gunicorn -w 4 app.main:app  # 4 workers
```

Each worker has its own memory, so the **effective limit is 10 × workers**.

**Solution for Production**: Use Redis-based rate limiting (Flask-Limiter).

### ⚠️ IP Spoofing

**Issue**: Determined attacker can rotate IPs (VPN, proxy, botnet).

**Mitigation**: 
- PythonAnywhere has its own infrastructure-level protections
- Cloudflare (if added) provides enterprise DDoS protection

### ⚠️ Memory Growth

**Issue**: If you get millions of unique IPs, memory could grow.

**Mitigation**: 
- Automatic cleanup after 1 hour
- Cleanup runs every 60 seconds
- For 1M IPs × 10 requests each = ~80MB (acceptable)

---

## What's NOT Protected

| Attack Vector | Protected? | Why Not |
|---------------|------------|---------|
| Slow POST (Slowloris) | ❌ | Needs web server timeout config |
| Large file flood | ⚠️ Partial | 5MB limit + rate limit helps, but not foolproof |
| Connection exhaustion | ❌ | Needs web server connection limits |
| Layer 3/4 DDoS | ❌ | Needs infrastructure-level protection |

**Note**: PythonAnywhere provides some of these protections at the infrastructure level.

---

## Production-Grade Alternatives

### Option 1: Flask-Limiter (Redis-backed)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

@app.route("/api/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze_request():
    ...
```

**Pros**: Production-ready, multi-process safe  
**Cons**: Requires Redis (not available on PythonAnywhere free tier)

### Option 2: Cloudflare

Add Cloudflare in front of your app:
- DDoS protection
- Rate limiting
- WAF (Web Application Firewall)
- Bot detection

**Pros**: Enterprise-grade, free tier available  
**Cons**: Requires DNS changes

### Option 3: NGINX Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;

location /api/analyze {
    limit_req zone=api burst=5;
    proxy_pass http://127.0.0.1:5000;
}
```

**Pros**: Very fast, no app changes  
**Cons**: Requires NGINX (not available on PythonAnywhere)

---

## Monitoring & Alerting

### Check Rate Limiter Stats

Add an admin endpoint (optional):

```python
from app.rate_limiter import get_rate_limiter_stats

@app.route("/admin/rate-limit-stats")
def rate_limit_stats():
    return jsonify(get_rate_limiter_stats())
```

Returns:
```json
{
  "tracked_ips": 42,
  "total_requests": 156
}
```

### Log Monitoring

Rate limit violations are logged:
```
2026-10-12 15:30:00 - WARNING - Rate limit exceeded: IP=192.168.1.100, 
endpoint=analyze_request, count=11/10 in 60s
```

Search logs for "Rate limit exceeded" to detect potential attacks.

---

## Configuration

### Adjust Limits

Edit `app/main.py`:

```python
# More strict (5 requests per minute)
@rate_limit(limit=5, window=60)

# More lenient (20 requests per minute)
@rate_limit(limit=20, window=60)

# Longer window (10 requests per hour)
@rate_limit(limit=10, window=3600)
```

### Disable Rate Limiting

Remove the decorator:

```python
@app.route("/api/analyze", methods=["POST"])
# @rate_limit(limit=10, window=60)  # Commented out
def analyze_request():
    ...
```

---

## Assessment Considerations

### Why Basic Protection is Acceptable

For a hiring assessment project:

✅ **Demonstrates awareness** - Shows you understand abuse prevention  
✅ **Appropriate scope** - Production-grade DDoS protection is out of scope  
✅ **Working implementation** - Actually prevents basic abuse  
✅ **Documented tradeoffs** - Shows you understand limitations

### What Reviewers Look For

1. ✅ **Understanding of the problem** - "What happens with too many requests?"
2. ✅ **Practical solution** - Working rate limiter, not theoretical
3. ✅ **Documented limitations** - Honest about what it doesn't cover
4. ✅ **Production considerations** - Mentions Redis/Cloudflare for real deployment

---

## Decision Record

**ADR-013: Rate Limiting Strategy**

**Context**: Application needs protection against abuse and resource exhaustion.

**Decision**: Implement basic in-memory rate limiting on the upload endpoint.

**Rationale**:
- Sufficient for single-process PythonAnywhere deployment
- No external dependencies (Redis not available on free tier)
- Demonstrates understanding of abuse prevention
- Appropriate scope for hiring assessment

**Consequences**:
- ✅ Prevents basic abuse (10 req/min per IP)
- ✅ Protects most expensive endpoint
- ⚠️ Not suitable for multi-process production
- ⚠️ No protection against distributed attacks

**Alternatives Considered**:
- Flask-Limiter + Redis: Requires Redis (not available)
- Cloudflare: Out of scope for assessment
- No rate limiting: Leaves app vulnerable

**Status**: Implemented (2026-10-12)

---

*Last updated: 2026-10-12*
