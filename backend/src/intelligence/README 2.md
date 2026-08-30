# Intelligence Layer

AI-powered insights and actions for the Alphacon platform.

## Features

- **Chat Interface** — Conversational AI for portfolio analysis and recommendations
- **Data Consent** — User controls what data Claude can access
- **Action Logging** — Audit trail of all AI-driven actions
- **Report Generation** — Automated portfolio analysis and recommendations
- **Notifications** — Claude can trigger notifications based on insights

## Setup

### 1. Set Anthropic API Key

Add your Claude API key to Fly.io:

```bash
fly secrets set ANTHROPIC_API_KEY="your-key-here" -a nestra-mvp-api
```

### 2. Database Migration

The migration creates tables for:

- `user_consents` — Track user permissions
- `ai_conversations` — Chat history
- `ai_generated_reports` — Generated reports
- `ai_action_logs` — Audit trail

Run migrations automatically on deploy.

## API Endpoints

| Endpoint                | Method | Purpose                          |
| ----------------------- | ------ | -------------------------------- |
| `/intelligence/consent` | POST   | Set user data access permissions |
| `/intelligence/consent` | GET    | Get current permissions          |
| `/intelligence/chat`    | POST   | Chat with Claude                 |
| `/intelligence/reports` | GET    | Fetch generated reports          |

## Auth

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Next Steps

- Integrate real Claude API calls (currently mock responses)
- Connect portfolio data context
- Implement report generation handlers
- Wire up notification actions
