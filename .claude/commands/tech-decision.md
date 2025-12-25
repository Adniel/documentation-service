# Technology Decision Guide

Du hjälper användaren att välja och dokumentera teknologival för Documentation Service-projektet.

## Teknologival som behöver göras

Fråga användaren om följande beslut och dokumentera svaren:

### 1. Backend-ramverk

**Fråga användaren:**
> Vilket backend-ramverk vill du använda?

| Option | Fördelar | Nackdelar |
|--------|----------|-----------|
| **Node.js + Express/Fastify** | - Samma språk som frontend<br>- Utmärkt för WebSocket/CRDT<br>- Stort ekosystem | - Single-threaded<br>- Kräver care med CPU-intensiva ops |
| **Node.js + NestJS** | - Strukturerad arkitektur<br>- Inbyggd DI<br>- Bra för enterprise | - Mer boilerplate<br>- Steepare learning curve |
| **Python + FastAPI** | - Starka AI/ML-bibliotek<br>- Async support<br>- Automatisk API-docs | - Kräver type hints för full nytta<br>- Annat språk än frontend |
| **Go** | - Utmärkt performance<br>- go-git library<br>- Enkelt deployment | - Mindre ekosystem för webdev<br>- Explicit error handling |
| **Rust + Axum** | - Bästa performance<br>- gitoxide library<br>- Memory safety | - Lång kompileringstid<br>- Steep learning curve |

### 2. Frontend-ramverk

**Fråga användaren:**
> Vilket frontend-ramverk vill du använda?

| Option | Fördelar | Editor-stöd |
|--------|----------|-------------|
| **React + TypeScript** | - Störst ekosystem<br>- Flexibelt<br>- Välkänt | TipTap, Slate, Lexical, ProseMirror |
| **Vue 3 + TypeScript** | - Enklare API<br>- Bättre perf out-of-box<br>- Composition API | TipTap (primärt), ProseMirror |
| **SvelteKit** | - Kompilerat (snabbt)<br>- Mindre kod<br>- Enkelt state | Mindre ekosystem, möjligt med TipTap |

### 3. Editor-bibliotek

**Baserat på frontend-val, fråga:**
> Vilket editor-bibliotek föredrar du?

**För React:**
- **TipTap** - Baserat på ProseMirror, bra dokumentation
- **Slate** - Flexibelt, svårare att lära sig
- **Lexical** - Meta's editor, växande ekosystem

**För Vue:**
- **TipTap** - Bästa stödet för Vue

### 4. Git-bibliotek

**Baserat på backend-val:**
> Vilket Git-bibliotek ska användas?

| Backend | Rekommenderat | Alternativ |
|---------|--------------|------------|
| Node.js | isomorphic-git | nodegit (libgit2 binding) |
| Python | pygit2 | GitPython |
| Go | go-git | - |
| Rust | gitoxide | git2-rs (libgit2 binding) |

### 5. Sökmotor

**Fråga användaren:**
> Vilken sökmotor vill du använda?

| Option | Fördelar | Användningsfall |
|--------|----------|-----------------|
| **Meilisearch** | Enkel setup, typo-tolerant, snabb | Mindre deployments, enkel search |
| **Elasticsearch** | Skalbar, avancerade queries, aggregeringar | Enterprise, komplex search |

### 6. AI-provider

**Fråga användaren:**
> Vilken AI-provider vill du primärt använda?

| Option | Fördelar |
|--------|----------|
| **OpenAI** | Bäst kvalitet (GPT-4), välkänt API |
| **Anthropic (Claude)** | Lång context, bra för dokument |
| **Self-hosted (Ollama)** | Datasäkerhet, air-gap kompatibel |
| **Provider-agnostic** | Flexibilitet, men mer komplexitet |

---

## Dokumentera beslut

När användaren har svarat, skapa en ADR (Architecture Decision Record):

```markdown
# ADR-001: Technology Stack

## Status
Accepted

## Context
Documentation Service Platform kräver val av teknologistack för implementation.

## Decision

### Backend
- **Ramverk:** [valt ramverk]
- **Motivering:** [användarens motivering eller rekommendation]

### Frontend
- **Ramverk:** [valt ramverk]
- **Editor:** [valt editor-bibliotek]
- **Motivering:** [motivering]

### Data & Search
- **Database:** PostgreSQL (fast)
- **Sökmotor:** [vald sökmotor]
- **Audit Store:** TimescaleDB / Append-only table

### Git Integration
- **Bibliotek:** [valt Git-bibliotek]

### AI
- **Primär provider:** [vald provider]
- **Design:** Provider-agnostic abstraction layer

## Consequences
[Lista konsekvenser av valet]

## Date
[Datum]
```

Spara ADR till `/docs/architecture/adr-001-technology-stack.md`.

---

## Generera projektkonfiguration

Efter beslut, generera:

1. **package.json** eller motsvarande för valt språk
2. **docker-compose.yml** med alla services
3. **Grundläggande katalogstruktur**
4. **Konfigurationsfiler** (tsconfig, eslint, etc.)
