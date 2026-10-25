# Affordability Agent: can the borrower afford the repayments?

from __future__ import annotations

from al_ai import calculations as calc
from al_ai.agents.base import Agent, Context, eur, pct, write_reasoning
from al_ai.models import AgentOutput, Application

VARIABLE_INCOME = {"self-employed", "self employed", "temporary", "variable", "contract"}


class AffordabilityAgent(Agent):
    name = "Affordability Agent"
    role = "Affordability analyst"
    goal = "Work out whether the borrower can afford the repayments, including under a stress test."

    def run(self, app: Application, prior: list[AgentOutput], ctx: Context) -> AgentOutput:
        t, a = ctx.config["thresholds"], ctx.config["assumptions"]
        inc, loan, dep, b = app.income, app.loan, app.deposit, app.borrower
        warnings: list[str] = []

        # stop if income or loan amount is missing
        missing = []
        if inc.yearly is None and (inc.amount is None or inc.frequency is None):
            missing.append("income amount/frequency")
        if loan.amount is None:
            missing.append("loan amount")
        if missing:
            return AgentOutput(agent=self.name, status="UNAVAILABLE",
                               warnings=[f"Missing required field(s): {', '.join(missing)}"],
                               inputs_used={"missing": missing},
                               reasoning="Cannot assess affordability without income and loan amount.")

        # total yearly income
        main_yearly = inc.yearly if inc.yearly is not None else calc.normalise_to_yearly(inc.amount, inc.frequency)
        other_yearly = calc.normalise_to_yearly(inc.other_income, inc.other_income_frequency)
        co_yearly = inc.co_applicant_yearly or 0.0
        gross_yearly = main_yearly + other_yearly + co_yearly
        gross_monthly = gross_yearly / 12
        if gross_yearly <= 0:
            return AgentOutput(agent=self.name, status="UNAVAILABLE", warnings=["Gross income is zero"],
                               reasoning="Cannot assess affordability with zero income.")

        # fill in defaults and warn about each one
        defaulted = []
        rate = loan.interest_rate_pct
        if rate is None:
            rate = a["default_interest_rate_pct"]
            defaulted.append(f"interest rate defaulted to {rate}%")
        term = loan.term_years
        if term is None:
            term = a["default_term_years"]
            defaulted.append(f"loan term defaulted to {term} years")
        ftb = b.first_time_buyer
        if ftb is None:
            defaulted.append("first-time-buyer status unknown: using the stricter second-time-buyer LTI limit")
        max_lti = t["max_lti_first_time_buyer"] if ftb else t["max_lti_second_time_buyer"]
        dependants = b.dependants or 0
        warnings += defaulted

        # the numbers
        debts = 0.0 if app.no_existing_debts else sum(d.monthly_repayment for d in app.debts)
        s_rate = calc.stressed_rate(rate, t["stress_buffer_pct_points"])
        repay = calc.monthly_repayment(loan.amount, rate, term)
        repay_stressed = calc.monthly_repayment(loan.amount, s_rate, term)
        dti = calc.dti(debts, repay, gross_monthly)
        dti_stressed = calc.dti(debts, repay_stressed, gross_monthly)
        dti_existing = calc.dti(debts, 0, gross_monthly)
        lti = calc.lti(loan.amount, gross_yearly)
        living = calc.living_costs(b.household_status, dependants, a["living_cost_single"],
                                   a["living_cost_couple"], a["living_cost_per_dependant"])
        disposable = calc.disposable_income(gross_monthly, a["effective_tax_rate"], debts, repay, living)
        disposable_stressed = calc.disposable_income(gross_monthly, a["effective_tax_rate"], debts,
                                                     repay_stressed, living)
        capacity = calc.borrowing_capacity(gross_yearly, debts, dep.amount or 0.0, max_lti, t["max_dti"],
                                           t["max_ltv"], s_rate, term)

        # compare against the limits
        checks = [
            calc.check_threshold("DTI", dti, t["max_dti"]),
            calc.check_threshold("Stressed DTI", dti_stressed, t["max_dti"]),
            calc.check_threshold("LTI", lti, max_lti, as_percent=False),
        ]
        breaches = [c.message for c in checks if c.breached]
        warnings = breaches + warnings
        if disposable < 0:
            warnings.insert(0, f"Disposable income is negative ({eur(disposable)}/month)")
        elif disposable_stressed < 0:
            warnings.append(f"Disposable income turns negative under stress ({eur(disposable_stressed)}/month)")
        if loan.amount > capacity["estimate"]:
            warnings.append(f"Loan {eur(loan.amount)} is above estimated borrowing capacity "
                            f"{eur(capacity['estimate'])} (limited by {capacity['limited_by']})")
        if dep.gifted_amount and not dep.gift_source:
            warnings.append("Gifted deposit declared without a source")
        if (inc.employment_type or "").lower() in VARIABLE_INCOME:
            warnings.append(f"Income type '{inc.employment_type}' may need extra evidence")
        if (app.loan_type or "").lower() == "heloc":
            warnings.append("HELOC: repayment assumes the full credit line is drawn and amortised")

        status = "WARNING" if warnings else "OK"
        # confidence = how complete the inputs were
        confidence = round(max(0.5, 1.0 - 0.1 * len(defaulted)), 2)

        result = {
            "gross_yearly_income": round(gross_yearly, 2),
            "gross_monthly_income": round(gross_monthly, 2),
            "monthly_debts": round(debts, 2),
            "monthly_repayment": round(repay, 2),
            "monthly_repayment_stressed": round(repay_stressed, 2),
            "dti": round(dti, 4),
            "dti_stressed": round(dti_stressed, 4),
            "dti_existing_debts_only": round(dti_existing, 4),
            "lti": round(lti, 3),
            "disposable_income_monthly": round(disposable, 2),
            "disposable_income_monthly_stressed": round(disposable_stressed, 2),
            "borrowing_capacity_estimate": round(capacity["estimate"], 2),
            "borrowing_capacity_limited_by": capacity["limited_by"],
            "borrowing_capacity_caps": {k: round(capacity[k], 2) for k in
                                        ("lti_cap", "stressed_dti_cap", "deposit_ltv_cap")},
            "threshold_checks": [c.__dict__ for c in checks],
            # where each figure came from (SCRUM-191)
            "formulas": {
                "gross_yearly_income": f"main {eur(main_yearly)} + other {eur(other_yearly)} + co-applicant {eur(co_yearly)}",
                "monthly_repayment": f"amortise {eur(loan.amount)} at {rate}% over {term} years",
                "monthly_repayment_stressed": f"amortise {eur(loan.amount)} at {s_rate}% over {term} years",
                "dti": f"(debts {eur(debts)} + repayment {eur(repay)}) / income {eur(gross_monthly)}",
                "lti": f"loan {eur(loan.amount)} / income {eur(gross_yearly)}",
                "disposable_income_monthly": (f"net {eur(gross_monthly * (1 - a['effective_tax_rate']))} - debts "
                                              f"{eur(debts)} - repayment {eur(repay)} - living costs {eur(living)}"),
            },
            # assumptions used (SCRUM-149)
            "assumptions": {
                "interest_rate_pct": rate, "stress_rate_pct": s_rate, "term_years": term,
                "effective_tax_rate": a["effective_tax_rate"], "monthly_living_costs": living,
                "max_dti": t["max_dti"], "max_lti": max_lti, "max_ltv": t["max_ltv"],
                "lti_basis": "first-time buyer" if ftb else "second-time buyer",
                "thresholds_source": ctx.config.get("thresholds_source"),
            },
        }
        inputs_used = {
            "loan_type": app.loan_type,
            "income.amount": inc.amount, "income.frequency": inc.frequency, "income.yearly": inc.yearly,
            "income.other_income": inc.other_income, "income.other_income_frequency": inc.other_income_frequency,
            "income.co_applicant_yearly": inc.co_applicant_yearly, "income.employment_type": inc.employment_type,
            "debts": [d.model_dump() for d in app.debts], "no_existing_debts": app.no_existing_debts,
            "deposit.amount": dep.amount, "deposit.gifted_amount": dep.gifted_amount,
            "loan.amount": loan.amount, "loan.term_years": loan.term_years,
            "loan.interest_rate_pct": loan.interest_rate_pct, "loan.rate_type": loan.rate_type,
            "borrower.household_status": b.household_status, "borrower.dependants": b.dependants,
            "borrower.first_time_buyer": ftb,
        }

        prompt = (
            "Write a 3-4 sentence plain-English affordability summary for the underwriter.\n"
            f"Gross yearly income {eur(gross_yearly)}; loan {eur(loan.amount)} over {term} years at {rate}%.\n"
            f"Monthly repayment {eur(repay)} ({eur(repay_stressed)} at stressed {s_rate}%).\n"
            f"DTI {pct(dti)} (stressed {pct(dti_stressed)}, limit {pct(t['max_dti'])}); "
            f"LTI {lti:.2f}x (limit {max_lti}x).\n"
            f"Disposable income {eur(disposable)}/month; borrowing capacity estimate {eur(capacity['estimate'])}.\n"
            f"Warnings: {warnings or 'none'}.\n"
            "Do not give a final decision."
        )
        reasoning, model = write_reasoning(ctx, prompt)
        return AgentOutput(agent=self.name, status=status, result=result, confidence=confidence,
                           inputs_used=inputs_used, warnings=warnings, reasoning=reasoning, model=model)
