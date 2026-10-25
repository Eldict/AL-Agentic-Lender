# Market and Macro Researcher Agent: market and rate context from a static file.

from __future__ import annotations

import json

from al_ai.agents.base import Agent, Context, eur, write_reasoning
from al_ai.config import resolve
from al_ai.models import AgentOutput, Application


class MarketAgent(Agent):
    name = "Market and Macro Researcher Agent"
    role = "Market researcher"
    goal = "Give the underwriter market and interest-rate context for this property's location."

    def run(self, app: Application, prior: list[AgentOutput], ctx: Context) -> AgentOutput:
        path = resolve(ctx.config["market"]["context_path"])
        county = app.property.county
        inputs_used = {"property.county": county, "property.area": app.property.area,
                       "property.property_type": app.property.property_type,
                       "loan.interest_rate_pct": app.loan.interest_rate_pct, "market_context_file": str(path.name)}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            return AgentOutput(agent=self.name, status="UNAVAILABLE", inputs_used=inputs_used,
                               warnings=[f"Market context file unusable: {exc}"],
                               reasoning="No market context available.")

        as_of = data.get("as_of", "unknown date")
        source = f"Static file {path.name}, dated {as_of}"
        local = data.get("counties", {}).get(county or "")
        nat, rates = data.get("national", {}), data.get("interest_rates", {})
        warnings = [f"Context is from a static file dated {as_of}, not live data"]

        # bullet points built in Python (the LLM only rewords these)
        bullets = []
        if local:
            bullets.append(f"{county}: prices {local['annual_price_change_pct']:+.1f}% a year, "
                           f"median {eur(local['median_price'])}. {local.get('note', '')}".strip())
        else:
            warnings.append(f"No county figures for '{county}': national context only")
        if nat:
            bullets.append(f"National: prices {nat['annual_price_change_pct']:+.1f}% a year. {nat.get('note', '')}".strip())
        if rates:
            bullets.append(f"Rates: ECB deposit rate {rates['ecb_deposit_rate_pct']}%, typical new mortgage "
                           f"{rates['typical_new_mortgage_rate_pct']}%. {rates.get('note', '')}".strip())
            if app.loan.interest_rate_pct is not None:
                gap = app.loan.interest_rate_pct - rates["typical_new_mortgage_rate_pct"]
                where = ("in line with" if abs(gap) < 0.05 else
                         f"{abs(gap):.2f} points {'above' if gap > 0 else 'below'}")
                bullets.append(f"The application's rate ({app.loan.interest_rate_pct}%) is {where} "
                               "the typical new mortgage rate.")
        bullets.append(f"Source: {source}.")

        result = {"bullets": bullets, "county_data": local, "national": nat, "interest_rates": rates,
                  "as_of": as_of, "source": source, "source_note": data.get("source_note")}
        prompt = (
            "Rewrite these facts as 3-5 short bullet points of market context for an underwriter assessing a "
            f"{app.property.property_type or 'property'} in {app.property.area or ''} {county or 'Ireland'}. "
            "Use only these facts. The last bullet must say the context comes from a static file and give its date.\n"
            + "\n".join(f"- {b}" for b in bullets)
        )
        reasoning, model = write_reasoning(ctx, prompt)
        if model == "python-only":
            reasoning = "\n".join(f"• {b}" for b in bullets)
        # static data, so medium confidence (lower with no county figures)
        return AgentOutput(agent=self.name, status="OK" if local else "WARNING", result=result,
                           confidence=0.6 if local else 0.4, inputs_used=inputs_used,
                           warnings=warnings, reasoning=reasoning, model=model)
