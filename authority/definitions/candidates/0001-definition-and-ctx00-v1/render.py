#!/usr/bin/env python3
"""Generate every human projection for the Definition and CTX-00 candidate set."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
DEFINITION_GENERATOR = LAB / "authority/artifact-types/definition/v1/generator.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def render_registry(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit registry-postimage.json and run render.py. -->", "", "# Proposed CyberAlchemy Lab Definition Index", "", "> Generated candidate projection; the live canonical registry remains unchanged.", "", f"- Record: `{data['record_id']}`", f"- Status: `{data['status']}`", f"- Authority effect: `{data['authority_effect']}`", "", "| ID | Version | Term | Candidate path | Digest |", "| --- | --- | --- | --- | --- |"]
    for item in sorted(data["entries"], key=lambda x: (x["definition_id"], x["version"])):
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['path']}` | `{item['sha256']}` |")
    lines.extend(["", "## Activation rule", "", data["activation_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_drift(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit drift-audit-postimage.json and run render.py. -->", "", "# Definition and CTX-00 candidate drift audit", "", "> Generated candidate projection; it is not canonical.", "", "## Summary", ""]
    lines.extend(f"- {key.replace('_', ' ').title()}: `{value}`" for key, value in data["summary"].items())
    lines.extend(["", "## Findings", ""])
    for item in data["findings"]:
        lines.extend([f"### {item['finding_id']} ({item['severity']}, {item['status']})", "", item["condition"], "", f"Target: `{item['target']}`", "", f"Remediation: {item['remediation']}", ""])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_candidate(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: edit candidate.json and run render.py. -->", "", "# Definition and CTX-00 semantic candidate", "", "> Generated from the machine-canonical candidate manifest; it has no authority effect.", "", f"- Candidate: `{data['candidate_id']}`", f"- Status: `{data['status']}`", f"- Definitions: `{len(data['definitions'])}`", f"- Authority effect: `{data['authority_effect']}`", "", "## Bound definitions", "", "| ID | Path | Digest |", "| --- | --- | --- |"]
    for item in data["definitions"]:
        lines.append(f"| `{item['definition_id']}` | `{item['path']}` | `{item['sha256']}` |")
    lines.extend(["", "## Evaluation posture", "", data["evaluation_posture"], "", "## Remaining gate", "", data["remaining_gate"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def main() -> None:
    spec = importlib.util.spec_from_file_location("definition_v1_generator", DEFINITION_GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    for source in sorted(ROOT.glob("definitions/*/v1/definition.json")):
        write(source.with_name("DEFINITION.md"), module.render(load(source)))
    write(ROOT / "DEFINITIONS-INDEX.md", render_registry(load(ROOT / "registry-postimage.json")))
    write(ROOT / "DEFINITION-DRIFT-AUDIT.md", render_drift(load(ROOT / "drift-audit-postimage.json")))
    if (ROOT / "candidate.json").is_file():
        write(ROOT / "CANDIDATE.md", render_candidate(load(ROOT / "candidate.json")))


if __name__ == "__main__":
    main()
