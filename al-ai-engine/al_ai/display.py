# Console output for the demo (rich library).

from __future__ import annotations

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from al_ai.llm_clients import LLMRouter
from al_ai.models import DISCLAIMER, AgentOutput, Application, CommitteeResult

console = Console()

STATUS_STYLE = {"OK": "green", "WARNING": "yellow", "UNAVAILABLE": "magenta", "ERROR": "red"}
VOTE_STYLE = {"APPROVE": "green", "APPROVE_WITH_CONDITIONS": "cyan", "REFER": "yellow", "DECLINE": "red"}


def eur(x) -> str:
    return "—" if x is None else f"{'-' if x < 0 else ''}€{abs(x):,.0f}"


def pct(x) -> str:
    return "—" if x is None else f"{x * 100:.1f}%"


def _short(msg: str | None, limit: int = 90) -> str:
    msg = msg or ""
    return msg if len(msg) <= limit else msg[:limit] + "…"


def header(app: Application, llm: LLMRouter) -> None:
    t = Table.grid(padding=(0, 2))
    t.add_row("[bold]Application[/]", app.application_id, "[bold]Loan type[/]", (app.loan_type or "unknown").upper())
    t.add_row("[bold]Borrower[/]", app.borrower.first_name or "—", "[bold]Status[/]", app.status or "—")
    models = ", ".join(f"{p}/{m}" for p, m in llm.active) or "[yellow]none: numbers-only mode[/]"
    t.add_row("[bold]LLMs[/]", models, "", "")
    skipped = Text("\n".join(f"  {name} skipped: {why}" for name, why in llm.skipped.items()), style="dim")
    console.print(Panel(Group(t, skipped), title="[bold]AL-AI Engine · AI Committee[/]",
                        border_style="blue", box=box.DOUBLE))


def _limit_style(check: dict | None) -> str:
    if not check:
        return ""
    if check["breached"]:
        return "bold red"
    return "yellow" if check["value"] >= 0.9 * check["limit"] else "green"


def _checks(out: AgentOutput) -> dict:
    return {c["metric"]: c for c in out.result.get("threshold_checks", [])}


def _metrics_table() -> Table:
    t = Table(box=box.SIMPLE_HEAVY, show_edge=False, pad_edge=False)
    t.add_column("Metric")
    t.add_column("Value", justify="right")
    t.add_column("Limit", justify="right")
    return t


def affordability_body(out: AgentOutput):
    r, c = out.result, _checks(out)
    t = _metrics_table()

    def row(label, value, check_name=None, limit_fmt=pct):
        check = c.get(check_name)
        style = _limit_style(check)
        t.add_row(label, Text(value, style=style), limit_fmt(check["limit"]) if check else "")

    row("Gross yearly income", eur(r["gross_yearly_income"]))
    row("Existing monthly debts", eur(r["monthly_debts"]))
    row("Monthly repayment", eur(r["monthly_repayment"]))
    row(f"Repayment at stress rate ({r['assumptions']['stress_rate_pct']}%)", eur(r["monthly_repayment_stressed"]))
    row("DTI", pct(r["dti"]), "DTI")
    row("DTI (stressed)", pct(r["dti_stressed"]), "Stressed DTI")
    row("LTI", f"{r['lti']:.2f}x", "LTI", lambda x: f"{x:.2f}x")
    disp_style = "bold red" if r["disposable_income_monthly"] < 0 else (
        "yellow" if r["disposable_income_monthly_stressed"] < 0 else "")
    t.add_row("Disposable income / month", Text(eur(r["disposable_income_monthly"]), style=disp_style), "")
    t.add_row("Disposable income / month (stressed)", eur(r["disposable_income_monthly_stressed"]), "")
    t.add_row("Borrowing capacity estimate", eur(r["borrowing_capacity_estimate"]),
              Text(r["borrowing_capacity_limited_by"].replace("_", " "), style="dim"))
    return t


def valuation_body(out: AgentOutput):
    r, c = out.result, _checks(out)
    t = _metrics_table()
    lo, hi = r["estimated_range"]
    t.add_row("Estimated value (ML)", eur(r["estimated_value"]), Text(f"range {eur(lo)}–{eur(hi)}", style="dim"))
    t.add_row("Asking price", eur(r["asking_price"]), "")
    over = c.get("Overvaluation")
    t.add_row("Asking vs estimate", Text(f"{eur(r['valuation_difference_eur'])} ({pct(r['valuation_difference_pct'])})",
                                         style=_limit_style(over)), pct(over["limit"]))
    if "ltv" in r:
        t.add_row("LTV", Text(pct(r["ltv"]), style=_limit_style(c.get("LTV"))), pct(c["LTV"]["limit"]))
    return t


def market_body(out: AgentOutput):
    return Text(out.reasoning)


def strategist_body(out: AgentOutput):
    r = out.result
    votes = Table(box=box.SIMPLE_HEAVY, show_edge=False, pad_edge=False)
    votes.add_column("Model")
    votes.add_column("Vote")
    votes.add_column("Conf.", justify="right")
    votes.add_column("Key reasons / error", overflow="fold")
    for v in r["votes"]:
        if v["status"] == "OK":
            rec = v["recommendation"]
            votes.add_row(v["model"], Text(rec, style=VOTE_STYLE[rec]), f"{v['confidence']:.2f}",
                          "; ".join(v["key_reasons"][:3]))
        else:
            votes.add_row(Text(v["model"], style="dim"), Text(v["status"], style="dim"), "—",
                          Text(_short(v.get("error")), style="dim"))

    cons = r["consensus"]
    rec = cons["recommendation"]
    lines = Text()
    lines.append("Consensus: ", style="bold")
    lines.append(f"{rec}", style=f"bold {VOTE_STYLE[rec]}")
    lines.append(f"  (underwriter option: {cons['underwriter_option']}, confidence {cons['confidence']:.2f})\n")
    if cons["disagreement"]:
        lines.append(f"⚠ Models disagree {cons['vote_counts']}: referred for human review\n", style="bold yellow")
    if cons["conditions"]:
        lines.append("Suggested conditions: ", style="bold")
        lines.append("; ".join(cons["conditions"]) + "\n")
    g = r["green_mortgage"]
    lines.append("Green Mortgage: ", style="bold")
    lines.append(g["note"], style="green" if g["eligible"] else "dim")
    return Group(votes, lines)


BODIES = {"Affordability Agent": affordability_body, "Valuation Agent": valuation_body,
          "Market and Macro Researcher Agent": market_body, "Underwriting Strategist Agent": strategist_body}


def agent_panel(out: AgentOutput, verbose: bool = False) -> None:
    parts = []
    if out.status in ("OK", "WARNING") and out.result:
        parts.append(BODIES[out.agent](out))
    if out.warnings:
        w = Text()
        for msg in out.warnings:
            style = "red" if "exceeds" in msg or "negative" in msg.lower() else "yellow"
            w.append(f"• {msg}\n", style=style)
        parts.append(w)
    # Market and Strategist already show their reasoning above
    shown_above = out.agent in ("Market and Macro Researcher Agent", "Underwriting Strategist Agent")
    if out.reasoning and out.reasoning != "numbers-only mode" and not (shown_above and out.result):
        parts.append(Text(out.reasoning, style="italic"))
    if verbose:
        parts.append(Rule("inputs used (cross-check against the application)", style="dim"))
        parts.append(Text("\n".join(f"{k}: {v}" for k, v in out.inputs_used.items()), style="dim"))
        if out.result.get("formulas"):
            parts.append(Rule("formulas", style="dim"))
            parts.append(Text("\n".join(f"{k} = {v}" for k, v in out.result["formulas"].items()), style="dim"))
    parts.append(Text(f"model: {out.model} · confidence {out.confidence:.2f} · {out.timestamp}", style="dim"))
    style = STATUS_STYLE[out.status]
    console.print(Panel(Group(*parts), title=f"[bold]{out.agent}[/]", subtitle=f"[{style}]{out.status}[/]",
                        border_style=style, title_align="left"))


def summary(result: CommitteeResult) -> None:
    s = result.summary
    risk_style = {"LOW": "green", "MEDIUM": "yellow", "HIGH": "red"}[s["risk_rating"]]
    t = Table.grid(padding=(0, 2))
    t.add_row("[bold]Risk rating[/]", f"[{risk_style}]{s['risk_rating']}[/]",
              "[bold]AI recommendation[/]", f"[{VOTE_STYLE.get(s['recommendation'], '')}]{s['recommendation']}[/]")
    t.add_row("[bold]DTI[/]", pct(s["dti"]), "[bold]LTV[/]", pct(s["ltv"]))
    t.add_row("[bold]Thresholds from[/]", s["thresholds_source"] or "—", "[bold]Assessment hash[/]",
              f"[dim]{result.assessment_hash[:16]}…[/]")
    for note in s["notes"]:
        t.add_row("", f"[yellow]{note}[/]", "", "")
    console.print(Panel(t, title="[bold]Summary[/]", border_style=risk_style))


def footer() -> None:
    console.print(Panel(Text(DISCLAIMER, justify="center", style="bold"), border_style="red"))
