# Sprint Implementation Order - Quick Reference

## Recommended Order (Optimized for Go-to-Market)

| Priority | Sprint | Focus | Est. Effort | Key Deliverable |
|----------|--------|-------|-------------|-----------------|
| **P0** | A (was 12) | Publishing | 2 weeks | Shareable documentation sites |
| **P0** | B (was 9.5) | Admin UI | 1 week | Compliance configuration UI |
| **P1** | C (was 11) | MCP | 2 weeks | AI agent API access |
| **P2** | D (was 10) | AI Features | 2 weeks | Question gen, writing assistant |

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

## Notes

- Sprint D (AI) is optional for MVP
- Can ship after Sprint A for early demos
- Can ship after Sprint B for compliance customers
- Full feature set after Sprint C
