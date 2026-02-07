# Financial Compliance Auditor - Backend

FastAPI backend for the Financial Compliance Auditor hackathon project.

## Quick Start

```bash
# Navigate to server directory
cd server

# Create virtual environment (Must be Python 3.10+)
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Note: dedalus-labs SDK requires Python 3.10+

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase and Dedalus credentials

# Run the server
uvicorn main:app --reload --port 8000
```

## Environment Variables

Create a `.env` file with:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DEDALUS_API_KEY=your-dedalus-key
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run-audit` | Upload PDF and run compliance audit (3-agent pipeline) |
| GET | `/api/history?user_id={id}` | Get audit history for user |
| GET | `/api/audit/{audit_id}` | Get full audit details |
| GET | `/api/files/{filename}` | Download generated PDF report |
| GET | `/api/health` | Health check |

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
server/
├── main.py              # FastAPI app entry
├── routes/
│   ├── audit.py         # POST /api/run-audit (triggers pipeline)
│   ├── history.py       # GET /api/history, /api/audit/{id}
│   ├── files.py         # GET /api/files/{filename}
│   └── health.py        # GET /api/health
├── agents/
│   ├── pdf_analyzer.py  # Agent 2 (Real): Dedalus analyzer
│   ├── compliance_researcher.py  # Agent 1 (Stub): Regulation lookup
│   └── report_generator.py       # Agent 3 (Stub): Report creation
├── services/
│   ├── pdf_extractor.py # PyMuPDF text extraction
│   └── pipeline.py      # Orchestrator for 3-agent flow
├── db/
│   ├── schema.sql       # Supabase table definitions
│   └── database.py      # Supabase client + CRUD
└── generated_reports/   # PDF output directory
```

See `CONTRACT.md` for the full API specification.
