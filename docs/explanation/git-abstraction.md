# Git Abstraction

This document explains how the platform translates user-facing actions into Git operations, keeping version control invisible to end users.

## Design Principle

Users never see Git concepts. The platform presents familiar document management actions — save, draft, publish — while Git provides the underlying version control, diffing, and merge infrastructure.

## Action-to-Operation Mapping

| User Action | What User Sees | Git Operation |
|-------------|---------------|---------------|
| Create page | "Page created" | `create_file()` → commit to main |
| Edit page | Auto-save indicator | `update_file()` → commit to main |
| Start change request | "Draft created" | `create_branch("draft/CR-{id}")` |
| Save draft | Auto-save indicator | Commit to draft branch |
| Submit for review | "Submitted" status badge | DB status change (branch unchanged) |
| Approve | "Approved" badge + signature | DB signature record |
| Make effective (publish) | "Published" status | `merge_branch()` → merge into main |
| View history | Timeline of changes | `get_file_history()` → commit log |
| View diff | Side-by-side comparison | Git diff between branches/commits |

## Repository Structure

Each organization has one Git repository. Content is organized by workspace and space:

```
{org-slug}/
├── README.md                          # Auto-generated on init
├── quality-management/
│   ├── tutorials/
│   │   ├── getting-started.json
│   │   └── first-document.json
│   ├── how-to-guides/
│   │   └── configure-approvals.json
│   └── reference/
│       └── api-endpoints.json
└── engineering/
    ├── tutorials/
    │   └── dev-setup.json
    └── reference/
        └── coding-standards.json
```

File path pattern: `{workspace-slug}/{space-slug}/{page-slug}.json`

Content is stored as JSON (TipTap document format), enabling structured diffs and programmatic manipulation.

## Branching Strategy

The platform uses a simple branching model:

```
main (effective content)
 ├── draft/CR-001 (change request 1)
 ├── draft/CR-002 (change request 2)
 └── draft/CR-003 (change request 3)
```

- **main** — Always contains the current effective version of all documents
- **draft/CR-{id}** — Each change request gets its own branch
- Branches are created from main and merged back into main on publish
- Branches are deleted after merge

## How Saves Work

When a user edits a page, the `GitService` handles persistence:

1. Content is serialized to JSON
2. The file is written to the working directory
3. The file is staged (`repo.index.add()`)
4. A commit is created with the author's name and email
5. The commit SHA is returned and stored in the page metadata

The `create_file()` and `update_file()` methods in `src/modules/content/git_service.py` handle this transparently.

If the content has not changed since the last save, `update_file()` detects this and returns the existing HEAD SHA without creating a new commit. This prevents commit noise from no-op saves.

## How Merges Work

When a document is made effective:

1. The platform checks for merge conflicts via `check_merge_conflicts()`
2. If no conflicts, `merge_branch()` performs a `--no-ff` merge into main
3. The merge commit records the approver's identity
4. The draft branch is deleted via `delete_branch()`
5. The page status is updated to "Effective" in the database

If conflicts are detected (another change to the same file was published while the draft was open), the UI presents the conflicts for manual resolution before merging.

## Remote Synchronization

Organizations can optionally sync their Git repository with a remote (GitHub, GitLab, Gitea, or custom):

- **Push-only** — Local changes push to remote (backup/mirror)
- **Pull-only** — Remote changes pull into local (external source of truth)
- **Bidirectional** — Changes flow both ways (collaborative)

Remote operations use credential storage (encrypted) and support both HTTPS tokens and SSH keys. See [MCP Integration](../how-to/mcp-integration.md) for service account setup.

## Why This Approach?

### Advantages

1. **Full history without custom code** — Git's commit log provides complete version history
2. **Integrity by default** — Every commit has a SHA hash, providing content integrity verification
3. **Branching is free** — Concurrent change requests don't interfere with each other
4. **Diffing is solved** — Git's diff engine handles content comparison
5. **Air-gap friendly** — Works entirely offline, can sync when connected
6. **Portability** — Repositories can be cloned, backed up, or migrated with standard Git tools

### Tradeoffs

1. **Binary files** — Git is not ideal for large binaries (attachments use a separate storage backend)
2. **Query limitations** — Content queries go through PostgreSQL metadata, not Git
3. **Complexity** — The Git abstraction layer adds a translation step between user actions and storage
4. **Single-org repos** — Each organization has its own repository, limiting cross-org operations
