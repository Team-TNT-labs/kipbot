"""CLI commands for kipbot."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from kipbot import __version__

app = typer.Typer(name="kipbot", help="Super User-Friendly Personal AI Assistant")
console = Console()

CONFIG_DIR = Path.home() / ".kipbot"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _create_agent(config):
    """Create an agent with all built-in tools registered."""
    from kipbot.core.agent import Agent
    from kipbot.tools.calculator import CalculatorTool
    from kipbot.tools.datetime_tool import DateTimeTool
    from kipbot.tools.web_search import WebSearchTool

    agent = Agent(config)
    agent.register_tool(DateTimeTool())
    agent.register_tool(CalculatorTool())
    agent.register_tool(WebSearchTool())
    return agent


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


@app.command()
def version():
    """Show kipbot version."""
    console.print(f"kipbot v{__version__}")


@app.command()
def init():
    """Initialize kipbot configuration."""
    if CONFIG_FILE.exists():
        console.print("[yellow]Config already exists at ~/.kipbot/config.json[/yellow]")
        return

    config = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "",
        },
        "telegram": {"enabled": False, "token": ""},
        "discord": {"enabled": False, "token": ""},
        "kakao": {"enabled": False, "api_key": ""},
        "memory": {"enabled": True, "backend": "local"},
        "system_prompt": "You are Kipbot, a helpful personal AI assistant.",
        "language": "ko",
    }
    save_config(config)
    console.print(Panel(
        f"[green]Config created at {CONFIG_FILE}[/green]\n"
        "Edit the config file to add your API keys and enable platforms.",
        title="kipbot initialized",
    ))


@app.command()
def run(platform: str = typer.Argument("telegram", help="Platform to run: telegram, discord, kakao")):
    """Start kipbot on the specified platform."""
    import asyncio
    from kipbot.core.config import Config
    from kipbot.core.agent import Agent

    raw = load_config()
    if not raw:
        console.print("[red]No config found. Run 'kipbot init' first.[/red]")
        raise typer.Exit(1)

    config = Config(**raw)
    agent = _create_agent(config)

    if platform == "telegram":
        from kipbot.platforms.telegram import TelegramPlatform
        bot = TelegramPlatform(agent, config.telegram.token)
        bot.run()
    elif platform == "discord":
        from kipbot.platforms.discord_bot import DiscordPlatform
        bot = DiscordPlatform(agent, config.discord.token)
        bot.run()
    elif platform == "kakao":
        from kipbot.platforms.kakao import KakaoPlatform
        bot = KakaoPlatform(agent, config.kakao.api_key)
        bot.run()
    else:
        console.print(f"[red]Unknown platform: {platform}[/red]")
        raise typer.Exit(1)


@app.command()
def chat():
    """Start an interactive chat session in the terminal."""
    import asyncio
    from kipbot.core.config import Config
    from kipbot.core.agent import Agent, AgentContext

    raw = load_config()
    if not raw:
        console.print("[red]No config found. Run 'kipbot init' first.[/red]")
        raise typer.Exit(1)

    config = Config(**raw)
    agent = _create_agent(config)
    context = AgentContext(user_id="cli_user", platform="cli")

    console.print(Panel("kipbot interactive chat - type 'exit' to quit", title="kipbot"))

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.strip().lower() in ("exit", "quit", "q"):
            break

        response = asyncio.run(agent.chat(context, user_input))
        console.print(f"[bold green]Kipbot:[/bold green] {response}")
