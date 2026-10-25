# All the maths. LLMs never calculate anything.
# Ratios are floats (0.35 = 35%), rates are percents (4.0 = 4%).

from __future__ import annotations

from dataclasses import dataclass

# payments per year for each income frequency
FREQUENCY_PER_YEAR = {
    "weekly": 52,
    "fortnightly": 26,
    "monthly": 12,
    "quarterly": 4,
    "yearly": 1,
    "annual": 1,
    "annually": 1,
}


# turns weekly/monthly/yearly income into a yearly figure
def normalise_to_yearly(amount: float, frequency: str) -> float:
    key = frequency.strip().lower()
    if key not in FREQUENCY_PER_YEAR:
        raise ValueError(f"Unknown income frequency: {frequency!r}")
    if amount < 0:
        raise ValueError("Income cannot be negative")
    return amount * FREQUENCY_PER_YEAR[key]


# standard mortgage repayment: M = P * r / (1 - (1 + r) ** -n)
def monthly_repayment(principal: float, annual_rate_pct: float, term_years: float) -> float:
    if principal < 0:
        raise ValueError("Loan amount cannot be negative")
    if term_years <= 0:
        raise ValueError("Loan term must be greater than zero")
    n = round(term_years * 12)
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


# reverse of monthly_repayment: biggest loan a monthly payment can cover
def max_principal_for_payment(monthly_payment: float, annual_rate_pct: float, term_years: float) -> float:
    if monthly_payment <= 0:
        return 0.0
    n = round(term_years * 12)
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return monthly_payment * n
    return monthly_payment * (1 - (1 + r) ** -n) / r


# stress test rate, e.g. 4.0% + 2.0 = 6.0%
def stressed_rate(annual_rate_pct: float, buffer_pct_points: float) -> float:
    return annual_rate_pct + buffer_pct_points


# debt-to-income: (existing debts + new repayment) / monthly income
def dti(monthly_debts: float, monthly_mortgage: float, gross_monthly_income: float) -> float:
    if gross_monthly_income <= 0:
        raise ValueError("Gross monthly income must be greater than zero")
    return (monthly_debts + monthly_mortgage) / gross_monthly_income


# loan-to-income: loan / yearly income
def lti(loan_amount: float, gross_yearly_income: float) -> float:
    if gross_yearly_income <= 0:
        raise ValueError("Gross yearly income must be greater than zero")
    return loan_amount / gross_yearly_income


# loan-to-value, using the lower of asking price and estimate
def ltv(loan_amount: float, asking_price: float, estimated_value: float | None = None) -> float:
    values = [v for v in (asking_price, estimated_value) if v is not None]
    if not values or min(values) <= 0:
        raise ValueError("Property value must be greater than zero")
    return loan_amount / min(values)


# how far asking price is above (+) or below (-) the estimate, in € and %
def valuation_difference(asking_price: float, estimated_value: float) -> tuple[float, float]:
    if estimated_value <= 0:
        raise ValueError("Estimated value must be greater than zero")
    diff = asking_price - estimated_value
    return diff, diff / estimated_value


# rough monthly living costs for the household
def living_costs(household_status: str | None, dependants: int, cost_single: float,
                 cost_couple: float, cost_per_dependant: float) -> float:
    couple = (household_status or "").strip().lower() in {"married", "cohabiting", "couple", "civil partnership"}
    base = cost_couple if couple else cost_single
    return base + max(dependants, 0) * cost_per_dependant


# money left each month after tax, debts, repayment and living costs
def disposable_income(gross_monthly_income: float, effective_tax_rate: float, monthly_debts: float,
                      monthly_mortgage: float, monthly_living_costs: float) -> float:
    net = gross_monthly_income * (1 - effective_tax_rate)
    return net - monthly_debts - monthly_mortgage - monthly_living_costs


# biggest loan allowed by each limit; the estimate is the smallest one
def borrowing_capacity(gross_yearly_income: float, monthly_debts: float, deposit: float,
                       max_lti: float, max_dti: float, max_ltv: float,
                       stressed_rate_pct: float, term_years: float) -> dict:
    lti_cap = max_lti * gross_yearly_income
    room = max_dti * gross_yearly_income / 12 - monthly_debts  # monthly payment left under the DTI limit
    dti_cap = max_principal_for_payment(room, stressed_rate_pct, term_years)
    ltv_cap = deposit * max_ltv / (1 - max_ltv) if max_ltv < 1 else float("inf")  # deposit covers the rest
    caps = {"lti_cap": lti_cap, "stressed_dti_cap": dti_cap, "deposit_ltv_cap": ltv_cap}
    limiting = min(caps, key=caps.get)
    return {**caps, "estimate": caps[limiting], "limited_by": limiting}


@dataclass
class ThresholdCheck:
    metric: str
    value: float
    limit: float
    breached: bool
    message: str


# checks a value against its limit, e.g. "DTI 41% exceeds limit 35%"
def check_threshold(metric: str, value: float, limit: float, as_percent: bool = True) -> ThresholdCheck:
    fmt = (lambda x: f"{x * 100:.1f}%".replace(".0%", "%")) if as_percent else (lambda x: f"{x:.2f}x")
    breached = round(value, 6) > round(limit, 6)  # rounding stops 0.35000001 counting as a breach
    word = "exceeds" if breached else "within"
    return ThresholdCheck(metric, value, limit, breached, f"{metric} {fmt(value)} {word} limit {fmt(limit)}")
