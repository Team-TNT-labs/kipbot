"""Date/time tool for kipbot."""

from datetime import datetime, timezone

from kipbot.tools.base import BaseTool, ToolParam, ToolResult


class DateTimeTool(BaseTool):
    name = "get_datetime"
    description = "Get the current date and time."
    parameters = [
        ToolParam(
            name="timezone",
            type="string",
            description="Timezone name (e.g., 'Asia/Seoul', 'UTC'). Defaults to UTC.",
            required=False,
        ),
    ]

    async def execute(self, timezone_name: str = "Asia/Seoul", **kwargs) -> ToolResult:
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(timezone_name)
        except Exception:
            tz = timezone.utc

        now = datetime.now(tz)
        return ToolResult(
            success=True,
            output=f"{now.strftime('%Y-%m-%d %H:%M:%S %Z')} ({now.strftime('%A')})",
        )
