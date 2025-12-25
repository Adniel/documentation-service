"""User management API endpoints."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DbSession, CurrentUser
from src.modules.access.schemas import UserResponse, UserUpdate
from src.modules.access.service import (
    get_user_by_id,
    update_user,
    list_users,
)

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> list[UserResponse]:
    """List all users (requires authentication)."""
    users = await list_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> UserResponse:
    """Get a specific user by ID."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> UserResponse:
    """Update the current user's profile."""
    updated_user = await update_user(db, current_user, user_in)
    return UserResponse.model_validate(updated_user)
