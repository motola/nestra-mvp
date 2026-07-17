# Intelligence Module Tests

Tests for AI-driven device control via Claude API.

## Purpose

Verify:

- Claude API integration (prompt building, tool execution)
- Tool execution engine correctly invokes device control
- Natural language commands are parsed correctly
- Error handling (invalid commands, devices not found)
- API endpoint request/response contracts

## Test Files

```
tests/
└── README.md (this file)
```

## Running Tests

Run all intelligence tests:

```bash
cd backend && python -m pytest src/intelligence/tests/ -v
```

Run with coverage:

```bash
python -m pytest src/intelligence/tests/ --cov=src/intelligence
```

## Test Strategy

### Mocking Claude API

Mock the Anthropic API to avoid calling real Claude during tests:

```python
@pytest.fixture
def mock_claude_client(mocker):
    mock_client = MagicMock()

    # Mock Claude's response with tool_use
    mock_client.messages.create.return_value = {
        "content": [
            {
                "type": "tool_use",
                "name": "turn_on_device",
                "input": {"device_id": "device-123"},
            }
        ]
    }

    return mock_client

async def test_execute_command_with_tool_use(mock_claude_client):
    service = IntelligenceService(claude_client=mock_claude_client)
    result = await service.execute_command(
        text="turn on the light",
        property_id=PROPERTY_ID,
    )

    assert result.status == "success"
    assert "light is now on" in result.result.lower()
```

### Mocking Integrations

Mock the integration adapters to avoid real device control:

```python
@pytest.fixture
def mock_adapters(mocker):
    mock_august = MagicMock()
    mock_august.execute = AsyncMock(return_value=True)

    return {
        "august": mock_august,
        "bluetooth": mocker.MagicMock(),
    }
```

### Mocking Device Repository

Mock device queries:

```python
@pytest.fixture
def mock_device_repo(mocker):
    mock_repo = MagicMock()
    mock_repo.list_by_property = AsyncMock(return_value=[
        Device(
            id=UUID("device-123"),
            device_type=DeviceType.LOCK,
            vendor="august",
            vendor_name="Front Door Lock",
            online=True,
            # ... other fields
        )
    ])
    return mock_repo
```

## Example Tests

### Test Natural Language Command Parsing

```python
async def test_turn_on_device_command(mock_claude_client, mock_adapters):
    service = IntelligenceService(
        claude_client=mock_claude_client,
        adapters=mock_adapters,
    )

    result = await service.execute_command(
        text="turn on the living room light",
        property_id=PROPERTY_ID,
    )

    # Verify Claude was called with proper prompt
    mock_claude_client.messages.create.assert_called_once()
    call_args = mock_claude_client.messages.create.call_args

    # Verify result
    assert result.status == "success"
    assert result.executed_tools[0].name == "turn_on_device"
```

### Test Tool Execution

```python
async def test_execute_tool_calls_adapter(mock_adapters):
    executor = ToolExecutor(adapters=mock_adapters)

    success = await executor.execute(
        device_id=UUID("device-123"),
        tool_name="turn_on_device",
        tool_input={},
    )

    assert success is True
    mock_adapters["august"].execute.assert_called_once()
```

### Test Error Handling

```python
async def test_execute_invalid_command():
    service = IntelligenceService(claude_client=mock_claude_client)

    # Claude returns no tool_use (can't parse command)
    mock_claude_client.messages.create.return_value = {
        "content": [{"type": "text", "text": "I don't understand that command"}]
    }

    result = await service.execute_command(
        text="xyzabc gibberish",
        property_id=PROPERTY_ID,
    )

    assert result.status == "error"
    assert "understand" in result.error.lower()
```

### Test Device Not Found

```python
async def test_execute_tool_device_not_found():
    executor = ToolExecutor(device_repo=empty_repo)

    with pytest.raises(DeviceNotFoundError):
        await executor.execute(
            device_id=UUID("nonexistent"),
            tool_name="turn_on_device",
            tool_input={},
        )
```

## Coverage Goals

Target test coverage:

- `executor.py` — 90%+ (critical execution path)
- `services.py` — 85%+ (orchestration logic)
- `tools.py` — 100% (tool definitions static)
- `api/routes.py` — 90%+ (HTTP contracts)

## Related

- Intelligence module: `backend/src/intelligence/README.md`
- Executor (tool execution): `backend/src/intelligence/executor.py`
- Services: `backend/src/intelligence/services.py`
- Claude API docs: https://docs.anthropic.com
