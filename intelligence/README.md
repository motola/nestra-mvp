# Intelligence Service

AI-driven device control via Anthropic Claude API. Parse natural language commands and execute them on devices.

## Overview

The Intelligence Service is a standalone microservice that enables natural language control of smart home devices:

```
User: "Turn on the living room light"
    ↓
Intelligence Service (FastAPI)
    ↓
Claude API (with tool definitions)
    ↓
Tool execution (call device adapters)
    ↓
Device turns on
```

## Running the Service

```bash
cd intelligence

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_api_key
export DATABASE_URL=postgresql://user:pass@localhost/nestra

# Run the service
python -m uvicorn src.main:app --reload --port 8001
```

## Architecture

```
intelligence/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   └── routes.py       # FastAPI routes
│   ├── utility/            # Internal utilities
│   ├── tests/
│   │   └── README.md
│   ├── domain.py           # Domain models (Conversation, Message)
│   ├── executor.py         # Tool execution engine
│   ├── models.py           # SQLAlchemy ORM models
│   ├── services.py         # Claude API integration
│   ├── tools.py            # Tool definitions
│   └── main.py             # Service entry point
├── requirements.txt
├── README.md (this file)
└── ...
```

## Key Components

### executor.py — Tool Execution

Executes tools chosen by Claude by calling device adapters:

```python
class DeviceExecutor:
    async def execute_tool(tool_name, tool_input) -> str
```

### services.py — Claude Integration

Wraps the shared Claude client:

```python
class ClaudeIntegration:
    async def stream_response(system_prompt, messages, tools) -> AsyncGenerator[str]
```

### tools.py — Tool Definitions

Claude tool schemas for device control:

- `list_devices` — List devices in a property
- `control_lock` — Lock/unlock devices
- `set_temperature` — Set thermostat
- `toggle_plug` — Turn plug on/off
- `get_device_status` — Get device state

### api/routes.py — HTTP Endpoints

```
POST /intelligence/conversations
GET /intelligence/conversations/{id}
POST /intelligence/conversations/{id}/messages
```

## Shared Clients

Intelligence uses shared API clients from `nestra-mvp/shared/clients/`:

- **ClaudeClient** — Wrapper around Anthropic SDK (async messages, streaming, tool use)
- **HttpClient** — Generic HTTP client for vendor APIs (used by device adapters)

Example usage:

```python
from shared.clients import ClaudeClient

client = ClaudeClient(api_key=api_key)
response = await client.create_message(
    messages=[{"role": "user", "content": "turn on light"}],
    system="You control smart home devices",
    tools=DEVICE_TOOLS,
)
```

## Database

Connects to PostgreSQL (same DB as backend). Models:

- `conversations` — Conversation history
- `conversation_messages` — Individual messages
- Device tables (shared with backend)

Migration: Uses Alembic from backend directory.

## Configuration

Environment variables:

```bash
ANTHROPIC_API_KEY          # Claude API key
DATABASE_URL               # PostgreSQL connection string
DEBUG                      # Enable debug logging
```

## Communication with Backend

Intelligence service makes HTTP calls to backend property/device APIs:

```python
# Fetch devices from backend
devices = await http_client.get(
    "http://backend:8000/property/devices",
    params={"property_id": property_id},
)
```

Or backend calls intelligence endpoints:

```
POST http://intelligence:8001/intelligence/conversations/{id}/messages
```

## Tool Use Flow

1. User sends natural language command
2. Intelligence calls Claude with device context + tool definitions
3. Claude chooses appropriate tool(s) and sends `tool_use` block
4. `DeviceExecutor` executes the tool (calls device adapter)
5. Result sent back to Claude for confirmation
6. Final response returned to user

Example Claude response:

```json
{
  "content": [
    {
      "type": "tool_use",
      "name": "turn_on_device",
      "input": { "device_id": "abc123" }
    }
  ]
}
```

## Adding New Tools

1. Define tool schema in `tools.py`
2. Add handler method in `DeviceExecutor`
3. Test with Claude

Example:

```python
# tools.py
{
    "name": "set_brightness",
    "description": "Set brightness on a light",
    "input_schema": {...},
}

# executor.py
async def execute_tool(self, tool_name, tool_input):
    if tool_name == "set_brightness":
        return await self._set_brightness(tool_input)

async def _set_brightness(self, tool_input):
    device_id = tool_input.get("device_id")
    brightness = tool_input.get("brightness")
    device = await self._repository.get_by_id(device_id)
    adapter = self._registry.resolve(device.vendor)
    success = await adapter.execute(device, "set_brightness", {"brightness": brightness})
    return f"✓ Brightness set to {brightness}%" if success else "✗ Failed"
```

## Testing

Run tests:

```bash
cd intelligence && python -m pytest src/tests/
```

**Related:** `src/tests/README.md`

## Related Documentation

- Backend: `../backend/README.md`
- Shared clients: `../shared/clients/README.md`
- Backend property/integrations: `../backend/src/property/README.md`, `../backend/src/integrations/README.md`
