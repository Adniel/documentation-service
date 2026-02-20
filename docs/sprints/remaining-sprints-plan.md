# Remaining Sprints Plan - Optimized for Time-to-Market

## Executive Summary

This document outlines the recommended implementation order for the remaining sprints, optimized for faster time-to-market while maintaining quality.

**Completed Sprints:** 1-9, 13 (Git Remote)
**Remaining Sprints:** 9.5 (Admin UI), 10 (AI), 11 (MCP), 12 (Publishing)

**Recommended Order (Changed from Original):**

| Order | Original Sprint | Focus | Rationale |
|-------|-----------------|-------|-----------|
| 1st | **12** | Publishing | Enables demos, customer previews, go-to-market |
| 2nd | **9.5** | Admin UI | Makes all existing compliance features usable |
| 3rd | **11** | MCP Integration | Modern API for AI agent consumption |
| 4th | **10** | AI Features | Value-add differentiation (can be deferred) |

---

## Current State Assessment

### Backend (Complete)
- Authentication & sessions
- Content hierarchy (Org → Workspace → Space → Page)
- Git-based version control
- Change requests & diff
- Access control with permissions
- Document control with lifecycle
- Electronic signatures (21 CFR Part 11)
- Audit trail with hash chain
- Learning module with assessments
- Git remote sync

### Frontend (Partial)
- Editor with TipTap
- Navigation & search
- Version control UI
- Signature dialogs
- Audit viewer
- Learning components
- Admin page (tabs exist but some incomplete)

### Missing
- Publishing engine
- AI services (question generation, writing assistant)
- MCP server/client
- Some admin configuration panels

---

## Sprint A: Publishing (Original Sprint 12)

**Goal:** Enable content publishing to shareable sites for demos and customer access.

**Priority:** P0 - Blocks go-to-market

### Deliverables

#### A.1 Publishing Engine Backend

**New Files:**
```
backend/src/modules/publishing/
├── __init__.py
├── service.py              # PublishingService
├── renderer.py             # Markdown/HTML rendering
├── site_generator.py       # Static site generation
├── schemas.py              # Pydantic models
└── theme_service.py        # Theme management
```

**Database Migration (009_publishing.py):**
```python
# PublishedSite model
class PublishedSite(Base, UUIDMixin, TimestampMixin):
    space_id: UUID                    # FK to spaces (one site per space)
    organization_id: UUID             # FK to organizations

    # Site configuration
    slug: str                         # URL slug (e.g., "docs")
    custom_domain: str | None         # e.g., "docs.company.com"
    is_public: bool = False           # Public or authenticated

    # Theme
    theme_id: UUID | None             # FK to themes
    custom_css: Text | None
    logo_url: str | None
    favicon_url: str | None

    # SEO
    site_title: str
    site_description: str | None
    og_image_url: str | None

    # Publishing state
    last_published_at: datetime | None
    published_by_id: UUID | None
    published_commit_sha: str | None

    # Access control
    require_auth: bool = True
    allowed_domains: list[str] | None  # Email domain whitelist

# Theme model
class Theme(Base, UUIDMixin, TimestampMixin):
    organization_id: UUID | None      # None = system theme
    name: str
    description: str | None

    # Colors
    primary_color: str = "#2563eb"
    secondary_color: str = "#64748b"
    background_color: str = "#ffffff"
    text_color: str = "#1f2937"

    # Typography
    heading_font: str = "Inter"
    body_font: str = "Inter"
    code_font: str = "JetBrains Mono"

    # Layout
    sidebar_position: str = "left"    # left, right, hidden
    toc_enabled: bool = True
    max_content_width: str = "prose"  # prose, wide, full

    # Custom
    custom_css: Text | None
    custom_head_html: Text | None
```

**PublishingService:**
```python
class PublishingService:
    async def create_site(space_id: UUID, config: SiteConfig) -> PublishedSite
    async def update_site(site_id: UUID, config: SiteConfig) -> PublishedSite
    async def publish(site_id: UUID, user_id: UUID) -> PublishResult
    async def unpublish(site_id: UUID) -> None
    async def get_site_content(site_id: UUID, path: str) -> RenderedPage
    async def generate_static_site(site_id: UUID) -> bytes  # ZIP archive
```

**API Endpoints:**
```
POST   /api/v1/sites                           # Create site for space
GET    /api/v1/sites/{site_id}                 # Get site config
PATCH  /api/v1/sites/{site_id}                 # Update site config
DELETE /api/v1/sites/{site_id}                 # Delete site
POST   /api/v1/sites/{site_id}/publish         # Publish latest content
POST   /api/v1/sites/{site_id}/unpublish       # Take site offline
GET    /api/v1/sites/{site_id}/preview         # Preview before publish
POST   /api/v1/sites/{site_id}/export          # Export as static ZIP

# Theme management
GET    /api/v1/themes                          # List available themes
POST   /api/v1/themes                          # Create custom theme
GET    /api/v1/themes/{theme_id}               # Get theme
PATCH  /api/v1/themes/{theme_id}               # Update theme

# Public site routes (separate router)
GET    /s/{site_slug}                          # Site homepage
GET    /s/{site_slug}/{page_path}              # Page by path
GET    /s/{site_slug}/search                   # Site search
```

#### A.2 Publishing Frontend

**New Components:**
```
frontend/src/components/publishing/
├── SiteConfigPanel.tsx          # Site settings form
├── ThemeEditor.tsx              # Visual theme customization
├── ThemePreview.tsx             # Live preview of theme
├── PublishButton.tsx            # Publish with confirmation
├── SiteStatusBadge.tsx          # Published/draft indicator
├── CustomDomainSetup.tsx        # Domain configuration
├── SiteAccessControl.tsx        # Public/private settings
└── index.ts
```

**New Pages:**
```
frontend/src/pages/
├── SiteSettingsPage.tsx         # Site configuration
├── PublishedSitePage.tsx        # Public site viewer
└── SitePreviewPage.tsx          # Preview before publish
```

**SiteConfigPanel.tsx:**
```typescript
interface SiteConfigPanelProps {
  spaceId: string;
  siteId?: string;
}

// Features:
// - Site slug configuration
// - Custom domain setup with DNS instructions
// - Theme selection with preview
// - Logo/favicon upload
// - SEO metadata form
// - Access control settings
// - Publish/unpublish buttons
```

#### A.3 Public Site Viewer

**Separate frontend build for published sites:**
```
frontend/src/published-site/
├── App.tsx                      # Minimal published site app
├── components/
│   ├── SiteNavigation.tsx       # Site sidebar/nav
│   ├── PageContent.tsx          # Rendered page
│   ├── TableOfContents.tsx      # In-page TOC
│   ├── SearchDialog.tsx         # Site search
│   └── Footer.tsx               # Site footer
└── index.tsx
```

**Or use SSR/SSG approach:**
- Option A: Static site generation (Astro/Next export)
- Option B: Server-rendered pages (FastAPI templates)
- Option C: SPA with dynamic loading

**Recommendation:** Option B for MVP (FastAPI + Jinja2), migrate to Option A for scale.

### Tests Required

**Backend:**
- Unit: Site slug validation, uniqueness
- Unit: Theme CSS generation
- Unit: Page rendering pipeline
- Integration: Full publish flow
- Integration: Access control for public/private sites

**Frontend:**
- Unit: SiteConfigPanel form validation
- Unit: ThemePreview rendering
- Integration: Publish workflow
- E2E: Create site → Configure → Publish → View

### Verification Criteria

- [ ] Admin can create a published site for a space
- [ ] Site has configurable slug (e.g., `/s/product-docs`)
- [ ] Theme customization works (colors, fonts, logo)
- [ ] Published site shows navigation tree
- [ ] Pages render with proper formatting
- [ ] Search works on published site
- [ ] Access control enforced (public vs authenticated)
- [ ] Custom domain setup documented (manual DNS)

---

## Sprint B: Admin UI Completion (Original Sprint 9.5)

**Goal:** Complete administrative interfaces for all existing features.

**Priority:** P0 - Required for compliance configuration

### Current Admin State

The AdminPage.tsx already has these tabs:
- ✅ Assessments (AssessmentAdminList, AssessmentBuilder)
- ✅ Document Control (DocumentControlDashboard)
- ✅ Approvals (PendingApprovalsPanel, ApprovalMatrixEditor)
- ✅ Training Reports (CompletionReport)
- ✅ Git Remote (RemoteConfigPanel, SyncHistoryList)

### Remaining Admin Work

#### B.1 User Management Tab

**New Components:**
```
frontend/src/components/admin/
├── UserManagement.tsx           # User list with CRUD
├── UserRoleEditor.tsx           # Assign roles to users
├── UserClearanceEditor.tsx      # Set classification clearance
├── UserInviteForm.tsx           # Invite new users
├── UserActivityLog.tsx          # Recent user activity
└── BulkUserImport.tsx           # CSV import
```

**Features:**
- List all users with search/filter
- Edit user roles per organization/workspace
- Set classification clearance levels
- Invite users via email
- Deactivate/reactivate users
- View user's permissions summary
- Bulk import from CSV

**API Endpoints (already exist, need frontend):**
```
GET    /api/v1/users                           # List users
GET    /api/v1/users/{id}                      # Get user
PATCH  /api/v1/users/{id}                      # Update user
POST   /api/v1/users/invite                    # Invite user
GET    /api/v1/users/{id}/permissions          # User's permissions
```

#### B.2 Organization Settings Tab

**New Components:**
```
frontend/src/components/admin/
├── OrganizationSettings.tsx     # Org-level settings
├── DocumentNumberingConfig.tsx  # Numbering scheme setup
├── RetentionPolicyConfig.tsx    # Default retention settings
├── ClassificationLevels.tsx     # Configure clearance levels
└── AuditSettings.tsx            # Audit export settings
```

**Features:**
- Document numbering schemes (prefix patterns)
- Default retention policies per document type
- Classification level customization
- Audit trail export configuration
- Signature settings (MFA requirements)
- Session timeout configuration

#### B.3 Enhanced Document Control Dashboard

**Additions to existing DocumentControlDashboard:**
```typescript
// New panels to add
<RetentionReviewPanel />         // Documents due for retention review
<PeriodicReviewPanel />          // Documents due for periodic review
<SupersessionReport />           // Obsolete document tracking
<DocumentTypeStatistics />       # Count by type, status
```

#### B.4 Audit Trail Management

**New Components:**
```
frontend/src/components/admin/
├── AuditDashboard.tsx           # Audit overview
├── AuditExportPanel.tsx         # Export audit trail
├── ChainIntegrityCheck.tsx      # Verify hash chain
└── AuditAlertConfig.tsx         # Configure audit alerts
```

**Features:**
- View recent audit events with filters
- Export audit trail (CSV, JSON, PDF)
- Run integrity verification
- Configure alerts for specific events

### Updated AdminPage Structure

```typescript
const tabs: AdminTab[] = [
  { id: 'users', label: 'Users', icon: UsersIcon },
  { id: 'organization', label: 'Organization', icon: BuildingIcon },
  { id: 'document-control', label: 'Document Control', icon: DocumentIcon },
  { id: 'approvals', label: 'Approvals', icon: CheckIcon },
  { id: 'assessments', label: 'Assessments', icon: ClipboardIcon },
  { id: 'training-reports', label: 'Training', icon: AcademicCapIcon },
  { id: 'audit', label: 'Audit Trail', icon: ShieldIcon },
  { id: 'git-remote', label: 'Git Remote', icon: CloudIcon },
  { id: 'publishing', label: 'Publishing', icon: GlobeIcon },  // Added from Sprint A
];
```

### Tests Required

**Frontend:**
- Unit: UserManagement table rendering
- Unit: Role editor validation
- Integration: User invite flow
- Integration: Audit export
- E2E: Complete admin workflow

### Verification Criteria

- [ ] Admin can list, search, filter users
- [ ] Admin can assign roles at org/workspace/space level
- [ ] Admin can set user clearance levels
- [ ] Admin can configure document numbering schemes
- [ ] Admin can set retention policies
- [ ] Admin can export audit trail
- [ ] Admin can verify audit chain integrity
- [ ] All existing compliance features configurable via UI

---

## Sprint C: MCP Integration (Original Sprint 11)

**Goal:** Enable platform as MCP server for AI agent consumption.

**Priority:** P1 - Enables AI integration use cases

### Deliverables

#### C.1 MCP Server Implementation

**New Files:**
```
backend/src/modules/mcp/
├── __init__.py
├── server.py                    # MCP server implementation
├── tools.py                     # Tool definitions
├── resources.py                 # Resource handlers
├── auth.py                      # Service account auth
├── rate_limiter.py              # Rate limiting
└── schemas.py
```

**MCP Tools to Expose:**
```python
# Document tools
search_documents(query: str, space_id?: str) -> list[DocumentResult]
get_document(document_id: str) -> Document
get_document_content(document_id: str) -> str  # Markdown
list_spaces(workspace_id?: str) -> list[Space]

# Metadata tools
get_document_metadata(document_id: str) -> DocumentMetadata
get_document_history(document_id: str) -> list[Version]
get_document_signatures(document_id: str) -> list[Signature]

# Search tools
full_text_search(query: str, filters?: SearchFilters) -> SearchResults
semantic_search(query: str, limit: int) -> list[Document]  # If embeddings enabled
```

**MCP Resources to Expose:**
```python
# Resource URIs
doc://{org}/{workspace}/{space}/{page}     # Document content
space://{org}/{workspace}/{space}          # Space listing
workspace://{org}/{workspace}              # Workspace listing
```

#### C.2 Service Account Management

**Database Model:**
```python
class ServiceAccount(Base, UUIDMixin, TimestampMixin):
    organization_id: UUID
    name: str                              # "CI/CD Bot"
    description: str | None

    # Authentication
    api_key_hash: str                      # Hashed API key
    api_key_prefix: str                    # First 8 chars for identification

    # Permissions
    role: Role                             # viewer, editor, etc.
    allowed_spaces: list[UUID] | None      # None = all
    allowed_operations: list[str] | None   # None = all

    # Security
    ip_allowlist: list[str] | None         # CIDR ranges
    rate_limit_per_minute: int = 60

    # Status
    is_active: bool = True
    last_used_at: datetime | None
    created_by_id: UUID

class ServiceAccountUsage(Base, UUIDMixin):
    service_account_id: UUID
    timestamp: datetime
    operation: str
    resource_id: UUID | None
    ip_address: str
    response_code: int
```

**API Endpoints:**
```
# Service account management
POST   /api/v1/service-accounts                    # Create account
GET    /api/v1/service-accounts                    # List accounts
GET    /api/v1/service-accounts/{id}               # Get account
PATCH  /api/v1/service-accounts/{id}               # Update account
DELETE /api/v1/service-accounts/{id}               # Delete account
POST   /api/v1/service-accounts/{id}/rotate-key    # Rotate API key
GET    /api/v1/service-accounts/{id}/usage         # Usage statistics

# MCP endpoint
POST   /mcp                                        # MCP JSON-RPC endpoint
```

#### C.3 MCP Frontend

**New Components:**
```
frontend/src/components/mcp/
├── ServiceAccountList.tsx       # List service accounts
├── ServiceAccountForm.tsx       # Create/edit account
├── ApiKeyDisplay.tsx            # Show key (once)
├── UsageStats.tsx               # Usage dashboard
├── McpEndpointInfo.tsx          # Connection instructions
└── index.ts
```

**Add to AdminPage:**
```typescript
{ id: 'integrations', label: 'Integrations', icon: PlugIcon }
```

### Tests Required

**Backend:**
- Unit: MCP tool implementations
- Unit: Service account permission checking
- Unit: Rate limiting
- Integration: MCP JSON-RPC protocol
- Integration: Service account CRUD

**Frontend:**
- Unit: ServiceAccountForm validation
- Integration: Create account flow
- E2E: Full MCP workflow

### Verification Criteria

- [ ] Admin can create service accounts
- [ ] API key generated and displayed once
- [ ] Service account can authenticate via API key
- [ ] MCP tools return correct data
- [ ] Rate limiting enforced
- [ ] All MCP access logged to audit trail
- [ ] IP allowlist enforced
- [ ] Usage statistics tracked

---

## Sprint D: AI Features (Original Sprint 10)

**Goal:** Add AI-powered features for question generation and writing assistance.

**Priority:** P2 - Nice-to-have differentiation

### Deliverables

#### D.1 AI Service Infrastructure

**New Files:**
```
backend/src/modules/ai/
├── __init__.py
├── service.py                   # AIService facade
├── providers/
│   ├── __init__.py
│   ├── base.py                  # Provider interface
│   ├── openai_provider.py       # OpenAI implementation
│   ├── anthropic_provider.py    # Claude implementation
│   └── ollama_provider.py       # Local model support
├── question_generator.py        # Generate quiz questions
├── writing_assistant.py         # Writing suggestions
├── masking_service.py           # Sensitive data detection
└── schemas.py
```

**Configuration:**
```python
# config.py additions
ai_provider: str = "openai"                    # openai, anthropic, ollama
ai_api_key: SecretStr | None = None
ai_model: str = "gpt-4o"
ai_base_url: str | None = None                 # For ollama/custom
ai_max_tokens: int = 2000
ai_temperature: float = 0.7
ai_rate_limit_per_minute: int = 20
```

#### D.2 Question Generation

**QuestionGenerator:**
```python
class QuestionGenerator:
    async def generate_questions(
        self,
        document_id: UUID,
        question_count: int = 5,
        question_types: list[QuestionType] = None,
        difficulty: Difficulty = Difficulty.MEDIUM,
    ) -> list[GeneratedQuestion]:
        """
        Generate quiz questions from document content.

        Steps:
        1. Extract document content (Markdown)
        2. Build prompt with question requirements
        3. Call AI provider
        4. Parse and validate response
        5. Return questions for human review
        """

    async def generate_from_multiple_sources(
        self,
        document_ids: list[UUID],
        external_urls: list[str] | None = None,
        question_count: int = 10,
    ) -> list[GeneratedQuestion]:
        """Generate questions from multiple sources."""
```

**API Endpoints:**
```
POST   /api/v1/ai/questions/generate           # Generate questions
POST   /api/v1/ai/questions/preview            # Preview without saving
GET    /api/v1/ai/questions/pending            # Questions awaiting review
POST   /api/v1/ai/questions/{id}/approve       # Approve generated question
POST   /api/v1/ai/questions/{id}/reject        # Reject generated question
PATCH  /api/v1/ai/questions/{id}               # Edit before approval
```

#### D.3 Writing Assistant

**WritingAssistant:**
```python
class WritingAssistant:
    async def suggest_completion(
        self,
        document_id: UUID,
        cursor_position: int,
        context_before: str,
        context_after: str,
    ) -> list[Suggestion]:
        """Suggest text completions at cursor position."""

    async def improve_text(
        self,
        text: str,
        improvement_type: ImprovementType,  # clarity, conciseness, grammar
    ) -> ImprovedText:
        """Suggest improvements to selected text."""

    async def generate_summary(
        self,
        document_id: UUID,
        length: SummaryLength,  # brief, standard, detailed
    ) -> str:
        """Generate document summary."""
```

**API Endpoints:**
```
POST   /api/v1/ai/suggest                      # Get text suggestions
POST   /api/v1/ai/improve                      # Improve selected text
POST   /api/v1/ai/summarize                    # Generate summary
POST   /api/v1/ai/explain                      # Explain complex text
```

#### D.4 Document Masking

**MaskingService:**
```python
class MaskingService:
    async def detect_sensitive(
        self,
        document_id: UUID,
    ) -> list[SensitiveSpan]:
        """
        Detect potentially sensitive content.

        Detects:
        - Personal names
        - Email addresses
        - Phone numbers
        - Company names
        - Financial figures
        - Medical terms
        - Custom patterns
        """

    async def apply_masking(
        self,
        document_id: UUID,
        spans_to_mask: list[SensitiveSpan],
    ) -> MaskedDocument:
        """Create masked version of document."""
```

#### D.5 AI Frontend

**New Components:**
```
frontend/src/components/ai/
├── QuestionGeneratorPanel.tsx   # Generate questions UI
├── QuestionReviewList.tsx       # Review generated questions
├── WritingAssistant.tsx         # Floating assistant panel
├── SuggestionPopover.tsx        # Inline suggestions
├── MaskingReviewPanel.tsx       # Review detected sensitive data
├── AiSettingsPanel.tsx          # AI configuration
└── index.ts
```

**Editor Integration:**
```typescript
// Add to editor toolbar
<WritingAssistantButton onClick={openAssistant} />

// Add suggestion popover
<SuggestionPopover
  suggestions={suggestions}
  onAccept={acceptSuggestion}
  onDismiss={dismissSuggestion}
/>
```

### Tests Required

**Backend:**
- Unit: Prompt construction
- Unit: Response parsing
- Integration: Question generation (mocked provider)
- Integration: Writing suggestions (mocked provider)

**Frontend:**
- Unit: QuestionReviewList rendering
- Unit: SuggestionPopover behavior
- Integration: Generate and review flow

### Verification Criteria

- [ ] AI provider configurable (OpenAI, Claude, Ollama)
- [ ] Questions generated from document content
- [ ] Generated questions require human review
- [ ] Writing suggestions appear in editor
- [ ] Sensitive data detection works
- [ ] All AI operations logged to audit
- [ ] Rate limiting enforced

---

## Implementation Timeline

### Parallel Work Opportunities

```
Week 1-2: Sprint A (Publishing)
├── Backend: PublishingService, themes, rendering
└── Frontend: SiteConfigPanel, ThemeEditor (parallel)

Week 3: Sprint B (Admin UI)
├── Backend: Minor API additions
└── Frontend: All new admin components

Week 4-5: Sprint C (MCP)
├── Backend: MCP server, service accounts
└── Frontend: ServiceAccountList, integration UI

Week 6+: Sprint D (AI)
├── Backend: AI providers, generators
└── Frontend: WritingAssistant, question review
```

### Dependencies

```
Sprint A (Publishing)
    └── No blockers, can start immediately

Sprint B (Admin UI)
    └── No blockers, can start immediately
    └── Better after A (adds Publishing tab)

Sprint C (MCP)
    └── Depends on: Access control (done)
    └── Depends on: Audit (done)

Sprint D (AI)
    └── Depends on: Learning module (done)
    └── Can integrate with MCP (optional)
```

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Publishing complexity | Start with SSR, optimize later |
| Custom domain setup | Document manual DNS, automate later |
| AI provider availability | Support multiple providers |
| AI cost management | Strict rate limiting, usage tracking |
| MCP protocol changes | Abstract behind interface |

---

## Success Metrics

### Sprint A (Publishing)
- Time to create and publish a site < 5 minutes
- Published site load time < 2 seconds
- Zero data leakage on private sites

### Sprint B (Admin UI)
- All compliance features configurable via UI
- Admin task completion rate > 95%
- Support ticket reduction for configuration

### Sprint C (MCP)
- API response time < 200ms
- Rate limiting effective (no abuse)
- 100% audit coverage

### Sprint D (AI)
- Question generation accuracy > 80%
- Writing suggestion acceptance rate > 30%
- AI response time < 3 seconds

---

## Sprint E: Diátaxis Type Revision (Original Sprint 14)

**Goal:** Move Diátaxis categorization from Space level to Page level for more flexible content organization.

**Priority:** P2 - Enhancement for better content organization

### Deliverables

#### E.1 Per-Page Diátaxis Tags

**Database Migration (012_diataxis_revision.py):**
```python
# Add diataxis_types to pages table
class Page(Base):
    # Existing fields...
    diataxis_types: list[str] = []  # Multiple types per page
    # e.g., ["tutorial", "how-to"]

# Remove diataxis_type from spaces (or keep for default)
class Space(Base):
    default_diataxis_type: str | None  # Optional default for new pages
```

**API Changes:**
```
PATCH  /api/v1/pages/{id}                    # Update diataxis_types array
GET    /api/v1/pages?diataxis_type=tutorial  # Filter by type
GET    /api/v1/search?type=how-to            # Search with type filter
```

#### E.2 Configurable Content Types

**New Components:**
```
frontend/src/components/admin/
├── ContentTypeManager.tsx       # Manage custom content types
├── ContentTypeEditor.tsx        # Create/edit content types
└── ContentTypeBadge.tsx         # Display type badge
```

**Features:**
- Organization-level custom content types beyond Diátaxis 4
- Custom type definitions with name, description, icon, color
- Type templates and guidelines
- Migration wizard for existing content

#### E.3 Migration

**Migration Script:**
```python
# migrate_diataxis_to_pages.py
async def migrate():
    # 1. For each space with diataxis_type
    # 2. Apply type to all pages in that space
    # 3. Keep space.default_diataxis_type for new pages
```

### Tests Required

**Backend:**
- Unit: Multiple diataxis types on page
- Unit: Custom content type CRUD
- Integration: Migration script
- Integration: Search with type filter

**Frontend:**
- Unit: ContentTypeManager rendering
- Unit: Multi-select type picker
- Integration: Type assignment flow

### Verification Criteria

- [ ] Pages can have multiple Diátaxis types
- [ ] Custom content types can be created per organization
- [ ] Migration preserves existing categorization
- [ ] Search filters by content type
- [ ] Type badges display correctly

---

## Sprint F: Metadata Portability (Original Sprint 15)

**Goal:** Store metadata alongside content in Git for full portability and backup.

**Priority:** P2 - Enhancement for data portability

### Deliverables

#### F.1 Filesystem Metadata Storage

**File Structure:**
```
repo/
├── spaces/
│   └── quality-management/
│       ├── _space.yaml              # Space metadata
│       └── pages/
│           └── sop-vial-inspection/
│               ├── content.json     # TipTap content
│               ├── _meta.yaml       # Page metadata
│               └── assets/          # Embedded images
```

**_meta.yaml Schema:**
```yaml
document_number: SOP-QMS-042
title: Vial Inspection Procedure
revision: B
version: "2.1"
status: effective
diataxis_types:
  - how-to
classification: internal
owner_email: sarah@company.com
custodian_email: james@company.com
effective_date: 2025-01-15
next_review_date: 2026-01-15
review_cycle_months: 12
retention_years: 7
supersedes: SOP-QMS-041
tags:
  - quality
  - manufacturing
  - inspection
```

#### F.2 Export/Import

**New Files:**
```
backend/src/modules/portability/
├── __init__.py
├── exporter.py              # Export to portable format
├── importer.py              # Import from external systems
├── confluence_adapter.py    # Confluence import
├── sharepoint_adapter.py    # SharePoint import
├── markdown_adapter.py      # Markdown folder import
└── schemas.py
```

**API Endpoints:**
```
POST   /api/v1/export/space/{id}              # Export space to ZIP
POST   /api/v1/export/pages                   # Export selected pages
POST   /api/v1/import/upload                  # Upload import file
POST   /api/v1/import/preview                 # Preview import changes
POST   /api/v1/import/execute                 # Execute import
GET    /api/v1/import/status/{job_id}         # Import job status
```

**Frontend Components:**
```
frontend/src/components/portability/
├── ExportWizard.tsx         # Export configuration
├── ImportWizard.tsx         # Multi-step import wizard
├── ImportPreview.tsx        # Preview changes before import
├── ConflictResolver.tsx     # Resolve import conflicts
├── ImportProgress.tsx       # Progress indicator
└── index.ts
```

#### F.3 Metadata Schema Validation

**Features:**
- JSON Schema for metadata validation
- Schema versioning for backward compatibility
- Validation on import
- Custom metadata fields per organization

### Tests Required

**Backend:**
- Unit: YAML serialization/deserialization
- Unit: Schema validation
- Unit: Confluence adapter parsing
- Integration: Full export/import cycle
- Integration: Conflict resolution

**Frontend:**
- Unit: ImportWizard step navigation
- Unit: ConflictResolver rendering
- Integration: Import workflow

### Verification Criteria

- [ ] Metadata stored in Git alongside content
- [ ] Export creates valid ZIP with all metadata
- [ ] Import from Confluence works
- [ ] Import preview shows accurate changes
- [ ] Conflicts can be resolved manually
- [ ] Custom metadata fields supported

---

## Sprint G: System Documentation (Original Sprint 16)

**Goal:** Create comprehensive system documentation using Diátaxis framework.

**Priority:** P2 - Required for user adoption

### Deliverables

#### G.1 Diátaxis-Structured Documentation

**Documentation Structure:**
```
docs/
├── tutorials/
│   ├── getting-started.md           # First-time user guide
│   ├── create-first-document.md     # Create and publish doc
│   ├── set-up-approval-workflow.md  # Configure approvals
│   └── complete-training.md         # User training completion
├── how-to/
│   ├── configure-document-numbering.md
│   ├── set-up-retention-policies.md
│   ├── create-acknowledgment-campaign.md
│   ├── verify-audit-trail.md
│   ├── configure-git-remote.md
│   ├── publish-documentation-site.md
│   └── integrate-with-mcp.md
├── reference/
│   ├── api/
│   │   ├── authentication.md
│   │   ├── content.md
│   │   ├── document-control.md
│   │   ├── signatures.md
│   │   ├── audit.md
│   │   └── learning.md
│   ├── configuration.md
│   ├── permissions.md
│   ├── document-lifecycle.md
│   └── compliance-matrix.md
└── explanation/
    ├── architecture.md
    ├── git-abstraction.md
    ├── compliance-approach.md
    ├── security-model.md
    └── design-decisions.md
```

#### G.2 Fixture-Based Installation

**Seed Data:**
```
backend/fixtures/
├── demo_organization.yaml
├── demo_users.yaml
├── demo_spaces.yaml
├── demo_pages.yaml
├── demo_approval_matrices.yaml
├── demo_retention_policies.yaml
└── demo_assessments.yaml
```

**CLI Command:**
```bash
# Install with demo data
python -m docservice.cli seed --fixture demo

# Install minimal (empty org)
python -m docservice.cli seed --fixture minimal
```

#### G.3 Interactive Tutorials

**Features:**
- Guided walkthroughs with step highlighting
- Interactive demos embedded in docs
- Video tutorial links
- FAQ and troubleshooting section
- Contextual help tooltips in UI

**New Components:**
```
frontend/src/components/help/
├── GuidedTour.tsx           # Step-by-step tour
├── HelpTooltip.tsx          # Contextual help
├── VideoEmbed.tsx           # Embedded tutorials
├── FAQAccordion.tsx         # FAQ section
└── index.ts
```

### Tests Required

**Documentation:**
- All code examples tested and working
- Screenshots up to date
- Links validated

**Backend:**
- Unit: Fixture loading
- Integration: Seed command execution

**Frontend:**
- Unit: GuidedTour rendering
- Integration: Tour completion tracking

### Verification Criteria

- [ ] All four Diátaxis categories have content
- [ ] Getting started tutorial < 15 minutes
- [ ] API reference is complete and accurate
- [ ] Fixture installation creates working demo
- [ ] Guided tours work for key workflows

---

## Sprint H: Reader UI & Accessibility (Original Sprint 17)

**Goal:** Optimize the reading experience and achieve WCAG 2.1 AA compliance.

**Priority:** P2 - Required for enterprise adoption

### Deliverables

#### H.1 WCAG 2.1 AA Accessibility

**Requirements:**
```
Perceivable:
- Alt text for all images
- High contrast mode (4.5:1 ratio)
- Resizable text (up to 200%)
- No information conveyed by color alone
- Dark mode / Light mode toggle
- Dyslexic-friendly fonts (OpenDyslexic, Lexie Readable)

Operable:
- Full keyboard navigation
- Skip links to main content
- No keyboard traps
- Focus indicators visible
- No time limits (or adjustable)

Understandable:
- Clear error messages
- Consistent navigation
- Input labels and instructions
- Language declaration

Robust:
- Semantic HTML
- ARIA labels where needed
- Screen reader tested (NVDA, VoiceOver)
```

**New Components:**
```
frontend/src/components/accessibility/
├── SkipLinks.tsx            # Skip to content links
├── HighContrastToggle.tsx   # High contrast mode
├── ThemeToggle.tsx          # Dark/Light mode switch
├── FontSizeControl.tsx      # Text size adjustment
├── DyslexicFontToggle.tsx   # Dyslexic-friendly fonts
├── FocusIndicator.tsx       # Custom focus styles
└── index.ts
```

#### H.2 Context Menu (GitBook-style)

**Features:**
- Right-click context menu for pages
- Copy link to section
- Copy page as Markdown (for LLMs)
- View as Markdown (plain text view)
- Open in ChatGPT (launch with page context)
- Open in Claude (launch with page context)
- Connect with MCP (copy MCP server URL)
- Connect to VSCode (install MCP server instructions)
- Print document
- Export as PDF/Markdown/DOCX
- Add to favorites
- Share options

**New Components:**
```
frontend/src/components/reader/
├── ContextMenu.tsx          # Right-click menu
├── ShareDialog.tsx          # Share options
├── PrintView.tsx            # Print-optimized view
├── MarkdownView.tsx         # Plain text/Markdown view
├── AiIntegrationMenu.tsx    # ChatGPT/Claude/MCP options
└── index.ts
```

#### H.3 Reading Aids

**Features:**
- Table of contents sidebar (auto-generated from headings)
- Progress indicator for long documents
- Estimated reading time
- Breadcrumb trail
- Previous/Next page navigation
- Scroll-to-top button
- Reading position memory
- Speed reader mode (RSVP - Rapid Serial Visual Presentation, similar to leto.axym.org)
- Rabbit-hole links (inline expandable previews, similar to mystmd.org)
- Focus mode (hide navigation, maximize reading area)

**New Components:**
```
frontend/src/components/reader/
├── TableOfContents.tsx      # Auto-generated TOC
├── ReadingProgress.tsx      # Progress bar
├── ReadingTime.tsx          # Time estimate
├── PageNavigation.tsx       # Prev/Next buttons
├── ScrollToTop.tsx          # Return to top
├── ReadingPosition.tsx      # Remember position
├── SpeedReader.tsx          # RSVP speed reading mode
├── RabbitHoleLink.tsx       # Inline expandable link previews
├── FocusMode.tsx            # Distraction-free reading
└── index.ts
```

**Speed Reader Features:**
- Adjustable words-per-minute (100-1000 WPM)
- Pause/resume controls
- Progress indicator
- Keyboard shortcuts (space to pause, arrows to adjust speed)
- Word highlighting in context

**Rabbit-Hole Links:**
- Hover to preview linked page content
- Click to expand inline without navigation
- Nested expansion support
- Back-links display (pages linking to current page)

#### H.4 Print and Export

**Features:**
- Print-optimized CSS
- PDF generation with headers/footers
- Export to Markdown
- Export to DOCX
- Batch export functionality

**API Endpoints:**
```
POST   /api/v1/export/pdf/{page_id}           # Generate PDF
POST   /api/v1/export/docx/{page_id}          # Generate DOCX
POST   /api/v1/export/markdown/{page_id}      # Export as Markdown
POST   /api/v1/export/batch                   # Batch export
GET    /api/v1/export/status/{job_id}         # Export job status
```

**Backend:**
```
backend/src/modules/export/
├── __init__.py
├── pdf_generator.py         # PDF with WeasyPrint
├── docx_generator.py        # DOCX with python-docx
├── markdown_exporter.py     # Markdown conversion
└── schemas.py
```

### Tests Required

**Accessibility:**
- Automated: axe-core accessibility testing
- Manual: Keyboard navigation test
- Manual: Screen reader test (VoiceOver, NVDA)
- Contrast ratio verification

**Backend:**
- Unit: PDF generation
- Unit: DOCX generation
- Integration: Batch export

**Frontend:**
- Unit: ContextMenu rendering
- Unit: TableOfContents generation
- Integration: Export workflow

### Verification Criteria

- [ ] WCAG 2.1 AA audit passes (0 critical, < 5 minor issues)
- [ ] All features keyboard accessible
- [ ] Screen reader announces content correctly
- [ ] High contrast mode has 4.5:1 ratio
- [ ] Dark/Light mode toggle works
- [ ] Dyslexic fonts render correctly
- [ ] Speed reader mode functional with keyboard controls
- [ ] Rabbit-hole links expand inline correctly
- [ ] Context menu includes all AI integration options
- [ ] Copy as Markdown produces valid LLM-ready output
- [ ] PDF export includes headers/footers
- [ ] DOCX export preserves formatting
- [ ] Batch export handles 100+ pages

---

## Sprint I: Performance & Operations (New)

**Goal:** Optimize performance and add production monitoring.

**Priority:** P2 - Required for production readiness

### Deliverables

#### I.1 Caching Layer

**Redis Integration:**
```python
# config.py additions
redis_url: str = "redis://localhost:6379"
cache_ttl_seconds: int = 300
cache_enabled: bool = True

# New service
backend/src/modules/cache/
├── __init__.py
├── service.py               # CacheService
├── decorators.py            # @cached decorator
└── keys.py                  # Cache key patterns
```

**Cached Operations:**
- Page content (5 min TTL)
- Search results (2 min TTL)
- User permissions (5 min TTL)
- Navigation tree (10 min TTL)

#### I.2 Frontend Optimization

**Features:**
- Code splitting by route
- Lazy loading for heavy components
- Image optimization (WebP, lazy load)
- Bundle size analysis and reduction
- Service worker for offline support

**Configuration:**
```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        editor: ['@tiptap/react', '@tiptap/starter-kit'],
        charts: ['recharts'],
        admin: ['./src/pages/AdminPage'],
      }
    }
  }
}
```

#### I.3 Database Optimization

**Features:**
- Query analysis and optimization
- Index tuning
- Connection pooling (pgBouncer)
- Slow query logging and alerting
- Read replica support

**Migrations:**
```python
# Add missing indexes
CREATE INDEX idx_pages_space_id ON pages(space_id);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX idx_audit_events_resource ON audit_events(resource_type, resource_id);
CREATE INDEX idx_permissions_user_resource ON permissions(user_id, resource_type, resource_id);
```

#### I.4 Monitoring & Observability

**Stack:**
- Prometheus for metrics
- Grafana for dashboards
- Loki for log aggregation
- Alertmanager for alerts

**Metrics to Track:**
```python
# Custom metrics
api_request_duration_seconds
api_request_total
database_query_duration_seconds
cache_hit_total
cache_miss_total
git_operation_duration_seconds
active_users_gauge
audit_events_total
```

**Dashboards:**
- System health overview
- API performance
- Database performance
- User activity
- Error rates

### Tests Required

**Backend:**
- Load testing with Locust (1000 concurrent users)
- Cache hit/miss verification
- Database query performance

**Frontend:**
- Lighthouse performance score > 90
- Bundle size < 500KB (initial)
- Time to interactive < 3s

### Verification Criteria

- [ ] Page load time < 2s (p95)
- [ ] API response time < 200ms (p50)
- [ ] Cache hit rate > 80%
- [ ] Database queries < 100ms (p99)
- [ ] Lighthouse performance score > 90
- [ ] Monitoring dashboards operational
- [ ] Alerts configured for critical metrics

---

## Updated Implementation Timeline

### Phase 1: Core Platform (Completed)
- Sprints 1-9, 9.5, 13: Foundation through Learning + Git Remote

### Phase 2: Go-to-Market (Current)
- Sprint A (Publishing): ✅ Completed
- Sprint B (Admin UI): Next
- Sprint C (MCP): Following
- Sprint D (AI): Optional for MVP

### Phase 3: Enhancement
- Sprint E (Diátaxis Revision)
- Sprint F (Metadata Portability)

### Phase 4: Polish
- Sprint G (System Documentation)
- Sprint H (Reader UI & Accessibility)
- Sprint I (Performance & Operations)

### Dependencies

```
Phase 2 (Go-to-Market)
├── Sprint A (Publishing) ✅
├── Sprint B (Admin UI)
├── Sprint C (MCP)
└── Sprint D (AI)

Phase 3 (Enhancement)
├── Sprint E (Diátaxis) - Can start after Phase 2
└── Sprint F (Portability) - Can start after Phase 2

Phase 4 (Polish)
├── Sprint G (Documentation) - Can start after Phase 3
├── Sprint H (Accessibility) - Can start after Phase 3
└── Sprint I (Performance) - Can start anytime after Phase 2
```

---

## Success Metrics (Updated)

### Sprint E (Diátaxis Revision)
- Migration completes without data loss
- Users can assign multiple types per page
- Search by type returns accurate results

### Sprint F (Metadata Portability)
- Export/import cycle preserves all data
- Confluence import success rate > 95%
- Import preview accuracy > 99%

### Sprint G (System Documentation)
- Documentation coverage > 90% of features
- Getting started completion rate > 80%
- Support tickets reduced by 30%

### Sprint H (Reader UI & Accessibility)
- WCAG 2.1 AA compliance (0 critical issues)
- PDF export accuracy > 99%
- User satisfaction with reader UI > 4.5/5

### Sprint I (Performance)
- Page load time < 2s (p95)
- API latency < 200ms (p50)
- Uptime > 99.5%

---

## Appendix: File Changes Summary

### New Backend Files
```
# Phase 2
backend/src/modules/publishing/          # Sprint A
backend/src/modules/mcp/                 # Sprint C
backend/src/modules/ai/                  # Sprint D
backend/alembic/versions/009_publishing.py
backend/alembic/versions/010_mcp.py
backend/alembic/versions/011_ai.py

# Phase 3
backend/alembic/versions/012_diataxis_revision.py  # Sprint E
backend/src/modules/portability/         # Sprint F

# Phase 4
backend/fixtures/                        # Sprint G
backend/src/modules/export/              # Sprint H
backend/src/modules/cache/               # Sprint I
```

### New Frontend Files
```
# Phase 2
frontend/src/components/publishing/      # Sprint A
frontend/src/components/admin/           # Sprint B
frontend/src/components/mcp/             # Sprint C
frontend/src/components/ai/              # Sprint D
frontend/src/pages/SiteSettingsPage.tsx
frontend/src/pages/PublishedSitePage.tsx

# Phase 3
frontend/src/components/admin/ContentTypeManager.tsx  # Sprint E
frontend/src/components/portability/     # Sprint F

# Phase 4
frontend/src/components/help/            # Sprint G
frontend/src/components/accessibility/   # Sprint H
frontend/src/components/reader/          # Sprint H
```

### Modified Files
```
frontend/src/pages/AdminPage.tsx         # Add new tabs
frontend/src/lib/api.ts                  # Add new API clients
backend/src/api/router.py                # Register new routers
backend/src/config.py                    # Add AI, cache, monitoring settings
backend/src/db/models/page.py            # Add diataxis_types array (Sprint E)
```
