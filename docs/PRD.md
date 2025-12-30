# Product Requirements Document: Documentation Service Platform

**Version:** 1.0
**Date:** 2025-12-29
**Status:** Active
**Document Owner:** Product Management

---

## Executive Summary

### Product Vision

The Documentation Service Platform is a comprehensive documentation management system that combines modern knowledge management practices with rigorous regulatory compliance. It provides organizations with a unified platform to create, manage, and distribute technical documentation while meeting the stringent requirements of regulated industries (life sciences, medical devices, pharmaceuticals).

### Mission Statement

To enable regulated organizations to maintain high-quality, compliant documentation through an intuitive, Git-backed platform that abstracts technical complexity while maintaining full auditability and regulatory compliance.

### Target Market

- **Primary:** Life sciences and medical device companies requiring FDA 21 CFR Part 11 and ISO 13485 compliance
- **Secondary:** Organizations implementing ISO 9001 quality management systems
- **Tertiary:** Enterprise teams requiring structured documentation with version control and access management

### Key Value Propositions

1. **Compliance by Design:** Built-in FDA 21 CFR Part 11 and ISO 9001/13485 compliance without additional configuration
2. **Git-Powered, User-Friendly:** Full Git version control without requiring users to understand Git concepts
3. **Diátaxis Framework:** Structured content organization (Tutorials, How-to Guides, Reference, Explanation)
4. **Learning Integration:** Built-in assessment and acknowledgment tracking for training compliance
5. **AI-Enhanced:** Optional AI assistance for content creation and assessment generation
6. **Bidirectional MCP:** Expose documentation as an API resource and consume external content sources

### Success Metrics (1-Year Targets)

- **Adoption:** 50+ organizations using the platform in production
- **Compliance:** 100% pass rate on regulatory audits for platform features
- **User Satisfaction:** Net Promoter Score (NPS) > 50
- **Quality:** < 5 critical bugs per quarter
- **Performance:** 99.5% uptime SLA
- **Audit Readiness:** < 1 hour to generate compliance reports

---

## Problem Statement

### Current Challenges

Organizations in regulated industries face significant challenges managing documentation:

#### 1. **Compliance Complexity**

- FDA 21 CFR Part 11 requires electronic signatures, audit trails, and access controls
- ISO 9001/13485 mandate document control, approval workflows, and change management
- Traditional document management systems (SharePoint, Confluence) lack compliance features
- Paper-based systems are inefficient and error-prone
- Custom solutions are expensive to develop and maintain

#### 2. **Version Control Gaps**

- Users track changes manually or use inadequate version numbering schemes
- Git provides powerful version control but requires technical expertise
- Non-technical users struggle with Git concepts (branches, commits, merges)
- No clear audit trail of who changed what and why
- Difficult to trace document lineage and supersession

#### 3. **Training and Acknowledgment**

- Training records are maintained separately from documentation
- No way to verify that staff have read and understood critical procedures
- Manual tracking of document acknowledgments is time-consuming
- No integration between training systems and document updates
- Difficult to prove compliance during audits

#### 4. **Content Organization**

- Documentation mixes different content types (tutorials, reference, procedures)
- Users struggle to find the right information quickly
- No standard framework for organizing technical content
- Search functionality is limited or non-existent
- Cross-referencing and linking is manual

#### 5. **Access Control and Security**

- Coarse-grained permissions (all or nothing)
- No classification levels for sensitive content
- Difficult to manage permissions across hierarchical organizations
- No session management or timeout enforcement
- Audit logging is insufficient for regulatory requirements

### Market Gaps

Current solutions fall short in critical areas:

| Solution Type | Strengths | Weaknesses |
|---------------|-----------|------------|
| **SharePoint/Confluence** | Familiar UI, collaboration | No compliance features, weak version control |
| **Document Management Systems** | Compliance features | Expensive, poor UX, limited version control |
| **Git + Static Site Generators** | Excellent version control | Requires technical expertise, no compliance |
| **Custom Builds** | Tailored to needs | High cost, maintenance burden, long development |

**Gap:** No solution combines Git-level version control, regulatory compliance, and non-technical user accessibility in a single platform.

---

## Product Overview

### Core Capabilities

The Documentation Service Platform provides six core capability areas:

#### 1. **Content Management**

- Block-based WYSIWYG editor with Markdown support
- Hierarchical content organization (Organization → Workspace → Space → Page)
- Real-time collaborative editing (CRDT-based)
- Rich content types (text, code blocks, tables, diagrams)
- Template support for standardized documents
- Full-text search with typo tolerance

#### 2. **Version Control**

- Git-backed storage with abstracted user experience
- Change requests (drafts) instead of Git branches
- Visual diff viewer for comparing versions
- Version history timeline
- Automated merging with conflict detection
- Git remote synchronization for backup/collaboration

#### 3. **Document Control (ISO/FDA Compliance)**

- Document lifecycle management (Draft → In Review → Approved → Effective → Obsolete)
- Auto-generated unique document numbers (e.g., SOP-QMS-001)
- Revision tracking (Rev A, Rev B) separate from version numbers
- Approval workflows with multi-step matrices
- Electronic signatures (21 CFR Part 11 compliant)
- Retention policies and disposition management
- Periodic review scheduling with reminders
- Supersession tracking

#### 4. **Access Control & Security**

- Role-based permissions (Owner, Admin, Editor, Reviewer, Viewer)
- Classification levels (Public, Internal, Confidential, Restricted)
- Hierarchical permission inheritance with document-level overrides
- Session management with configurable timeout
- Re-authentication for sensitive operations
- Service accounts for API/MCP access

#### 5. **Audit Trail**

- Immutable, append-only audit log
- Cryptographic hash chaining for tamper detection
- Mandatory reason capture for critical operations
- NTP-sourced timestamps for legal validity
- Compliance reporting and export (CSV, PDF)
- Chain integrity verification

#### 6. **Learning & Assessment**

- Document acknowledgment campaigns (e.g., Code of Conduct)
- Optional assessment before acknowledgment
- Manual and AI-generated quiz questions
- Assessment attempt tracking and pass/fail criteria
- Training record management
- Validity periods and re-training triggers

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Block Editor │  │ Admin Panel  │  │ Learning Interface   │  │
│  │ (TipTap)     │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Reader UI    │  │ Published    │  │ MCP Server           │  │
│  │              │  │ Sites        │  │ Endpoints            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ Content Management   │  │ Document Control             │    │
│  │ - Hierarchy          │  │ - Lifecycle                  │    │
│  │ - Search             │  │ - Numbering                  │    │
│  │ - CRDT Sync          │  │ - Approval Workflows         │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ Access Control       │  │ Electronic Signatures        │    │
│  │ - Permissions        │  │ - Re-authentication          │    │
│  │ - Classifications    │  │ - NTP Timestamps             │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ Audit Trail          │  │ Learning & Assessment        │    │
│  │ - Hash Chain         │  │ - Campaigns                  │    │
│  │ - Compliance Reports │  │ - Quiz Engine                │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ AI Services          │  │ MCP Client/Server            │    │
│  │ - Question Gen       │  │ - Content Exposure           │    │
│  │ - Writing Assistant  │  │ - External Sources           │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Git Repos    │  │ PostgreSQL   │  │ Audit Store          │  │
│  │ (Content     │  │ (Metadata,   │  │ (Immutable Events    │  │
│  │  Storage)    │  │  Workflows)  │  │  with Hash Chain)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐                                               │
│  │ Meilisearch  │  Search Index                                 │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend** | Python + FastAPI | Strong AI/ML libraries, async support, automatic OpenAPI docs |
| **Frontend** | React + TypeScript | Largest ecosystem for editors, excellent tooling |
| **Editor** | TipTap (ProseMirror) | Excellent Yjs integration, extensible, well-documented |
| **Database** | PostgreSQL | Proven reliability, excellent JSON support |
| **Search** | Meilisearch | Typo-tolerant, fast, easy to configure |
| **Git Library** | pygit2 (libgit2) | Full Git functionality, good performance |
| **CRDT** | Yjs | De facto standard for web collaboration |
| **AI** | Provider-agnostic | OpenAI, Anthropic, or local models (Ollama) |

---

## User Personas

### 1. Documentation Author (Technical Writer)

**Name:** Sarah Martinez
**Role:** Senior Technical Writer
**Organization:** MedTech Corp (medical device manufacturer)

#### Demographics
- Age: 32
- Education: Bachelor's in Technical Communication
- Experience: 8 years in regulated documentation

#### Goals
- Create clear, compliant SOPs and work instructions
- Maintain consistency across documentation
- Minimize time spent on administrative tasks
- Focus on content quality, not technical details

#### Pain Points
- Current system (SharePoint) has poor version control
- Manual tracking of document numbers and revisions
- Difficult to see what changed between versions
- No support for reusable content blocks
- Search is slow and returns irrelevant results

#### Use Cases
- Create new SOP using template
- Update existing procedure with tracked changes
- Review change requests from subject matter experts
- Search for similar procedures for reference
- Generate document number for new SOP

#### Success Criteria
- Can create/edit documents without learning Git
- Auto-save prevents lost work
- Clear visual diff when reviewing changes
- Fast, accurate search results
- Templates speed up document creation

---

### 2. Quality Manager (Reviewer/Approver)

**Name:** Dr. James Chen
**Role:** Quality Assurance Manager
**Organization:** BioPharma Solutions

#### Demographics
- Age: 45
- Education: PhD in Pharmaceutical Sciences
- Experience: 15 years in QA, 8 years in management

#### Goals
- Ensure all procedures meet regulatory requirements
- Maintain audit readiness at all times
- Track training and acknowledgment compliance
- Minimize risk of non-compliance
- Efficiently review and approve documents

#### Pain Points
- Approval workflows are manual and slow
- Difficult to track who has acknowledged critical procedures
- Training records are disconnected from documents
- Cannot easily generate compliance reports for auditors
- Electronic signatures are not legally valid

#### Use Cases
- Review and approve change requests
- Electronically sign approved documents
- Generate audit trail reports for FDA inspection
- Create acknowledgment campaign for new Code of Conduct
- Track periodic review compliance

#### Success Criteria
- Approval workflow is enforced by system
- Electronic signatures meet 21 CFR Part 11 requirements
- Can generate compliance reports in < 5 minutes
- Real-time dashboard shows training compliance status
- Automatic reminders for overdue reviews

---

### 3. End User (Procedure Reader)

**Name:** Maria Rodriguez
**Role:** Manufacturing Technician
**Organization:** MedTech Corp

#### Demographics
- Age: 28
- Education: Associate's degree in Manufacturing Technology
- Experience: 5 years on production floor

#### Goals
- Quickly find correct procedures for tasks
- Understand instructions clearly
- Complete required training acknowledgments
- Access procedures on tablet at workstation
- Avoid compliance violations

#### Pain Points
- Current system is slow on shop floor tablets
- Difficult to navigate nested folder structures
- Cannot tell which version is current
- Acknowledgment process is confusing
- No offline access during network issues

#### Use Cases
- Search for "vial inspection procedure"
- Read SOP on tablet at workstation
- Complete acknowledgment with assessment
- View training status dashboard
- Access procedures in "How-to Guides" section

#### Success Criteria
- Fast page load times on tablets
- Clear visual indicators for document status
- Assessment questions test actual understanding
- Can complete acknowledgment in < 5 minutes
- Dashboard shows upcoming training due dates

---

### 4. System Administrator

**Name:** Alex Thompson
**Role:** IT Systems Administrator
**Organization:** BioPharma Solutions

#### Demographics
- Age: 35
- Education: Bachelor's in Computer Science
- Experience: 10 years in IT, 3 years in regulated environments

#### Goals
- Maintain system uptime and performance
- Ensure data security and backup
- Manage user accounts and permissions
- Monitor audit trail integrity
- Support validation activities

#### Pain Points
- Current system requires frequent manual intervention
- Backup procedures are complex and error-prone
- Difficult to configure approval workflows
- No visibility into system health
- Audit trail verification is manual

#### Use Cases
- Configure document numbering schemes
- Set up approval matrices for different document types
- Create retention policies
- Verify audit trail chain integrity
- Configure Git remote for backup
- Generate validation reports for IQ/OQ/PQ

#### Success Criteria
- Automated backups with verification
- Self-service permission management for managers
- Real-time system health monitoring
- One-click audit trail integrity check
- Comprehensive admin audit logging

---

### 5. Integration Developer (API Consumer)

**Name:** Jordan Kim
**Role:** Senior Software Engineer
**Organization:** HealthTech Innovations

#### Demographics
- Age: 30
- Education: Master's in Computer Science
- Experience: 7 years in software development

#### Goals
- Integrate documentation into AI agent workflows
- Build custom tooling on top of platform
- Automate documentation generation
- Ensure API stability and performance
- Maintain security in integrations

#### Pain Points
- Many systems lack proper APIs
- Documentation for APIs is often outdated
- Authentication is complex and poorly documented
- No webhooks for real-time updates
- API rate limits are too restrictive

#### Use Cases
- Expose documentation via MCP for AI agents
- Query procedures from internal chatbot
- Automatically create change requests from Jira tickets
- Generate compliance reports via API
- Set up webhooks for document updates

#### Success Criteria
- Comprehensive OpenAPI documentation
- Service account authentication
- MCP server for AI agent integration
- Webhook support for real-time updates
- Clear rate limits with throttling headers
- Full audit logging of API access

---

## Feature Requirements

### Implemented Features (Sprints 1-13)

#### Sprint 1: Foundation ✅

**Status:** Completed
**Compliance:** Foundation for all compliance features

##### Backend Infrastructure
- FastAPI application with health check endpoints
- JWT-based authentication with secure password hashing (bcrypt)
- PostgreSQL database connection with SQLAlchemy ORM
- Database schema with UUIDMixin and TimestampMixin base classes
- User model with email verification and password reset

##### Git Integration
- pygit2-based Git service for repository management
- Programmatic repository creation and initialization
- Commit creation with author information
- Branch operations (create, switch, delete)
- File operations (read, write, stage, commit)

##### API Foundation
- RESTful API design with OpenAPI documentation
- Pydantic models for request/response validation
- Error handling with appropriate HTTP status codes
- CORS configuration for frontend integration

##### Testing
- pytest test infrastructure
- Unit tests for authentication
- Integration tests for Git service
- 80%+ code coverage

**Deliverables:**
- Runnable API with `/health`, `/auth/register`, `/auth/login` endpoints
- User can register, log in, and receive JWT token
- Git repositories can be created programmatically
- All tests passing

---

#### Sprint 2: Editor Core ✅

**Status:** Completed

##### Block-Based Editor
- TipTap editor integration with React
- Basic block types (paragraph, heading, bullet list, numbered list)
- Code blocks with syntax highlighting
- Tables with resize and cell merge
- Markdown shortcuts (e.g., `#` for heading, `-` for bullet)

##### Content Serialization
- JSON-based content storage (ProseMirror schema)
- Markdown import/export functionality
- Content validation on save

##### Auto-Save
- Debounced auto-save (2-second delay after last edit)
- Visual indicator for save status
- Automatic Git commit on save

**Deliverables:**
- Working block-based editor
- Documents can be created and edited
- Content is saved to Git automatically
- Markdown compatibility

---

#### Sprint 3: Content Organization ✅

**Status:** Completed

##### Content Hierarchy
- Four-level hierarchy: Organization → Workspace → Space → Page
- Hierarchical permission inheritance
- Navigation tree with expand/collapse
- Breadcrumb navigation

##### Diátaxis Categorization
- Page types: Tutorial, How-to Guide, Reference, Explanation
- Visual badges for content type
- Filtering by Diátaxis category
- Type-specific templates

##### Search
- Meilisearch integration for full-text search
- Typo-tolerant search with ranking
- Search results with highlighting
- Filter by Diátaxis type, status, or owner

##### Navigation
- Sidebar with collapsible tree view
- Recent pages list
- Favorites/bookmarks
- Search-as-you-type

**Deliverables:**
- Full content hierarchy implemented
- Sidebar navigation functional
- Search returns relevant results
- Diátaxis tagging applied

---

#### Sprint 4: Version Control UI ✅

**Status:** Completed

##### Change Request System
- Change requests (CR) as abstraction over Git branches
- CR status: Draft, Submitted, In Review, Approved, Published, Rejected
- Author can create, edit, and submit CRs
- Reviewers can approve, reject, or request changes

##### Visual Diff Viewer
- Side-by-side diff view
- Inline diff view
- Syntax highlighting in code blocks
- Line numbers and change indicators
- Hunks are collapsible for large diffs

##### Version History
- Timeline view of all commits for a page
- Author avatars and commit messages
- Click to view specific version
- Compare any two versions
- Restore previous version functionality

##### Merge Workflow
- Automated merge on approval
- Conflict detection and resolution UI
- No-fast-forward merges for audit trail
- Merge commits include CR metadata

**Deliverables:**
- Change request creation and workflow
- Visual diff viewer
- Version history timeline
- Merge/publish functionality

---

#### Sprint 5: Access Control ✅

**Status:** Completed
**Compliance:** ISO 9001 §7.5.3, 21 CFR §11.10(d)

##### Role-Based Permissions
- Five roles: Owner, Admin, Editor, Reviewer, Viewer
- Role capabilities defined in code
- Hierarchical inheritance (Organization → Workspace → Space → Document)
- Document-level permission overrides

##### Classification Levels
- Four levels: Public, Internal, Confidential, Restricted
- User clearance levels
- Classification enforcement on access
- Visual badges for classification

##### Granular Permission Model
- Permission table linking users to resources
- Scope: Organization, Workspace, Space, Document
- Permission grant/revoke logged to audit trail
- Effective permission resolution algorithm

##### Session Management
- Configurable session timeout (default: 30 minutes)
- Session tracking in database
- Automatic logout on timeout
- Warning before session expires

##### Audit Logging
- All permission changes logged
- Access denied events logged
- Session creation/termination logged
- IP address and user agent captured

**Deliverables:**
- Role-based permissions enforced
- Classification levels working
- Session timeout functional
- Access control audit logging

---

#### Sprint 6: Document Control ✅

**Status:** Completed
**Compliance:** ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489

##### Document Lifecycle
- Five states: Draft, In Review, Approved, Effective, Obsolete
- State machine with valid transitions
- Transition permissions based on role
- Metadata validation before transitions

##### Document Numbering
- Auto-generated unique document numbers (e.g., SOP-QMS-001)
- Organization-level sequences per document type
- Configurable prefixes and format patterns
- Concurrent number generation protection (SELECT FOR UPDATE)

##### Revision Tracking
- Revision letters (A, B, C...) for major changes
- Major/minor version numbers (1.0, 1.1, 2.0)
- Separate revision and version incrementing
- Revision history with change reasons

##### Approval Workflows
- Approval matrices defining multi-step workflows
- Sequential or parallel approval steps
- Optional vs. required steps
- Approval records with approver comments
- Integration with Change Request system

##### Retention Policies
- Configurable retention periods per document type
- Disposition methods: Archive, Destroy, Transfer, Review
- Automatic disposition date calculation
- Review overdue actions: Notify, Auto-state-change, Block access
- Notification settings (owner, custodian, days before)

##### Metadata Management
- Owner and custodian assignment
- Effective date and approved date tracking
- Review cycle (e.g., annual review)
- Next review date with automatic calculation
- Supersession tracking (links to replaced documents)

##### Change Control
- Change summary and reason fields
- Mandatory change reason for major revisions
- Change history viewable in revision log

**Deliverables:**
- Document lifecycle enforced
- Auto-numbering functional
- Revision tracking working
- Approval workflows integrated
- Retention policies applied
- Periodic review reminders

---

#### Sprint 7: Electronic Signatures ✅

**Status:** Completed
**Compliance:** 21 CFR Part 11 §11.50-200

##### Signature Components
- Frozen signer information (name, email, title)
- Signature meaning (Authored, Reviewed, Approved, Witnessed, Acknowledged)
- Trusted timestamp from NTP server
- Content hash (SHA-256) of signed content
- Git commit SHA linkage for non-repudiation
- IP address and user agent capture

##### Re-Authentication
- Password re-entry required before signing
- Optional MFA verification
- Short-lived re-auth token (5 minutes)
- Re-auth session tracking

##### Signature Verification
- Content hash verification against current document
- Signer existence check
- Signature chain integrity check
- Verification endpoint returns detailed status

##### Signature Manifestation
- Display format: "[Name], [Meaning], [Date/Time]"
- Example: "Dr. James Chen, Approved, 2025-12-29 14:32:15 UTC"
- Visible on document view
- Included in PDF exports

##### Signature Scenarios
- **Collective Signing (SigningCeremony):** Multiple signers on same document (e.g., board protocol)
- **Individual Signing (Acknowledgment):** Per-user signing (e.g., Code of Conduct acknowledgment)

**Deliverables:**
- Electronic signature creation with re-auth
- NTP timestamp integration
- Content hash calculation and verification
- Signature manifestation display
- 21 CFR Part 11 compliance verified

---

#### Sprint 8: Audit Trail ✅

**Status:** Completed
**Compliance:** 21 CFR §11.10(e), ISO 9001 §7.5.3

##### Immutable Audit Log
- Append-only audit_events table
- Database triggers prevent UPDATE/DELETE
- REVOKE TRUNCATE on table
- All critical operations logged

##### Cryptographic Hash Chain
- Each event links to previous event hash
- SHA-256 content hashing
- Hash calculation includes all event metadata
- Chain integrity verification endpoint

##### Event Capture
- Event type, timestamp, actor, resource, details
- Mandatory reason for critical operations:
  - Content updated/deleted
  - Workflow rejected
  - Access revoked
  - Signature created (optional but recommended)
- NTP-validated timestamps
- IP address and user agent

##### Compliance Reporting
- Query events by date range, actor, resource, type
- Export to CSV, JSON, PDF
- Pre-built compliance reports:
  - User activity report
  - Signature report
  - Access changes report
  - Document lifecycle report
- Chain integrity verification report

##### Tamper Detection
- Hash chain verification endpoint
- Automated integrity checks (scheduled job)
- Alert on hash chain breaks
- Detailed error reporting on integrity failures

**Deliverables:**
- Immutable audit trail
- Hash chain integrity
- Compliance report export
- Tamper detection

---

#### Sprint 9: Learning Module Basics ✅

**Status:** Completed

##### Acknowledgment Campaigns
- AcknowledgmentCampaign model for mass distribution
- Assignment tracking per user
- Campaign status: Draft, Active, Completed, Cancelled
- Due dates with automatic reminders

##### Assessment Integration
- Optional assessment before acknowledgment
- Manual questions embedded in pages
- Pass criteria: Question count, percentage, max attempts
- Assessment attempt tracking with scores

##### Quiz Engine
- Multiple-choice questions
- True/false questions
- Free-text questions (manual grading)
- Randomized question order
- Immediate feedback on answers

##### Assignment Dashboard
- User dashboard showing pending assignments
- Status: Pending, In Progress, Completed, Overdue
- Document read tracking (time spent)
- Assessment pass/fail status
- Signature status

##### Campaign Management
- Admin UI to create campaigns
- Bulk user assignment
- Completion statistics dashboard
- Reminder configuration (interval, max count)
- Export completion reports

**Deliverables:**
- Acknowledgment campaigns functional
- Assessment before signing
- Assignment dashboard for users
- Campaign management for admins
- Completion tracking

---

#### Sprint 9.5: Admin UI ✅

**Status:** Completed

##### Assessment Builder
- Visual question editor
- Add/edit/delete questions
- Question type selection
- Answer options configuration
- Pass criteria settings

##### Lifecycle UI
- Visual workflow designer for lifecycles
- State configuration (name, label, editable, visible)
- Transition rules configuration
- Role-based transition permissions

##### Approval Matrix UI
- Create/edit approval matrices
- Multi-step workflow designer
- Sequential vs. parallel configuration
- Required vs. optional steps
- Applicable document type selection

##### Signature Configuration
- SigningCeremony creation wizard
- Signer selection and role assignment
- Completion rule configuration (all/count/percentage)
- Delegation and peer review settings
- Reminder and timeout configuration

##### Admin Dashboard
- System health metrics
- User activity overview
- Recent audit events
- Pending approvals and reviews
- Training compliance summary

**Deliverables:**
- Assessment builder UI
- Lifecycle configuration UI
- Approval matrix designer
- Signature ceremony wizard
- Admin dashboard

---

#### Sprint 10: AI Features (Planned)

**Status:** Planned

##### Question Generation
- AI-generated questions from document content
- Multi-source question generation (document + references)
- Question difficulty levels
- Automatic distractor generation for multiple-choice
- Review and edit AI-generated questions

##### Writing Assistant
- AI suggestions while typing
- Grammar and clarity improvements
- Compliance language suggestions
- Template-based content generation
- Tone adjustment (formal, casual)

##### Document Masking
- Automatic detection of sensitive content (PII, proprietary)
- Redaction suggestions
- Classification recommendation
- Export with masked content

##### Content Suggestions
- Related document recommendations
- Similar procedure detection
- Missing sections detection
- Completeness scoring

**Deliverables:**
- AI-generated quiz questions
- Writing assistant integration
- Document masking
- Content suggestions

---

#### Sprint 11: MCP Integration (Planned)

**Status:** Planned

##### MCP Server (Expose Platform Content)
- Implement MCP protocol endpoints
- Expose pages as resources
- Expose tools (search, create, update)
- Service account authentication
- Rate limiting per service account
- Audit logging of MCP access

##### MCP Client (Consume External Sources)
- Connect to external MCP servers
- Import content from external sources
- Map external content to pages
- Sync changes from external sources
- Conflict resolution for bidirectional sync

##### Service Account Management
- Create service accounts for API/MCP access
- API key generation and rotation
- Permission scoping for service accounts
- Service account audit logging
- Rate limit configuration per account

**Deliverables:**
- MCP server endpoints functional
- MCP client integration
- Service account management
- Rate limiting and audit

---

#### Sprint 12: Publishing & Polish (Planned)

**Status:** Planned

##### Static Site Generation
- Generate static HTML from published pages
- Custom domain support
- SSL certificate management
- Incremental builds for performance

##### Theming
- Customizable themes (colors, fonts, logos)
- CSS variable-based theming
- Dark mode support
- Responsive design for mobile/tablet

##### Analytics
- Page view tracking
- User engagement metrics
- Search analytics
- Popular content dashboard
- Export analytics data

##### Performance Optimization
- Code splitting and lazy loading
- Image optimization and CDN
- Service worker for offline support
- Database query optimization
- Caching strategy (Redis)

**Deliverables:**
- Published sites functional
- Theming system
- Analytics dashboard
- Performance optimizations

---

#### Sprint 13: Git Remote Sync ✅

**Status:** Completed

##### Remote Repository Integration
- Configure remote Git repositories (GitHub, GitLab, Bitbucket, bare repos)
- Git credential management (HTTPS, SSH, token-based)
- Encrypted credential storage
- Manual and automatic sync triggers

##### Push/Pull Operations
- Push local changes to remote
- Pull remote changes to local
- Conflict detection and resolution
- Merge strategies (fast-forward, no-ff, rebase)

##### Sync Event Tracking
- GitSyncEvent model tracking all sync operations
- Sync status: Pending, In Progress, Success, Failed
- Error logging for failed syncs
- Sync history and audit trail

##### Backup Strategy
- Scheduled automatic pushes to remote
- Backup verification
- Retention policy for remote backups
- Disaster recovery documentation

**Deliverables:**
- Remote repository configuration
- Push/pull functionality
- Sync event tracking
- Automatic backup scheduling

---

### Planned Features (Sprints 14-17)

#### Sprint 14: Diataxis Type Revision

**Status:** Planned
**Priority:** High

##### Per-Page Diátaxis Tags
- Move Diátaxis type from Space level to Page level
- Support multiple types per page (e.g., Tutorial + How-to)
- Tag-based filtering and navigation
- Type badges on page cards

##### Configurable Types
- Organization-level customization of Diátaxis types
- Add custom content types beyond standard four
- Custom type definitions with descriptions
- Type templates and guidelines

##### Migration
- Migrate existing Space-level types to Page tags
- Data migration script for existing installations
- Backward compatibility during transition

**Deliverables:**
- Per-page Diátaxis tagging
- Configurable content types
- Migration completed

---

#### Sprint 15: Metadata Portability

**Status:** Planned
**Priority:** High

##### Filesystem Metadata Storage
- Store metadata alongside content files in Git
- YAML frontmatter for page metadata
- JSON sidecar files for complex metadata
- Metadata version control in Git

##### Export/Import
- Export pages with full metadata to portable format
- Import from external systems (Confluence, SharePoint)
- Bulk export for backup
- Selective import with conflict resolution

##### Metadata Schema
- Define standard metadata schema
- Validation on import
- Schema versioning for backward compatibility
- Custom metadata fields

**Deliverables:**
- Metadata in filesystem
- Export/import functionality
- Schema validation

---

#### Sprint 16: System Documentation

**Status:** Planned
**Priority:** Medium

##### Diátaxis-Structured Docs
- Tutorial: Getting started guides
- How-to: Common tasks and workflows
- Reference: API documentation, configuration
- Explanation: Architecture and design decisions

##### Fixture-Based Installation
- Seed data for demo/testing
- Sample organization with example content
- Pre-configured approval matrices and retention policies
- Example documents with full lifecycle

##### Interactive Tutorials
- Guided walkthroughs for new users
- Interactive demos embedded in docs
- Video tutorials
- FAQ and troubleshooting

**Deliverables:**
- Complete system documentation
- Fixture-based demo installation
- Interactive tutorials

---

#### Sprint 17: Reader UI

**Status:** Planned
**Priority:** Medium

##### Accessibility (WCAG 2.1 AA)
- Keyboard navigation
- Screen reader support
- High contrast mode
- Adjustable font sizes
- Alt text for images
- ARIA labels

##### Context Menu
- Right-click menu for quick actions
- Copy link to section
- Print document
- Export as PDF/Markdown
- Add to favorites

##### Reading Aids
- Table of contents sidebar
- Progress indicator for long documents
- Estimated reading time
- Breadcrumb trail
- Previous/Next navigation
- Scroll-to-top button

##### Print and Export
- Print-optimized CSS
- PDF generation with headers/footers
- Export to Markdown, DOCX
- Batch export functionality

**Deliverables:**
- WCAG 2.1 AA compliant reader
- Context menu
- Reading aids
- Print/export functionality

---

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Page Load Time** | < 2 seconds (95th percentile) | Lighthouse, WebPageTest |
| **Search Response** | < 500ms (average) | Backend instrumentation |
| **Auto-Save Latency** | < 1 second | Frontend telemetry |
| **API Response Time** | < 200ms (median) | APM tool (e.g., Datadog) |
| **Concurrent Users** | 1000+ simultaneous editors | Load testing (Locust) |
| **Database Query Time** | < 100ms (99th percentile) | PostgreSQL slow query log |

### Scalability

| Metric | Target | Strategy |
|--------|--------|----------|
| **Content Volume** | 100,000+ pages | Database partitioning, indexed search |
| **Users** | 10,000+ users | Stateless API, horizontal scaling |
| **Storage** | 1TB+ content | Git repository sharding, object storage |
| **Audit Events** | 100M+ events | TimescaleDB compression, archival |

### Security

| Requirement | Implementation | Compliance |
|-------------|----------------|-----------|
| **Authentication** | JWT with secure password hashing (bcrypt) | OWASP Top 10 |
| **Authorization** | Role-based + classification-based | ISO 27001 |
| **Data Encryption** | TLS 1.3 in transit, AES-256 at rest | HIPAA, GDPR |
| **Session Management** | Configurable timeout, secure cookies | 21 CFR §11.10(d) |
| **Audit Logging** | Immutable, cryptographically chained | 21 CFR §11.10(e) |
| **Input Validation** | Pydantic schemas, SQL injection prevention | OWASP Top 10 |
| **Secrets Management** | Environment variables, encrypted storage | NIST 800-53 |

### Compliance Requirements

#### FDA 21 CFR Part 11 (Electronic Records and Electronic Signatures)

| Section | Requirement | Implementation |
|---------|-------------|----------------|
| **§11.10(a)** | Validation of systems | IQ/OQ/PQ protocols, test coverage > 80% |
| **§11.10(b)** | Ability to generate accurate and complete copies | PDF export, audit trail export |
| **§11.10(c)** | Protection of records | Git storage, encrypted backups, access control |
| **§11.10(d)** | Limit system access to authorized individuals | Role-based permissions, session timeout |
| **§11.10(e)** | Audit trail | Immutable log with hash chain, tamper detection |
| **§11.10(g)** | Authority checks | Permission enforcement at API layer |
| **§11.50** | Signature manifestation | Name, date/time, meaning displayed |
| **§11.70** | Signature/record linking | Content hash + Git commit SHA |
| **§11.100** | Uniqueness | User ID + non-reusable tokens |
| **§11.200** | Re-authentication | Password re-entry + optional MFA before signing |

#### ISO 9001:2015 (Quality Management Systems)

| Section | Requirement | Implementation |
|---------|-------------|----------------|
| **§7.5.2** | Creating and updating documented information | Change requests, approval workflows, version control |
| **§7.5.3** | Control of documented information | Access control, permissions, classification |
| **§7.5.3.1** | Documented information identification | Unique document numbers, revision tracking |
| **§7.5.3.2** | Control of changes | Change reason capture, approval before release |

#### ISO 13485:2016 (Medical Devices - Quality Management)

| Section | Requirement | Implementation |
|---------|-------------|----------------|
| **§4.2.4** | Control of documents | Approval before release, document numbering, supersession tracking |
| **§4.2.5** | Control of records | Retention policies, disposition management, immutable audit trail |

#### ISO 15489 (Records Management)

| Requirement | Implementation |
|-------------|----------------|
| **Document Identification** | Auto-generated unique numbers (SOP-QMS-001) |
| **Versioning** | Revision letters (A, B) + version numbers (1.0, 1.1) |
| **Metadata** | Owner, custodian, dates, classification |
| **Retention** | Configurable policies, disposition dates |
| **Supersession** | Links to replaced/obsolete documents |
| **Change Control** | Mandatory reason capture for changes |

### Accessibility Standards

**Target:** WCAG 2.1 Level AA Compliance

| Guideline | Implementation |
|-----------|----------------|
| **Perceivable** | Alt text for images, high contrast mode, resizable text |
| **Operable** | Keyboard navigation, skip links, no keyboard traps |
| **Understandable** | Clear labels, error messages, consistent navigation |
| **Robust** | Semantic HTML, ARIA labels, screen reader testing |

### Reliability & Availability

| Metric | Target | Strategy |
|--------|--------|----------|
| **Uptime SLA** | 99.5% (43.8 hours downtime/year) | Redundant infrastructure, health checks |
| **Recovery Time Objective (RTO)** | < 4 hours | Automated failover, documented recovery procedures |
| **Recovery Point Objective (RPO)** | < 1 hour | Continuous Git sync, hourly database backups |
| **Mean Time Between Failures (MTBF)** | > 720 hours (30 days) | Comprehensive testing, monitoring |
| **Mean Time To Recovery (MTTR)** | < 2 hours | Automated alerting, runbooks |

### Backup & Disaster Recovery

| Requirement | Implementation |
|-------------|----------------|
| **Backup Frequency** | Database: hourly; Git: continuous sync |
| **Backup Retention** | Daily: 7 days, Weekly: 4 weeks, Monthly: 12 months |
| **Backup Verification** | Automated restore tests weekly |
| **Geographic Redundancy** | Primary + secondary data centers |
| **Disaster Recovery Plan** | Documented, tested annually |

### Monitoring & Observability

| Component | Tool | Metrics |
|-----------|------|---------|
| **Application Performance** | Datadog / New Relic | Response times, error rates, throughput |
| **Infrastructure** | Prometheus + Grafana | CPU, memory, disk, network |
| **Logs** | ELK Stack / Loki | Centralized logging, log retention |
| **Uptime** | Pingdom / StatusCake | Endpoint availability, response time |
| **Audit Trail** | Custom dashboards | Event counts, integrity checks |

---

## User Stories and Use Cases

### Documentation Author Use Cases

#### UC-001: Create New SOP

**Actor:** Documentation Author (Sarah)
**Preconditions:** User is logged in with Editor role
**Trigger:** Sarah needs to document a new manufacturing process

**Main Flow:**
1. Sarah navigates to Quality Management System space
2. Clicks "New Document" and selects "SOP" template
3. System generates unique document number (SOP-QMS-042)
4. Sarah selects "How-to Guide" Diátaxis type
5. Sarah fills in title: "Vial Inspection Procedure"
6. Sarah uses editor to write procedure steps with code blocks for specifications
7. System auto-saves every 2 seconds to Git
8. Sarah assigns herself as document owner, designates QA manager as custodian
9. Sarah sets review cycle to 12 months
10. Sarah clicks "Submit for Review"
11. System creates change request and notifies approvers

**Postconditions:**
- SOP is in "In Review" status
- Change request is created with Git branch
- Approval workflow is initiated
- Audit event logged

**Alternate Flows:**
- 3a. If document number generation fails, show error and retry
- 7a. If network disconnects, queue saves locally and retry on reconnect
- 10a. If metadata validation fails, show errors and block submission

**Success Criteria:**
- Document created in < 2 minutes
- Auto-save prevents data loss
- Clear visual feedback on save status

---

#### UC-002: Review Change Request with Visual Diff

**Actor:** Reviewer (Dr. Chen)
**Preconditions:** Change request is in "In Review" status, Dr. Chen has Reviewer role
**Trigger:** Dr. Chen receives notification of pending review

**Main Flow:**
1. Dr. Chen opens "Pending Reviews" dashboard
2. Clicks on change request "Update Vial Inspection Procedure"
3. System displays side-by-side diff of current vs. proposed version
4. Dr. Chen reviews changes, notes updated specification in section 3.2
5. Dr. Chen adds comment: "Please verify spec tolerance with engineering"
6. Dr. Chen clicks "Request Changes"
7. System sends notification to author
8. CR status changes to "Changes Requested"

**Postconditions:**
- CR status updated
- Author receives notification
- Comment logged to audit trail
- CR timeline shows review event

**Alternate Flows:**
- 6a. If Dr. Chen clicks "Approve": CR moves to "Approved" status
- 6b. If Dr. Chen clicks "Reject": CR moves to "Rejected" status and branch can be deleted
- 4a. Dr. Chen can switch to inline diff view
- 4b. Dr. Chen can download diff as PDF for offline review

**Success Criteria:**
- Diff is clear and easy to understand
- Review can be completed in < 10 minutes
- Comments are threaded and trackable

---

### Quality Manager Use Cases

#### UC-003: Create Acknowledgment Campaign for Code of Conduct

**Actor:** Quality Manager (Dr. Chen)
**Preconditions:** Code of Conduct document is in "Effective" status, Dr. Chen has Admin role
**Trigger:** Annual Code of Conduct acknowledgment required

**Main Flow:**
1. Dr. Chen navigates to Code of Conduct document
2. Clicks "Create Acknowledgment Campaign"
3. Fills in campaign details:
   - Name: "2025 Code of Conduct Annual Acknowledgment"
   - Due date: 2025-01-31
   - Recipients: All employees (500 users selected from org)
   - Requires assessment: Yes (pass 80%, 2 attempts max)
4. Configures reminders: Daily starting 7 days before due date
5. Reviews campaign settings and clicks "Launch Campaign"
6. System creates 500 assignments, one per employee
7. System sends email notifications to all recipients

**Postconditions:**
- Campaign is "Active"
- Assignments created for all users
- Initial notifications sent
- Campaign dashboard shows 0% completion

**Alternate Flows:**
- 3a. If assessment is not required, skip to step 4
- 4a. If custom reminder schedule needed, configure intervals and max count
- 6a. If user already has pending assignment, skip duplicate creation

**Success Criteria:**
- Campaign created in < 5 minutes
- All recipients notified immediately
- Dashboard shows real-time completion status

---

#### UC-004: Generate FDA Audit Trail Report

**Actor:** Quality Manager (Dr. Chen)
**Preconditions:** FDA auditor requests documentation of changes to SOP-QMS-015 over past year
**Trigger:** FDA audit in progress

**Main Flow:**
1. Dr. Chen opens Compliance Reports page
2. Selects "Audit Trail Report" template
3. Configures filters:
   - Resource: SOP-QMS-015
   - Date range: 2024-01-01 to 2024-12-31
   - Event types: All
4. Clicks "Generate Report"
5. System queries audit trail, verifies hash chain integrity
6. System generates PDF with:
   - All audit events for SOP-QMS-015
   - Who performed each action
   - Timestamps (UTC)
   - Reason for changes
   - Hash chain verification statement
7. Dr. Chen downloads PDF
8. Provides PDF to auditor

**Postconditions:**
- Report generated successfully
- Hash chain integrity verified
- Audit event logged for report generation
- PDF includes all required information

**Alternate Flows:**
- 5a. If hash chain integrity check fails, alert Dr. Chen and include error details in report
- 6a. If too many events (> 10,000), offer paginated report or CSV export
- 3a. Can filter by event type (e.g., only signature events)
- 7a. Can export as CSV for further analysis

**Success Criteria:**
- Report generated in < 1 minute
- Report includes all required audit elements (who, what, when, why)
- Hash chain verification provides tamper evidence

---

### End User Use Cases

#### UC-005: Acknowledge Document with Assessment

**Actor:** End User (Maria)
**Preconditions:** Maria has pending assignment for Code of Conduct, assignment includes assessment
**Trigger:** Maria logs in and sees assignment notification

**Main Flow:**
1. Maria opens her dashboard, sees "1 Action Required"
2. Clicks on "2025 Code of Conduct Annual Acknowledgment" assignment
3. System displays Code of Conduct document
4. Maria reads document (system tracks time spent: 8 minutes)
5. Maria clicks "Start Assessment"
6. System presents 10 multiple-choice questions
7. Maria answers all questions
8. System scores assessment: 9/10 correct (90%) - PASS
9. System prompts for electronic signature
10. Maria re-enters password
11. Maria selects signature meaning: "Acknowledged"
12. Maria adds optional comment: "I understand and agree to follow the Code of Conduct"
13. Maria clicks "Sign"
14. System creates electronic signature with NTP timestamp
15. Assignment status changes to "Completed"
16. Maria receives confirmation email

**Postconditions:**
- Assignment completed
- Electronic signature created and logged
- Training record updated
- Completion percentage on campaign dashboard incremented

**Alternate Flows:**
- 8a. If Maria scores < 80% (fail), allow second attempt (max 2 attempts)
- 8b. If Maria fails twice, notify supervisor and prevent signature
- 10a. If password is incorrect, show error and retry
- 5a. If Maria navigates away, save progress and allow resume later

**Success Criteria:**
- Assessment completion in < 10 minutes
- Clear pass/fail feedback
- Signature process is intuitive
- Confirmation provides peace of mind

---

### System Administrator Use Cases

#### UC-006: Configure Approval Matrix for SOPs

**Actor:** System Administrator (Alex)
**Preconditions:** Alex has Admin role, organization requires 3-step approval for SOPs
**Trigger:** New regulatory requirement for additional approval step

**Main Flow:**
1. Alex opens Admin Panel → Approval Matrices
2. Clicks "Create Approval Matrix"
3. Fills in details:
   - Name: "SOP 3-Step Approval"
   - Description: "Technical Review → QA Approval → Management Approval"
   - Applicable document types: SOP
4. Configures steps:
   - Step 1: Technical Review (role: Reviewer, required: true)
   - Step 2: QA Approval (role: Admin with QA department, required: true)
   - Step 3: Management Approval (role: Admin with Management department, required: true)
5. Sets require_sequential: true
6. Clicks "Save"
7. System validates configuration
8. Matrix is activated

**Postconditions:**
- Approval matrix created
- All new SOP change requests use this matrix
- Existing in-progress CRs are unaffected
- Audit event logged

**Alternate Flows:**
- 4a. Can configure parallel approval (all approvers notified simultaneously)
- 4b. Can mark steps as optional (skippable)
- 7a. If validation fails (e.g., no approvers with required role), show error

**Success Criteria:**
- Matrix created in < 5 minutes
- Configuration is intuitive with clear labeling
- Validation prevents misconfiguration

---

#### UC-007: Verify Audit Trail Integrity

**Actor:** System Administrator (Alex)
**Preconditions:** Monthly integrity check required by SOP
**Trigger:** Scheduled task or manual check

**Main Flow:**
1. Alex opens Admin Panel → Audit Trail
2. Clicks "Verify Chain Integrity"
3. System iterates through all audit events
4. For each event:
   - Recalculates hash based on event data
   - Compares to stored hash
   - Verifies link to previous hash
5. System generates integrity report:
   - Total events checked: 1,234,567
   - Hash mismatches: 0
   - Chain breaks: 0
   - Verification time: 23 seconds
   - Result: PASS ✓
6. Alex downloads report as PDF
7. Alex files report in quality records

**Postconditions:**
- Integrity verified
- Report generated and stored
- Audit event logged for verification

**Alternate Flows:**
- 5a. If hash mismatch detected:
  - Report shows which events are compromised
  - Alert sent to security team
  - Result: FAIL with details
- 5b. If chain break detected (missing previous_hash):
  - Report shows gap in chain
  - Alert sent to security team
  - Result: FAIL with details

**Success Criteria:**
- Verification completes in < 1 minute for 1M events
- Report is clear and actionable
- Failures are immediately alerted

---

### Integration Developer Use Cases

#### UC-008: Expose Documentation via MCP for AI Agent

**Actor:** Integration Developer (Jordan)
**Preconditions:** Jordan has service account with MCP access
**Trigger:** Building internal AI chatbot that needs to answer procedure questions

**Main Flow:**
1. Jordan creates service account in Admin Panel
2. System generates API key
3. Jordan configures service account permissions:
   - Read access to "Quality Management System" space
   - Classification clearance: Confidential
4. Jordan reads MCP endpoint documentation at `/docs/mcp`
5. Jordan implements MCP client in chatbot:
   - Connect to MCP server at `https://docs.company.com/mcp`
   - Authenticate with API key
   - List available resources (pages)
   - Query page content
6. Jordan tests chatbot:
   - User asks: "How do I inspect vials?"
   - Chatbot queries MCP for "vial inspection"
   - MCP returns SOP-QMS-042 content
   - Chatbot generates answer with citation
7. Jordan deploys chatbot to production

**Postconditions:**
- Service account active with API key
- MCP access logged to audit trail
- Chatbot successfully queries documentation
- Users get accurate answers with citations

**Alternate Flows:**
- 3a. If insufficient permissions, MCP returns 403 Forbidden
- 6a. If rate limit exceeded, MCP returns 429 Too Many Requests with retry-after header
- 6b. If document is classified above service account clearance, MCP returns 403

**Success Criteria:**
- Service account setup in < 10 minutes
- MCP API is well-documented with examples
- Rate limits are clear and appropriate
- All API access is audited

---

## Success Metrics

### Adoption Metrics (Year 1)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Active Organizations** | 50+ | User registrations by organization |
| **Active Users** | 2,000+ | Monthly active users (MAU) |
| **Documents Created** | 10,000+ | Total page count across all orgs |
| **API Integrations** | 100+ | Service account activations |
| **Paid Conversion** | 30% | Free trial to paid subscription |

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Critical Bugs** | < 5 per quarter | Jira issue tracker (severity: critical) |
| **Bug Resolution Time** | < 48 hours (critical), < 7 days (high) | Jira time-to-resolution |
| **Test Coverage** | > 80% | pytest --cov backend, vitest coverage frontend |
| **Code Quality** | A rating | SonarQube analysis |
| **Security Vulnerabilities** | 0 critical, < 5 high | Snyk/Dependabot scans |

### User Satisfaction

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Net Promoter Score (NPS)** | > 50 | Quarterly user survey |
| **Customer Satisfaction (CSAT)** | > 4.5/5 | Post-interaction survey |
| **User Retention** | > 90% (annual) | Subscription renewal rate |
| **Support Ticket Volume** | < 50/month | Support system metrics |
| **Documentation Usefulness** | > 4.0/5 | User feedback on help docs |

### Performance Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Uptime** | 99.5% | Pingdom monitoring |
| **Page Load Time (p95)** | < 2 seconds | Lighthouse CI, Real User Monitoring |
| **API Response Time (p50)** | < 200ms | APM tool (Datadog) |
| **Search Response Time** | < 500ms | Backend instrumentation |
| **Auto-Save Latency** | < 1 second | Frontend telemetry |

### Compliance & Audit Readiness

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Audit Pass Rate** | 100% | Regulatory audit results |
| **Audit Preparation Time** | < 1 hour | Time to generate all required reports |
| **Hash Chain Integrity** | 100% | Automated daily verification |
| **Signature Compliance** | 100% | 21 CFR Part 11 validation tests |
| **Access Control Violations** | 0 | Audit trail analysis |

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Annual Recurring Revenue (ARR)** | $500K (Year 1) | Subscription billing |
| **Customer Acquisition Cost (CAC)** | < $5,000 | Marketing spend / new customers |
| **Customer Lifetime Value (CLV)** | > $50,000 | Average subscription value × retention |
| **Monthly Recurring Revenue (MRR)** | 20% MoM growth | Subscription billing |
| **Churn Rate** | < 5% monthly | Subscription cancellations |

---

## Constraints and Assumptions

### Technical Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Git Performance** | Large repos (> 10GB) can slow down | Repository sharding, Git LFS for large files |
| **PostgreSQL Scale** | Single instance limits to ~10K concurrent users | Read replicas, connection pooling (pgBouncer) |
| **CRDT Conflict Resolution** | Complex conflicts may require manual resolution | Clear UI for conflict review and resolution |
| **Browser Support** | Must support Chrome, Firefox, Safari, Edge (last 2 versions) | Feature detection, polyfills, progressive enhancement |
| **libgit2 Dependency** | Requires system library installation | Docker containers, documented installation |

### Regulatory Constraints

| Constraint | Requirement | Implementation |
|------------|-------------|----------------|
| **21 CFR Part 11 Validation** | System must be validated before use in production | IQ/OQ/PQ protocols, traceability matrix, test reports |
| **Audit Trail Retention** | Minimum 2 years (longer for some industries) | Configurable retention, archival to cold storage |
| **Data Residency** | Some customers require data stored in specific regions | Multi-region deployment option, regional instances |
| **Air-Gap Deployment** | Some customers require on-premise without internet | On-premise installation option, local AI models |
| **Change Control** | All system changes must be documented and approved | Internal change control process, release notes |

### Business Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Budget** | Limited development resources (2 backend, 2 frontend, 1 DevOps) | Prioritize features, leverage open-source, incremental delivery |
| **Time to Market** | MVP needed in 6 months | Focus on core features (Sprints 1-8), defer nice-to-have |
| **Support Capacity** | Limited support team (2 FTE) | Comprehensive documentation, self-service admin tools |
| **Compliance Expertise** | Requires regulatory knowledge | Partner with compliance consultants, hire QA expert |
| **Competition** | Established vendors (Veeva, MasterControl) | Differentiate on UX, Git integration, pricing |

### Assumptions

#### User Assumptions
- Users have basic computer literacy
- Users can read and understand English (initially; i18n planned for future)
- Users have access to modern web browsers
- Users are willing to learn new system (training provided)
- Administrators have technical knowledge for configuration

#### Technical Assumptions
- PostgreSQL is acceptable database for most customers
- Git is reliable for content storage and version control
- CRDT-based collaboration is sufficient for concurrent editing
- NTP servers are accessible for timestamp validation
- Internet connectivity is available (for cloud deployment)

#### Business Assumptions
- Regulatory compliance is a primary buying factor
- Customers are willing to migrate from existing systems
- Subscription pricing model is acceptable
- Market size is sufficient (5,000+ potential customers in life sciences)
- Partners will integrate via API/MCP

#### Deployment Assumptions
- Cloud deployment is preferred (AWS, Azure, GCP)
- On-premise option needed for <20% of customers
- Customers have budget for professional services (implementation, training)
- Annual subscription model is viable
- Support SLA expectations are reasonable (9-5 business hours, < 24h response)

---

## Glossary

### Regulatory Terms

| Term | Definition |
|------|------------|
| **21 CFR Part 11** | FDA regulation governing electronic records and electronic signatures for life sciences |
| **Audit Trail** | Chronological record of system activities that enables reconstruction and review of events |
| **CAPA** | Corrective and Preventive Action - process for addressing quality issues |
| **Change Control** | Formal process for managing changes to controlled documents or systems |
| **Controlled Document** | Document subject to formal document control (numbering, approval, versioning) |
| **Disposition** | Final action taken on a record at end of retention period (archive, destroy, transfer) |
| **Effective Date** | Date when a document becomes active and enforceable |
| **GxP** | Good Practice (GMP, GLP, GCP) - quality guidelines for regulated industries |
| **ISO 9001** | International standard for quality management systems |
| **ISO 13485** | International standard for medical device quality management |
| **ISO 15489** | International standard for records management |
| **Retention Policy** | Rules defining how long records must be kept and how they are disposed |
| **Revision** | Letter-based identifier for major document changes (Rev A, Rev B) |
| **Supersession** | Process of replacing an old document with a new version |
| **Validation** | Documented evidence that a system meets regulatory requirements |

### Platform Terms

| Term | Definition |
|------|------------|
| **Acknowledgment Campaign** | Mass distribution of a document for user acknowledgment/signature |
| **Approval Matrix** | Multi-step workflow defining who must approve a document |
| **Assignment** | Task for a user to acknowledge a document (with optional assessment) |
| **Audit Event** | Single entry in the immutable audit trail |
| **Change Request (CR)** | User-facing abstraction for a Git branch containing proposed changes |
| **Classification** | Security level of a document (Public, Internal, Confidential, Restricted) |
| **Collective Signing** | Multiple signers on same document (e.g., board protocol) |
| **Content Hash** | SHA-256 hash of document content for signature linking |
| **CRDT** | Conflict-free Replicated Data Type - technology for real-time collaboration |
| **Diátaxis** | Documentation framework with four types: Tutorial, How-to, Reference, Explanation |
| **Document Number** | Unique identifier for controlled documents (e.g., SOP-QMS-001) |
| **Electronic Signature** | Legally-binding digital signature meeting 21 CFR Part 11 requirements |
| **Git Abstraction** | Hiding Git complexity from users (branches become "change requests") |
| **Hash Chain** | Cryptographic linking of audit events to detect tampering |
| **Hierarchical Permission** | Permission inherited through content tree (Org → Workspace → Space → Page) |
| **Individual Signing** | Per-user signing (e.g., Code of Conduct acknowledgment) |
| **Lifecycle** | Document status progression (Draft → In Review → Approved → Effective → Obsolete) |
| **MCP (Model Context Protocol)** | Protocol for exposing content to AI agents |
| **NTP (Network Time Protocol)** | Protocol for obtaining trusted timestamps |
| **Page** | Individual document/article in the platform |
| **Re-authentication** | Password re-entry required before electronic signature |
| **Service Account** | Non-human account for API/MCP access |
| **SigningCeremony** | Collective signing session with multiple signers |
| **Space** | Container for related pages (e.g., "Quality Management System") |
| **Workspace** | Container for spaces within an organization |

### Technical Terms

| Term | Definition |
|------|------------|
| **API (Application Programming Interface)** | Programmatic interface for external systems to interact with platform |
| **Bcrypt** | Secure password hashing algorithm |
| **FastAPI** | Modern Python web framework used for backend |
| **Git** | Distributed version control system used for content storage |
| **JWT (JSON Web Token)** | Token-based authentication mechanism |
| **OpenAPI** | Standard specification for describing REST APIs |
| **PostgreSQL** | Relational database management system |
| **Pydantic** | Python library for data validation using type hints |
| **pygit2** | Python bindings for libgit2 (Git library) |
| **React** | JavaScript library for building user interfaces |
| **SHA-256** | Cryptographic hash function for content integrity |
| **SQLAlchemy** | Python SQL toolkit and ORM |
| **TipTap** | Headless block editor built on ProseMirror |
| **TypeScript** | Typed superset of JavaScript |
| **WebSocket** | Protocol for real-time bidirectional communication |
| **Yjs** | CRDT library for collaborative editing |

---

## Appendix A: Compliance Validation Checklist

### 21 CFR Part 11 - Electronic Records

| Requirement | Section | Implementation | Test Coverage |
|-------------|---------|----------------|---------------|
| Access control | §11.10(d) | Role-based permissions, classification, session timeout | Sprint 5 tests |
| Audit trail | §11.10(e) | Immutable log with hash chain, NTP timestamps | Sprint 8 tests |
| Authority checks | §11.10(g) | Permission enforcement at API layer | Sprint 5 tests |
| Device checks | §11.10(c) | Git SHA integrity, content hash verification | Sprint 1, 7 tests |
| Accurate copies | §11.10(b) | PDF export, audit trail export | Sprint 8 tests |
| System validation | §11.10(a) | IQ/OQ/PQ protocols, test coverage > 80% | All sprint tests |

### 21 CFR Part 11 - Electronic Signatures

| Requirement | Section | Implementation | Test Coverage |
|-------------|---------|----------------|---------------|
| Manifestation | §11.50 | Name, date/time, meaning display | Sprint 7 tests |
| Signature/record linking | §11.70 | Content hash + Git commit SHA | Sprint 7 tests |
| Uniqueness | §11.100 | User ID + non-reusable tokens | Sprint 7 tests |
| Re-authentication | §11.200 | Password re-entry + optional MFA | Sprint 7 tests |

### ISO 9001/13485 - Document Control

| Requirement | ISO 9001 | ISO 13485 | Implementation | Test Coverage |
|-------------|----------|-----------|----------------|---------------|
| Approval before release | 7.5.2 | 4.2.4 | Approval workflows | Sprint 6 tests |
| Document identification | 7.5.3.1 | 4.2.4 | Unique document numbers | Sprint 6 tests |
| Version control | 7.5.2 | 4.2.4 | Git + revision tracking | Sprint 1, 6 tests |
| Change control | 7.5.2 | 4.2.5 | Change reason capture | Sprint 6 tests |
| Periodic review | 7.5.2 | 4.2.4 | Review reminders | Sprint 6 tests |
| Distribution control | 7.5.3.1 | 4.2.4 | Access control | Sprint 5 tests |
| Obsolete prevention | 7.5.3.2 | 4.2.4 | Supersession tracking | Sprint 6 tests |

---

## Appendix B: API Overview

### Authentication Endpoints

```
POST   /api/v1/auth/register            - Register new user
POST   /api/v1/auth/login               - Login with credentials
POST   /api/v1/auth/logout              - Logout current session
POST   /api/v1/auth/refresh             - Refresh JWT token
POST   /api/v1/auth/re-authenticate     - Re-authenticate for signing
POST   /api/v1/auth/password/reset      - Request password reset
```

### Content Management Endpoints

```
GET    /api/v1/organizations            - List organizations
POST   /api/v1/organizations            - Create organization
GET    /api/v1/workspaces               - List workspaces
POST   /api/v1/workspaces               - Create workspace
GET    /api/v1/spaces                   - List spaces
POST   /api/v1/spaces                   - Create space
GET    /api/v1/pages                    - List pages
POST   /api/v1/pages                    - Create page
GET    /api/v1/pages/{id}               - Get page details
PATCH  /api/v1/pages/{id}               - Update page
DELETE /api/v1/pages/{id}               - Delete page
GET    /api/v1/pages/{id}/history       - Get version history
GET    /api/v1/pages/{id}/diff          - Get diff between versions
```

### Change Request Endpoints

```
GET    /api/v1/change-requests                      - List change requests
POST   /api/v1/change-requests                      - Create change request
GET    /api/v1/change-requests/{id}                 - Get CR details
PATCH  /api/v1/change-requests/{id}                 - Update CR
DELETE /api/v1/change-requests/{id}                 - Cancel CR
POST   /api/v1/change-requests/{id}/submit          - Submit for review
POST   /api/v1/change-requests/{id}/approve         - Approve CR
POST   /api/v1/change-requests/{id}/reject          - Reject CR
POST   /api/v1/change-requests/{id}/publish         - Publish (merge)
GET    /api/v1/change-requests/{id}/diff            - Get diff vs published
```

### Document Control Endpoints

```
POST   /api/v1/documents/{id}/number                - Generate document number
POST   /api/v1/documents/{id}/revise                - Create revision
GET    /api/v1/documents/{id}/revisions             - Get revision history
POST   /api/v1/documents/{id}/status                - Transition lifecycle status
GET    /api/v1/documents/review-due                 - Get documents due for review
GET    /api/v1/documents/retention-due              - Get documents due for disposition
```

### Signature Endpoints

```
POST   /api/v1/signatures                           - Create signature
GET    /api/v1/signatures/{id}                      - Get signature details
POST   /api/v1/signatures/{id}/verify               - Verify signature
GET    /api/v1/documents/{id}/signatures            - List document signatures
POST   /api/v1/signing-ceremonies                   - Create signing ceremony
GET    /api/v1/signing-ceremonies/{id}              - Get ceremony details
POST   /api/v1/signing-ceremonies/{id}/sign         - Sign in ceremony
```

### Audit Endpoints

```
GET    /api/v1/audit/events                         - Query audit events
GET    /api/v1/audit/events/{resource_type}/{id}    - Get events for resource
GET    /api/v1/audit/verify                         - Verify chain integrity
POST   /api/v1/audit/export                         - Export audit trail
```

### Learning & Assessment Endpoints

```
POST   /api/v1/campaigns                            - Create acknowledgment campaign
GET    /api/v1/campaigns/{id}                       - Get campaign details
GET    /api/v1/campaigns/{id}/status                - Get completion statistics
GET    /api/v1/assignments/me                       - Get current user's assignments
POST   /api/v1/assignments/{id}/read                - Record document read
POST   /api/v1/assignments/{id}/acknowledge         - Complete acknowledgment
POST   /api/v1/assignments/{id}/assessment/start    - Start assessment
POST   /api/v1/assignments/{id}/assessment/submit   - Submit assessment
```

### Search Endpoints

```
GET    /api/v1/search                               - Full-text search
GET    /api/v1/search/suggest                       - Search suggestions
```

### MCP Endpoints

```
GET    /mcp/resources                               - List MCP resources
GET    /mcp/resources/{id}                          - Get resource content
POST   /mcp/tools/search                            - MCP search tool
POST   /mcp/tools/create                            - MCP create page tool
POST   /mcp/tools/update                            - MCP update page tool
```

---

## Appendix C: Database Schema Overview

### Core Tables

- `organizations` - Top-level tenant organization
- `workspaces` - Workspace within organization
- `spaces` - Space within workspace
- `pages` - Individual documents/pages
- `users` - User accounts
- `sessions` - Active user sessions

### Document Control Tables

- `document_number_sequences` - Auto-incrementing sequences per org/type
- `retention_policies` - Retention policy definitions
- `approval_matrices` - Approval workflow definitions
- `approval_records` - Individual approval actions

### Version Control Tables

- `change_requests` - Change requests (Git branches abstraction)
- `change_request_comments` - Comments on CRs
- `git_credentials` - Credentials for remote repositories
- `git_sync_events` - Git sync operation tracking

### Access Control Tables

- `permissions` - Granular permissions
- `classifications` - Document classification levels

### Compliance Tables

- `electronic_signatures` - 21 CFR Part 11 signatures
- `signature_challenges` - Re-authentication challenges
- `audit_events` - Immutable audit trail
- `signing_ceremonies` - Collective signing sessions
- `signing_requests` - Individual signing requests in ceremony

### Learning Tables

- `assessments` - Assessment configurations
- `questions` - Assessment questions
- `acknowledgment_campaigns` - Mass acknowledgment campaigns
- `assignments` - User assignments
- `quiz_attempts` - Assessment attempt tracking
- `training_acknowledgments` - Training completion records

---

## Appendix D: Deployment Architecture

### Cloud Deployment (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLOUD REGION                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      LOAD BALANCER                          │ │
│  │             (AWS ALB / Azure LB / GCP LB)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│       ┌──────────────────────┴───────────────────────┐          │
│       │                                               │          │
│  ┌────▼─────┐  ┌─────────┐  ┌─────────┐  ┌─────────▼────┐     │
│  │ Frontend │  │ Backend │  │ Backend │  │   Backend    │     │
│  │ (Static) │  │  API    │  │  API    │  │     API      │     │
│  │   CDN    │  │ (Pod 1) │  │ (Pod 2) │  │   (Pod N)    │     │
│  └──────────┘  └────┬────┘  └────┬────┘  └──────┬───────┘     │
│                     │            │               │              │
│                     └────────────┼───────────────┘              │
│                                  │                               │
│  ┌──────────────────────────────┴──────────────────────────┐   │
│  │              DATABASE CLUSTER                            │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐          │   │
│  │  │PostgreSQL│◄───│PostgreSQL│◄───│PostgreSQL│          │   │
│  │  │ Primary  │    │ Replica  │    │ Replica  │          │   │
│  │  └──────────┘    └──────────┘    └──────────┘          │   │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ Git Storage   │  │ Meilisearch   │  │  Object Storage  │   │
│  │ (EFS/Azure    │  │  (Search)     │  │  (S3/Blob/GCS)   │   │
│  │  Files/GCS)   │  │               │  │                  │   │
│  └───────────────┘  └───────────────┘  └──────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │                                          │
         │                                          │
    ┌────▼────────┐                          ┌─────▼─────────┐
    │  Monitoring │                          │ Backup Region │
    │  (Datadog)  │                          │ (Disaster     │
    │             │                          │  Recovery)    │
    └─────────────┘                          └───────────────┘
```

### On-Premise Deployment (Air-Gap)

```
┌─────────────────────────────────────────────────────────────────┐
│                      CUSTOMER DATA CENTER                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    REVERSE PROXY                            │ │
│  │                (nginx / HAProxy)                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│  ┌───────────────────────────┴──────────────────────┐           │
│  │                                                   │           │
│  │  ┌──────────────┐         ┌──────────────┐      │           │
│  │  │   Backend    │         │   Backend    │      │           │
│  │  │     API      │         │     API      │      │           │
│  │  │  (Docker)    │         │  (Docker)    │      │           │
│  │  └──────┬───────┘         └──────┬───────┘      │           │
│  │         │                         │              │           │
│  │         └─────────────┬───────────┘              │           │
│  │                       │                          │           │
│  │  ┌────────────────────▼─────────────────────┐   │           │
│  │  │         PostgreSQL (Primary)              │   │           │
│  │  └───────────────────────────────────────────┘   │           │
│  │                                                   │           │
│  │  ┌──────────────┐  ┌──────────────┐            │           │
│  │  │ Git Storage  │  │ Meilisearch  │            │           │
│  │  │   (Local)    │  │   (Docker)   │            │           │
│  │  └──────────────┘  └──────────────┘            │           │
│  │                                                   │           │
│  │  ┌────────────────────────────────────────┐     │           │
│  │  │      Local AI Model (Optional)         │     │           │
│  │  │        (Ollama / LocalAI)              │     │           │
│  │  └────────────────────────────────────────┘     │           │
│  │                                                   │           │
│  └───────────────────────────────────────────────────┘          │
│                                                                   │
│  ┌───────────────────────────────────────────────────┐          │
│  │          Backup Storage (NAS / SAN)               │          │
│  │      (Automated daily backups)                     │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Document Control Information

| Field | Value |
|-------|-------|
| **Document Number** | PRD-DOC-001 |
| **Version** | 1.0 |
| **Revision** | A |
| **Document Type** | Product Requirements Document |
| **Classification** | Internal |
| **Owner** | Product Management |
| **Approved By** | (Pending) |
| **Effective Date** | (Pending approval) |
| **Next Review Date** | 2026-06-29 (6 months) |
| **Diátaxis Type** | Reference |

---

**End of Document**
