"""Calculator tool for kipbot."""

from kipbot.tools.base import BaseTool, ToolParam, ToolResult


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate a mathematical expression. Supports basic arithmetic, powers, etc."
    parameters = [
        ToolParam(name="expression", type="string", description="Math expression to evaluate (e.g., '2 + 3 * 4')"),
    ]

    ALLOWED_NAMES = {
        "abs": abs, "round": round, "min": min, "max": max,
        "pow": pow, "int": int, "float": float,
    }

    async def execute(self, expression: str = "", **kwargs) -> ToolResult:
        if not expression:
            return ToolResult(success=False, output="No expression provided.")

        try:
            result = eval(expression, {"__builtins__": {}}, self.ALLOWED_NAMES)  # noqa: S307
            return ToolResult(success=True, output=str(result))
        except Exception as e:
            return ToolResult(success=False, output=f"Calculation error: {e}")
