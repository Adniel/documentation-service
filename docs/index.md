# Documentation Service Platform

Welcome to the Documentation Service Platform — a Diataxis-based documentation system with ISO/GxP document control, Git-based version management, and integrated learning.

## Tutorials

Step-by-step lessons to get you started:

- [Getting Started](tutorials/getting-started.md) — Account setup, first login, navigating the UI
- [Create Your First Document](tutorials/create-first-document.md) — Organization, workspace, space, and page flow
- [Approval Workflow](tutorials/approval-workflow.md) — Submit, review, approve, and make documents effective
- [Training and Assessments](tutorials/training-and-assessments.md) — Set up assessments and document acknowledgments

## How-to Guides

Task-oriented instructions for specific goals:

- [Document Numbering](how-to/document-numbering.md) — Configure SOP-QMS-001 style numbering
- [Retention Policies](how-to/retention-policies.md) — Set retention periods and disposition methods
- [Publishing Sites](how-to/publishing-sites.md) — Create sites, apply themes, custom domains
- [Attachments and Media](how-to/attachments-and-media.md) — Upload files, manage media, inline images
- [MCP Integration](how-to/mcp-integration.md) — Service accounts and MCP tool exposure
- [Import and Export](how-to/import-export.md) — Export ZIP bundles, import Markdown and Confluence content

## Reference

Technical specifications and API documentation:

### API Endpoints

- [Authentication](reference/api/authentication.md) — `/auth/*` endpoints
- [Content](reference/api/content.md) — `/content/*`, `/spaces`, `/workspaces`, `/organizations`
- [Document Control](reference/api/document-control.md) — `/document-control/*` lifecycle, numbering, retention
- [Signatures](reference/api/signatures.md) — `/signatures/*` challenge, sign, verify
- [Audit](reference/api/audit.md) — `/audit/*` events, export, verification
- [Learning](reference/api/learning.md) — `/learning/*` assessments, assignments, attempts
- [Attachments](reference/api/attachments.md) — `/attachments/*` upload, download, list

### Platform Reference

- [Configuration](reference/configuration.md) — All environment variables and settings
- [Permissions](reference/permissions.md) — Role hierarchy, classification levels, ACLs
- [Compliance Matrix](reference/compliance-matrix.md) — Feature mapping to ISO 9001/13485 and 21 CFR Part 11

## Explanation

Background knowledge and design rationale:

- [Architecture](explanation/architecture.md) — Three-layer architecture and module boundaries
- [Git Abstraction](explanation/git-abstraction.md) — How user actions map to Git operations
- [Compliance Approach](explanation/compliance-approach.md) — Why e-signatures and hash chains work this way
- [Security Model](explanation/security-model.md) — Dual-dimension access control model
