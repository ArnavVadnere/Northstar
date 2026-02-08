# Financial Compliance Auditor

## Product Requirements Document

**Hackathon MVP — Columbia DevFest 2026**
Version 4.0 | Updated Feb 7, 2026 | Team: [Your Team Name]

---

## 1. Executive Summary

| Field | Details |
|-------|---------|
| Product Name | Financial Compliance Auditor |
| Track | Business & Enterprise |
| Prize Target | Best Use of Tool-Calling + Best Use of Dedalus API |
| Demo Time | 3 minutes |
| MVP Timeline | 10 hours |
| Team | 3 engineers ($300 total credits available) |
| Frontend | Next.js 14 + React + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI + uvicorn |
| Database | Supabase (PostgreSQL) |
| AI Pipeline | Dedalus SDK with 3 agents + MCP tool-calling |
| Discord | discord.py bot with slash commands |

**One-liner:** AI-powered compliance auditor that analyzes financial PDFs against live 2026 regulations via a Next.js dashboard and Discord bot, delivering executive reports in under 90 seconds.

---

## 2. Problem & Opportunity

Finance teams spend 40+ hours manually auditing SOX 404, 10-Ks, and invoices against ever-changing SEC/FINRA rules. Missing gaps can lead to million-dollar fines.

Our edge is a Dedalus-powered pipeline that extracts PDFs, researches live rules, and produces remediation playbooks in under 60 seconds — accessible from both a polished React dashboard and directly inside Discord.

**Success Metrics:**

- Process a 10-K PDF in under 90 seconds
- Flag at least 3 realistic compliance gaps
- Deliver results via both the Next.js UI and Discord bot with embed + PDF attachment

---

## 3. User Personas & Stories

Primary users include CFOs, Compliance Officers, and External Auditors.

**Key User Stories:**

- As a CFO, I upload a SOX PDF via the web dashboard and review my compliance score with gap details.
- As a Compliance Officer, I drop a 10-K PDF into our Discord channel and the bot replies with a full audit report in-thread.
- As an External Auditor, I use the /audit slash command in Discord to trigger an audit and receive results without leaving the chat.
- As a returning user, I view my audit history to track compliance improvements over time.
- As a judge at DevFest, I can interact with the bot in Discord to see it work live.

---

## 4. MVP Features

### 4a. Next.js Web Dashboard (Owner: Person 3)

A polished React frontend built with Next.js and Tailwind CSS, giving full design control and a professional look that stands out from typical hackathon demos.

**Pages & Components:**

- **Landing / Upload Page** — document type selector (SOX 404, 10-K, Invoice), drag-and-drop PDF upload zone, "Run Audit" button
- **Live Processing View** — real-time agent reasoning display with step indicators as each of the 3 agents works (Researching → Analyzing → Generating)
- **Results Dashboard** — compliance score gauge/ring, severity-colored gap cards (Critical red, High orange, Medium yellow), 5 remediation steps, executive summary
- **PDF Report** — download button for the generated PDF report, "Send to Discord" button
- **Audit History Page** — table of past audits with score, document name, date; click any row to view full results; compliance score trend chart over time

**Tech Stack:**

- Next.js 14 (App Router) with TypeScript
- Tailwind CSS for styling + shadcn/ui component library for polished UI primitives
- Recharts or Chart.js for the compliance score gauge and trend chart
- React Query (TanStack Query) for API state management and polling
- Communicates with FastAPI backend via REST endpoints

### 4b. Discord Bot (Owner: Person 1)

*Discord is not just a notification endpoint — it is a full input channel. Users can trigger audits entirely from within Discord.*

**Input Methods:**

- `/audit` slash command — attach a PDF and select document type; bot processes and replies in-thread
- Direct PDF upload — user drops a PDF into a designated channel; bot auto-detects and runs the audit

**Output:**

- Rich embed reply with compliance score, severity-colored gap cards, and executive summary
- Generated PDF report attached to the thread
- Threaded follow-up: user can ask clarifying questions in the thread and the bot responds

**History:**

- `/history` command — returns a list of the user's past audits with scores and dates
- `/audit-detail <id>` — retrieves full results for a specific past audit

**Tech Stack:**

- Python 3.11+
- discord.py (or py-cord) with slash command support
- aiohttp for calling FastAPI endpoints
- Formats JSON responses as Discord rich embeds

### 4c. 3-Agent Dedalus Pipeline (Owners: Split across team)

| Agent | Role | Tools / MCP | Owner |
|-------|------|-------------|-------|
| Agent 1 | Compliance Researcher — looks up live 2026 SEC/FINRA regulations relevant to the document type | Web search MCP, regulation database tool | **Person 1** |
| Agent 2 | PDF Analyzer — extracts text/tables from the uploaded PDF and cross-references against Agent 1's rules to identify gaps | PDF extraction tool, text analysis | **Person 2** |
| Agent 3 | Report Generator — synthesizes findings into a compliance score, gap cards, remediation playbook, and executive summary | PDF generation tool, Discord webhook | **Person 3** |

### 4d. FastAPI Backend + Database (Owner: Person 2)

Person 2 owns the FastAPI server, all API endpoints, pipeline orchestration, and database.

**Backend Tech Stack:**

- Python 3.11+ with FastAPI + uvicorn
- PyMuPDF (fitz) or pdfplumber for PDF text extraction
- Dedalus SDK for agent orchestration
- ReportLab or WeasyPrint for PDF report generation

**Database: Supabase (PostgreSQL)**

We use Supabase as our hosted PostgreSQL database. This gives us a real database with zero ops overhead, a REST API out of the box, and a dashboard to inspect data during the hackathon.

- **Supabase project URL and anon key** must be shared with all team members as environment variables
- The backend connects via `supabase-py` (Python client) or direct `psycopg2`/`asyncpg` connection
- Supabase Storage can optionally be used to store generated PDF reports (alternative: serve from FastAPI's local filesystem)

**Database Tables:**

```sql
-- users table
CREATE TABLE users (
  id TEXT PRIMARY KEY,            -- Discord user ID or web session ID
  source TEXT NOT NULL,           -- 'discord' or 'web'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- audits table
CREATE TABLE audits (
  audit_id TEXT PRIMARY KEY,      -- e.g. 'aud_abc123'
  user_id TEXT REFERENCES users(id),
  document_name TEXT NOT NULL,
  document_type TEXT NOT NULL,    -- 'SOX 404', '10-K', 'Invoice'
  score INTEGER NOT NULL,
  grade TEXT NOT NULL,            -- 'A', 'B', 'C', 'D', 'F'
  executive_summary TEXT,
  report_pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- audit_gaps table
CREATE TABLE audit_gaps (
  id SERIAL PRIMARY KEY,
  audit_id TEXT REFERENCES audits(audit_id) ON DELETE CASCADE,
  severity TEXT NOT NULL,         -- 'critical', 'high', 'medium'
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  regulation TEXT NOT NULL
);

-- audit_remediations table
CREATE TABLE audit_remediations (
  id SERIAL PRIMARY KEY,
  audit_id TEXT REFERENCES audits(audit_id) ON DELETE CASCADE,
  step_number INTEGER NOT NULL,
  description TEXT NOT NULL
);
```

**Environment Variables (all team members need these):**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # backend only
DEDALUS_API_KEY=your-dedalus-key
DISCORD_BOT_TOKEN=your-bot-token                 # Person 1 only
```

---

## 5. Golden Paths

### Path A: Next.js Web Flow

1. User opens the Next.js app and selects a document type
2. User uploads a SOX 404 / 10-K / Invoice PDF via drag-and-drop
3. Clicks "Run Audit" — live processing view shows agent reasoning with step indicators
4. Results dashboard displays compliance score gauge + top 3 gap cards with severity
5. User downloads the PDF report or clicks "Send to Discord"
6. User navigates to Audit History page to review past audits and trend chart

### Path B: Discord Bot Flow

1. User drops a PDF into the audit channel (or runs /audit with attachment)
2. Bot acknowledges with a "Processing..." embed
3. Backend pipeline (same 3 agents) processes the PDF
4. Bot replies in-thread with rich embed: compliance score, gap cards, executive summary
5. Bot attaches the generated PDF report to the thread
6. User can run /history to see all past audits or ask follow-up questions in the thread

---

## 6. Architecture

**The system has two entry points that share a single backend pipeline:**

```
Next.js UI  → FastAPI → Dedalus SDK (3 Agents) → MCP Servers → Supabase + PDF
Discord Bot → FastAPI → Dedalus SDK (3 Agents) → MCP Servers → Supabase + PDF
```

**Key architectural decisions:**

- FastAPI is the shared backend — both Next.js and the Discord bot call the same `/api/run-audit` and `/api/history` endpoints
- The Discord bot downloads the attached PDF, sends it to FastAPI, and formats the JSON response as a rich embed
- Next.js fetches from FastAPI and renders the response as a polished React dashboard
- PDF report generation happens server-side and is returned as a file to both clients
- Supabase (PostgreSQL) stores all audit results; both clients query `/api/history` for past audits
- Next.js uses React Query to poll for processing status during long-running audits

---

## 7. Minimum Demo Output

| Output | Specification |
|--------|---------------|
| Compliance Score | 0–100 numeric score with color indicator |
| Compliance Gaps | Exactly 3 gaps: 1 Critical, 1 High, 1 Medium |
| Remediation Steps | 5 actionable remediation steps |
| Executive Summary | 5-sentence summary for C-suite |
| Downloadable Report | Formatted PDF attached in Discord / downloadable from Next.js |
| Audit History | Past audits viewable in web dashboard and via /history in Discord |

---

## 8. Shared Data Contract

All three team members must agree on this JSON response shape from FastAPI on day one. This allows Person 1 and Person 3 to mock responses and build independently while Person 2 builds the real pipeline.

### Endpoints

#### POST `/api/run-audit`

**Request:** `multipart/form-data`
- `file` — PDF file upload
- `document_type` — string: `"SOX 404"` | `"10-K"` | `"Invoice"`
- `user_id` — string (Discord user ID or web session ID)

**Response:**

```json
{
  "audit_id": "aud_abc123",
  "score": 62,
  "grade": "C",
  "document_name": "sox_404_report.pdf",
  "document_type": "SOX 404",
  "timestamp": "2026-02-07T14:32:00Z",
  "gaps": [
    { "severity": "critical", "title": "...", "description": "...", "regulation": "..." },
    { "severity": "high", "title": "...", "description": "...", "regulation": "..." },
    { "severity": "medium", "title": "...", "description": "...", "regulation": "..." }
  ],
  "remediation": ["Step 1...", "Step 2...", "Step 3...", "Step 4...", "Step 5..."],
  "executive_summary": "Five sentence summary...",
  "report_pdf_url": "/api/files/report_aud_abc123.pdf"
}
```

#### GET `/api/history?user_id={user_id}`

**Response:**

```json
{
  "audits": [
    { "audit_id": "aud_abc123", "document_name": "sox_404.pdf", "document_type": "SOX 404",
      "score": 62, "grade": "C", "timestamp": "2026-02-07T14:32:00Z" },
    { "audit_id": "aud_def456", "document_name": "10k_q3.pdf", "document_type": "10-K",
      "score": 78, "grade": "B", "timestamp": "2026-02-07T13:10:00Z" }
  ]
}
```

#### GET `/api/audit/{audit_id}`

**Response:** Same shape as POST `/api/run-audit` response (full audit detail).

#### GET `/api/files/{filename}`

Returns the generated PDF report file.

#### GET `/api/health`

Returns `{"status": "ok"}`.

---

## 9. Project Structure

This is the full repo layout. Each person works ONLY in their assigned directory.

```
project-root/
├── docs/
│   └── Financial_Compliance_Auditor_PRD_v4.md    # This file
│
├── server/                                        # 👤 PERSON 2 ONLY
│   ├── main.py                                    # FastAPI app entry point
│   ├── requirements.txt                           # Python dependencies
│   ├── README.md                                  # Setup instructions
│   ├── CONTRACT.md                                # API contract (shared reference)
│   ├── .env                                       # Environment variables (gitignored)
│   ├── routes/
│   │   ├── audit.py                               # POST /api/run-audit
│   │   ├── history.py                             # GET /api/history, /api/audit/{id}
│   │   ├── files.py                               # GET /api/files/{filename}
│   │   └── health.py                              # GET /api/health
│   ├── agents/
│   │   ├── compliance_researcher.py               # Agent 1 stub (Person 1 fills in)
│   │   ├── pdf_analyzer.py                        # Agent 2 (Person 2 builds)
│   │   └── report_generator.py                    # Agent 3 stub (Person 3 fills in)
│   ├── services/
│   │   ├── pdf_extractor.py                       # PDF text extraction
│   │   └── pipeline.py                            # 3-agent orchestration
│   ├── db/
│   │   ├── schema.sql                             # Supabase table definitions
│   │   └── database.py                            # Supabase client + CRUD operations
│   └── generated_reports/                         # PDF output directory
│
├── discord-bot/                                   # 👤 PERSON 1 ONLY
│   ├── bot.py                                     # Discord bot entry point
│   ├── commands/
│   │   ├── audit.py                               # /audit slash command
│   │   ├── history.py                             # /history command
│   │   └── audit_detail.py                        # /audit-detail command
│   ├── services/
│   │   ├── api_client.py                          # HTTP client for FastAPI calls
│   │   └── embed_builder.py                       # Rich embed formatting
│   ├── agents/
│   │   └── compliance_researcher.py               # Agent 1 (Person 1 builds)
│   ├── requirements.txt
│   ├── README.md
│   └── .env
│
├── web/                                           # 👤 PERSON 3 ONLY
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .env.local                                 # NEXT_PUBLIC_API_URL etc.
│   ├── app/
│   │   ├── layout.tsx                             # Root layout
│   │   ├── page.tsx                               # Landing / Upload page
│   │   ├── audit/[id]/page.tsx                    # Audit results page
│   │   ├── history/page.tsx                       # Audit history page
│   │   └── processing/page.tsx                    # Live agent reasoning view
│   ├── components/
│   │   ├── upload-zone.tsx                        # Drag-and-drop PDF upload
│   │   ├── score-gauge.tsx                        # Compliance score ring/gauge
│   │   ├── gap-card.tsx                           # Severity-colored gap card
│   │   ├── remediation-list.tsx                   # Remediation steps display
│   │   ├── agent-status.tsx                       # Live agent step indicators
│   │   ├── history-table.tsx                      # Past audits table
│   │   └── trend-chart.tsx                        # Score over time chart
│   ├── lib/
│   │   ├── api.ts                                 # FastAPI client functions
│   │   └── types.ts                               # TypeScript types matching contract
│   ├── agents/
│   │   └── report_generator.py                    # Agent 3 (Person 3 builds)
│   └── public/
│       └── ...
│
├── test-docs/                                     # Shared test PDFs
│   ├── sample_sox_404.pdf                         # Clean SOX 404 doc
│   ├── sample_10k_short.pdf                       # Short 10-K (< 10 pages)
│   └── sample_with_gaps.pdf                       # Doc with deliberate gaps
│
├── .gitignore
└── README.md                                      # Project overview + setup
```

### Ownership Rules

- **Person 1** works ONLY in `discord-bot/` and `server/agents/compliance_researcher.py`
- **Person 2** works ONLY in `server/` (all files except the agent stubs owned by others)
- **Person 3** works ONLY in `web/` and `server/agents/report_generator.py`
- **`docs/`** and **`test-docs/`** are shared — anyone can read, coordinate changes
- **Do not modify files outside your directory** without telling the team first

---

## 10. Tech Stack Summary

| Layer | Technology | Owner |
|-------|-----------|-------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts, React Query | Person 3 |
| Discord Bot | Python, discord.py, aiohttp | Person 1 |
| Backend API | Python, FastAPI, uvicorn | Person 2 |
| AI Pipeline | Dedalus SDK, MCP tool-calling | All (1 agent each) |
| Database | Supabase (hosted PostgreSQL) via supabase-py | Person 2 |
| PDF Extraction | PyMuPDF (fitz) or pdfplumber | Person 2 |
| PDF Generation | ReportLab or WeasyPrint | Person 2 |
| File Storage | Local filesystem (generated_reports/) or Supabase Storage | Person 2 |

---

## 11. Success Criteria

- End-to-end /audit command working in Discord: PDF in → embed + report PDF out
- End-to-end Next.js flow working: upload → dashboard → download report
- Audit history persists across sessions — past audits visible in Next.js history page and via /history in Discord
- Both paths call the same FastAPI backend (no duplicated logic)
- Clean downloadable PDF report from either interface
- Sub-90-second processing time
