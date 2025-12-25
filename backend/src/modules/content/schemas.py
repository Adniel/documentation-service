"""Pydantic schemas for content management."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DiataxisType(str, Enum):
    """Diátaxis documentation types."""

    TUTORIAL = "tutorial"
    HOW_TO = "how_to"
    REFERENCE = "reference"
    EXPLANATION = "explanation"
    MIXED = "mixed"


class PageStatus(str, Enum):
    """Document lifecycle status."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    EFFECTIVE = "effective"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class ClassificationLevel(str, Enum):
    """Document classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# Organization schemas
class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None


class OrganizationCreate(OrganizationBase):
    """Create organization schema."""

    pass


class OrganizationUpdate(BaseModel):
    """Update organization schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    logo_url: str | None = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema."""

    id: str
    is_active: bool
    logo_url: str | None
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workspace schemas
class WorkspaceBase(BaseModel):
    """Base workspace schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None


class WorkspaceCreate(WorkspaceBase):
    """Create workspace schema."""

    organization_id: str
    is_public: bool = False


class WorkspaceUpdate(BaseModel):
    """Update workspace schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class WorkspaceResponse(WorkspaceBase):
    """Workspace response schema."""

    id: str
    organization_id: str
    is_active: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Space schemas
class SpaceBase(BaseModel):
    """Base space schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    diataxis_type: DiataxisType = DiataxisType.MIXED


class SpaceCreate(SpaceBase):
    """Create space schema."""

    workspace_id: str
    parent_id: str | None = None
    classification: ClassificationLevel = ClassificationLevel.PUBLIC


class SpaceUpdate(BaseModel):
    """Update space schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    diataxis_type: DiataxisType | None = None
    classification: ClassificationLevel | None = None
    sort_order: int | None = None


class SpaceResponse(SpaceBase):
    """Space response schema."""

    id: str
    workspace_id: str
    parent_id: str | None
    classification: int  # Spaces use integer classification (0-3)
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Page schemas
class PageBase(BaseModel):
    """Base page schema."""

    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-z0-9-]+$")


class PageCreate(PageBase):
    """Create page schema."""

    space_id: str
    parent_id: str | None = None
    content: dict | None = None
    summary: str | None = None
    classification: ClassificationLevel = ClassificationLevel.PUBLIC


class PageUpdate(BaseModel):
    """Update page schema."""

    title: str | None = Field(None, min_length=1, max_length=500)
    content: dict | None = None
    summary: str | None = None
    classification: ClassificationLevel | None = None
    sort_order: int | None = None


class PageResponse(PageBase):
    """Page response schema."""

    id: str
    space_id: str
    author_id: str
    parent_id: str | None
    document_number: str | None
    version: str
    status: str
    classification: str
    content: dict | None
    summary: str | None
    git_path: str | None
    git_commit_sha: str | None
    is_active: bool
    is_template: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageSummary(BaseModel):
    """Brief page info for listings."""

    id: str
    title: str
    slug: str
    status: str
    version: str
    updated_at: datetime

    class Config:
        from_attributes = True
