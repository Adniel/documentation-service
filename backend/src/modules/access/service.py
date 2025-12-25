"""User and authentication service layer."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import User
from src.modules.access.schemas import UserCreate, UserUpdate
from src.modules.access.security import hash_password, verify_password


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_with_organizations(db: AsyncSession, user_id: str) -> User | None:
    """Get a user with their organizations loaded."""
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.organizations))
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        title=user_in.title,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    """Update an existing user."""
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        return None

    if not verify_password(password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        # Lock account after 5 failed attempts for 15 minutes
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        await db.commit()
        return None

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    return user


async def change_password(
    db: AsyncSession, user: User, current_password: str, new_password: str
) -> bool:
    """Change a user's password. Returns True if successful."""
    if not verify_password(current_password, user.hashed_password):
        return False

    user.hashed_password = hash_password(new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, active_only: bool = True
) -> list[User]:
    """List users with pagination."""
    query = select(User)
    if active_only:
        query = query.where(User.is_active == True)  # noqa: E712
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# Import timedelta here to avoid issues with the module
from datetime import timedelta  # noqa: E402
