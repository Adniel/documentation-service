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

## Appendix: File Changes Summary

### New Backend Files
```
backend/src/modules/publishing/          # Sprint A
backend/src/modules/mcp/                 # Sprint C
backend/src/modules/ai/                  # Sprint D
backend/alembic/versions/009_publishing.py
backend/alembic/versions/010_mcp.py
backend/alembic/versions/011_ai.py
```

### New Frontend Files
```
frontend/src/components/publishing/      # Sprint A
frontend/src/components/admin/           # Sprint B
frontend/src/components/mcp/             # Sprint C
frontend/src/components/ai/              # Sprint D
frontend/src/pages/SiteSettingsPage.tsx
frontend/src/pages/PublishedSitePage.tsx
```

### Modified Files
```
frontend/src/pages/AdminPage.tsx         # Add new tabs
frontend/src/lib/api.ts                  # Add new API clients
backend/src/api/router.py                # Register new routers
backend/src/config.py                    # Add AI settings
```
