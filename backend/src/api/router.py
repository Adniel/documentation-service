"""Main API router that aggregates all module routers."""

from fastapi import APIRouter

from src.api.endpoints import (
    auth,
    users,
    organizations,
    workspaces,
    spaces,
    content,
    search,
    navigation,
    change_requests,
    permissions,
    document_control,
    signatures,
    audit,
    learning,
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Organization routes
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["Organizations"]
)

# Workspace routes
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])

# Space routes
api_router.include_router(spaces.router, prefix="/spaces", tags=["Spaces"])

# Content routes
api_router.include_router(content.router, prefix="/content", tags=["Content"])

# Search routes
api_router.include_router(search.router, prefix="/search", tags=["Search"])

# Navigation routes
api_router.include_router(navigation.router, prefix="/nav", tags=["Navigation"])

# Change request (drafts) routes
api_router.include_router(
    change_requests.router, prefix="/content", tags=["Change Requests"]
)

# Permission management routes (Sprint 5)
api_router.include_router(permissions.router)

# Document control routes (Sprint 6)
api_router.include_router(
    document_control.router, prefix="/document-control", tags=["Document Control"]
)

# Electronic signatures routes (Sprint 7)
api_router.include_router(
    signatures.router, tags=["Electronic Signatures"]
)

# Audit trail routes (Sprint 8)
api_router.include_router(
    audit.router, tags=["Audit Trail"]
)

# Learning module routes (Sprint 9)
api_router.include_router(
    learning.router, prefix="/learning", tags=["Learning"]
)
