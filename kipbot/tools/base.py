"""Base tool interface for kipbot agent tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    success: bool
    output: str


class BaseTool(ABC):
    """Base class for all agent tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool and return a result."""
        ...
