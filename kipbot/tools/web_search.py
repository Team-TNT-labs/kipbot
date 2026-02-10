"""Web search tool for kipbot."""

import httpx

from kipbot.tools.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information."

    async def execute(self, query: str = "", **kwargs) -> ToolResult:
        # Placeholder - integrate with a search API (e.g., SerpAPI, Tavily)
        return ToolResult(success=False, output="Web search not configured yet.")
