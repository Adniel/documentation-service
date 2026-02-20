# Sprint Implementation Order - Quick Reference

## Recommended Order (Optimized for Go-to-Market)

### Phase 2: Go-to-Market (Current)

| Priority | Sprint | Focus | Est. Effort | Key Deliverable |
|----------|--------|-------|-------------|-----------------|
| **P0** | A (was 12) | Publishing | 2 weeks | Shareable documentation sites |
| **P0** | B (was 9.5) | Admin UI | 1 week | Compliance configuration UI |
| **P1** | C (was 11) | MCP | 2 weeks | AI agent API access |
| **P2** | D (was 10) | AI Features | 2 weeks | Question gen, writing assistant |

### Phase 3: Enhancement

| Priority | Sprint | Focus | Est. Effort | Key Deliverable |
|----------|--------|-------|-------------|-----------------|
| **P2** | E (was 14) | Diátaxis Revision | 1 week | Per-page content types |
| **P2** | F (was 15) | Metadata Portability | 2 weeks | Export/Import, Confluence migration |

### Phase 4: Polish

| Priority | Sprint | Focus | Est. Effort | Key Deliverable |
|----------|--------|-------|-------------|-----------------|
| **P2** | G (was 16) | System Documentation | 1 week | Diátaxis-structured docs, fixtures |
| **P2** | H (was 17) | Reader UI & Accessibility | 2 weeks | WCAG 2.1 AA, PDF/DOCX export |
| **P2** | I (new) | Performance & Operations | 2 weeks | Caching, monitoring, optimization |

## Rationale for Reordering

### Original Order Problems
1. Publishing last → Can't demo or sell until everything done
2. Admin UI after compliance → Can't configure compliance features
3. AI before MCP → Missing modern API pattern

### New Order Benefits
1. **Publishing first** → Demo to customers after 2 weeks
2. **Admin UI second** → Make all existing features usable
3. **MCP before AI** → Modern API enables future AI integrations

## Sprint A: Publishing (2 weeks)

### Week 1
- [ ] Database models (PublishedSite, Theme)
- [ ] PublishingService backend
- [ ] Page rendering pipeline
- [ ] Site CRUD API endpoints

### Week 2
- [ ] SiteConfigPanel frontend
- [ ] ThemeEditor frontend
- [ ] Public site viewer
- [ ] Integration tests

### Milestone
- Admin can create and publish a documentation site
- Users can view published content

---

## Sprint B: Admin UI (1 week)

### Days 1-2
- [ ] UserManagement component
- [ ] UserRoleEditor component
- [ ] User invite flow

### Days 3-4
- [ ] OrganizationSettings component
- [ ] DocumentNumberingConfig
- [ ] RetentionPolicyConfig

### Day 5
- [ ] AuditDashboard
- [ ] AuditExportPanel
- [ ] Integration tests

### Milestone
- All compliance features configurable via UI
- Admin can manage users, roles, and settings

---

## Sprint C: MCP Integration (2 weeks)

### Week 1
- [ ] MCP server skeleton
- [ ] Tool implementations (search, get_document)
- [ ] ServiceAccount model
- [ ] API key authentication

### Week 2
- [ ] Rate limiting
- [ ] Usage tracking
- [ ] ServiceAccountList frontend
- [ ] Integration tests

### Milestone
- External AI agents can query platform content
- Service accounts with scoped permissions

---

## Sprint D: AI Features (2 weeks)

### Week 1
- [ ] AI provider abstraction
- [ ] Question generator backend
- [ ] QuestionGeneratorPanel frontend
- [ ] Question review workflow

### Week 2
- [ ] Writing assistant backend
- [ ] WritingAssistant frontend (editor integration)
- [ ] MaskingService
- [ ] Integration tests

### Milestone
- AI-generated quiz questions
- Writing suggestions in editor

---

## Go-Live Checklist

### After Sprint A
- [ ] Test published site with real content
- [ ] Verify access control on private sites
- [ ] Load test published site

### After Sprint B
- [ ] All compliance features tested via UI
- [ ] User management tested
- [ ] Audit export verified

### After Sprint C
- [ ] MCP endpoint documented
- [ ] Service account security reviewed
- [ ] Rate limiting tested

### After Sprint D (Optional)
- [ ] AI quality reviewed
- [ ] Cost monitoring in place
- [ ] Human review workflow tested

---

## Technical Dependencies

```
           ┌─────────────────┐
           │ Sprint A        │
           │ Publishing      │
           └────────┬────────┘
                    │
           ┌────────▼────────┐
           │ Sprint B        │
           │ Admin UI        │
           │ (adds Pub tab)  │
           └────────┬────────┘
                    │
           ┌────────▼────────┐
           │ Sprint C        │
           │ MCP             │
           └────────┬────────┘
                    │
           ┌────────▼────────┐
           │ Sprint D        │
           │ AI Features     │
           │ (uses MCP auth) │
           └─────────────────┘
```

## Commands for Each Sprint

```bash
# Sprint A - Publishing
cd backend && pytest tests/unit/test_publishing*.py
cd frontend && npm test -- --grep "Publishing"

# Sprint B - Admin UI
cd frontend && npm test -- --grep "Admin"

# Sprint C - MCP
cd backend && pytest tests/unit/test_mcp*.py
cd backend && pytest tests/integration/test_mcp*.py

# Sprint D - AI
cd backend && pytest tests/unit/test_ai*.py
```

---

## Sprint E: Diátaxis Revision (1 week)

### Days 1-2
- [ ] Database migration for diataxis_types array on pages
- [ ] API endpoints for multi-type assignment
- [ ] Search filter by content type

### Days 3-4
- [ ] ContentTypeManager admin component
- [ ] ContentTypeEditor for custom types
- [ ] Multi-select type picker in page editor

### Day 5
- [ ] Migration script for existing content
- [ ] Integration tests
- [ ] Documentation update

### Milestone
- Pages can have multiple Diátaxis types
- Organizations can define custom content types

---

## Sprint F: Metadata Portability (2 weeks)

### Week 1
- [ ] Define _meta.yaml schema
- [ ] Implement filesystem metadata storage
- [ ] Sync service between DB and filesystem
- [ ] Export API endpoints

### Week 2
- [ ] ImportWizard frontend component
- [ ] Confluence adapter
- [ ] SharePoint adapter
- [ ] Conflict resolution UI
- [ ] Integration tests

### Milestone
- Metadata stored in Git alongside content
- Import from Confluence/SharePoint works
- Full export/import cycle preserves all data

---

## Sprint G: System Documentation (1 week)

### Days 1-2
- [ ] Tutorial: Getting started guide
- [ ] Tutorial: Create first document
- [ ] How-to guides for common tasks

### Days 3-4
- [ ] Reference: API documentation
- [ ] Reference: Configuration guide
- [ ] Explanation: Architecture and design

### Day 5
- [ ] Fixture data for demo organization
- [ ] CLI seed command
- [ ] GuidedTour component

### Milestone
- Complete Diátaxis-structured documentation
- Fixture installation creates working demo

---

## Sprint H: Reader UI & Accessibility (2 weeks)

### Week 1
- [ ] WCAG 2.1 AA accessibility audit
- [ ] SkipLinks and keyboard navigation
- [ ] High contrast and dark mode
- [ ] Dyslexic font support
- [ ] Screen reader testing

### Week 2
- [ ] Context menu with AI integrations
- [ ] Speed reader (RSVP) mode
- [ ] Rabbit-hole inline previews
- [ ] PDF/DOCX export
- [ ] Batch export functionality

### Milestone
- WCAG 2.1 AA compliant
- GitBook-style reader experience
- All export formats working

---

## Sprint I: Performance & Operations (2 weeks)

### Week 1
- [ ] Redis caching layer
- [ ] Cache decorators for common queries
- [ ] Frontend code splitting
- [ ] Bundle size optimization

### Week 2
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Database index tuning
- [ ] Load testing (Locust)
- [ ] Alertmanager configuration

### Milestone
- Page load < 2s (p95)
- API response < 200ms (p50)
- Monitoring dashboards operational

---

## Go-Live Checklist

### After Phase 2 (Sprints A-D)
- [ ] Published sites functional
- [ ] All compliance features configurable via UI
- [ ] MCP endpoint documented
- [ ] AI features quality reviewed (if included)

### After Phase 3 (Sprints E-F)
- [ ] Per-page Diátaxis tagging working
- [ ] Export/import tested with real data
- [ ] Metadata portability verified

### After Phase 4 (Sprints G-I)
- [ ] System documentation complete
- [ ] WCAG 2.1 AA audit passed
- [ ] Performance SLAs met
- [ ] Monitoring alerts configured

---

## Notes

- Sprint D (AI) is optional for MVP
- Can ship after Sprint A for early demos
- Can ship after Sprint B for compliance customers
- Full feature set after Sprint C
- Sprints E-I are enhancement/polish phases
