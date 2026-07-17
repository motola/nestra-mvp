# Shared API Clients

Centralized API clients for all services (backend integrations, intelligence, etc).

## Clients

### HttpClient

Generic HTTP client for third-party vendor APIs (August, TP-Link, Hikvision, Govee, etc).

**Features:**

- Async/await support
- Automatic retries on timeout/5xx errors
- Basic auth support
- Query parameters, headers, request bodies
- Context manager support

**Usage in integrations:**

```python
# backend/src/integrations/august/adapter.py
from shared.clients import HttpClient

class AugustAdapter:
    def __init__(self, http_client: HttpClient, api_key: str):
        self.http_client = http_client
        self.api_key = api_key

    async def fetch_devices(self, org_id, prop_id, int_id):
        response = await self.http_client.get(
            "https://api.august.com/devices",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        # Normalize to Device schema...
        return devices

    async def execute(self, device, command, params):
        return await self.http_client.post(
            f"https://api.august.com/locks/{device.vendor_specific_id}/lock",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"action": command},
        )
```

### ClaudeClient

Wrapper around Anthropic SDK for Claude API with tool use support.

**Features:**

- Async message creation
- Tool use (structured tool calling)
- Streaming responses
- Model selection
- System prompts

**Usage in intelligence:**

```python
# intelligence/src/services.py
from shared.clients import ClaudeClient

class IntelligenceService:
    def __init__(self, claude_client: ClaudeClient):
        self.claude_client = claude_client

    async def execute_command(self, text: str, property_id: UUID):
        devices = await self.device_repo.list_by_property(property_id)

        response = await self.claude_client.create_message(
            messages=[{"role": "user", "content": text}],
            system="You control smart home devices...",
            tools=DEVICE_TOOLS,
            max_tokens=1024,
        )

        # Parse response, execute tools...
        return result
```

## Configuration

### HttpClient

```python
from shared.clients import HttpClient

# Create client
client = HttpClient(
    timeout=30.0,           # seconds
    max_retries=3,
    base_url="https://api.vendor.com",  # optional
)

# Use in integrations
response = await client.post("/devices", json={...})

# Or as context manager
async with HttpClient() as client:
    response = await client.get("https://api.example.com/devices")
```

### ClaudeClient

```python
from shared.clients import ClaudeClient
import os

api_key = os.getenv("ANTHROPIC_API_KEY")

client = ClaudeClient(
    api_key=api_key,
    model="claude-3-5-sonnet-20241022",
    timeout=30.0,
)

response = await client.create_message(
    messages=[{"role": "user", "content": "Turn on the light"}],
    system="You control smart home devices.",
    tools=[...],
)
```

## Related

- Backend integrations: `backend/src/integrations/README.md`
- Intelligence service: `intelligence/src/README.md`
- Shared utilities: `shared/README.md`
