# Runs the four agents in order. Each agent sees the earlier agents' outputs.
# No printing here, so a web API can reuse run_committee() later.

from __future__ import annotations

import hashlib
import json
from typing import Callable

from al_ai.agents.affordability import AffordabilityAgent
from al_ai.agents.base import Agent, Context
from al_ai.agents.market import MarketAgent
from al_ai.agents.strategist import StrategistAgent
from al_ai.agents.valuation import ValuationAgent
from al_ai.llm_clients import LLMRouter
from al_ai.models import AgentOutput, Application, CommitteeResult


# borrower said no to AI analysis (SCRUM-35)
class ConsentError(Exception):
    pass


def default_agents() -> list[Agent]:
    return [AffordabilityAgent(), ValuationAgent(), MarketAgent(), StrategistAgent()]


# on_start / on_done let the console show spinners
def run_committee(app: Application, config: dict, llm: LLMRouter,
                  on_start: Callable[[str], None] | None = None,
                  on_done: Callable[[AgentOutput], None] | None = None) -> CommitteeResult:
    if app.ai_consent is False:
        raise ConsentError(f"Application {app.application_id}: borrower has not consented to AI-assisted analysis")

    ctx = Context(config=config, llm=llm)
    outputs: list[AgentOutput] = []
    for agent in default_agents():
        if on_start:
            on_start(agent.name)
        try:
            out = agent.run(app, list(outputs), ctx)
        except Exception as exc:  # one broken agent doesn't stop the others
            out = AgentOutput(agent=agent.name, status="ERROR", warnings=[f"{type(exc).__name__}: {exc}"],
                              reasoning="Agent failed; see warnings.")
        outputs.append(out)
        if on_done:
            on_done(out)

    result = CommitteeResult(application_id=app.application_id, loan_type=app.loan_type,
                             borrower_first_name=app.borrower.first_name,
                             summary=build_summary(app, outputs, config), agents=outputs)
    result.assessment_hash = assessment_hash(result)
    return result


# top-level figures for the underwriter work queue (SCRUM-177)
def build_summary(app: Application, outputs: list[AgentOutput], config: dict) -> dict:
    by = {o.agent: o for o in outputs}
    aff = by["Affordability Agent"].result
    val = by["Valuation Agent"].result
    strat = by["Underwriting Strategist Agent"].result
    breaches = [c["message"] for o in outputs for c in o.result.get("threshold_checks", []) if c["breached"]]
    incomplete = [o.agent for o in outputs if o.status in ("UNAVAILABLE", "ERROR")]
    core = [b for b in breaches if b.split()[0] in {"DTI", "LTI", "LTV"}]
    negative = aff.get("disposable_income_monthly", 0) < 0

    # risk rating: 2+ core breaches = HIGH, any breach = MEDIUM
    if negative or len(core) >= 2:
        risk = "HIGH"
    elif breaches or incomplete:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    consensus = strat.get("consensus", {})
    notes = []
    if app.ai_consent is None:
        notes.append("AI consent flag missing on application")
    if app.status and app.status.lower() == "draft":
        notes.append("Application is still a Draft")
    if app.missing_fields:
        notes.append(f"{len(app.missing_fields)} application field(s) missing or invalid (see missing_fields)")
    return {
        "dti": aff.get("dti"), "lti": aff.get("lti"), "ltv": val.get("ltv"),
        "estimated_value": val.get("estimated_value"),
        "risk_rating": risk, "breaches": breaches, "incomplete_agents": incomplete,
        "recommendation": consensus.get("recommendation"),
        "underwriter_option": consensus.get("underwriter_option"),
        "green_mortgage_eligible": strat.get("green_mortgage", {}).get("eligible"),
        "thresholds_source": config.get("thresholds_source"),
        "notes": notes,
        "missing_fields": app.missing_fields,
    }


# SHA-256 fingerprint for the blockchain (SCRUM-75), name left out
def assessment_hash(result: CommitteeResult) -> str:
    payload = result.model_dump(exclude={"assessment_hash", "borrower_first_name"})
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
