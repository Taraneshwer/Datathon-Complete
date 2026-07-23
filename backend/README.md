# AI Crime Intelligence & Investigation Platform

> **International Hackathon Submission**
> **Challenge:** AI-Driven Crime Analytics & Visualization Platform
> **Organization:** Karnataka State Police (KSP)

---

## Architecture Overview

```
External Sources (FIR, CCTNS, CCTV, GPS, Drone, IoT, Emergency Calls)
                          │
              ┌───────────▼───────────┐
              │   Data Ingestion      │  POST /api/v1/ingest
              │   + Trust Layer       │  (Completeness · Quality · Geo · Duplicate)
              └───────────┬───────────┘
                          │
    ┌─────────────────────▼─────────────────────────────┐
    │            AI Intelligence Processing Layer        │
    │  Pattern Matching   │  Hotspot Prediction          │
    │  Knowledge Graph    │  Crime Replay Engine         │
    │  Evidence AI        │  Bias Detector               │
    │  Blind-Spot Finder  │  Intervention Recommender    │
    │  National Early Warning   │  AI Assistant (RAG)   │
    └─────────────────────┬─────────────────────────────┘
                          │
    ┌─────────────────────▼─────────────────────────────┐
    │              Intelligence Storage Layer            │
    │  Zoho Catalyst Data Store │  Neo4j  │  Qdrant │
    │  Zoho Catalyst File Store                         │
    │  Blockchain Audit Trail (Hyperledger Fabric stub) │
    └───────────────────────────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │  Zoho Catalyst Cloud  │  Auth · API GW · Functions
              │  Services Layer       │  File Store · Monitoring
              └───────────┬───────────┘
                          │
              WebSocket Real-time Alerts
                          │
              React Intelligence Dashboard
```

---

## Project Structure

```
DATATHON_BACKEND/
├── .env.example
├── requirements.txt
├── pyproject.toml
└── app/
    ├── main.py               ← FastAPI factory + 4-stage lifespan
    ├── config.py             ← pydantic-settings
    ├── dependencies.py       ← FastAPI Depends() factories
    │
    ├── auth/
    │   ├── jwt_handler.py    ← JWT creation/verification + bcrypt
    │   └── rbac.py           ← 6-role RBAC + permission matrix
    │
    ├── models/
    │   ├── fir.py            ← SQLModel: Officer, Case, Evidence,
    │   │                        BlockchainRecord, SystemAlert, AuditTrail
    │   └── schemas.py        ← Pydantic v2 API schemas
    │
    ├── db/
    │   ├── catalyst.py       ← Zoho Catalyst Data Store client
    │   ├── neo4j_client.py   ← Async Neo4j driver + schema bootstrap
    │   └── qdrant_client.py  ← Async Qdrant client + collection
    │
    ├── intelligence/
    │   ├── firewall.py       ← Prompt injection ASGI middleware
    │   ├── pattern_matcher.py← Qdrant cosine similarity search
    │   ├── hotspot_predictor.py ← DBSCAN / HDBSCAN geo-clustering
    │   ├── crime_replay.py   ← Chronological investigation timeline
    │   ├── bias_detector.py  ← 5-check investigation bias analysis
    │   ├── blind_spot_detector.py ← H3 surveillance gap detection
    │   ├── intervention_recommender.py ← Rule-based policing strategies
    │   ├── early_warning.py  ← National crime trend monitoring
    │   └── evidence_analyzer.py ← CV + OCR + Whisper STT pipeline
    │
    ├── services/
    │   ├── embedding_service.py ← BGE-M3 async wrapper
    │   ├── graph_service.py  ← Neo4j 8-node-type Cypher service
    │   ├── ingest_service.py ← Orchestrated multi-DB ingestion pipeline
    │   ├── trust_service.py  ← Data Trust Layer (5 validation checks)
    │   └── blockchain_service.py ← SHA-256 audit chain + Fabric stub
    │
    ├── assistant/
    │   ├── prompt_templates.py ← Hardened system prompt
    │   └── rag_graph.py      ← LangGraph 6-node RAG pipeline
    │
    ├── routers/
    │   ├── auth.py           ← Login + register + MFA
    │   ├── ingest.py         ← FIR ingest + pattern match + hotspots
    │   ├── analytics.py      ← Replay + Bias + BlindSpot + EarlyWarning
    │   ├── evidence.py       ← AI evidence upload + analysis
    │   ├── assistant.py      ← RAG investigative chat
    │   └── websocket.py      ← Real-time alert stream
    │
    └── websocket/
        └── connection_manager.py ← Topic-filtered WebSocket broadcast
```

---

## Quick Start

### 1. Start Infrastructure Services

```bash
# Catalyst Data Store
# (Configured natively via AppSail or Zoho Catalyst CLI)

# Neo4j
docker run -d --name neo4j \
  -e NEO4J_AUTH=neo4j/password \
  -p 7474:7474 -p 7687:7687 neo4j:5

# Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 2. Install & Configure

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — fill in ZOHO_CATALYST_PROJECT_ID, NEO4J_*, NVIDIA_API_KEY etc.
```

### 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

API Docs → **http://localhost:8000/docs**

---

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/login` | Badge + password + optional MFA |
| `POST` | `/auth/refresh` | Exchange refresh token |
| `POST` | `/auth/register` | Create officer account |
| `GET`  | `/auth/me` | Current officer profile |
| `POST` | `/auth/mfa/setup` | Generate TOTP secret |
| `POST` | `/auth/mfa/verify` | Activate MFA |

### Ingestion (`/api/v1/ingest`)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ingest` | Ingest FIR → Trust → Catalyst Data Store + Neo4j + Qdrant + Blockchain |
| `POST` | `/ingest/match` | Semantic pattern matching |
| `POST` | `/ingest/hotspots` | DBSCAN / HDBSCAN hotspot prediction |

### Intelligence Analytics (`/api/v1/analytics`)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/analytics/replay/{case_id}` | Crime timeline reconstruction |
| `POST` | `/analytics/bias/{case_id}` | Investigation bias detection |
| `POST` | `/analytics/blind-spots` | H3 surveillance gap discovery |
| `POST` | `/analytics/interventions` | Policing strategy recommendations |
| `POST` | `/analytics/early-warning` | National crime trend monitoring |
| `GET`  | `/analytics/blockchain/{case_id}` | Audit chain verification |

### Evidence (`/api/v1/evidence`)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/evidence/{case_id}/analyze` | Upload + AI analysis (CV/OCR/Whisper) |
| `GET`  | `/evidence/{case_id}` | List evidence with AI results |

### AI Assistant (`/api/v1/assistant`)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/assistant/chat` | LangGraph RAG investigative query |
| `GET`  | `/assistant/health` | LLM provider health check |

### Real-time (`/api/v1/ws`)
| Method | Path | Description |
|--------|------|-------------|
| `WS`   | `/ws/alerts` | Live alert stream (topic-filtered) |
| `POST` | `/ws/broadcast` | Admin alert broadcast |
| `GET`  | `/ws/status` | Active connection count |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn |
| Language | Python 3.11 |
| Relational DB | Zoho Catalyst Data Store (ZCQL) |
| Graph DB | Neo4j (official async driver) |
| Vector DB | Qdrant (AsyncQdrantClient) |
| Embeddings | BGE-M3 (BAAI/bge-m3) |
| AI Orchestration | LangGraph + LangChain |
| ML | scikit-learn (DBSCAN), XGBoost, HDBSCAN |
| Computer Vision | OpenCV + YOLOv11 (stub) |
| OCR | EasyOCR (English + Kannada) |
| Speech-to-Text | OpenAI Whisper |
| Geospatial | H3, GeoPandas, Shapely |
| Blockchain | SHA-256 chain + Hyperledger Fabric stub |
| Auth | JWT (python-jose) + bcrypt + TOTP MFA |
| Cloud | Zoho Catalyst |
| Observability | OpenTelemetry + structlog |

---

## RBAC Roles

| Role | Permissions |
|---|---|
| `super_admin` | Full platform access |
| `district_admin` | District management + all operations |
| `io` (Investigating Officer) | FIR filing, evidence, AI queries |
| `analyst` | Read-only + intelligence queries |
| `forensic_expert` | Evidence upload and analysis |
| `field_officer` | FIR filing only |
| `court_liaison` | Court submission access |

---

## Security Features

- **JWT Authentication** — short-lived access + long-lived refresh tokens
- **TOTP MFA** — Google Authenticator compatible
- **Prompt Injection Firewall** — blocks 30+ injection patterns at ASGI layer
- **Blockchain Audit Trail** — SHA-256 chained immutable records, Fabric-ready
- **Data Trust Layer** — 5-point validation gate before any data enters the system
- **RBAC** — 6-tier role hierarchy with per-endpoint permission matrix
- **Zero Trust** — no debug stack traces in production responses
