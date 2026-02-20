# Documentation Service Platform

A Diataxis-based documentation platform with ISO/GxP document control, Git-based version management, and AI-powered features.

## Overview

Documentation Service is a comprehensive platform for creating, managing, and publishing technical documentation. It combines modern editing capabilities with enterprise-grade document control features suitable for regulated industries.

### Key Features

- **Block-based Editor** - Rich WYSIWYG editing with TipTap, supporting code blocks, tables, callouts, and more
- **Diataxis Framework** - Content organized into Tutorials, How-to Guides, Reference, and Explanation
- **Git-based Version Control** - Full history, branching, and diff capabilities (abstracted for non-technical users)
- **Document Control** - Lifecycle management with approval workflows (ISO 9001, ISO 13485)
- **Electronic Signatures** - 21 CFR Part 11 compliant e-signatures with re-authentication and content hashing
- **Immutable Audit Trail** - Cryptographic hash-chain audit log with compliance export
- **Full-text Search** - Powered by Meilisearch with typo-tolerance and filtering
- **Hierarchical Organization** - Organization > Workspace > Space > Page structure
- **Classification System** - Multi-level access control based on clearance levels
- **Learning & Assessment** - Document acknowledgment, quizzes, and training tracking
- **Publishing** - Published documentation sites with themes, custom domains, and SEO
- **MCP Integration** - Model Context Protocol server for AI agent access to documentation
- **Admin UI** - Organization-scoped management for users, settings, and audit
- **AI Services** - Provider-agnostic AI for question generation, writing assistance, and document masking
- **Reader UI & Accessibility** - WCAG 2.1 AA reading experience with context menus, reading aids, and PDF/DOCX/MD export
- **Attachments & Media** - File attachments with local or S3-compatible storage
- **Metadata Portability** - Import/export with format adapters
- **Compliance Documentation** - Built-in SOPs, system validation docs, risk assessments, and role-based training

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async) |
| Frontend | React 18, TypeScript, TipTap Editor |
| Database | PostgreSQL 15+ |
| Search | Meilisearch |
| Cache | Redis (optional) |
| Version Control | pygit2 (libgit2) |
| Real-time | Yjs (CRDT) |
| Styling | Tailwind CSS |
| State Management | Zustand, TanStack Query |
| Logging | structlog (JSON/console) |
| Testing | pytest, Vitest, Playwright |

## Prerequisites

- **Python** 3.12 or higher
- **Node.js** 20 LTS or higher
- **PostgreSQL** 15 or higher
- **Meilisearch** 1.0 or higher
- **libgit2** (for pygit2)
- **Docker** (optional, for running services)
- **Redis** (optional, for response caching)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd documentation-service
```

### 2. Start Infrastructure Services

Using Docker Compose:

```bash
docker-compose up -d postgres meilisearch redis
```

Or install services manually:
- PostgreSQL on port 5432
- Meilisearch on port 7700
- Redis on port 6379 (optional, for caching)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed sample data (optional)
python -m src.cli seed --fixture demo

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- API docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Development

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn src.main:app --reload

# Run linting
ruff check src/

# Run type checking
mypy src/

# Format code
ruff format src/
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

### Seed Data

The CLI seed tool populates the database with sample content for development:

```bash
cd backend

# Full demo data (3 workspaces, 27 pages, 4 assessments with 20 questions)
python -m src.cli seed --fixture demo

# Minimal data (1 workspace, no pages)
python -m src.cli seed --fixture minimal

# Force overwrite existing data
python -m src.cli seed --fixture demo --force
```

Or via Makefile:

```bash
make seed          # demo fixture
make seed-minimal  # minimal fixture
```

### Environment Variables

**Backend** (`backend/.env`):

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_USER=docservice
POSTGRES_PASSWORD=docservice_dev
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docservice

# Database pool tuning
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Security
SECRET_KEY=your-secret-key-change-in-production

# Services
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your-meilisearch-key
REDIS_URL=redis://localhost:6379

# Git
GIT_REPOS_PATH=/tmp/docservice/repos

# AI (optional)
AI_PROVIDER=openai          # openai, anthropic, openrouter, ollama
AI_API_KEY=your-api-key
AI_MODEL=gpt-4o-mini
```

**Frontend** (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Frontend Tests

```bash
cd frontend

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- src/lib/diataxis.test.ts
```

### Test Structure

```
backend/tests/
├── conftest.py
├── unit/                              # 33 unit test files
│   ├── test_security.py
│   ├── test_git_service.py
│   ├── test_search_service.py
│   ├── test_navigation_service.py
│   ├── test_permission_model.py
│   ├── test_session_model.py
│   ├── test_change_request_service.py
│   ├── test_diff_service.py
│   ├── test_revision_service.py
│   ├── test_access_service.py
│   ├── test_classification_service.py
│   ├── test_lifecycle_service.py
│   ├── test_numbering_service.py
│   ├── test_metadata_service.py
│   ├── test_retention_service.py
│   ├── test_approval_service.py
│   ├── test_credential_service.py
│   ├── test_grading_service.py
│   ├── test_learning_service.py
│   ├── test_tiptap_to_markdown.py
│   ├── test_sync_service.py
│   ├── test_webhook_service.py
│   ├── test_publishing_service.py
│   ├── test_rate_limiter.py
│   ├── test_mcp_service.py
│   ├── test_content_transformer.py
│   ├── test_storage_backends.py
│   ├── test_attachment_service.py
│   ├── test_diataxis_revision.py
│   ├── test_portability_metadata.py
│   ├── test_exporter.py
│   ├── test_importer.py
│   └── test_seed.py
└── integration/                       # 16 integration test files
    ├── test_auth_api.py
    ├── test_organizations_api.py
    ├── test_workspaces_api.py
    ├── test_spaces_api.py
    ├── test_permissions_api.py
    ├── test_change_requests_api.py
    ├── test_conflict_detection.py
    ├── test_version_control_workflow.py
    ├── test_document_control_api.py
    ├── test_learning_api.py
    ├── test_publishing_api.py
    ├── test_mcp_api.py
    ├── test_visitor_api.py
    ├── test_attachment_api.py
    ├── test_diataxis_api.py
    └── test_portability_api.py

frontend/src/
├── test/
│   ├── setup.ts
│   └── utils.tsx
├── lib/
│   ├── diataxis.test.ts
│   └── markdown.test.ts
└── components/
    ├── navigation/Breadcrumbs.test.tsx
    └── search/SearchBar.test.tsx
```

## Project Structure

```
documentation-service/
├── backend/
│   ├── src/
│   │   ├── api/                    # API routes and endpoints
│   │   │   ├── router.py           # Route aggregation
│   │   │   ├── deps.py             # Dependency injection
│   │   │   ├── public_site.py      # Public published site routes
│   │   │   └── endpoints/
│   │   │       ├── auth.py         # Authentication & sessions
│   │   │       ├── users.py        # User management
│   │   │       ├── organizations.py
│   │   │       ├── workspaces.py
│   │   │       ├── spaces.py
│   │   │       ├── content.py      # Page CRUD
│   │   │       ├── search.py       # Full-text search
│   │   │       ├── navigation.py   # Nav trees & breadcrumbs
│   │   │       ├── change_requests.py  # Drafts, reviews, diffs
│   │   │       ├── permissions.py  # ACL management
│   │   │       ├── document_control.py # Lifecycle, approvals
│   │   │       ├── signatures.py   # E-signatures (21 CFR Part 11)
│   │   │       ├── audit.py        # Audit trail & export
│   │   │       ├── learning.py     # Assessments & quizzes
│   │   │       ├── git.py          # Remote config & sync
│   │   │       ├── webhooks.py     # Git provider webhooks
│   │   │       ├── publishing.py   # Site & theme management
│   │   │       ├── service_accounts.py # MCP service accounts
│   │   │       ├── mcp.py          # MCP JSON-RPC endpoint
│   │   │       ├── visitors.py     # External visitor access
│   │   │       ├── attachments.py  # File uploads & media
│   │   │       ├── portability.py  # Import/export metadata
│   │   │       ├── export.py       # PDF, DOCX, Markdown export
│   │   │       └── ai.py          # AI services (questions, writing, masking)
│   │   ├── db/
│   │   │   ├── base.py             # Base, UUIDMixin, TimestampMixin
│   │   │   ├── session.py          # Database connection
│   │   │   └── models/             # SQLAlchemy models
│   │   ├── modules/                # Business logic
│   │   │   ├── access/             # Auth, permissions, classification
│   │   │   ├── content/            # Content management & search
│   │   │   ├── editor/             # Editor services
│   │   │   ├── git/                # Git abstraction layer
│   │   │   ├── document_control/   # Lifecycle, numbering, metadata
│   │   │   ├── audit/              # Immutable hash-chain audit
│   │   │   ├── learning/           # Assessments & training
│   │   │   ├── ai/                 # AI services (provider-agnostic)
│   │   │   ├── mcp/                # MCP server & tools
│   │   │   ├── publishing/         # Site generation & themes
│   │   │   ├── attachments/        # File storage backends
│   │   │   ├── export/             # PDF/DOCX/MD generation
│   │   │   └── portability/        # Import/export adapters
│   │   ├── cli/                    # CLI tools
│   │   │   ├── seed.py             # Database seeding
│   │   │   └── fixtures.py         # Seed data (demo, minimal)
│   │   ├── shared/                 # Shared utilities
│   │   ├── config.py               # Application configuration
│   │   ├── main.py                 # FastAPI application
│   │   ├── cache.py                # Redis cache with @cached decorator
│   │   ├── logging.py              # structlog configuration
│   │   └── middleware.py           # Request context (X-Request-ID)
│   ├── tests/
│   │   ├── unit/                   # 33 unit test files
│   │   └── integration/            # 16 integration test files
│   ├── alembic/
│   │   └── versions/               # 14 database migrations
│   ├── alembic.ini
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── editor/             # TipTap block editor + extensions
│   │   │   ├── navigation/         # Sidebar, breadcrumbs
│   │   │   ├── search/             # Search bar & results
│   │   │   ├── layout/             # App shell & navigation
│   │   │   ├── version-control/    # Change requests, diff, merge
│   │   │   ├── signatures/         # E-signature dialogs
│   │   │   ├── document-control/   # Lifecycle, approvals, retention
│   │   │   ├── audit/              # Audit trail viewer
│   │   │   ├── learning/           # Assessment builder, quizzes
│   │   │   ├── git/                # Remote config, sync history
│   │   │   ├── publishing/         # Site config, themes, publish
│   │   │   ├── admin/              # User, org, audit management
│   │   │   ├── mcp/                # Service account management
│   │   │   ├── ai/                 # AI panels (questions, writing, masking)
│   │   │   ├── help/               # Guided tour, tooltips, FAQ
│   │   │   ├── accessibility/      # WCAG 2.1 AA components
│   │   │   ├── reading-aids/       # Font size, line spacing, focus mode
│   │   │   ├── context-menu/       # Right-click context menus
│   │   │   └── portability/        # Import/export UI
│   │   ├── pages/                  # Page components
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── EditorPage.tsx
│   │   │   ├── ReadingPage.tsx     # WCAG 2.1 AA reader
│   │   │   ├── ContentBrowserPage.tsx
│   │   │   ├── SearchResultsPage.tsx
│   │   │   ├── AdminPage.tsx
│   │   │   └── ...
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utilities and API client
│   │   ├── stores/                 # Zustand state stores
│   │   ├── types/                  # TypeScript types
│   │   └── test/                   # Test utilities
│   ├── package.json
│   └── vitest.config.ts
│
├── docs/                           # Project documentation (Diataxis)
│   ├── tutorials/                  # Getting started guides
│   ├── how-to/                     # Task-oriented guides
│   ├── reference/                  # API reference, configuration
│   │   └── api/                    # Per-module API docs
│   ├── explanation/                # Architecture, design decisions
│   ├── architecture/               # ADRs and module boundaries
│   └── sprints/                    # Sprint planning documents
│
├── docker-compose.yml
├── Makefile
├── CLAUDE.md
└── README.md
```

## API Overview

All API endpoints are prefixed with `/api/v1`.

| Area | Endpoint | Description |
|------|----------|-------------|
| **Health** | `GET /health` | System health (database, redis, meilisearch) |
| **Auth** | `POST /auth/register` | Register new user |
| | `POST /auth/login` | Login and get tokens |
| | `GET /auth/me` | Get current user |
| **Organizations** | `GET /organizations/` | List organizations |
| **Workspaces** | `GET /workspaces/org/{id}` | List workspaces |
| **Spaces** | `GET /spaces/workspace/{id}` | List spaces |
| **Content** | `GET /content/pages/{id}` | Get page content |
| | `POST /content/pages` | Create page |
| **Search** | `GET /search/pages` | Search pages |
| **Navigation** | `GET /nav/tree/workspace/{id}` | Get navigation tree |
| **Change Requests** | `POST /content/change-requests` | Create draft |
| | `GET /content/change-requests/{id}/diff` | View diff |
| **Permissions** | `GET /permissions/{type}/{id}` | Get effective permissions |
| **Document Control** | `POST /document-control/lifecycle` | Manage lifecycle |
| | `POST /document-control/approvals` | Approval workflows |
| **Signatures** | `POST /signatures/initiate` | Initiate e-signature |
| | `POST /signatures/complete` | Complete e-signature |
| **Audit** | `GET /audit/trail` | Query audit events |
| | `GET /audit/export` | Export for compliance |
| **Learning** | `GET /learning/assessments` | List assessments |
| | `POST /learning/quiz-attempts` | Submit quiz attempt |
| **Git** | `POST /git/remote` | Configure remote |
| | `POST /git/sync` | Trigger sync |
| **Publishing** | `POST /publishing/sites` | Create published site |
| | `POST /publishing/sites/{id}/publish` | Publish site |
| **MCP** | `POST /mcp/jsonrpc` | MCP JSON-RPC endpoint |
| **Service Accounts** | `POST /service-accounts/` | Create service account |
| **Visitors** | `POST /visitors/invite` | Invite external visitor |
| **Attachments** | `POST /attachments/upload` | Upload file attachment |
| **Portability** | `POST /portability/export` | Export metadata |
| | `POST /portability/import` | Import metadata |
| **Export** | `GET /export/pages/{id}/pdf` | Export page as PDF |
| | `GET /export/pages/{id}/docx` | Export page as DOCX |
| | `GET /export/pages/{id}/markdown` | Export page as Markdown |
| **AI** | `POST /ai/generate-questions` | Generate assessment questions |
| | `POST /ai/writing-assist` | AI writing assistance |
| | `POST /ai/mask` | Detect and mask sensitive content |

Published sites are served at `/s/{site_slug}` with navigation, search, sitemap, and robots.txt.

See full API documentation at http://localhost:8000/docs

## Database Migrations

| # | Migration | Sprint |
|---|-----------|--------|
| 001 | Initial schema (users, orgs, workspaces, spaces, pages) | 1-3 |
| 002 | Change requests & version control | 4 |
| 003 | Sessions and permissions | 5 |
| 004 | Document control (lifecycle, numbering, metadata) | 6 |
| 005 | Electronic signatures | 7 |
| 006 | Audit immutability (hash chain) | 8 |
| 007 | Learning module (assessments, questions) | 9 |
| 008 | Git remote support | 13 |
| 009 | Publishing (sites, themes) | A |
| 010 | Admin UI completion | B |
| 011 | MCP integration (service accounts) | C |
| 012 | Integrated access control (visitors, site access) | D |
| 013 | Attachments & media | F |
| 014 | Diataxis revision (per-page content types) | E |

## Sprint Roadmap

| Sprint | Status | Focus |
|--------|--------|-------|
| 1 | ✅ Complete | Foundation - API, Auth, Git, DB |
| 2 | ✅ Complete | Editor Core - Block editor, Markdown |
| 3 | ✅ Complete | Content Organization - Hierarchy, Search |
| 4 | ✅ Complete | Version Control UI - Diff, History, Merge |
| 5 | ✅ Complete | Access Control - Permissions, Classification |
| 6 | ✅ Complete | Document Control - Lifecycle, Approvals |
| 7 | ✅ Complete | Electronic Signatures - 21 CFR Part 11 |
| 8 | ✅ Complete | Audit Trail - Hash chain, Export |
| 9 | ✅ Complete | Learning Module - Assessments, Training |
| 9.5 | ✅ Complete | Admin UI - Assessment builder, Approval config |
| 13 | ✅ Complete | Git Remote - Sync, Webhooks |
| A | ✅ Complete | Publishing - Sites, Themes, Static generation |
| B | ✅ Complete | Admin UI Completion - Users, Org settings, Audit |
| C | ✅ Complete | MCP Integration - AI agent access |
| D | ✅ Complete | Integrated Access Control - Visitor management |
| E | ✅ Complete | Diataxis Revision - Per-page content types |
| F | ✅ Complete | Attachments & Media - Storage backends, editor integration |
| G | ✅ Complete | Metadata Portability - Export/import with format adapters |
| H | ✅ Complete | System Documentation - 25 docs, CLI seed, help components |
| I | ✅ Complete | Reader UI & Accessibility - WCAG 2.1 AA, PDF/DOCX/MD export |
| J | ✅ Complete | Performance & Operations - structlog, health checks, Redis cache |
| K | ✅ Complete | AI Features - Question generation, writing assistant, masking |
| L | ✅ Complete | Compliance Docs & Training - 15 compliance pages, 4 assessments |

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass
4. Submit a pull request

### Code Quality

Before submitting:

```bash
# Backend
cd backend
ruff check src/
mypy src/
pytest

# Frontend
cd frontend
npm run type-check
npm run lint
npm test
```

## License

MIT License - see LICENSE file for details.

## Documentation

- [Specification](./documentation-service-specification.md)
- [Sprint Overview](./docs/sprints/sprint-overview.md)
- [Architecture Decisions](./docs/architecture/)
- [API Reference](./docs/reference/api/)
- [Operations Runbook](./docs/reference/operations-runbook.md)
- [Configuration Reference](./docs/reference/configuration.md)
- [Compliance Matrix](./docs/reference/compliance-matrix.md)
- [Diataxis Framework](https://diataxis.fr/)
