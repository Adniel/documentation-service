"""Theme service for managing documentation site themes.

Sprint A: Publishing
"""

from typing import Any

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Theme
from src.modules.publishing.schemas import ThemeCreate, ThemeUpdate


class ThemeService:
    """Service for theme management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_themes(
        self,
        organization_id: str | None = None,
        include_system: bool = True,
    ) -> list[Theme]:
        """List available themes.

        Args:
            organization_id: Filter to organization-specific themes
            include_system: Include system themes (organization_id=None)

        Returns:
            List of themes
        """
        conditions = []

        if organization_id:
            if include_system:
                conditions.append(
                    or_(
                        Theme.organization_id == organization_id,
                        Theme.organization_id.is_(None),
                    )
                )
            else:
                conditions.append(Theme.organization_id == organization_id)
        elif include_system:
            conditions.append(Theme.organization_id.is_(None))

        query = select(Theme)
        if conditions:
            query = query.where(*conditions)
        query = query.order_by(Theme.is_default.desc(), Theme.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_theme(self, theme_id: str) -> Theme | None:
        """Get a theme by ID.

        Args:
            theme_id: Theme ID

        Returns:
            Theme if found, None otherwise
        """
        result = await self.db.execute(select(Theme).where(Theme.id == theme_id))
        return result.scalar_one_or_none()

    async def get_default_theme(self, organization_id: str | None = None) -> Theme | None:
        """Get the default theme.

        Args:
            organization_id: Check for org-specific default first

        Returns:
            Default theme if found
        """
        # First check for org-specific default
        if organization_id:
            result = await self.db.execute(
                select(Theme).where(
                    Theme.organization_id == organization_id,
                    Theme.is_default.is_(True),
                )
            )
            theme = result.scalar_one_or_none()
            if theme:
                return theme

        # Fall back to system default
        result = await self.db.execute(
            select(Theme).where(
                Theme.organization_id.is_(None),
                Theme.is_default.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create_theme(
        self,
        organization_id: str,
        data: ThemeCreate,
        created_by_id: str,
    ) -> Theme:
        """Create a new theme.

        Args:
            organization_id: Organization ID
            data: Theme data
            created_by_id: User creating the theme

        Returns:
            Created theme
        """
        theme = Theme(
            organization_id=organization_id,
            created_by_id=created_by_id,
            name=data.name,
            description=data.description,
            is_default=False,  # New themes are not default by default
            primary_color=data.primary_color,
            secondary_color=data.secondary_color,
            accent_color=data.accent_color,
            background_color=data.background_color,
            surface_color=data.surface_color,
            text_color=data.text_color,
            text_muted_color=data.text_muted_color,
            heading_font=data.heading_font,
            body_font=data.body_font,
            code_font=data.code_font,
            base_font_size=data.base_font_size,
            sidebar_position=data.sidebar_position.value,
            content_width=data.content_width.value,
            toc_enabled=data.toc_enabled,
            header_height=data.header_height,
            logo_url=data.logo_url,
            favicon_url=data.favicon_url,
            custom_css=data.custom_css,
            custom_head_html=data.custom_head_html,
        )

        self.db.add(theme)
        await self.db.commit()
        await self.db.refresh(theme)

        return theme

    async def update_theme(
        self,
        theme_id: str,
        data: ThemeUpdate,
    ) -> Theme | None:
        """Update a theme.

        Args:
            theme_id: Theme ID
            data: Update data

        Returns:
            Updated theme if found
        """
        theme = await self.get_theme(theme_id)
        if not theme:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(theme, key):
                # Handle enum values
                if key in ("sidebar_position", "content_width") and value is not None:
                    value = value.value if hasattr(value, "value") else value
                setattr(theme, key, value)

        await self.db.commit()
        await self.db.refresh(theme)

        return theme

    async def delete_theme(self, theme_id: str) -> bool:
        """Delete a theme.

        Args:
            theme_id: Theme ID

        Returns:
            True if deleted, False if not found
        """
        theme = await self.get_theme(theme_id)
        if not theme:
            return False

        # Don't allow deleting system themes
        if theme.organization_id is None:
            raise ValueError("Cannot delete system themes")

        await self.db.delete(theme)
        await self.db.commit()

        return True

    async def set_default_theme(
        self,
        theme_id: str,
        organization_id: str,
    ) -> Theme | None:
        """Set a theme as the default for an organization.

        Args:
            theme_id: Theme ID to set as default
            organization_id: Organization ID

        Returns:
            Updated theme if found
        """
        theme = await self.get_theme(theme_id)
        if not theme:
            return None

        # Verify theme belongs to organization or is a system theme
        if theme.organization_id and theme.organization_id != organization_id:
            raise ValueError("Theme does not belong to this organization")

        # Clear existing default for this organization
        result = await self.db.execute(
            select(Theme).where(
                Theme.organization_id == organization_id,
                Theme.is_default.is_(True),
            )
        )
        for existing_default in result.scalars().all():
            existing_default.is_default = False

        # Set new default
        theme.is_default = True
        await self.db.commit()
        await self.db.refresh(theme)

        return theme

    async def duplicate_theme(
        self,
        theme_id: str,
        organization_id: str,
        new_name: str,
        created_by_id: str,
    ) -> Theme | None:
        """Duplicate a theme.

        Args:
            theme_id: Theme ID to duplicate
            organization_id: Organization for the new theme
            new_name: Name for the new theme
            created_by_id: User creating the copy

        Returns:
            New theme if source found
        """
        source = await self.get_theme(theme_id)
        if not source:
            return None

        new_theme = Theme(
            organization_id=organization_id,
            created_by_id=created_by_id,
            name=new_name,
            description=f"Copy of {source.name}",
            is_default=False,
            primary_color=source.primary_color,
            secondary_color=source.secondary_color,
            accent_color=source.accent_color,
            background_color=source.background_color,
            surface_color=source.surface_color,
            text_color=source.text_color,
            text_muted_color=source.text_muted_color,
            heading_font=source.heading_font,
            body_font=source.body_font,
            code_font=source.code_font,
            base_font_size=source.base_font_size,
            sidebar_position=source.sidebar_position,
            content_width=source.content_width,
            toc_enabled=source.toc_enabled,
            header_height=source.header_height,
            logo_url=source.logo_url,
            favicon_url=source.favicon_url,
            custom_css=source.custom_css,
            custom_head_html=source.custom_head_html,
        )

        self.db.add(new_theme)
        await self.db.commit()
        await self.db.refresh(new_theme)

        return new_theme
