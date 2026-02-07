# Integration Notes for Person 2

## API Dependencies

The Discord bot calls the following endpoints:

### POST `/api/run-audit`
- Expects: `multipart/form-data` with `file`, `document_type`, `user_id`
- Returns: Full audit result JSON (see contract in PRD)
- Timeout: Bot will wait up to 120 seconds

### GET `/api/history?user_id={user_id}`
- Returns: `{"audits": [...]}` — array of audit summaries
- Used by `/history` command

### GET `/api/audit/{audit_id}`
- Returns: Full audit details (same shape as run-audit response)
- Should return 404 with a message body if audit_id doesn't exist
- Used by `/audit-detail` command

### GET `/api/files/{filename}`
- Returns: PDF file binary
- Used to download generated reports and attach them in Discord

## Error Handling Needed

Please ensure your API returns clear error messages:
- **400** for invalid input (we'll show the error body to the user)
- **404** for audit not found (we check for this specifically)
- **500** for internal errors (we'll show a generic "please try again" message)

## Edge Cases

- What happens if audit takes > 2 minutes? The bot will time out and tell the user to check `/history`.
- Should we support PDFs > 50MB? Currently capped at 50MB on the bot side.
- How to handle concurrent audits from same user? The bot doesn't block — a user could start multiple audits.

## Questions

- Is there rate limiting on the API?
- Should Discord user_id be stored as string or int in DB? We send it as string.
- Does the `report_pdf_url` path always start with `/api/files/`? We prepend `FASTAPI_BASE_URL` to it.

## Agent 1 — Compliance Researcher

The compliance researcher agent lives at `server/agents/compliance_researcher.py`.
- Currently returns hardcoded rules for MVP
- Exports `research_compliance_rules(document_type: str) -> ComplianceRulesSchema`
- Ready to be called from your pipeline orchestrator
- TODO: Upgrade to Dedalus SDK with web search MCP when ready
