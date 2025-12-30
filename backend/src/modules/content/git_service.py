"""Git integration service using pygit2.

This module provides an abstraction layer over Git operations,
hiding Git concepts from the application layer.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pygit2


class GitService:
    """Service for managing Git repositories and content."""

    def __init__(self, base_path: str):
        """Initialize the Git service.

        Args:
            base_path: Base directory for storing Git repositories
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_repo_path(self, org_slug: str) -> Path:
        """Get the path for an organization's repository."""
        return self.base_path / org_slug

    def _get_signature(self, name: str, email: str) -> pygit2.Signature:
        """Create a Git signature for commits."""
        return pygit2.Signature(name, email, int(datetime.now(timezone.utc).timestamp()), 0)

    def init_repo(self, org_slug: str) -> pygit2.Repository:
        """Initialize a new Git repository for an organization.

        Args:
            org_slug: Organization slug used as repository name

        Returns:
            Initialized repository
        """
        repo_path = self._get_repo_path(org_slug)
        if repo_path.exists():
            return pygit2.Repository(str(repo_path))

        # Initialize bare repository
        repo = pygit2.init_repository(str(repo_path), bare=False)

        # Create initial commit with README
        readme_content = f"# {org_slug}\n\nDocumentation repository.\n"
        blob_id = repo.create_blob(readme_content.encode())

        # Build tree
        tree_builder = repo.TreeBuilder()
        tree_builder.insert("README.md", blob_id, pygit2.GIT_FILEMODE_BLOB)
        tree_id = tree_builder.write()

        # Create initial commit
        sig = self._get_signature("Documentation Service", "system@docservice.local")
        repo.create_commit(
            "HEAD",
            sig,
            sig,
            "Initial repository setup",
            tree_id,
            [],  # No parents for initial commit
        )

        # Checkout the tree to make files available in working directory
        repo.checkout_head()

        return repo

    def get_repo(self, org_slug: str) -> pygit2.Repository | None:
        """Get an existing repository.

        Args:
            org_slug: Organization slug

        Returns:
            Repository or None if not found
        """
        repo_path = self._get_repo_path(org_slug)
        if not repo_path.exists():
            return None
        return pygit2.Repository(str(repo_path))

    def _get_file_path(
        self, workspace_slug: str, space_slug: str, page_slug: str
    ) -> str:
        """Build the file path within the repository."""
        return f"{workspace_slug}/{space_slug}/{page_slug}.json"

    def create_file(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        content: dict[str, Any],
        author_name: str,
        author_email: str,
        message: str | None = None,
    ) -> str:
        """Create a new file in the repository.

        Args:
            org_slug: Organization slug
            workspace_slug: Workspace slug
            space_slug: Space slug
            page_slug: Page slug (filename without extension)
            content: Content to store (will be JSON serialized)
            author_name: Author's name for the commit
            author_email: Author's email for the commit
            message: Optional commit message

        Returns:
            Git commit SHA
        """
        repo = self.get_repo(org_slug)
        if not repo:
            repo = self.init_repo(org_slug)

        file_path = self._get_file_path(workspace_slug, space_slug, page_slug)
        full_path = self._get_repo_path(org_slug) / file_path

        # Ensure parent directories exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        json_content = json.dumps(content, indent=2, ensure_ascii=False)
        full_path.write_text(json_content, encoding="utf-8")

        # Stage and commit
        repo.index.add(file_path)
        repo.index.write()

        sig = self._get_signature(author_name, author_email)
        tree = repo.index.write_tree()
        parent = repo.head.peel().id if not repo.head_is_unborn else None
        parents = [parent] if parent else []

        commit_message = message or f"Create {page_slug}"
        commit_id = repo.create_commit("HEAD", sig, sig, commit_message, tree, parents)

        return str(commit_id)

    def update_file(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        content: dict[str, Any],
        author_name: str,
        author_email: str,
        message: str | None = None,
    ) -> str:
        """Update an existing file in the repository.

        Args:
            Same as create_file

        Returns:
            Git commit SHA (new commit if content changed, existing HEAD if unchanged)
        """
        repo = self.get_repo(org_slug)
        if not repo:
            raise ValueError(f"Repository not found: {org_slug}")

        file_path = self._get_file_path(workspace_slug, space_slug, page_slug)
        full_path = self._get_repo_path(org_slug) / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Generate new content JSON
        json_content = json.dumps(content, indent=2, ensure_ascii=False)

        # Read existing content to check for actual changes
        existing_content = full_path.read_text(encoding="utf-8")

        # Skip commit if content is identical
        if existing_content == json_content:
            # Return current HEAD SHA - no new commit needed
            return str(repo.head.peel().id)

        # Write updated content
        full_path.write_text(json_content, encoding="utf-8")

        # Stage and commit
        repo.index.add(file_path)
        repo.index.write()

        sig = self._get_signature(author_name, author_email)
        tree = repo.index.write_tree()
        parent = repo.head.peel().id

        commit_message = message or f"Update {page_slug}"
        commit_id = repo.create_commit("HEAD", sig, sig, commit_message, tree, [parent])

        return str(commit_id)

    def read_file(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        commit_sha: str | None = None,
    ) -> dict[str, Any] | None:
        """Read a file from the repository.

        Args:
            org_slug: Organization slug
            workspace_slug: Workspace slug
            space_slug: Space slug
            page_slug: Page slug
            commit_sha: Optional specific commit to read from (defaults to HEAD)

        Returns:
            Parsed JSON content or None if not found
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return None

        file_path = self._get_file_path(workspace_slug, space_slug, page_slug)

        try:
            if commit_sha:
                commit = repo.get(commit_sha)
                tree = commit.tree
            else:
                tree = repo.head.peel().tree

            # Navigate to file in tree
            entry = tree[file_path]
            blob = repo.get(entry.id)
            content = blob.data.decode("utf-8")
            return json.loads(content)
        except (KeyError, pygit2.GitError):
            return None

    def get_file_history(
        self,
        org_slug: str,
        workspace_slug: str,
        space_slug: str,
        page_slug: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get commit history for a specific file.

        Args:
            org_slug: Organization slug
            workspace_slug: Workspace slug
            space_slug: Space slug
            page_slug: Page slug
            limit: Maximum number of commits to return

        Returns:
            List of commit information dicts
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return []

        file_path = self._get_file_path(workspace_slug, space_slug, page_slug)
        history = []

        try:
            for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TIME):
                # Check if file exists in this commit
                try:
                    commit.tree[file_path]
                    history.append(
                        {
                            "sha": str(commit.id),
                            "message": commit.message.strip(),
                            "author_name": commit.author.name,
                            "author_email": commit.author.email,
                            "timestamp": datetime.fromtimestamp(
                                commit.commit_time, tz=timezone.utc
                            ).isoformat(),
                        }
                    )
                    if len(history) >= limit:
                        break
                except KeyError:
                    continue
        except pygit2.GitError:
            pass

        return history

    def create_branch(
        self, org_slug: str, branch_name: str, from_ref: str = "HEAD"
    ) -> bool:
        """Create a new branch (for change requests/drafts).

        Args:
            org_slug: Organization slug
            branch_name: Name of the new branch
            from_ref: Reference to branch from (default HEAD)

        Returns:
            True if successful
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return False

        try:
            commit = repo.revparse_single(from_ref)
            repo.branches.create(branch_name, commit)
            return True
        except pygit2.GitError:
            return False

    def list_branches(self, org_slug: str) -> list[str]:
        """List all branches in the repository.

        Args:
            org_slug: Organization slug

        Returns:
            List of branch names
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return []

        return [b for b in repo.branches.local]

    def check_merge_conflicts(
        self,
        org_slug: str,
        source_branch: str,
        target_branch: str,
    ) -> dict[str, Any]:
        """Check if merging would create conflicts (dry run).

        Args:
            org_slug: Organization slug
            source_branch: Branch to merge from
            target_branch: Branch to merge into

        Returns:
            Dict with:
            - has_conflicts: bool
            - conflict_files: list of file paths with conflicts
            - can_fast_forward: bool (if true, merge is trivial)
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return {"has_conflicts": False, "conflict_files": [], "can_fast_forward": False}

        try:
            source = repo.branches[source_branch].peel()
            target = repo.branches[target_branch].peel()

            # Check if source is ancestor of target (already merged)
            if repo.descendant_of(target.id, source.id):
                return {"has_conflicts": False, "conflict_files": [], "can_fast_forward": True}

            # Check if target is ancestor of source (fast-forward possible)
            if repo.descendant_of(source.id, target.id):
                return {"has_conflicts": False, "conflict_files": [], "can_fast_forward": True}

            # Do a merge analysis
            merge_result, _ = repo.merge_analysis(source.id)

            # Check for up-to-date or fast-forward scenarios
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return {"has_conflicts": False, "conflict_files": [], "can_fast_forward": True}

            if merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                return {"has_conflicts": False, "conflict_files": [], "can_fast_forward": True}

            # Need to do actual merge to check for conflicts
            # Save current state
            current_head = repo.head.target

            # Perform merge in memory
            repo.merge(source.id)

            conflict_files = []
            if repo.index.conflicts:
                for conflict in repo.index.conflicts:
                    if conflict[1]:  # ours
                        conflict_files.append(conflict[1].path)
                    elif conflict[2]:  # theirs
                        conflict_files.append(conflict[2].path)

            # Cleanup - reset to previous state
            repo.state_cleanup()
            repo.reset(current_head, pygit2.GIT_RESET_HARD)

            return {
                "has_conflicts": len(conflict_files) > 0,
                "conflict_files": conflict_files,
                "can_fast_forward": False,
            }

        except pygit2.GitError as e:
            return {"has_conflicts": True, "conflict_files": [], "error": str(e), "can_fast_forward": False}

    def merge_branch(
        self,
        org_slug: str,
        source_branch: str,
        target_branch: str,
        author_name: str,
        author_email: str,
        message: str | None = None,
    ) -> str | None:
        """Merge a branch into another (publish a draft).

        Args:
            org_slug: Organization slug
            source_branch: Branch to merge from
            target_branch: Branch to merge into
            author_name: Author's name for merge commit
            author_email: Author's email
            message: Optional merge commit message

        Returns:
            Merge commit SHA or None if failed
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return None

        try:
            # Get source and target commits
            source = repo.branches[source_branch].peel()
            target = repo.branches[target_branch].peel()

            # Perform merge
            repo.merge(source.id)

            if repo.index.conflicts:
                # Conflicts exist - would need manual resolution
                repo.state_cleanup()
                return None

            # Create merge commit
            sig = self._get_signature(author_name, author_email)
            tree = repo.index.write_tree()
            merge_message = message or f"Merge {source_branch} into {target_branch}"
            commit_id = repo.create_commit(
                f"refs/heads/{target_branch}",
                sig,
                sig,
                merge_message,
                tree,
                [target.id, source.id],
            )

            repo.state_cleanup()
            return str(commit_id)
        except pygit2.GitError:
            return None

    def delete_branch(self, org_slug: str, branch_name: str) -> bool:
        """Delete a branch.

        Args:
            org_slug: Organization slug
            branch_name: Branch to delete

        Returns:
            True if successful
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return False

        try:
            branch = repo.branches[branch_name]
            branch.delete()
            return True
        except (KeyError, pygit2.GitError):
            return False

    # =========================================================================
    # REMOTE OPERATIONS (Sprint 13)
    # =========================================================================

    def add_remote(
        self,
        org_slug: str,
        remote_url: str,
        remote_name: str = "origin",
    ) -> bool:
        """Add a remote to the repository.

        Args:
            org_slug: Organization slug
            remote_url: Remote URL (SSH or HTTPS)
            remote_name: Name for the remote (default: origin)

        Returns:
            True if successful
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return False

        try:
            # Remove existing remote if present
            if remote_name in [r.name for r in repo.remotes]:
                repo.remotes.delete(remote_name)

            repo.remotes.create(remote_name, remote_url)
            return True
        except pygit2.GitError:
            return False

    def remove_remote(
        self,
        org_slug: str,
        remote_name: str = "origin",
    ) -> bool:
        """Remove a remote from the repository.

        Args:
            org_slug: Organization slug
            remote_name: Name of the remote to remove

        Returns:
            True if successful
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return False

        try:
            if remote_name in [r.name for r in repo.remotes]:
                repo.remotes.delete(remote_name)
                return True
            return False
        except pygit2.GitError:
            return False

    def get_remote_info(
        self,
        org_slug: str,
        remote_name: str = "origin",
    ) -> dict[str, Any] | None:
        """Get information about a remote.

        Args:
            org_slug: Organization slug
            remote_name: Name of the remote

        Returns:
            Dict with remote info or None if not found
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return None

        try:
            remote = repo.remotes[remote_name]
            return {
                "name": remote.name,
                "url": remote.url,
                "push_url": remote.push_url or remote.url,
            }
        except KeyError:
            return None

    def _create_ssh_callbacks(
        self,
        ssh_key: str | None = None,
    ) -> pygit2.RemoteCallbacks | None:
        """Create callbacks for SSH authentication.

        Args:
            ssh_key: SSH private key content (PEM format)

        Returns:
            RemoteCallbacks or None
        """
        if not ssh_key:
            return None

        # Write key to temporary file for pygit2
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".key") as f:
            f.write(ssh_key)
            key_path = f.name

        try:
            # Set proper permissions
            os.chmod(key_path, 0o600)

            # For SSH keys, we need to use the keypair callback
            keypair = pygit2.Keypair(
                username="git",
                pubkey=None,  # Public key will be derived
                privkey=key_path,
                passphrase="",
            )
            callbacks = pygit2.RemoteCallbacks(credentials=keypair)
            return callbacks
        finally:
            # Clean up temp file
            try:
                os.unlink(key_path)
            except OSError:
                pass

    def _create_https_callbacks(
        self,
        token: str | None = None,
        username: str = "oauth2",
    ) -> pygit2.RemoteCallbacks | None:
        """Create callbacks for HTTPS token authentication.

        Args:
            token: Personal access token
            username: Username (default: oauth2 for tokens)

        Returns:
            RemoteCallbacks or None
        """
        if not token:
            return None

        userpass = pygit2.UserPass(username, token)
        callbacks = pygit2.RemoteCallbacks(credentials=userpass)
        return callbacks

    def fetch_remote(
        self,
        org_slug: str,
        credential: str | None = None,
        credential_type: str = "https_token",
        remote_name: str = "origin",
    ) -> dict[str, Any]:
        """Fetch from remote repository.

        Args:
            org_slug: Organization slug
            credential: Credential value (token or SSH key)
            credential_type: Type of credential (https_token, ssh_key)
            remote_name: Name of the remote

        Returns:
            Dict with fetch results
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return {"success": False, "error": "Repository not found"}

        try:
            remote = repo.remotes[remote_name]

            # Create appropriate callbacks
            if credential_type == "ssh_key":
                callbacks = self._create_ssh_callbacks(credential)
            else:
                callbacks = self._create_https_callbacks(credential)

            # Fetch
            transfer_progress = remote.fetch(callbacks=callbacks)

            return {
                "success": True,
                "received_objects": transfer_progress.received_objects if transfer_progress else 0,
                "total_objects": transfer_progress.total_objects if transfer_progress else 0,
            }
        except pygit2.GitError as e:
            return {"success": False, "error": str(e)}

    def push_to_remote(
        self,
        org_slug: str,
        branch: str,
        credential: str | None = None,
        credential_type: str = "https_token",
        remote_name: str = "origin",
        force: bool = False,
    ) -> dict[str, Any]:
        """Push branch to remote repository.

        Args:
            org_slug: Organization slug
            branch: Branch name to push
            credential: Credential value
            credential_type: Type of credential
            remote_name: Name of the remote
            force: Force push (use with caution)

        Returns:
            Dict with push results
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return {"success": False, "error": "Repository not found"}

        try:
            remote = repo.remotes[remote_name]

            # Create callbacks
            if credential_type == "ssh_key":
                callbacks = self._create_ssh_callbacks(credential)
            else:
                callbacks = self._create_https_callbacks(credential)

            # Get current commit SHA before push
            try:
                local_branch = repo.branches[branch]
                commit_sha = str(local_branch.peel().id)
            except KeyError:
                return {"success": False, "error": f"Branch not found: {branch}"}

            # Build refspec
            refspec = f"+refs/heads/{branch}:refs/heads/{branch}" if force else f"refs/heads/{branch}:refs/heads/{branch}"

            # Push
            remote.push([refspec], callbacks=callbacks)

            return {
                "success": True,
                "branch": branch,
                "commit_sha": commit_sha,
                "forced": force,
            }
        except pygit2.GitError as e:
            return {"success": False, "error": str(e)}

    def pull_from_remote(
        self,
        org_slug: str,
        branch: str,
        credential: str | None = None,
        credential_type: str = "https_token",
        remote_name: str = "origin",
        author_name: str = "Documentation Service",
        author_email: str = "system@docservice.local",
    ) -> dict[str, Any]:
        """Pull changes from remote repository.

        Args:
            org_slug: Organization slug
            branch: Branch name to pull
            credential: Credential value
            credential_type: Type of credential
            remote_name: Name of the remote
            author_name: Author for merge commit if needed
            author_email: Author email for merge commit

        Returns:
            Dict with pull results
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return {"success": False, "error": "Repository not found"}

        try:
            # First fetch
            fetch_result = self.fetch_remote(
                org_slug, credential, credential_type, remote_name
            )
            if not fetch_result.get("success"):
                return fetch_result

            # Get remote branch ref
            remote_ref = f"{remote_name}/{branch}"
            try:
                remote_branch = repo.lookup_reference(f"refs/remotes/{remote_ref}")
                remote_commit = repo.get(remote_branch.target)
            except KeyError:
                return {"success": False, "error": f"Remote branch not found: {remote_ref}"}

            # Get local branch
            try:
                local_branch = repo.branches[branch]
                local_commit = local_branch.peel()
            except KeyError:
                return {"success": False, "error": f"Local branch not found: {branch}"}

            # Check merge analysis
            merge_result, _ = repo.merge_analysis(remote_commit.id)

            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return {"success": True, "message": "Already up to date", "updated": False}

            if merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                # Fast-forward merge
                local_branch.set_target(remote_commit.id)
                repo.checkout_head()
                return {
                    "success": True,
                    "message": "Fast-forward merge",
                    "updated": True,
                    "commit_sha": str(remote_commit.id),
                }

            # Need actual merge
            repo.merge(remote_commit.id)

            if repo.index.conflicts:
                conflict_files = [c[1].path for c in repo.index.conflicts if c[1]]
                repo.state_cleanup()
                return {
                    "success": False,
                    "error": "Merge conflicts detected",
                    "conflict_files": conflict_files,
                }

            # Create merge commit
            sig = self._get_signature(author_name, author_email)
            tree = repo.index.write_tree()
            merge_message = f"Merge {remote_ref} into {branch}"
            commit_id = repo.create_commit(
                "HEAD",
                sig,
                sig,
                merge_message,
                tree,
                [local_commit.id, remote_commit.id],
            )
            repo.state_cleanup()

            return {
                "success": True,
                "message": "Merge completed",
                "updated": True,
                "commit_sha": str(commit_id),
            }

        except pygit2.GitError as e:
            return {"success": False, "error": str(e)}

    def get_divergence(
        self,
        org_slug: str,
        branch: str,
        remote_name: str = "origin",
    ) -> dict[str, Any]:
        """Check how local and remote branches have diverged.

        Args:
            org_slug: Organization slug
            branch: Branch name
            remote_name: Name of the remote

        Returns:
            Dict with divergence info (ahead, behind counts)
        """
        repo = self.get_repo(org_slug)
        if not repo:
            return {"ahead": 0, "behind": 0, "error": "Repository not found"}

        try:
            # Get local branch commit
            local_branch = repo.branches[branch]
            local_commit = local_branch.peel()

            # Get remote branch commit
            remote_ref = f"refs/remotes/{remote_name}/{branch}"
            try:
                remote_branch = repo.lookup_reference(remote_ref)
                remote_commit = repo.get(remote_branch.target)
            except KeyError:
                return {"ahead": 0, "behind": 0, "diverged": False, "remote_exists": False}

            # Count commits ahead and behind
            ahead, behind = repo.ahead_behind(local_commit.id, remote_commit.id)

            return {
                "ahead": ahead,
                "behind": behind,
                "diverged": ahead > 0 and behind > 0,
                "remote_exists": True,
                "local_sha": str(local_commit.id),
                "remote_sha": str(remote_commit.id),
            }

        except pygit2.GitError as e:
            return {"ahead": 0, "behind": 0, "error": str(e)}

    def get_head_sha(self, org_slug: str) -> str | None:
        """Get current HEAD commit SHA.

        Args:
            org_slug: Organization slug

        Returns:
            SHA string or None
        """
        repo = self.get_repo(org_slug)
        if not repo or repo.head_is_unborn:
            return None

        try:
            return str(repo.head.peel().id)
        except pygit2.GitError:
            return None


# Singleton instance
_git_service: GitService | None = None


def get_git_service() -> GitService:
    """Get the Git service singleton."""
    global _git_service
    if _git_service is None:
        from src.config import get_settings
        settings = get_settings()
        _git_service = GitService(settings.git_repos_path)
    return _git_service
