# Underwriting Strategist Agent: each model votes, Python combines the votes.
# All agree -> that answer. Any disagreement -> REFER for a human.

from __future__ import annotations

import json
from collections import Counter

from al_ai.agents.base import SYSTEM_RULES, Agent, Context
from al_ai.models import AgentOutput, Application
from al_ai.valuation_model import BER_ORDER

RECOMMENDATIONS = ["APPROVE", "APPROVE_WITH_CONDITIONS", "REFER", "DECLINE"]
# matching underwriter options in AL-Web (SCRUM-186)
UNDERWRITER_OPTION = {"APPROVE": "Approve", "APPROVE_WITH_CONDITIONS": "Conditionally Approve",
                      "REFER": "Request Further Information", "DECLINE": "Decline"}
GREEN_BER = set(BER_ORDER[:6])          # A1-B3
GREEN_DISCOUNT_PCT = 0.25


# checks an LLM vote has the right fields and values
def validate_vote(data: dict) -> dict:
    rec = str(data["recommendation"]).strip().upper().replace(" ", "_")
    if rec not in RECOMMENDATIONS:
        raise ValueError(f"recommendation must be one of {RECOMMENDATIONS}, got {rec!r}")
    conf = float(data["confidence"])
    if not 0 <= conf <= 1:
        raise ValueError("confidence must be between 0 and 1")

    def as_list(v):
        return [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])

    return {"recommendation": rec, "confidence": round(conf, 2),
            "key_reasons": as_list(data.get("key_reasons")), "conditions": as_list(data.get("conditions"))}


# fixed Python rules vote, always included (so it works with no LLMs)
def rules_vote(app: Application, prior: list[AgentOutput]) -> dict:
    agents = {o.agent: o for o in prior}
    aff = agents.get("Affordability Agent")
    val = agents.get("Valuation Agent")
    reasons, conditions = [], []

    breaches = []
    for out in (aff, val):
        if out:
            breaches += [c["message"] for c in out.result.get("threshold_checks", []) if c["breached"]]
    core = [b for b in breaches if b.split()[0] in {"DTI", "LTI", "LTV"}]
    unavailable = [o.agent for o in prior if o.status in ("UNAVAILABLE", "ERROR")]
    disposable = aff.result.get("disposable_income_monthly") if aff else None
    over_capacity = bool(aff and aff.result and app.loan.amount
                         and app.loan.amount > aff.result["borrowing_capacity_estimate"])

    if disposable is not None and disposable < 0:
        reasons.append("Disposable income is negative after the new repayment")
    reasons += breaches
    if over_capacity:
        reasons.append("Loan is above the estimated borrowing capacity")
    if unavailable:
        reasons.append(f"Assessment incomplete: {', '.join(unavailable)} unavailable")

    # never DECLINE when data is missing, send it to a human instead
    if ((disposable is not None and disposable < 0) or len(core) >= 2) and not unavailable:
        rec = "DECLINE"
    elif breaches or over_capacity or unavailable:
        rec = "REFER"
    else:
        # small issues become conditions
        if aff:
            for w in aff.warnings:
                if "defaulted" in w or "unknown" in w:
                    conditions.append(f"Confirm: {w}")
                elif "Gifted deposit" in w:
                    conditions.append("Gift letter and evidence of the gift's source")
                elif "extra evidence" in w:
                    conditions.append("Two years' income evidence (accounts / tax returns)")
                elif "under stress" in w:
                    conditions.append("Review budget: disposable income is negative at the stressed rate")
            if app.deposit.gifted_amount and app.deposit.gift_source:
                conditions.append("Gift letter from " + app.deposit.gift_source)
        if (app.loan_type or "").lower() == "heloc":
            conditions.append("Confirm outstanding mortgage balance for combined LTV")
        rec = "APPROVE_WITH_CONDITIONS" if conditions else "APPROVE"
        reasons.append("All figures within configured thresholds")

    confidence = round(min([o.confidence for o in prior if o.status != "UNAVAILABLE"] or [0.5]), 2)
    return {"recommendation": rec, "confidence": confidence, "key_reasons": reasons, "conditions": conditions}


# what the LLMs see: figures and warnings only, no personal data
def facts_for_llm(app: Application, prior: list[AgentOutput]) -> dict:
    facts = {"loan_type": app.loan_type, "loan_amount": app.loan.amount, "term_years": app.loan.term_years,
             "first_time_buyer": app.borrower.first_time_buyer, "dependants": app.borrower.dependants}
    keep = {"Affordability Agent": ["gross_yearly_income", "monthly_repayment", "monthly_repayment_stressed", "dti",
                                    "dti_stressed", "lti", "disposable_income_monthly",
                                    "disposable_income_monthly_stressed", "borrowing_capacity_estimate"],
            "Valuation Agent": ["estimated_value", "asking_price", "valuation_difference_pct", "ltv"],
            "Market and Macro Researcher Agent": ["bullets"]}
    for out in prior:
        facts[out.agent] = {"status": out.status, "warnings": out.warnings,
                            **{k: out.result[k] for k in keep.get(out.agent, []) if k in out.result}}
    return facts


VOTE_PROMPT = """Here are the committee's findings for one application (all figures calculated by Python):

{facts}

Thresholds: {thresholds}

Give your independent recommendation as ONLY a JSON object with exactly these keys:
{{"recommendation": "APPROVE" | "APPROVE_WITH_CONDITIONS" | "REFER" | "DECLINE",
  "confidence": number between 0 and 1,
  "key_reasons": [up to 4 short strings],
  "conditions": [short strings, empty list if none]}}
Use REFER when information is missing or the case needs a human judgement call."""


class StrategistAgent(Agent):
    name = "Underwriting Strategist Agent"
    role = "Underwriting strategist"
    goal = "Combine the other agents' findings into a recommendation for the human underwriter."

    def run(self, app: Application, prior: list[AgentOutput], ctx: Context) -> AgentOutput:
        # collect votes: Python rules first, then each LLM
        votes = [{"model": "python-rules", "status": "OK", **rules_vote(app, prior)}]
        prompt = VOTE_PROMPT.format(facts=json.dumps(facts_for_llm(app, prior), indent=1, default=str),
                                    thresholds=json.dumps(ctx.config["thresholds"]))
        for provider, model in ctx.llm.active:
            vote, reply = ctx.llm.ask_json(provider, model, SYSTEM_RULES, prompt, validate_vote)
            if vote:
                votes.append({"model": reply.label, "status": "OK", **vote})
            else:
                votes.append({"model": reply.label, "status": "ERROR", "error": reply.error,
                              "recommendation": None, "confidence": 0.0, "key_reasons": [], "conditions": []})
        for name, reason in ctx.llm.skipped.items():
            votes.append({"model": name, "status": "SKIPPED", "error": reason,
                          "recommendation": None, "confidence": 0.0, "key_reasons": [], "conditions": []})

        consensus = combine(votes)

        # green mortgage: BER A1-B3 gets 0.25% off (the smart contract applies it)
        ber = (app.property.ber_rating or "").strip().upper()
        green = {"ber_rating": ber or None,
                 "eligible": ber in GREEN_BER if ber else None,
                 "discount_apr_pct": GREEN_DISCOUNT_PCT if ber in GREEN_BER else 0.0,
                 "note": ("Qualifies for the Green Mortgage 0.25% APR discount (applied by the smart contract at "
                          "minting)" if ber in GREEN_BER else
                          "BER unknown: eligibility cannot be checked" if not ber else
                          f"BER {ber} does not qualify (A1-B3 required)")}

        warnings = []
        if consensus["disagreement"]:
            warnings.append("Models disagree: referred for human review")
        llm_votes = [v for v in votes if v["model"] != "python-rules" and v["status"] == "OK"]
        if not llm_votes:
            warnings.append("Numbers-only mode: no LLM votes, consensus is the Python rules baseline")
        warnings += [f"{v['model']} failed: {v['error']}" for v in votes if v["status"] == "ERROR"]

        reasoning = "; ".join(consensus["key_reasons"]) or "No issues found."
        return AgentOutput(
            agent=self.name, status="OK" if llm_votes and not consensus["disagreement"] else "WARNING",
            result={"votes": votes, "consensus": consensus, "green_mortgage": green},
            confidence=consensus["confidence"],
            inputs_used={"agents": [f"{o.agent}: {o.status}" for o in prior], "property.ber_rating": ber or None},
            warnings=warnings, reasoning=reasoning,
            model=", ".join(v["model"] for v in votes if v["status"] == "OK"))


# combines the votes: all agree -> that answer, otherwise REFER
def combine(votes: list[dict]) -> dict:
    valid = [v for v in votes if v["status"] == "OK"]
    counts = Counter(v["recommendation"] for v in valid)
    top, top_n = counts.most_common(1)[0]
    tie = list(counts.values()).count(top_n) > 1
    disagreement = len(counts) > 1
    final = top if not disagreement else "REFER"
    agreeing = [v for v in valid if v["recommendation"] == top]
    confidence = round(sum(v["confidence"] for v in agreeing) / len(agreeing) * top_n / len(valid), 2)
    reasons = list(dict.fromkeys(r for v in valid for r in v["key_reasons"]))[:6]
    conditions = list(dict.fromkeys(c for v in valid for c in v["conditions"]))
    return {
        "recommendation": final,
        "underwriter_option": UNDERWRITER_OPTION[final],
        "confidence": confidence,
        "disagreement": disagreement,
        "majority": None if tie else f"{top} ({top_n} of {len(valid)})",
        "vote_counts": dict(counts),
        "key_reasons": reasons,
        "conditions": conditions,
    }
