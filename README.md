# kipbot

Super User-Friendly Personal AI Assistant

A lightweight, multi-platform AI assistant framework that connects to your favorite chat platforms.

## Features

- **Multi-LLM Support** - OpenAI, Anthropic, Gemini, DeepSeek, and more via LiteLLM
- **Multi-Platform** - Telegram, Discord, KakaoTalk
- **Persistent Memory** - Remembers conversations across sessions
- **Extensible Tools** - Easy-to-add tool system for web search, scheduling, and more
- **CLI Chat** - Interactive terminal chat mode

## Quick Start

```bash
# Install
pip install kipbot

# Initialize config
kipbot init

# Edit ~/.kipbot/config.json with your API keys

# Start chatting in terminal
kipbot chat

# Or run on a platform
kipbot run telegram
kipbot run discord
kipbot run kakao
```

## Configuration

After running `kipbot init`, edit `~/.kipbot/config.json`:

```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "api_key": "your-api-key"
  },
  "telegram": {
    "enabled": true,
    "token": "your-telegram-bot-token"
  },
  "discord": {
    "enabled": true,
    "token": "your-discord-bot-token"
  }
}
```

## Project Structure

```
kipbot/
├── cli/          # CLI commands (typer)
├── core/         # Agent logic & configuration
├── llm/          # LLM provider abstraction (LiteLLM)
├── memory/       # Persistent conversation memory
├── platforms/    # Chat platform integrations
│   ├── telegram.py
│   ├── discord_bot.py
│   └── kakao.py
└── tools/        # Extensible agent tools
```

## Development

```bash
git clone https://github.com/Team-TNT-labs/kipbot.git
cd kipbot
pip install -e ".[dev]"
pytest
```

## License

MIT
