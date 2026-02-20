# Sprint Implementation Order - Quick Reference

## Phase 1: Core Platform (Complete)

Sprints 1-9, 13 delivered the foundational platform: auth, content hierarchy,
editor, version control, access control, document control, e-signatures,
audit trail, learning module, and Git remote sync.

## Phase 2: Go-to-Market (Complete)

| Priority | Sprint | Focus | Status |
|----------|--------|-------|--------|
| **P0** | A | Publishing | Done |
| **P0** | B | Admin UI | Done |
| **P1** | C | MCP Integration | Done |
| **P1** | D | Integrated Access Control | Done |
| **P1** | F | Attachments & Media | Done |

## Phase 3: Enhancement (Complete)

| Priority | Sprint | Focus | Status |
|----------|--------|-------|--------|
| **P2** | E | Diataxis Revision | Done |
| **P2** | G | Metadata Portability | Done |

## Phase 4: Polish

| Priority | Sprint | Focus | Est. Effort | Key Deliverable |
|----------|--------|-------|-------------|-----------------|
| **P2** | H | System Documentation | 1 week | Diataxis-structured docs, fixtures |
| **P2** | I | Reader UI & Accessibility | 2 weeks | WCAG 2.1 AA, PDF/DOCX export |
| **P2** | J | Performance & Operations | 2 weeks | Caching, monitoring, optimization |

## Unscheduled

| Sprint | Focus | Notes |
|--------|-------|-------|
| TBD | AI Features | Question generation, writing assistant, masking. Can be added to any phase. |

---

## What Was Completed in Each Sprint

### Sprint A: Publishing
- [x] Database models (PublishedSite, Theme)
- [x] PublishingService, ThemeService, PageRenderer
- [x] Site CRUD API endpoints + public site routes
- [x] SiteConfigPanel, ThemeEditor frontend
- [x] Public site viewer

### Sprint B: Admin UI
- [x] UserManagement, UserRoleEditor
- [x] OrganizationSettings, DocumentNumberingConfig
- [x] AuditDashboard, AuditExportPanel
- [x] All compliance features configurable via UI

### Sprint C: MCP Integration
- [x] MCP server with tool implementations
- [x] ServiceAccount model + API key auth
- [x] Rate limiting + usage tracking
- [x] ServiceAccountList frontend

### Sprint D: Integrated Access Control
- [x] SiteVisitor and SiteVisitorRole models
- [x] ClassificationService with inheritance chain
- [x] ContentTransformer for access-filtered rendering
- [x] PublishedSiteAccessService, PublishValidator
- [x] SSOBridge for internal/external user mapping
- [x] VisitorManagement, DiscoverySettings, PublishPreview frontend
- [x] RestrictedPagePlaceholder component

### Sprint F: Attachments & Media
- [x] Attachment model with versioning and SHA-256 hashes
- [x] StorageBackend abstraction (LocalFilesystem + S3)
- [x] AttachmentService (upload, download, replace, soft-delete, manifest)
- [x] Attachment API endpoints (upload, content, thumbnail, list, replace, delete, public)
- [x] TipTap extensions (FileAttachment, AttachmentList, ImageUpload with drag-and-drop/paste)
- [x] React components (AttachmentUploader, FileAttachmentCard, AttachmentGallery)
- [x] Slash commands (/image, /file, /attachment-list)
- [x] attachmentApi in frontend API client

### Sprint E: Diataxis Revision
- [x] Per-page diataxis_types JSONB field with GIN index
- [x] Space-to-page type inheritance
- [x] DiataxisTypePicker frontend component
- [x] Search and navigation updated for array field

### Sprint G: Metadata Portability
- [x] PageMeta, SpaceMeta, WorkspaceMeta YAML schemas
- [x] MetadataSyncService (write _meta.yaml alongside content in Git)
- [x] ExportService (ZIP generation for org/workspace/space)
- [x] ImportService with preview, conflict detection, and execution
- [x] MarkdownAdapter (folder import with frontmatter)
- [x] ConfluenceAdapter (HTML-to-TipTap conversion)
- [x] Portability API endpoints (/portability/export, /portability/import/*)
- [x] portabilityApi in frontend API client
- [x] ExportWizard, ImportWizard, ImportPreview, ConflictResolver, ImportProgress components

---

## Remaining Sprint Details

### Sprint E: Diataxis Revision (1 week)

**Days 1-2**
- [x] Database migration for diataxis_types JSONB array on pages (014_diataxis_revision.py)
- [x] Page model updated with diataxis_types field
- [x] Pydantic schemas updated (PageCreate, PageUpdate, PageResponse, PageSummary)
- [x] Content service: create_page inherits from space, update_page handles types
- [x] List pages API supports diataxis_type filter
- [x] Search service and API updated for per-page diataxis_types array

**Days 3-4**
- [x] Navigation service includes diataxis_types in page nodes
- [x] Frontend types and API client updated
- [x] DiataxisTypePicker component (multi-select badge picker)
- [x] SearchResultsPage updated for diataxis_types array
- [ ] ContentTypeManager admin component (custom types - deferred)
- [ ] ContentTypeEditor for custom types (deferred)

**Day 5**
- [x] Data migration: pages inherit space diataxis_type in migration
- [x] Unit tests (test_diataxis_revision.py)
- [x] Integration tests (test_diataxis_api.py)

**Milestone:** Pages can have multiple Diataxis types. Custom content types deferred to future sprint.

---

### Sprint G: Metadata Portability (2 weeks)

**Week 1**
- [x] Define _meta.yaml schema (PageMeta, SpaceMeta, WorkspaceMeta Pydantic models)
- [x] Implement filesystem metadata storage (MetadataSyncService)
- [x] Sync service between DB and filesystem (write _meta.yaml on page create/update)
- [x] Export API endpoints (ExportService + /portability/export)
- [x] ExportManifest with format version, statistics

**Week 2**
- [x] ImportWizard frontend component (multi-step: upload, preview, execute)
- [x] Confluence adapter (HTML-to-TipTap conversion)
- [x] Markdown adapter (folder import with frontmatter support)
- [ ] SharePoint adapter (deferred - low demand)
- [x] Conflict resolution UI (ConflictResolver component with skip/overwrite/rename)
- [x] ExportWizard, ImportPreview, ImportProgress frontend components
- [x] Unit tests (test_portability_metadata.py, test_exporter.py, test_importer.py)
- [x] Integration tests (test_portability_api.py)

**Milestone:** Metadata stored in Git alongside content. Export/import works. Confluence migration supported.

---

### Sprint H: System Documentation (1 week) ✅

- [x] Tutorials: Getting started, create first document, approval workflow, training
- [x] How-to guides: Document numbering, retention, publishing, attachments, MCP, import/export
- [x] Reference: API documentation (7 endpoint groups), configuration, permissions, compliance matrix
- [x] Explanation: Architecture, git abstraction, compliance approach, security model
- [x] Fixture data for demo organization (DEMO_FIXTURE + MINIMAL_FIXTURE)
- [x] CLI seed command (`python -m src.cli seed --fixture demo`)
- [x] Frontend help components (GuidedTour, HelpTooltip, VideoEmbed, FAQAccordion)
- [x] Unit tests for seed CLI (20 tests passing)

---

### Sprint I: Reader UI & Accessibility (2 weeks)

- [ ] WCAG 2.1 AA accessibility audit
- [ ] Keyboard navigation, skip links, focus indicators
- [ ] High contrast, dark mode, dyslexic font support
- [ ] Context menu (copy as Markdown, AI integrations)
- [ ] Speed reader (RSVP) mode
- [ ] Rabbit-hole inline previews
- [ ] PDF/DOCX export
- [ ] Batch export

---

### Sprint J: Performance & Operations (2 weeks)

- [ ] Redis caching layer with decorators
- [ ] Frontend code splitting and bundle optimization
- [ ] Database index tuning and query optimization
- [ ] Prometheus metrics + Grafana dashboards
- [ ] Load testing (Locust)
- [ ] Alertmanager configuration

---

## Technical Dependencies

```
Phase 1 (Core) - DONE
└── Phase 2 (Go-to-Market) - DONE
    ├── Sprint A (Publishing) ✅
    ├── Sprint B (Admin UI) ✅
    ├── Sprint C (MCP) ✅
    ├── Sprint D (Access Control) ✅
    └── Sprint F (Attachments) ✅
        │
        ├── Phase 3 (Enhancement)
        │   ├── Sprint E (Diataxis Revision)
        │   └── Sprint G (Metadata Portability)
        │
        └── Phase 4 (Polish)
            ├── Sprint H (System Documentation) ✅
            ├── Sprint I (Reader UI & Accessibility)
            └── Sprint J (Performance & Operations)
```

## Test Commands

```bash
# Sprint D - Access Control
cd backend && pytest tests/unit/test_access_service.py tests/unit/test_classification_service.py tests/unit/test_content_transformer.py
cd backend && pytest tests/integration/test_visitor_api.py

# Sprint F - Attachments
cd backend && pytest tests/unit/test_attachment_service.py tests/unit/test_storage_backends.py
cd backend && pytest tests/integration/test_attachment_api.py

# Sprint H - System Documentation
cd backend && pytest tests/unit/test_seed.py -v
```

---

## Notes

- AI Features sprint is unscheduled - can be inserted into any phase
- Can ship after Phase 2 for full go-to-market readiness
- Phase 3-4 sprints are independent and can be parallelized
- Sprint J (Performance) can start anytime after Phase 2
