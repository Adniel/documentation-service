"""Pydantic schemas for authentication, users, and permissions."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# -------------------------------------------------------------------------
# Enums for API
# -------------------------------------------------------------------------

class RoleEnum(str, Enum):
    """Role levels for API."""
    VIEWER = "viewer"
    REVIEWER = "reviewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


class ResourceTypeEnum(str, Enum):
    """Resource types for permissions."""
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    SPACE = "space"
    PAGE = "page"


class ClassificationLevelEnum(str, Enum):
    """Classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ActionEnum(str, Enum):
    """Actions for permission checks."""
    READ = "read"
    COMMENT = "comment"
    EDIT = "edit"
    DELETE_OWN = "delete_own"
    DELETE_ANY = "delete_any"
    APPROVE = "approve"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_SETTINGS = "manage_settings"
    DELETE_RESOURCE = "delete_resource"


# -------------------------------------------------------------------------
# Authentication schemas
# -------------------------------------------------------------------------
class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # user_id
    exp: datetime
    type: str  # "access" or "refresh"


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str
    old_access_token: Optional[str] = Field(
        None,
        description="Optional old access token to preserve session"
    )


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    title: str | None = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    title: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    """User response schema."""

    id: str
    is_active: bool
    email_verified: bool
    clearance_level: int
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithOrgsResponse(UserResponse):
    """User response with organizations."""

    organizations: list["OrganizationSummary"]


class PasswordChange(BaseModel):
    """Password change request."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# Organization summary for nested responses
class OrganizationSummary(BaseModel):
    """Brief organization info."""

    id: str
    name: str
    slug: str

    class Config:
        from_attributes = True


UserWithOrgsResponse.model_rebuild()


# -------------------------------------------------------------------------
# Permission Schemas
# -------------------------------------------------------------------------

class PermissionCreate(BaseModel):
    """Create a new permission."""

    user_id: str = Field(..., description="User to grant permission to")
    resource_type: ResourceTypeEnum = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="UUID of the resource")
    role: RoleEnum = Field(..., description="Role to grant")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for granting")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")


class PermissionUpdate(BaseModel):
    """Update an existing permission."""

    role: Optional[RoleEnum] = Field(None, description="New role")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for update")
    expires_at: Optional[datetime] = Field(None, description="New expiration time")
    is_active: Optional[bool] = Field(None, description="Active status")


class PermissionResponse(BaseModel):
    """Permission response."""

    id: str
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    resource_type: str
    resource_id: str
    role: str
    granted_by_id: str
    granted_by_name: Optional[str] = None
    granted_at: datetime
    reason: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """Paginated permission list response."""

    items: list[PermissionResponse]
    total: int
    limit: int
    offset: int


class EffectivePermissionSource(BaseModel):
    """Source of an effective permission."""

    resource_type: str
    resource_id: str
    role: str


class EffectivePermission(BaseModel):
    """Effective permission after inheritance resolution."""

    user_id: str
    user_name: Optional[str]
    user_email: Optional[str]
    effective_role: str
    clearance_level: int
    has_access: bool
    sources: list[EffectivePermissionSource]


class EffectivePermissionsResponse(BaseModel):
    """Response for effective permissions query."""

    resource_type: str
    resource_id: str
    classification: str
    effective_permissions: list[EffectivePermission]


class AccessCheckRequest(BaseModel):
    """Request to check access."""

    user_id: str = Field(..., description="User to check")
    resource_type: ResourceTypeEnum = Field(..., description="Resource type")
    resource_id: str = Field(..., description="Resource ID")
    action: ActionEnum = Field(..., description="Action to check")


class AccessCheckResponse(BaseModel):
    """Response for access check."""

    allowed: bool
    reason: str
    effective_role: Optional[str] = None
    clearance_sufficient: bool = True
    required_clearance: int = 0
    user_clearance: int = 0


class ClearanceUpdateRequest(BaseModel):
    """Request to update user clearance level."""

    clearance_level: int = Field(..., ge=0, le=3, description="New clearance level (0-3)")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for change")


class ClearanceUpdateResponse(BaseModel):
    """Response for clearance update."""

    user_id: str
    previous_clearance: int
    new_clearance: int
    updated_by: str
    reason: str
    updated_at: datetime


# -------------------------------------------------------------------------
# Role Capabilities
# -------------------------------------------------------------------------

class RoleCapability(BaseModel):
    """Capabilities for a role."""

    can_read: bool
    can_comment: bool
    can_edit: bool
    can_delete_own: bool
    can_delete_any: bool
    can_approve: bool
    can_manage_members: bool
    can_manage_settings: bool
    can_delete_resource: bool


class RoleCapabilitiesResponse(BaseModel):
    """Response with all role capabilities."""

    roles: dict[str, RoleCapability]
