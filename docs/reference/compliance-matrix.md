# Compliance Matrix

This document maps platform features to specific regulatory requirements from ISO 9001, ISO 13485, and 21 CFR Part 11.

## 21 CFR Part 11 — Electronic Records and Signatures

| Requirement | Section | Platform Feature | Implementation |
|-------------|---------|-----------------|----------------|
| System validation | §11.10(a) | Test suite | Unit, integration, and E2E tests; CI pipeline |
| Generate accurate copies | §11.10(b) | Export API | `/portability/export` with Markdown, JSON, HTML formats |
| Record protection | §11.10(c) | Role-based access + classification | Dual-dimension access control model |
| Audit trail | §11.10(e) | Hash-chained audit events | Append-only audit store, `GET /audit/events` |
| Operational checks | §11.10(f) | Approval workflow gates | Status transitions require all approvals |
| Authority checks | §11.10(g) | Role-based permissions | Per-action role requirements in endpoints |
| Device checks | §11.10(h) | Session management | JTI-tracked sessions, auto-expiry, force logout |
| Training records | §11.10(i) | Learning module | Assessments, acknowledgments, completion tracking |
| Written policies | §11.10(j) | Documentation | Platform documentation (this guide) |
| Controls for open systems | §11.10(k) | Encryption | HTTPS transport, encrypted credential storage |
| Signature manifestation | §11.50 | Signature display | Name, date/time, meaning shown on signed documents |
| Signature linking | §11.70 | Content hash | SHA-256 hash links signature to specific content version |
| Signature components | §11.100 | Re-authentication | Password re-entry at signature time |
| Unique signatures | §11.100(a) | User identity | Signatures tied to authenticated user account |
| Signature meaning | §11.200(a)(2) | Meaning capture | Authored, Reviewed, Approved, Witnessed |
| Continuous session | §11.200(a)(1)(i) | Challenge-based signing | Time-limited signature challenges |
| Non-repudiation | §11.200(a)(3) | Signature verification | `GET /signatures/{id}/verify` endpoint |

## ISO 9001:2015 — Quality Management Systems

| Requirement | Section | Platform Feature | Implementation |
|-------------|---------|-----------------|----------------|
| Approval before release | §7.5.2(a) | Approval workflow | Configurable approval matrices, electronic signatures |
| Review and update | §7.5.2(b) | Change requests | Branch-based editing, review process |
| Changes identified | §7.5.2(c) | Version tracking | Git-based version history, revision tracking |
| Current versions available | §7.5.2(d) | Published sites | Publishing module with effective status |
| Legible and identifiable | §7.5.2(e) | Document numbering | Auto-generated numbers (SOP-QMS-001) |
| External documents identified | §7.5.2(f) | Classification | Classification levels on all content |
| Prevention of unintended use | §7.5.2(g) | Lifecycle status | Obsolete/archived documents clearly marked |
| Documented information control | §7.5.3 | Access control | Role + classification dual-dimension model |
| Distribution and access | §7.5.3.1(a) | Publishing + permissions | Workspace/space/page level access |
| Storage and preservation | §7.5.3.1(b) | Git + PostgreSQL | Immutable Git history, database backups |
| Control of changes | §7.5.3.1(c) | Change requests | Tracked changes with approval workflow |
| Retention and disposition | §7.5.3.1(d) | Retention policies | Configurable periods and disposition methods |

## ISO 13485:2016 — Medical Device QMS

| Requirement | Section | Platform Feature | Implementation |
|-------------|---------|-----------------|----------------|
| Document control procedure | §4.2.4 | Platform workflow | Integrated lifecycle management |
| Document approval | §4.2.4(a) | Approval matrices | Configurable per document type |
| Review and re-approval | §4.2.4(b) | Periodic review | Reminder system for effective documents |
| Changes identified | §4.2.4(c) | Diff view | Git-based diff between versions |
| Relevant versions available | §4.2.4(d) | Version history | Full commit history per page |
| Documents legible | §4.2.4(e) | Editor | TipTap rich content editor |
| External documents identified | §4.2.4(f) | MCP integration | External source tracking |
| Prevent deterioration | §4.2.4(g) | Git + backups | Immutable content, remote sync |
| Prevent unintended use | §4.2.4(g) | Status management | Draft/obsolete documents separated |
| Records control | §4.2.5 | Audit trail | Complete, tamper-evident event log |
| Records retention | §4.2.5 | Retention policies | Configurable per document type |
| Training records | §6.2 | Learning module | Assessment completion, acknowledgments |
| Training effectiveness | §6.2 | Quiz scoring | Pass/fail tracking with score records |

## Feature Coverage Summary

| Feature Area | 21 CFR Part 11 | ISO 9001 | ISO 13485 |
|-------------|---------------|----------|-----------|
| Electronic signatures | Full | Partial | Partial |
| Audit trail | Full | Full | Full |
| Document control | N/A | Full | Full |
| Access control | Full | Full | Full |
| Version control | Full | Full | Full |
| Training records | Partial | N/A | Full |
| Records retention | Partial | Full | Full |
| System validation | Framework | N/A | N/A |

**Full** = All relevant requirements addressed
**Partial** = Most requirements addressed, some require organizational procedures
**N/A** = Standard does not specifically address this area
