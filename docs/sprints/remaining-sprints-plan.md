# Remaining Sprints Plan

## Executive Summary

**Completed Sprints:** 1-9, 13, A, B, C, D, F
**Remaining Sprints:** E, G, H, I, J (+ AI Features unscheduled)

### Completed Work

| Phase | Sprint | Focus | Status |
|-------|--------|-------|--------|
| 1 (Core) | 1-9, 13 | Foundation through Learning + Git Remote | Done |
| 2 (Go-to-Market) | A | Publishing (sites, themes, rendering) | Done |
| 2 | B | Admin UI (compliance config, user mgmt) | Done |
| 2 | C | MCP Integration (AI agent API, service accounts) | Done |
| 2 | D | Integrated Access Control (visitors, classification, content transformer) | Done |
| 2 | F | Attachments & Media (storage backend, upload/download, editor integration) | Done |

### Remaining Work

| Phase | Sprint | Focus | Est. Effort |
|-------|--------|-------|-------------|
| 3 (Enhancement) | E | Diataxis Revision | 1 week |
| 3 | G | Metadata Portability | 2 weeks |
| 4 (Polish) | H | System Documentation | 1 week |
| 4 | I | Reader UI & Accessibility | 2 weeks |
| 4 | J | Performance & Operations | 2 weeks |
| Unscheduled | TBD | AI Features (question gen, writing assistant) | 2 weeks |

---

## Current State Assessment

### Backend (Complete)
- Authentication & sessions (Sprint 1)
- Content hierarchy: Org -> Workspace -> Space -> Page (Sprint 3)
- Block-based editor with TipTap (Sprint 2)
- Git-based version control (Sprint 4)
- Change requests & diff (Sprint 4)
- Access control with permissions & classification (Sprint 5)
- Document control with lifecycle (Sprint 6)
- Electronic signatures - 21 CFR Part 11 (Sprint 7)
- Audit trail with hash chain (Sprint 8)
- Learning module with assessments (Sprint 9)
- Git remote sync (Sprint 13)
- Publishing engine with themes (Sprint A)
- Admin UI configuration (Sprint B)
- MCP server + service accounts (Sprint C)
- Integrated access control for published sites (Sprint D)
- Attachment storage, versioning, and API (Sprint F)

### Frontend (Complete)
- Editor with TipTap + slash commands
- Navigation & search
- Version control UI
- Signature dialogs
- Audit viewer
- Learning components
- Admin page with all tabs
- Publishing config, theme editor, public site viewer
- Visitor management, discovery settings, publish preview
- Attachment uploader, file cards, gallery, drag-and-drop image upload

---

## Sprint E: Diataxis Type Revision (1 week)

**Goal:** Move Diataxis categorization from Space level to Page level for more flexible content organization.

**Priority:** P2 - Enhancement for better content organization

### Deliverables

#### E.1 Per-Page Diataxis Tags

**Database Migration:**
```python
# Add diataxis_types to pages table
op.add_column("pages", sa.Column("diataxis_types", JSONB, server_default="[]"))

# Keep space.default_diataxis_type for new page defaults
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
- Organization-level custom content types beyond Diataxis 4
- Custom type definitions with name, description, icon, color
- Type templates and guidelines
- Migration wizard for existing content

#### E.3 Migration

```python
# migrate_diataxis_to_pages.py
# 1. For each space with diataxis_type
# 2. Apply type to all pages in that space
# 3. Keep space.default_diataxis_type for new pages
```

### Verification Criteria

- [ ] Pages can have multiple Diataxis types
- [ ] Custom content types can be created per organization
- [ ] Migration preserves existing categorization
- [ ] Search filters by content type
- [ ] Type badges display correctly

---

## Sprint G: Metadata Portability (2 weeks)

**Goal:** Store metadata alongside content in Git for full portability and backup.

**Priority:** P2 - Enhancement for data portability

### Deliverables

#### G.1 Filesystem Metadata Storage

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
│               ├── *.attachments.md # Attachment manifest (Sprint F)
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

#### G.2 Export/Import

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

### Verification Criteria

- [ ] Metadata stored in Git alongside content
- [ ] Export creates valid ZIP with all metadata
- [ ] Import from Confluence works
- [ ] Import preview shows accurate changes
- [ ] Conflicts can be resolved manually
- [ ] Custom metadata fields supported

---

## Sprint H: System Documentation (1 week)

**Goal:** Create comprehensive system documentation using Diataxis framework.

**Priority:** P2 - Required for user adoption

### Deliverables

#### H.1 Diataxis-Structured Documentation

```
docs/
├── tutorials/
│   ├── getting-started.md
│   ├── create-first-document.md
│   ├── set-up-approval-workflow.md
│   └── complete-training.md
├── how-to/
│   ├── configure-document-numbering.md
│   ├── set-up-retention-policies.md
│   ├── publish-documentation-site.md
│   ├── manage-attachments.md
│   └── integrate-with-mcp.md
├── reference/
│   ├── api/
│   │   ├── authentication.md
│   │   ├── content.md
│   │   ├── document-control.md
│   │   ├── signatures.md
│   │   ├── audit.md
│   │   ├── learning.md
│   │   └── attachments.md
│   ├── configuration.md
│   ├── permissions.md
│   └── compliance-matrix.md
└── explanation/
    ├── architecture.md
    ├── git-abstraction.md
    ├── compliance-approach.md
    └── security-model.md
```

#### H.2 Fixture-Based Installation

```bash
python -m docservice.cli seed --fixture demo     # Full demo data
python -m docservice.cli seed --fixture minimal   # Empty org
```

#### H.3 Interactive Tutorials

```
frontend/src/components/help/
├── GuidedTour.tsx           # Step-by-step tour
├── HelpTooltip.tsx          # Contextual help
├── VideoEmbed.tsx           # Embedded tutorials
├── FAQAccordion.tsx         # FAQ section
└── index.ts
```

### Verification Criteria

- [ ] All four Diataxis categories have content
- [ ] Getting started tutorial < 15 minutes
- [ ] API reference is complete and accurate
- [ ] Fixture installation creates working demo

---

## Sprint I: Reader UI & Accessibility (2 weeks)

**Goal:** Optimize the reading experience and achieve WCAG 2.1 AA compliance.

**Priority:** P2 - Required for enterprise adoption

### Deliverables

#### I.1 WCAG 2.1 AA Accessibility

```
frontend/src/components/accessibility/
├── SkipLinks.tsx            # Skip to content links
├── HighContrastToggle.tsx   # High contrast mode
├── ThemeToggle.tsx          # Dark/Light mode switch
├── FontSizeControl.tsx      # Text size adjustment
├── DyslexicFontToggle.tsx   # Dyslexic-friendly fonts
└── index.ts
```

#### I.2 Context Menu (GitBook-style)

```
frontend/src/components/reader/
├── ContextMenu.tsx          # Right-click menu
├── ShareDialog.tsx          # Share options
├── PrintView.tsx            # Print-optimized view
├── MarkdownView.tsx         # Copy as Markdown for LLMs
├── AiIntegrationMenu.tsx    # ChatGPT/Claude/MCP options
└── index.ts
```

#### I.3 Reading Aids

```
frontend/src/components/reader/
├── TableOfContents.tsx      # Auto-generated TOC
├── ReadingProgress.tsx      # Progress bar
├── SpeedReader.tsx          # RSVP speed reading mode
├── RabbitHoleLink.tsx       # Inline expandable link previews
├── FocusMode.tsx            # Distraction-free reading
└── index.ts
```

#### I.4 Print and Export

```
backend/src/modules/export/
├── __init__.py
├── pdf_generator.py         # PDF with WeasyPrint
├── docx_generator.py        # DOCX with python-docx
├── markdown_exporter.py     # Markdown conversion
└── schemas.py
```

### Verification Criteria

- [ ] WCAG 2.1 AA audit passes (0 critical issues)
- [ ] Full keyboard navigation
- [ ] Screen reader announces content correctly
- [ ] Speed reader mode functional
- [ ] PDF/DOCX export preserves formatting
- [ ] Batch export handles 100+ pages

---

## Sprint J: Performance & Operations (2 weeks)

**Goal:** Optimize performance and add production monitoring.

**Priority:** P2 - Required for production readiness

### Deliverables

#### J.1 Caching Layer

```
backend/src/modules/cache/
├── __init__.py
├── service.py               # CacheService
├── decorators.py            # @cached decorator
└── keys.py                  # Cache key patterns
```

Cached operations: page content, search results, user permissions, navigation tree.

#### J.2 Frontend Optimization

- Code splitting by route
- Lazy loading for heavy components (editor, admin)
- Image optimization (WebP, lazy load)
- Bundle size analysis and reduction

#### J.3 Database Optimization

- Query analysis and index tuning
- Connection pooling
- Slow query logging

#### J.4 Monitoring & Observability

- Prometheus metrics
- Grafana dashboards (system health, API performance, user activity)
- Alertmanager configuration
- Load testing with Locust

### Verification Criteria

- [ ] Page load time < 2s (p95)
- [ ] API response time < 200ms (p50)
- [ ] Cache hit rate > 80%
- [ ] Lighthouse performance score > 90
- [ ] Monitoring dashboards operational
- [ ] Alerts configured for critical metrics

---

## Unscheduled: AI Features (2 weeks)

**Goal:** Add AI-powered features for question generation and writing assistance.

**Priority:** P3 - Nice-to-have differentiation. Can be inserted into any phase.

### Deliverables

#### AI Service Infrastructure

```
backend/src/modules/ai/
├── __init__.py
├── service.py                   # AIService facade
├── providers/
│   ├── base.py                  # Provider interface
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── ollama_provider.py       # Local model support
├── question_generator.py
├── writing_assistant.py
├── masking_service.py
└── schemas.py
```

#### Question Generation

```
POST   /api/v1/ai/questions/generate
POST   /api/v1/ai/questions/preview
GET    /api/v1/ai/questions/pending
POST   /api/v1/ai/questions/{id}/approve
```

#### Writing Assistant

```
POST   /api/v1/ai/suggest
POST   /api/v1/ai/improve
POST   /api/v1/ai/summarize
```

#### Document Masking

Detect and mask sensitive content (names, emails, financial figures, medical terms).

#### Frontend

```
frontend/src/components/ai/
├── QuestionGeneratorPanel.tsx
├── QuestionReviewList.tsx
├── WritingAssistant.tsx
├── SuggestionPopover.tsx
├── MaskingReviewPanel.tsx
└── index.ts
```

### Verification Criteria

- [ ] AI provider configurable (OpenAI, Claude, Ollama)
- [ ] Questions generated from document content
- [ ] Generated questions require human review
- [ ] Writing suggestions appear in editor
- [ ] All AI operations logged to audit

---

## Implementation Timeline

### Dependencies

```
Phase 2 (Go-to-Market) - DONE
├── Sprint A (Publishing) ✅
├── Sprint B (Admin UI) ✅
├── Sprint C (MCP) ✅
├── Sprint D (Access Control) ✅
└── Sprint F (Attachments) ✅

Phase 3 (Enhancement) - NEXT
├── Sprint E (Diataxis) - No blockers
└── Sprint G (Portability) - No blockers

Phase 4 (Polish)
├── Sprint H (Documentation) - After Phase 3
├── Sprint I (Accessibility) - After Phase 3
└── Sprint J (Performance) - Can start anytime
```

### Parallel Work Opportunities

- Sprints E and G are independent and can run in parallel
- Sprint J (Performance) can start independently of Phase 3
- AI Features can be inserted anywhere

---

## Success Metrics

### Sprint E (Diataxis Revision)
- Migration completes without data loss
- Users can assign multiple types per page
- Search by type returns accurate results

### Sprint G (Metadata Portability)
- Export/import cycle preserves all data
- Confluence import success rate > 95%
- Import preview accuracy > 99%

### Sprint H (System Documentation)
- Documentation coverage > 90% of features
- Getting started completion rate > 80%

### Sprint I (Reader UI & Accessibility)
- WCAG 2.1 AA compliance (0 critical issues)
- PDF export accuracy > 99%

### Sprint J (Performance)
- Page load time < 2s (p95)
- API latency < 200ms (p50)
- Uptime > 99.5%

---

## Appendix: File Changes Summary

### Existing Backend Modules
```
backend/src/modules/access/           # Sprint 5 + D
backend/src/modules/attachments/      # Sprint F
backend/src/modules/audit/            # Sprint 8
backend/src/modules/content/          # Sprint 1-4
backend/src/modules/document_control/ # Sprint 6-7
backend/src/modules/learning/         # Sprint 9
backend/src/modules/mcp/             # Sprint C
backend/src/modules/publishing/       # Sprint A + D
```

### New Backend Modules (Remaining)
```
backend/src/modules/portability/      # Sprint G
backend/src/modules/export/           # Sprint I
backend/src/modules/cache/            # Sprint J
backend/src/modules/ai/              # AI Features (unscheduled)
```

### Existing Migrations
```
backend/alembic/versions/001-008     # Core platform
backend/alembic/versions/009_publishing.py
backend/alembic/versions/010_admin_ui_completion.py
backend/alembic/versions/011_mcp_integration.py
backend/alembic/versions/012_integrated_access_control.py
backend/alembic/versions/013_attachments.py
```
