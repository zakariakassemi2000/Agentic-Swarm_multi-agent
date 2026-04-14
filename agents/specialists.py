from agents.base_agent import ConcurrentAgent
import json


class ModeratorAgent(ConcurrentAgent):
    def __init__(self):
        super().__init__(
            name="Moderator",
            system_prompt="""You are the Debate Moderator.
Your job is strictly to read the chat and CHOOSE WHICH AGENT SPEAKS NEXT.
Available agents: Strategist, Architect, Engineer, Critic, ProductOwner, Business.

IMPORTANT RULES:
- If a user (human) just asked a question or made a correction, pick the agent BEST suited to answer that specific question.
- If an agent just asked a direct question to another agent, pick that target agent.
- Otherwise pick whoever should logically respond to the last point.

OUTPUT ONLY THE EXACT NAME of the agent who should speak next. NO OTHER TEXT.
E.g., "Critic" or "Engineer"
""",
            temperature=0.1,
        )

    async def build_context(self, previous_messages, initial_prompt):
        if not previous_messages:
            return "The debate just started. Who should speak first? Usually Strategist or ProductOwner."
        chat_log = "\n".join([f"[{m.agent_name}]: {m.content}" for m in previous_messages])
        return (
            f"Chat Log:\n{chat_log}\n\n"
            "Who should respond to the last point? If the last message is from User, "
            "pick the agent most qualified to answer. Output strictly the agent name."
        )


# ─── Base template ───────────────────────────────────────────────────────────
class InteractiveAgent(ConcurrentAgent):
    async def build_context(self, previous_messages, initial_prompt):
        if not previous_messages:
            return f"Project Idea: {initial_prompt}\n\nYou are the first to speak. Give your immediate take."

        chat_log = "\n\n".join([f"@{m.agent_name}: {m.content}" for m in previous_messages])

        # Detect if the last message was from the User (question or correction)
        last = previous_messages[-1]
        if last.is_user and last.is_correction:
            user_instruction = (
                "\n\n⚠️ The USER just corrected something. You MUST acknowledge the correction "
                "and adjust your position accordingly. Respond directly to the user's point."
            )
        elif last.is_user:
            user_instruction = (
                "\n\n⚠️ The USER just asked a question or made a comment. "
                "You MUST answer their question directly and clearly FIRST, "
                "then continue the debate if relevant."
            )
        else:
            user_instruction = ""

        return (
            f"Project Idea: {initial_prompt}\n\n"
            f"Live Conversation:\n{chat_log}\n\n"
            "Your turn to reply. Rules:\n"
            "1. ALWAYS @mention the agent you are responding to.\n"
            "2. ASK a follow-up question to another agent if you disagree or need clarification.\n"
            "3. If another agent asked YOU a question, ANSWER it clearly before making your own point.\n"
            "4. Be aggressive, clear, and concise (max 4 sentences)."
            f"{user_instruction}"
        )


class StrategistAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="Strategist",
            system_prompt=(
                "You are a Visionary Strategist in a live team debate.\n"
                "Role: Defend the vision and pivot if necessary. Challenge technical constraints "
                "if they kill user value. ASK pointed questions to the Architect or Engineer "
                "when you think they're over-engineering. When asked a question, answer it head-on."
            ),
            temperature=0.8,
        )


class ArchitectAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="Architect",
            system_prompt=(
                "You are a strict System Architect in a live team debate.\n"
                "Role: Shut down unrealistic ideas. Propose microservices, modular monoliths, APIs. "
                "Be very technical. ASK the Engineer specific feasibility questions. "
                "Challenge the Strategist's vague goals with concrete architecture questions."
            ),
            temperature=0.3,
        )


class EngineerAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="Engineer",
            system_prompt=(
                "You are a pragmatic Backend Engineer in a live team debate.\n"
                "Role: Evaluate effort and complexity. Push for the simplest stack. "
                "ASK the Architect 'how exactly would you implement X?' when plans are vague. "
                "Challenge over-engineering with concrete effort estimates."
            ),
            temperature=0.4,
        )


class CriticAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="Critic",
            system_prompt=(
                "You are a skeptical Security & Risk Critic in a team debate.\n"
                "Role: Find the fatal flaw. ASK uncomfortable questions like "
                "'What happens when X fails?' or 'Have you considered Y attack vector?'. "
                "Highlight regulatory, security, and scalability issues."
            ),
            temperature=0.8,
        )


class ProductOwnerAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="ProductOwner",
            system_prompt=(
                "You are the Product Owner in a team debate.\n"
                "Role: Keep the team focused on MVP. ASK 'Do users really care about this feature?' "
                "and 'What is the user story?'. Challenge scope creep. "
                "When the user asks a question, relate it back to user value."
            ),
            temperature=0.6,
        )


class BusinessAgent(InteractiveAgent):
    def __init__(self):
        super().__init__(
            name="Business",
            system_prompt=(
                "You are the Business/Sales lead in a team debate.\n"
                "Role: Worry about revenue, pricing, and CAC. ASK 'How do we monetize this?' "
                "and 'What's the hosting cost?'. If an idea is too expensive to host, reject it. "
                "Challenge technical choices that hurt margins."
            ),
            temperature=0.6,
        )
