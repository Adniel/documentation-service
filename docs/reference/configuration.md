# Configuration Reference

All configuration is managed through environment variables, loaded via Pydantic `BaseSettings` in `backend/src/config.py`. Values can be set in a `.env` file or directly as environment variables.

## Environment

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENVIRONMENT` | `development` \| `staging` \| `production` | `development` | Deployment environment |
| `DEBUG` | bool | `true` | Enable debug mode (verbose SQL logging, detailed errors) |

## API

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_PREFIX` | string | `/api/v1` | URL prefix for all API routes |
| `API_TITLE` | string | `Documentation Service API` | OpenAPI documentation title |
| `API_VERSION` | string | `0.1.0` | API version string |

## Security

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | string | `dev_secret_key_change_in_production` | JWT signing key. **Must change in production.** |
| `ALGORITHM` | string | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | int | `7` | Refresh token lifetime in days |

## Database

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_USER` | string | `docservice` | PostgreSQL username |
| `POSTGRES_PASSWORD` | string | `docservice_dev` | PostgreSQL password |
| `POSTGRES_HOST` | string | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | int | `5432` | PostgreSQL port |
| `POSTGRES_DB` | string | `docservice` | PostgreSQL database name |

Computed URLs (not set directly):
- `database_url` — `postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}`
- `sync_database_url` — `postgresql://{user}:{password}@{host}:{port}/{db}` (for Alembic)

## Redis

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | string | `redis://localhost:6379` | Redis connection URL for caching and sessions |

## Meilisearch

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MEILISEARCH_URL` | string | `http://localhost:7700` | Meilisearch instance URL |
| `MEILISEARCH_API_KEY` | string | `docservice_dev_key` | Meilisearch API key |

## Git

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GIT_REPOS_PATH` | string | `/tmp/docservice/repos` | Base directory for Git repositories |

## Git Remote (Sprint 13)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GIT_CREDENTIAL_ENCRYPTION_KEY` | string | `""` | Base64-encoded 32-byte key for encrypting stored Git credentials |
| `GIT_SYNC_TIMEOUT_SECONDS` | int | `120` | Timeout for remote Git operations |
| `GIT_WEBHOOK_RATE_LIMIT` | int | `10` | Max webhook requests per minute per organization |
| `GIT_DEFAULT_SYNC_STRATEGY` | string | `push_only` | Default sync strategy: `push_only`, `pull_only`, `bidirectional` |
| `GIT_ALLOWED_PROVIDERS` | string | `github,gitlab,gitea,custom` | Comma-separated list of allowed Git remote providers |

## Attachments (Sprint F)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ATTACHMENT_STORAGE_BACKEND` | string | `local` | Storage backend: `local` or `s3` |
| `ATTACHMENT_STORAGE_PATH` | string | `/tmp/docservice/attachments` | Local storage directory (when backend is `local`) |
| `ATTACHMENT_S3_BUCKET` | string | `""` | S3 bucket name (when backend is `s3`) |
| `ATTACHMENT_S3_REGION` | string | `us-east-1` | S3 region |
| `ATTACHMENT_S3_ENDPOINT_URL` | string | `""` | S3 endpoint URL (for MinIO or compatible services) |
| `ATTACHMENT_S3_ACCESS_KEY` | string | `""` | S3 access key ID |
| `ATTACHMENT_S3_SECRET_KEY` | string | `""` | S3 secret access key |
| `ATTACHMENT_MAX_FILE_SIZE_MB` | int | `100` | Maximum upload file size in megabytes |

## CORS

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed CORS origins |

## Example `.env` File

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Security (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your-production-secret-key-at-least-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=1

# Database
POSTGRES_USER=docservice
POSTGRES_PASSWORD=strong-production-password
POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=docservice_prod

# Redis
REDIS_URL=redis://redis.example.com:6379

# Search
MEILISEARCH_URL=http://search.example.com:7700
MEILISEARCH_API_KEY=production-meili-key

# Git
GIT_REPOS_PATH=/var/lib/docservice/repos
GIT_CREDENTIAL_ENCRYPTION_KEY=base64-encoded-32-byte-key

# Attachments
ATTACHMENT_STORAGE_BACKEND=s3
ATTACHMENT_S3_BUCKET=acme-docs-attachments
ATTACHMENT_S3_REGION=us-east-1

# CORS
CORS_ORIGINS=https://docs.acme.com,https://admin.acme.com
```
