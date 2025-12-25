# Sprint Guide

Du hjälper användaren med att arbeta igenom en specifik sprint i Documentation Service-projektet.

## Argument
- `$ARGUMENTS` innehåller sprintnumret (1-12)

## Sprint-översikt

Baserat på sprintnummer, ge detaljerad vägledning:

---

## Sprint 1: Foundation
**Mål:** Grundläggande infrastruktur med körbar applikation

### Delleverabler
1. **Projektuppsättning**
   - Initiera projekt med valt ramverk
   - Konfigurera TypeScript/typsystem
   - Sätt upp linting, formattering
   - Docker Compose för utvecklingsmiljö

2. **Databas**
   - PostgreSQL-schema för grundläggande entiteter
   - Migrations-system
   - Seed-data för utveckling
   ```
   Tabeller: organizations, workspaces, spaces, users, sessions
   ```

3. **Authentication**
   - Lokal autentisering (email/password)
   - Session-hantering
   - JWT eller session cookies
   - Grundläggande middleware

4. **Git Integration (grundläggande)**
   - Initiera Git-repos programmatiskt
   - Skapa/läsa filer i repo
   - Grundläggande commits
   ```
   Funktioner: initRepo, createFile, readFile, commitChanges
   ```

5. **API-grund**
   - REST API-struktur
   - Error handling
   - Request validation
   - Health check endpoint

### Verifieringskriterier
- [ ] `docker-compose up` startar alla tjänster
- [ ] Användare kan registrera sig och logga in
- [ ] API returnerar 200 på health check
- [ ] Git-repo kan skapas och innehålla filer
- [ ] Alla tester passerar

---

## Sprint 2: Editor Core
**Mål:** Fungerande block-baserad editor

### Delleverabler
1. **Block-datamodell**
   - Block-typer (paragraph, heading, code, etc.)
   - Block-serialisering (JSON ↔ Markdown)
   - Block-validering

2. **Editor-komponent**
   - Grundläggande block-rendering
   - Text-redigering inom block
   - Block-tillägg/borttagning
   - Drag-and-drop (grundläggande)

3. **Markdown-stöd**
   - Markdown-shortcuts (# för heading, etc.)
   - Import från Markdown
   - Export till Markdown

4. **Sparfunktion**
   - Auto-save med debounce
   - Manuell sparning
   - Git commit vid sparning

### Block-typer (Sprint 2)
- Paragraph
- Heading (H1-H6)
- Code block (utan syntax highlighting ännu)
- Bulleted list
- Numbered list
- Quote

### Verifieringskriterier
- [ ] Editor laddar och visar dokument
- [ ] Användare kan skriva och formatera text
- [ ] Markdown-shortcuts fungerar
- [ ] Ändringar sparas till Git
- [ ] Dokument kan exporteras som Markdown

---

## Sprint 3: Content Organization
**Mål:** Fullständig innehållshierarki och navigation

### Delleverabler
1. **Hierarki-implementation**
   ```
   Organization → Workspace → Space → Section → Page Group → Page
   ```
   - CRUD för alla nivåer
   - Flytta innehåll mellan nivåer
   - Sortering och ordning

2. **Navigation**
   - Sidebar med trädstruktur
   - Breadcrumbs
   - Sökfunktion (grundläggande)

3. **Sök-integration**
   - Meilisearch/Elasticsearch setup
   - Indexering av dokument
   - Full-text search API

4. **Diátaxis-stöd**
   - Taggning av innehåll per typ
   - Filtrering per Diátaxis-kategori
   - Mallar per typ

### Verifieringskriterier
- [ ] Användare kan skapa och navigera i hierarkin
- [ ] Sök returnerar relevanta resultat
- [ ] Diátaxis-taggar kan appliceras
- [ ] Navigation fungerar responsivt

---

## Sprint 4: Version Control UI
**Mål:** Visuell versionshantering utan Git-terminologi

### Delleverabler
1. **Change Requests**
   - Skapa "utkast" (branch)
   - Lista aktiva utkast
   - Byt mellan utkast
   - UI utan branch-terminologi

2. **Diff-vy**
   - Visuell jämförelse (gammal vs ny)
   - Inline diff-highlighting
   - Rad-för-rad jämförelse

3. **Historik**
   - Versionshistorik (Git log abstraktion)
   - Jämför valfria versioner
   - Återställ till tidigare version

4. **Merge UI**
   - Sammanslagning av utkast
   - Konflikthantering (UI-guidad)
   - Merge-bekräftelse

### Git-abstraktioner
| Användargränssnitt | Git-operation |
|-------------------|---------------|
| "Skapa utkast" | `git checkout -b draft/CR-xxx` |
| "Visa ändringar" | `git diff main...branch` |
| "Publicera" | `git merge --no-ff` |
| "Versionshistorik" | `git log --follow` |

### Verifieringskriterier
- [ ] Användare kan skapa och hantera utkast
- [ ] Diff-vy visar ändringar tydligt
- [ ] Historik visar alla versioner
- [ ] Merge fungerar utan konflikter (happy path)
- [ ] Konflikthantering fungerar (edge case)

---

## Sprint 5: Access Control
**Mål:** Komplett åtkomstkontroll med två dimensioner

### Delleverabler
1. **Hierarkiska behörigheter**
   - Roller: Owner, Admin, Editor, Reviewer, Viewer
   - Arv genom hierarkin
   - Dokumentnivå-restriktioner

2. **Klassificeringssystem**
   - Nivåer: Public, Internal, Confidential, Restricted
   - Clearance per användare
   - Klassificering per dokument

3. **Åtkomstlogik**
   ```
   Access = Hierarchical Permission AND Classification Clearance
   ```

4. **Administration**
   - Användarhantering
   - Rollhantering
   - Clearance-tilldelning
   - Audit av behörighetsändringar

### Verifieringskriterier
- [ ] Behörigheter ärvs korrekt
- [ ] Klassificering blockerar åtkomst
- [ ] Admin kan hantera användare
- [ ] Alla behörighetsändringar loggas

---

## Sprint 6: Document Control Basics
**Mål:** Grundläggande dokumentkontroll med livscykel

### Delleverabler
1. **Livscykelstatus**
   ```
   Draft → In Review → Approved → Effective → Obsolete → Archived
   ```
   - Statusövergångar
   - Validering per övergång

2. **Arbetsflöden (grundläggande)**
   - Skicka för granskning
   - Tilldela granskare
   - Godkänn/avslå
   - Notifieringar

3. **Dokumentnumrering**
   - Auto-numrering (t.ex. SOP-QMS-001)
   - Revisionsspårning
   - Metadata-schema

4. **Periodisk granskning**
   - Review-datum
   - Påminnelser
   - Eskalering

### Verifieringskriterier
- [ ] Dokument kan gå genom hela livscykeln
- [ ] Granskningsflöde fungerar
- [ ] Auto-numrering genererar korrekta nummer
- [ ] Påminnelser skickas vid deadline

---

## Sprint 7: Electronic Signatures
**Mål:** 21 CFR Part 11-kompatibla e-signaturer

### Delleverabler
1. **Signaturprocess**
   - Re-autentisering vid signering
   - Capture av signatur-betydelse
   - Trusted timestamp
   - Content hash (SHA-256)

2. **Signaturpost**
   ```
   SignatureRecord:
     user_id, full_name, title
     meaning (Approved, Reviewed, Authored)
     timestamp (UTC, NTP)
     git_commit_sha
     content_hash (SHA-256)
     auth_method
   ```

3. **Approval Matrix**
   - Konfigurerbara krav
   - Parallella/sekventiella godkännanden
   - Roll-baserade krav

4. **Signaturverifiering**
   - Verifiera signatur mot innehåll
   - Visa signaturhistorik
   - Export för compliance

### Verifieringskriterier
- [ ] Signering kräver re-autentisering
- [ ] Alla signaturfält sparas korrekt
- [ ] Content hash matchar vid verifiering
- [ ] Approval matrix enforces krav

---

## Sprint 8: Audit Trail
**Mål:** Immutable audit trail för compliance

### Delleverabler
1. **Event Store**
   - Append-only lagring
   - Kryptografisk kedja (hash av föregående)
   - Tamper-detection

2. **Event-typer**
   - Content events (create, update, delete)
   - Workflow events (submit, approve, reject)
   - Access events (view, download, print)
   - Admin events (permission changes)

3. **Sök och filter**
   - Sök i audit trail
   - Filter per dokument, användare, tid
   - Export till CSV/JSON

4. **Compliance-rapporter**
   - Dokumenthistorik-rapport
   - Användaraktivitet-rapport
   - Signaturverifiering-rapport

### Verifieringskriterier
- [ ] Events kan inte modifieras efter skapande
- [ ] Kedjan valideras vid startup
- [ ] Alla kritiska händelser loggas
- [ ] Rapporter kan genereras och exporteras

---

## Sprint 9: Learning Module Basics
**Mål:** Grundläggande utbildningsmodul

### Delleverabler
1. **Assessments**
   - Manuella frågor (markup i dokument)
   - Frågetyper (MC, T/F, fill-in)
   - Poängsättning

2. **Acknowledgment Flow**
   - Läs dokument
   - Svara på frågor
   - Godkänn (med e-signatur)

3. **Tilldelningar**
   - Tilldela dokument till användare
   - Due dates
   - Påminnelser
   - Status-spårning

4. **Rapportering**
   - Completion rates
   - Quiz results
   - Overdue assignments

### Verifieringskriterier
- [ ] Frågor kan definieras i dokument
- [ ] Quiz blockerar godkännande tills godkänt
- [ ] Tilldelningar spåras korrekt
- [ ] Rapporter visar korrekt data

---

## Sprint 10: AI Features
**Mål:** AI-assisterade funktioner

### Delleverabler
1. **Question Generation**
   - Generera frågor från dokument
   - Multi-source support (docs, URLs)
   - Author review workflow

2. **Writing Assistant**
   - Textförslag
   - Omskrivning
   - Grammatik-check

3. **Document Masking**
   - Sensitive content detection (NER)
   - Masking suggestions
   - Review interface
   - Masked versions

4. **AI Configuration**
   - Provider-agnostic design
   - Prompt templates
   - Rate limiting

### Verifieringskriterier
- [ ] AI genererar relevanta frågor
- [ ] Writing assistant ger användbar hjälp
- [ ] Masking identifierar känslig information
- [ ] Human review krävs för AI-output

---

## Sprint 11: MCP Integration
**Mål:** Bidirektionell MCP-integration

### Delleverabler
1. **MCP Server**
   - Exponera platform content
   - Tools: search_documents, get_document, etc.
   - Access control enforcement
   - Rate limiting

2. **MCP Client**
   - Konsumera externa källor
   - Server registry
   - Query templates

3. **Service Accounts**
   - Skapa/hantera service accounts
   - Scoped permissions
   - IP restrictions
   - Usage monitoring

4. **Audit**
   - Logga all MCP-åtkomst
   - Rate limit tracking
   - Error monitoring

### Verifieringskriterier
- [ ] Externa AI-agenter kan query:a plattformen
- [ ] Access control enforces vid MCP-anrop
- [ ] Plattformen kan konsumera externa MCP-servrar
- [ ] All MCP-trafik loggas

---

## Sprint 12: Publishing & Polish
**Mål:** Publicering och slutpolering

### Delleverabler
1. **Publishing Engine**
   - Static site generation
   - Custom domains
   - Access control för sites

2. **Theming**
   - Logo, färger, fonts
   - Custom CSS
   - Navigation-anpassning

3. **Analytics**
   - Page views, visitors
   - Search analytics
   - Content feedback

4. **Performance**
   - Caching
   - CDN-integration
   - Load testing
   - Optimization

5. **Documentation**
   - API-dokumentation
   - User guides
   - Admin guides

### Verifieringskriterier
- [ ] Sites kan publiceras med custom domain
- [ ] Theming fungerar
- [ ] Analytics samlar data
- [ ] Performance targets uppfylls
- [ ] All dokumentation komplett

---

## Nästa steg

Efter att ha valt sprint, använd:
- `/docservice:implement <module>` för implementation
- `/docservice:test <module>` för testgenerering
- `/docservice:api <module>` för API-design
