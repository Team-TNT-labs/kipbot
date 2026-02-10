"""Discord platform integration."""

import discord
from loguru import logger

from kipbot.core.agent import Agent, AgentContext


class DiscordPlatform:
    """Discord bot platform."""

    def __init__(self, agent: Agent, token: str) -> None:
        self.agent = agent
        self.token = token
        self.contexts: dict[str, AgentContext] = {}
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self._setup_events()

    def _get_context(self, user_id: str) -> AgentContext:
        if user_id not in self.contexts:
            self.contexts[user_id] = AgentContext(user_id=user_id, platform="discord")
        return self.contexts[user_id]

    def _setup_events(self) -> None:
        @self.client.event
        async def on_ready():
            logger.info(f"Discord bot connected as {self.client.user}")

        @self.client.event
        async def on_message(message: discord.Message):
            if message.author == self.client.user:
                return

            # Only respond when mentioned or in DMs
            if not (
                self.client.user.mentioned_in(message)
                or isinstance(message.channel, discord.DMChannel)
            ):
                return

            user_id = str(message.author.id)
            text = message.content.replace(f"<@{self.client.user.id}>", "").strip()

            if not text:
                return

            context = self._get_context(user_id)
            response = await self.agent.chat(context, text)

            await message.reply(response)

    def run(self) -> None:
        """Start the Discord bot."""
        logger.info("Discord bot starting...")
        self.client.run(self.token)
