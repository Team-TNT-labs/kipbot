"""Persistent memory store for kipbot."""

import json
from pathlib import Path

from loguru import logger

from kipbot.core.config import MemoryConfig


class MemoryStore:
    """Simple local file-based memory store."""

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        self.path = Path(config.path)
        if config.enabled:
            self.path.mkdir(parents=True, exist_ok=True)

    async def save(self, user_id: str, user_message: str, assistant_message: str) -> None:
        """Save a conversation turn to memory."""
        if not self.config.enabled:
            return

        user_file = self.path / f"{user_id}.jsonl"
        entry = {
            "user": user_message,
            "assistant": assistant_message,
        }
        try:
            with open(user_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    async def load(self, user_id: str, limit: int = 10) -> list[dict]:
        """Load recent conversation history for a user."""
        if not self.config.enabled:
            return []

        user_file = self.path / f"{user_id}.jsonl"
        if not user_file.exists():
            return []

        try:
            lines = user_file.read_text(encoding="utf-8").strip().split("\n")
            entries = [json.loads(line) for line in lines[-limit:]]
            return entries
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return []
