# Reads applications from Firestore. ALL Firestore field names live in this file.
#
# ASSUMPTIONS (not checked against the real database yet):
# - field names below are camelCase guesses from the Jira stories
# - applications are in the "applications" collection (config.yaml), doc ID = application ID
# - "property.berRating" means {"property": {"berRating": ...}}
# - debts are a list of {type, monthlyRepayment}
# - threshold percents may be stored as 35 or 0.35
# To fix: export one application from the Firebase console and edit FIELD_MAP.

from __future__ import annotations

import json
import os
from typing import Any

from pydantic import ValidationError

from al_ai.models import Application, CommitteeResult

# our field -> Firestore field. EDIT THE RIGHT-HAND SIDE.
FIELD_MAP: dict[str, str] = {
    "loan_type": "loanType",
    "status": "status",
    "ai_consent": "consent.aiAnalysis",
    "borrower.first_name": "personalDetails.firstName",
    "borrower.household_status": "personalDetails.householdStatus",
    "borrower.dependants": "personalDetails.dependants",
    "borrower.first_time_buyer": "personalDetails.firstTimeBuyer",
    "borrower.joint_application": "personalDetails.jointApplication",
    "income.employment_type": "employment.employmentType",
    "income.amount": "employment.incomeAmount",
    "income.frequency": "employment.incomeFrequency",
    "income.yearly": "employment.incomeYearly",
    "income.other_income": "employment.otherIncome",
    "income.other_income_frequency": "employment.otherIncomeFrequency",
    "income.co_applicant_yearly": "coApplicant.incomeYearly",
    "debts": "debts",
    "no_existing_debts": "noExistingDebts",
    "deposit.amount": "deposit.amount",
    "deposit.gifted_amount": "deposit.giftedAmount",
    "deposit.gift_source": "deposit.giftSource",
    "deposit.savings": "deposit.savings",
    "loan.amount": "loanRequest.amount",
    "loan.term_years": "loanRequest.termYears",
    "loan.interest_rate_pct": "loanRequest.interestRate",
    "loan.rate_type": "loanRequest.rateType",
    "loan.repayment_type": "loanRequest.repaymentType",
    "property.property_type": "property.propertyType",
    "property.floor_area_m2": "property.floorArea",
    "property.bedrooms": "property.bedrooms",
    "property.bathrooms": "property.bathrooms",
    "property.year_built": "property.yearBuilt",
    "property.ber_rating": "property.berRating",
    "property.county": "property.county",
    "property.area": "property.area",
    "property.asking_price": "property.askingPrice",
}
FULL_NAME_FALLBACK = "personalDetails.fullName"   # used if there's no first name field
DEBT_FIELDS = {"type": "type", "monthly_repayment": "monthlyRepayment"}  # inside each debt
LIST_FIELDS = {"loan_type": "loanType", "status": "status"}              # shown by --list
# admin risk settings doc -> config.yaml threshold names
THRESHOLD_MAP = {
    "max_lti_first_time_buyer": "maxLtiFirstTimeBuyer",
    "max_lti_second_time_buyer": "maxLtiSecondTimeBuyer",
    "max_ltv": "maxLtv",
    "max_dti": "maxDti",
    "overvaluation_limit": "overvaluationLimit",
    "stress_buffer_pct_points": "stressBuffer",
}
PERCENT_THRESHOLDS = {"max_ltv", "max_dti", "overvaluation_limit"}

_db = None


# setup problem: exits with a message instead of a traceback
class FirestoreError(SystemExit):
    pass


# connects once; firebase reads GOOGLE_APPLICATION_CREDENTIALS itself
def db():
    global _db
    if _db is None:
        path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not path or not os.path.exists(path):
            raise FirestoreError("Firestore not configured: set GOOGLE_APPLICATION_CREDENTIALS in .env to the "
                                 "path of the Firebase service account JSON (see README).")
        import firebase_admin
        from firebase_admin import firestore
        firebase_admin.initialize_app()
        _db = firestore.client()
    return _db


# reads "a.b.c" from nested dicts, None if missing
def get_path(doc: dict, dotted: str) -> Any:
    cur: Any = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _set_path(target: dict, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value


# Firestore doc -> Application; missing or bad fields are listed, never crash
def to_application(app_id: str, doc: dict) -> Application:
    data: dict = {"application_id": app_id}
    missing: list[str] = []
    for internal, remote in FIELD_MAP.items():
        value = get_path(doc, remote)
        if internal == "borrower.first_name" and not value:
            full = get_path(doc, FULL_NAME_FALLBACK)
            value = str(full).split()[0] if full else None
        if internal == "debts" and isinstance(value, list):
            value = [{k: item.get(v) for k, v in DEBT_FIELDS.items() if item.get(v) is not None}
                     for item in value if isinstance(item, dict)]
        if value is None:
            missing.append(f"{internal} (Firestore: {remote})")
        else:
            _set_path(data, internal, value)

    # drop values that can't be converted (e.g. "abc" for a number)
    for _ in range(len(FIELD_MAP)):
        try:
            app = Application(**data)
            break
        except ValidationError as exc:
            for err in exc.errors():
                loc = [str(p) for p in err["loc"] if not isinstance(p, int)]
                node = data
                for part in loc[:-1]:
                    node = node.get(part, {})
                node.pop(loc[-1], None)
                missing.append(f"{'.'.join(loc)} (invalid value)")
    else:
        app = Application(application_id=app_id)
    app.missing_fields = missing
    return app


def get_application(app_id: str) -> Application:
    from al_ai.config import load_config
    coll = load_config()["firestore"]["applications_collection"]
    snap = db().collection(coll).document(app_id).get()
    if not snap.exists:
        raise FirestoreError(f"No application '{app_id}' in collection '{coll}'. Try: python main.py --list")
    return to_application(app_id, snap.to_dict() or {})


# prints ID, loan type and status only (no personal data)
def print_applications() -> None:
    from rich.console import Console
    from rich.table import Table

    from al_ai.config import load_config
    coll = load_config()["firestore"]["applications_collection"]
    table = Table(title=f"Applications in '{coll}'")
    for col in ("Application ID", "Loan type", "Status"):
        table.add_column(col)
    for snap in db().collection(coll).limit(100).stream():
        doc = snap.to_dict() or {}
        table.add_row(snap.id, str(get_path(doc, LIST_FIELDS["loan_type"]) or "—"),
                      str(get_path(doc, LIST_FIELDS["status"]) or "—"))
    Console().print(table)


# reads the admin's risk thresholds (SCRUM-60), if the doc exists
def load_threshold_overrides(cfg: dict) -> dict | None:
    path = cfg["firestore"].get("settings_document")
    if not path:
        return None
    snap = db().document(path).get()
    if not snap.exists:
        return None
    doc = snap.to_dict() or {}
    out = {}
    for key, remote in THRESHOLD_MAP.items():
        value = get_path(doc, remote)
        if isinstance(value, (int, float)):
            out[key] = value / 100 if key in PERCENT_THRESHOLDS and value > 1 else value  # 35 -> 0.35
    return out


# shows exactly what will be saved, asks y/N, then saves it
def write_back(app_id: str, result: CommitteeResult, cfg: dict) -> bool:
    coll = cfg["firestore"]["applications_collection"]
    sub = cfg["firestore"]["assessments_subcollection"]
    doc_id = result.generated_at.replace(":", "-")
    payload = result.model_dump()
    print(f"\nAbout to write to Firestore: {coll}/{app_id}/{sub}/{doc_id}\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if input("\nWrite this to Firestore? [y/N] ").strip().lower() != "y":
        print("Not written.")
        return False
    db().collection(coll).document(app_id).collection(sub).document(doc_id).set(payload)
    print(f"Written: {coll}/{app_id}/{sub}/{doc_id}")
    return True
