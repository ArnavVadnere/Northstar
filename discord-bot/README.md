# Northstar Discord Bot

Discord bot for financial compliance auditing. Users upload PDF documents and receive compliance scores, gap analysis, and remediation steps — all within Discord.

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env .env.backup   # optional
# Edit .env with your DISCORD_BOT_TOKEN
```

You need a bot token from the [Discord Developer Portal](https://discord.com/developers/applications):
- Create a new application
- Go to Bot settings and copy the token
- Enable the **Message Content** intent under Privileged Gateway Intents

3. **Invite the bot to your server:**

Use the OAuth2 URL Generator in the Developer Portal with these scopes:
- `bot`
- `applications.commands`

And these bot permissions:
- Send Messages
- Embed Links
- Attach Files
- Use Slash Commands

4. **Run the bot:**

```bash
python bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/audit` | Run compliance audit on a PDF. Parameters: `document_type` (SOX 404 / 10-K / Invoice), `file` (PDF attachment) |
| `/history` | View your past audit history |
| `/audit-detail <audit_id>` | View detailed results for a specific audit |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Bot token from Developer Portal | (required) |
| `FASTAPI_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Architecture

The bot is a thin client that calls the shared FastAPI backend:

```
Discord User → /audit command → Bot → FastAPI /api/run-audit → Results embed
```

The backend runs the 3-agent Dedalus pipeline and returns JSON, which the bot formats as Discord rich embeds.

## Development

See [TESTING.md](TESTING.md) for testing instructions.
See [INTEGRATION_NOTES.md](INTEGRATION_NOTES.md) for backend integration details.
