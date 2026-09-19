#!/usr/bin/env python3
"""Extend the previous read-only reconciliation with this batch's exact target."""
from collections import Counter
import json
import subprocess
import sys
from support import ROOT, PREVIOUS, PACKAGE, binding, dump, load, sha, need


def build():
    result = subprocess.run([sys.executable, "-c", "import json,reconcile; print(json.dumps(reconcile.build()))"],
        cwd=PREVIOUS, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    entries = load(ROOT / "registry.json")["entries"]
    need(len(entries) == 1 and entries[0]["target_id"] == "type.residue", "Unexpected batch target")
    entry = entries[0]
    need(entry["sha256"] == sha(PACKAGE / "artifact.json"), "Residue carrier changed")
    rows = [x for x in data["targets"] if x["target_id"] == "type.residue"]
    need(len(rows) == 1 and rows[0]["construction_state"] == "scaffold-only", "Residue frontier has changed")
    rows[0].update(construction_state="constructed-candidate", evidence=[{**binding(PACKAGE / "artifact.json"), "registry": str((ROOT / "registry.json").relative_to(ROOT.parents[4]))}],
                   next_action="retain candidate; use current tests before promotion")
    data["inputs"].append(binding(ROOT / "registry.json"))
    data["state_counts"] = dict(sorted(Counter(x["construction_state"] for x in data["targets"]).items()))
    return data


if __name__ == "__main__":
    result = build()
    dump(ROOT / "reconciliation.json", result)
    print(result["state_counts"])
