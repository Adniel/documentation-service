# Implementation Guide

Du hjälper användaren att implementera en specifik modul i Documentation Service.

## Argument
- `$ARGUMENTS` innehåller modulnamnet

## Tillgängliga moduler

### content
Core content management - hierarki, Git-abstraktion, CRDT-sync

### editor
Block-baserad editor med alla block-typer

### access
Åtkomstkontroll - hierarkiska behörigheter och klassificering

### document-control
Livscykel, arbetsflöden, dokumentnumrering

### signatures
21 CFR Part 11-kompatibla elektroniska signaturer

### audit
Immutable audit trail med kryptografisk kedja

### learning
Assessment, acknowledgments, learning tracks

### ai
Question generation, writing assistant, masking

### mcp
MCP server och client implementation

### publishing
Static site generation, theming

---

## Implementation-process

För varje modul, följ denna process:

### 1. Analysera specifikationen
Läs relevanta delar av `documentation-service-specification-v3.5.md`:
- Identifiera krav
- Förstå datamodeller
- Notera integrationer med andra moduler

### 2. Design datamodell
Skapa databas-schema:
```sql
-- Exempel för content-modulen
CREATE TABLE spaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID REFERENCES workspaces(id),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Design API
Skapa OpenAPI-specifikation eller beskrivning:
```yaml
paths:
  /api/spaces:
    get:
      summary: List spaces
    post:
      summary: Create space
  /api/spaces/{id}:
    get:
      summary: Get space
    patch:
      summary: Update space
    delete:
      summary: Delete space
```

### 4. Implementera
Generera kod baserat på teknologival (läs från ADR om det finns).

### 5. Testa
Generera tester:
- Unit tests för affärslogik
- Integration tests för API
- E2E tests för kritiska flöden

---

## Modul-specifika instruktioner

### content
**Nyckelkoncept:**
- Git-repos per Space
- Block-baserad dokumentstruktur
- CRDT för real-time collaboration
- Markdown som källa

**Filer att skapa:**
- `src/modules/content/models/` - Document, Block, Space
- `src/modules/content/services/git-service` - Git-abstraktioner
- `src/modules/content/services/content-service` - CRUD operations
- `src/modules/content/api/` - REST endpoints

### editor
**Nyckelkoncept:**
- Block-typer med schema
- Serialisering JSON ↔ Markdown
- Slash commands
- Real-time collaboration

**Frontend-komponenter:**
- Editor container
- Block renderer (per typ)
- Toolbar
- Slash command menu

### access
**Nyckelkoncept:**
- Dual-dimension: Hierarchical + Classification
- Permission inheritance
- Document-level overrides

**Datamodell:**
```
users - roles - permissions
documents - classifications
users - clearances
```

### document-control
**Nyckelkoncept:**
- Lifecycle states med övergångsregler
- Approval workflows
- Reviewer assignments

**State machine:**
```
Draft → In Review → Approved → Effective → Obsolete
         ↓                      ↑
         → Changes Requested ───┘
```

### signatures
**21 CFR Part 11 krav:**
1. Re-authentication (lösenord + MFA om konfigurerat)
2. Signature meaning (dropdown)
3. Trusted timestamp (NTP)
4. Content hash (SHA-256 av dokumentinnehåll)
5. Icke-repudierbar lagring

### audit
**Nyckelkoncept:**
- Append-only
- Kryptografisk kedja (varje post innehåller hash av föregående)
- Tamper detection vid startup

**Event schema:**
```typescript
interface AuditEvent {
  id: string;
  timestamp: Date;
  event_type: string;
  actor_id: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  previous_hash: string;
  hash: string;
}
```

### learning
**Nyckelkoncept:**
- Questions embedded i dokument (markup)
- Quiz gatar acknowledgment
- AI-genererade frågor (Sprint 10)

**Frågetyper:**
- multiple-choice (single/multi)
- true-false
- fill-in-blank
- ordering
- matching

### ai
**Provider-agnostic design:**
```typescript
interface AIProvider {
  generateQuestions(content: string, config: QuestionConfig): Promise<Question[]>;
  suggestMasking(content: string): Promise<MaskingSuggestion[]>;
  assist(prompt: string, context: string): Promise<string>;
}
```

### mcp
**MCP Server Tools:**
- search_documents
- get_document
- get_document_section
- list_documents
- get_effective_documents

**Access Control:**
- Service accounts med scoped permissions
- Rate limiting
- Full audit logging

### publishing
**Process:**
1. Build static HTML från dokument
2. Apply theme
3. Deploy till CDN/hosting
4. Configure custom domain

---

## Output

Generera:
1. **Databasschema** (SQL migrations)
2. **API-specifikation** (OpenAPI)
3. **Service-kod** (baserat på valt språk)
4. **Tester** (unit + integration)
5. **Dokumentation** (README för modulen)
