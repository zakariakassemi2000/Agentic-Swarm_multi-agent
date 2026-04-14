"""
Synapse Studio V2 Ultra – Shared State Schema
"""
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time


class AgentMessage(BaseModel):
    agent: str
    emoji: str
    content: str
    timestamp: float = Field(default_factory=time.time)
    iteration: int = 0
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectScore(BaseModel):
    technical_complexity: float = 0.0
    scalability: float = 0.0
    innovation: float = 0.0
    business_value: float = 0.0
    code_quality: float = 0.0
    overall: float = 0.0

    def compute_overall(self) -> float:
        scores = [
            self.technical_complexity,
            self.scalability,
            self.innovation,
            self.business_value,
            self.code_quality,
        ]
        valid = [s for s in scores if s > 0]
        self.overall = round(sum(valid) / len(valid), 2) if valid else 0.0
        return self.overall


class SynapseState(TypedDict):
    """LangGraph graph state – passed between all nodes."""
    session_id: str
    project_name: str
    user_prompt: str
    messages: List[AgentMessage]
    current_iteration: int
    max_iterations: int
    active_agents: List[str]
    generated_code: Dict[str, str]      # filename → code
    scores: List[ProjectScore]
    convergence_reached: bool
    mode: str                           # "brainstorm" | "build" | "debate"
    on_chunk: Any                       # Streaming callback for UI (agent_name, chunk)
    status: str                         # "running" | "paused" | "done" | "error"
    summary: Optional[str]
    error: Optional[str]
