"""Access control module.

Sprint 5: Permission-based access control
Sprint D: Classification inheritance for published sites
"""

from src.modules.access.classification_service import (
    ClassificationService,
    ClassificationChain,
    CLASSIFICATION_NAMES,
    CLASSIFICATION_VALUES,
    get_classification_service,
)
from src.modules.access.permission_service import (
    PermissionService,
    PermissionDeniedError,
    get_permission_service,
)

__all__ = [
    # Classification
    "ClassificationService",
    "ClassificationChain",
    "CLASSIFICATION_NAMES",
    "CLASSIFICATION_VALUES",
    "get_classification_service",
    # Permissions
    "PermissionService",
    "PermissionDeniedError",
    "get_permission_service",
]
