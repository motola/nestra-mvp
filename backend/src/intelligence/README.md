# Intelligence Module

AI-driven device control via Anthropic Claude API. Parse natural language commands and execute them on devices.

## Overview

Enables users to control smart home devices with natural language:

```
User: "Turn on the living room light"
    ↓
Claude API (with tool definitions)
    ↓
Tool execution (call integration adapters)
    ↓
Device turns on
```

## Structure

```
intelligence/
├── README.md (this file)
├── domain.py         # Intelligence-specific models
├── executor.py       # Tool execution engine
├── services.py       # Business logic orchestration
├── tools.py          # Claude tool definitions
└── api/
    └── routes.py     # FastAPI endpoints
```

## How It Works

1. **User sends command:** `POST /intelligence/execute` with text like "turn on living room light"

2. **Create message for Claude:** Package command + current device state + tool definitions

3. **Claude chooses tools:** Claude analyzes command and decides which tools to call

4. **Execute tools:** `executor.execute()` runs the selected tools (calls integration adapters)

5. **Update Claude:** Send tool results back to Claude for validation/refinement

6. **Return result:** Send status to user

## Key Components

### executor.py

Executes tools chosen by Claude:

```python
class ToolExecutor:
    async def execute(self, device_id: UUID, tool_name: str, tool_input: dict) -> dict:
        # 1. Fetch device from repository
        # 2. Call appropriate integration adapter
        # 3. Return result to Claude
```

### tools.py

Defines Claude tool schemas:

```python
TOOLS = [
    {
        "name": "turn_on_device",
        "description": "Turn on a smart home device",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string"},
            },
            "required": ["device_id"],
        },
    },
    # ... more tools
]
```

### services.py

Orchestrates Claude API calls and tool execution:

```python
class IntelligenceService:
    async def execute_command(self, text: str, property_id: UUID) -> str:
        # 1. Fetch devices for property
        # 2. Create Claude prompt with device context
        # 3. Call Claude API with tools
        # 4. Execute returned tools via executor
        # 5. Return final result to user
```

### api/routes.py

HTTP endpoint:

```python
@router.post("/execute")
async def execute_command(
    request: ExecuteRequest,  # {text: "turn on light"}
    user: User = Depends(get_current_user),
) -> ExecuteResponse:
    result = await intelligence_service.execute_command(
        text=request.text,
        property_id=request.property_id,
    )
    return ExecuteResponse(status="success", result=result)
```

## Tool Use Flow

```
1. User: "Turn on living room light"
         ↓
2. Service creates Claude message with:
   - User text
   - List of available devices
   - Tool definitions (turn_on, set_brightness, etc)
         ↓
3. Claude responds with:
   {
     "tool_use": {
       "name": "turn_on_device",
       "input": {"device_id": "abc123"}
     }
   }
         ↓
4. Executor calls turn_on_device(device_id)
   - Fetches device from repository
   - Calls integration adapter: adapter.execute(device, "turn_on", {})
         ↓
5. Send result back to Claude for confirmation
         ↓
6. Claude returns: "Living room light is now on"
```

## Device Context

Before calling Claude, build context about available devices:

```python
devices = await device_repo.list_by_property(property_id)

device_context = [
    {
        "id": d.id,
        "type": d.device_type,
        "vendor": d.vendor,
        "vendor_name": d.vendor_name,
        "online": d.online,
        "raw_state": d.raw_state,  # vendor-specific state
    }
    for d in devices
]

prompt = f"""
You have access to the following devices:
{json.dumps(device_context, indent=2)}

User command: {user_text}

Available tools: turn_on_device, turn_off_device, set_brightness, etc.

Analyze the command and determine which device and tool to use.
"""
```

## Adding New Tools

1. Define tool schema in `tools.py`
2. Add handler method in `ToolExecutor` class
3. Implement tool logic (call integration adapters)
4. Document in this README

Example:

```python
# tools.py
{
    "name": "set_thermostat_temperature",
    "description": "Set target temperature on thermostat",
    "input_schema": {
        "type": "object",
        "properties": {
            "device_id": {"type": "string"},
            "temperature": {"type": "number", "description": "Target temp in Fahrenheit"},
        },
        "required": ["device_id", "temperature"],
    },
}

# executor.py
async def set_thermostat_temperature(self, device_id: UUID, temperature: float) -> dict:
    device = await self.device_repo.get_by_id(device_id)
    adapter = self.adapter_factory.get(device.vendor)
    success = await adapter.execute(device, "set_temperature", {"temp": temperature})
    return {"success": success, "temperature": temperature}
```

## Related

- Backend overview: `backend/src/README.md`
- Property module (devices): `backend/src/property/README.md`
- Integrations (execute commands): `backend/src/integrations/README.md`
- Claude API: https://docs.anthropic.com
