# Shared bits for the four agents.
# Each agent has a role, a goal and a run() step (maps 1:1 onto CrewAI later).

from __future__ import annotations

from dataclasses import dataclass

from al_ai.llm_clients import LLMRouter
from al_ai.models import AgentOutput, Application

# instructions every LLM gets
SYSTEM_RULES = (
    "You are part of an AI committee assisting a human mortgage underwriter in Ireland. "
    "You only recommend; a human underwriter makes the final decision. "
    "All figures were calculated by Python and are correct: do not recalculate, change or invent numbers. "
    "Be concise and plain-English. Reply with only the requested text: no introduction such as "
    "'Here is a summary', and no closing remarks."
)


@dataclass
class Context:
    config: dict
    llm: LLMRouter


class Agent:
    name: str = ""
    role: str = ""
    goal: str = ""

    def run(self, app: Application, prior: list[AgentOutput], ctx: Context) -> AgentOutput:
        raise NotImplementedError


# asks the first available LLM for a short summary, returns (text, model)
def write_reasoning(ctx: Context, prompt: str) -> tuple[str, str]:
    if ctx.llm.numbers_only:
        return "numbers-only mode", "python-only"
    reply = ctx.llm.ask_first(SYSTEM_RULES, prompt)
    if reply and reply.text:
        return strip_preamble(reply.text), reply.label
    why = reply.error if reply else "no provider answered"
    return f"numbers-only mode (LLM summary failed: {why})", "python-only"


# removes a "Here is the summary:" first line
def strip_preamble(text: str) -> str:
    lines = text.strip().splitlines()
    if len(lines) > 1 and lines[0].rstrip().endswith(":") and lines[0].lower().startswith(("here", "sure", "below")):
        lines = lines[1:]
    return "\n".join(lines).strip()


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def eur(x: float) -> str:
    return f"{'-' if x < 0 else ''}€{abs(x):,.0f}"
