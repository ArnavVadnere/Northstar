# Northstar

AI-powered financial compliance auditor. Upload SEC filings, SOX 404 reports, or invoices and get a full compliance audit in under two minutes — from a web dashboard or Discord.

## How It Works

Northstar runs a 4-stage AI agent pipeline powered by the Dedalus SDK and OpenAI GPT-4o:

1. **Document Gatekeeper** — Validates the upload is a real financial document before running the full pipeline.
2. **Compliance Researcher** — Searches the live web via Brave Search MCP for current SEC, PCAOB, FINRA, and GAAP regulations specific to the document type.
3. **PDF Analyzer** — Uses 6 custom MCP tools (built with PyMuPDF) to structurally analyze the document — finding regulatory sections, extracting financial statements, validating math, checking signatures, and detecting red flags — then identifies compliance gaps against the researched rules.
4. **Report Generator** — Scores the findings, generates an executive summary and remediation plan, and produces a downloadable PDF report.

## Architecture

```
┌─────────────┐     ┌─────────────┐
│   Next.js   │     │  Discord.py │
│   Web App   │     │     Bot     │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └───────┬───────────┘
               │
        ┌──────▼──────┐
        │   FastAPI   │
        │   Backend   │
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 Agent 1    Agent 2    Agent 3
Researcher  Analyzer   Reporter
 (Brave MCP) (PDF MCP)  (ReportLab)
               │
          ┌────▼────┐
          │ Supabase│
          └─────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python, Pydantic |
| AI/LLM | Dedalus SDK (dedalus-labs, dedalus-mcp), OpenAI GPT-4o |
| MCP Servers | Brave Search MCP, Custom PDF Compliance Analyzer (PyMuPDF) |
| Database | Supabase (PostgreSQL) |
| PDF Generation | ReportLab |
| Discord | discord.py 2.0, aiohttp |

## Supported Document Types

- **SOX 404** — Sarbanes-Oxley internal controls reports
- **10-K** — SEC annual reports
- **8-K** — SEC current reports
- **Invoice** — Financial invoices

## Project Structure

```
Northstar/
├── server/                  # FastAPI backend + agent pipeline
│   ├── agents/              # 4 AI agents (classifier, researcher, analyzer, reporter)
│   ├── services/            # Pipeline orchestrator, PDF extraction
│   ├── routes/              # API endpoints (audit, history, files, health)
│   └── db/                  # Supabase schema + CRUD
├── web/                     # Next.js frontend
│   └── src/app/             # Pages: upload, results, history
├── discord-bot/             # Discord.py bot
│   ├── commands/            # /audit, /history, /audit-detail
│   └── services/            # API client, embed builder
└── mcp-servers/             # Custom MCP server
    └── pdf-compliance-analyzer/  # 6 PDF analysis tools
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Dedalus API key
- Discord bot token (for Discord integration)
- Supabase project (optional — falls back to mock data)

### Backend

```bash
cd server
pip install -r requirements.txt
cp .env.example .env  # Add DEDALUS_API_KEY, Supabase credentials
uvicorn main:app --reload --port 8000
```

### Web Frontend

```bash
cd web
npm install
cp .env.example .env.local  # Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Discord Bot

```bash
cd discord-bot
pip install -r requirements.txt
cp .env.example .env  # Add DISCORD_BOT_TOKEN, FASTAPI_BASE_URL
python bot.py
```

### MCP Server

```bash
cd mcp-servers/pdf-compliance-analyzer
pip install -r requirements.txt
python server.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run-audit` | Upload PDF and run compliance audit |
| GET | `/api/audit/{audit_id}` | Get audit result by ID |
| GET | `/api/history?user_id=` | Get audit history for a user |
| GET | `/api/files/{filename}` | Download generated PDF report |
| GET | `/api/health` | Health check |

## Output

Each audit produces:
- **Compliance Score** (0-100) with letter grade (A-F)
- **Executive Summary** written for C-suite
- **Compliance Gaps** with severity (critical/high/medium), description, and regulation reference
- **Remediation Steps** — 5 prioritized, actionable steps
- **PDF Report** — downloadable professional compliance report
