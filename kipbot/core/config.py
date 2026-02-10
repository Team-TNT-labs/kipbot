"""Configuration management for kipbot."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

DEFAULT_CONFIG_DIR = Path.home() / ".kipbot"


class LLMConfig(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


class TelegramConfig(BaseSettings):
    enabled: bool = False
    token: str = ""
    allowed_users: list[int] = Field(default_factory=list)


class DiscordConfig(BaseSettings):
    enabled: bool = False
    token: str = ""
    allowed_guilds: list[int] = Field(default_factory=list)


class KakaoConfig(BaseSettings):
    enabled: bool = False
    api_key: str = ""
    bot_id: str = ""


class MemoryConfig(BaseSettings):
    enabled: bool = True
    backend: str = "local"  # "local" or "sqlite"
    path: str = str(DEFAULT_CONFIG_DIR / "memory")


class Config(BaseSettings):
    """Root configuration for kipbot."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    kakao: KakaoConfig = Field(default_factory=KakaoConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    system_prompt: str = "You are Kipbot, a helpful personal AI assistant."
    language: str = "ko"
