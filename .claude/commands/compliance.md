# Compliance Check

Du hjälper användaren att verifiera att implementationen uppfyller regulatoriska krav.

## Compliance-ramverk

### FDA 21 CFR Part 11

Elektroniska signaturer och records för FDA-reglerade industrier.

#### Checklista - Electronic Records (11.10)

| Krav | Paragraf | Implementation | Status |
|------|----------|----------------|--------|
| System access limited to authorized | 11.10(d) | Access control module | [ ] |
| Authority checks | 11.10(g) | Role-based permissions | [ ] |
| Device checks | 11.10(c) | Session management | [ ] |
| Audit trail | 11.10(e) | Audit module | [ ] |
| Operational system checks | 11.10(f) | Validation framework | [ ] |
| Document retention | 11.10(c) | Archive functionality | [ ] |
| Copy availability | 11.10(b) | Export features | [ ] |

#### Checklista - Electronic Signatures (11.50-11.200)

| Krav | Paragraf | Implementation | Status |
|------|----------|----------------|--------|
| Signature manifestation | 11.50 | Printed name, date/time, meaning | [ ] |
| Signature/record linking | 11.70 | Content hash, Git SHA | [ ] |
| Unique to individual | 11.100(a) | User identity verification | [ ] |
| Identity verification before issuance | 11.100(b) | Registration process | [ ] |
| Periodic certification | 11.100(c) | Annual confirmation | [ ] |
| Non-reusable | 11.200(a)(1) | One-time signature tokens | [ ] |
| Credential security | 11.200(a)(2) | Password policies, MFA | [ ] |

---

### ISO 9001:2015 / ISO 13485:2016

Quality Management Systems.

#### Checklista - Document Control (7.5)

| Krav | ISO 9001 | ISO 13485 | Implementation | Status |
|------|----------|-----------|----------------|--------|
| Approval before issue | 7.5.2 | 4.2.4 | Approval workflow | [ ] |
| Review and update | 7.5.2 | 4.2.4 | Periodic review | [ ] |
| Change identification | 7.5.2 | 4.2.4 | Version tracking | [ ] |
| Current version at point of use | 7.5.3.1 | 4.2.4 | Effective status | [ ] |
| Legible and identifiable | 7.5.3.1 | 4.2.4 | Document numbering | [ ] |
| External document control | 7.5.3.2 | 4.2.4 | External references | [ ] |
| Prevent unintended use of obsolete | 7.5.3.2 | 4.2.5 | Obsolete status | [ ] |

#### Checklista - Training (7.2)

| Krav | ISO 9001 | ISO 13485 | Implementation | Status |
|------|----------|-----------|----------------|--------|
| Determine competence | 7.2(a) | 6.2 | Role requirements | [ ] |
| Provide training | 7.2(b) | 6.2 | Learning module | [ ] |
| Evaluate effectiveness | 7.2(c) | 6.2 | Assessments | [ ] |
| Retain evidence | 7.2(d) | 6.2 | Training records | [ ] |

---

## Verifieringstest

### E-signatur verifiering

```typescript
describe('Electronic Signatures - 21 CFR Part 11', () => {
  it('requires re-authentication at signature time', async () => {
    // Test that user must re-enter credentials
  });

  it('captures signature meaning', async () => {
    // Test that meaning is required and stored
  });

  it('records trusted timestamp', async () => {
    // Test NTP timestamp is used
  });

  it('computes and stores content hash', async () => {
    // Test SHA-256 hash is computed
  });

  it('links signature to specific content version', async () => {
    // Test Git SHA is recorded
  });

  it('prevents signature modification', async () => {
    // Test immutability
  });
});
```

### Audit Trail verifiering

```typescript
describe('Audit Trail - 21 CFR Part 11 §11.10(e)', () => {
  it('records all create/modify/delete actions', async () => {
    // Test event capture
  });

  it('includes user ID for each action', async () => {
    // Test actor tracking
  });

  it('includes timestamp for each action', async () => {
    // Test timing
  });

  it('is append-only', async () => {
    // Test that records cannot be modified
  });

  it('detects tampering', async () => {
    // Test cryptographic chain validation
  });
});
```

### Access Control verifiering

```typescript
describe('Access Control - 21 CFR Part 11 §11.10(d)', () => {
  it('limits access to authorized individuals', async () => {
    // Test permission enforcement
  });

  it('enforces classification clearance', async () => {
    // Test classification-based access
  });

  it('logs access attempts', async () => {
    // Test access logging
  });

  it('supports permission inheritance', async () => {
    // Test hierarchy
  });
});
```

---

## Generera Compliance Report

Skapa rapport med:

### 1. System Description
- Systemets syfte
- Användare och roller
- Dataflöden

### 2. Regulatory Mapping
- Vilka regulatoriska krav som adresseras
- Hur varje krav implementeras
- Hänvisning till kod/konfiguration

### 3. Validation Protocol
- IQ (Installation Qualification)
- OQ (Operational Qualification)
- PQ (Performance Qualification)

### 4. Risk Assessment
- Identifierade risker
- Mitigeringsåtgärder
- Residual risk

### 5. Test Evidence
- Testprotokoll
- Testresultat
- Avvikelsehantering

---

## Output

Generera:
1. **Compliance Matrix** - Mappning av krav till implementation
2. **Test Protocol** - Verifieringstester för varje krav
3. **Gap Analysis** - Identifierade luckor
4. **Remediation Plan** - Åtgärder för luckor
