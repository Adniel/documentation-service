# Operations Runbook

> Tier 2 optimizations to implement when the platform reaches significant load. These are documented for future implementation — the platform currently has the foundational infrastructure (structured logging, Redis, health checks, configurable DB pool) from Sprint J.

## 1. Metrics & Monitoring

### Prometheus Endpoint

Add a `/metrics` endpoint using `prometheus-fastapi-instrumentator`:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

### Key Metrics to Track

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total requests by method, path, status |
| `http_request_duration_seconds` | Histogram | Latency p50/p95/p99 |
| `db_pool_size` | Gauge | Current DB connection pool usage |
| `redis_cache_hits_total` | Counter | Cache hit count |
| `redis_cache_misses_total` | Counter | Cache miss count |
| `http_errors_total` | Counter | Error count by status code |

### Grafana Dashboards

Create dashboards for:
- **Request Overview**: Rate, latency percentiles, error rate
- **Database**: Pool usage, query duration, connection wait time
- **Cache**: Hit rate, key count, memory usage
- **Application**: Active users, document operations, search queries

---

## 2. Hot-Path Caching

### Candidates for Caching

| Endpoint/Operation | TTL | Invalidation Trigger |
|--------------------|-----|---------------------|
| Published page renders | 5 min | Page update/publish |
| Search results | 2 min | Content index update |
| Table of contents (space) | 5 min | Page create/move/delete |
| Permission checks | 1 min | ACL change |
| User profile/settings | 5 min | Profile update |

### Strategy: Cache-Aside

```python
# Using the @cached decorator from src.cache
@cached(ttl=300, key_prefix="page_render")
async def get_rendered_page(page_id: str, version: int) -> dict:
    ...
```

### Cache Invalidation

On write operations, delete related cache keys:

```python
await cache.delete(f"cache:page_render:{page_id}:*")
```

Consider using Redis key patterns or tag-based invalidation for groups of related keys.

---

## 3. Redis-Backed Rate Limiting

### Current State

`src/modules/mcp/rate_limiter.py` uses in-memory storage — only works for single-process deployments.

### Migration Path

Replace the in-memory store with Redis sliding window:

```python
async def is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_seconds)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()
    return results[2] > limit
```

### When to Migrate

- When running multiple uvicorn workers (`--workers > 1`)
- When deploying behind a load balancer with multiple instances

---

## 4. Load Testing

### Tool: Locust or k6

Create load test scripts covering:

1. **Concurrent page reads** — 100 users reading published pages
2. **Editor saves** — 20 concurrent users saving content
3. **Search queries** — 50 concurrent search requests
4. **Export generation** — 10 concurrent PDF/DOCX exports
5. **Authentication flow** — Login/token refresh under load

### Baseline Targets

| Scenario | Target p95 | Target Throughput |
|----------|-----------|-------------------|
| Page read | < 200ms | 500 req/s |
| Search | < 500ms | 100 req/s |
| Page save | < 1s | 50 req/s |
| PDF export | < 5s | 10 req/s |
| Auth (login) | < 300ms | 100 req/s |

### Running Tests

```bash
# k6 example
k6 run --vus 50 --duration 5m tests/load/read_pages.js

# Locust example
locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 5m
```

---

## 5. Slow Query Analysis

### PostgreSQL Configuration

Enable slow query logging in `postgresql.conf`:

```ini
log_min_duration_statement = 100   # Log queries > 100ms
log_statement = 'none'             # Don't log all statements
```

### SQLAlchemy Query Logging

For development debugging, set `DB_ECHO=true` in `.env` to enable SQLAlchemy echo mode. The configurable `db_echo` setting (Sprint J) supports this without code changes.

### Common N+1 Patterns to Watch

- Page listing with space/org details
- Permission checks per page in listings
- Attachment metadata for page renders
- Change request with approver details

### Fix Strategies

- Use `selectinload()` or `joinedload()` for relationships
- Aggregate permission queries with `IN` clauses
- Pre-fetch related data in service layer

---

## 6. Connection Pooling

### PgBouncer for Production

When running multiple application workers:

```
workers × db_pool_size ≤ PostgreSQL max_connections
```

Example: 4 workers × 5 pool_size = 20 connections (within default 100 max_connections).

### PgBouncer Configuration

```ini
[databases]
docservice = host=127.0.0.1 port=5432 dbname=docservice

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 20
```

### When to Add PgBouncer

- When connection count approaches PostgreSQL `max_connections`
- When using serverless or auto-scaling infrastructure
- When connection establishment latency becomes significant

---

## 7. Bundle Analysis

### Setup

```bash
npm install -D rollup-plugin-visualizer
```

Add to `vite.config.ts`:

```typescript
import { visualizer } from 'rollup-plugin-visualizer';

plugins: [
  react(),
  visualizer({ open: true, gzipSize: true }),
]
```

### Tree-Shaking Audit

Check for:
- Barrel file re-exports pulling in unused code
- Large utility libraries imported for single functions (use specific imports)
- Icon libraries (import individual icons, not the entire set)

### Dynamic Import Opportunities

Beyond the current lazy routes (Sprint J), consider:
- PDF/DOCX export libraries (only loaded when user clicks export)
- Admin-only components (assessment builder, lifecycle management)
- Diagram rendering (Mermaid, etc.)

---

## 8. Alerting

### Critical Alerts (page immediately)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Health check unhealthy | Any component `error` for > 1 min | Check service, restart if needed |
| Error rate spike | > 5% of requests returning 5xx | Investigate logs, check dependencies |
| Database connection pool exhausted | 0 available connections | Scale pool, check for leaks |

### Warning Alerts (notify within 1 hour)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Response time degradation | p95 > 2x baseline for > 5 min | Profile, check DB queries |
| Cache hit rate drop | < 50% for > 10 min | Check Redis, review TTLs |
| Disk usage | > 80% on any volume | Clean up, expand storage |
| Certificate expiry | < 14 days | Renew certificates |

### Alert Channels

Configure alerts via:
- **PagerDuty/OpsGenie** — Critical alerts
- **Slack/Email** — Warning alerts
- **Grafana Alerting** — Integrates with dashboards

### Health Check Integration

Use the `/health` endpoint (Sprint J) as the basis for uptime monitoring:

```bash
# Simple cron-based check
curl -sf http://localhost:8000/health | jq -e '.status == "healthy"'
```

For production, use an external uptime monitor (UptimeRobot, Pingdom, etc.) pointed at the `/health` endpoint.
