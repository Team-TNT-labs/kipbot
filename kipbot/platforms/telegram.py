"""Telegram platform integration."""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from loguru import logger

from kipbot.core.agent import Agent, AgentContext


class TelegramPlatform:
    """Telegram bot platform."""

    def __init__(self, agent: Agent, token: str) -> None:
        self.agent = agent
        self.token = token
        self.contexts: dict[str, AgentContext] = {}

    def _get_context(self, user_id: str) -> AgentContext:
        if user_id not in self.contexts:
            self.contexts[user_id] = AgentContext(user_id=user_id, platform="telegram")
        return self.contexts[user_id]

    async def _handle_start(self, update: Update, context) -> None:
        await update.message.reply_text("Hello! I'm Kipbot, your personal AI assistant.")

    async def _handle_message(self, update: Update, context) -> None:
        user_id = str(update.effective_user.id)
        text = update.message.text

        agent_context = self._get_context(user_id)
        response = await self.agent.chat(agent_context, text)

        await update.message.reply_text(response)
        logger.info(f"[telegram] replied to {user_id}")

    def run(self) -> None:
        """Start the Telegram bot."""
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self._handle_start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

        logger.info("Telegram bot starting...")
        app.run_polling()
