import asyncio
from typing import List
from core.message_queue import MessageQueue, AgentMessage
from agents.specialists import (
    ModeratorAgent, StrategistAgent, ArchitectAgent, EngineerAgent,
    CriticAgent, ProductOwnerAgent, BusinessAgent,
)


class LiveDebateOrchestrator:
    def __init__(self):
        self.moderator = ModeratorAgent()
        self.agents = {
            "Strategist": StrategistAgent(),
            "Architect": ArchitectAgent(),
            "Engineer": EngineerAgent(),
            "Critic": CriticAgent(),
            "ProductOwner": ProductOwnerAgent(),
            "Business": BusinessAgent(),
        }

    async def run_debate(
        self,
        session_id: str,
        initial_prompt: str,
        ws_callback=None,
        stop_event: asyncio.Event = None,
        message_queue: MessageQueue = None,
    ) -> dict:
        """
        Infinite debate loop — runs until stop_event is set by the client.
        Supports user message injection mid-debate.
        """
        if message_queue is None:
            message_queue = MessageQueue(session_id)

        if stop_event is None:
            stop_event = asyncio.Event()

        if ws_callback:
            await ws_callback(
                "system",
                "🚀 Debate started — agents will discuss continuously until you stop them.",
                is_status=True,
            )

        messages_count = 0
        current_speaker = "Strategist"

        while not stop_event.is_set():

            # ── Drain any user messages injected via WebSocket ───────────
            while not message_queue.user_injection_queue.empty():
                try:
                    user_payload = message_queue.user_injection_queue.get_nowait()
                    content = user_payload.get("content", "")
                    is_correction = user_payload.get("is_correction", False)

                    user_msg = await message_queue.inject_user_message(
                        content, is_correction=is_correction,
                    )

                    # Broadcast the user message to the UI
                    if ws_callback:
                        label = "🔧 CORRECTION" if is_correction else "💬 MESSAGE"
                        await ws_callback(
                            "system",
                            f"[User {label}]: {content}",
                            is_status=True,
                        )
                        await ws_callback("User", content)
                except asyncio.QueueEmpty:
                    break

            # ── Agent speaks ─────────────────────────────────────────────
            agent = self.agents.get(current_speaker)

            if agent:
                try:
                    await agent.speak(
                        message_queue=message_queue,
                        initial_prompt=initial_prompt,
                        ws_callback=ws_callback,
                        stop_event=stop_event,
                    )
                except asyncio.CancelledError:
                    break

                messages_count += 1
                message_queue.round_number = messages_count

            if stop_event.is_set():
                break

            # ── Moderator picks next speaker ─────────────────────────────
            if ws_callback:
                await ws_callback(
                    "system",
                    f"[Round {messages_count}] Moderator selecting next speaker...",
                    is_status=True,
                )

            try:
                mod_reply = await self.moderator.speak(
                    message_queue, initial_prompt, ws_callback=None, stop_event=stop_event,
                )
                next_agent_name = mod_reply.content.strip().split("\n")[0]
            except asyncio.CancelledError:
                break

            # Resolve agent name
            current_speaker = None
            for key in self.agents.keys():
                if key.lower() in next_agent_name.lower():
                    current_speaker = key
                    break

            if not current_speaker:
                keys = list(self.agents.keys())
                current_speaker = keys[messages_count % len(keys)]

            await asyncio.sleep(0.3)

        # ── Debate ended ─────────────────────────────────────────────────
        if ws_callback:
            await ws_callback(
                "system",
                f"🛑 Debate stopped after {messages_count} messages.",
                is_status=True,
            )

        return {
            "session_id": session_id,
            "rounds_completed": messages_count,
            "status": "stopped_by_user",
        }
