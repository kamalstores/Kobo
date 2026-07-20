# Kobo — Comprehensive Project Documentation

> **Version**: 0.1.0 · **License**: MIT · **Author**: kamalstores  
> **Repository**: [github.com/kamalstores/Kobo](https://github.com/kamalstores/Kobo)

---

# Phase 1: The Genesis (The "Why")

## The Core Idea

**Kobo is a self-hosted AI agent runtime that behaves like a durable digital employee, not a disposable chatbot.**

If you were pitching this to an investor, the message would be:

> *"Most AI agent products forget the job between sessions. Kobo is built the other way around: you brief it once — goals, tools, source material, escalation rules — and it keeps working across sessions, on infrastructure you own and can inspect. It works as a personal operator on day one and becomes a durable workflow employee the moment the work starts repeating."*

### The Problem It Solves

| Problem | How Kobo Solves It |
|---|---|
| **Session amnesia** — AI agents forget context between conversations | Persistent memory (Mem0 + Qdrant), durable SQLite checkpoints, thread rollups, and saved skills |
| **Constant re-briefing** — users re-explain workflows every time | "Brief once" model with saved intake workflows, scheduled routines, and prepared knowledge packs |
| **Fragmented tooling** — separate bots for DMs, research, scheduling | Unified runtime handles Telegram chat, Instagram DMs, browser automation, web search, file analysis, and SaaS integrations |
| **Vendor lock-in** — data trapped in cloud AI services | Fully self-hosted. All state lives on local disk under `.Kobo/` and `kobo_stuff/` — back it up, mount it, or read it directly |
| **Integration friction** — custom code for every SaaS tool | Composio connector layer provides pre-built OAuth flows for Google Workspace, Slack, Notion, HubSpot, Gmail, Instagram, and 200+ apps |

## Target Audience

1. **Solo operators and small business owners** — who want an AI employee to handle inbound customer DMs (booking, lead qualification, FAQ) on Telegram Business or Instagram without writing bot code.
2. **Developers and technical power users** — who want a self-hosted agent they can inspect, extend with custom LangGraph tools, and deploy on their own infrastructure.
3. **Automation-forward teams** — who need scheduled monitoring routines (dashboards, competitor tracking, error alerts) and research workflows with persistent context.

---

# Phase 2: The Blueprint (Tech Stack & Architecture)

## Tech Stack Breakdown

### Language

| Technology | Version | Purpose |
|---|---|---|
| **Python** | ≥ 3.12 | Primary application language. Chosen for its ecosystem dominance in AI/ML, LangChain/LangGraph compatibility, and async support via `asyncio`. |
| **Bash** | — | Startup orchestration (`start.sh`). A ~790-line production-grade script that bootstraps `uv`, installs deps, manages tunnels, and prompts for configuration. |

### Core Frameworks

| Framework | Version | Role | Why This Choice |
|---|---|---|---|
| **FastAPI** | ≥ 0.109 | HTTP server, webhooks, internal API | Best-in-class async Python web framework. Handles Telegram webhooks, internal tool APIs, and SSE streaming. |
| **LangGraph** | ≥ 0.2 | Agent orchestration engine | Provides a stateful graph-based execution model with checkpointing — critical for multi-turn tool-calling loops with durable state. |
| **LangChain** | ≥ 0.3 | LLM abstraction layer | Standardizes model calls across OpenAI-compatible providers (OpenRouter, Groq, vLLM, DeepSeek, etc.). |
| **Uvicorn** | ≥ 0.27 | ASGI server | Production-ready async HTTP server with graceful shutdown support. |

### Data & Storage

| Technology | Role | Why This Choice |
|---|---|---|
| **SQLite** | Checkpoints, workflow state, profiles, skills, tasks, business inbox, events, wake queue | Zero-configuration embedded database. No external DB server needed. Persists to disk under `.Kobo/`. |
| **Qdrant (embedded)** | Vector store for memory retrieval | Embedded mode via Mem0 — no separate Qdrant server required. Stores semantic memory vectors on disk. |
| **Mem0** | Long-term memory service | Provides structured memory extraction and retrieval with semantic search. Categorizes memories by kind (preferences, facts, projects, etc.). |

### Key Libraries

| Library | Purpose |
|---|---|
| **langchain-openai** | OpenAI-compatible chat model bindings |
| **langchain-openrouter** | OpenRouter-specific chat model factory |
| **langchain-deepseek** | DeepSeek model support |
| **langgraph-checkpoint-sqlite** | SQLite-backed durable graph checkpoints |
| **httpx** | Async HTTP client for internal API calls, Telegram API, and external services |
| **pydantic-settings** | Configuration management with YAML + env + .env layered sources |
| **crawl4ai** | Web page content extraction (markdown/text) for `fetch_url_content` tool |
| **pypdf** | PDF text extraction for file analysis |
| **openpyxl** | Excel/spreadsheet parsing and structure inspection |
| **browser-use** | Playwright-based browser automation with LLM-driven control |
| **composio / composio-langchain** | Third-party SaaS app connectors (Google, Slack, Notion, HubSpot, etc.) |
| **apscheduler** | Cron-style routine scheduling |
| **langfuse** | Optional observability: trace turns, LLM calls, tool executions, and costs |
| **headroom-ai** | Audio transcription for voice message support |
| **Playwright** | Chromium browser engine for `browser-use` automation |

### Deployment

| Tool | Purpose |
|---|---|
| **Docker** | Containerized deployment via `Dockerfile` + `docker-compose.yml` |
| **Railway** | PaaS deployment with `railway.toml` (health checks, rolling deploys, drain windows) |
| **Cloudflare Tunnel (`cloudflared`)** | Local development: creates a public HTTPS endpoint for Telegram webhook delivery |
| **uv** | Fast Python package manager (replaces pip/poetry for dependency resolution) |

### External Services (Optional)

| Service | Purpose |
|---|---|
| **OpenRouter** | Default OpenAI-compatible model provider (routes to GPT-4, Claude, Gemini, etc.) |
| **Exa** | Alternative web search provider (semantic/neural search) |
| **Perplexity Sonar** | Default web search via OpenRouter |
| **Composio** | OAuth and tool execution for 200+ SaaS apps |
| **Browser Use Cloud** | Hosted browser sessions with profiles, proxying, and live owner handoff |
| **CapSolver** | CAPTCHA solving for browser automation (reCAPTCHA v2/v3, Cloudflare Turnstile) |
| **Langfuse** | Observability platform for LLM traces |
| **Telegram Bot API** | Primary chat interface |

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL CLIENTS                             │
│   Telegram Bot API ◄──── Webhook ────► POST /webhook/telegram          │
│   Instagram DMs ◄───── Composio ─────► Intake Workflow Service         │
│   Web Dashboard ◄──── SSE/REST ──────► /web/chat/* · /web/events       │
│   Composio OAuth ◄─── Callback ──────► /webhook/composio/callback      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Application                           │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Webhook      │  │  Internal    │  │  Web/Chat    │  │  Health    │ │
│  │  Routes       │  │  API Routes  │  │  Routes      │  │  Routes   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────────┘ │
│         │                 │                 │                          │
│         ▼                 ▼                 ▼                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              APPLICATION LAYER (Orchestrators)                  │   │
│  │  TurnOrchestrator · WakeOrchestrator · WorkflowSetupOrch.      │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                        │
│                               ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AGENT RUNTIME (LangGraph)                    │   │
│  │                                                                 │   │
│  │  ┌───────┐    ┌────────────────┐    ┌───────┐    ┌──────────┐  │   │
│  │  │ Agent │───►│ Validate Tools │───►│ Tools │───►│ Finalize │  │   │
│  │  │ Node  │    │     Node       │    │ Node  │    │   Turn   │  │   │
│  │  └───────┘    └────────────────┘    └───┬───┘    └──────────┘  │   │
│  │       ▲                                 │                       │   │
│  │       └─────────────────────────────────┘ (loop)               │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                        │
│         ┌─────────────────────┼─────────────────────┐                  │
│         ▼                     ▼                     ▼                  │
│  ┌────────────┐  ┌─────────────────────┐  ┌──────────────────────┐    │
│  │ Context    │  │ Integrations        │  │ Services             │    │
│  │ Engine     │  │                     │  │                      │    │
│  │ ─ Memory   │  │ ─ Browser Use       │  │ ─ Intake Workflows   │    │
│  │ ─ Profiles │  │ ─ Composio          │  │ ─ Scheduler          │    │
│  │ ─ Files    │  │ ─ Web Search        │  │ ─ Tasks/Sandbox      │    │
│  │ ─ Rollups  │  │ ─ Headroom (audio)  │  │ ─ Skills Store       │    │
│  │ ─ Events   │  │ ─ CapSolver         │  │ ─ Business Knowledge │    │
│  └────────────┘  └─────────────────────┘  └──────────────────────┘    │
│                                                                        │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE LAYER                             │
│                                                                        │
│  .Kobo/                               kobo_stuff/                     │
│  ├── langgraph_checkpoints.sqlite     ├── (generated artifacts)        │
│  ├── qdrant/  (vector embeddings)     └── __init__.py                  │
│  ├── context_events.db                                                 │
│  ├── customer_profiles.db                                              │
│  ├── thread_rollups.db                                                 │
│  ├── link_aliases.db                                                   │
│  ├── skills.db + skills/                                               │
│  ├── file_vault.db + file_vault/                                       │
│  ├── intake_workflows.db                                               │
│  ├── telegram_business.db                                              │
│  ├── telegram_state.json                                               │
│  ├── tasks.db · wake_events.db                                         │
│  ├── knowledge/ (knowledge.db + packs)                                 │
│  ├── user_context.db                                                   │
│  └── logs/agent_behavior.jsonl                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Communication Flow Summary

1. **Inbound** → Messages arrive via Telegram webhook, Instagram (Composio), or direct API call.
2. **Routing** → The Telegram interface layer parses updates, resolves `customer_id` and `thread_id`, and determines the turn mode (interactive, workflow setup, routine, intake).
3. **Orchestration** → `TurnOrchestrator` or `WakeOrchestrator` shapes the request and delegates to the LangGraph agent runtime.
4. **Execution** → The LangGraph `StateGraph` runs an `agent → validate_tools → tools → agent` loop until the model produces a final response or the turn budget is exhausted.
5. **Persistence** → Checkpoints, memories, tool outputs, and context events are persisted to SQLite/Qdrant for the next turn.
6. **Delivery** → The assistant reply is streamed back to Telegram or returned via API/SSE.

---

# Phase 3: The Map (Directory Structure)

```text
Kobo/
├── .env.example                    # Template for secrets and env vars
├── .gitignore
├── .dockerignore
├── Dockerfile                      # Multi-stage build: uv + Python 3.12 + Playwright
├── docker-compose.yml              # Single-service compose with persistent volume
├── railway.toml                    # Railway PaaS deployment config
├── pyproject.toml                  # Project metadata, dependencies, tool config
├── uv.lock                        # Pinned dependency lockfile
├── Kobo.config.yaml               # Non-secret runtime defaults (models, limits, paths)
├── start.sh                        # 790-line bootstrap/run orchestrator
├── LICENSE                         # MIT
├── README.md
│
├── docs/
│   ├── ARCHITECTURE.md             # Runtime layout, request flows, safety controls
│   ├── DEPLOYMENT.md               # Local, Docker, and Railway deployment guides
│   ├── E2E_TESTING.md              # End-to-end testing documentation
│   ├── CHAT_COOKBOOK.md             # Prompt patterns and use-case recipes
│   ├── EXTERNAL_TOOL_SAFETY_CHECKLIST.md
│   └── assets/                     # Logo and screenshots
│
├── scripts/
│   ├── manager.py                  # Local Telegram mode: app + Cloudflare tunnel + webhook sync
│   ├── replay_qwen_prompt_cache.py # Prompt cache replay testing utility
│   └── run_live_e2e_sections.py    # Live E2E test runner
│
├── src/Kobo/                       # ═══════════ MAIN SOURCE PACKAGE ═══════════
│   ├── __init__.py
│   ├── __main__.py                 # ★ APPLICATION ENTRY POINT — bootstraps all services
│   │
│   ├── core/                       # ── Foundation ──
│   │   ├── config.py               # ★ Settings class: env + YAML + .env layered config
│   │   ├── ids.py                  # Short ID generation
│   │   ├── debug_logs.py           # Process output capture and log management
│   │   ├── public_urls.py          # Public base URL resolution
│   │   └── shutdown_drain.py       # Graceful shutdown with active-turn tracking
│   │
│   ├── api/                        # ── HTTP Layer ──
│   │   ├── app.py                  # ★ FastAPI app factory: wires all services and routes
│   │   ├── kobo_loader.py          # Dynamic .kobo file router mounting
│   │   ├── customer_ids.py         # Customer ID resolution helpers
│   │   ├── file_helpers.py         # File upload/download utilities
│   │   ├── web_auth.py             # Web token authentication
│   │   └── routes/                 # ── 25 route modules ──
│   │       ├── chat.py             # POST /internal/chat
│   │       ├── generic_chat.py     # POST /web/chat/* (SSE streaming)
│   │       ├── telegram_webhook.py # POST /webhook/telegram
│   │       ├── intake.py           # Intake workflow CRUD + execution
│   │       ├── composio.py         # Composio auth flows and tool execution
│   │       ├── memory.py           # Memory search/add
│   │       ├── files.py            # File vault operations
│   │       ├── knowledge.py        # Business knowledge indexing/querying
│   │       ├── profiles.py         # Customer profile management
│   │       ├── skills.py           # Skill CRUD
│   │       ├── scheduler.py        # Routine scheduling
│   │       ├── tasks.py            # Background task management
│   │       ├── health.py           # GET /healthz, /agent/healthz
│   │       ├── web_events.py       # SSE web event stream
│   │       └── ... (11 more)
│   │
│   ├── application/                # ── Use-Case Orchestration ──
│   │   ├── turn_orchestrator.py    # Coordinates a single agent turn
│   │   ├── wake_orchestrator.py    # Routes scheduled/task wake events
│   │   └── workflow_setup_orchestrator.py  # Manages workflow setup sessions
│   │
│   ├── agent/                      # ── LangGraph Agent Runtime ── (largest module)
│   │   ├── runtime.py              # ★ 4774-line runtime: model init, streaming, tool dispatch
│   │   ├── graph_builder.py        # ★ StateGraph construction (agent → validate → tools → finalize)
│   │   ├── models.py               # AgentState TypedDict
│   │   ├── model_pool.py           # Model initialization and caching
│   │   ├── prompt_policy.py        # System prompt construction
│   │   ├── prompt_sections.py      # Prompt section assembly
│   │   ├── prompt_sources.py       # Context injection sources
│   │   ├── context_compaction.py   # Hysteresis-based thread context compression
│   │   ├── context_engine.py       # Token budget and context windowing
│   │   ├── tool_validation.py      # Pre-execution tool call validation
│   │   ├── tool_execution_policy.py# Turn-scoped execution constraints
│   │   ├── tool_loop_guardrails.py # Repetitive tool-call detection
│   │   ├── turn_budget.py          # Model call budget per turn
│   │   ├── turn_finalizer.py       # Reply normalization and fallback
│   │   ├── turn_policy.py          # Turn mode routing logic
│   │   ├── turn_plan.py            # Optional turn planning
│   │   ├── prompt_cache_policy.py  # Provider-specific prompt caching
│   │   ├── tools/                  # ── 23 tool modules ──
│   │   │   ├── core_tools.py       # File ops, web fetch, memory, directives
│   │   │   ├── browser_tools.py    # Browser Use automation
│   │   │   ├── composio_tools.py   # Composio SaaS connectors
│   │   │   ├── intake_workflow_tools.py   # Workflow CRUD tools
│   │   │   ├── intake_setup_tools.py      # Workflow setup tools
│   │   │   ├── web_tools.py        # Web search and URL fetching
│   │   │   ├── skill_tools.py      # Skill retrieval/creation
│   │   │   ├── routine_tools.py    # Scheduled routine management
│   │   │   ├── tool_gateway_tools.py      # Dynamic tool group gateway
│   │   │   └── ... (14 more)
│   │   ├── graph_nodes/            # Graph node implementations
│   │   └── turn_prompt_builder/    # Multi-stage prompt assembly
│   │
│   ├── interfaces/                 # ── Transport Adapters ──
│   │   └── telegram/               # ── 16 Telegram modules ──
│   │       ├── chat_service.py     # ★ Main Telegram chat handler (65KB)
│   │       ├── relay.py            # ★ Streaming relay to Telegram (49KB)
│   │       ├── client.py           # Telegram Bot API client
│   │       ├── business.py         # Telegram Business inbox service
│   │       ├── attachments.py      # Photo/document/voice/video handling
│   │       ├── state_store.py      # Owner/support session state
│   │       ├── security.py         # Allowlist enforcement
│   │       └── ... (9 more)
│   │
│   ├── context/                    # ── Durable Context Layer ──
│   │   ├── customer_profiles.py    # Profile storage and alias resolution
│   │   ├── file_vault.py           # Uploaded file storage and retrieval
│   │   ├── user_context.py         # User context indexing and search
│   │   ├── link_aliases.py         # Short alias registry for long URLs
│   │   ├── thread_rollups.py       # Compressed conversation history
│   │   ├── service.py              # Event context service (backlog)
│   │   └── uploaded_files.py       # File upload processing
│   │
│   ├── intake/                     # ── Intake Workflow Engine ──
│   │   ├── service.py              # ★ Workflow execution engine (100KB)
│   │   ├── store.py                # SQLite-backed workflow state
│   │   ├── workflow_runner.py      # Workflow decision loop
│   │   ├── workflow_setup_service.py # Conversational workflow builder
│   │   ├── sink_writer.py          # Output writing (Google Sheets, CSV, etc.)
│   │   ├── decision_maker.py       # LLM-powered field extraction
│   │   ├── messaging_adapters.py   # Channel-specific message formatting
│   │   └── ... (7 more)
│   │
│   ├── integrations/               # ── External Service Adapters ──
│   │   ├── browser_use_local.py    # Local Playwright browser automation (62KB)
│   │   ├── browser_use_cloud.py    # Browser Use Cloud sessions
│   │   ├── browser_use_captcha.py  # CAPTCHA solving integration
│   │   ├── composio.py             # Composio SDK wrapper (22KB)
│   │   ├── composio_google_sheets.py # Google Sheets-specific helpers
│   │   ├── composio_instagram.py   # Instagram DM handling
│   │   ├── web_search.py           # Exa + Perplexity Sonar search
│   │   ├── headroom.py             # Audio transcription
│   │   └── capsolver.py            # CapSolver CAPTCHA API client
│   │
│   ├── business_knowledge/         # ── Knowledge Pack System ──
│   │   ├── service.py              # Knowledge indexing and retrieval
│   │   ├── extraction.py           # Content extraction from files
│   │   ├── oracle_client.py        # LLM-grounded Q&A over knowledge
│   │   ├── table_normalizer.py     # Spreadsheet normalization
│   │   └── ... (4 more)
│   │
│   ├── memory/                     # Memory service (Mem0 wrapper)
│   ├── skills/                     # Durable skill store
│   ├── scheduler/                  # APScheduler-based routine engine
│   ├── tasks/                      # Background task runner + sandbox
│   ├── persistence/                # SQLite policy enforcement
│   ├── logging/                    # Langfuse observability integration
│   ├── domain/                     # Domain contracts (Conversation model)
│   └── web/                        # Web event store (SSE backend)
│
└── tests/                          # ═══════════ TEST SUITE ═══════════
    ├── 116 test files              # Unit, integration, and E2E tests
    ├── e2e/                        # End-to-end test scenarios
    └── workbook_fixtures.py        # Test data generators
```

### Key Files at a Glance

| File | Lines | Role |
|---|---|---|
| `src/Kobo/agent/runtime.py` | 4,774 | The central runtime — model initialization, streaming, tool dispatch, compaction, and all LLM orchestration |
| `src/Kobo/intake/service.py` | ~2,800 | Intake workflow engine — DM processing, booking state, conversation cursors, sink writes |
| `src/Kobo/interfaces/telegram/chat_service.py` | ~1,700 | Telegram transport — parses updates, resolves identities, manages owner/support/business sessions |
| `src/Kobo/interfaces/telegram/relay.py` | ~1,300 | Streaming relay — chunks LLM output into Telegram messages with typing indicators |
| `src/Kobo/integrations/browser_use_local.py` | ~1,600 | Browser automation — Playwright sessions, screenshot capture, task lifecycle |
| `src/Kobo/agent/graph_builder.py` | ~895 | LangGraph graph construction — nodes, edges, tool execution loop |
| `src/Kobo/api/app.py` | 749 | FastAPI app factory — wires every service, route, and lifecycle hook |
| `start.sh` | 790 | Bootstrap script — uv, deps, Playwright, cloudflared, env prompts, app launch |

---

# Phase 4: The Engine (Core Mechanics & APIs)

## Data Flow: Lifecycle of a Telegram Message

Here is what happens step-by-step when a user sends a message to the Kobo bot on Telegram:

```text
1. TELEGRAM WEBHOOK DELIVERY
   Telegram POST → /webhook/telegram
   ├── Header: x-telegram-bot-api-secret-token (validated)
   └── Body: Telegram Update JSON

2. WEBHOOK PARSING & SECURITY
   telegram_webhook.py → chat_service.py
   ├── Parse update type (message, business_message, callback_query)
   ├── Extract text, attachments (photo/document/voice/video)
   ├── Resolve customer_id from Telegram user → profile alias resolution
   ├── Resolve thread_id (owner chat, support chat, or business inbox)
   ├── Check TELEGRAM_ALLOWED_USERNAMES / TELEGRAM_ALLOWED_USER_IDS
   └── Determine turn_mode: interactive | workflow_setup | intake

3. MULTIMODAL PRE-PROCESSING (if attachments present)
   file_analysis.py
   ├── Images → multimodal LLM (Gemini Flash) → text description
   ├── Documents → PDF/DOCX/Excel extraction → text summary
   ├── Voice → Headroom AI transcription → text
   ├── Video → frame extraction + multimodal LLM → description
   └── Store processed files in FileVault

4. TURN ORCHESTRATION
   TurnOrchestrator → agent runtime
   ├── Load durable context: workflow state, memory, profiles, events
   ├── Check for active workflow setup session
   ├── Prepare turn context (token-budgeted prompt assembly)
   └── Invoke LangGraph StateGraph

5. LANGGRAPH EXECUTION LOOP
   agent_node → validate_tools → tools_node → (repeat or finalize)
   │
   ├── AGENT NODE
   │   ├── Build turn prompt (system prompt + memory + context + history)
   │   ├── Apply prompt caching (Anthropic/Gemini cache breakpoints)
   │   ├── Invoke LLM with tool bindings
   │   └── Route: has_tool_calls → validate_tools | no_tools → finalize
   │
   ├── VALIDATE TOOLS NODE
   │   ├── Check required arguments present
   │   ├── Strip forbidden arguments (e.g., customer_id injection)
   │   ├── Enforce tool loop guardrails (detect repetitive calls)
   │   └── Pass validated calls to tools node
   │
   ├── TOOLS NODE
   │   ├── Set customer/thread/turn-mode scope via context vars
   │   ├── Execute each tool call (web search, file ops, Composio, etc.)
   │   ├── Emit interactive progress updates to Telegram
   │   ├── Compact tool results for model context budget
   │   ├── Track tool outcomes for final response hints
   │   └── Return → agent node for next reasoning step
   │
   └── FINALIZE TURN
       ├── Apply reply length limits (default: 4,000 chars)
       ├── Handle empty/blank reply fallback
       └── Return final assistant message

6. STREAMING RELAY TO TELEGRAM
   relay.py
   ├── Stream LLM chunks as they arrive
   ├── Send typing indicator during tool execution
   ├── Split long replies into multiple Telegram messages
   ├── Format with Telegram HTML (bold, code blocks, links)
   └── Handle stream timeout fallback

7. POST-TURN PERSISTENCE
   ├── Checkpoint LangGraph state to SQLite
   ├── Extract and store memories via Mem0
   ├── Update thread rollup for context compaction
   ├── Persist context events to backlog
   ├── Register URL aliases from tool outputs
   └── Log turn to agent_behavior.jsonl + optional Langfuse trace
```

## API Integrations

### Internal API Routes (`/internal/*`)

These routes are restricted to localhost/private network traffic:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/internal/chat` | Direct text chat (non-Telegram) |
| `POST` | `/internal/wake` | Process scheduled wake events |
| `POST` | `/internal/search` | Web search proxy |
| `GET/POST` | `/internal/memory/*` | Memory search and add |
| `POST` | `/internal/files/send` | Send files to Telegram |
| `GET/POST` | `/internal/profiles/*` | Customer profile CRUD |
| `GET/POST` | `/internal/skills/*` | Skill store CRUD |
| `GET/POST` | `/internal/scheduler/*` | Routine scheduling |
| `GET/POST` | `/internal/tasks/*` | Background task management |
| `GET/POST` | `/internal/composio/*` | Composio auth and tool execution |
| `GET/POST` | `/internal/intake/*` | Intake workflow CRUD and execution |
| `GET/POST` | `/internal/knowledge/*` | Business knowledge indexing/querying |
| `GET/POST` | `/internal/user-context/*` | User context management |

### Webhook Routes (`/webhook/*`)

Public internet accessible:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/webhook/telegram` | Telegram Bot API webhook (secret-token authenticated) |
| `GET` | `/webhook/composio/callback` | Composio OAuth callback landing |

### Web/Dashboard Routes (`/web/*`)

Authenticated via `Kobo_WEB_TOKEN`:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/web/chat/{customer_id}` | SSE streaming chat for web dashboard |
| `GET` | `/web/events` | SSE event stream (proactive messages, routine results) |
| `GET` | `/web/intake/workflows` | List intake workflows |
| `POST` | `/web/files/upload` | File upload for web clients |
| `GET` | `/web/telegram/status` | Telegram webhook health |

### Health Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/healthz` | App health check (returns 503 during drain) |
| `GET` | `/agent/healthz` | Agent runtime health check |

---

## Advanced Concepts

### 1. Context Compaction (Hysteresis-Based)

Kobo uses a **high-watermark / low-watermark** strategy to manage conversation context:

- **High watermark** (`AGENT_CONTEXT_TOKEN_LIMIT` = 20,000 tokens): When the thread context exceeds this, compaction triggers.
- **Low watermark** (`AGENT_CONTEXT_RECENT_TOKENS` = 3,500 tokens): After compaction, only recent messages within this budget are kept verbatim.
- **Rollup budget** (`AGENT_CONTEXT_ROLLUP_TOKENS` = 2,200 tokens): Older history is compressed by an LLM into a bounded summary injected as system context.
- **Source window** (`AGENT_CONTEXT_COMPACTION_SOURCE_TOKENS` = 12,000 tokens): Maximum span of oldest tokens processed per compaction pass.

This prevents unbounded context growth while preserving the most important historical context.

### 2. Prompt Caching

Provider-specific prompt caching reduces costs and latency:

- **Anthropic models**: Receive explicit `cache_control` markers on stable prompt prefix content.
- **Gemini models**: Use per-message cache breakpoints on the stable system prompt prefix.
- **OpenAI-compatible models**: Rely on provider-side automatic caching (no explicit markers).

The `turn_prompt_builder` separates stable prefix content (system prompt, memory, skills) from turn-volatile content (recent messages, tool results) to maximize cache hit rates.

### 3. Tool Validation & Safety

Tool calls go through multiple validation layers before execution:

1. **Required argument validation** — ensures all mandatory parameters are present.
2. **Forbidden argument stripping** — prevents the model from injecting `customer_id` into tool calls (the runtime supplies it from the authenticated scope).
3. **Tool loop guardrails** — detects and breaks repetitive tool-call patterns (e.g., fetching the same URL repeatedly).
4. **Turn budget enforcement** — limits model calls and tool rounds per turn to prevent runaway execution.
5. **Execution origin tracking** — tags whether the tool call originated from interactive chat, workflow setup, routine, or wake event.

### 4. Intake Workflow Engine

The intake workflow system is a fully autonomous DM handler:

1. **Setup phase**: Owner describes the job in chat → workflow setup tools build a structured `IntakeWorkflow` with required fields, source material, sink configuration, and behavior rules.
2. **Knowledge preparation**: Large source files (spreadsheets, PDFs, policy docs) are inspected, relevant sections extracted, and compiled into smaller knowledge packs bound to the workflow.
3. **Execution phase**: Inbound DMs are processed by the LLM against the workflow definition → fields are extracted → missing fields trigger follow-up questions → complete bookings are written to configured sinks (Google Sheets, CSV, etc.).
4. **Idempotency**: Per-conversation cursors prevent reprocessing the same message.

### 5. Memory Architecture

Memory uses **Mem0** with an embedded **Qdrant** vector store:

- Memories are categorized by kind with priority ordering: `directive_fact` > `preference_fact` > `user_profile_fact` > `life_fact` > `project_fact` > `skill_fact` > ...
- Memory grounding sections are injected into the system prompt organized by category.
- A separate `memory_llm_model` (default: Gemini Flash) handles background memory extraction so it doesn't interfere with the main chat model.

### 6. Multi-Model Architecture

Kobo uses **different models for different roles** to optimize cost and capability:

| Role | Default Model | Purpose |
|---|---|---|
| Main chat | `z-ai/glm-5.2` | Primary reasoning and tool calling |
| Memory extraction | `google/gemini-3-flash-preview` | Background memory operations |
| Multimodal understanding | `google/gemini-3.1-flash-lite-preview` | Image, audio, video analysis |
| Business knowledge oracle | `google/gemini-3.1-flash-lite-preview` | Source-grounded Q&A |
| Browser automation | `google/gemini-3-flash-preview` | Browser Use step decisions |
| Context compaction | `google/gemini-3-flash-preview` | Thread history compression |
| Wake classification | Configurable (null = main model) | Routine notify decisions |

### 7. Graceful Deployment Shutdown

The `ShutdownDrain` system ensures in-flight work completes during deploys:

1. App marks itself **draining** → `/healthz` returns `503`.
2. New turns are rejected by the old process.
3. Active turns are allowed to finish until `Kobo_SHUTDOWN_DRAIN_TIMEOUT_SECONDS` (default: 300s).
4. Railway uses `overlapping deploys` + `drainingSeconds: 300` so the new process starts before the old one fully stops.

### 8. Observability Stack

- **Structured JSONL logs** (`agent_behavior.jsonl`): Every turn lifecycle event, graph node outcome, tool execution, and workflow retry is logged.
- **Langfuse traces** (optional): Full turn traces with LLM call details, token usage, costs, cache hit rates, and tool execution spans.
- **Debug logs command** (`/debug_logs`): Telegram bot command that sends the last 7 days of server logs as a file.

---

# Phase 5: The Workshop (Setup & Execution)

## Prerequisites

- **OS**: macOS or Linux (with `bash` and `curl`)
- **Python**: 3.12+ (managed via `uv`)
- **A Telegram bot token** from [@BotFather](https://t.me/BotFather)
- **An OpenAI-compatible API key** (OpenRouter recommended; also supports Groq, local vLLM, etc.)

## Option A: Quick Start (Local with Telegram)

```bash
# 1. Clone the repository
git clone https://github.com/kamalstores/Kobo.git
cd Kobo

# 2. Run the start script
./start.sh
```

**What `start.sh` does automatically:**

1. Installs `uv` (Astral's Python package manager) if missing.
2. Runs `uv sync` to install Python 3.12 and all dependencies.
3. Installs Chromium via Playwright for browser automation (skip with `--no-browser-use`).
4. Installs `cloudflared` for the Telegram tunnel (skip with `--no-cloudflared`).
5. Creates `.env` from `.env.example` and prompts for missing values.
6. Starts the app on `127.0.0.1:8000`, opens a Cloudflare tunnel, and points Telegram at the webhook.

**After startup**, message your bot on Telegram. Health check: `http://127.0.0.1:8000/healthz`.

### Start Script Modes

```bash
# Full local setup (install + run with Telegram tunnel)
./start.sh local          # or just ./start.sh

# Server mode (no tunnel, requires PUBLIC_BASE_URL)
./start.sh server

# Install dependencies only
./start.sh install

# Run without re-installing
./start.sh run local
./start.sh run server

# Check readiness
./start.sh doctor local
./start.sh doctor server

# Skip optional components
./start.sh --no-browser-use --no-cloudflared
```

## Option B: Docker

```bash
# 1. Clone and configure
git clone https://github.com/kamalstores/Kobo.git
cd Kobo
cp .env.example .env
# Edit .env with your API keys and tokens

# 2. Build and run
docker compose up --build
```

The Docker Compose setup:
- Builds from the Dockerfile (Python 3.12 + uv + Playwright + Node.js)
- Mounts a persistent volume at `/app/Kobo`
- Exposes port `8000`

## Option C: Railway

1. Fork the repo on GitHub.
2. Create a new Railway project from the fork.
3. Set environment variables in Railway dashboard:
   - `OPENAI_COMPATIBLE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_WEBHOOK_SECRET`
   - `TELEGRAM_ALLOWED_USERNAMES`
   - `Kobo_DATA_ROOT=/app/Kobo_data`
4. Mount a persistent volume at `/app/Kobo_data`.
5. Deploy. Railway auto-configures the webhook via `RAILWAY_PUBLIC_DOMAIN`.

## Environment Variables Reference

### Required

| Variable | Description |
|---|---|
| `OPENAI_COMPATIBLE_API_KEY` | API key for your OpenAI-compatible provider |

### Required for Telegram

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_ALLOWED_USERNAMES` | Comma-separated usernames (without @) |

### Required for Server Mode

| Variable | Description |
|---|---|
| `Kobo_DATA_ROOT` | Path for persistent data storage |
| `PUBLIC_BASE_URL` | Public HTTPS URL for webhook (or `RAILWAY_PUBLIC_DOMAIN`) |
| `TELEGRAM_WEBHOOK_SECRET` | Secret token for webhook verification |

### Optional but Recommended

| Variable | Description |
|---|---|
| `COMPOSIO_API_KEY` | Enables Google Sheets, Gmail, Slack, Instagram, and 200+ SaaS connectors |
| `BROWSER_USE_API_KEY` | Enables Browser Use Cloud hosted browser sessions |
| `EXA_API_KEY` | Enables Exa semantic web search (otherwise uses Perplexity Sonar) |
| `CAPSOLVER_API_KEY` | Enables CAPTCHA solving for browser automation |

### Optional Observability

| Variable | Description |
|---|---|
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing (both keys required to enable) |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing |
| `LANGFUSE_BASE_URL` | Defaults to `https://us.cloud.langfuse.com` |

### Model Overrides

All model defaults live in `Kobo.config.yaml` and can be overridden via env vars:

| Variable | Default | Purpose |
|---|---|---|
| `LLM_MODEL` | `z-ai/glm-5.2` | Main chat model |
| `MEMORY_LLM_MODEL` | `google/gemini-3-flash-preview` | Memory extraction |
| `MULTIMODAL_LLM` | `google/gemini-3.1-flash-lite-preview` | Image/audio/video analysis |
| `BROWSER_USE_MODEL` | `google/gemini-3-flash-preview` | Browser automation |
| `BUSINESS_KNOWLEDGE_ORACLE_MODEL` | `google/gemini-3.1-flash-lite-preview` | Knowledge Q&A |

## Running Tests

```bash
# Install dev dependencies
uv sync --dev

# Run all unit tests
uv run pytest tests/ -x

# Run with specific markers
uv run pytest tests/ -m "not e2e and not live_llm" -x

# Run E2E tests (requires API key)
uv run pytest tests/ -m e2e -x
```

## Verifying the Setup

```bash
# Run the doctor check
./start.sh doctor local

# Manual health check
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/agent/healthz
```

---

> **Architecture document generated from source analysis of the [Kobo](file:///Users/kamal/Desktop/Project/Kobo) repository.**
