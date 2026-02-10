"""Kakao i Open Builder integration (Skill Server)."""

import asyncio

from loguru import logger

from kipbot.core.agent import Agent, AgentContext


class KakaoPlatform:
    """Kakao i Open Builder skill server using Flask."""

    def __init__(self, agent: Agent, api_key: str = "", port: int = 5000) -> None:
        self.agent = agent
        self.api_key = api_key
        self.port = port
        self.contexts: dict[str, AgentContext] = {}

    def _get_context(self, user_id: str) -> AgentContext:
        if user_id not in self.contexts:
            self.contexts[user_id] = AgentContext(user_id=user_id, platform="kakao")
        return self.contexts[user_id]

    def run(self) -> None:
        """Start the Kakao skill server."""
        try:
            from flask import Flask, request, jsonify
        except ImportError:
            logger.error("Flask is required for Kakao platform. Install with: pip install kipbot[kakao]")
            return

        app = Flask(__name__)

        @app.route("/kakao/chat", methods=["POST"])
        def chat():
            body = request.get_json()
            user_id = body.get("userRequest", {}).get("user", {}).get("id", "unknown")
            utterance = body.get("userRequest", {}).get("utterance", "")

            context = self._get_context(user_id)
            response = asyncio.run(self.agent.chat(context, utterance))

            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [
                        {"simpleText": {"text": response}}
                    ]
                }
            })

        logger.info(f"Kakao skill server starting on port {self.port}...")
        app.run(host="0.0.0.0", port=self.port)
