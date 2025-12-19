# Documentation Service Platform

A Diátaxis-based documentation platform with ISO/GxP document control, Git-based version management, and AI-powered features.

## Overview

Documentation Service is a comprehensive platform for creating, managing, and publishing technical documentation. It combines modern editing capabilities with enterprise-grade document control features suitable for regulated industries.

### Key Features

- **Block-based Editor** - Rich WYSIWYG editing with TipTap, supporting code blocks, tables, callouts, and more
- **Diátaxis Framework** - Content organized into Tutorials, How-to Guides, Reference, and Explanation
- **Git-based Version Control** - Full history, branching, and diff capabilities (abstracted for non-technical users)
- **Document Control** - Lifecycle management with approval workflows
- **Electronic Signatures** - 21 CFR Part 11 compliant e-signatures (planned)
- **Full-text Search** - Powered by Meilisearch with typo-tolerance and filtering
- **Hierarchical Organization** - Organization → Workspace → Space → Page structure
- **Classification System** - Multi-level access control based on clearance levels

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async) |
| Frontend | React 18, TypeScript, TipTap Editor |
| Database | PostgreSQL with TimescaleDB |
| Search | Meilisearch |
| Version Control | pygit2 (libgit2) |
| Real-time | Yjs (CRDT) |
| Styling | Tailwind CSS |

## Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **PostgreSQL** 14 or higher
- **Meilisearch** 1.0 or higher
- **libgit2** (for pygit2)
- **Docker** (optional, for running services)

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

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- API docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

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

# Security
SECRET_KEY=your-secret-key-change-in-production

# Services
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=your-meilisearch-key
REDIS_URL=redis://localhost:6379

# Git
GIT_REPOS_PATH=/tmp/docservice/repos
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
├── conftest.py          # Fixtures and configuration
├── unit/
│   ├── test_security.py      # Auth, JWT, password tests
│   ├── test_git_service.py   # Git operations tests
│   ├── test_search_service.py
│   └── test_navigation_service.py
└── integration/
    └── test_auth_api.py      # API endpoint tests

frontend/src/
├── test/
│   ├── setup.ts         # Test configuration
│   └── utils.tsx        # Test utilities
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
│   │   ├── api/              # API routes and endpoints
│   │   │   └── endpoints/
│   │   ├── db/               # Database models and migrations
│   │   │   ├── models/
│   │   │   └── migrations/
│   │   ├── modules/          # Business logic modules
│   │   │   ├── access/       # Authentication & authorization
│   │   │   ├── content/      # Content management, Git, Search
│   │   │   ├── editor/       # Editor-related services
│   │   │   └── ...
│   │   ├── shared/           # Shared utilities
│   │   ├── config.py         # Application configuration
│   │   └── main.py           # FastAPI application
│   ├── tests/
│   ├── alembic.ini
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── editor/
│   │   │   ├── navigation/
│   │   │   ├── search/
│   │   │   └── layout/
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Utilities and API client
│   │   ├── stores/           # Zustand state stores
│   │   ├── types/            # TypeScript types
│   │   └── test/             # Test utilities
│   ├── package.json
│   └── vitest.config.ts
│
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   └── sprints/              # Sprint planning documents
│
├── docker-compose.yml
├── CLAUDE.md                 # AI assistant instructions
└── README.md
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | Register new user |
| `POST /api/v1/auth/login` | Login and get tokens |
| `GET /api/v1/auth/me` | Get current user |
| `GET /api/v1/organizations/` | List organizations |
| `GET /api/v1/workspaces/org/{id}` | List workspaces |
| `GET /api/v1/spaces/workspace/{id}` | List spaces |
| `GET /api/v1/content/pages/{id}` | Get page content |
| `GET /api/v1/search/pages` | Search pages |
| `GET /api/v1/nav/tree/workspace/{id}` | Get navigation tree |

See full API documentation at http://localhost:8000/docs

## Sprint Roadmap

| Sprint | Status | Focus |
|--------|--------|-------|
| 1 | ✅ Complete | Foundation - API, Auth, Git, DB |
| 2 | ✅ Complete | Editor Core - Block editor, Markdown |
| 3 | ✅ Complete | Content Organization - Hierarchy, Search |
| 4 | 📋 Planned | Version Control UI - Diff, History |
| 5 | 📋 Planned | Access Control - Permissions |
| 6 | 📋 Planned | Document Control - Workflows |
| 7 | 📋 Planned | E-Signatures - 21 CFR Part 11 |
| 8 | 📋 Planned | Audit Trail |
| 9 | 📋 Planned | Learning Module |
| 10 | 📋 Planned | AI Features |
| 11 | 📋 Planned | MCP Integration |
| 12 | 📋 Planned | Publishing |

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

- [Specification](./documentation-service-specification-v3.5.md)
- [Sprint Overview](./docs/sprints/sprint-overview.md)
- [Architecture Decisions](./docs/adr/)
- [Diátaxis Framework](https://diataxis.fr/)
# documentation-service
