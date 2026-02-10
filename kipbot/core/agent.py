"""Core agent logic for kipbot."""

from dataclasses import dataclass, field

from loguru import logger

from kipbot.core.config import Config
from kipbot.llm.provider import LLMProvider
from kipbot.memory.store import MemoryStore


@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class AgentContext:
    user_id: str
    platform: str
    history: list[Message] = field(default_factory=list)


class Agent:
    """The core AI agent that processes messages and generates responses."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.llm = LLMProvider(config.llm)
        self.memory = MemoryStore(config.memory)
        self.tools: dict = {}

    async def chat(self, context: AgentContext, user_message: str) -> str:
        """Process a user message and return a response."""
        logger.info(f"[{context.platform}] {context.user_id}: {user_message}")

        context.history.append(Message(role="user", content=user_message))

        messages = self._build_messages(context)
        response = await self.llm.complete(messages)

        context.history.append(Message(role="assistant", content=response))

        if self.config.memory.enabled:
            await self.memory.save(context.user_id, user_message, response)

        return response

    def _build_messages(self, context: AgentContext) -> list[dict]:
        """Build the message list for the LLM."""
        messages = [{"role": "system", "content": self.config.system_prompt}]

        for msg in context.history[-20:]:  # keep last 20 messages
            messages.append({"role": msg.role, "content": msg.content})

        return messages

    def register_tool(self, name: str, func: callable, description: str = "") -> None:
        """Register a tool that the agent can use."""
        self.tools[name] = {"func": func, "description": description}
