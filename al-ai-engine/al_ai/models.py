# Data shapes: the application coming in, the agent outputs going out.
# Every application field is optional so missing data never crashes anything.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

DISCLAIMER = ("AI recommendation only. Estimates, not a lending decision. "
              "Final decision is made by a human underwriter.")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- application (input) ---

class Borrower(BaseModel):
    first_name: Optional[str] = None
    household_status: Optional[str] = None     # single, married, cohabiting
    dependants: Optional[int] = None
    first_time_buyer: Optional[bool] = None
    joint_application: bool = False


class Income(BaseModel):
    employment_type: Optional[str] = None      # salaried, self-employed, temporary, variable
    amount: Optional[float] = None
    frequency: Optional[str] = None            # weekly, monthly, yearly
    yearly: Optional[float] = None             # already-normalised figure, if the app stored one
    other_income: float = 0.0
    other_income_frequency: str = "yearly"
    co_applicant_yearly: Optional[float] = None


class Debt(BaseModel):
    type: str = "other"
    monthly_repayment: float = 0.0


class Deposit(BaseModel):
    amount: Optional[float] = None             # total deposit, gift included
    gifted_amount: float = 0.0
    gift_source: Optional[str] = None
    savings: float = 0.0


class LoanRequest(BaseModel):
    amount: Optional[float] = None
    term_years: Optional[float] = None
    interest_rate_pct: Optional[float] = None
    rate_type: Optional[str] = None            # fixed / variable
    repayment_type: Optional[str] = None


class Property(BaseModel):
    property_type: Optional[str] = None        # detached, semi-detached, terraced, apartment
    floor_area_m2: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    ber_rating: Optional[str] = None           # A1 ... G
    county: Optional[str] = None
    area: Optional[str] = None
    asking_price: Optional[float] = None


class Application(BaseModel):
    application_id: str
    loan_type: Optional[str] = None            # mortgage / heloc
    status: Optional[str] = None               # Draft, Submitted
    ai_consent: Optional[bool] = None          # consent to AI analysis (SCRUM-35)
    borrower: Borrower = Field(default_factory=Borrower)
    income: Income = Field(default_factory=Income)
    debts: list[Debt] = Field(default_factory=list)
    no_existing_debts: bool = False
    deposit: Deposit = Field(default_factory=Deposit)
    loan: LoanRequest = Field(default_factory=LoanRequest)
    property: Property = Field(default_factory=Property)
    missing_fields: list[str] = Field(default_factory=list)   # set by the Firestore adapter


# --- agent output ---

Status = Literal["OK", "WARNING", "UNAVAILABLE", "ERROR"]


# same shape for every agent, shown in the AI Audit Console
class AgentOutput(BaseModel):
    agent: str
    status: Status
    result: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    inputs_used: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    reasoning: str = "numbers-only mode"
    model: str = "python-only"
    timestamp: str = Field(default_factory=utc_now)


# the full result of one committee run
class CommitteeResult(BaseModel):
    application_id: str
    loan_type: Optional[str] = None
    borrower_first_name: Optional[str] = None
    summary: dict[str, Any] = Field(default_factory=dict)   # dti, ltv, risk rating
    agents: list[AgentOutput] = Field(default_factory=list)
    assessment_hash: str = ""                               # SHA-256 for the blockchain (SCRUM-75)
    disclaimer: str = DISCLAIMER
    generated_at: str = Field(default_factory=utc_now)
