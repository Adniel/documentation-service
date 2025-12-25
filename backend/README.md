# Documentation Service - Backend

FastAPI backend for the Documentation Service Platform.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

## Project Structure

```
src/
├── api/              # API routes
│   └── endpoints/    # Endpoint modules
├── db/               # Database
│   ├── models/       # SQLAlchemy models
│   └── migrations/   # Alembic migrations
├── modules/          # Business logic
│   ├── access/       # Auth & permissions
│   ├── content/      # Content management
│   └── ...
├── shared/           # Shared utilities
├── config.py         # Configuration
└── main.py           # Application entry
```

See the main [README](../README.md) for full documentation.
