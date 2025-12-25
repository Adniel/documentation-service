"""Content Hash Service for 21 CFR Part 11 compliance.

Provides SHA-256 hashing of document content for signature integrity.
Content hashes ensure that signatures are bound to specific content
versions per §11.70 (signature/record linking).

Key properties:
- Deterministic: Same content always produces same hash
- Canonical: Content is normalized before hashing (sorted keys, no whitespace)
- Integrity: Any change to content produces a different hash
"""

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContentHashError(Exception):
    """Raised when content cannot be hashed."""
    pass


def _make_canonical_json(content: Any) -> str:
    """Convert content to canonical JSON representation.

    Canonical JSON has:
    - Keys sorted alphabetically
    - No unnecessary whitespace
    - Consistent encoding (UTF-8)

    This ensures the same logical content always produces
    the same hash, regardless of key order in the original.

    Args:
        content: Any JSON-serializable content

    Returns:
        Canonical JSON string

    Raises:
        ContentHashError: If content cannot be serialized
    """
    try:
        return json.dumps(
            content,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,  # Handle datetime and other non-JSON types
        )
    except (TypeError, ValueError) as e:
        raise ContentHashError(f"Cannot serialize content for hashing: {e}")


def compute_content_hash(content: Any) -> str:
    """Compute SHA-256 hash of document content.

    The content is first converted to canonical JSON, then hashed.
    This ensures consistent hashing regardless of:
    - Key order in dictionaries
    - Whitespace formatting
    - Object serialization order

    Args:
        content: Document content (dict, list, or JSON-serializable)

    Returns:
        SHA-256 hash as lowercase hex string (64 characters)

    Raises:
        ContentHashError: If content cannot be hashed

    Examples:
        >>> compute_content_hash({"title": "Test", "body": "Content"})
        'a1b2c3...'  # 64-char hex string

        >>> # Same content, different key order = same hash
        >>> h1 = compute_content_hash({"b": 2, "a": 1})
        >>> h2 = compute_content_hash({"a": 1, "b": 2})
        >>> h1 == h2
        True
    """
    if content is None:
        raise ContentHashError("Cannot hash None content")

    try:
        canonical = _make_canonical_json(content)
        content_bytes = canonical.encode("utf-8")
        hash_obj = hashlib.sha256(content_bytes)
        return hash_obj.hexdigest().lower()
    except ContentHashError:
        raise
    except Exception as e:
        raise ContentHashError(f"Failed to compute content hash: {e}")


def verify_content_hash(content: Any, expected_hash: str) -> bool:
    """Verify that content matches an expected hash.

    Args:
        content: Document content to verify
        expected_hash: Expected SHA-256 hash (hex string)

    Returns:
        True if content hash matches expected hash

    Raises:
        ContentHashError: If content cannot be hashed
    """
    actual_hash = compute_content_hash(content)
    return actual_hash.lower() == expected_hash.lower()


def compute_combined_hash(*items: Any) -> str:
    """Compute hash of multiple items combined.

    Useful for hashing document content along with metadata.
    Items are concatenated in a deterministic way before hashing.

    Args:
        *items: Items to hash together

    Returns:
        SHA-256 hash as lowercase hex string

    Example:
        >>> compute_combined_hash(
        ...     {"content": "doc"},
        ...     {"title": "Doc Title"},
        ...     "2025-01-01T00:00:00Z"
        ... )
        'abc123...'
    """
    combined = []
    for item in items:
        if item is not None:
            combined.append(_make_canonical_json(item))

    combined_str = "|".join(combined)  # Use delimiter to prevent collisions
    content_bytes = combined_str.encode("utf-8")
    hash_obj = hashlib.sha256(content_bytes)
    return hash_obj.hexdigest().lower()


def get_content_preview(content: Any, max_length: int = 200) -> str:
    """Get a human-readable preview of content for display.

    Used to show users what they're about to sign without
    revealing the full technical content.

    Args:
        content: Document content
        max_length: Maximum preview length

    Returns:
        Human-readable preview string
    """
    try:
        if isinstance(content, dict):
            # Try to extract meaningful text
            if "title" in content:
                title = str(content.get("title", ""))
            else:
                title = ""

            # Try common content field names
            body = ""
            for field in ["content", "body", "text", "description"]:
                if field in content:
                    body = str(content.get(field, ""))
                    break

            if title and body:
                preview = f"{title}: {body}"
            elif title:
                preview = title
            elif body:
                preview = body
            else:
                # Fallback to JSON representation
                preview = json.dumps(content, default=str)

        elif isinstance(content, str):
            preview = content
        elif isinstance(content, list):
            preview = json.dumps(content, default=str)
        else:
            preview = str(content)

        # Truncate if needed
        if len(preview) > max_length:
            preview = preview[:max_length - 3] + "..."

        return preview

    except Exception as e:
        logger.warning(f"Failed to create content preview: {e}")
        return "[Content preview unavailable]"
