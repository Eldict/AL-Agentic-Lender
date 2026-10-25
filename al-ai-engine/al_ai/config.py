# Loads config.yaml, optionally with thresholds from Firestore on top.

from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path = ROOT / "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["thresholds_source"] = "config.yaml defaults"
    return cfg


# replaces known threshold values, ignores unknown keys
def with_threshold_overrides(cfg: dict, overrides: dict | None, source: str) -> dict:
    if not overrides:
        return cfg
    cfg = copy.deepcopy(cfg)
    known = cfg["thresholds"].keys()
    applied = {k: float(v) for k, v in overrides.items() if k in known and v is not None}
    cfg["thresholds"].update(applied)
    if applied:
        cfg["thresholds_source"] = source
    return cfg


# config paths are relative to the project folder
def resolve(path: str) -> Path:
    return ROOT / path
