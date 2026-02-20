# Architecture

This document explains the three-layer architecture of the Documentation Service Platform, its module boundaries, and key design decisions.

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
│  Block-based editor · Admin dashboard · Published sites         │
│  Self-service portal · Learning interface · MCP endpoints       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                        │
│  Content management · Document control · Access control         │
│  Learning & Assessment · AI services · MCP Client               │
│  Real-time sync · Publishing engine                             │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Git Repos    │  │ PostgreSQL   │  │ Audit Store          │  │
│  │ (Content)    │  │ (Metadata)   │  │ (Immutable Events)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Presentation Layer

The frontend is a React + TypeScript single-page application:

- **Block-based editor** — TipTap (ProseMirror) with custom extensions for headings, code blocks, tables, callouts, and inline images
- **Admin dashboard** — Organization settings, approval matrices, retention policies, user management
- **Published sites** — Static or server-rendered public documentation sites with themes and custom domains
- **State management** — Zustand stores for authentication, content, and UI state
- **API client** — Axios-based client with namespaced objects (`authApi`, `contentApi`, `publishingApi`, etc.)

### Application Layer

The backend is Python/FastAPI with async support:

- **Routers** — FastAPI APIRouter instances aggregated in `src/api/router.py`, each with a prefix and tag
- **Service layer** — Business logic in `src/modules/<name>/service.py`, decoupled from HTTP concerns
- **Schemas** — Pydantic models in three tiers: Base (shared fields), Create (input), Response (output)
- **Dependencies** — FastAPI dependency injection for `DbSession`, `CurrentUser`, and permission checks

### Data Layer

Three storage systems serve different purposes:

| Store | Purpose | Technology |
|-------|---------|-----------|
| **Git Repositories** | Content versioning, branch-based drafts, merge-based publishing | pygit2 (libgit2) |
| **PostgreSQL** | Metadata, relationships, workflows, permissions, signatures | SQLAlchemy 2.0 async |
| **Audit Store** | Immutable event log with cryptographic hash chain | PostgreSQL (append-only table) |

## Module Boundaries

```
src/
├── api/endpoints/     # HTTP handlers — thin, delegates to services
├── modules/
│   ├── content/       # Org, Workspace, Space, Page CRUD + Git service
│   ├── access/        # Authentication, permissions, sessions, security
│   ├── document_control/  # Lifecycle, numbering, retention, approvals
│   ├── signatures/    # Electronic signatures (21 CFR Part 11)
│   ├── audit/         # Append-only audit trail with hash chain
│   ├── learning/      # Assessments, assignments, acknowledgments
│   ├── publishing/    # Site generation, themes, visitor access
│   ├── mcp/           # MCP server + client, service accounts
│   ├── attachments/   # File upload, storage backends (local/S3)
│   └── portability/   # Import/export in multiple formats
├── db/
│   ├── models/        # SQLAlchemy ORM models with barrel export
│   ├── base.py        # Base class, UUIDMixin, TimestampMixin
│   └── session.py     # Async engine and session factory
└── config.py          # Pydantic BaseSettings with @lru_cache singleton
```

Each module follows the same internal structure:

- `service.py` — Business logic functions (async, accept `db: AsyncSession`)
- `schemas.py` — Pydantic models for validation
- `__init__.py` — Barrel exports

## Key Design Decisions

### Why Git for Content Storage?

Git provides several properties that align with document control requirements:

1. **Immutable history** — Every change is a commit with a cryptographic hash
2. **Branching** — Drafts live on branches, publishing is a merge
3. **Diffing** — Built-in content comparison for review workflows
4. **Air-gap compatible** — Works with bare local repos, no cloud dependency
5. **Portability** — Standard format, can sync with GitHub/GitLab

The platform abstracts Git entirely — users never see branches, commits, or merges. See [Git Abstraction](git-abstraction.md).

### Why PostgreSQL for Metadata?

Content metadata (permissions, workflows, signatures) needs:

- Relational queries (joins across users, organizations, pages)
- Transactional consistency (approval workflows)
- Index-based search (by status, classification, type)
- Schema enforcement (not possible in Git)

### Why a Separate Audit Store?

The audit trail has stricter requirements than regular data:

- **Append-only** — Events are never updated or deleted
- **Hash-chained** — Each event includes a hash of the previous event
- **Tamper-evident** — Any modification breaks the hash chain
- **Exportable** — Auditors can independently verify the chain

While stored in PostgreSQL, the audit table uses application-level constraints to enforce immutability.

### Configuration Approach

All configuration uses Pydantic `BaseSettings` loaded from environment variables:

- Defaults suitable for development (no `.env` file required to start)
- Computed fields for derived values (e.g., `database_url` from components)
- `@lru_cache` ensures a singleton instance across the application
- See [Configuration Reference](../reference/configuration.md) for all fields

## Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend framework | FastAPI | Async support, OpenAPI generation, dependency injection |
| ORM | SQLAlchemy 2.0 | Async engine, mature ecosystem, Alembic migrations |
| Git library | pygit2 | C bindings (libgit2), full Git feature set |
| Editor | TipTap (ProseMirror) | Extensible, collaborative editing support, JSON output |
| State management | Zustand | Lightweight, TypeScript-friendly, no boilerplate |
| Search | Meilisearch | Fast, typo-tolerant, simple API |
| Password hashing | Argon2 | Memory-hard, no 72-byte limit (unlike bcrypt) |
| Tokens | JWT (python-jose) | Stateless auth, refresh token rotation |
