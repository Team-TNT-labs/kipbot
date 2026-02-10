"""Core agent logic for kipbot."""

import json
from dataclasses import dataclass, field

from loguru import logger

from kipbot.core.config import Config
from kipbot.llm.provider import LLMProvider
from kipbot.memory.store import MemoryStore
from kipbot.tools.base import BaseTool

MAX_TOOL_ROUNDS = 10


@dataclass
class Message:
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: list | None = None
    tool_call_id: str | None = None
    name: str | None = None


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
        self.tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool the agent can use."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    async def chat(self, context: AgentContext, user_message: str) -> str:
        """Process a user message, run tool calls if needed, return final response."""
        logger.info(f"[{context.platform}] {context.user_id}: {user_message}")

        # Load memory on first message
        if not context.history and self.config.memory.enabled:
            prev = await self.memory.load(context.user_id, limit=10)
            for entry in prev:
                context.history.append(Message(role="user", content=entry["user"]))
                context.history.append(Message(role="assistant", content=entry["assistant"]))

        context.history.append(Message(role="user", content=user_message))

        tools_schema = [t.to_openai_schema() for t in self.tools.values()] or None

        # Agentic loop: keep calling LLM until it produces a text response
        for _ in range(MAX_TOOL_ROUNDS):
            messages = self._build_messages(context)
            response = await self.llm.complete(messages, tools=tools_schema)
            choice = response.choices[0]
            msg = choice.message

            # No tool calls — final text response
            if not msg.tool_calls:
                text = msg.content or ""
                context.history.append(Message(role="assistant", content=text))
                if self.config.memory.enabled:
                    await self.memory.save(context.user_id, user_message, text)
                return text

            # Has tool calls — execute each and feed results back
            context.history.append(Message(
                role="assistant",
                content=msg.content or "",
                tool_calls=[tc.model_dump() for tc in msg.tool_calls],
            ))

            for tc in msg.tool_calls:
                result = await self._execute_tool(tc.function.name, tc.function.arguments)
                context.history.append(Message(
                    role="tool",
                    content=result,
                    tool_call_id=tc.id,
                    name=tc.function.name,
                ))

        # Exhausted rounds, ask LLM for a final answer without tools
        context.history.append(Message(
            role="user",
            content="Please provide your final answer based on the tool results above.",
        ))
        messages = self._build_messages(context)
        response = await self.llm.complete(messages, tools=None)
        text = response.choices[0].message.content or ""
        context.history.append(Message(role="assistant", content=text))
        return text

    async def _execute_tool(self, name: str, arguments: str) -> str:
        """Execute a tool by name and return the result as a string."""
        tool = self.tools.get(name)
        if not tool:
            return f"Error: unknown tool '{name}'"

        try:
            kwargs = json.loads(arguments) if arguments else {}
            result = await tool.execute(**kwargs)
            logger.info(f"Tool {name} -> success={result.success}")
            return result.output
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return f"Error executing {name}: {e}"

    def _build_messages(self, context: AgentContext) -> list[dict]:
        """Build the message list for the LLM API."""
        messages = [{"role": "system", "content": self.config.system_prompt}]

        for msg in context.history[-30:]:
            entry: dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                entry["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            if msg.name:
                entry["name"] = msg.name
            messages.append(entry)

        return messages
