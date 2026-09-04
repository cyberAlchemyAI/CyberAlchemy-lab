#!/usr/bin/env python3
"""Render the exact CTX07 artifact-type admission decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def render(data: dict) -> str:
    selection = data["selection"]
    result = data["admission_result"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and rerun render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Machine-canonical decision; this Markdown is a generated projection.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Selection: `{selection['selection_token']}`",
        f"- Principal: `{selection['selected_by_principal']}` as `{selection['selected_role']}`",
        f"- Recorded: `{selection['recorded_at']}`",
        "",
        "## Admitted artifact types",
        "",
        "| Artifact type | Version | Predecessor | Digest |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admitted_artifact_types"]:
        lines.append(
            f"| `{item['artifact_type_ref']}` | `{item['version']}` | "
            f"`{item['predecessor_ref']}` | `{item['artifact_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Admission result",
            "",
            f"- Artifact types admitted: `{result['artifact_types_admitted']}`",
            f"- Current for new normalized construction: `{result['artifact_type_versions_current_for_new_normalized_construction']}`",
            f"- Predecessors withdrawn: `{result['predecessors_withdrawn']}`",
            f"- Predecessors superseded: `{result['predecessors_superseded']}`",
            f"- Context instances created: `{result['context_instances_created']}`",
            f"- Context Maps created: `{result['context_maps_created']}`",
            f"- Tooling runtimes admitted: `{result['tooling_runtimes_admitted']}`",
            "",
            "## Materialization",
            "",
            data["materialization"]["rule"],
            "",
            data["materialization"]["predecessor_boundary"],
            "",
            data["materialization"]["resolution_boundary"],
            "",
            data["materialization"]["projection_boundary"],
            "",
            "## Excluded effects",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
