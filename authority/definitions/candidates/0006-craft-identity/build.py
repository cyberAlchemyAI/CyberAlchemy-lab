#!/usr/bin/env python3
"""Generate human projections for the CML-07 W0 machine-canonical candidates."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
ADMISSIONS = LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json"
OWNERS = LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owner-bindings.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def render_admissions(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit admissions.json and run build.py. -->", "", "# Craft Identity Source Admissions", "", "> Candidate only; no source authority is active.", ""]
    for item in data["admissions"]:
        selector = "whole file" if item["selector_kind"] == "whole-file-v1" else f"lines {item['start_line']}-{item['end_line']}"
        lines += [f"## {item['admission_id']}", "", f"- Source: `{item['source_repository']}:{item['source_path']}`", f"- Selector: `{selector}`", f"- Digest: `{item['selected_sha256']}`", f"- Permitted use: {item['target_use']}", ""]
    lines += ["## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def render_owners(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit owner-bindings.json and run build.py. -->", "", "# Craft Identity Owner Bindings", "", "> Candidate only; these bindings are not active.", "", f"- Preserved role: `{data['preserved_required_role']['role_id']}` -> `{data['preserved_required_role']['principal_id']}`", "", "## Proposed separate assignments", "", "| Role | Principal | Scope |", "| --- | --- | --- |"]
    for item in data["assignments"]:
        lines.append(f"| `{item['role_id']}` | `{item['principal_id']}` | {item['scope']} |")
    lines += ["", "## Separation rule", "", data["separation_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def main() -> None:
    tools = ROOT.parent / "_candidate_pack.py"
    spec = importlib.util.spec_from_file_location("candidate_pack", tools)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.render(ROOT)
    write(ADMISSIONS.with_name("SOURCE-ADMISSIONS.md"), render_admissions(load(ADMISSIONS)))
    write(OWNERS.with_name("OWNER-BINDINGS.md"), render_owners(load(OWNERS)))


if __name__ == "__main__":
    main()
