# Sprint D: Integrated Access Control for Published Sites

## Overview

This sprint implements a **layered access model** for published sites where:
1. **Site visibility** acts as the first gate (who can reach the site)
2. **Document classification + ACLs** act as the second gate (what they can see once inside)

The principle: **Most restrictive wins** - both classification AND ACLs must grant access.

## Design Decisions

| Aspect | Decision |
|--------|----------|
| **Authentication** | Hybrid: SSO for internal users, email invitation with roles for external |
| **External user default** | Public access only (clearance 0) until role assigned |
| **Access rule** | Classification AND ACLs must both allow access |
| **Site visibility** | First gate - must pass to reach site |
| **Document access** | Second gate - clearance + ACLs checked per document |
| **Hidden docs** | Completely hidden by default, configurable per-site/document |
| **Classification default** | Full hierarchy: Org → Workspace → Space → Document |
| **Publishing** | Summary report + audit log |
| **Cross-doc links** | Transformed based on discovery setting (see Content Transformation) |
| **Embedded content** | Filtered based on discovery setting |
| **Transclusions** | Filtered based on discovery setting (future support) |

## Access Matrix

### Site Visibility as First Gate

| Site Visibility | Who Can Reach |
|-----------------|---------------|
| `PUBLIC` | Anyone (including anonymous) |
| `AUTHENTICATED` | Logged-in users only |
| `RESTRICTED` | Allowed email domains only |

### Document Access (Second Gate)

For users who pass the site visibility gate:

| User Type | Clearance | Can See Documents With Classification |
|-----------|-----------|---------------------------------------|
| Anonymous visitor | N/A (treated as 0) | `public` only + no restrictive ACLs |
| External (no role) | 0 | `public` only + ACLs they're in |
| External (role assigned) | Per role | Up to role's clearance + ACLs they're in |
| Internal (SSO) | Per user record | Up to their clearance + ACLs they're in |

### Classification to Site Visibility Mapping

When a document's effective classification is higher than what the site allows:

| Document Classification | Can Appear On Site With Visibility |
|------------------------|-----------------------------------|
| `public` (0) | PUBLIC, AUTHENTICATED, RESTRICTED |
| `internal` (1) | AUTHENTICATED, RESTRICTED (hidden on PUBLIC for anonymous) |
| `confidential` (2) | RESTRICTED (or shown only to high-clearance users) |
| `restricted` (3) | RESTRICTED (only to high-clearance users) |

## Implementation Phases

### Phase 1: Database Schema Updates

#### 1.1 Add Workspace Classification Default

```python
# backend/src/db/models/workspace.py
class Workspace(Base, UUIDMixin, TimestampMixin):
    # ... existing fields ...

    # Classification default (inherits from org, can be stricter)
    default_classification: Mapped[int | None] = mapped_column(
        default=None,  # None = inherit from org
        nullable=True,
    )
```

#### 1.2 Add Page Discovery Override

```python
# backend/src/db/models/page.py
class Page(Base, UUIDMixin, TimestampMixin):
    # ... existing fields ...

    # Discovery behavior when user lacks access
    # None = inherit from site setting
    # True = show "Access Restricted" message
    # False = completely hidden
    show_when_restricted: Mapped[bool | None] = mapped_column(
        default=None,
        nullable=True,
    )
```

#### 1.3 Add Site Discovery Default

```python
# backend/src/db/models/published_site.py
class PublishedSite(Base, UUIDMixin, TimestampMixin):
    # ... existing fields ...

    # Discovery behavior for restricted documents
    show_restricted_as_placeholder: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    restricted_placeholder_message: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
```

#### 1.4 Site Visitors Table (External Users)

```python
# backend/src/db/models/site_visitor.py
class SiteVisitor(Base, UUIDMixin, TimestampMixin):
    """External user with access to published sites."""

    __tablename__ = "site_visitors"

    # Email-based identity
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Authentication
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    magic_link_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    magic_link_expires: Mapped[datetime | None] = mapped_column(nullable=True)

    # Profile
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Link to internal user if applicable (for SSO)
    internal_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
```

#### 1.5 Site Visitor Roles Table

```python
# backend/src/db/models/site_visitor_role.py
class SiteVisitorRole(Base, UUIDMixin, TimestampMixin):
    """Role assignment for external visitors on a site."""

    __tablename__ = "site_visitor_roles"

    # The visitor
    visitor_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("site_visitors.id", ondelete="CASCADE"),
    )

    # The site
    site_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("published_sites.id", ondelete="CASCADE"),
    )

    # Role and clearance
    role_name: Mapped[str] = mapped_column(String(100), default="visitor")
    clearance_level: Mapped[int] = mapped_column(default=0)  # 0=public only

    # Optional explicit page access
    allowed_page_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Invitation tracking
    invited_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    invited_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Expiration
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("visitor_id", "site_id", name="uq_visitor_site_role"),
    )
```

#### 1.6 Migration File

```python
# backend/alembic/versions/012_integrated_access_control.py
"""Add integrated access control for published sites.

Revision ID: 012_integrated_access_control
Revises: 011_mcp_integration
"""
```

### Phase 2: Classification Inheritance Service

#### 2.1 Classification Resolution

```python
# backend/src/modules/access/classification_service.py
class ClassificationService:
    """Resolves effective classification using hierarchy inheritance."""

    async def get_effective_classification(self, page: Page) -> int:
        """
        Resolve effective classification for a page.

        Hierarchy: Org → Workspace → Space → Page
        Rule: Use page classification, falling back up the hierarchy.
        """
        # Page has explicit classification
        if page.classification:
            return ClassificationLevel.from_string(page.classification).value

        # Inherit from space
        space = await self.get_space(page.space_id)
        if space.classification is not None:
            return space.classification

        # Inherit from workspace
        workspace = await self.get_workspace(space.workspace_id)
        if workspace.default_classification is not None:
            return workspace.default_classification

        # Inherit from organization
        org = await self.get_organization(workspace.organization_id)
        return org.default_classification

    async def get_inherited_classification_chain(self, page_id: str) -> dict:
        """
        Get the full inheritance chain for debugging/display.

        Returns:
            {
                "effective": 2,
                "page": None,  # Not set on page
                "space": 2,    # Set at space level
                "workspace": None,
                "organization": 0
            }
        """
```

### Phase 3: Published Site Access Service

#### 3.1 Access Checker

```python
# backend/src/modules/publishing/access_service.py
class PublishedSiteAccessService:
    """Checks access to documents on published sites."""

    async def can_access_page(
        self,
        site: PublishedSite,
        page: Page,
        visitor: SiteVisitor | None,
        internal_user: User | None,
    ) -> AccessResult:
        """
        Check if visitor can access a page on a published site.

        Returns AccessResult with:
        - allowed: bool
        - reason: str (for debugging/logging)
        - show_placeholder: bool (if not allowed, should show restricted message?)
        """
        # Determine effective user clearance
        clearance = self._get_visitor_clearance(site, visitor, internal_user)

        # Get page's effective classification
        page_classification = await self.classification_service.get_effective_classification(page)

        # Check classification
        if clearance < page_classification:
            return AccessResult(
                allowed=False,
                reason=f"Clearance {clearance} < classification {page_classification}",
                show_placeholder=self._should_show_placeholder(site, page),
            )

        # Check ACLs
        if not await self._check_acls(page, visitor, internal_user):
            return AccessResult(
                allowed=False,
                reason="ACL restriction",
                show_placeholder=self._should_show_placeholder(site, page),
            )

        return AccessResult(allowed=True, reason="Access granted")

    def _get_visitor_clearance(
        self,
        site: PublishedSite,
        visitor: SiteVisitor | None,
        internal_user: User | None,
    ) -> int:
        """Get effective clearance for a site visitor."""
        # Anonymous = 0
        if not visitor and not internal_user:
            return 0

        # Internal user via SSO
        if internal_user:
            return internal_user.clearance_level

        # External visitor with role
        role = await self.get_visitor_role(visitor.id, site.id)
        if role:
            return role.clearance_level

        # External visitor without role = 0
        return 0

    async def _check_acls(
        self,
        page: Page,
        visitor: SiteVisitor | None,
        internal_user: User | None,
    ) -> bool:
        """Check if visitor passes ACL restrictions."""
        # Get all applicable ACLs
        permissions = await self.permission_service.get_permissions_for_resource(
            resource_type="page",
            resource_id=page.id,
        )

        # If no ACLs, access is allowed (classification already checked)
        if not permissions:
            # Also check space-level ACLs
            space_permissions = await self.permission_service.get_permissions_for_resource(
                resource_type="space",
                resource_id=page.space_id,
            )
            if not space_permissions:
                return True  # No restrictions

        # Check if visitor is in any allowed permission
        # ... implementation

    def _should_show_placeholder(self, site: PublishedSite, page: Page) -> bool:
        """Determine if restricted page should show placeholder."""
        # Page-level override takes precedence
        if page.show_when_restricted is not None:
            return page.show_when_restricted

        # Fall back to site setting
        return site.show_restricted_as_placeholder
```

#### 3.2 Access-Filtered Navigation

```python
# Modification to PublishingService.get_site_navigation()

async def get_site_navigation(
    self,
    site_id: str,
    visitor: SiteVisitor | None = None,
    internal_user: User | None = None,
    current_page_id: str | None = None,
) -> SiteNavigation:
    """Get navigation tree filtered by visitor's access."""
    site = await self.get_site(site_id)
    pages = await self._get_publishable_pages(site.space_id)

    # Filter pages by access
    visible_pages = []
    for page in pages:
        access = await self.access_service.can_access_page(
            site, page, visitor, internal_user
        )
        if access.allowed:
            visible_pages.append(page)
        elif access.show_placeholder:
            # Include but mark as restricted
            visible_pages.append(PagePlaceholder(
                id=page.id,
                title=page.title,
                is_restricted=True,
                message=site.restricted_placeholder_message,
            ))

    # Build navigation tree from visible pages
    return self._build_navigation_tree(visible_pages, current_page_id)
```

### Phase 3.5: Content Transformation (Links, Embeds, Transclusions)

When rendering page content, internal references to restricted documents must be transformed
based on the viewer's access level and the site's discovery settings.

#### 3.5.1 Content Types to Transform

| Content Type | Example | Transformation |
|--------------|---------|----------------|
| **Internal links** | `[See details](./secret-doc)` | Plain text or restricted indicator |
| **Wiki links** | `[[Secret Doc]]` | Plain text or restricted indicator |
| **Embedded images** | `![Diagram](./restricted-page/image.png)` | Remove or placeholder image |
| **Embedded files** | `[Download PDF](./restricted-page/file.pdf)` | Remove or restricted indicator |
| **Transclusions** | `{{include:restricted-page}}` | Remove or placeholder block |

#### 3.5.2 Transformation Rules

The transformation behavior aligns with the site's discovery setting:

| Discovery Setting | Link Behavior | Embed Behavior |
|-------------------|---------------|----------------|
| `show_restricted_as_placeholder = false` | Render as plain text (no link) | Remove entirely |
| `show_restricted_as_placeholder = true` | Show with 🔒 indicator, link to placeholder | Show placeholder with message |

#### 3.5.3 Content Transformer Service

```python
# backend/src/modules/publishing/content_transformer.py
from dataclasses import dataclass
from enum import Enum
import re
from typing import Callable

class TransformAction(str, Enum):
    """How to transform inaccessible content."""
    REMOVE = "remove"           # Remove entirely
    PLAIN_TEXT = "plain_text"   # Keep text, remove link
    PLACEHOLDER = "placeholder"  # Show with restricted indicator


@dataclass
class TransformResult:
    """Result of content transformation."""
    content: str
    restricted_references: list[str]  # IDs of restricted docs referenced
    removed_embeds: list[str]         # IDs of removed embedded content


class ContentTransformer:
    """Transforms page content based on viewer's access level."""

    # Regex patterns for different content types
    MARKDOWN_LINK_PATTERN = re.compile(
        r'\[([^\]]+)\]\((/page/[^)]+|\.{0,2}/[^)]+)\)'
    )
    WIKI_LINK_PATTERN = re.compile(
        r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
    )
    IMAGE_EMBED_PATTERN = re.compile(
        r'!\[([^\]]*)\]\(([^)]+)\)'
    )
    TRANSCLUSION_PATTERN = re.compile(
        r'\{\{include:([^}]+)\}\}'
    )

    def __init__(
        self,
        access_service: PublishedSiteAccessService,
        site: PublishedSite,
        visitor: SiteVisitor | None,
        internal_user: User | None,
    ):
        self.access_service = access_service
        self.site = site
        self.visitor = visitor
        self.internal_user = internal_user
        self._access_cache: dict[str, bool] = {}

    async def transform_content(self, content: str) -> TransformResult:
        """
        Transform all internal references in content based on access.

        Returns transformed content and list of restricted references found.
        """
        restricted_refs = []
        removed_embeds = []

        # Determine transform action based on site settings
        action = (
            TransformAction.PLACEHOLDER
            if self.site.show_restricted_as_placeholder
            else TransformAction.PLAIN_TEXT
        )

        # Transform internal links
        content = await self._transform_links(content, action, restricted_refs)

        # Transform wiki links
        content = await self._transform_wiki_links(content, action, restricted_refs)

        # Transform image embeds
        content = await self._transform_images(content, action, removed_embeds)

        # Transform transclusions (future support)
        content = await self._transform_transclusions(content, action, removed_embeds)

        return TransformResult(
            content=content,
            restricted_references=restricted_refs,
            removed_embeds=removed_embeds,
        )

    async def _check_access(self, page_id: str) -> bool:
        """Check access with caching to avoid repeated DB queries."""
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
        restricted_refs: list[str],
    ) -> str:
        """Transform markdown links to restricted pages."""

        async def replace_link(match: re.Match) -> str:
            link_text = match.group(1)
            link_target = match.group(2)

            # Resolve link to page ID
            page_id = await self._resolve_link_to_page_id(link_target)
            if not page_id:
                return match.group(0)  # External link, keep as-is

            # Check access
            if await self._check_access(page_id):
                return match.group(0)  # Has access, keep link

            # No access - transform based on action
            restricted_refs.append(page_id)

            if action == TransformAction.PLACEHOLDER:
                # Keep as link but add indicator
                return f"🔒 [{link_text}]({link_target})"
            else:
                # Plain text, no link
                return link_text

        # Process all links
        return await self._async_sub(self.MARKDOWN_LINK_PATTERN, replace_link, content)

    async def _transform_wiki_links(
        self,
        content: str,
        action: TransformAction,
        restricted_refs: list[str],
    ) -> str:
        """Transform wiki-style links to restricted pages."""

        async def replace_wiki_link(match: re.Match) -> str:
            page_ref = match.group(1)
            display_text = match.group(2) or page_ref

            # Resolve to page ID
            page_id = await self._resolve_wiki_link(page_ref)
            if not page_id:
                return match.group(0)  # Unresolved, keep as-is

            if await self._check_access(page_id):
                return match.group(0)  # Has access, keep link

            restricted_refs.append(page_id)

            if action == TransformAction.PLACEHOLDER:
                return f"🔒 {display_text}"
            else:
                return display_text

        return await self._async_sub(self.WIKI_LINK_PATTERN, replace_wiki_link, content)

    async def _transform_images(
        self,
        content: str,
        action: TransformAction,
        removed_embeds: list[str],
    ) -> str:
        """Transform embedded images from restricted pages."""

        async def replace_image(match: re.Match) -> str:
            alt_text = match.group(1)
            image_src = match.group(2)

            # Check if image is from a restricted page
            page_id = await self._resolve_image_source_to_page(image_src)
            if not page_id:
                return match.group(0)  # External image, keep as-is

            if await self._check_access(page_id):
                return match.group(0)  # Has access, keep image

            removed_embeds.append(page_id)

            if action == TransformAction.PLACEHOLDER:
                # Show placeholder
                return f"[🔒 Image: {alt_text or 'Restricted content'}]"
            else:
                # Remove entirely
                return ""

        return await self._async_sub(self.IMAGE_EMBED_PATTERN, replace_image, content)

    async def _transform_transclusions(
        self,
        content: str,
        action: TransformAction,
        removed_embeds: list[str],
    ) -> str:
        """Transform transclusions (embedded page content) from restricted pages."""

        async def replace_transclusion(match: re.Match) -> str:
            page_ref = match.group(1)

            page_id = await self._resolve_wiki_link(page_ref)
            if not page_id:
                return match.group(0)

            if await self._check_access(page_id):
                # Has access - actual transclusion rendering happens elsewhere
                return match.group(0)

            removed_embeds.append(page_id)

            if action == TransformAction.PLACEHOLDER:
                return (
                    f"\n> 🔒 **Restricted Content**\n"
                    f"> {self.site.restricted_placeholder_message or 'You do not have access to view this content.'}\n"
                )
            else:
                return ""

        return await self._async_sub(self.TRANSCLUSION_PATTERN, replace_transclusion, content)

    async def _async_sub(
        self,
        pattern: re.Pattern,
        replacer: Callable,
        content: str,
    ) -> str:
        """Perform async regex substitution."""
        result = []
        last_end = 0

        for match in pattern.finditer(content):
            result.append(content[last_end:match.start()])
            replacement = await replacer(match)
            result.append(replacement)
            last_end = match.end()

        result.append(content[last_end:])
        return "".join(result)

    async def _resolve_link_to_page_id(self, link: str) -> str | None:
        """Resolve a markdown link to a page ID."""
        # Handle /page/slug format
        if link.startswith("/page/"):
            slug = link[6:]
            return await self._get_page_id_by_slug(slug)

        # Handle relative links ./slug or ../slug
        if link.startswith("./") or link.startswith("../"):
            # Resolve relative to current page
            # Implementation depends on current page context
            pass

        return None  # External link

    async def _resolve_wiki_link(self, ref: str) -> str | None:
        """Resolve a wiki-style link to a page ID."""
        # Wiki links can be page titles or slugs
        return await self._get_page_id_by_title_or_slug(ref)

    async def _resolve_image_source_to_page(self, src: str) -> str | None:
        """
        Resolve image source to the page it belongs to.

        Images stored within page content inherit the page's classification.
        """
        # Implementation depends on how images are stored
        # Could be /page/{page_id}/attachments/{filename}
        # or /attachments/{page_id}/{filename}
        pass
```

#### 3.5.4 Integration with Page Renderer

```python
# Modification to PublishingService.render_page()

async def render_page(
    self,
    site_id: str,
    page_slug: str,
    visitor: SiteVisitor | None = None,
    internal_user: User | None = None,
) -> RenderedPage | None:
    """Render a page with access-aware content transformation."""
    site = await self.get_site(site_id)
    page = await self.get_page_by_slug(site.space_id, page_slug)

    if not page:
        return None

    # Check page access first
    access = await self.access_service.can_access_page(
        site, page, visitor, internal_user
    )
    if not access.allowed:
        if access.show_placeholder:
            return RenderedPage(
                id=page.id,
                title=page.title,
                is_restricted=True,
                restricted_message=site.restricted_placeholder_message,
                content=None,
            )
        return None

    # Get raw content
    raw_content = await self._get_page_content(page)

    # Transform content (links, embeds, transclusions)
    transformer = ContentTransformer(
        access_service=self.access_service,
        site=site,
        visitor=visitor,
        internal_user=internal_user,
    )
    transform_result = await transformer.transform_content(raw_content)

    # Convert to HTML
    html_content = self._markdown_to_html(transform_result.content)

    return RenderedPage(
        id=page.id,
        title=page.title,
        slug=page.slug,
        content=html_content,
        restricted_references=transform_result.restricted_references,
        toc=self._extract_toc(html_content) if site.toc_enabled else None,
    )
```

#### 3.5.5 Visual Styling for Restricted Indicators

```css
/* Styling for restricted content indicators */

/* Restricted link */
a.restricted-link {
  color: var(--text-muted);
  cursor: not-allowed;
  text-decoration: none;
  border-bottom: 1px dashed var(--border-color);
}

a.restricted-link::before {
  content: "🔒 ";
  font-size: 0.9em;
}

a.restricted-link:hover {
  /* Show tooltip explaining restriction */
}

/* Restricted image placeholder */
.restricted-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-color);
  border: 1px dashed var(--border-color);
  border-radius: 4px;
  padding: 1rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Restricted transclusion block */
.restricted-transclusion {
  background: var(--surface-color);
  border-left: 3px solid var(--warning-color);
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 0 4px 4px 0;
}

.restricted-transclusion::before {
  content: "🔒";
  margin-right: 0.5rem;
}
```

#### 3.5.6 Performance Optimization

To avoid N+1 queries when a page has many links:

```python
class ContentTransformer:
    async def prefetch_access(self, content: str) -> None:
        """
        Pre-fetch access for all referenced pages in one batch.

        Call this before transform_content() for better performance.
        """
        # Extract all page references
        page_refs = set()

        for match in self.MARKDOWN_LINK_PATTERN.finditer(content):
            page_refs.add(match.group(2))

        for match in self.WIKI_LINK_PATTERN.finditer(content):
            page_refs.add(match.group(1))

        # Resolve all to page IDs
        page_ids = await self._batch_resolve_refs(page_refs)

        # Batch fetch pages
        pages = await self._batch_get_pages(page_ids)

        # Batch check access
        for page in pages:
            access = await self.access_service.can_access_page(
                self.site, page, self.visitor, self.internal_user
            )
            self._access_cache[page.id] = access.allowed
```

### Phase 4: Publishing Validation & Report

#### 4.1 Pre-Publish Summary

```python
# backend/src/modules/publishing/publish_validator.py
class PublishValidator:
    """Validates and reports on site content before publishing."""

    async def generate_publish_report(
        self,
        site: PublishedSite,
    ) -> PublishReport:
        """
        Generate summary report of what will be visible to different audiences.

        Returns breakdown by:
        - Anonymous visitors
        - Authenticated (clearance 0)
        - Clearance levels 1-3
        """
        pages = await self._get_all_pages(site.space_id)

        report = PublishReport(
            site_id=site.id,
            site_visibility=site.visibility,
            total_pages=len(pages),
            breakdown={
                "anonymous": [],
                "clearance_0": [],
                "clearance_1": [],
                "clearance_2": [],
                "clearance_3": [],
            },
            warnings=[],
        )

        for page in pages:
            classification = await self.classification_service.get_effective_classification(page)

            # Categorize by minimum required clearance
            if classification == 0:
                report.breakdown["anonymous"].append(page.id)
                report.breakdown["clearance_0"].append(page.id)

            if classification <= 1:
                report.breakdown["clearance_1"].append(page.id)

            if classification <= 2:
                report.breakdown["clearance_2"].append(page.id)

            report.breakdown["clearance_3"].append(page.id)  # All pages

            # Check for ACL restrictions that might further limit access
            if await self._has_acl_restrictions(page):
                report.warnings.append(
                    f"Page '{page.title}' has ACL restrictions beyond classification"
                )

            # Warn if high-classification doc on public site
            if site.visibility == "public" and classification >= 2:
                report.warnings.append(
                    f"Page '{page.title}' (classification={classification}) "
                    f"will be hidden from anonymous visitors on public site"
                )

        return report

    async def log_publish_report(
        self,
        report: PublishReport,
        user_id: str,
    ):
        """Store publish report in audit log."""
        await self.audit_service.log_event(
            event_type="SITE_PUBLISHED",
            entity_type="published_site",
            entity_id=report.site_id,
            user_id=user_id,
            details={
                "visibility": report.site_visibility,
                "total_pages": report.total_pages,
                "public_pages": len(report.breakdown["anonymous"]),
                "internal_pages": len(report.breakdown["clearance_1"]) - len(report.breakdown["anonymous"]),
                "confidential_pages": len(report.breakdown["clearance_2"]) - len(report.breakdown["clearance_1"]),
                "restricted_pages": len(report.breakdown["clearance_3"]) - len(report.breakdown["clearance_2"]),
                "warnings": report.warnings,
            },
        )
```

### Phase 5: External User Management

#### 5.1 Visitor Service

```python
# backend/src/modules/publishing/visitor_service.py
class VisitorService:
    """Manage external visitors to published sites."""

    async def invite_visitor(
        self,
        site_id: str,
        email: str,
        role_name: str,
        clearance_level: int,
        invited_by_id: str,
        expires_at: datetime | None = None,
    ) -> tuple[SiteVisitor, SiteVisitorRole]:
        """
        Invite an external user to access a site.

        Sends magic link email for passwordless login.
        """
        # Get or create visitor
        visitor = await self.get_or_create_visitor(email)

        # Create role assignment
        role = SiteVisitorRole(
            visitor_id=visitor.id,
            site_id=site_id,
            role_name=role_name,
            clearance_level=clearance_level,
            invited_by_id=invited_by_id,
            expires_at=expires_at,
        )
        self.db.add(role)

        # Generate magic link
        await self.send_invitation_email(visitor, site_id)

        # Audit log
        await self.audit_service.log_event(
            event_type="VISITOR_INVITED",
            entity_type="site_visitor",
            entity_id=visitor.id,
            user_id=invited_by_id,
            details={
                "site_id": site_id,
                "email": email,
                "role_name": role_name,
                "clearance_level": clearance_level,
            },
        )

        return visitor, role

    async def authenticate_visitor(
        self,
        magic_link_token: str,
    ) -> tuple[SiteVisitor, str]:
        """
        Authenticate visitor via magic link.

        Returns visitor and session token.
        """
```

#### 5.2 SSO Bridge for Internal Users

```python
# backend/src/modules/publishing/sso_bridge.py
class SSOBridge:
    """Bridge internal user sessions to published site access."""

    async def get_internal_user_from_session(
        self,
        request: Request,
    ) -> User | None:
        """
        Check if request has valid internal user session.

        Looks for:
        1. Authorization header (Bearer token)
        2. Session cookie
        """
        # Try JWT from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            return await self.validate_internal_token(token)

        # Try session cookie
        session_cookie = request.cookies.get("docservice_session")
        if session_cookie:
            return await self.validate_session_cookie(session_cookie)

        return None
```

### Phase 6: API Updates

#### 6.1 Public Site Endpoints

```python
# backend/src/api/public_site.py (updated)

@router.get("/{site_slug}/page/{page_slug:path}")
async def get_site_page(
    site_slug: str,
    page_slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RenderedPage:
    """Get a rendered page, checking access permissions."""
    site = await get_public_site(site_slug, db, request)

    # Get visitor identity
    visitor, internal_user = await get_visitor_identity(request, db)

    publishing_service = PublishingService(db)
    access_service = PublishedSiteAccessService(db)

    page = await publishing_service.get_page_by_slug(site.space_id, page_slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Check access
    access = await access_service.can_access_page(site, page, visitor, internal_user)

    if not access.allowed:
        if access.show_placeholder:
            # Return placeholder response
            return RenderedPage(
                id=page.id,
                title=page.title,
                is_restricted=True,
                restricted_message=site.restricted_placeholder_message or "Access Restricted",
                content=None,
            )
        else:
            raise HTTPException(status_code=404, detail="Page not found")

    # Render full page
    return await publishing_service.render_page(site_id=site.id, page_slug=page_slug)
```

#### 6.2 Visitor Management Endpoints

```python
# backend/src/api/endpoints/visitors.py
router = APIRouter(prefix="/sites/{site_id}/visitors", tags=["visitors"])

@router.post("/invite")
async def invite_visitor(
    site_id: str,
    data: VisitorInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VisitorInviteResponse:
    """Invite an external user to access a published site."""

@router.get("/")
async def list_visitors(
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[VisitorWithRole]:
    """List all visitors with access to a site."""

@router.patch("/{visitor_id}/role")
async def update_visitor_role(
    site_id: str,
    visitor_id: str,
    data: VisitorRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SiteVisitorRole:
    """Update a visitor's role and clearance."""

@router.delete("/{visitor_id}")
async def revoke_visitor_access(
    site_id: str,
    visitor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a visitor's access to a site."""
```

#### 6.3 Publish Report Endpoint

```python
# backend/src/api/endpoints/publishing.py (addition)

@router.get("/sites/{site_id}/publish-preview")
async def get_publish_preview(
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PublishReport:
    """
    Get preview of what will be visible after publishing.

    Returns breakdown by audience and any warnings.
    """
    validator = PublishValidator(db)
    site = await publishing_service.get_site(site_id)

    return await validator.generate_publish_report(site)
```

### Phase 7: Frontend Components

#### 7.1 Visitor Management Panel

```typescript
// frontend/src/components/publishing/VisitorManagement.tsx
interface VisitorManagementProps {
  siteId: string;
}

export function VisitorManagement({ siteId }: VisitorManagementProps) {
  // List visitors
  // Invite new visitor dialog
  // Edit role/clearance
  // Revoke access
}
```

#### 7.2 Publish Preview Report

```typescript
// frontend/src/components/publishing/PublishPreview.tsx
interface PublishPreviewProps {
  siteId: string;
  onPublish: () => void;
}

export function PublishPreview({ siteId, onPublish }: PublishPreviewProps) {
  // Show breakdown by audience
  // Display warnings
  // Confirm publish button
}
```

#### 7.3 Discovery Settings

```typescript
// frontend/src/components/publishing/DiscoverySettings.tsx
interface DiscoverySettingsProps {
  site: PublishedSite;
  onUpdate: (settings: DiscoveryConfig) => void;
}

export function DiscoverySettings({ site, onUpdate }: DiscoverySettingsProps) {
  // Site-level default: hidden vs placeholder
  // Placeholder message customization
}
```

#### 7.4 Page Discovery Override

```typescript
// frontend/src/components/editor/PageAccessSettings.tsx
interface PageAccessSettingsProps {
  page: Page;
  onUpdate: (settings: AccessConfig) => void;
}

export function PageAccessSettings({ page, onUpdate }: PageAccessSettingsProps) {
  // Classification override
  // Discovery behavior override
  // Shows inherited values
}
```

### Phase 8: Testing

#### 8.1 Unit Tests

- `test_classification_service.py` - Inheritance resolution
- `test_access_service.py` - Access checking logic
- `test_publish_validator.py` - Report generation

#### 8.2 Integration Tests

- `test_public_site_access.py` - End-to-end access scenarios
- `test_visitor_management.py` - Invitation and role management
- `test_sso_bridge.py` - Internal user access

#### 8.3 E2E Tests

- Anonymous visitor access to public site
- Authenticated visitor with clearance
- Internal user via SSO
- Mixed-classification site navigation

## Migration Path

For existing sites:

1. **Default to current behavior**: All existing pages get `show_when_restricted = null` (inherit)
2. **Site default**: Existing sites get `show_restricted_as_placeholder = false` (hidden)
3. **No breaking changes**: Sites work as before until explicitly configured

## Files to Create/Modify

### New Files

| File | Description |
|------|-------------|
| `backend/alembic/versions/012_integrated_access_control.py` | Migration |
| `backend/src/db/models/site_visitor.py` | External visitor model |
| `backend/src/db/models/site_visitor_role.py` | Visitor role model |
| `backend/src/modules/access/classification_service.py` | Inheritance resolver |
| `backend/src/modules/publishing/access_service.py` | Access checker |
| `backend/src/modules/publishing/content_transformer.py` | Link/embed/transclusion transformer |
| `backend/src/modules/publishing/visitor_service.py` | Visitor management |
| `backend/src/modules/publishing/sso_bridge.py` | SSO integration |
| `backend/src/modules/publishing/publish_validator.py` | Publish reports |
| `backend/src/api/endpoints/visitors.py` | Visitor API |
| `frontend/src/components/publishing/VisitorManagement.tsx` | Visitor UI |
| `frontend/src/components/publishing/PublishPreview.tsx` | Report UI |
| `frontend/src/components/publishing/DiscoverySettings.tsx` | Settings UI |
| `frontend/src/components/editor/PageAccessSettings.tsx` | Page settings |

### Modified Files

| File | Changes |
|------|---------|
| `backend/src/db/models/workspace.py` | Add `default_classification` |
| `backend/src/db/models/page.py` | Add `show_when_restricted` |
| `backend/src/db/models/published_site.py` | Add discovery settings |
| `backend/src/api/public_site.py` | Add access checking |
| `backend/src/modules/publishing/service.py` | Filter by access |
| `frontend/src/lib/api.ts` | Add visitor types/methods |
| `frontend/src/pages/AdminPage.tsx` | Add visitor management tab |

## Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1: Database Schema | Small |
| Phase 2: Classification Service | Small |
| Phase 3: Access Service | Medium |
| Phase 3.5: Content Transformation | Medium |
| Phase 4: Publish Validation | Small |
| Phase 5: External User Management | Medium |
| Phase 6: API Updates | Medium |
| Phase 7: Frontend Components | Medium |
| Phase 8: Testing | Medium |

## Compliance Notes

This implementation supports:
- **ISO 9001 §7.5.3**: Controlled access to documented information
- **ISO 13485 §4.2.4**: Document access control
- **21 CFR §11.10(d)**: Limiting system access to authorized individuals
- **Audit trail**: All access grants, changes, and publish events are logged

## Future Extensibility

This implementation is designed to support future enhancements without breaking changes.

### Extension Points

#### 1. Content Source Abstraction

Current model ties a site to a single space:

```python
class PublishedSite:
    space_id: str  # Single space as content source
```

Future enhancement can add flexible content sources:

```python
class PublishedSite:
    # Content source options (use one)
    space_id: str | None              # Traditional: single space
    content_query: ContentQuery | None # Query-based: tags, themes, etc.
    page_ids: list[str] | None        # Explicit: manually selected pages

class ContentQuery:
    """Flexible content selection."""
    tags: list[str] | None            # Include pages with these tags
    exclude_tags: list[str] | None    # Exclude pages with these tags
    themes: list[str] | None          # Include pages in these themes
    space_ids: list[str] | None       # Include pages from multiple spaces
    status: list[str] | None          # Filter by document status
```

**Why this works**: Access control is per-page, so regardless of how pages are selected (space, tag, query), each page goes through the same access check.

#### 2. Navigation Source Abstraction

Current model auto-generates navigation from page hierarchy:

```python
async def get_site_navigation(site_id: str) -> SiteNavigation:
    # Auto-generate from space's page tree
```

Future enhancement can support custom TOC:

```python
class PublishedSite:
    navigation_mode: str = "auto"     # "auto" | "custom" | "hybrid"
    custom_navigation: CustomTOC | None

class CustomTOC:
    """User-defined navigation structure."""
    items: list[TOCItem]

class TOCItem:
    title: str                        # Display title (can differ from page title)
    page_id: str | None               # Link to page (None for section headers)
    external_url: str | None          # External link
    children: list[TOCItem]           # Nested items
```

**Why this works**: Navigation filtering (`can_access_page`) applies regardless of whether navigation came from auto-generation or custom TOC. Inaccessible items are filtered/transformed the same way.

#### 3. Content Transformation Extensibility

The `ContentTransformer` class is designed for extension:

```python
class ContentTransformer:
    # Current patterns
    MARKDOWN_LINK_PATTERN = ...
    WIKI_LINK_PATTERN = ...
    IMAGE_EMBED_PATTERN = ...
    TRANSCLUSION_PATTERN = ...

    # Future: Add new patterns without modifying existing code
    CUSTOM_BLOCK_PATTERN = ...        # {{custom:type:ref}}
    EMBED_PATTERN = ...               # For embedded videos, widgets, etc.
```

#### 4. Access Rule Extensibility

Current: Classification + ACLs (most restrictive wins)

Future possibilities (without breaking changes):
- **Time-based access**: Pages visible only during certain hours
- **Geographic restrictions**: Based on visitor location
- **Device-based access**: Desktop vs mobile restrictions

```python
class AccessRule(Protocol):
    """Interface for access rules."""
    async def check(self, page: Page, visitor: Visitor) -> AccessResult

class ClassificationRule(AccessRule): ...  # Current
class ACLRule(AccessRule): ...              # Current
class TimeBasedRule(AccessRule): ...        # Future
class GeoRule(AccessRule): ...              # Future

class AccessService:
    rules: list[AccessRule]  # Compose multiple rules

    async def check_access(self, page, visitor) -> AccessResult:
        # All rules must pass (most restrictive wins)
        for rule in self.rules:
            result = await rule.check(page, visitor)
            if not result.allowed:
                return result
        return AccessResult(allowed=True)
```

### Design Principles to Preserve

When extending the publishing system, maintain these principles:

1. **Per-page access control**: Access decisions are made per-page, independent of how pages are grouped or selected.

2. **Layered architecture**: Site visibility → Page access → Content transformation. Each layer is independent.

3. **Consistent transformation**: Links, embeds, and transclusions follow the same discovery rules as navigation.

4. **Audit everything**: Any new access rule or content source must integrate with audit logging.

5. **Graceful degradation**: If a future feature isn't configured, fall back to current behavior (space-based, auto-navigation).
