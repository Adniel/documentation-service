"""Authentication API endpoints.

Sprint 5: Added session management for 21 CFR Part 11 compliance.
Sessions track user activity and enforce inactivity timeouts.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.api.deps import DbSession, CurrentUser, get_session_service
from src.modules.access.schemas import (
    Token,
    UserCreate,
    UserResponse,
    RefreshTokenRequest,
    PasswordChange,
)
from src.modules.access.service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    change_password,
)
from src.modules.access.security import (
    create_token_pair,
    decode_token,
    create_access_token,
    extract_jti,
)
from src.modules.access.session_service import SessionService
from src.modules.audit import AuditService

router = APIRouter()

# For getting token from header in logout endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: DbSession) -> UserResponse:
    """Register a new user."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    user = await create_user(db, user_in)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Login to get access and refresh tokens.

    Creates a session to track user activity and enforce inactivity timeouts.
    Sessions comply with 21 CFR §11.10(d) - limiting system access.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    audit_service = AuditService(db)

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        await audit_service.log_login(
            user_id="",
            user_email=form_data.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="Invalid credentials",
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        # Log failed login attempt
        await audit_service.log_login(
            user_id=str(user.id),
            user_email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="Account disabled",
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Create a session and get JTI for token
    session_service = SessionService(db)
    session, token_jti = await session_service.create_session(
        user_id=str(user.id),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Log successful login
    await audit_service.log_login(
        user_id=str(user.id),
        user_email=user.email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
    )
    await db.commit()

    # Create tokens with session JTI
    access_token, refresh_token = create_token_pair(str(user.id), token_jti)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    token_request: RefreshTokenRequest,
    db: DbSession,
) -> Token:
    """Get a new access token using a refresh token.

    If the old access token had a session, the session is preserved.
    Otherwise, a new session is created.
    """
    payload = decode_token(token_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")

    # Check if we have an existing session from the old access token
    session_service = SessionService(db)
    old_jti = token_request.old_access_token and extract_jti(token_request.old_access_token)

    if old_jti:
        # Refresh the existing session
        refreshed = await session_service.refresh_session(old_jti)
        if refreshed:
            # Use existing session
            access_token, new_refresh_token = create_token_pair(user_id, old_jti)
            await db.commit()
            return Token(access_token=access_token, refresh_token=new_refresh_token)

    # Create new session if no valid old session
    session, token_jti = await session_service.create_session(
        user_id=user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await db.commit()

    access_token, new_refresh_token = create_token_pair(user_id, token_jti)
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> None:
    """Logout and invalidate the current session.

    The session is revoked, making all tokens using that session's JTI invalid.
    """
    if not token:
        return  # No token provided, nothing to invalidate

    jti = extract_jti(token)
    if jti:
        session_service = SessionService(db)
        session = await session_service.get_session_by_jti(jti)
        await session_service.revoke_session(jti, reason="User logout")

        # Log logout
        if session:
            audit_service = AuditService(db)
            await audit_service.log_logout(
                user_id=session.user_id,
                user_email="",  # Would need to fetch user for email
                ip_address=request.client.host if request.client else None,
                session_jti=jti,
            )
        await db.commit()


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all_sessions(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    """Logout from all sessions.

    Revokes all active sessions for the current user.
    Useful when user suspects their account has been compromised.
    """
    session_service = SessionService(db)
    await session_service.revoke_all_user_sessions(
        user_id=str(current_user.id),
        reason="User logged out from all sessions",
        exclude_jti=None,  # Revoke all, including current
    )

    # Log logout from all sessions
    audit_service = AuditService(db)
    await audit_service.log_logout(
        user_id=str(current_user.id),
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None,
        session_jti="all",
    )
    await db.commit()


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    password_data: PasswordChange,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    """Change the current user's password.

    After password change, all other sessions are revoked for security.
    """
    success = await change_password(
        db, current_user, password_data.current_password, password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Revoke all other sessions after password change
    current_jti = extract_jti(token) if token else None
    session_service = SessionService(db)
    await session_service.revoke_all_user_sessions(
        user_id=str(current_user.id),
        reason="Password changed - sessions revoked for security",
        exclude_jti=current_jti,  # Keep current session active
    )

    # Log password change
    audit_service = AuditService(db)
    await audit_service.log_password_change(
        user_id=str(current_user.id),
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()
