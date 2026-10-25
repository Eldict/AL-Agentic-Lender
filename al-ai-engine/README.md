# AL-AI Engine

The AI part of **Agentic Lender (AL)**, an Irish mortgage / HELOC lending platform (3rd-year group project).

A standalone console app that reads one loan application (a local sample file or Firestore) and runs an
"AI committee" of four agents on it, printing every step.

> **AI recommendation only. Estimates, not a lending decision. Final decision is made by a human underwriter.**

---

## Setup (Windows, PowerShell)

```powershell
cd al-ai-engine
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train_valuation.py          # generates the SYNTHETIC dataset and trains the valuation model
copy .env.example .env             # then fill in whatever keys you have (all optional)
```

Run the tests (the numbers the underwriter relies on):

```powershell
python -m pytest
```

### Optional: LLMs (all free)

Every provider is optional. A missing key, a stopped server or a failed call is skipped and reported in the output.

| Provider | How to set it up | Model (in `config.yaml`) |
|---|---|---|
| **Ollama** (local) | Install from <https://ollama.com>, then `ollama pull llama3`. Ollama runs in the background on `http://localhost:11434`. | `llama3` |
| **Groq** (cloud) | Sign up at <https://console.groq.com>, create a key, put it in `.env` as `GROQ_API_KEY=...` | `openai/gpt-oss-20b` (the free plan has no Llama models) |
| **Google Gemini** (cloud) | Get a key at <https://aistudio.google.com/apikey>, put it in `.env` as `GEMINI_API_KEY=...` | `gemini-3.5-flash-lite` |

Model IDs change over time. They live in `config.yaml`, not in the code (checked October 2026).
Note: Google may use free-tier Gemini prompts to improve its products. The engine only sends figures and
warnings to LLMs, never names or other personal data.

### Optional: Firestore

1. Firebase console > Project settings > Service accounts > **Generate new private key**.
2. Save the JSON **outside the repo** (or name it `*service-account*.json`, which is gitignored).
3. In `.env`: `GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json`
4. **Check the field names** in `al_ai/firestore_adapter.py` (`FIELD_MAP`). They are guesses until checked
   against a real application document.

---

## Demo commands

```powershell
python main.py --sample samples/affordable.json     # BER A2, within limits      -> LOW risk, APPROVE
python main.py --sample samples/borderline.json     # asking price 15% over estimate -> MEDIUM risk, REFER
python main.py --sample samples/breach.json         # DTI and LTI over limits    -> HIGH risk, DECLINE

python main.py --sample samples/breach.json --no-llm     # force numbers-only mode
python main.py --sample samples/affordable.json -v       # also show inputs used + formulas (cross-check)
python main.py --sample samples/affordable.json --json   # full structured result, for the web team

python main.py --list                                     # application IDs, loan type, status
python main.py --firestore <applicationId>
python main.py --firestore <applicationId> --write-back   # shows the exact document, asks y/N first
```

The demo works with **no API keys and no Ollama** (numbers-only mode), with **only Ollama**, or with all three LLMs.

---

## How it works

```
application (sample JSON or Firestore)
        │
        ▼
 1. Affordability Agent ──► 2. Valuation Agent ──► 3. Market and Macro Researcher Agent ──► 4. Underwriting Strategist Agent
    (Python maths)            (scikit-learn model)    (static market file)                   (each LLM votes + Python rules,
                                                                                               Python combines the votes)
        │
        ▼
 summary (DTI, LTV, risk rating, recommendation) + SHA-256 assessment hash
```

**Python does all the numbers. LLMs only explain and vote.** Every figure (repayment, DTI, LTI, LTV,
disposable income, valuation difference) comes from `al_ai/calculations.py`, which is covered by pytest.
LLMs get the finished figures and are told not to recalculate them.

1. **Affordability Agent**: normalises income to yearly (weekly/monthly/yearly, plus other income and any
   co-applicant), sums monthly debts, then calculates the monthly repayment (standard amortisation),
   the repayment at a stressed rate (rate + 2 points), DTI (existing debts + new repayment over gross monthly
   income), LTI, disposable income after tax, debts, repayment and living costs, and a borrowing-capacity
   estimate (the lowest of the LTI cap, stressed-DTI cap and deposit/LTV cap). Each figure is checked against
   its threshold, e.g. `DTI 44% exceeds limit 35%`. Any defaulted assumption (rate, term, first-time-buyer
   status) is listed as a warning.
2. **Valuation Agent**: a `GradientBoostingRegressor` (trained on log price) estimates the property value
   from type, floor area, bedrooms, bathrooms, year built, BER and county. It reports the difference from the
   asking price (€ and %), LTV on the lower of asking price and estimate, and an overvaluation warning above
   the limit. If property details are missing it returns `UNAVAILABLE` and hides the LTV and overvaluation
   figures. **The training data is SYNTHETIC.** To use real data, change `load_dataset()` in
   `al_ai/valuation_model.py` and run `python train_valuation.py --data <file.csv>`.
3. **Market and Macro Researcher Agent**: reads `data/market_context.json` (county price trends and the rate
   environment, with an `as_of` date) and turns it into 3–5 bullet points. It always says the context comes
   from a static file and gives the file's date.
4. **Underwriting Strategist Agent**: a fixed Python rules baseline plus every available LLM vote
   independently (`APPROVE` / `APPROVE_WITH_CONDITIONS` / `REFER` / `DECLINE`, confidence, reasons,
   conditions). LLM replies must be valid JSON. A bad reply is retried once, then recorded as `ERROR`.
   **If all votes agree, that is the recommendation. Any disagreement or tie becomes `REFER` for human
   review.** It never declines an incomplete assessment. It also flags **Green Mortgage** eligibility
   (BER A1–B3 qualifies for the 0.25% APR discount, which the smart contract applies).

Every agent returns the same structure (`al_ai/models.py` → `AgentOutput`), ready for Firestore and the
AL-Web AI Audit Console:

```json
{ "agent": "Affordability Agent", "status": "OK | WARNING | UNAVAILABLE | ERROR",
  "result": {...}, "confidence": 0.0, "inputs_used": {...}, "warnings": ["..."],
  "reasoning": "LLM text, or 'numbers-only mode'", "model": "groq/openai/gpt-oss-20b | python-only",
  "timestamp": "ISO 8601 UTC" }
```

`inputs_used` and `result.formulas` show which raw application values each figure came from, so the
underwriter can cross-check every AI figure. `assessment_hash` is a SHA-256 of the assessment (without the
borrower's name), so the ledger can detect later changes.

### Guard rails
- No final decisions: every output carries the human-underwriter disclaimer.
- Thresholds come from `config.yaml` (prototype defaults; check against current Central Bank of Ireland
  mortgage measures). If a Firestore risk settings document exists, its values override the defaults.
- If the borrower has not consented to AI-assisted analysis (`ai_consent: false`), the engine refuses to run.
- Only figures go to LLMs. No personal data beyond the first name is shown, and none is logged.
- Secrets live in `.env` (gitignored), never in code.

### Project layout

```
main.py                 CLI (argparse)
train_valuation.py      synthetic data + model training
config.yaml             thresholds, assumptions, model IDs
al_ai/calculations.py   pure maths (tested)
al_ai/models.py         Application, AgentOutput, CommitteeResult (Pydantic)
al_ai/agents/           the four agents
al_ai/committee.py      runs the agents in order; no I/O, so an API can reuse it
al_ai/llm_clients.py    Ollama / Groq / Gemini wrappers, JSON validation + retry
al_ai/valuation_model.py  scikit-learn pipeline, load_dataset() swap point
al_ai/firestore_adapter.py  FIELD_MAP and all Firestore access
al_ai/display.py        rich console output
```

---

## Next steps

- **FastAPI endpoint** (next sprint): `POST /assess` would build an `Application` from the request body and
  return `run_committee(app, load_config(), LLMRouter.from_config(cfg)).model_dump()`. `committee.py` does no
  printing or file I/O, so no changes are needed there.
- **Porting to CrewAI**: each agent already has a `role`, a `goal` and a `run()` step, so it maps one to one:
  `role`/`goal` become a CrewAI `Agent`, and `run()` becomes a `Task` whose tool is the existing Python
  function (the calculations stay as tools, not LLM work). The four tasks run in a sequential `Crew`,
  matching `committee.py`. The vote combining in `strategist.combine()` stays in plain Python. This demo keeps
  a plain loop so every step is easy to explain and debug.
- Replace the synthetic housing data with a real dataset (Daft.ie / Property Price Register).
- Replace `market_context.json` with real CSO / Daft.ie figures.
