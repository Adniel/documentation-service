# Module Boundaries

## Overview

Documentation Service is organized into loosely-coupled modules that communicate through well-defined interfaces.

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                  │
│  REST endpoints • GraphQL • WebSocket • MCP Server               │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Content │ │Document │ │ Access  │ │Learning │ │   AI    │   │
│  │         │ │ Control │ │ Control │ │         │ │ Service │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │  Audit  │ │Signature│ │   MCP   │ │Publishing│              │
│  │         │ │         │ │  Client │ │         │               │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │   Git   │ │PostgreSQL│ │  Audit │ │  Search │ │  Cache  │   │
│  │  Repos  │ │         │ │  Store │ │  Index  │ │         │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Module Definitions

### Content Module
**Responsibility:** Core content management and Git abstraction

**Owns:**
- Documents (content in Git)
- Spaces, Sections, Page Groups
- Block serialization
- Real-time collaboration (CRDT)

**Exposes:**
```typescript
interface ContentService {
  createSpace(workspace: string, name: string): Promise<Space>
  createDocument(space: string, content: Block[]): Promise<Document>
  getDocument(id: string, version?: string): Promise<Document>
  updateDocument(id: string, content: Block[]): Promise<void>
  getVersionHistory(id: string): Promise<Version[]>
  compareVersions(id: string, v1: string, v2: string): Promise<Diff>
}
```

**Events:**
- `document.created`
- `document.updated`
- `document.deleted`

---

### Document Control Module
**Responsibility:** Lifecycle management and approval workflows

**Owns:**
- Document status (Draft, In Review, Approved, Effective, Obsolete)
- Change requests
- Approval workflows
- Reviewer assignments
- Periodic review schedules

**Exposes:**
```typescript
interface DocumentControlService {
  createChangeRequest(documentId: string): Promise<ChangeRequest>
  submitForReview(crId: string, reviewers: string[]): Promise<void>
  approve(crId: string, approval: ApprovalRequest): Promise<void>
  reject(crId: string, reason: string): Promise<void>
  merge(crId: string): Promise<void>
  getWorkflow(documentId: string): Promise<Workflow>
}
```

**Events:**
- `change_request.created`
- `change_request.submitted`
- `change_request.approved`
- `change_request.rejected`
- `change_request.merged`
- `document.status_changed`

---

### Access Control Module
**Responsibility:** Permissions and classification

**Owns:**
- User roles and permissions
- Permission inheritance
- Document classifications
- User clearances
- Document-level overrides

**Exposes:**
```typescript
interface AccessControlService {
  checkAccess(userId: string, resourceId: string, action: Action): Promise<boolean>
  grantPermission(userId: string, resourceId: string, role: Role): Promise<void>
  revokePermission(userId: string, resourceId: string): Promise<void>
  setClassification(documentId: string, level: Classification): Promise<void>
  grantClearance(userId: string, level: Classification): Promise<void>
}
```

**Events:**
- `permission.granted`
- `permission.revoked`
- `classification.changed`
- `clearance.granted`
- `access.denied`

---

### Signature Module
**Responsibility:** Electronic signatures (21 CFR Part 11)

**Owns:**
- Signature records
- Content hash generation
- Timestamp management
- Signature verification

**Exposes:**
```typescript
interface SignatureService {
  sign(documentId: string, request: SignatureRequest): Promise<SignatureRecord>
  verify(signatureId: string): Promise<VerificationResult>
  getSignatures(documentId: string): Promise<SignatureRecord[]>
}

interface SignatureRequest {
  password: string
  mfaCode?: string
  meaning: 'Authored' | 'Reviewed' | 'Approved' | 'Acknowledged'
  comment?: string
}
```

**Events:**
- `signature.created`
- `signature.verified`
- `signature.verification_failed`

---

### Audit Module
**Responsibility:** Immutable event logging

**Owns:**
- Audit event store
- Cryptographic chain
- Compliance reports

**Exposes:**
```typescript
interface AuditService {
  log(event: AuditEvent): Promise<void>
  query(filters: AuditFilters): Promise<AuditEvent[]>
  export(filters: AuditFilters, format: 'csv' | 'json'): Promise<Stream>
  verifyIntegrity(): Promise<IntegrityResult>
}

interface AuditEvent {
  eventType: string
  actorId: string
  resourceType: string
  resourceId: string
  details: Record<string, unknown>
  timestamp: Date
}
```

**Events:**
(Audit module is event sink, doesn't emit)

---

### Learning Module
**Responsibility:** Training and assessment

**Owns:**
- Assessments and questions
- Learning tracks and modules
- Assignments
- Completion records
- Question generation configuration

**Exposes:**
```typescript
interface LearningService {
  createAssignment(userId: string, documentId: string, dueDate: Date): Promise<Assignment>
  getAssessment(documentId: string): Promise<Assessment>
  submitAnswers(assessmentId: string, answers: Answer[]): Promise<Result>
  generateQuestions(config: QuestionGenConfig): Promise<Question[]>
  getCompletionStatus(userId: string): Promise<CompletionStatus[]>
}
```

**Events:**
- `assignment.created`
- `assessment.started`
- `assessment.completed`
- `acknowledgment.signed`

---

### AI Service Module
**Responsibility:** AI-powered features

**Owns:**
- Question generation
- Writing assistance
- Document masking (sensitive content detection)
- Content suggestions

**Exposes:**
```typescript
interface AIService {
  generateQuestions(content: string, sources: Source[], config: Config): Promise<Question[]>
  suggestMasking(content: string): Promise<MaskingSuggestion[]>
  assist(prompt: string, context: string): Promise<string>
  summarize(content: string): Promise<string>
}
```

**Events:**
- `ai.questions_generated`
- `ai.masking_suggested`

---

### MCP Module
**Responsibility:** Model Context Protocol integration

**Owns:**
- MCP Server (exposing content)
- MCP Client (consuming external sources)
- Service accounts
- Rate limiting

**Exposes:**
```typescript
// MCP Server tools
interface MCPServer {
  searchDocuments(query: string, filters?: Filters): Promise<SearchResult[]>
  getDocument(id: string, version?: string): Promise<Document>
  getDocumentSection(id: string, path: string): Promise<Section>
  listDocuments(space?: string, type?: string): Promise<DocumentMeta[]>
}

// MCP Client
interface MCPClient {
  query(server: string, tool: string, args: unknown): Promise<unknown>
}
```

**Events:**
- `mcp.tool_invoked`
- `mcp.access_denied`
- `mcp.rate_limited`

---

### Publishing Module
**Responsibility:** Static site generation and hosting

**Owns:**
- Site configuration
- Theme management
- Build pipeline
- CDN integration

**Exposes:**
```typescript
interface PublishingService {
  createSite(space: string, config: SiteConfig): Promise<Site>
  publish(siteId: string): Promise<Deployment>
  setTheme(siteId: string, theme: Theme): Promise<void>
  getAnalytics(siteId: string, range: DateRange): Promise<Analytics>
}
```

**Events:**
- `site.published`
- `site.deployment_failed`

---

## Inter-Module Communication

### Direct Calls
Modules can call each other's services directly for synchronous operations:

```typescript
// Document Control calls Access Control
const hasAccess = await accessControlService.checkAccess(userId, docId, 'approve')
if (!hasAccess) throw new ForbiddenError()
```

### Events
Modules publish events for asynchronous communication:

```typescript
// Content module publishes event
eventBus.publish('document.updated', { documentId, userId, changes })

// Audit module subscribes
eventBus.subscribe('document.*', (event) => {
  auditService.log(event)
})

// Search module subscribes
eventBus.subscribe('document.updated', (event) => {
  searchService.reindex(event.documentId)
})
```

## Dependency Rules

1. **Audit** - No dependencies (pure sink)
2. **Access Control** - No module dependencies
3. **Content** - Depends on Access Control
4. **Document Control** - Depends on Content, Access Control, Signature
5. **Signature** - Depends on Content (for content hash)
6. **Learning** - Depends on Content, Document Control, AI Service
7. **AI Service** - Depends on Content, MCP Client
8. **MCP** - Depends on Content, Access Control
9. **Publishing** - Depends on Content

## Data Ownership

| Data | Owner Module | Storage |
|------|--------------|---------|
| Document content | Content | Git |
| Document metadata | Content | PostgreSQL |
| Workflow state | Document Control | PostgreSQL |
| Permissions | Access Control | PostgreSQL |
| Classifications | Access Control | PostgreSQL |
| Signatures | Signature | PostgreSQL |
| Audit events | Audit | Audit Store |
| Questions | Learning | PostgreSQL |
| Assignments | Learning | PostgreSQL |
| Service accounts | MCP | PostgreSQL |
| Site config | Publishing | PostgreSQL |
| Search index | (shared) | Meilisearch |
