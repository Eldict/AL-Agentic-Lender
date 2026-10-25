# AL-AI Engine: runs the AI committee on one loan application.
# example: python main.py --sample samples/affordable.json

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from al_ai import display
from al_ai.committee import ConsentError, run_committee
from al_ai.config import ROOT, load_config, with_threshold_overrides
from al_ai.llm_clients import LLMRouter
from al_ai.models import DISCLAIMER, Application


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the AL-AI committee on a loan application.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--sample", metavar="FILE", help="local JSON application, e.g. samples/affordable.json")
    src.add_argument("--firestore", metavar="APPLICATION_ID", help="read the application from Firestore")
    src.add_argument("--list", action="store_true", help="list application IDs in Firestore")
    p.add_argument("--json", action="store_true", help="print the full structured result as JSON")
    p.add_argument("--write-back", action="store_true", help="save the result to Firestore (asks first)")
    p.add_argument("--no-llm", action="store_true", help="numbers-only mode: skip all LLMs")
    p.add_argument("--verbose", "-v", action="store_true", help="show inputs used and formulas per agent")
    return p.parse_args()


def load_sample(path: str) -> Application:
    file = Path(path)
    if not file.exists():
        file = ROOT / path
    return Application(**json.loads(file.read_text(encoding="utf-8")))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # so € prints on Windows
    load_dotenv(ROOT / ".env")                # API keys
    args = parse_args()
    cfg = load_config()

    # 1. load the application
    if args.list or args.firestore:
        from al_ai import firestore_adapter as fs
        if args.list:
            fs.print_applications()
            return 0
        app = fs.get_application(args.firestore)
        cfg = with_threshold_overrides(cfg, fs.load_threshold_overrides(cfg), "Firestore risk settings")
    else:
        if args.write_back:
            print("--write-back only works with --firestore")
            return 2
        try:
            app = load_sample(args.sample)
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            print(f"Could not load sample application: {exc}")
            return 2

    # 2. check which LLMs are available
    llm = LLMRouter.from_config(cfg, disabled=args.no_llm)

    # 3. run the four agents
    try:
        if args.json:
            result = run_committee(app, cfg, llm)
        else:
            display.header(app, llm)
            status = None

            # spinner while each agent works, then print its panel
            def start(name):
                nonlocal status
                status = display.console.status(f"[bold cyan]{name} thinking…", spinner="dots")
                status.start()

            def done(out):
                status.stop()
                display.agent_panel(out, verbose=args.verbose)

            result = run_committee(app, cfg, llm, on_start=start, on_done=done)
            display.summary(result)
    except ConsentError as exc:
        print(f"Not assessed: {exc}")
        print(DISCLAIMER)
        return 3

    # 4. print the result (and save it if asked)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        display.footer()

    if args.write_back:
        from al_ai import firestore_adapter as fs
        fs.write_back(app.application_id, result, cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
