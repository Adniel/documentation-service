"""Credential service - AES-256 encryption for Git credentials.

Sprint 13: Git Remote Support

Provides secure storage and retrieval of Git credentials using:
- AES-256-GCM encryption
- Per-credential random IV
- Optional SSH key fingerprint extraction
"""

import base64
import hashlib
import os
import re
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.db.models.git_credential import GitCredential, CredentialType


class CredentialError(Exception):
    """Error in credential operations."""

    pass


class CredentialService:
    """Service for managing Git credentials with encryption."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._settings = get_settings()

    def _get_encryption_key(self) -> bytes:
        """Get AES-256 encryption key from settings.

        Key should be a base64-encoded 32-byte value.
        """
        key_str = self._settings.git_credential_encryption_key
        if not key_str:
            raise CredentialError(
                "GIT_CREDENTIAL_ENCRYPTION_KEY not configured. "
                "Generate with: python -c \"import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())\""
            )
        try:
            key = base64.b64decode(key_str)
            if len(key) != 32:
                raise CredentialError(
                    f"Encryption key must be 32 bytes, got {len(key)}"
                )
            return key
        except Exception as e:
            raise CredentialError(f"Invalid encryption key: {e}")

    def _encrypt(self, plaintext: str) -> tuple[str, str]:
        """Encrypt plaintext using AES-256-GCM.

        Returns (encrypted_value, iv) as base64 strings.
        """
        key = self._get_encryption_key()
        iv = os.urandom(12)  # 96-bit nonce for GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
        return (
            base64.b64encode(ciphertext).decode("utf-8"),
            base64.b64encode(iv).decode("utf-8"),
        )

    def _decrypt(self, encrypted_value: str, iv: str) -> str:
        """Decrypt ciphertext using AES-256-GCM."""
        key = self._get_encryption_key()
        ciphertext = base64.b64decode(encrypted_value)
        iv_bytes = base64.b64decode(iv)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(iv_bytes, ciphertext, None)
        return plaintext.decode("utf-8")

    def _extract_ssh_fingerprint(self, ssh_key: str) -> Optional[str]:
        """Extract fingerprint from SSH public key.

        Returns MD5 fingerprint in colon-separated hex format.
        """
        try:
            # SSH public keys have format: type base64-data comment
            parts = ssh_key.strip().split()
            if len(parts) < 2:
                return None

            key_data = base64.b64decode(parts[1])
            fingerprint = hashlib.md5(key_data).hexdigest()
            # Format as colon-separated pairs
            return ":".join(
                fingerprint[i : i + 2] for i in range(0, len(fingerprint), 2)
            )
        except Exception:
            return None

    def _validate_ssh_key(self, key: str) -> bool:
        """Validate SSH key format."""
        key = key.strip()
        # Check for common SSH key types
        valid_types = [
            "ssh-rsa",
            "ssh-ed25519",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ]
        return any(key.startswith(t) for t in valid_types)

    def _validate_token(self, token: str, provider: Optional[str] = None) -> bool:
        """Validate token format based on provider."""
        token = token.strip()
        if not token:
            return False

        # GitHub personal access tokens
        if provider == "github":
            # Classic: ghp_*, Fine-grained: github_pat_*
            return bool(re.match(r"^(ghp_|github_pat_)[a-zA-Z0-9_]+$", token))

        # GitLab personal access tokens
        if provider == "gitlab":
            # GitLab tokens are typically 20+ alphanumeric
            return bool(re.match(r"^(glpat-)?[a-zA-Z0-9\-_]{20,}$", token))

        # Generic validation - at least 20 chars
        return len(token) >= 20

    async def get_credential(self, organization_id: str) -> Optional[GitCredential]:
        """Get credential for organization."""
        result = await self.db.execute(
            select(GitCredential).where(
                GitCredential.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def get_decrypted_credential(
        self, organization_id: str
    ) -> Optional[str]:
        """Get decrypted credential value.

        Returns the plaintext credential or None if not found.
        """
        credential = await self.get_credential(organization_id)
        if not credential:
            return None

        return self._decrypt(credential.encrypted_value, credential.encryption_iv)

    async def create_credential(
        self,
        organization_id: str,
        credential_type: CredentialType,
        value: str,
        created_by_id: str,
        label: Optional[str] = None,
        expires_at: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> GitCredential:
        """Create new credential for organization.

        Validates credential format and encrypts before storage.
        """
        # Validate based on type
        if credential_type == CredentialType.SSH_KEY:
            if not self._validate_ssh_key(value):
                raise CredentialError(
                    "Invalid SSH key format. Must be a public key starting with "
                    "ssh-rsa, ssh-ed25519, or ecdsa-*"
                )
            fingerprint = self._extract_ssh_fingerprint(value)
        elif credential_type == CredentialType.HTTPS_TOKEN:
            if not self._validate_token(value, provider):
                raise CredentialError(
                    "Invalid token format. Tokens must be at least 20 characters."
                )
            fingerprint = None
        else:
            # Deploy key - validate as SSH key
            if not self._validate_ssh_key(value):
                raise CredentialError("Invalid deploy key format.")
            fingerprint = self._extract_ssh_fingerprint(value)

        # Check for existing credential
        existing = await self.get_credential(organization_id)
        if existing:
            raise CredentialError(
                "Credential already exists for this organization. "
                "Delete existing credential first."
            )

        # Encrypt the credential
        encrypted_value, iv = self._encrypt(value)

        # Create credential record
        credential = GitCredential(
            organization_id=organization_id,
            credential_type=credential_type,
            encrypted_value=encrypted_value,
            encryption_iv=iv,
            key_fingerprint=fingerprint,
            label=label,
            expires_at=expires_at,
            created_by_id=created_by_id,
        )

        self.db.add(credential)
        await self.db.flush()
        await self.db.refresh(credential)

        return credential

    async def delete_credential(self, organization_id: str) -> bool:
        """Delete credential for organization."""
        credential = await self.get_credential(organization_id)
        if not credential:
            return False

        await self.db.delete(credential)
        await self.db.flush()
        return True

    async def rotate_credential(
        self,
        organization_id: str,
        new_value: str,
        created_by_id: str,
    ) -> GitCredential:
        """Rotate credential with new value.

        Keeps the same type and label, just updates the encrypted value.
        """
        existing = await self.get_credential(organization_id)
        if not existing:
            raise CredentialError("No credential found to rotate")

        # Delete old and create new
        credential_type = existing.credential_type
        label = existing.label
        expires_at = existing.expires_at

        await self.delete_credential(organization_id)

        return await self.create_credential(
            organization_id=organization_id,
            credential_type=credential_type,
            value=new_value,
            created_by_id=created_by_id,
            label=label,
            expires_at=expires_at,
        )
