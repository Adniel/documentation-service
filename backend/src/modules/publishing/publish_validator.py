"""Publishing validation and reports.

Sprint D: Integrated Access Control

Generates pre-publish reports showing what different audiences can see,
and logs publish events to the audit trail.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.page import Page, PageStatus
from src.db.models.published_site import PublishedSite, SiteVisibility
from src.db.models.permission import Permission
from src.modules.access.classification_service import (
    ClassificationService,
    CLASSIFICATION_NAMES,
)


@dataclass
class AudienceBreakdown:
    """Pages accessible by a specific audience."""

    audience_name: str
    clearance_level: int
    page_count: int
    page_ids: list[str] = field(default_factory=list)
    page_titles: list[str] = field(default_factory=list)


@dataclass
class PublishWarning:
    """Warning about potential visibility issues."""

    level: str  # "info", "warning", "error"
    page_id: Optional[str]
    page_title: Optional[str]
    message: str


@dataclass
class PublishReport:
    """Complete report on what will be visible after publishing."""

    site_id: str
    site_slug: str
    site_visibility: str
    generated_at: datetime

    # Total counts
    total_pages: int
    publishable_pages: int  # APPROVED or EFFECTIVE status

    # Breakdown by audience
    audiences: list[AudienceBreakdown] = field(default_factory=list)

    # Classification breakdown
    classification_counts: dict[str, int] = field(default_factory=dict)

    # Warnings
    warnings: list[PublishWarning] = field(default_factory=list)

    # Pages with ACL restrictions
    acl_restricted_pages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "site_id": self.site_id,
            "site_slug": self.site_slug,
            "site_visibility": self.site_visibility,
            "generated_at": self.generated_at.isoformat(),
            "total_pages": self.total_pages,
            "publishable_pages": self.publishable_pages,
            "audiences": [
                {
                    "audience_name": a.audience_name,
                    "clearance_level": a.clearance_level,
                    "page_count": a.page_count,
                    "page_ids": a.page_ids,
                }
                for a in self.audiences
            ],
            "classification_counts": self.classification_counts,
            "warnings": [
                {
                    "level": w.level,
                    "page_id": w.page_id,
                    "page_title": w.page_title,
                    "message": w.message,
                }
                for w in self.warnings
            ],
            "acl_restricted_pages": self.acl_restricted_pages,
        }

    def to_audit_summary(self) -> dict:
        """Create concise summary for audit log."""
        return {
            "site_visibility": self.site_visibility,
            "total_pages": self.total_pages,
            "publishable_pages": self.publishable_pages,
            "public_pages": next(
                (a.page_count for a in self.audiences if a.clearance_level == 0),
                0,
            ),
            "internal_pages": next(
                (a.page_count for a in self.audiences if a.clearance_level == 1),
                0,
            ) - next(
                (a.page_count for a in self.audiences if a.clearance_level == 0),
                0,
            ),
            "confidential_pages": next(
                (a.page_count for a in self.audiences if a.clearance_level == 2),
                0,
            ) - next(
                (a.page_count for a in self.audiences if a.clearance_level == 1),
                0,
            ),
            "restricted_pages": next(
                (a.page_count for a in self.audiences if a.clearance_level == 3),
                0,
            ) - next(
                (a.page_count for a in self.audiences if a.clearance_level == 2),
                0,
            ),
            "warning_count": len(self.warnings),
            "acl_restricted_count": len(self.acl_restricted_pages),
        }


class PublishValidator:
    """Validates and reports on site content before publishing."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.classification_service = ClassificationService(db)

    async def _get_all_pages(self, space_id: str) -> list[Page]:
        """Get all pages in a space."""
        result = await self.db.execute(
            select(Page).where(Page.space_id == space_id)
        )
        return list(result.scalars().all())

    async def _get_publishable_pages(self, space_id: str) -> list[Page]:
        """Get pages that can be published (APPROVED or EFFECTIVE status)."""
        result = await self.db.execute(
            select(Page).where(
                Page.space_id == space_id,
                Page.status.in_([PageStatus.APPROVED.value, PageStatus.EFFECTIVE.value]),
            )
        )
        return list(result.scalars().all())

    async def _has_acl_restrictions(self, page: Page) -> bool:
        """Check if a page has ACL restrictions beyond classification."""
        # Check page-level ACLs
        result = await self.db.execute(
            select(Permission).where(
                Permission.resource_type == "page",
                Permission.resource_id == page.id,
                Permission.is_active == True,
            ).limit(1)
        )
        if result.scalar_one_or_none():
            return True

        # Check space-level ACLs
        result = await self.db.execute(
            select(Permission).where(
                Permission.resource_type == "space",
                Permission.resource_id == page.space_id,
                Permission.is_active == True,
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def generate_publish_report(
        self,
        site: PublishedSite,
    ) -> PublishReport:
        """Generate comprehensive report of what will be visible after publishing.

        Breaks down visibility by:
        - Anonymous visitors (clearance 0)
        - Each clearance level (0-3)
        - Includes warnings for potential issues
        """
        all_pages = await self._get_all_pages(site.space_id)
        publishable_pages = await self._get_publishable_pages(site.space_id)

        report = PublishReport(
            site_id=site.id,
            site_slug=site.slug,
            site_visibility=site.visibility,
            generated_at=datetime.utcnow(),
            total_pages=len(all_pages),
            publishable_pages=len(publishable_pages),
        )

        # Initialize classification counts
        for level_name in CLASSIFICATION_NAMES.values():
            report.classification_counts[level_name] = 0

        # Initialize audience breakdowns
        audience_pages: dict[int, list[tuple[str, str]]] = {
            0: [],  # Public
            1: [],  # Internal
            2: [],  # Confidential
            3: [],  # Restricted (all pages)
        }

        # Analyze each publishable page
        for page in publishable_pages:
            classification = await self.classification_service.get_effective_classification(page)
            classification_name = CLASSIFICATION_NAMES.get(classification, "unknown")

            # Count by classification
            report.classification_counts[classification_name] = (
                report.classification_counts.get(classification_name, 0) + 1
            )

            # Categorize by minimum required clearance
            for clearance in range(classification, 4):
                audience_pages[clearance].append((page.id, page.title))

            # Check for ACL restrictions
            if await self._has_acl_restrictions(page):
                report.acl_restricted_pages.append(page.id)
                report.warnings.append(PublishWarning(
                    level="info",
                    page_id=page.id,
                    page_title=page.title,
                    message=f"Page has ACL restrictions beyond classification",
                ))

            # Warn about high-classification docs on public sites
            if site.visibility == SiteVisibility.PUBLIC.value and classification >= 2:
                report.warnings.append(PublishWarning(
                    level="warning",
                    page_id=page.id,
                    page_title=page.title,
                    message=(
                        f"Page (classification={classification_name}) "
                        f"will be hidden from anonymous visitors on public site"
                    ),
                ))

            # Warn about restricted docs on authenticated sites
            if site.visibility == SiteVisibility.AUTHENTICATED.value and classification >= 3:
                report.warnings.append(PublishWarning(
                    level="warning",
                    page_id=page.id,
                    page_title=page.title,
                    message=(
                        f"Page (classification={classification_name}) "
                        f"will only be visible to users with highest clearance"
                    ),
                ))

        # Build audience breakdowns
        audience_names = {
            0: "Anonymous / Public",
            1: "Internal (clearance 1+)",
            2: "Confidential (clearance 2+)",
            3: "Restricted (clearance 3)",
        }

        for clearance, pages in audience_pages.items():
            report.audiences.append(AudienceBreakdown(
                audience_name=audience_names[clearance],
                clearance_level=clearance,
                page_count=len(pages),
                page_ids=[p[0] for p in pages],
                page_titles=[p[1] for p in pages],
            ))

        # Add warning if public site has no public pages
        if site.visibility == SiteVisibility.PUBLIC.value:
            public_count = len(audience_pages[0])
            if public_count == 0:
                report.warnings.append(PublishWarning(
                    level="warning",
                    page_id=None,
                    page_title=None,
                    message="Public site has no pages visible to anonymous visitors",
                ))

        return report

    async def validate_for_publish(
        self,
        site: PublishedSite,
    ) -> tuple[bool, list[str]]:
        """Validate if site is ready for publishing.

        Returns (is_valid, list of errors).
        """
        errors = []

        # Check site has content
        publishable_pages = await self._get_publishable_pages(site.space_id)
        if not publishable_pages:
            errors.append("No publishable pages (need APPROVED or EFFECTIVE status)")

        # Check for required fields
        if not site.site_title:
            errors.append("Site title is required")

        if not site.slug:
            errors.append("Site slug is required")

        return len(errors) == 0, errors


# Convenience function
async def generate_publish_report(
    db: AsyncSession,
    site: PublishedSite,
) -> PublishReport:
    """Generate publish report for a site."""
    validator = PublishValidator(db)
    return await validator.generate_publish_report(site)
