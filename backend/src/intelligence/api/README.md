# Intelligence API

FastAPI endpoints for natural language device control.

## Routes

### Execute Command

- `POST /intelligence/execute` — Parse and execute natural language command

**Request:**

```json
{
  "text": "Turn on the living room light",
  "property_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**

```json
{
  "status": "success",
  "result": "Living room light is now on",
  "executed_tools": [
    {
      "name": "turn_on_device",
      "device_id": "d94cab91-6e79-48e4-abc4-bd0206512024",
      "success": true
    }
  ]
}
```

**Error Response (400):**

```json
{
  "status": "error",
  "error": "Claude could not understand the command. Please try again.",
  "suggestion": "Try 'turn on the light' instead of 'get the light on'"
}
```

## Flow

1. Validate request (text, property_id)
2. Fetch devices for property from `property.repository`
3. Build Claude prompt with:
   - Available devices
   - Tool definitions
   - User text
4. Call Anthropic Claude API with `tools` parameter
5. Parse Claude response:
   - If tool_use: execute via `ToolExecutor`
   - If text response: return to user
   - Handle errors gracefully
6. Return result + metadata to user

## Schemas

### ExecuteRequest

```python
class ExecuteRequest(BaseModel):
    text: str                      # User command
    property_id: UUID              # Which property
    include_explanation: bool = True  # Return reasoning
```

### ExecuteResponse

```python
class ExecuteResponse(BaseModel):
    status: Literal["success", "error"]
    result: str                    # Human-readable result
    executed_tools: list[ToolExecution] = []
    explanation: str | None = None  # Claude's reasoning
```

## Related

- Intelligence module: `backend/src/intelligence/README.md`
- Executor (tool execution): `backend/src/intelligence/executor.py`
- Services (orchestration): `backend/src/intelligence/services.py`
- Property API (fetch devices): `backend/src/property/api/README.md`
