# Documentation Service Platform

> A Diátaxis-Based Documentation Platform with ISO/GxP Document Control & Git-Based Architecture

## Project Overview

This project implements a comprehensive documentation platform as specified in `documentation-service-specification-v3.5.md`. The platform combines:

- **Diátaxis Framework** - Content organized into Tutorials, How-to Guides, Reference, and Explanation
- **Document Control** - ISO 9001, ISO 13485, FDA 21 CFR Part 11 compliance
- **Git-Based Architecture** - Version control with abstracted complexity
- **Learning & Assessment** - Integrated training with AI-generated questions
- **Bidirectional MCP** - Both consumes and exposes content via Model Context Protocol

## Technology Stack

**IMPORTANT:** Technology choices are made at project start. Use `/docservice:tech-decision` to record choices.

### Backend Options (choose one)
| Option | Best For | Considerations |
|--------|----------|----------------|
| **Node.js/TypeScript** | Full-stack JS teams, real-time features | Excellent for CRDT/WebSocket, large ecosystem |
| **Python/FastAPI** | AI/ML integration, data processing | Strong AI libraries, good for document processing |
| **Go** | High performance, concurrent operations | Excellent Git integration, compiled binaries |
| **Rust** | Maximum performance, safety | Best Git library (gitoxide), steep learning curve |

### Frontend Options (choose one)
| Option | Best For | Considerations |
|--------|----------|----------------|
| **React + TypeScript** | Complex UI, large ecosystem | Excellent editor libraries (Slate, TipTap) |
| **Vue 3 + TypeScript** | Progressive adoption, simpler API | Good editor options, lighter weight |
| **SvelteKit** | Performance-critical, less boilerplate | Growing ecosystem, compiled approach |

### Database (required)
- **PostgreSQL** - Metadata, workflows, permissions, signatures
- **TimescaleDB extension** - Immutable audit trail (optional, can use separate store)

### Search (choose one)
- **Meilisearch** - Simpler setup, good for smaller deployments
- **Elasticsearch** - Enterprise scale, advanced features

### Real-time Collaboration
- **Yjs** - CRDT library for collaborative editing (framework agnostic)

### Git Integration (choose based on backend)
- **libgit2** - C library with bindings for most languages
- **isomorphic-git** - JavaScript implementation
- **go-git** - Pure Go implementation
- **gitoxide** - Rust implementation

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                         │
│  • Block-based editor      • Self-service portal                 │
│  • Admin dashboard         • Learning interface                  │
│  • Published sites         • MCP Server endpoints                │
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                          │
│  • Content management      • Document control workflows          │
│  • Access control          • Learning & Assessment               │
│  • AI services             • MCP Client                          │
│  • Real-time sync          • Publishing engine                   │
└─────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Git Repos    │  │ PostgreSQL   │  │ Audit Store          │   │
│  │ (Content)    │  │ (Metadata)   │  │ (Immutable Events)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Sprint Plan Overview

The project is divided into **12 sprints**, each delivering a functional increment:

| Sprint | Focus | Deliverable | Compliance |
|--------|-------|-------------|------------|
| 1 | Foundation | Basic API, auth, content storage (Git), DB schema | - |
| 2 | Editor Core | Block-based editor, basic Markdown support | - |
| 3 | Content Organization | Hierarchy (Org→Space→Page), navigation, search | - |
| 4 | Version Control UI | Change requests, diff view, merge, history | - |
| 5 | Access Control | Permissions, ACLs, classification, session management | ISO 9001 §7.5.3, 21 CFR §11.10(d) |
| 6 | Document Control | Lifecycle, numbering, metadata, retention, supersession | ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489 |
| 7 | Electronic Signatures | Re-auth, NTP timestamp, content hash, meaning capture | **21 CFR Part 11 §11.50-200** |
| 8 | Audit Trail | Hash chain, immutability, reason capture, export | **21 CFR §11.10(e)**, ISO 9001 §7.5.3 |
| 9 | Learning Module Basics | Assessments, manual questions, acknowledgments | Training records |
| 10 | AI Features | Question generation, writing assistant, masking | - |
| 11 | MCP Integration | Platform as MCP server + client | Service account audit |
| 12 | Publishing & Polish | Published sites, themes, analytics, optimization | - |

Each sprint produces a **runnable system** with incremental functionality.

**⚠️ COMPLIANCE-CRITICAL**: Sprints 5-8 implement regulatory requirements. See `docs/sprints/sprint-overview.md` for detailed compliance specifications.

## Commands

```bash
# Sprint management
/docservice:sprint <N>         # Get detailed tasks for sprint N
/docservice:sprint-status      # Current sprint progress

# Development
/docservice:implement <module> # Implement specific module
/docservice:test <module>      # Generate tests for module
/docservice:api <module>       # Design API for module

# Technology decisions
/docservice:tech-decision      # Record technology choice
/docservice:architecture       # Review architecture decisions

# Code quality
/docservice:review             # Code review current changes
/docservice:security           # Security review
/docservice:compliance         # Compliance check (21 CFR Part 11)
```

## Module Breakdown

### 1. Core Content Module
- Content hierarchy management
- Block-based document structure
- Git abstraction layer
- Real-time collaboration (CRDT)

### 2. Editor Module
- WYSIWYG block editor
- Markdown shortcuts
- Slash commands
- Code blocks, tables, diagrams

### 3. Access Control Module
- Hierarchical permissions (Owner → Admin → Editor → Reviewer → Viewer)
- Classification levels (Public → Internal → Confidential → Restricted)
- Document-level overrides
- Service accounts for MCP

### 4. Document Control Module
- Lifecycle management (Draft → In Review → Approved → Effective → Obsolete)
- Approval workflows with matrices
- Electronic signatures (21 CFR Part 11)
- Periodic review reminders

### 5. Audit Module
- Append-only event store
- Cryptographic chaining
- Compliance reporting
- Export for auditors

### 6. Learning Module
- Document acknowledgment with assessment
- AI-generated questions from multiple sources
- Learning tracks with modules and lessons
- Completion tracking and certifications

### 7. AI Services Module
- Writing assistant
- Question generation (multi-source)
- Document masking (sensitive content detection)
- Content suggestions

### 8. MCP Module
- MCP Server (expose platform content)
- MCP Client (consume external sources)
- Service account management
- Rate limiting and audit

### 9. Publishing Module
- Static site generation
- Custom domains
- Theming and customization
- SEO optimization

## Key Design Decisions

### Git Abstraction
Users never see Git concepts. The application translates user actions:

| User Action | Git Operation | User Sees |
|-------------|--------------|-----------|
| Start editing | `git checkout -b draft/CR-xxx` | "Draft created" |
| Save | `git commit` | Auto-save indicator |
| Submit for review | DB record | "Submitted" |
| Approve | E-signature in DB | "Approved" badge |
| Publish | `git merge --no-ff` | "Published" |

### Approval Workflow
Approvals are **application-managed**, not dependent on GitHub/GitLab:
- Works with bare Git repos (air-gap compatible)
- 21 CFR Part 11 compliant e-signatures
- Custom approval matrices
- Integrated audit trail

### Access Control
Dual-dimension model:
1. **Hierarchical** - Role-based, inherited through content tree
2. **Classification** - Clearance-based, independent of hierarchy

Both must grant access for content to be visible.

## Compliance Requirements

### FDA 21 CFR Part 11 (Electronic Signatures)
- Re-authentication at signature time
- Signature meaning captured (Authored, Reviewed, Approved, Witnessed)
- Trusted timestamp from NTP source
- Content hash (SHA-256) for integrity
- Non-repudiation via Git commit linkage
- Signature verification endpoint

### ISO 9001/13485 (Document Control)
- Approval before release
- Version control with history
- Access control with audit logging
- Immutable audit trail with hash chain
- Training records with validity tracking

### Records Management (ISO 15489)
- **Document Identification**: Auto-generated unique document numbers (e.g., SOP-QMS-001)
- **Versioning**: Separate revision (A, B, C) and version (1.0, 1.1) tracking
- **Metadata**: Owner, custodian, effective date, review dates, classification
- **Retention**: Configurable retention periods and disposition methods
- **Supersession**: Tracking of replaced/obsolete documents
- **Change Control**: Mandatory reason capture for document changes

## Development Guidelines

### Code Structure
```
src/
├── modules/
│   ├── content/          # Core content management
│   ├── editor/           # Block editor components
│   ├── access/           # Access control
│   ├── document-control/ # Workflows, signatures
│   ├── audit/            # Audit trail
│   ├── learning/         # Assessment & training
│   ├── ai/               # AI services
│   ├── mcp/              # MCP client & server
│   └── publishing/       # Site generation
├── shared/               # Shared utilities
├── api/                  # API routes
└── db/                   # Database schemas, migrations
```

### Testing Requirements
- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical workflows (approval, signatures)
- Compliance tests for 21 CFR Part 11 features

### Documentation
- API documentation with OpenAPI
- Architecture Decision Records (ADRs)
- Module documentation in `/docs`

## Subagents

The project includes specialized subagents:

- **architect** - System design, module boundaries, tech decisions
- **compliance-expert** - 21 CFR Part 11, ISO requirements validation
- **api-designer** - REST/GraphQL API design, MCP protocol
- **security-reviewer** - Security analysis, access control verification
- **test-engineer** - Test strategy, coverage analysis
- **frontend-specialist** - Editor implementation, UX patterns

## Getting Started

1. **Make technology decision** - Run `/docservice:tech-decision`
2. **Review Sprint 1** - Run `/docservice:sprint 1`
3. **Set up development environment** - Follow generated instructions
4. **Start implementation** - Use `/docservice:implement` for guidance

## Reference Documents

- **Specification**: `./documentation-service-specification-v3.5.md`
- **Diátaxis Framework**: https://diataxis.fr/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **21 CFR Part 11**: https://www.ecfr.gov/current/title-21/part-11
- **Yjs (CRDT)**: https://docs.yjs.dev/
