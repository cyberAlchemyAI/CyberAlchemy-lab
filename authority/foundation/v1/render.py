#!/usr/bin/env python3
"""Generate every Foundation-01 human projection from canonical JSON."""

from __future__ import annotations

import json
from pathlib import Path


LAB = Path(__file__).resolve().parents[3]
GENERATOR_ID = "cal.generator.foundation-projections/v1"


def load(rel: str) -> dict:
    return json.loads((LAB / rel).read_text(encoding="utf-8"))


def write(rel: str, text: str) -> None:
    (LAB / rel).write_text(text.rstrip() + "\n", encoding="utf-8")


def header(title: str, source: str, data: dict) -> list[str]:
    return ["<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->", "", f"# {title}", "", f"> Generated from `{source}`; this view is not canonical.", "", f"- Status: `{data['status']}`", f"- Authority effect: `{data['authority_effect']}`", f"- Owner: `{data.get('owner_ref', data.get('semantic_owner_ref'))}`", ""]


def artifact_type(data: dict) -> str:
    lines = header("Artifact Type v1", "artifact.json", data)
    lines += ["## Bounded self-application", "", data["self_application"]["bound"], "", f"Bootstrap gate: {data['self_application']['bootstrap_gate']}", "", "## Registered artifact types", "", "| Type | Semantic kind | Schema | Purpose |", "| --- | --- | --- | --- |"]
    for item in data["registered_types"]:
        lines.append(f"| `{item['artifact_type_ref']}` | `{item['semantic_kind']}` | `{item['schema_path']}` | {item['distinct_validation_purpose']} |")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def lifecycle(data: dict) -> str:
    lines = header("Definition lifecycle profile v1", "lifecycle.json", data)
    lines += ["## States", ""] + [f"- `{x}`" for x in data["states"]]
    lines += ["", "## Transitions", "", "| From | To | Gate | Effect |", "| --- | --- | --- | --- |"]
    for x in data["transitions"]:
        lines.append(f"| `{x['from']}` | `{x['to']}` | {x['gate']} | {x['effect']} |")
    lines += ["", "## Separation invariants", ""] + [f"- {x}" for x in data["separation_invariants"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def evaluation(data: dict) -> str:
    lines = header("Definition evaluation profile v1", "evaluation.json", data)
    lines += ["## Outcomes", ""] + [f"- `{x}`" for x in data["outcomes"]]
    lines += ["", "## Checks", "", "| Check | Purpose | Blocked by |", "| --- | --- | --- |"]
    for x in data["checks"]:
        lines.append(f"| `{x['check_id']}` | {x['purpose']} | {', '.join(x['blocked_by']) or 'nothing'} |")
    lines += ["", "## Admission rule", "", data["admission_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def owners(data: dict) -> str:
    lines = header("Foundation-01 accountable owners", "owners.json", data)
    lines += ["## Principals", ""]
    for x in data["principals"]:
        lines.append(f"- `{x['principal_id']}` — {x['display_label']} (`{x['identity_assurance']}`)")
    lines += ["", "## Separate role assignments", "", "| Role | Principal | Scope |", "| --- | --- | --- |"]
    for x in data["role_assignments"]:
        lines.append(f"| `{x['role_id']}` | `{x['principal_id']}` | {x['scope']} |")
    lines += ["", "## Separation rule", "", data["separation_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def admissions(data: dict) -> str:
    lines = header("Foundation-01 source-admission candidates", "admissions.json", data)
    lines += ["## Candidates", "", "| ID | Selector | Selected digest | Target use |", "| --- | --- | --- | --- |"]
    for x in data["admissions"]:
        lines.append(f"| `{x['admission_id']}` | `{x['selector']}` | `{x['selected_sha256']}` | {x['target_use']} |")
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def registry(data: dict) -> str:
    lines = header("CyberAlchemy Lab Definition Index", "registry.json", data)
    lines += ["## Definitions", ""]
    if data["entries"]:
        lines += ["| ID | Version | Term | Path |", "| --- | --- | --- | --- |"]
        for x in sorted(data["entries"], key=lambda item: (item["definition_id"], item["version"])):
            lines.append(f"| `{x['definition_id']}` | `{x['version']}` | {x['term']} | `{x['path']}` |")
    else:
        lines.append("No admitted Definitions are registered.")
    lines += ["", "## Identity rule", "", data["identity_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def drift(data: dict) -> str:
    lines = header("Definition drift audit", "drift-audit.json", data)
    lines += ["## Summary", ""] + [f"- {k.replace('_', ' ').title()}: `{v}`" for k, v in data["summary"].items()]
    lines += ["", "## Findings", ""]
    for x in data["findings"]:
        lines += [f"### {x['finding_id']} ({x['severity']})", "", x["condition"], "", f"Target: `{x['target']}`", "", f"Remediation: {x['remediation']}", ""]
    lines += ["## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def manifest(data: dict) -> str:
    lines = header("Foundation-01 candidate manifest", "manifest.json", data)
    lines += [f"Principal: `{data['principal_id']}`", "", "## Bound materials", "", "| ID | Path | Digest | Role |", "| --- | --- | --- | --- |"]
    for x in data["materials"]:
        lines.append(f"| `{x['material_id']}` | `{x['path']}` | `{x['sha256']}` | {x['role']} |")
    lines += ["", "## D65 boundary", "", "| Stage | Status | Effect |", "| --- | --- | --- |"]
    for x in data["d65_boundary"]:
        lines.append(f"| {x['stage']} | `{x['status']}` | {x['effect']} |")
    lines += ["", "## Admission posture", "", data["admission_posture"], "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


SURFACES = [
    ("authority/artifact-types/artifact-type/v1/artifact.json", "authority/artifact-types/artifact-type/v1/ARTIFACT.md", artifact_type),
    ("authority/profiles/definition/v1/lifecycle.json", "authority/profiles/definition/v1/LIFECYCLE.md", lifecycle),
    ("authority/profiles/definition/v1/evaluation.json", "authority/profiles/definition/v1/EVALUATION.md", evaluation),
    ("authority/owners/foundation-01/v1/owners.json", "authority/owners/foundation-01/v1/OWNERS.md", owners),
    ("authority/decisions/source-admission/foundation-01/v1/admissions.json", "authority/decisions/source-admission/foundation-01/v1/SOURCE-ADMISSIONS.md", admissions),
    ("authority/definitions/registry.json", "authority/definitions/DEFINITIONS-INDEX.md", registry),
    ("authority/definitions/drift-audit.json", "authority/definitions/DEFINITION-DRIFT-AUDIT.md", drift),
    ("authority/foundation/v1/manifest.json", "authority/foundation/v1/MANIFEST.md", manifest),
]


def main() -> None:
    for source, output, renderer in SURFACES:
        source_path = LAB / source
        if source_path.is_file():
            write(output, renderer(load(source)))


if __name__ == "__main__":
    main()
