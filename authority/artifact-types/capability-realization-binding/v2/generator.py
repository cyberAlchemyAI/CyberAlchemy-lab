#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def render_artifact(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is artifact.json. -->",
        "",
        "# Capability Realization Binding Artifact Type v2",
        "",
        f"- Type: `{data['artifact_type_ref']}`",
        f"- Version: `{data['version']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Predecessor: `{data['predecessor_contract']['artifact_type_ref']}`",
        "",
        "## Semantic identity",
        "",
    ]
    for item in data["semantic_definition_bindings"]:
        lines.append(f"- `{item['definition_ref']}` — `{item['admission_posture']}` — `{item['path']}`")
    lines += ["", "## Distinct validation purpose", "", data["distinct_validation_purpose"], "", "## Orthogonality rules", ""]
    lines += [f"- **{item['rule_id']}**: {item['statement']}" for item in data["orthogonality_rules"]]
    lines += ["", "## Realistic example", "", "One binding names `product-capability:governed-definition-admission@1` and an explicit `workflow:definition-admission:v1` realization. The binding records their governed connection; it does not become either endpoint or prove that the workflow runs successfully.", "", "## Typed residue", ""]
    lines += [f"- `{item['residue_id']}` ({item['owner_ref']}): {item['missing']} Consequence: {item['consequence']}" for item in data["typed_residue"]]
    lines += ["", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_instance(artifact: dict, data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is record.json. -->",
        "",
        "# Capability Realization Binding v2 fixture",
        "",
        f"- Binding: `{data['node_id']}`",
        f"- Capability version: `{data['capability_version_ref']}`",
        f"- State: `{data['binding_state']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        "",
        "## Realization endpoints",
        "",
    ]
    for endpoint in data["realization_refs"]:
        lines.append(f"- `{endpoint['realization_kind']}` `{endpoint['realization_ref']}` — owner `{endpoint['owner_ref']}` — contract `{endpoint['contract_ref']}`")
    lines += ["", "## Limitations", ""]
    lines += [f"- {item}" for item in data["limitations"]]
    lines += ["", "## Projection boundary", "", "This generated view adds no admission, adoption, conformance, operation, effectiveness, value, or runtime authority."]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    artifact = json.loads((ROOT / "artifact.json").read_text(encoding="utf-8"))
    witness = ROOT / artifact["validation_contract"]["positive_witness"]
    data = json.loads(witness.read_text(encoding="utf-8"))
    (ROOT / "ARTIFACT.md").write_text(render_artifact(artifact), encoding="utf-8")
    (ROOT / artifact["validation_contract"]["positive_projection"]).write_text(render_instance(artifact, data), encoding="utf-8")


if __name__ == "__main__":
    main()
