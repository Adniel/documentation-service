# Documentation Service Platform Specification

**A Diátaxis-Based Documentation Platform with ISO/GxP Document Control & Git-Based Architecture**

Version 3.6 | December 2025

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision & Goals](#2-vision--goals)
3. [Diátaxis Framework Integration](#3-diátaxis-framework-integration)
4. [Core Features](#4-core-features)
5. [AI & Collaboration](#5-ai--collaboration)
   - 5.2 [Bidirectional MCP Integration](#52-bidirectional-mcp-integration)
6. [Document Control Module (ISO/GxP)](#6-document-control-module-isogxp)
7. [Technical Architecture (Git-Based Versioning)](#7-technical-architecture-git-based-versioning)
   - 7.14 [Access Control Model](#714-access-control-model)
   - 7.15 [Document Masking](#715-document-masking-redaction-for-broader-access)
   - 7.16 [Multi-Language Support](#716-multi-language-support)
8. [Learning & Assessment Module](#8-learning--assessment-module)
   - 8.1 [Overview](#81-overview)
   - 8.2 [Approval-Integrated Assessment](#82-approval-integrated-assessment)
   - 8.3 [AI-Generated Questions with Multi-Source Support](#83-ai-generated-questions-with-multi-source-support)
   - 8.4 [Standalone Learning Platform](#84-standalone-learning-platform)
   - 8.5 [User Experience](#85-user-experience)
   - 8.6 [Administration](#86-administration)
   - 8.7 [Architecture](#87-architecture)
   - 8.8 [Compliance & Reporting](#88-compliance--reporting)
9. [Publishing, API Docs, Analytics](#9-publishing-api-docs-analytics)
   - 9.4 [Platform as MCP Server](#94-platform-as-mcp-server)
10. [Integrations & Enterprise](#10-integrations--enterprise)
    - 10.2 [MCP Integration (Bidirectional)](#102-mcp-integration-bidirectional)
- [Appendix A: Diátaxis Quick Reference](#appendix-a-diátaxis-quick-reference)
- [Appendix B: Document Control Compliance Matrix](#appendix-b-document-control-compliance-matrix)
- [Appendix C: Git Abstraction Complete Mapping](#appendix-c-git-abstraction-complete-mapping)

---

## 1. Executive Summary

This specification defines a modern documentation platform combining GitBook-style features with the Diátaxis framework. The platform enables teams to create, manage, and publish technical documentation that serves users at every stage—from learning to doing to understanding.

### Version 3.6 Highlights

- **Diátaxis Framework**: Content organized into Tutorials, How-to Guides, Reference, and Explanation
- **Document Control Module**: ISO 9001, ISO 13485, FDA 21 CFR Part 11 compliance with electronic signatures and audit trails
- **Git-Based Architecture**: Version control built on Git for integrity, history, and multi-remote backup—with all complexity hidden from non-technical users
- **Application-Managed Approvals**: Approval workflows operate entirely within the platform, with no dependency on external Git hosting services (GitHub/GitLab are optional)
- **Dual-Dimension Access Control**: Hierarchical permissions combined with classification-based restrictions for granular, compliance-ready access management
- **AI-Assisted Document Masking**: Create redacted versions of classified documents for broader distribution, with AI suggesting sensitive content and human approval required before publication
- **Learning & Assessment Module**: Integrated training with AI-generated questions from multiple sources (documents, external links, MCP servers), approval-gated assessments, learning tracks, and compliance reporting
- **Bidirectional MCP Integration**: Platform both consumes external MCP servers and exposes itself as an MCP server for enterprise AI agents, support bots, and partner systems
- **Multi-Language Support**: System UI and content localization, AI-assisted translation with clear review status indicators, configurable language fallback, and language-aware workflows

---

## 2. Vision & Goals

To create a documentation platform that makes excellent documentation achievable for every team, embedding best practices into tooling while serving regulated industries requiring formal document control.

### 2.1 Primary Goals

1. Enable documentation aligned with the Diátaxis framework
2. Provide world-class editing for technical and non-technical users
3. Support docs-as-code workflows with Git integration
4. Leverage AI for content creation and quality assurance
5. Deliver ISO/GxP-compliant document control
6. Build on Git for proven versioning with vendor independence
7. Operate independently of external services (air-gap compatible)

---

## 3. Diátaxis Framework Integration

The platform is built around the Diátaxis documentation framework, which organizes content into four quadrants based on user needs and content purpose.

| Type | Purpose | User Need | Characteristics |
|------|---------|-----------|-----------------|
| **Tutorials** | Learning-oriented | "I want to learn" | Step-by-step, hands-on, safe to fail |
| **How-to Guides** | Task-oriented | "I want to do X" | Problem-focused, practical, assumes knowledge |
| **Reference** | Information-oriented | "I need to look up Y" | Accurate, complete, structured, dry |
| **Explanation** | Understanding-oriented | "I want to understand" | Contextual, conceptual, discursive |

### Platform Support

- **Content Type Templates**: Pre-built templates for each Diátaxis type with guidance
- **Type Tagging**: Metadata system to classify content by Diátaxis type
- **Navigation Modes**: Filter/browse by content type
- **Quality Linting**: AI-powered suggestions when content mixes types inappropriately
- **Coverage Analysis**: Dashboard showing documentation coverage across all four quadrants

---

## 4. Core Features

### 4.1 Block-Based Editor

A modern block-based editor combining WYSIWYG simplicity with structured content power.

**Block Types**: Paragraphs, Headings (H1-H6), Code blocks with syntax highlighting, Tables, Images, Callouts/hints, Expandable sections, Tabs, Steppers, Cards, Embedded content, Mathematical equations (LaTeX), Diagrams (Mermaid, PlantUML)

**Editing Capabilities**: Markdown shortcuts, slash commands, drag-and-drop, multi-block selection, copy/paste with formatting, real-time collaboration, offline mode with sync

### 4.2 Content Organization

- **Hierarchy**: Organization → Workspace → Space → Section → Page Group → Page
- **Navigation**: Sidebar TOC, breadcrumbs, section anchors, full-text search

### 4.3 Content Reusability

Reusable blocks, variables, snippets, templates, content variants

### 4.4 Version Control

Change requests (Git branches abstracted), diff view, merge rules, complete version history (Git log), restore previous versions

---

## 5. AI & Collaboration

### 5.1 AI Capabilities

The platform provides unified AI services across multiple domains:

| Domain | Capabilities |
|--------|--------------|
| **Writing Assistant** | Generation, rewriting, translation, grammar checking |
| **Documentation Agent** | Monitors for staleness, learns from support tickets, suggests improvements |
| **Reader Assistant** | Embedded chatbot, natural language Q&A, context-aware help |
| **Document Masking** | Sensitive content detection, redaction suggestions (see §7.15) |
| **Learning & Assessment** | Question generation, adaptive difficulty, knowledge gap analysis (see §8) |
| **Translation** | AI-assisted translation with mandatory review status indicators (see §7.16) |
| **AI-Optimized Publishing** | llms.txt generation, semantic search indexing |

### 5.2 Bidirectional MCP Integration

The platform supports Model Context Protocol (MCP) in both directions—as a **client** consuming external knowledge sources, and as a **server** exposing documentation to external AI systems.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│    EXTERNAL MCP SERVERS                 DOCUMENT SERVICE PLATFORM       │
│    (Platform as Client)                                                 │
│                                                                         │
│    ┌─────────────────┐                 ┌─────────────────────────────┐  │
│    │ Company Wiki    │────────────────►│                             │  │
│    ├─────────────────┤                 │    MCP CLIENT               │  │
│    │ Regulatory DB   │────────────────►│    (Consuming)              │  │
│    ├─────────────────┤                 │                             │  │
│    │ HR System       │────────────────►│                             │  │
│    └─────────────────┘                 └──────────────┬──────────────┘  │
│                                                       │                 │
│                                                       ▼                 │
│                                        ┌─────────────────────────────┐  │
│                                        │   PLATFORM CORE             │  │
│                                        │   • Documents & Content     │  │
│                                        │   • Learning & Training     │  │
│                                        │   • Access Control          │  │
│                                        └──────────────┬──────────────┘  │
│                                                       │                 │
│                                                       ▼                 │
│    EXTERNAL CONSUMERS                  ┌─────────────────────────────┐  │
│    (Platform as Server)                │                             │  │
│                                        │    MCP SERVER               │  │
│    ┌─────────────────┐                 │    (Exposing)               │  │
│    │ Enterprise AI   │◄────────────────│                             │  │
│    ├─────────────────┤                 │                             │  │
│    │ Support Bot     │◄────────────────│                             │  │
│    ├─────────────────┤                 │                             │  │
│    │ Dev Copilot     │◄────────────────│                             │  │
│    └─────────────────┘                 └─────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 5.2.1 MCP Client (Consuming External Sources)

AI features can draw from multiple external knowledge sources:

| Source Type | Description | Use Cases |
|-------------|-------------|-----------|
| **Platform Documents** | Any document the user has access to | Question generation, cross-referencing |
| **External URLs** | Web pages, PDFs, external documentation | Regulatory references, vendor docs |
| **MCP Servers** | Model Context Protocol integrations | Company wikis, databases, APIs |

**Example MCP Server Configurations**:

| Server | Purpose | Example Queries |
|--------|---------|-----------------|
| Company Wiki | Internal knowledge base | "What is our return policy?" |
| Regulatory DB | Compliance requirements | "FDA 21 CFR Part 11 signature requirements" |
| HR System | Employee/role data | "Who needs to complete this training?" |
| Product Database | Product specifications | "What are the specs for Model X?" |

#### 5.2.2 MCP Server (Exposing Platform Content)

The platform exposes its content as an MCP server, allowing external AI systems to query documentation with full access control enforcement. See §9.4 for detailed specification.

### 5.3 Collaboration

- **Team Features**: Real-time presence, comments, mentions, notifications, tasks
- **Git Integration**: Optional bidirectional sync with GitHub/GitLab, PR workflows, monorepo support
- **Access Control**: Roles (Owner, Admin, Editor, Reviewer, Viewer)

---

## 6. Document Control Module (ISO/GxP)

Formal document control for regulated industries.

### 6.1 Regulatory Framework Support

ISO 9001:2015, ISO 13485:2016, FDA 21 CFR Part 11, EU Annex 11, ISO 27001, AS9100D, IATF 16949

### 6.2 Key Capabilities

| Capability | Description |
|------------|-------------|
| **Document Identification** | Auto-numbering (e.g., SOP-QMS-001), revision tracking, metadata schema |
| **Lifecycle Management** | Draft → In Review → Approved → Effective → Obsolete → Archived |
| **Electronic Signatures** | 21 CFR Part 11 compliant with re-authentication, meaning, timestamp, content hash |
| **Approval Workflows** | Configurable routing, approval matrix, escalation (application-managed) |
| **Periodic Review** | Scheduled reviews, automatic reminders, overdue escalation |
| **Change Control** | Revision reasons, change summaries, version comparison |
| **Audit Trail** | Immutable, timestamped, searchable, exportable event log |
| **Training & Acknowledgment** | Comprehension verification, quizzes, training matrix (see §8 for full Learning Module) |
| **Retention & Disposition** | Configurable policies, legal hold, disposition certificates |

### 6.3 Document Control Roles

- **Document Controller**: Manage numbering, configure workflows, run reports
- **Quality Manager**: Final approval authority, override capabilities, audit access
- **Author**: Create/edit documents, submit for review
- **Reviewer**: Review assigned documents, add comments, approve/request changes
- **Approver**: Apply electronic signature for final approval
- **Reader**: View effective documents, acknowledge training
- **Auditor**: Read-only access to all documents, audit trails, reports

---

## 7. Technical Architecture (Git-Based Versioning)

The platform uses Git as the foundational version control layer. This provides proven versioning, content integrity, complete history, and vendor independence—while an application layer abstracts all Git complexity from end users.

### 7.1 Three-Layer Architecture

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| **Content Layer** | Git Repository | Document content (Markdown/MDX), assets, version history, branching |
| **Metadata Layer** | PostgreSQL | Document metadata, workflow state, permissions, e-signatures, training |
| **Audit Layer** | Append-Only Store | Immutable audit trail, compliance events, tamper-evident logging |

### 7.2 Why Git as Foundation

| Git Capability | Document Control Benefit |
|----------------|-------------------------|
| Content-addressable storage (SHA) | Cryptographic integrity—proves content hasn't been tampered with |
| Complete history with diffs | Full change tracking with before/after for any revision |
| Branching model | Natural fit for change requests, drafts, parallel editing |
| Atomic commits | Each save is a discrete, traceable unit with author/timestamp |
| Distributed architecture | Multiple remotes for redundancy, DR, offline operation |
| Signed commits (GPG) | Cryptographic proof of authorship for high-assurance environments |
| Proven at scale | Battle-tested by millions of projects; known performance characteristics |

### 7.3 Git Abstraction Layer

Users work with intuitive concepts; the platform translates these to Git operations transparently. Non-technical users never see branches, commits, or merge conflicts.

| User Action | Git Implementation | User Sees |
|-------------|-------------------|-----------|
| Create draft | `git checkout -b draft/CR-xxx` | "Draft created" |
| Save changes | `git add && git commit` (auto) | Auto-save indicator |
| Submit for review | Record in DB; no Git op needed | "Submitted" |
| View changes | `git diff main...branch` | Visual diff highlighting |
| Approve | Record in DB with e-signature | "Approved" badge |
| Publish/merge | `git merge --no-ff` | "Published" |
| View history | `git log --follow` | Timeline with versions |
| Compare versions | `git diff sha1..sha2` | Side-by-side view |
| Restore version | `git checkout <sha> -- file` | "Restored to v.X" |
| Resolve conflict | UI-guided merge resolution | "Choose version" dialog |

#### 7.3.1 What Users Never See

- Branch names, SHA hashes, commit IDs, staging area
- Command line, rebase, cherry-pick, reset
- Merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Force push, detached HEAD, or error states

#### 7.3.2 Technical User Access (Optional)

For technical users who prefer Git workflows:

- **Git Sync**: Bidirectional sync with external GitHub/GitLab repos
- **Clone URL**: Direct Git access for IDE editing
- **PR Integration**: Change requests can sync with GitHub/GitLab PRs/MRs
- **CI/CD Hooks**: Webhooks on Git events for automation

### 7.4 Application-Managed Approval Workflows

> **Key Architectural Decision**: Approval workflows are managed entirely within the application layer, not dependent on GitHub/GitLab Pull Requests or Merge Requests.

#### 7.4.1 Why Application-Managed Approvals

Pull Requests (GitHub) and Merge Requests (GitLab) are platform features built on top of Git, not native Git capabilities. For a platform targeting regulated industries, approvals must live in the application layer because:

1. **No external dependencies** — Works with bare Git repos on local filesystem or NFS
2. **Air-gap compatible** — No network calls to external services required
3. **21 CFR Part 11 compliant** — GitHub/GitLab approvals don't satisfy e-signature requirements (no re-authentication, no signature meaning, no trusted timestamp)
4. **Custom approval matrices** — Enforce rules like "2 reviewers + QA Manager" that PRs can't express
5. **Integrated audit trail** — Approvals logged alongside all other document events
6. **Consistent UX** — Non-technical users see the same interface regardless of Git backend

#### 7.4.2 Approval Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Change Request System                   │    │
│  │  • Create change request (DB record)                │    │
│  │  • Assign reviewers (DB)                            │    │
│  │  • Track approvals + e-signatures (DB)              │    │
│  │  • Enforce approval matrix (application logic)      │    │
│  │  • Trigger merge when approved (calls Git)          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      GIT LAYER (Local)                       │
│  • Branch created: draft/CR-2025-0042                       │
│  • Commits accumulated during editing                        │
│  • Diff generated: git diff main...draft/CR-2025-0042       │
│  • Merge executed: git merge --no-ff (after approval)       │
│  • Branch deleted post-merge                                 │
└─────────────────────────────────────────────────────────────┘
```

#### 7.4.3 Approval Workflow Steps

| Step | Application Action | Git Operation | Database Action |
|------|-------------------|---------------|-----------------|
| Author starts edit | Create ChangeRequest | `git checkout -b draft/CR-xxx` | Insert CR record |
| Author saves work | — | `git commit` | Update CR timestamp |
| Author submits | Notify reviewers | — | Set status = "In Review" |
| Reviewer views diff | Render diff UI | `git diff main...branch` | Log access event |
| Reviewer comments | — | — | Store comment |
| Reviewer approves | Capture e-signature | — | Store signature with meaning, timestamp, hash |
| All approvals complete | Check matrix | — | Validate requirements met |
| System merges | — | `git merge --no-ff` | Set status = "Merged" |
| Document effective | — | (optionally tag) | Set status = "Effective" |

#### 7.4.4 Optional GitHub/GitLab Integration

If an organization wants to use GitHub/GitLab (e.g., developers prefer that workflow), the platform offers **optional sync**:

```
┌──────────────┐     bidirectional      ┌──────────────┐
│   Platform   │◄──────────────────────►│   GitHub/    │
│   Git Repo   │         sync           │   GitLab     │
└──────────────┘                        └──────────────┘
       │                                       │
       │ application                           │ PR/MR
       │ approvals                             │ approvals
       │ (AUTHORITATIVE)                       │ (informational)
       ▼                                       ▼
┌──────────────┐                        ┌──────────────┐
│  Compliance  │                        │  Developer   │
│  Signatures  │                        │  Convenience │
└──────────────┘                        └──────────────┘
```

**Integration Rules**:
- Platform approval system is **authoritative** for compliance
- GitHub/GitLab PRs are a **convenience** for technical users
- Merges only occur when platform approval requirements are satisfied
- PR approval status is informational only; it does not satisfy regulatory requirements
- Sync can be disabled for air-gapped deployments

### 7.5 Multi-Remote Architecture

Git's distributed nature enables flexible backup, geographic distribution, and vendor independence.

| Remote | Purpose | Configuration |
|--------|---------|---------------|
| **Primary** | Main working repository | Platform-managed (local/NFS) or self-hosted (Gitea) |
| **Backup** | Real-time redundancy | Different storage system or region |
| **Archive** | Long-term retention | Cold storage (S3/Glacier, Azure Blob, tape) |
| **Air-gapped** | Isolated environments | On-premise mirror for secure/classified environments |
| **External Sync** | Developer convenience | GitHub/GitLab (optional, non-authoritative) |

**Benefits**:
- **Disaster Recovery**: Full content recovery from any remote
- **Vendor Independence**: Not locked into any Git hosting provider
- **Geographic Distribution**: Data residency compliance
- **Offline Operation**: Air-gapped environments operate independently
- **Regulatory Archive**: Long-term retention in compliant storage

### 7.6 Repository Structure

Each Space maps to a Git repository:

```
space-repository/
├── .docservice/              # Platform configuration
│   ├── config.yaml           # Space settings, navigation
│   └── variables.yaml        # Reusable variables
├── docs/                     # Documentation content
│   ├── tutorials/            # Diátaxis: Tutorials
│   ├── how-to/               # Diátaxis: How-to Guides
│   ├── reference/            # Diátaxis: Reference
│   └── explanation/          # Diátaxis: Explanation
├── assets/                   # Images, files (Git LFS)
└── SUMMARY.md                # Table of contents
```

**Content Format**:
- **Markdown/MDX**: Documents stored as Markdown with MDX extensions
- **YAML Frontmatter**: Document metadata in file header
- **Git LFS**: Large binary files managed via Git Large File Storage
- **Portable**: Content can be exported and used with any Markdown-compatible system

### 7.7 Metadata Database

While Git stores content, PostgreSQL stores everything else required for document control.

| Data Category | Stored Information |
|---------------|-------------------|
| **Document Metadata** | Doc number, revision, effective date, review date, type, owner, classification |
| **Workflow State** | Current status, assigned reviewers, due dates, approval history |
| **Electronic Signatures** | Signer ID, timestamp, meaning, linked Git SHA, content hash |
| **Permissions** | Document-level ACLs, role assignments, access grants |
| **Training Records** | Acknowledgments, quiz results, assignments, completion status |
| **Relationships** | Links to CAPAs, change controls, related documents |

**Git-Database Linkage**: Database records reference Git commit SHA. Electronic signatures store the exact SHA that was signed plus a content hash (SHA-256) for independent verification.

### 7.8 Audit Trail Architecture

Events from both Git and application layer combine into a unified, immutable log.

| Source | Events Captured | Enrichment |
|--------|-----------------|------------|
| Git Repository | Commits, merges, branch ops | User ID, doc ID, change summary |
| Workflow Engine | Status transitions, approvals | Signature details, comments |
| Signature Service | E-signatures applied | Meaning, timestamp, content hash |
| Access Control | View, download, print, ACL changes | User context, IP address |
| Training Module | Acknowledgments, quiz completions | Score, attempts, time spent |

**Audit Log Properties**:
- **Append-Only**: Records can only be added, never modified or deleted
- **Cryptographically Chained**: Each record includes hash of previous (blockchain-like integrity)
- **Timestamped**: Trusted NTP source, UTC timezone
- **Separately Stored**: Dedicated storage, separate from content and metadata databases
- **Retained Per Policy**: Configurable retention, typically exceeding content retention

### 7.9 Real-Time Collaboration

Git doesn't support real-time collaboration natively. The platform implements a CRDT-based layer that syncs to Git.

1. **Real-Time Layer**: CRDT (Yjs) for live editing with cursor presence
2. **Periodic Sync**: Changes committed to Git on inactivity (e.g., 30 seconds)
3. **Explicit Save**: User-triggered save creates immediate Git commit
4. **Conflict Resolution**: CRDT handles concurrent edits; Git merges via UI if needed
5. **Offline Mode**: Local cache, queue changes, sync on reconnect

### 7.10 Electronic Signatures Integration

Git commits alone don't satisfy 21 CFR Part 11. A separate signature layer links to Git content.

**Signature Process**:

1. **Content Freeze**: Document locked; Git commit SHA recorded
2. **Content Hash**: SHA-256 of document content computed
3. **Re-Authentication**: User re-enters password (+ MFA if configured)
4. **Meaning Capture**: User selects meaning (Approved, Reviewed, Authored, etc.)
5. **Timestamp**: Server timestamp from trusted NTP source
6. **Record Creation**: Signature stored in DB with all elements
7. **Audit Log**: Event written to immutable trail

**Signature Record Contains**:
- User ID (linked to validated identity via SSO)
- Full name and title at time of signature
- Signature meaning
- Timestamp (UTC from trusted source)
- Git commit SHA of signed content
- Content hash (SHA-256)
- Authentication method used
- Optional comment/reason

### 7.11 Implementation Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Git Library | libgit2 / isomorphic-git | Embedded Git without CLI dependency |
| Git Hosting | Local filesystem, Gitea, or optional GitHub/GitLab | Flexible deployment, no external dependency required |
| Database | PostgreSQL | ACID compliance, JSON support, proven reliability |
| Audit Log | TimescaleDB or dedicated append-only store | Immutable, time-series optimized |
| Real-Time Sync | Yjs (CRDT) | Proven collaborative editing library |
| Binary Storage | Git LFS + S3-compatible storage | Efficient large file handling |
| Search | Elasticsearch / Meilisearch | Full-text search across content |
| Time Source | NTP with multiple sources + monitoring | Trusted timestamps for compliance |

### 7.12 Security

- **Encryption at Rest**: AES-256 for database, Git repositories, and backups
- **Encryption in Transit**: TLS 1.3 for all communications
- **Key Management**: HSM or cloud KMS for encryption keys
- **Authentication**: SSO/SAML integration, MFA support
- **Authorization**: Dual-dimension access control (see §7.14)
- **Git Access**: SSH keys or personal access tokens; no password authentication
- **Integrity**: Git SHA integrity, optional GPG signing, cryptographic audit chain

### 7.13 Performance & Scale

**Performance Targets**:
- Published page load: < 500ms (CDN-cached)
- Editor load: < 2 seconds
- Real-time sync latency: < 100ms
- Git operations: < 3 seconds
- Search results: < 500ms

**Scale Limits**:
- Documents per space: 10,000+
- Spaces per organization: 1,000+
- Concurrent editors per document: 50+
- Git history depth: Unlimited (with optimization for large repos)
- Audit log retention: 10+ years

### 7.14 Access Control Model

The platform implements a dual-dimension access control model combining **hierarchical permissions** (role-based, inherited through the content tree) with **classification-based restrictions** (clearance-based, independent of hierarchy). Both dimensions must grant access for a user to view or edit content.

#### 7.14.1 Hierarchical Permission Inheritance

Access control is hierarchical by default, cascading downward through the content structure:

```
Organization
    │
    ├─► Workspace
    │       │
    │       ├─► Space ◄─── User granted "Editor" here
    │       │     │
    │       │     ├─► Section ──► inherits Editor access
    │       │     │     │
    │       │     │     └─► Page ──► inherits Editor access
    │       │     │
    │       │     └─► Page ──► inherits Editor access
    │       │
    │       └─► Space ──► no access (different space)
    │
    └─► Workspace ──► no access (different workspace)
```

**Inheritance Rules**:
- A user with access to a Space can access all Sections and Pages within it (by default)
- Permissions flow downward only; child access never grants parent access
- Each level can **restrict** inherited permissions but not **expand** them

#### 7.14.2 Permission Levels

| Role | Capabilities |
|------|--------------|
| **Owner** | Full control including delete, transfer ownership, manage billing |
| **Admin** | Manage members, configure settings, all Editor capabilities |
| **Editor** | Create, edit, delete content; submit for review |
| **Reviewer** | View content, add comments, approve/reject change requests |
| **Viewer** | Read-only access to published/effective content |

#### 7.14.3 Document-Level Overrides

Permissions can be restricted (not expanded) at lower levels in the hierarchy:

| Scenario | Behavior |
|----------|----------|
| User has Space access, no document override | ✅ Access granted (inherited) |
| User has Space access, document restricts to specific users | ❌ Denied unless explicitly listed |
| User has no Space access, document grants access | ❌ Denied (cannot expand beyond parent) |
| User has Space Editor role, document restricts to Viewer | ✅ Access granted but limited to Viewer |

**Use Cases for Document-Level Restrictions**:
- Sensitive documents (CAPA records, audit findings) within a broader QMS space
- Draft documents visible only to authors until submitted
- Executive procedures within a department space
- Documents under legal hold with access frozen to specific users

#### 7.14.4 Classification-Based Restrictions

Classifications add a second, independent dimension of access control. Users must have both **hierarchical permission** AND **classification clearance** to access a document.

```
┌─────────────────────────────────────────────────────────────┐
│                     ACCESS DECISION                          │
│                                                              │
│   Hierarchical Permission    AND    Classification Clearance │
│   (Role in Space/Document)          (User's clearance level) │
│                                                              │
│              BOTH must be satisfied for access               │
└─────────────────────────────────────────────────────────────┘
```

**Default Classification Levels**:

| Level | Description | Typical Use |
|-------|-------------|-------------|
| **Public** | Anyone with space access | Published procedures, general guides, templates |
| **Internal** | All authenticated organization members | SOPs, work instructions, policies |
| **Confidential** | Specific departments or roles | HR policies, financial procedures, supplier info |
| **Restricted** | Named individuals only | CAPA records, audit findings, executive documents |

**Classification Evaluation**:

| Document Classification | User Clearance | Space Access | Result |
|------------------------|----------------|--------------|--------|
| Public | (any) | ✅ Viewer | ✅ Access |
| Internal | Internal | ✅ Viewer | ✅ Access |
| Internal | Public | ✅ Viewer | ❌ Denied (insufficient clearance) |
| Confidential | Internal | ✅ Editor | ❌ Denied (insufficient clearance) |
| Confidential | Confidential | ✅ Editor | ✅ Access |
| Restricted | Confidential | ✅ Editor | ❌ Denied (insufficient clearance) |
| Restricted | Restricted | ❌ None | ❌ Denied (no hierarchical access) |

#### 7.14.5 Classification Configuration

Organizations can customize classification schemes to match their requirements:

| Setting | Description |
|---------|-------------|
| **Custom levels** | Define organization-specific classification levels (e.g., ITAR, Export Controlled, Patient Data) |
| **Level hierarchy** | Configure clearance inheritance (e.g., Restricted clearance implies Confidential) |
| **Default classification** | Set Space-level default for new documents |
| **Mandatory classification** | Require classification before document can be published |
| **Classification elevation only** | Documents can be reclassified to higher levels only (cannot downgrade) |

#### 7.14.6 Classification Features for Regulated Industries

| Feature | Description |
|---------|-------------|
| **Classification inheritance** | New documents inherit Space default; can be elevated but not lowered without approval |
| **Classification change workflow** | Reclassification requires approval and generates audit entry with reason |
| **Clearance expiration** | Temporary clearance grants with automatic revocation date |
| **Need-to-know enforcement** | For highest levels, require explicit document-level grant even with clearance |
| **Clearance by role** | Assign clearance levels to roles (e.g., "Quality Manager" role includes Confidential clearance) |
| **Clearance by group** | Assign clearance to groups (e.g., "Executive Team" group has Restricted clearance) |
| **Watermarking** | PDFs and prints display classification level; configurable per level |
| **Access logging** | All access to Confidential and above is logged with user, timestamp, and action |

#### 7.14.7 Access Control Scenarios

| Scenario | Configuration |
|----------|---------------|
| QMS Space with sensitive CAPA records | Space: Quality team (Editor); CAPA folder: Restricted classification + named approvers |
| Training materials with draft versions | Published docs: Public; Drafts: Confidential (Training Admins only) |
| Audit findings visible only to auditors | Classification: Restricted; Clearance granted to Auditor role |
| Department space with executive procedures | Space: Department (Editor); Executive docs: Restricted + named executives |
| Supplier-facing documentation | Classification: External; shared via controlled access links with expiration |
| Multi-site organization | Clearance by site group; documents classified by site applicability |
| Contract-specific documentation | Custom classification per contract; clearance granted to project team |

#### 7.14.8 Access Control in Document Lifecycle

Classification interacts with document lifecycle:

| Lifecycle State | Access Behavior |
|-----------------|-----------------|
| **Draft** | Author + explicitly granted users only (regardless of classification) |
| **In Review** | Author + assigned reviewers + classification clearance |
| **Approved** | Per classification and hierarchical permissions |
| **Effective** | Per classification and hierarchical permissions |
| **Obsolete** | Hidden by default; accessible to Admins + Document Controllers |
| **Archived** | Read-only; per classification; may require elevated clearance |

#### 7.14.9 Access Control Audit

All access control events are logged:

| Event | Logged Information |
|-------|-------------------|
| Permission granted/revoked | User, target user, permission level, scope, timestamp, granted by |
| Clearance granted/revoked | User, clearance level, expiration (if any), granted by, reason |
| Classification changed | Document, old level, new level, changed by, reason, approval reference |
| Access denied | User, document, reason (permission or clearance), timestamp |
| Document accessed | User, document, action (view/download/print), timestamp, IP address |
| Override applied | Document, restriction type, affected users, applied by |

### 7.15 Document Masking (Redaction for Broader Access)

The platform provides AI-assisted document masking to create redacted versions of classified documents that can be shared with users who lack clearance for the original. This enables broader information sharing while protecting sensitive content.

#### 7.15.1 Concept Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ORIGINAL DOCUMENT                                 │
│                    Classification: Restricted                            │
│                                                                          │
│  "The investigation found that [PATIENT NAME: John Smith] was           │
│   prescribed [MEDICATION: Oxycodone 40mg] by Dr. [PHYSICIAN: Jane Doe]  │
│   on [DATE: 2024-03-15]. The total cost was [AMOUNT: $4,250.00]."       │
│                                                                          │
│                    Accessible to: Named individuals only                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ AI-assisted masking
┌─────────────────────────────────────────────────────────────────────────┐
│                        MASKED VERSION                                    │
│                    Classification: Internal                              │
│                                                                          │
│  "The investigation found that [REDACTED] was prescribed [REDACTED]     │
│   by Dr. [REDACTED] on [REDACTED]. The total cost was [REDACTED]."      │
│                                                                          │
│                    Accessible to: All authenticated users                │
└─────────────────────────────────────────────────────────────────────────┘
```

A masked version is a **derived document** linked to the original, with sensitive information redacted. The masked version can have a lower classification, making it accessible to a broader audience while the original remains restricted.

#### 7.15.2 Masking Workflow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Document   │    │  AI Suggests │    │    Owner     │    │   Masked     │
│    Owner     │───►│   Masking    │───►│   Reviews    │───►│   Version    │
│   Initiates  │    │              │    │  & Approves  │    │  Published   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

**Detailed Steps**:

| Step | Actor | Action | System Behavior |
|------|-------|--------|-----------------|
| 1. Initiate | Document Owner | Requests masked version creation | Creates draft masked version linked to original |
| 2. Configure | Document Owner | Selects masking profile and target classification | Loads applicable masking rules |
| 3. Analyze | AI Service | Analyzes document content | Identifies sensitive content using NLP/NER |
| 4. Suggest | AI Service | Proposes redactions | Highlights suggested masks with confidence scores |
| 5. Review | Document Owner | Reviews each suggestion | Can accept, reject, or modify each mask |
| 6. Adjust | Document Owner | Adds manual masks if needed | Marks additional content for redaction |
| 7. Preview | Document Owner | Views final masked result | Renders document with all masks applied |
| 8. Approve | Document Owner | Approves masked version | Signs off with e-signature |
| 9. Verify | Quality/Compliance (optional) | Second review for sensitive documents | Additional approval for high-risk content |
| 10. Publish | System | Makes masked version effective | Masked version accessible per its classification |

#### 7.15.3 Sensitive Information Categories

The AI masking service recognizes multiple categories of sensitive information:

| Category | Examples | Detection Method |
|----------|----------|------------------|
| **Personal Identifiers** | Names, SSN, passport numbers, employee IDs | Named Entity Recognition (NER) |
| **Contact Information** | Addresses, phone numbers, email addresses | Pattern matching + NER |
| **Medical/Health** | Diagnoses, medications, patient records | Medical NER models + terminology |
| **Financial** | Account numbers, amounts, salaries, pricing | Pattern matching + context analysis |
| **Legal** | Case numbers, party names, witness information | Legal NER + document structure |
| **Technical** | IP addresses, credentials, API keys, source code | Pattern matching + code detection |
| **Organizational** | Internal project names, codenames, strategies | Custom dictionary + context |
| **Dates & Times** | Specific dates that could identify events | Contextual date detection |
| **Locations** | Addresses, facility names, GPS coordinates | Location NER + geocoding |
| **Custom** | Organization-defined sensitive terms | Configurable keyword lists |

#### 7.15.4 Masking Profiles

Organizations can define masking profiles for consistent redaction across document types:

| Profile | Target Documents | Auto-Mask Categories | Target Classification |
|---------|------------------|---------------------|----------------------|
| **Public Release** | Press releases, public reports | All PII, financial, internal refs | Public |
| **Internal Distribution** | Policies, procedures | Patient names, specific financials | Internal |
| **Regulatory Submission** | Audit responses | Trade secrets, strategic info | Confidential |
| **Legal Discovery** | Litigation documents | Privileged content, work product | As specified |
| **GDPR/Privacy** | Data subject requests | All personal data | Per request |
| **Custom** | Organization-defined | Configurable | Configurable |

#### 7.15.5 AI Masking Engine

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI MASKING SERVICE                          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    OCR      │  │    NLP      │  │   Named Entity          │  │
│  │  (images,   │  │  Pipeline   │  │   Recognition (NER)     │  │
│  │   scans)    │  │             │  │                         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                     │                 │
│         └────────────────┼─────────────────────┘                 │
│                          ▼                                       │
│                ┌─────────────────┐                               │
│                │  Sensitivity    │◄── Masking Profile            │
│                │  Classifier     │◄── Custom Dictionary          │
│                │                 │◄── Confidence Threshold       │
│                └────────┬────────┘                               │
│                         │                                        │
│                         ▼                                        │
│                ┌─────────────────┐                               │
│                │  Mask Proposal  │──► Suggestions with           │
│                │  Generator      │    confidence scores          │
│                └─────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

**AI Capabilities**:

| Capability | Description |
|------------|-------------|
| **Multi-format support** | PDF, DOCX, images (via OCR), Markdown, HTML |
| **Contextual understanding** | Distinguishes "John Smith (patient)" from "John Smith (author)" |
| **Confidence scoring** | Each suggestion includes confidence level (high/medium/low) |
| **Cross-reference detection** | Identifies the same entity mentioned multiple ways |
| **Table/structured data** | Handles sensitive data in tables and lists |
| **Consistent masking** | Same entity masked consistently throughout document |
| **Partial masking** | Can mask portions (e.g., "J*** S****" or "***-**-1234") |

#### 7.15.6 Masking Review Interface

The review interface enables document owners to efficiently review and approve AI suggestions:

**Features**:

| Feature | Description |
|---------|-------------|
| **Side-by-side view** | Original and masked version displayed together |
| **Highlight mode** | Suggested masks highlighted with category color coding |
| **Confidence indicators** | Visual indicator of AI confidence (green/yellow/red) |
| **Bulk actions** | Accept/reject all suggestions in a category |
| **Search sensitive** | Find all instances of a term to ensure consistent masking |
| **Manual mask tool** | Draw/select additional content to mask |
| **Mask type selector** | Choose redaction style (blackout, replacement text, partial) |
| **Preview toggle** | Switch between edit mode and final preview |
| **Audit comments** | Add justification for mask decisions |

#### 7.15.7 Redaction Styles

| Style | Appearance | Use Case |
|-------|------------|----------|
| **Blackout** | █████████ | Complete redaction, no hint of content |
| **Category label** | [PERSONAL NAME] | Indicates type of redacted content |
| **Partial mask** | J*** S**** | Preserves some information for context |
| **Replacement** | [Name 1], [Name 2] | Consistent pseudonyms throughout |
| **Length-preserving** | ████ ████████ | Preserves word/character count |

#### 7.15.8 Masked Version Management

**Relationship Model**:

```
┌─────────────────────┐
│  Original Document  │
│  (Restricted)       │
│  DOC-2024-0042 v2.1 │
└──────────┬──────────┘
           │ has masked versions
           │
     ┌─────┴─────┬─────────────────┐
     ▼           ▼                 ▼
┌──────────┐ ┌──────────┐    ┌──────────┐
│ Masked   │ │ Masked   │    │ Masked   │
│ Public   │ │ Internal │    │ Custom   │
│ v2.1-M1  │ │ v2.1-M2  │    │ v2.1-M3  │
└──────────┘ └──────────┘    └──────────┘
```

| Aspect | Behavior |
|--------|----------|
| **Version linkage** | Masked versions linked to specific original version |
| **Automatic invalidation** | When original is revised, masked versions marked "needs update" |
| **Independent lifecycle** | Masked version has own effective/obsolete status |
| **Access independence** | Users see only masked versions they have clearance for |
| **Audit linkage** | Full traceability from masked to original |

#### 7.15.9 Masking Policies

Organizations can enforce masking policies:

| Policy | Description |
|--------|-------------|
| **Mandatory for release** | Documents above certain classification require masked version for broader distribution |
| **Minimum review** | High-sensitivity documents require second reviewer |
| **Auto-expire masked versions** | Masked versions expire after configurable period |
| **Masking profile enforcement** | Certain document types must use specific masking profile |
| **AI-only restriction** | Prohibit publishing AI suggestions without human review |
| **Completeness check** | Warn if AI confidence is low on any detected entity |

#### 7.15.10 Masking Audit Trail

All masking activities are logged:

| Event | Logged Information |
|-------|-------------------|
| Masking initiated | Document, initiator, profile selected, timestamp |
| AI analysis completed | Document, entities detected, confidence scores, processing time |
| Suggestion accepted | Entity, category, mask style, reviewer |
| Suggestion rejected | Entity, category, rejection reason, reviewer |
| Manual mask added | Content masked, category, justification, reviewer |
| Masked version approved | Document, approver, e-signature, timestamp |
| Second review completed | Document, reviewer, decision, comments |
| Masked version published | Document, classification, accessible to |
| Masked version invalidated | Document, reason (original updated/manual), timestamp |

#### 7.15.11 Training and Improvement

The AI masking model improves over time:

| Mechanism | Description |
|-----------|-------------|
| **Feedback loop** | Accepted/rejected suggestions used as training signal |
| **Anonymized training** | Training data stripped of actual sensitive content |
| **Organization-specific tuning** | Model adapts to organization's document types and terminology |
| **False positive tracking** | Monitors over-masking to reduce unnecessary suggestions |
| **False negative tracking** | Monitors missed entities (reported post-publication) |
| **Confidence calibration** | Adjusts confidence thresholds based on reviewer decisions |

#### 7.15.12 Security Considerations

| Concern | Mitigation |
|---------|------------|
| **AI data leakage** | AI service runs on-premise or in isolated environment; no external API calls |
| **Training data exposure** | Only anonymized, approved data used for training |
| **Incomplete masking** | Mandatory human review; optional second reviewer for sensitive docs |
| **Mask reversal** | True redaction (content removed), not overlay; original content not in masked file |
| **Metadata leakage** | Document metadata also reviewed and masked if needed |
| **Version confusion** | Clear visual distinction between original and masked versions |

#### 7.15.13 Integration with Document Control

Masking integrates with the document control workflow:

| Integration Point | Behavior |
|-------------------|----------|
| **Approval workflow** | Masked version approval can require same or different approvers as original |
| **Electronic signatures** | Masked version approval captured with compliant e-signature |
| **Periodic review** | Masked versions included in review cycles |
| **Change control** | Original revision triggers masked version review |
| **Training acknowledgment** | Can require acknowledgment for either or both versions |
| **Distribution control** | Masked version distribution tracked separately |
| **Retention** | Masked version retention linked to original |

### 7.16 Multi-Language Support

The platform provides comprehensive multi-language support for both the system interface and document content, enabling global organizations to serve users in their preferred languages while maintaining content governance.

#### 7.16.1 Overview

| Aspect | Description |
|--------|-------------|
| **System UI** | Platform interface localizable to multiple languages |
| **Content** | Documents can be authored and maintained in multiple languages |
| **Fallback** | Configurable fallback language (default: English) when content unavailable |
| **AI Translation** | Automatic translation with mandatory review status indication |
| **Workflows** | Language-aware approval and review processes |

#### 7.16.2 System Localization

The platform interface supports multiple languages:

**Supported Elements**:

| Element | Localization |
|---------|--------------|
| Navigation & menus | Fully translated |
| Buttons & labels | Fully translated |
| System messages | Fully translated |
| Email notifications | Template-based, per user language preference |
| Error messages | Fully translated |
| Help content | Linked to language-specific documentation |
| Date/time formats | Locale-aware (e.g., DD/MM/YYYY vs MM/DD/YYYY) |
| Number formats | Locale-aware (e.g., 1,000.00 vs 1.000,00) |

**Configuration**:

```yaml
system_localization:
  default_language: "en"
  available_languages:
    - code: "en"
      name: "English"
      enabled: true
    - code: "sv"
      name: "Svenska"
      enabled: true
    - code: "de"
      name: "Deutsch"
      enabled: true
    - code: "fr"
      name: "Français"
      enabled: true
    - code: "es"
      name: "Español"
      enabled: true
  user_language_selection: true  # Users can choose their preferred language
  browser_detection: true        # Auto-detect from browser settings
```

#### 7.16.3 Content Language Model

Documents support multiple language variants:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT LANGUAGE MODEL                          │
│                                                                          │
│  Document: SOP-QMS-001 "Quality Management Procedure"                    │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  English (en)   │  │  Swedish (sv)   │  │  German (de)    │          │
│  │  [Primary]      │  │  [Translation]  │  │  [AI-Generated] │          │
│  │                 │  │                 │  │                 │          │
│  │  Status:        │  │  Status:        │  │  Status:        │          │
│  │  Effective      │  │  Effective      │  │  Draft          │          │
│  │                 │  │                 │  │                 │          │
│  │  Version: 2.1   │  │  Version: 2.1   │  │  Version: 2.1   │          │
│  │  Reviewed: Yes  │  │  Reviewed: Yes  │  │  Reviewed: No ⚠️│          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│  Fallback chain: User preference → Space default → Organization default │
└─────────────────────────────────────────────────────────────────────────┘
```

**Language Variant Properties**:

| Property | Description |
|----------|-------------|
| **Language code** | ISO 639-1 code (e.g., "en", "sv", "de") |
| **Variant type** | Primary, Human Translation, AI Translation |
| **Translation source** | Which language variant this was translated from |
| **Review status** | Reviewed, Unreviewed, Needs Update |
| **Translator** | User who created/reviewed translation (or "AI" for automatic) |
| **Last sync** | When translation was last synced with source |
| **Drift status** | Whether source has changed since translation |

#### 7.16.4 Language Fallback Configuration

When content is not available in a user's preferred language:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LANGUAGE FALLBACK CHAIN                           │
│                                                                          │
│  User requests document in: German (de)                                  │
│                                                                          │
│  1. Check: German version available?                                     │
│     └─► No                                                               │
│                                                                          │
│  2. Check: Space fallback language (Swedish) available?                  │
│     └─► No                                                               │
│                                                                          │
│  3. Check: Organization fallback language (English) available?           │
│     └─► Yes ✓                                                            │
│                                                                          │
│  Result: Show English version with notice:                               │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ ⓘ This document is not available in German.                     │    │
│  │   Showing English version. [Request Translation]                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Fallback Settings**:

| Level | Setting | Description |
|-------|---------|-------------|
| **Organization** | `default_content_language` | Ultimate fallback language |
| **Space** | `space_language` | Space-specific default |
| **User** | `preferred_language` | User's preferred content language |
| **Document** | `primary_language` | Authoritative language for document |

#### 7.16.5 AI Translation

The platform provides AI-assisted translation with mandatory transparency:

**AI Translation Workflow**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Source    │    │     AI      │    │   Review    │    │  Published  │
│   Content   │───►│  Translates │───►│  Required?  │───►│  (Status    │
│             │    │             │    │             │    │  Indicated) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                          ┌──────────────────┴──────────────────┐
                          ▼                                     ▼
                   ┌─────────────┐                       ┌─────────────┐
                   │  Reviewed   │                       │ Unreviewed  │
                   │  Human      │                       │ AI-Only     │
                   │  Approved   │                       │ ⚠️ Indicated │
                   └─────────────┘                       └─────────────┘
```

**Translation Status Indicators** (Mandatory Display):

| Status | Visual Indicator | Meaning |
|--------|------------------|---------|
| **Human Authored** | (none) | Content originally written in this language |
| **Human Translated** | 🌐 | Translated by human, reviewed and approved |
| **AI Translated + Reviewed** | 🌐 ✓ | AI translation, human reviewed and approved |
| **AI Translated (Unreviewed)** | ⚠️ 🤖 | AI translation, NOT reviewed — clearly indicated |

**Unreviewed AI Translation Display**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚠️ AUTOMATIC TRANSLATION                                               │
│                                                                         │
│  This content was automatically translated from English and has         │
│  NOT been reviewed for accuracy. For official information, please       │
│  refer to the English version.                                          │
│                                                                         │
│  [View Original (English)] [Report Translation Issue]                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Document content in translated language...]                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**AI Translation Configuration**:

| Setting | Description |
|---------|-------------|
| `ai_translation_enabled` | Enable/disable AI translation feature |
| `auto_translate_on_publish` | Automatically generate translations when primary is published |
| `require_review_for_effective` | AI translations cannot become Effective without review |
| `unreviewed_access` | Who can view unreviewed AI translations (all, internal, none) |
| `translation_notice_style` | Banner, watermark, or both |
| `source_link_required` | Always show link to source language version |

#### 7.16.6 Translation Workflow

**For Controlled Documents (Document Control Module)**:

| Step | Action | Result |
|------|--------|--------|
| 1. Source published | Primary language document becomes Effective | Triggers translation |
| 2. Translation created | AI generates or human authors translation | Draft status |
| 3. Review assigned | Translation assigned to qualified reviewer | In Review status |
| 4. Review completed | Reviewer approves or requests changes | Approved or Revision |
| 5. Approval | Translation approved (may require e-signature) | Effective status |
| 6. Source updated | Primary language document revised | Translation marked "Needs Update" |

**Translation Review Requirements**:

| Document Type | AI Translation Review | Human Translation Review |
|---------------|----------------------|--------------------------|
| **Controlled (ISO/GxP)** | Mandatory before Effective | Mandatory before Effective |
| **Internal** | Configurable | Configurable |
| **Public/Help** | Optional (can publish with warning) | Optional |

#### 7.16.7 Translation Status Tracking

**Document Translation Dashboard**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Translation Status: SOP-QMS-001 "Quality Management Procedure"         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Primary Language: English (v2.1, Effective)                            │
│                                                                         │
│  Language      Status          Type        Last Updated    Action       │
│  ─────────────────────────────────────────────────────────────────────  │
│  🇸🇪 Swedish    Effective       Human       2024-11-15      [View]       │
│  🇩🇪 German     Needs Update ⚠️  Human       2024-10-01      [Update]     │
│  🇫🇷 French     In Review       AI+Review   2024-11-20      [Review]     │
│  🇪🇸 Spanish    Unreviewed 🤖   AI-Only     2024-11-20      [Review]     │
│  🇯🇵 Japanese   Not Available   —           —               [Translate]  │
│                                                                         │
│  [Add Language] [Bulk AI Translate] [Export Translation Memory]         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Translation Drift Detection**:

When source content changes, translations are automatically flagged:

| Change Type | Translation Impact |
|-------------|-------------------|
| Minor edit (typo, formatting) | Flagged for optional review |
| Content change | Marked "Needs Update", may be hidden |
| Major revision | Translation marked obsolete until updated |

#### 7.16.8 Language in Git Repository

Language variants stored in the Git repository structure:

```
space-repository/
├── docs/
│   └── procedures/
│       └── quality-management/
│           ├── index.en.md         # English (primary)
│           ├── index.sv.md         # Swedish (human translated)
│           ├── index.de.md         # German (AI translated)
│           └── _translations.yaml  # Translation metadata
```

**Translation Metadata File**:

```yaml
# _translations.yaml
primary_language: en
translations:
  sv:
    type: human
    translator: "user:anna.svensson"
    reviewed_by: "user:erik.lindberg"
    reviewed_at: "2024-11-15T10:30:00Z"
    source_version: "abc123"  # Git SHA of source when translated
    status: effective
  de:
    type: ai
    model: "claude-3"
    generated_at: "2024-11-20T08:00:00Z"
    source_version: "abc123"
    reviewed: false
    status: draft
```

#### 7.16.9 Language-Specific Features

**Search**:

| Feature | Behavior |
|---------|----------|
| Language-specific search | Search within selected language |
| Cross-language search | Search across all languages with results grouped |
| Language boosting | Prefer results in user's preferred language |

**Publishing**:

| Feature | Behavior |
|---------|----------|
| Language selector | Readers can switch languages on published site |
| URL structure | `/en/docs/...` or `/docs/.../index.en` |
| SEO | Proper `hreflang` tags for search engines |
| Fallback display | Clear indication when showing fallback language |

**Notifications**:

| Feature | Behavior |
|---------|----------|
| User preference | Notifications sent in user's preferred language |
| Translation alerts | Notify translators when source content changes |

#### 7.16.10 Multi-Language in Learning Module

The Learning & Assessment Module (§8) supports multiple languages:

| Feature | Multi-Language Support |
|---------|----------------------|
| **Learning content** | Lessons available in multiple languages |
| **Assessments** | Questions can be language-specific or translated |
| **AI-generated questions** | Can generate questions from any language version |
| **Completion tracking** | Tracks completion regardless of language viewed |
| **Certificates** | Generated in user's preferred language |

**Assessment Language Handling**:

| Scenario | Behavior |
|----------|----------|
| Assessment in user's language | Use native language questions |
| Assessment not translated | Offer fallback language with notice |
| AI-translated questions | Clearly marked; may require review before use |

#### 7.16.11 MCP and Multi-Language

**MCP Server (§9.4)** supports language parameters:

| Tool | Language Parameter |
|------|-------------------|
| `search_documents` | `language?: string` — filter by language |
| `get_document` | `language?: string` — request specific language |
| `list_documents` | `language?: string` — filter results |

**Response includes language metadata**:

```json
{
  "content": "...",
  "metadata": {
    "language": "de",
    "translation_type": "ai",
    "reviewed": false,
    "primary_language": "en",
    "primary_version_available": true
  }
}
```

#### 7.16.12 Audit Trail

All language-related events are logged:

| Event | Logged Information |
|-------|-------------------|
| Translation created | Document, source language, target language, type (human/AI), user |
| AI translation generated | Document, target language, model used, source version |
| Translation reviewed | Document, language, reviewer, decision, comments |
| Translation published | Document, language, approver, e-signature (if required) |
| Translation drift detected | Document, language, source change type |
| Language preference changed | User, old language, new language |

#### 7.16.13 Compliance Considerations

For regulated environments:

| Requirement | Implementation |
|-------------|----------------|
| **Authoritative version** | Primary language is legally authoritative |
| **Translation accuracy** | Reviewed translations required for controlled documents |
| **Audit trail** | Full history of translation and review actions |
| **AI disclosure** | Unreviewed AI translations clearly marked |
| **Training records** | Track which language version user completed training in |
| **Signature binding** | E-signatures apply to specific language version |

---

## 8. Learning & Assessment Module

The Learning & Assessment Module provides integrated training capabilities, from simple document acknowledgment with comprehension verification to full learning management with tracks, certifications, and compliance reporting.

### 8.1 Overview

The module serves two integrated purposes:

| Mode | Use Case | Example |
|------|----------|---------|
| **Approval-Integrated Assessment** | Verify comprehension before document acknowledgment | "Read and pass quiz on Code of Conduct to confirm understanding" |
| **Standalone Learning Platform** | Structured training with tracks and progress | "Complete Q1 Compliance Training (5 modules, 2 hours)" |

**Key Capabilities**:

- Assessment as a gate for document approval/acknowledgment
- AI-generated questions from multiple sources (documents, URLs, MCP servers)
- Manual question authoring with structured markup
- Learning tracks with modules, lessons, and certifications
- Microlearning with spaced repetition
- Comprehensive compliance reporting and audit trails

### 8.2 Approval-Integrated Assessment

#### 8.2.1 Workflow Integration

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Document   │    │   User      │    │ Assessment  │    │  Approval   │
│  Assigned   │───►│   Reads     │───►│  Required   │───►│  Enabled    │
│  for Ack.   │    │  Document   │    │  (Pass)     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼ (Fail)
                                      ┌─────────────┐
                                      │   Retry or  │
                                      │   Re-read   │
                                      └─────────────┘
```

#### 8.2.2 Assessment Configuration Options

| Option | Description |
|--------|-------------|
| **No assessment** | Simple acknowledgment ("I have read and understood") |
| **Manual questions** | Author defines questions in document (structured section) |
| **AI-generated questions** | AI creates questions from document content and/or other sources |
| **Hybrid** | Mix of manual key questions + AI-generated supplementary |

#### 8.2.3 Manual Question Definition

Questions can be defined in documents using structured markup:

```markdown
## New Office Features

The new office includes a gym on floor 3, a cafeteria with 
subsidized meals, and 24/7 access for all employees.

:::assessment
question: Which floor is the gym located on?
type: multiple-choice
options:
  - Floor 1
  - Floor 2
  - Floor 3 [correct]
  - Floor 4
:::
```

**Supported Question Types**:

| Type | Description | Auto-Gradable |
|------|-------------|---------------|
| Multiple choice (single) | Select one correct answer | ✅ Yes |
| Multiple choice (multi) | Select all that apply | ✅ Yes |
| True/False | Binary choice | ✅ Yes |
| Fill-in-the-blank | Type exact or close match | ✅ Yes (fuzzy) |
| Ordering | Arrange items in sequence | ✅ Yes |
| Matching | Match pairs | ✅ Yes |
| Short answer | Free text response | ⚠️ AI-assisted |
| Scenario-based | Complex situation with questions | ✅/⚠️ Depends |

#### 8.2.4 Pass Criteria Configuration

| Setting | Description | Example |
|---------|-------------|---------|
| `correct_required` | Minimum correct answers | 2 |
| `percentage_required` | Alternative: percentage | 70% |
| `max_attempts` | Attempts before lockout | 3 |
| `lockout_duration` | Time before retry allowed | 24 hours |
| `time_limit` | Maximum time for assessment | 15 minutes |
| `require_all_critical` | Must get flagged questions right | true |
| `show_correct_answers` | Reveal answers after attempt | after_pass |
| `randomize_order` | Shuffle question order | true |
| `randomize_options` | Shuffle answer options | true |

### 8.3 AI-Generated Questions with Multi-Source Support

#### 8.3.1 Source Selection

When configuring AI-generated questions, users can select from multiple knowledge sources:

| Source Type | Description | Access Control |
|-------------|-------------|----------------|
| **Primary Document** | The document being acknowledged | Automatic (always included) |
| **Related Documents** | Other platform documents | User must have read access |
| **External URLs** | Web pages, PDFs, external docs | Configured by admin |
| **MCP Servers** | Connected knowledge sources | Per MCP server permissions |

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI QUESTION GENERATION - SOURCE SELECTION            │
│                                                                         │
│  Primary Document: Code of Conduct 2025 ✓ (required)                   │
│                                                                         │
│  Additional Sources:                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Platform Documents                                               │   │
│  │ ☑ Anti-Bribery Policy (SOP-HR-012)                              │   │
│  │ ☑ Whistleblower Procedures (SOP-HR-015)                         │   │
│  │ ☐ Travel & Expense Policy (SOP-FIN-003)                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ External URLs                                                    │   │
│  │ ☑ https://www.justice.gov/criminal-fraud/fcpa-guidance          │   │
│  │ + Add URL...                                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ MCP Servers                                                      │   │
│  │ ☑ Company Policy Wiki                                           │   │
│  │ ☐ Regulatory Database                                           │   │
│  │ ☐ HR Knowledge Base                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [Generate Questions]                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.3.2 Configuration by Sender

```yaml
assessment:
  source: ai-generated
  prompt: "Generate questions about ethical conduct and reporting procedures"
  sources:
    primary_document: true
    additional_documents:
      - id: "SOP-HR-012"
      - id: "SOP-HR-015"
    external_urls:
      - url: "https://www.justice.gov/criminal-fraud/fcpa-guidance"
        sections: ["penalties", "compliance-programs"]
    mcp_servers:
      - server: "company-policy-wiki"
        query: "ethics reporting whistleblower"
  question_count: 5
  difficulty: standard
  question_types: [multiple-choice, true-false]
  pass_criteria:
    correct_required: 3
    max_attempts: 3
  author_review: required  # AI questions must be approved before use
```

#### 8.3.3 AI Question Generation Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI QUESTION GENERATOR                                 │
│                                                                          │
│  Sources:                                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
│  │  Primary    │ │  Platform   │ │  External   │ │  MCP Server     │    │
│  │  Document   │ │  Documents  │ │  URLs       │ │  Responses      │    │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────┬────────┘    │
│         │               │               │                 │             │
│         └───────────────┴───────────────┴─────────────────┘             │
│                                   │                                      │
│                                   ▼                                      │
│                    ┌──────────────────────────┐                          │
│                    │  Content Aggregator      │                          │
│                    │  • Fetch & parse sources │                          │
│                    │  • Extract key content   │                          │
│                    │  • Resolve references    │                          │
│                    └────────────┬─────────────┘                          │
│                                 ▼                                        │
│                    ┌──────────────────────────┐                          │
│                    │  Context Builder         │◄── Custom Prompt         │
│                    │  • Combine sources       │◄── Generation Config     │
│                    │  • Apply focus areas     │                          │
│                    └────────────┬─────────────┘                          │
│                                 ▼                                        │
│                    ┌──────────────────────────┐                          │
│                    │  Question Generator      │                          │
│                    │  • Generate questions    │                          │
│                    │  • Create distractors    │                          │
│                    │  • Assign difficulty     │                          │
│                    │  • Tag source references │                          │
│                    └────────────┬─────────────┘                          │
│                                 ▼                                        │
│                    ┌──────────────────────────┐                          │
│                    │  Quality Filter          │                          │
│                    │  • Clarity check         │                          │
│                    │  • Ambiguity detection   │                          │
│                    │  • Source verification   │                          │
│                    │  • Confidence scoring    │                          │
│                    └────────────┬─────────────┘                          │
│                                 │                                        │
│  Output:                        ▼                                        │
│                    ┌──────────────────────────┐                          │
│                    │  Question Pool           │                          │
│                    │  + Source attribution    │                          │
│                    │  + Confidence scores     │                          │
│                    │  + Review status         │                          │
│                    └──────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.3.4 AI Generation Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| `question_count` | 1-20 | Number of questions to generate |
| `difficulty` | basic, standard, advanced | Complexity level |
| `question_types` | array | Restrict to specific types |
| `focus_sections` | all, array of sections | Which parts to draw from |
| `prompt` | string | Custom guidance ("focus on safety procedures") |
| `avoid_topics` | array | Exclude certain content |
| `bloom_level` | remember, understand, apply, analyze | Cognitive level |
| `randomize` | boolean | Different questions per user from pool |
| `author_review` | required, optional, none | Whether author must approve AI questions |
| `source_attribution` | boolean | Show which source each question comes from |

#### 8.3.5 Source Attribution

Generated questions include source attribution for transparency and auditability:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Question 2 of 5                                                        │
│                                                                         │
│  According to company policy, what is the maximum gift value that       │
│  can be accepted without manager approval?                              │
│                                                                         │
│  ○ $25                                                                  │
│  ○ $50                                                                  │
│  ○ $100                                                                 │
│  ○ No gifts are ever permitted                                          │
│                                                                         │
│  ────────────────────────────────────────────────────────────────────   │
│  📄 Source: Code of Conduct 2025, Section 4.2 "Gifts and Entertainment" │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.3.6 Author Review Workflow

When `author_review: required`, AI-generated questions must be approved:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    AI       │    │   Author    │    │   Approved  │    │   Ready     │
│  Generates  │───►│   Reviews   │───►│   Question  │───►│   for Use   │
│  Questions  │    │   Each Q    │    │   Pool      │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼ (Reject/Edit)
                   ┌─────────────┐
                   │  Modified   │
                   │  or Removed │
                   └─────────────┘
```

**Review Interface**:

| Action | Description |
|--------|-------------|
| **Approve** | Accept question as-is |
| **Edit** | Modify question text, options, or correct answer |
| **Reject** | Remove question from pool |
| **Flag** | Mark for discussion/second opinion |
| **Regenerate** | Request AI to generate alternative |

### 8.4 Standalone Learning Platform

#### 8.4.1 Content Hierarchy

```
Learning Catalog
└── Learning Track (e.g., "2025 Compliance Training")
    └── Module (e.g., "Anti-Bribery Fundamentals")
        └── Lesson (e.g., "Recognizing Red Flags")
            ├── Content Block (text, video, interactive)
            ├── Knowledge Check (inline quiz, non-graded)
            └── Assessment (end-of-lesson, graded)
```

#### 8.4.2 Learning Track Features

| Feature | Description |
|---------|-------------|
| **Sequential progression** | Lessons must be completed in order |
| **Prerequisites** | Track B requires Track A completion |
| **Time-based release** | Lessons unlock on schedule |
| **Branching paths** | Role-based content variations |
| **Certification** | Certificate generated on completion |
| **Expiration** | Certification valid for N months, then re-certification required |
| **Version management** | Track updates with grandfathering rules |

#### 8.4.3 Content Types

| Type | Description | Tracking |
|------|-------------|----------|
| **Document** | Platform document as learning content | Time spent, scroll depth |
| **Video** | Embedded or hosted video | Watch time, completion % |
| **Interactive** | Simulations, click-through demos | Interactions, completion |
| **SCORM/xAPI** | External learning content | Standard LMS tracking |
| **External link** | Link to external resource | Click tracked |
| **Live session** | Webinar/classroom (scheduled) | Attendance |
| **Knowledge check** | Inline non-graded questions | Responses (no score) |
| **Assessment** | Graded quiz | Score, pass/fail |
| **Practical task** | Upload evidence, manager sign-off | Completion status |

#### 8.4.4 Microlearning Features

| Feature | Description |
|---------|-------------|
| **Daily nuggets** | Short (2-5 min) daily learning pushed to users |
| **Spaced repetition** | Re-surface content at optimal intervals for retention |
| **Mobile-first** | Designed for phone completion |
| **Offline capable** | Download content for offline completion |
| **Gamification** | Points, streaks, leaderboards (optional) |
| **Social learning** | Comments, discussions, peer questions |

#### 8.4.5 AI-Powered Learning Features

| Feature | Description |
|---------|-------------|
| **Auto-generate quizzes** | Create assessments from any document or source combination |
| **Adaptive difficulty** | Adjust questions based on learner performance |
| **Content summarization** | Generate bite-sized summaries |
| **Knowledge gap analysis** | Identify weak areas from quiz performance |
| **Personalized recommendations** | Suggest content based on role + gaps |
| **Q&A assistant** | Learner can ask questions about content |
| **Translation** | Auto-translate content for global teams |

### 8.5 User Experience

#### 8.5.1 Learner Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│  My Learning                                            [User: J. Smith]│
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ⚠️ ACTION REQUIRED (2)                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📄 Code of Conduct 2025 — Acknowledge by Jan 15                 │   │
│  │    ▶ Read document → Pass quiz (3/5) → Sign acknowledgment      │   │
│  │    [Start Now]                                                  │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ 📚 Q1 Compliance Training — Due Jan 31                          │   │
│  │    Progress: ████████░░░░ 65% (3 of 5 modules complete)         │   │
│  │    [Continue]                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  📊 MY PROGRESS                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Completed    │ │ In Progress  │ │ Certificates │ │ Streak       │   │
│  │     12       │ │      2       │ │      4       │ │   7 days 🔥  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                         │
│  📚 CONTINUE LEARNING                                                   │
│  • Anti-Bribery Module 4: Reporting Concerns (18 min remaining)        │
│  • Data Privacy Refresher (not started)                                │
│                                                                         │
│  🎯 RECOMMENDED FOR YOU                                                 │
│  • Advanced Excel for Finance (based on your role)                     │
│  • Leadership Foundations (new track available)                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.5.2 Assessment Experience

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Code of Conduct 2025 — Comprehension Check                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Question 2 of 5                                    Time remaining: 12:34│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ According to the Code of Conduct, which of the following        │   │
│  │ is acceptable when receiving gifts from vendors?                │   │
│  │                                                                 │   │
│  │ ○ Accepting gifts of any value if disclosed to manager         │   │
│  │ ● Accepting gifts under $50 with no approval required          │   │
│  │ ○ Accepting gifts only during holiday season                   │   │
│  │ ○ Never accepting any gifts under any circumstances            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  📄 Source: Code of Conduct 2025, Section 4.2                          │
│                                                                         │
│  [← Previous]                                              [Next →]     │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  Pass requirement: 3 of 5 correct    Attempt: 1 of 3                    │
│  📄 [Review Document]                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.5.3 Results & Completion

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ✅ Assessment Passed                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Score: 4/5 (80%)                                                       │
│  Time: 6 minutes 42 seconds                                             │
│  Attempt: 1 of 3                                                        │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ✓ Question 1: Correct                                           │   │
│  │ ✓ Question 2: Correct                                           │   │
│  │ ✗ Question 3: Incorrect — Review: Section 3.1 Conflicts         │   │
│  │ ✓ Question 4: Correct                                           │   │
│  │ ✓ Question 5: Correct                                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  You may now acknowledge the document.                                  │
│                                                                         │
│  [Acknowledge Code of Conduct 2025]                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.6 Administration

#### 8.6.1 Admin Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Learning Administration                                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📊 COMPLIANCE OVERVIEW                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Code of Conduct 2025 Acknowledgment        Due: Jan 15, 2025     │  │
│  │                                                                   │  │
│  │ Completed  ████████████████████░░░░  847/1,024 (83%)             │  │
│  │ In Progress ██░░░░░░░░░░░░░░░░░░░░░   89/1,024 (9%)              │  │
│  │ Not Started █░░░░░░░░░░░░░░░░░░░░░░   88/1,024 (8%)              │  │
│  │                                                                   │  │
│  │ [View Details] [Send Reminder] [Export Report] [Extend Deadline] │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ⚠️ ATTENTION NEEDED                                                    │
│  • 12 users failed assessment 3 times (locked out) — [Review]          │
│  • 88 users have not started (8 days until deadline) — [Send Reminder] │
│  • 3 questions flagged as confusing — [Review Feedback]                │
│                                                                         │
│  📈 ASSESSMENT ANALYTICS                                                │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ Question                              Pass Rate   Avg Time     │    │
│  │ Q1: Gift policy threshold             94%         0:42         │    │
│  │ Q2: Conflict of interest reporting    78%         1:15         │    │
│  │ Q3: Whistleblower protections         71%  ⚠️     1:45         │    │
│  └────────────────────────────────────────────────────────────────┘    │
│  ⚠️ Q3 has low pass rate — consider reviewing question or content      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.6.2 Admin Features

| Feature | Description |
|---------|-------------|
| **Assignment management** | Assign learning to users, groups, roles, or entire org |
| **Due date management** | Set, extend, escalate deadlines |
| **Reminder automation** | Scheduled reminders (7 days, 3 days, 1 day before due) |
| **Escalation rules** | Notify managers when direct reports are overdue |
| **Exemptions** | Exempt specific users (with reason logged) |
| **Bulk actions** | Reset attempts, extend deadlines, reassign |
| **Question management** | Review, edit, retire questions; manage pools |
| **Content versioning** | Update content with rules for in-progress learners |
| **Compliance reports** | Export for auditors (who completed, when, scores) |
| **Analytics** | Question difficulty, time analysis, drop-off points |

#### 8.6.3 Assessment Builder

| Feature | Description |
|---------|-------------|
| **Question bank** | Organize questions by topic, difficulty, document |
| **AI generation** | Generate questions from selected sources |
| **Source selection** | Choose documents, URLs, MCP servers |
| **Question preview** | Test questions before publishing |
| **Randomization rules** | Configure pool size, selection rules |
| **Scoring configuration** | Points per question, partial credit, weighting |
| **Feedback authoring** | Custom feedback for correct/incorrect answers |
| **Accessibility check** | Ensure questions meet accessibility standards |
| **Multi-language** | Questions in multiple languages |

#### 8.6.4 MCP Server Configuration for Learning

Administrators can configure MCP servers as knowledge sources for question generation:

| Setting | Description |
|---------|-------------|
| **Server URL** | MCP server endpoint |
| **Authentication** | API key, OAuth, or other credentials |
| **Allowed contexts** | Which learning contexts can use this server |
| **Query templates** | Pre-defined queries for common topics |
| **Cache policy** | How long to cache responses |
| **Fallback behavior** | What to do if server is unavailable |

### 8.7 Architecture

#### 8.7.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LEARNING MODULE                                   │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │  Learning       │  │  Assessment     │  │  AI Question            │  │
│  │  Catalog &      │  │  Engine         │  │  Generator              │  │
│  │  Track Manager  │  │                 │  │  (Multi-Source)         │  │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘  │
│           │                    │                        │               │
│           └────────────────────┼────────────────────────┘               │
│                                │                                        │
│                                ▼                                        │
│                    ┌─────────────────────┐                              │
│                    │  Assignment &       │                              │
│                    │  Progress Tracker   │                              │
│                    └──────────┬──────────┘                              │
│                               │                                         │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│  Document     │    │  Workflow Engine    │    │  Notification   │
│  Control      │    │  (Approvals)        │    │  Service        │
│  Module       │    │                     │    │                 │
└───────────────┘    └─────────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                    ┌─────────────────────┐
                    │  External Sources   │
                    │  • Platform Docs    │
                    │  • External URLs    │
                    │  • MCP Servers      │
                    └─────────────────────┘
```

#### 8.7.2 Integration Points

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| **Document Control** | Bidirectional | Documents as learning content; assessment gates acknowledgment |
| **Workflow Engine** | → | Block approval until assessment passed |
| **User Directory** | ← | User info, roles, groups for assignment |
| **Notification Service** | → | Reminders, completion confirmations |
| **Audit Trail** | → | Log all learning events |
| **Reporting Engine** | ← | Compliance and analytics reports |
| **AI Services** | → | Question generation from multi-source context |
| **MCP Servers** | ← | External knowledge for question generation |

#### 8.7.3 Data Model (Key Entities)

```
LearningTrack
├── id, name, description
├── modules: [Module]
├── prerequisites: [LearningTrack]
├── certification_validity: duration
└── version, status

Module
├── id, name, description
├── lessons: [Lesson]
├── sequence_enforced: boolean
└── estimated_duration

Lesson
├── id, name
├── content_blocks: [ContentBlock]
├── assessment_id (optional)
└── estimated_duration

Assessment
├── id, name
├── question_pool: [Question]
├── source_config: AssessmentSourceConfig
├── selection_config (count, randomize, etc.)
├── pass_criteria
├── time_limit
└── author_review_required: boolean

AssessmentSourceConfig
├── primary_document_id
├── additional_document_ids: [id]
├── external_urls: [url]
├── mcp_servers: [{server, query}]
└── custom_prompt

Question
├── id, type, text
├── options (for MC)
├── correct_answer
├── explanation
├── difficulty, bloom_level
├── source_type: manual | ai-generated
├── source_reference: {type, id, section}
├── review_status: pending | approved | rejected
└── confidence_score (for AI)

Assignment
├── id, user_id
├── assignable_type: track | module | document_ack
├── assignable_id
├── due_date, status
├── completed_at
└── assessment_attempts: [Attempt]

Attempt
├── id, assignment_id
├── attempt_number
├── questions_presented: [{question_id, source_ref}]
├── answers
├── score, passed
├── started_at, completed_at
└── time_taken
```

### 8.8 Compliance & Reporting

#### 8.8.1 Compliance Reports

| Report | Description | Audience |
|--------|-------------|----------|
| **Training completion** | Who completed what, when, with scores | Managers, HR, Auditors |
| **Outstanding assignments** | Overdue and upcoming by user/dept | Managers |
| **Assessment analysis** | Question-level statistics | Training admins |
| **Certification status** | Valid, expiring, expired certs | HR, Compliance |
| **Audit trail export** | All learning events for compliance | Auditors |
| **Acknowledgment proof** | Evidence of document acknowledgment | Legal, Compliance |
| **Source attribution** | Which sources were used for each assessment | Auditors |

#### 8.8.2 Audit Trail Events

| Event | Data Captured |
|-------|---------------|
| Assignment created | User, content, assigner, due date |
| Content accessed | User, content, timestamp, duration |
| Assessment started | User, assessment, attempt number |
| Questions generated | Assessment, sources used, question count, reviewer |
| Answer submitted | User, question, answer, timestamp |
| Assessment completed | User, assessment, score, pass/fail |
| Acknowledgment signed | User, document, e-signature details |
| Reminder sent | User, content, reminder type |
| Deadline extended | User, content, old/new date, by whom |
| Exemption granted | User, content, reason, by whom |

#### 8.8.3 Security & Privacy

| Concern | Mitigation |
|---------|------------|
| **Answer tampering** | Answers recorded server-side with timestamps |
| **Question leakage** | Randomization from pools; questions not exposed in bulk |
| **Assessment fraud** | Time limits, question randomization, proctoring option |
| **Source access** | Questions only generated from sources user can access |
| **External URL security** | Admin-approved URLs only; content cached securely |
| **MCP data handling** | Responses not persisted; used only for generation |
| **Data retention** | Configurable; delete detailed answers after period |
| **Accessibility** | WCAG 2.1 AA compliance for all interfaces |

---

## 9. Publishing, API Docs, Analytics

### 9.1 Publishing

- **Site Types**: Public sites, private sites, custom domains, subdirectory hosting
- **Customization**: Logo, colors, fonts, themes, custom CSS, navigation
- **Access Control**: Visitor authentication, SSO, share links, IP restrictions
- **SEO**: Sitemap, meta tags, structured data, robots.txt, `hreflang` tags
- **Multi-Language**: Language selector, localized URLs, fallback display with notices (see §7.16)

### 9.2 API Documentation

- **OpenAPI Integration**: Import specs, auto-generate reference, interactive explorer
- **Components**: Endpoint blocks, schema visualization, code samples, error documentation

### 9.3 Analytics

- Page views, unique visitors, time on page
- Search analytics (queries, no-results)
- Content feedback (helpful/not helpful)
- Broken link detection
- Content freshness monitoring
- User journey analysis

### 9.4 Platform as MCP Server

The platform exposes itself as a Model Context Protocol (MCP) server, enabling external AI systems to query documentation content while respecting access control and classification rules.

#### 9.4.1 Overview

| Aspect | Description |
|--------|-------------|
| **Protocol** | Model Context Protocol (MCP) over HTTP/WebSocket |
| **Authentication** | API keys, OAuth 2.0, or service accounts |
| **Authorization** | All queries respect user permissions and document classifications |
| **Rate Limiting** | Configurable per client/endpoint |
| **Audit Logging** | All MCP access logged for compliance |

#### 9.4.2 Exposed Tools

The MCP server exposes the following tools for external AI agents:

| Tool | Parameters | Description |
|------|------------|-------------|
| `search_documents` | query, filters?, limit?, language? | Semantic search across accessible documents |
| `get_document` | id, version?, language? | Retrieve full document content |
| `get_document_section` | id, section_path, language? | Retrieve specific section of a document |
| `list_documents` | space?, type?, classification?, status?, language? | List documents with filters |
| `get_document_metadata` | id, language? | Get metadata without content (status, version, dates, translation status) |
| `get_effective_documents` | space?, category?, language? | List currently effective documents |
| `search_by_diataxis` | type, query?, language? | Search within specific Diátaxis category |
| `get_related_documents` | id, language? | Find documents related to a given document |
| `search_training` | query, track?, language? | Search learning content |
| `get_training_status` | user_id?, track? | Get training completion status |
| `get_document_history` | id, limit? | Retrieve version history |
| `list_languages` | document_id | List available languages for a document |

**Language Parameter Behavior**:

| Value | Behavior |
|-------|----------|
| Not specified | Returns user's preferred language or fallback |
| Specific code (e.g., "de") | Returns that language if available, else error |
| `"*"` | Returns all available languages |
| `"primary"` | Returns primary/authoritative language version |

#### 9.4.3 Exposed Resources

The MCP server also exposes resources via URI schemes:

| URI Pattern | Description | Example |
|-------------|-------------|---------|
| `docs://{space}/{path}` | Document by path | `docs://engineering/api/authentication` |
| `docs://id/{document_id}` | Document by ID | `docs://id/DOC-2024-0042` |
| `docs://{space}?type={diataxis}` | Documents by Diátaxis type | `docs://engineering?type=how-to` |
| `training://{track}/{module}` | Training content | `training://compliance-2025/anti-bribery` |
| `training://status/{user}` | User training status | `training://status/jsmith` |

#### 9.4.4 Access Control Enforcement

All MCP queries enforce the platform's access control model:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MCP REQUEST FLOW                                 │
│                                                                          │
│  External AI Agent                                                       │
│        │                                                                 │
│        ▼                                                                 │
│  ┌─────────────────┐                                                     │
│  │ Authentication  │◄── API Key / OAuth Token / Service Account          │
│  └────────┬────────┘                                                     │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                     │
│  │ Identity        │◄── Map to platform user or service identity         │
│  │ Resolution      │                                                     │
│  └────────┬────────┘                                                     │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                     │
│  │ Permission      │◄── Check hierarchical permissions (§7.14)           │
│  │ Check           │                                                     │
│  └────────┬────────┘                                                     │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                     │
│  │ Classification  │◄── Verify clearance level (§7.14.4)                 │
│  │ Check           │                                                     │
│  └────────┬────────┘                                                     │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐                                                     │
│  │ Content         │──► Return only accessible content                   │
│  │ Retrieval       │──► Filtered by permissions + classification         │
│  └─────────────────┘                                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Behaviors**:

| Scenario | Behavior |
|----------|----------|
| Document not accessible | Return "not found" (not "access denied" to prevent enumeration) |
| Partial access | Return only accessible sections; indicate content was filtered |
| Classification mismatch | Exclude from results; log access attempt |
| Masked version available | Return masked version if user lacks clearance for original |

#### 9.4.5 Service Account Configuration

External systems connect via service accounts with scoped permissions:

| Setting | Description |
|---------|-------------|
| **Name** | Identifier for the service account |
| **Spaces** | Which spaces the account can access |
| **Classification ceiling** | Maximum classification level accessible |
| **Allowed tools** | Which MCP tools the account can invoke |
| **Rate limits** | Requests per minute/hour |
| **IP allowlist** | Restrict to specific IP ranges |
| **Expiration** | Optional expiration date |

**Example Configuration**:

```yaml
service_account:
  name: "customer-support-bot"
  description: "AI bot for customer support ticket handling"
  spaces:
    - product-documentation
    - knowledge-base
  classification_ceiling: "internal"
  allowed_tools:
    - search_documents
    - get_document
    - get_document_section
  rate_limit:
    requests_per_minute: 60
    requests_per_hour: 1000
  ip_allowlist:
    - 10.0.0.0/8
  expires: "2025-12-31"
```

#### 9.4.6 Response Formatting

MCP responses include metadata for AI context management:

```json
{
  "content": "## Authentication\n\nThe API uses OAuth 2.0...",
  "metadata": {
    "document_id": "DOC-2024-0042",
    "title": "API Authentication Guide",
    "space": "engineering",
    "diataxis_type": "how-to",
    "version": "2.3",
    "effective_date": "2024-11-01",
    "classification": "internal",
    "last_updated": "2024-10-28",
    "word_count": 1250,
    "filtered": false,
    "language": {
      "code": "de",
      "name": "Deutsch",
      "translation_type": "ai",
      "reviewed": false,
      "primary_language": "en",
      "primary_available": true,
      "available_languages": ["en", "sv", "de", "fr"]
    }
  },
  "source_uri": "docs://engineering/api/authentication?lang=de"
}
```

**Language Warning in Response** (for unreviewed AI translations):

```json
{
  "content": "...",
  "warnings": [
    {
      "type": "unreviewed_translation",
      "message": "This content is an AI translation that has not been reviewed. For authoritative information, refer to the English version.",
      "primary_language": "en",
      "primary_uri": "docs://engineering/api/authentication?lang=en"
    }
  ]
}
```

#### 9.4.7 Use Cases

| Consumer | Use Case | Tools Used |
|----------|----------|------------|
| **Enterprise AI Assistant** | Answer employee questions about policies | `search_documents`, `get_document` |
| **Customer Support Bot** | Retrieve product documentation for tickets | `search_documents`, `get_document_section` |
| **Developer Copilot** | Access API reference and how-to guides | `search_by_diataxis`, `get_document` |
| **Compliance System** | Check current effective procedures | `get_effective_documents`, `get_document_metadata` |
| **Onboarding Bot** | Guide new employees through required training | `search_training`, `get_training_status` |
| **Partner Portal** | Provide partners access to shared documentation | `list_documents`, `get_document` |
| **CI/CD Pipeline** | Validate documentation exists for features | `get_document_metadata`, `search_documents` |

#### 9.4.8 Audit Trail

All MCP access is logged:

| Event | Logged Information |
|-------|-------------------|
| Tool invocation | Service account, tool, parameters, timestamp |
| Resource access | Service account, URI, response size, timestamp |
| Content returned | Document IDs accessed, sections retrieved |
| Access denied | Service account, requested resource, denial reason |
| Rate limit hit | Service account, endpoint, limit type |
| Authentication failure | Attempted credential, IP address, timestamp |

#### 9.4.9 Monitoring & Analytics

| Metric | Description |
|--------|-------------|
| **Requests by client** | Volume per service account |
| **Popular content** | Most frequently accessed documents |
| **Query patterns** | Common search queries from AI systems |
| **Error rates** | Failed requests by type |
| **Latency** | Response time percentiles |
| **Cache hit rate** | Effectiveness of response caching |

---

## 10. Integrations & Enterprise

### 10.1 Native Integrations

| Category | Integrations |
|----------|--------------|
| **Source Control** | GitHub, GitLab, Bitbucket |
| **Communication** | Slack, Microsoft Teams, Email |
| **Support** | Zendesk, Intercom, Freshdesk |
| **Project Management** | Jira, Asana, Linear |
| **Analytics** | Google Analytics, Amplitude, Mixpanel |
| **Identity** | Okta, Azure AD, OneLogin, SAML 2.0 |
| **Storage** | AWS S3, Azure Blob, Google Cloud Storage |

### 10.2 MCP Integration (Bidirectional)

The platform fully supports the Model Context Protocol (MCP) as both a **client** and a **server**:

| Role | Capability | Reference |
|------|------------|-----------|
| **MCP Client** | Consume external knowledge sources for AI features | §5.2.1 |
| **MCP Server** | Expose documentation to external AI systems | §9.4 |

#### 10.2.1 MCP Client (Consuming External Sources)

The platform can connect to external MCP servers for enhanced AI capabilities:

| Feature | MCP Usage |
|---------|-----------|
| **Reader Assistant** | Query external knowledge bases for answers |
| **Question Generation** | Pull content from company wikis, databases, APIs |
| **Content Suggestions** | Reference external standards, regulations |
| **Compliance Checking** | Validate against regulatory databases |

**MCP Server Management (Inbound)**:

| Setting | Description |
|---------|-------------|
| **Server registry** | Central list of available external MCP servers |
| **Authentication** | Per-server credentials management |
| **Permissions** | Which users/features can access each server |
| **Query templates** | Pre-defined queries for common topics |
| **Cache policy** | How long to cache responses |
| **Fallback handling** | Graceful degradation if server unavailable |

#### 10.2.2 MCP Server (Exposing Platform Content)

The platform exposes its documentation as an MCP server:

| Capability | Description |
|------------|-------------|
| **Document Query** | External AI agents can search and retrieve documentation |
| **Structured Access** | Query by space, document type, Diátaxis category |
| **Access Control** | All queries respect permissions and classifications |
| **Training Content** | Query learning materials and completion status |
| **Audit Logging** | Full audit trail of all MCP access |

**Service Account Management (Outbound)**:

| Setting | Description |
|---------|-------------|
| **Service accounts** | Credentials for external systems |
| **Scope configuration** | Spaces, classification ceiling, allowed tools |
| **Rate limiting** | Per-account request limits |
| **IP restrictions** | Allowlist for additional security |
| **Usage monitoring** | Dashboard showing access patterns |

See §9.4 for complete MCP server specification.

### 10.3 Platform Extensibility

- **Custom blocks SDK**: Build custom content blocks
- **Webhooks**: Subscribe to platform events
- **REST API**: Full platform access programmatically
- **GraphQL API**: Flexible queries for integrations
- **OAuth apps**: Third-party app authorization

### 10.4 Enterprise Features

- **Security & Compliance**: SOC 2 Type II, ISO 27001, GDPR, HIPAA
- **Administration**: User management, groups, custom roles, domain verification
- **Support**: Dedicated account manager, SLA, migration assistance, validation support
- **Deployment**: Cloud, private cloud, on-premise, air-gapped options

### 10.5 Import & Export

| Direction | Formats |
|-----------|---------|
| **Import** | Markdown, Confluence, Notion, Google Docs, Word, legacy DMS, SCORM/xAPI |
| **Export** | Markdown, PDF (with watermark), HTML, JSON, SCORM, audit reports, compliance packages |

---

## Appendix A: Diátaxis Quick Reference

|  | **Practical** | **Theoretical** |
|--|---------------|-----------------|
| **Acquisition** | **TUTORIALS** (Learning-oriented) | **EXPLANATION** (Understanding-oriented) |
| **Application** | **HOW-TO GUIDES** (Task-oriented) | **REFERENCE** (Information-oriented) |

---

## Appendix B: Document Control Compliance Matrix

| Requirement | ISO 9001 | ISO 13485 | 21 CFR Part 11 | Platform Section |
|-------------|----------|-----------|----------------|------------------|
| Approval before release | 7.5.2 | 4.2.4 | 11.10(a) | §6, §7.4 |
| Electronic signatures | — | — | 11.50-200 | §6, §7.10 |
| Audit trail | 7.5.3 | 4.2.5 | 11.10(e) | §7.8 |
| Version control | 7.5.2 | 4.2.4 | 11.10(a) | §7.2, §7.3 |
| Data integrity | 7.5.3 | 4.2.5 | 11.10(c) | §7.2 |
| Access control | 7.5.3 | 4.2.4 | 11.10(d) | §7.12, §7.14 |
| Training records | 7.2 | 6.2 | 11.10(i) | §6, §8 |
| Training effectiveness | 7.2 | 6.2 | — | §8.2, §8.8 |
| Competence verification | 7.2 | 6.2 | — | §8.2, §8.4 | |

---

## Appendix C: Git Abstraction Complete Mapping

| User Action | Git Operations | UI Feedback |
|-------------|---------------|-------------|
| Open document | `git checkout main; read file` | Document loads in editor |
| Start editing | `git checkout -b draft/<id>` | "Draft created" |
| Type/edit content | CRDT sync; periodic `git commit` | Auto-save indicator |
| Save explicitly | `git add && commit && push` | "Changes saved" |
| Submit for review | DB record created | "Submitted for review" |
| Review changes | `git diff main...branch` | Visual diff highlighting |
| Add comment | Store in DB (file:line ref) | Comment appears inline |
| Approve | E-signature in DB | "Approved" badge |
| Reject | DB status update | "Changes requested" |
| Publish/merge | `git merge --no-ff; push` | "Published successfully" |
| View history | `git log --follow` | Version timeline |
| Compare versions | `git diff sha1..sha2` | Side-by-side view |
| Restore version | `git checkout <sha> -- file; commit` | "Restored to version X" |
| Delete document | `git rm; commit` (history preserved) | "Moved to trash" |
| Resolve conflict | UI-guided; `git add; commit` | "Choose version" dialog |

---

*End of Specification*
