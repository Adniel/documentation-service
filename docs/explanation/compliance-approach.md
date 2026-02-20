# Compliance Approach

This document explains the platform's approach to regulatory compliance, covering electronic signatures, audit trails, and document control as required by 21 CFR Part 11, ISO 9001, and ISO 13485.

## Regulatory Landscape

The platform addresses three overlapping regulatory frameworks:

| Standard | Focus | Key Requirements |
|----------|-------|-----------------|
| **21 CFR Part 11** | Electronic records and signatures | Re-authentication, signature meaning, audit trails, system validation |
| **ISO 9001:2015** | Quality management systems | Document control (§7.5), records management, approval before release |
| **ISO 13485:2016** | Medical device QMS | Document control (§4.2.4–5), training records, traceability |

## Electronic Signatures (21 CFR Part 11)

### Why Re-authentication?

§11.200 requires that electronic signatures "be executed by their owner" and not shared or transferred. The platform enforces this by requiring password re-entry at signature time, even if the user is already logged in.

**Flow:**

1. User requests to sign → `POST /api/v1/signatures/challenge`
2. Server creates a time-limited challenge (default: 5 minutes)
3. User enters password → `POST /api/v1/signatures/sign`
4. Server verifies password, creates signature record
5. Challenge is consumed (single-use)

This design prevents:
- Replay attacks (challenges expire and are single-use)
- Session hijacking (knowing the session token is not enough to sign)
- Shared signatures (password verification ties the signature to the individual)

### Why Capture Signature Meaning?

§11.50 requires that signatures indicate "the printed name of the signer, the date and time, and the meaning" of the signature. The platform captures four meanings:

| Meaning | Use Case |
|---------|----------|
| **Authored** | The signer wrote or substantially contributed to the content |
| **Reviewed** | The signer reviewed the content for accuracy and completeness |
| **Approved** | The signer authorizes the content for release |
| **Witnessed** | The signer witnessed another's approval (for controlled environments) |

### Content Hash Integrity

Each signature includes a SHA-256 hash of the page content at signing time. This provides:

- **Non-repudiation** — The signer approved this exact content, provably
- **Tamper detection** — If content changes after signing, the hash won't match
- **Verification** — `GET /api/v1/signatures/{id}/verify` recomputes the hash and compares

### Trusted Timestamps

Signatures use NTP-sourced timestamps (via `ntplib`) rather than relying on the server's system clock. This ensures:

- Timestamps are traceable to a trusted time source
- Clock manipulation on the server doesn't affect signature timestamps
- Regulatory auditors can verify the time source

## Audit Trail Design

### Hash Chain

The audit trail uses a cryptographic hash chain where each event includes:

```
event_hash = SHA-256(event_id + event_type + timestamp + user_id + details + previous_hash)
```

This creates a tamper-evident log:

- **Inserting** an event after the fact would break the hash of all subsequent events
- **Modifying** an event would change its hash, breaking the chain
- **Deleting** an event would create a gap in the chain

### Why Append-Only?

§11.10(e) requires audit trails that "cannot be erased, modified, or obscured." The platform enforces this at the application level:

- No UPDATE or DELETE operations on the audit table
- All writes go through a single `create_audit_event()` function
- The function always reads and includes the previous event's hash
- Database triggers can optionally enforce the append-only constraint

### What Gets Audited?

Every state-changing action is recorded:

- Content: create, update, delete, restore
- Lifecycle: status transitions (draft → review → approved → effective)
- Signatures: challenge created, signature applied, verification performed
- Access: login, logout, permission changes, classification changes
- Admin: user creation, role changes, configuration changes
- System: seed operations, import/export, scheduled tasks

### Audit Export

For compliance audits, the entire audit trail (or a filtered subset) can be exported:

```
GET /api/v1/audit/export?from=2024-01-01&to=2024-12-31&format=csv
```

The export includes all event data and hash values, allowing auditors to independently verify chain integrity.

## Document Control (ISO 9001/13485)

### Approval Before Release

ISO 9001 §7.5.2 requires that documents be "reviewed and approved for adequacy prior to issue." The platform enforces this through:

1. **Approval Matrix** — Configurable per document type, defining required approver roles
2. **Status Gates** — A document cannot transition to "Effective" without all required approvals
3. **Electronic Signatures** — Each approval is a signed record, not just a checkbox

### Version Control

The platform tracks two version dimensions:

| Dimension | Format | When Incremented |
|-----------|--------|-----------------|
| **Revision** | A, B, C, ... | Major changes (new effective version) |
| **Version** | 1.0, 1.1, 1.2 | Each save/commit within a revision |

This follows ISO 15489 practices where revisions represent published releases and versions represent working drafts.

### Document Identification

Auto-generated document numbers follow a configurable pattern:

```
{PREFIX}-{CATEGORY}-{SEQUENCE}
Example: SOP-QMS-001, WI-ENG-042, POL-HR-003
```

The numbering system is managed per organization with:
- Configurable prefixes per document type
- Category codes derived from workspace
- Sequential numbering with gap prevention
- Optional manual override for migrated documents

### Retention and Disposition

Each document type can have a retention policy:

- **Retention period** — How long the document must be kept after becoming obsolete
- **Disposition method** — What happens after retention: archive, destroy, or review
- **Expiration action** — Automatic notification, archival, or manual review trigger

See [Retention Policies](../how-to/retention-policies.md) for configuration.

## System Validation Considerations

21 CFR Part 11 requires that systems producing electronic records be validated. While the platform provides the technical controls, deploying organizations should:

1. Perform Installation Qualification (IQ) — verify deployment matches specifications
2. Perform Operational Qualification (OQ) — verify features work as documented
3. Perform Performance Qualification (PQ) — verify the system meets user requirements
4. Maintain validation documentation and change control records
5. Conduct periodic reviews of system access and audit trails

The platform's test suite (unit, integration, and E2E tests) can serve as a foundation for OQ test protocols.
