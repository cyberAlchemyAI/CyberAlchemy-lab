#!/usr/bin/env python3
"""Exact, read-only inventory of the ten selected workflow definitions.

The output is an engineering work list. It does not infer a producer or an
admission from a carrier schema, a candidate adapter, or a historical receipt.
"""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BINDINGS = ROOT / "implementation/lab-runtime/candidates/repeatable-operation/design/workflow-bindings.json"
REGISTRY = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v30/workflow_output_registry.py"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def inventory() -> dict:
    selected = json.loads(BINDINGS.read_bytes())
    registry = runpy.run_path(str(REGISTRY))["REGISTRY"]
    if len(selected["workflows"]) != 10 or len(registry) != 28:
        raise ValueError("selected workflow or transition count changed")
    names: set[str] = set()
    refs: set[str] = set()
    rows: list[dict] = []
    for workflow in selected["workflows"]:
        name = workflow["name"]
        if name in names:
            raise ValueError("duplicate selected workflow")
        names.add(name)
        binding = workflow["source_binding"]
        path = ROOT / binding["path"]
        raw = path.read_bytes()
        if digest(raw) != binding["sha256"] or len(raw) != binding["size_bytes"]:
            raise ValueError(f"definition original bytes differ: {name}")
        definition = json.loads(raw)
        if definition["workflow_type_ref"] != f"workflow:{name}:v1-candidate":
            raise ValueError(f"workflow identity differs: {name}")
        declared = {step["transition_ref"]: step for step in definition["transitions"]}
        selected_steps = {step["transition_ref"]: step for step in workflow["transitions"]}
        if len(declared) != len(definition["transitions"]) or set(declared) != set(selected_steps):
            raise ValueError(f"transition selection differs: {name}")
        for ref, step in declared.items():
            if ref in refs:
                raise ValueError("duplicate selected transition")
            refs.add(ref)
            register = registry[ref]
            if register["workflow_type_ref"] != definition["workflow_type_ref"] or register["definition_binding"] != {"path": binding["path"], "sha256": binding["sha256"]}:
                raise ValueError(f"API30 registry definition differs: {ref}")
            if step["from_state"] != selected_steps[ref]["from_state"] or step["to_state"] != selected_steps[ref]["to_state"]:
                raise ValueError(f"transition endpoints differ: {ref}")
            carriers = step["output_carriers"]
            if not carriers or len(carriers) != len(set(carriers)) or carriers != register["output_carriers"]:
                raise ValueError(f"output carrier closure differs: {ref}")
            rows.append({"transition_ref": ref, "workflow": name, "from_state": step["from_state"],
                         "to_state": step["to_state"], "required_output_carriers": carriers,
                         "producer_path": register["original_producer_path"],
                         "status": "requires-actual-output-bearing-run-and-later-consumer"})
    if refs != set(registry):
        raise ValueError("registry contains unselected transitions")
    return {"schema_version": "lab-T31-exact-workflow-inventory/v1", "workflow_count": len(names),
            "transition_count": len(rows), "definition_bindings": [w["source_binding"] for w in selected["workflows"]],
            "transitions": sorted(rows, key=lambda row: row["transition_ref"])}


def check_output_set(transition: dict, originals: list[tuple[dict, bytes]]) -> list[dict]:
    """Refuse zero, missing, wrong, duplicate, or byte-drifted output sets."""
    expected = set(transition["required_output_carriers"])
    if not originals or len(originals) != len(expected):
        raise ValueError("complete nonempty output set required")
    carriers: set[str] = set()
    versions: set[str] = set()
    for header, raw in originals:
        if set(header) != {"carrier_ref", "identity_ref", "version_ref", "scope_ref", "byte_sha256"}:
            raise ValueError("closed output ArtifactRef required")
        if header["carrier_ref"] not in expected or header["carrier_ref"] in carriers:
            raise ValueError("wrong or duplicate output carrier")
        if header["version_ref"] in versions or not header["version_ref"].startswith(header["identity_ref"] + "@"):
            raise ValueError("duplicate or inconsistent output revision")
        if type(raw) is not bytes or not raw or digest(raw) != header["byte_sha256"]:
            raise ValueError("original output bytes differ")
        carriers.add(header["carrier_ref"])
        versions.add(header["version_ref"])
    if carriers != expected:
        raise ValueError("missing required output carrier")
    return [header for header, _ in originals]


if __name__ == "__main__":
    print(json.dumps(inventory(), sort_keys=True, indent=2))
