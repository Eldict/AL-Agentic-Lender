# Valuation Agent: estimates the property value and checks LTV.

from __future__ import annotations

from al_ai import calculations as calc
from al_ai import valuation_model as vm
from al_ai.agents.base import Agent, Context, eur, pct, write_reasoning
from al_ai.config import resolve
from al_ai.models import AgentOutput, Application


class ValuationAgent(Agent):
    name = "Valuation Agent"
    role = "Property valuer"
    goal = "Estimate the property's value and flag overvaluation and high LTV."

    def __init__(self):
        self._bundle = None

    # loads the trained model once
    def _model(self, ctx: Context) -> dict:
        if self._bundle is None:
            self._bundle = vm.load(resolve(ctx.config["valuation"]["model_path"]))
        return self._bundle

    def run(self, app: Application, prior: list[AgentOutput], ctx: Context) -> AgentOutput:
        t = ctx.config["thresholds"]
        prop = app.property.model_dump()
        inputs_used = {f"property.{k}": v for k, v in prop.items()} | {"loan.amount": app.loan.amount}

        # missing details: no valuation, no LTV (SCRUM-152)
        missing = [f for f in vm.REQUIRED_PROPERTY_FIELDS + ["asking_price"] if prop.get(f) in (None, "")]
        if missing:
            return AgentOutput(agent=self.name, status="UNAVAILABLE", inputs_used=inputs_used,
                               warnings=[f"Missing property details: {', '.join(missing)}"],
                               reasoning="Valuation not run: required property details were not provided. "
                                         "LTV and overvaluation figures are hidden until a valid valuation exists.")
        try:
            vm.ber_score(prop["ber_rating"])
        except ValueError as exc:
            return AgentOutput(agent=self.name, status="UNAVAILABLE", inputs_used=inputs_used,
                               warnings=[str(exc)], reasoning="Valuation not run: invalid BER rating.")
        try:
            bundle = self._model(ctx)
        except FileNotFoundError:
            return AgentOutput(agent=self.name, status="UNAVAILABLE", inputs_used=inputs_used,
                               warnings=["Valuation model not trained. Run: python train_valuation.py"],
                               reasoning="Valuation model file not found.")

        meta = bundle["metadata"]
        warnings: list[str] = []
        if meta.get("synthetic"):
            warnings.append("Model trained on SYNTHETIC data: estimate is for demo purposes only")
        if prop["county"] not in meta.get("counties", [prop["county"]]):
            warnings.append(f"County '{prop['county']}' not in training data: estimate is less reliable")
        if prop["property_type"] not in meta.get("property_types", [prop["property_type"]]):
            warnings.append(f"Property type '{prop['property_type']}' not in training data")

        estimate = vm.predict_value(bundle, prop)
        mape = meta.get("holdout_metrics", {}).get("mape", 0.1)
        asking = prop["asking_price"]
        diff_eur, diff_pct = calc.valuation_difference(asking, estimate)
        over = calc.check_threshold("Overvaluation", diff_pct, t["overvaluation_limit"])
        result = {
            "estimated_value": round(estimate, -3),
            "estimated_range": [round(estimate * (1 - mape), -3), round(estimate * (1 + mape), -3)],
            "asking_price": asking,
            "valuation_difference_eur": round(diff_eur, 0),
            "valuation_difference_pct": round(diff_pct, 4),
            "overvaluation_warning": over.breached,
            "threshold_checks": [over.__dict__],
            "model_info": {k: meta.get(k) for k in ("algorithm", "dataset", "synthetic", "trained_at",
                                                     "holdout_metrics", "sklearn_version")},
            "formulas": {"valuation_difference_pct": f"(asking {eur(asking)} - estimate {eur(estimate)}) / estimate"},
        }
        if over.breached:
            warnings.insert(0, f"Asking price is {pct(diff_pct)} ({eur(diff_eur)}) above the estimate; "
                               f"limit {pct(t['overvaluation_limit'])}")

        if app.loan.amount:
            value_basis = min(asking, estimate)
            ltv = calc.ltv(app.loan.amount, asking, estimate)
            ltv_check = calc.check_threshold("LTV", ltv, t["max_ltv"])
            result.update({"ltv": round(ltv, 4), "ltv_value_basis": round(value_basis, 0)})
            result["threshold_checks"].append(ltv_check.__dict__)
            result["formulas"]["ltv"] = f"loan {eur(app.loan.amount)} / min(asking, estimate) {eur(value_basis)}"
            if ltv_check.breached:
                warnings.insert(0, ltv_check.message)
            if (app.loan_type or "").lower() == "heloc":
                warnings.append("HELOC: LTV uses the requested credit line only; any outstanding mortgage "
                                "balance is not included")
        else:
            warnings.append("No loan amount: LTV not calculated")

        status = "WARNING" if any(c["breached"] for c in result["threshold_checks"]) else "OK"
        prompt = (
            "Write 2-3 plain-English sentences on this property valuation for the underwriter.\n"
            f"{prop['bedrooms']}-bed {prop['property_type']} in {prop.get('area') or ''} {prop['county']}, "
            f"{prop['floor_area_m2']} m2, built {prop['year_built']}, BER {prop['ber_rating']}.\n"
            f"Asking {eur(asking)}; model estimate {eur(result['estimated_value'])} "
            f"(range {eur(result['estimated_range'][0])}-{eur(result['estimated_range'][1])}); "
            f"difference {pct(diff_pct)}; LTV {pct(result['ltv']) if 'ltv' in result else 'n/a'}.\n"
            f"Warnings: {warnings}.\nMention that the model is trained on synthetic data."
        )
        reasoning, model = write_reasoning(ctx, prompt)
        if model == "python-only":
            model = f"python-only + sklearn ({meta.get('algorithm')})"
        else:
            model = f"{model} + sklearn"
        return AgentOutput(agent=self.name, status=status, result=result, confidence=round(1 - mape, 2),
                           inputs_used=inputs_used, warnings=warnings, reasoning=reasoning, model=model)
