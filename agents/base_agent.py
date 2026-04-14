from abc import ABC, abstractmethod
import asyncio
from core.message_queue import AgentMessage


class ConcurrentAgent(ABC):
    def __init__(self, name: str, system_prompt: str, temperature: float = 0.7):
        self.name = name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.messages_spoken = 0

    @abstractmethod
    async def build_context(self, previous_messages: list, initial_prompt: str) -> str:
        """Format the conversational context for the agent"""
        pass

    async def speak(
        self,
        message_queue,
        initial_prompt: str,
        ws_callback=None,
        stop_event: asyncio.Event = None,
    ) -> AgentMessage:
        """
        Agent generates a response reacting to the recent thread.
        Aborts cleanly if stop_event is set mid-stream.
        """
        prev_messages = await message_queue.get_last(n=8)
        context = await self.build_context(prev_messages, initial_prompt)
        reply_to_id = prev_messages[-1].id if prev_messages else None

        response_text = ""
        async for chunk in self._stream_response(context):
            # Abort streaming immediately if stop requested
            if stop_event and stop_event.is_set():
                break
            response_text += chunk
            if ws_callback:
                asyncio.create_task(ws_callback(self.name, chunk))

        if not response_text:
            response_text = "[stopped]"

        message = AgentMessage(
            agent_name=self.name,
            round_number=message_queue.round_number,
            content=response_text,
            reply_to=reply_to_id,
            tokens_used=len(response_text.split()),
        )

        await message_queue.push_message(message)
        self.messages_spoken += 1
        return message

    async def _stream_response(self, context: str):
        from core.llm import get_llm_provider
        llm = get_llm_provider()
        async for token in llm.stream_complete(
            system=self.system_prompt,
            user_prompt=context,
            temperature=self.temperature,
            max_tokens=300,
        ):
            yield token
