"""Content transformer for published sites.

Sprint D: Integrated Access Control

Transforms internal references (links, embeds, transclusions) in page content
based on viewer's access level. Aligns with site discovery settings.

Transformation rules:
- show_restricted_as_placeholder = False: Remove links/embeds or render as plain text
- show_restricted_as_placeholder = True: Show with restricted indicator, link to placeholder
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Awaitable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.page import Page
from src.db.models.published_site import PublishedSite
from src.db.models.site_visitor import SiteVisitor
from src.db.models.user import User
from src.modules.publishing.access_service import PublishedSiteAccessService


class TransformAction(str, Enum):
    """How to transform inaccessible content."""

    REMOVE = "remove"  # Remove entirely
    PLAIN_TEXT = "plain_text"  # Keep text, remove link
    PLACEHOLDER = "placeholder"  # Show with restricted indicator


@dataclass
class TransformResult:
    """Result of content transformation."""

    content: str
    restricted_references: list[str] = field(default_factory=list)  # IDs of restricted docs
    removed_embeds: list[str] = field(default_factory=list)  # IDs of removed embedded content
    transform_count: int = 0  # Number of transformations applied


class ContentTransformer:
    """Transforms page content based on viewer's access level.

    Handles:
    - Markdown links: [text](./path) or [text](/page/slug)
    - Wiki links: [[Page Name]] or [[Page Name|Display Text]]
    - Image embeds: ![alt](./path/image.png)
    - File embeds: [Download](./path/file.pdf)
    - Transclusions: {{include:page-ref}}
    """

    # Regex patterns for different content types
    # Markdown links to internal pages
    MARKDOWN_LINK_PATTERN = re.compile(
        r'\[([^\]]+)\]\(((?:/page/[^)]+)|(?:\.{1,2}/[^)]+))\)',
        re.MULTILINE
    )

    # Wiki-style links
    WIKI_LINK_PATTERN = re.compile(
        r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',
        re.MULTILINE
    )

    # Image embeds (internal)
    IMAGE_EMBED_PATTERN = re.compile(
        r'!\[([^\]]*)\]\(((?:/page/[^)]+)|(?:\.{1,2}/[^)]+)|(?:/attachments/[^)]+))\)',
        re.MULTILINE
    )

    # Transclusions
    TRANSCLUSION_PATTERN = re.compile(
        r'\{\{include:([^}]+)\}\}',
        re.MULTILINE
    )

    def __init__(
        self,
        db: AsyncSession,
        access_service: PublishedSiteAccessService,
        site: PublishedSite,
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
        current_page: Optional[Page] = None,
    ):
        self.db = db
        self.access_service = access_service
        self.site = site
        self.visitor = visitor
        self.internal_user = internal_user
        self.current_page = current_page
        self._access_cache: dict[str, bool] = {}
        self._page_cache: dict[str, Optional[Page]] = {}

    async def transform_content(self, content: str) -> TransformResult:
        """Transform all internal references in content based on access.

        Returns transformed content and lists of restricted/removed references.
        """
        result = TransformResult(content=content)

        # Determine transform action based on site settings
        action = (
            TransformAction.PLACEHOLDER
            if self.site.show_restricted_as_placeholder
            else TransformAction.PLAIN_TEXT
        )

        # Transform in order: transclusions first (they may contain links)
        content = await self._transform_transclusions(content, action, result)

        # Then images (before general links to avoid matching them)
        content = await self._transform_images(content, action, result)

        # Then wiki links
        content = await self._transform_wiki_links(content, action, result)

        # Finally markdown links
        content = await self._transform_links(content, action, result)

        result.content = content
        return result

    async def prefetch_access(self, content: str) -> None:
        """Pre-fetch access for all referenced pages to optimize batch queries.

        Call this before transform_content() for better performance with
        content containing many links.
        """
        page_refs: set[str] = set()

        # Extract all page references
        for match in self.MARKDOWN_LINK_PATTERN.finditer(content):
            page_refs.add(match.group(2))

        for match in self.WIKI_LINK_PATTERN.finditer(content):
            page_refs.add(match.group(1))

        for match in self.IMAGE_EMBED_PATTERN.finditer(content):
            page_refs.add(match.group(2))

        for match in self.TRANSCLUSION_PATTERN.finditer(content):
            page_refs.add(match.group(1))

        # Resolve and cache all
        for ref in page_refs:
            page_id = await self._resolve_ref_to_page_id(ref)
            if page_id:
                await self._check_access(page_id)

    async def _get_page(self, page_id: str) -> Optional[Page]:
        """Get page by ID with caching."""
        if page_id not in self._page_cache:
            result = await self.db.execute(
                select(Page).where(Page.id == page_id)
            )
            self._page_cache[page_id] = result.scalar_one_or_none()
        return self._page_cache[page_id]

    async def _get_page_by_slug(self, slug: str) -> Optional[Page]:
        """Get page by slug within the site's space."""
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == self.site.space_id,
                Page.slug == slug,
            )
        )
        page = result.scalar_one_or_none()
        if page:
            self._page_cache[page.id] = page
        return page

    async def _get_page_by_title(self, title: str) -> Optional[Page]:
        """Get page by title within the site's space."""
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == self.site.space_id,
                Page.title.ilike(title),
            )
        )
        page = result.scalar_one_or_none()
        if page:
            self._page_cache[page.id] = page
        return page

    async def _resolve_ref_to_page_id(self, ref: str) -> Optional[str]:
        """Resolve a reference to a page ID.

        Handles:
        - /page/slug
        - ./relative-slug
        - ../parent/slug
        - Attachment paths
        - Page titles (for wiki links)
        """
        ref = ref.strip()

        # /page/slug format
        if ref.startswith("/page/"):
            slug = ref[6:].split("?")[0].split("#")[0]  # Remove query/fragment
            page = await self._get_page_by_slug(slug)
            return page.id if page else None

        # Relative path ./slug or ../slug
        if ref.startswith("./") or ref.startswith("../"):
            # For now, treat as slug within same space
            slug = ref.split("/")[-1].split("?")[0].split("#")[0]
            page = await self._get_page_by_slug(slug)
            return page.id if page else None

        # Attachment path - extract page ID if embedded
        if ref.startswith("/attachments/"):
            # Format: /attachments/{page_id}/{filename}
            parts = ref.split("/")
            if len(parts) >= 3:
                potential_id = parts[2]
                # Validate it looks like a UUID
                if len(potential_id) == 36 and potential_id.count("-") == 4:
                    return potential_id
            return None

        # Try as page title (for wiki links)
        page = await self._get_page_by_title(ref)
        if page:
            return page.id

        # Try as slug
        page = await self._get_page_by_slug(ref)
        return page.id if page else None

    async def _check_access(self, page_id: str) -> bool:
        """Check access with caching to avoid repeated checks."""
        if page_id not in self._access_cache:
            page = await self._get_page(page_id)
            if not page:
                self._access_cache[page_id] = False
            else:
                access = await self.access_service.can_access_page(
                    self.site, page, self.visitor, self.internal_user
                )
                self._access_cache[page_id] = access.allowed
        return self._access_cache[page_id]

    async def _transform_links(
        self,
        content: str,
        action: TransformAction,
        result: TransformResult,
    ) -> str:
        """Transform markdown links to restricted pages."""
        matches = list(self.MARKDOWN_LINK_PATTERN.finditer(content))

        # Process in reverse to preserve positions
        for match in reversed(matches):
            link_text = match.group(1)
            link_target = match.group(2)

            # Resolve to page ID
            page_id = await self._resolve_ref_to_page_id(link_target)
            if not page_id:
                continue  # External or unresolvable link, keep as-is

            # Check access
            if await self._check_access(page_id):
                continue  # Has access, keep link

            # No access - transform
            result.restricted_references.append(page_id)
            result.transform_count += 1

            if action == TransformAction.PLACEHOLDER:
                replacement = f"🔒 [{link_text}]({link_target})"
            else:
                replacement = link_text  # Plain text, no link

            content = content[:match.start()] + replacement + content[match.end():]

        return content

    async def _transform_wiki_links(
        self,
        content: str,
        action: TransformAction,
        result: TransformResult,
    ) -> str:
        """Transform wiki-style links to restricted pages."""
        matches = list(self.WIKI_LINK_PATTERN.finditer(content))

        for match in reversed(matches):
            page_ref = match.group(1)
            display_text = match.group(2) or page_ref

            # Resolve to page ID
            page_id = await self._resolve_ref_to_page_id(page_ref)
            if not page_id:
                continue  # Unresolved, keep as-is

            if await self._check_access(page_id):
                continue  # Has access, keep link

            result.restricted_references.append(page_id)
            result.transform_count += 1

            if action == TransformAction.PLACEHOLDER:
                replacement = f"🔒 {display_text}"
            else:
                replacement = display_text

            content = content[:match.start()] + replacement + content[match.end():]

        return content

    async def _transform_images(
        self,
        content: str,
        action: TransformAction,
        result: TransformResult,
    ) -> str:
        """Transform embedded images from restricted pages."""
        matches = list(self.IMAGE_EMBED_PATTERN.finditer(content))

        for match in reversed(matches):
            alt_text = match.group(1)
            image_src = match.group(2)

            # Check if image is from a restricted page
            page_id = await self._resolve_ref_to_page_id(image_src)
            if not page_id:
                continue  # External image or not linked to a page

            if await self._check_access(page_id):
                continue  # Has access, keep image

            result.removed_embeds.append(page_id)
            result.transform_count += 1

            if action == TransformAction.PLACEHOLDER:
                replacement = f"[🔒 Image: {alt_text or 'Restricted content'}]"
            else:
                replacement = ""  # Remove entirely

            content = content[:match.start()] + replacement + content[match.end():]

        return content

    async def _transform_transclusions(
        self,
        content: str,
        action: TransformAction,
        result: TransformResult,
    ) -> str:
        """Transform transclusions from restricted pages."""
        matches = list(self.TRANSCLUSION_PATTERN.finditer(content))

        for match in reversed(matches):
            page_ref = match.group(1)

            page_id = await self._resolve_ref_to_page_id(page_ref)
            if not page_id:
                continue

            if await self._check_access(page_id):
                continue  # Has access, keep transclusion marker

            result.removed_embeds.append(page_id)
            result.transform_count += 1

            if action == TransformAction.PLACEHOLDER:
                message = (
                    self.site.restricted_placeholder_message
                    or "You do not have access to view this content."
                )
                replacement = (
                    f"\n> 🔒 **Restricted Content**\n"
                    f"> {message}\n"
                )
            else:
                replacement = ""

            content = content[:match.start()] + replacement + content[match.end():]

        return content


# Convenience function
async def transform_page_content(
    db: AsyncSession,
    site: PublishedSite,
    content: str,
    visitor: Optional[SiteVisitor] = None,
    internal_user: Optional[User] = None,
    current_page: Optional[Page] = None,
) -> TransformResult:
    """Transform page content for a specific visitor.

    Convenience function that creates a transformer and runs transformation.
    """
    access_service = PublishedSiteAccessService(db)
    transformer = ContentTransformer(
        db=db,
        access_service=access_service,
        site=site,
        visitor=visitor,
        internal_user=internal_user,
        current_page=current_page,
    )

    # Prefetch for performance
    await transformer.prefetch_access(content)

    return await transformer.transform_content(content)
