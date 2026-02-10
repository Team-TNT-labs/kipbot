"""Web search tool for kipbot."""

import httpx

from kipbot.tools.base import BaseTool, ToolParam, ToolResult


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information on any topic."
    parameters = [
        ToolParam(name="query", type="string", description="The search query"),
    ]

    def __init__(self, api_key: str = "", engine: str = "google") -> None:
        self.api_key = api_key
        self.engine = engine

    async def execute(self, query: str = "", **kwargs) -> ToolResult:
        if not self.api_key:
            return ToolResult(success=False, output="Web search API key not configured.")

        # Tavily search API integration
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.api_key, "query": query, "max_results": 5},
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                if not results:
                    return ToolResult(success=True, output="No results found.")
                output = "\n\n".join(
                    f"**{r['title']}**\n{r['url']}\n{r.get('content', '')[:300]}"
                    for r in results
                )
                return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output=f"Search failed: {e}")
