"""Publishing service for documentation sites.

Sprint A: Publishing
"""

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import (
    PublishedSite,
    SiteStatus,
    Space,
    Page,
    PageStatus,
    Theme,
)
from src.modules.publishing.schemas import (
    SiteCreate,
    SiteUpdate,
    PublishResult,
    RenderedPage,
    NavigationItem,
    SiteNavigation,
)
from src.modules.publishing.renderer import PageRenderer
from src.modules.audit.audit_service import AuditService


class PublishingError(Exception):
    """Publishing-related error."""

    pass


class PublishingService:
    """Service for managing published documentation sites."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def list_sites(
        self,
        organization_id: str | None = None,
        status: SiteStatus | None = None,
    ) -> list[PublishedSite]:
        """List published sites.

        Args:
            organization_id: Filter by organization
            status: Filter by status

        Returns:
            List of sites
        """
        query = select(PublishedSite).options(
            selectinload(PublishedSite.space),
            selectinload(PublishedSite.theme),
        )

        if organization_id:
            query = query.where(PublishedSite.organization_id == organization_id)
        if status:
            query = query.where(PublishedSite.status == status.value)

        query = query.order_by(PublishedSite.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_site(self, site_id: str) -> PublishedSite | None:
        """Get a site by ID.

        Args:
            site_id: Site ID

        Returns:
            Site if found
        """
        result = await self.db.execute(
            select(PublishedSite)
            .options(
                selectinload(PublishedSite.space),
                selectinload(PublishedSite.theme),
            )
            .where(PublishedSite.id == site_id)
        )
        return result.scalar_one_or_none()

    async def get_site_by_slug(self, slug: str) -> PublishedSite | None:
        """Get a site by slug.

        Args:
            slug: Site slug

        Returns:
            Site if found
        """
        result = await self.db.execute(
            select(PublishedSite)
            .options(
                selectinload(PublishedSite.space),
                selectinload(PublishedSite.theme),
            )
            .where(PublishedSite.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_site_by_domain(self, domain: str) -> PublishedSite | None:
        """Get a site by custom domain.

        Args:
            domain: Custom domain

        Returns:
            Site if found and domain is verified
        """
        result = await self.db.execute(
            select(PublishedSite)
            .options(
                selectinload(PublishedSite.space),
                selectinload(PublishedSite.theme),
            )
            .where(
                PublishedSite.custom_domain == domain,
                PublishedSite.custom_domain_verified.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_site_for_space(self, space_id: str) -> PublishedSite | None:
        """Get the site for a space.

        Args:
            space_id: Space ID

        Returns:
            Site if exists for space
        """
        result = await self.db.execute(
            select(PublishedSite)
            .options(
                selectinload(PublishedSite.space),
                selectinload(PublishedSite.theme),
            )
            .where(PublishedSite.space_id == space_id)
        )
        return result.scalar_one_or_none()

    async def create_site(
        self,
        data: SiteCreate,
        user_id: str,
    ) -> PublishedSite:
        """Create a new published site.

        Args:
            data: Site creation data
            user_id: User creating the site

        Returns:
            Created site
        """
        # Verify space exists and get organization
        result = await self.db.execute(
            select(Space)
            .options(selectinload(Space.workspace))
            .where(Space.id == data.space_id)
        )
        space = result.scalar_one_or_none()
        if not space:
            raise PublishingError(f"Space not found: {data.space_id}")

        # Check if site already exists for space
        existing = await self.get_site_for_space(data.space_id)
        if existing:
            raise PublishingError(f"Site already exists for space: {data.space_id}")

        # Check slug uniqueness
        existing_slug = await self.get_site_by_slug(data.slug)
        if existing_slug:
            raise PublishingError(f"Slug already in use: {data.slug}")

        # Get organization ID from space's workspace
        organization_id = space.workspace.organization_id

        site = PublishedSite(
            space_id=data.space_id,
            organization_id=organization_id,
            slug=data.slug,
            site_title=data.site_title,
            site_description=data.site_description,
            theme_id=data.theme_id,
            custom_css=data.custom_css,
            logo_url=data.logo_url,
            og_image_url=data.og_image_url,
            favicon_url=data.favicon_url,
            visibility=data.visibility.value,
            allowed_email_domains=data.allowed_email_domains,
            search_enabled=data.search_enabled,
            toc_enabled=data.toc_enabled,
            version_selector_enabled=data.version_selector_enabled,
            feedback_enabled=data.feedback_enabled,
            analytics_id=data.analytics_id,
            status=SiteStatus.DRAFT.value,
        )

        self.db.add(site)
        await self.db.commit()
        await self.db.refresh(site)

        # Log audit event
        await self.audit.log_event(
            event_type="SITE_CREATED",
            actor_id=user_id,
            resource_type="published_site",
            resource_id=site.id,
            details={"slug": site.slug, "space_id": data.space_id},
        )

        return site

    async def update_site(
        self,
        site_id: str,
        data: SiteUpdate,
        user_id: str,
    ) -> PublishedSite | None:
        """Update a site.

        Args:
            site_id: Site ID
            data: Update data
            user_id: User updating

        Returns:
            Updated site if found
        """
        site = await self.get_site(site_id)
        if not site:
            return None

        # Check slug uniqueness if changing
        if data.slug and data.slug != site.slug:
            existing = await self.get_site_by_slug(data.slug)
            if existing:
                raise PublishingError(f"Slug already in use: {data.slug}")

        # Check domain uniqueness if changing
        if data.custom_domain and data.custom_domain != site.custom_domain:
            existing = await self.get_site_by_domain(data.custom_domain)
            if existing:
                raise PublishingError(f"Domain already in use: {data.custom_domain}")
            # Reset verification when domain changes
            site.custom_domain_verified = False

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(site, key):
                # Handle enum values
                if key == "visibility" and value is not None:
                    value = value.value if hasattr(value, "value") else value
                # Handle JSON fields
                if key in ("navigation_config", "footer_config") and value is not None:
                    value = json.dumps(value)
                setattr(site, key, value)

        await self.db.commit()
        await self.db.refresh(site)

        # Log audit event
        await self.audit.log_event(
            event_type="SITE_UPDATED",
            actor_id=user_id,
            resource_type="published_site",
            resource_id=site.id,
            details={"updated_fields": list(update_data.keys())},
        )

        return site

    async def delete_site(
        self,
        site_id: str,
        user_id: str,
    ) -> bool:
        """Delete a site.

        Args:
            site_id: Site ID
            user_id: User deleting

        Returns:
            True if deleted
        """
        site = await self.get_site(site_id)
        if not site:
            return False

        slug = site.slug

        await self.db.delete(site)
        await self.db.commit()

        # Log audit event
        await self.audit.log_event(
            event_type="SITE_DELETED",
            actor_id=user_id,
            resource_type="published_site",
            resource_id=site_id,
            details={"slug": slug},
        )

        return True

    async def publish_site(
        self,
        site_id: str,
        user_id: str,
        commit_message: str | None = None,
    ) -> PublishResult:
        """Publish a site (make it live).

        Args:
            site_id: Site ID
            user_id: User publishing
            commit_message: Optional commit message

        Returns:
            Publish result
        """
        site = await self.get_site(site_id)
        if not site:
            raise PublishingError(f"Site not found: {site_id}")

        # Count publishable pages
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == site.space_id,
                Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            )
        )
        pages = result.scalars().all()
        pages_count = len(pages)

        # Update site status
        now = datetime.now(timezone.utc)
        site.status = SiteStatus.PUBLISHED.value
        site.last_published_at = now
        site.published_by_id = user_id

        await self.db.commit()
        await self.db.refresh(site)

        # Log audit event
        await self.audit.log_event(
            event_type="SITE_PUBLISHED",
            actor_id=user_id,
            resource_type="published_site",
            resource_id=site_id,
            details={
                "slug": site.slug,
                "pages_published": pages_count,
                "commit_message": commit_message,
            },
        )

        return PublishResult(
            success=True,
            site_id=site_id,
            published_at=now,
            commit_sha=site.published_commit_sha,
            pages_published=pages_count,
            public_url=site.public_url,
            message=f"Published {pages_count} pages",
        )

    async def unpublish_site(
        self,
        site_id: str,
        user_id: str,
    ) -> PublishedSite | None:
        """Unpublish a site (take offline).

        Args:
            site_id: Site ID
            user_id: User unpublishing

        Returns:
            Updated site if found
        """
        site = await self.get_site(site_id)
        if not site:
            return None

        site.status = SiteStatus.DRAFT.value

        await self.db.commit()
        await self.db.refresh(site)

        # Log audit event
        await self.audit.log_event(
            event_type="SITE_UNPUBLISHED",
            actor_id=user_id,
            resource_type="published_site",
            resource_id=site_id,
            details={"slug": site.slug},
        )

        return site

    async def get_site_navigation(
        self,
        site_id: str,
        current_page_id: str | None = None,
    ) -> SiteNavigation:
        """Get navigation structure for a site.

        Args:
            site_id: Site ID
            current_page_id: Current page for highlighting

        Returns:
            Navigation structure
        """
        site = await self.get_site(site_id)
        if not site:
            raise PublishingError(f"Site not found: {site_id}")

        # Get all published pages in the space
        result = await self.db.execute(
            select(Page)
            .where(
                Page.space_id == site.space_id,
                Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            )
            .order_by(Page.sort_order, Page.title)
        )
        pages = result.scalars().all()

        # Build navigation tree
        items = self._build_navigation_tree(pages, site.slug)

        return SiteNavigation(
            items=items,
            current_page_id=current_page_id,
        )

    def _build_navigation_tree(
        self,
        pages: list[Page],
        site_slug: str,
    ) -> list[NavigationItem]:
        """Build navigation tree from pages."""
        # Group pages by parent
        pages_by_parent: dict[str | None, list[Page]] = {}
        for page in pages:
            parent_id = page.parent_id
            if parent_id not in pages_by_parent:
                pages_by_parent[parent_id] = []
            pages_by_parent[parent_id].append(page)

        def build_items(parent_id: str | None) -> list[NavigationItem]:
            children = pages_by_parent.get(parent_id, [])
            items = []
            for page in children:
                item = NavigationItem(
                    id=page.id,
                    title=page.title,
                    slug=page.slug,
                    path=f"/s/{site_slug}/{page.slug}",
                    type="page",
                    children=build_items(page.id),
                )
                items.append(item)
            return items

        return build_items(None)

    async def render_page(
        self,
        site_id: str,
        page_slug: str,
    ) -> RenderedPage | None:
        """Render a page for the published site.

        Args:
            site_id: Site ID
            page_slug: Page slug

        Returns:
            Rendered page content
        """
        site = await self.get_site(site_id)
        if not site:
            return None

        # Get the page
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == site.space_id,
                Page.slug == page_slug,
                Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            )
        )
        page = result.scalar_one_or_none()
        if not page:
            return None

        # Render content
        renderer = PageRenderer(base_path=f"/s/{site.slug}")
        content_html = renderer.render(page.content or {})
        toc = renderer.get_toc()

        # Build breadcrumbs
        breadcrumbs = await self._build_breadcrumbs(page, site.slug)

        # Get prev/next pages
        prev_page, next_page = await self._get_adjacent_pages(page, site)

        return RenderedPage(
            id=page.id,
            title=page.title,
            slug=page.slug,
            path=f"/s/{site.slug}/{page.slug}",
            content_html=content_html,
            toc=toc,
            breadcrumbs=breadcrumbs,
            last_updated=page.updated_at,
            author_name=None,  # Could fetch from page owner
            meta_description=page.description,
            prev_page=prev_page,
            next_page=next_page,
        )

    async def _build_breadcrumbs(
        self,
        page: Page,
        site_slug: str,
    ) -> list[dict[str, str]]:
        """Build breadcrumb trail for a page."""
        breadcrumbs = [{"title": page.title, "path": f"/s/{site_slug}/{page.slug}"}]

        # Walk up parent chain
        current_id = page.parent_id
        while current_id:
            result = await self.db.execute(
                select(Page).where(Page.id == current_id)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                break
            breadcrumbs.insert(0, {
                "title": parent.title,
                "path": f"/s/{site_slug}/{parent.slug}",
            })
            current_id = parent.parent_id

        # Add home
        breadcrumbs.insert(0, {"title": "Home", "path": f"/s/{site_slug}"})

        return breadcrumbs

    async def _get_adjacent_pages(
        self,
        page: Page,
        site: PublishedSite,
    ) -> tuple[dict[str, str] | None, dict[str, str] | None]:
        """Get previous and next pages for navigation."""
        # Get all published pages ordered
        result = await self.db.execute(
            select(Page)
            .where(
                Page.space_id == site.space_id,
                Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            )
            .order_by(Page.sort_order, Page.title)
        )
        pages = list(result.scalars().all())

        # Find current page index
        current_idx = None
        for i, p in enumerate(pages):
            if p.id == page.id:
                current_idx = i
                break

        if current_idx is None:
            return None, None

        prev_page = None
        next_page = None

        if current_idx > 0:
            prev = pages[current_idx - 1]
            prev_page = {"title": prev.title, "path": f"/s/{site.slug}/{prev.slug}"}

        if current_idx < len(pages) - 1:
            next_p = pages[current_idx + 1]
            next_page = {"title": next_p.title, "path": f"/s/{site.slug}/{next_p.slug}"}

        return prev_page, next_page
