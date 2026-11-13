"""SHINOBI :: Baseline Diff Reporter."""

import json
from pathlib import Path
from typing import Any, Dict


def load_report(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def diff_reports(old_path: str, new_path: str) -> Dict[str, Any]:
    old = load_report(old_path)
    new = load_report(new_path)

    old_gaps = {
        (f["url"], g["header"])
        for f in old.get("findings", [])
        for g in f.get("header_gaps", [])
    }
    new_gaps = {
        (f["url"], g["header"])
        for f in new.get("findings", [])
        for g in f.get("header_gaps", [])
    }

    return {
        "fixed": sorted(old_gaps - new_gaps),
        "still_present": sorted(old_gaps & new_gaps),
        "newly_introduced": sorted(new_gaps - old_gaps),
    }
