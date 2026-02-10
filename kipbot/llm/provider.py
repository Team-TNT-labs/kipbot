"""LLM provider abstraction using LiteLLM."""

from litellm import acompletion
from loguru import logger

from kipbot.core.config import LLMConfig


class LLMProvider:
    """Multi-provider LLM abstraction powered by LiteLLM."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    async def complete(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> object:
        """Send messages to the LLM and return the raw response."""
        try:
            kwargs = {
                "model": self._get_model_string(),
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "api_key": self.config.api_key or None,
                "api_base": self.config.base_url,
            }
            if tools:
                kwargs["tools"] = tools
            return await acompletion(**kwargs)
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            raise

    def _get_model_string(self) -> str:
        """Build the LiteLLM model string (e.g., 'anthropic/claude-3-opus')."""
        provider = self.config.provider
        model = self.config.model
        if provider == "openai":
            return model
        return f"{provider}/{model}"
