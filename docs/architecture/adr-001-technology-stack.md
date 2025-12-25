# ADR-001: Technology Stack

## Status
Accepted

## Context
Documentation Service Platform kräver val av teknologistack för implementation. Plattformen ska stödja:
- Diátaxis-baserad dokumentationsstruktur
- ISO 9001/13485 och FDA 21 CFR Part 11 compliance
- Git-baserad versionshantering med abstraherad komplexitet
- Realtidssamarbete med CRDT
- AI-genererad bedömning och skrivassistans
- Bidirektionell MCP-integration

## Decision

### Backend
- **Ramverk:** Python + FastAPI
- **Motivering:**
  - Starka AI/ML-bibliotek (LangChain, transformers)
  - Utmärkt async support för realtidsfeatures
  - Automatisk OpenAPI-dokumentation
  - Type hints ger god utvecklarupplevelse
  - Väletablerat för dokumentbearbetning

### Frontend
- **Ramverk:** React + TypeScript
- **Editor:** TipTap (ProseMirror-baserad)
- **Motivering:**
  - Störst ekosystem för block-baserade editorer
  - TipTap har utmärkt dokumentation och Yjs-integration för CRDT
  - TypeScript ger typsäkerhet och bättre IDE-stöd
  - Stort community och många färdiga komponenter

### Data & Search
- **Database:** PostgreSQL (med TimescaleDB för audit trail)
- **Sökmotor:** Meilisearch
- **Audit Store:** Append-only table med kryptografisk kedja
- **Motivering:**
  - Meilisearch är enkel att konfigurera och snabb
  - Typo-tolerant sökning out-of-the-box
  - PostgreSQL är beprövad och har utmärkt stöd för JSON

### Git Integration
- **Bibliotek:** pygit2 (libgit2 Python binding)
- **Motivering:**
  - Fullständig Git-funktionalitet utan shell calls
  - Bra performance jämfört med GitPython
  - Stabil och väldokumenterad

### Real-time Collaboration
- **CRDT Library:** Yjs
- **Transport:** WebSocket via FastAPI
- **Motivering:**
  - Yjs är de facto standard för CRDT i webapplikationer
  - TipTap har inbyggt Yjs-stöd
  - y-py finns för Python-backend integration

### AI Services
- **Design:** Provider-agnostic abstraction layer
- **Stödda providers:** OpenAI, Anthropic, lokala modeller (Ollama)
- **Motivering:**
  - Flexibilitet att byta provider utan kodändringar
  - Möjlighet till air-gapped deployment med lokala modeller
  - Kostnadskontroll genom val av lämplig modell per användningsfall

## Consequences

### Positiva
- Python + FastAPI ger snabb prototyping och utveckling
- TipTap + React ger en kraftfull och flexibel editor
- Provider-agnostic AI möjliggör compliance-vänliga deployments
- Meilisearch förenklar sökimplementation avsevärt

### Negativa
- Två olika språk (Python backend, TypeScript frontend) kräver bredare kompetens
- pygit2 kräver libgit2 systembibliotek vid deployment
- Provider-agnostic AI-lager kräver mer initial utvecklingstid

### Risker
- Yjs + y-py integration kan kräva extra arbete för synkronisering
- Meilisearch saknar vissa avancerade aggregeringsfunktioner

## Technical Details

### Python Dependencies (Core)
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pygit2>=1.14.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.26.0
meilisearch>=0.31.0
y-py>=0.6.0
```

### Frontend Dependencies (Core)
```
react: ^18.2.0
typescript: ^5.3.0
@tiptap/react: ^2.2.0
@tiptap/starter-kit: ^2.2.0
@tiptap/extension-collaboration: ^2.2.0
yjs: ^13.6.0
y-websocket: ^1.5.0
@tanstack/react-query: ^5.17.0
zustand: ^4.5.0
```

## Date
2025-12-17

## Authors
- Technology decision recorded via /docservice:tech-decision
