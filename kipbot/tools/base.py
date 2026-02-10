"""Base tool interface for kipbot agent tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolParam:
    name: str
    type: str  # "string", "integer", "number", "boolean"
    description: str
    required: bool = True


@dataclass
class ToolResult:
    success: bool
    output: str


class BaseTool(ABC):
    """Base class for all agent tools."""

    name: str = ""
    description: str = ""
    parameters: list[ToolParam] = []

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool and return a result."""
        ...

    def to_openai_schema(self) -> dict:
        """Convert tool definition to OpenAI function calling schema."""
        properties = {}
        required = []
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
