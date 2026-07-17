"""Claude API client wrapper for intelligence service."""

from __future__ import annotations

from typing import Any

from anthropic import Anthropic, AsyncAnthropic


class ClaudeClient:
    """Wrapper around Anthropic SDK for Claude API access.

    Handles:
    - Authentication via API key
    - Message creation with tool use
    - Streaming responses
    - Model selection and configuration
    - Error handling and retries
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        timeout: float = 30.0,
    ):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key
            model: Claude model ID (default: claude-3-5-sonnet)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._async_client = AsyncAnthropic(
            api_key=api_key,
            timeout=timeout,
        )
        self._sync_client = Anthropic(
            api_key=api_key,
            timeout=timeout,
        )

    async def create_message(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a message with Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            tools: Optional list of tool definitions
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional Anthropic API parameters

        Returns:
            Message response dict with content, stop_reason, usage, etc.
        """
        return await self._async_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
            temperature=temperature,
            **kwargs,
        )

    async def stream_message(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Stream a message from Claude.

        Args:
            messages: List of message dicts
            system: Optional system prompt
            tools: Optional tool definitions
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Streaming content events from Claude
        """
        async with self._async_client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
            temperature=temperature,
            **kwargs,
        ) as stream:
            async for event in stream:
                yield event

    async def close(self) -> None:
        """Close async client."""
        await self._async_client.close()

    async def __aenter__(self) -> ClaudeClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
