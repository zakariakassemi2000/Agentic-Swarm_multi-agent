from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import asyncio
import uuid


@dataclass
class AgentMessage:
    agent_name: str
    round_number: int
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reply_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    model: str = ""
    is_user: bool = False          # True when the message is from the human user
    is_correction: bool = False    # True when the user is correcting a previous agent reply


class MessageQueue:
    """
    Async-safe conversational message queue with user-injection support.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[AgentMessage] = []
        self.round_number = 1
        self.lock = asyncio.Lock()
        self.message_event = asyncio.Event()
        # Queue for user messages injected mid-debate
        self.user_injection_queue: asyncio.Queue = asyncio.Queue()

    async def push_message(self, message: AgentMessage):
        async with self.lock:
            self.messages.append(message)
            self.message_event.set()

    async def get_last(self, n: int = 5) -> List[AgentMessage]:
        """Get the latest N messages for cognitive attention targeting"""
        async with self.lock:
            return self.messages[-n:]

    async def get_all(self) -> List[AgentMessage]:
        async with self.lock:
            return list(self.messages)

    async def inject_user_message(self, content: str, is_correction: bool = False):
        """Inject a message from the human user into the conversation."""
        msg = AgentMessage(
            agent_name="User",
            round_number=self.round_number,
            content=content,
            is_user=True,
            is_correction=is_correction,
        )
        await self.push_message(msg)
        return msg
