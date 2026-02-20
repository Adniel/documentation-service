"""Publishing module for documentation sites.

Sprint A: Publishing
Sprint D: Integrated Access Control
"""

from src.modules.publishing.schemas import (
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse,
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    SitePublishRequest,
    PublishResult,
    RenderedPage,
    NavigationItem,
    SiteNavigation,
)
from src.modules.publishing.service import PublishingService
from src.modules.publishing.theme_service import ThemeService
from src.modules.publishing.renderer import PageRenderer
from src.modules.publishing.access_service import (
    PublishedSiteAccessService,
    AccessResult,
    get_published_site_access_service,
)
from src.modules.publishing.content_transformer import (
    ContentTransformer,
    TransformResult,
    TransformAction,
    transform_page_content,
)
from src.modules.publishing.publish_validator import (
    PublishValidator,
    PublishReport,
    AudienceBreakdown,
    PublishWarning,
    generate_publish_report,
)
from src.modules.publishing.visitor_service import (
    VisitorService,
    MagicLinkResult,
    VisitorSession,
    get_visitor_service,
)
from src.modules.publishing.sso_bridge import (
    SSOBridge,
    SSOBridgeResult,
    get_sso_bridge,
)

__all__ = [
    # Schemas
    "ThemeCreate",
    "ThemeUpdate",
    "ThemeResponse",
    "SiteCreate",
    "SiteUpdate",
    "SiteResponse",
    "SitePublishRequest",
    "PublishResult",
    "RenderedPage",
    "NavigationItem",
    "SiteNavigation",
    # Services
    "PublishingService",
    "ThemeService",
    "PageRenderer",
    # Sprint D: Access Control
    "PublishedSiteAccessService",
    "AccessResult",
    "get_published_site_access_service",
    # Sprint D: Content Transformation
    "ContentTransformer",
    "TransformResult",
    "TransformAction",
    "transform_page_content",
    # Sprint D: Publishing Validation
    "PublishValidator",
    "PublishReport",
    "AudienceBreakdown",
    "PublishWarning",
    "generate_publish_report",
    # Sprint D: Visitor Management
    "VisitorService",
    "MagicLinkResult",
    "VisitorSession",
    "get_visitor_service",
    # Sprint D: SSO Bridge
    "SSOBridge",
    "SSOBridgeResult",
    "get_sso_bridge",
]
