#!/usr/bin/env python3
"""Render and validate the CML-07 Craft identity construction chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")
CHAIN = ROOT / "chain.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected(path: Path, selector: str) -> bytes:
    if selector == "whole-file":
        return path.read_bytes()
    start, end = (int(value) for value in selector.removeprefix("lines:").split("-"))
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(lines[start - 1:end]).encode()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_chain(data: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: edit chain.json and run build.py. -->", "", f"# {data['title']}", "", "> Candidate construction chain; no admission or implementation authority.", "", "## Sequence", ""]
    for stage in data["stages"]:
        lines += [f"### {stage['stage_id']}", "", stage["decision_question"], "", "Outputs:", ""]
        lines += [f"- `{item}`" for item in stage["outputs"]]
        lines += ["", f"Effect: {stage['promotion_effect']}", ""]
    lines += ["## Non-regression guarantees", ""] + [f"- {item}" for item in data["non_regression_guarantees"]]
    lines += ["", "## Recommended next unit", "", f"`{data['recommended_next_unit']['unit_id']}` — {data['recommended_next_unit']['scope']}", "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines)


def render_layering(data: dict[str, Any]) -> str:
    lines = ["---", "title: Craft Identity Implementation Layering", "status: draft", "updatedAt: 2026-09-03", "owner: role:lab-architecture-owner", "scope: system", "---", "", "# Craft Identity Implementation Layering", "", "Layer 0 is the smallest semantic and authority closure. Later layers add carrier mechanics, materialization, and admission packaging without invalidating earlier guarantees.", "", "## Context", "", "- Target: CML-07 Craft Product/Project/Method/Goal identity graph", "- Current state: admitted Definition foundation; identity carriers not authored", "- Primary operator: CyberAlchemy Lab architecture and Product owners", "- Primary constraint: migration without identity or authority collapse", "- Source: `docs/identity-packs/0001-craft-identity-chain/chain.json`", "", "## Layer Decision Table", "", "| Layer | Decision question | Stages | Promotion |", "| --- | --- | --- | --- |"]
    stages = {item["stage_id"]: item for item in data["stages"]}
    for layer in data["layering"]:
        question = f"After this layer, we know {layer['decision_unlocked']}."
        promotion = stages[layer["stages"][-1]]["promotion_effect"]
        lines.append(f"| `{layer['layer_id']}` | {question} | {', '.join(f'`{x}`' for x in layer['stages'])} | {promotion} |")
    lines += ["", "## Layer Boundary Heuristic", "", "Layer value = decision unlocked + operator-visible outcome + migration risk reduced.", "", "Layer cost = authoring time + verification time + owner coordination. A layer ends before the next distinct decision begins.", "", "## Recommended next layer", "", f"Start `L0` with `{data['recommended_next_unit']['unit_id']}`. It closes sources, owners, and canonical meanings before schemas or carriers exist.", "", "## Explicitly deferred", ""]
    lines += [f"- {item}" for item in data["deferred"]]
    lines += ["", "## Non-regression guardrails", ""] + [f"- {item}" for item in data["non_regression_guarantees"]]
    return "\n".join(lines)


def main() -> int:
    data = load(CHAIN)
    chain_md = render_chain(data)
    layering_md = render_layering(data)
    write(ROOT / "CHAIN.md", chain_md)
    layering_path = LAB / "docs/craft-identity/implementation-layering.md"
    write(layering_path, layering_md)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    predecessor_results = []
    for item in data["predecessors"]:
        path = LAB / item["path"]
        predecessor_results.append({"id": item["id"], "expected": item["sha256"], "actual": sha(path)})
    check("predecessors-current", all(item["expected"] == item["actual"] for item in predecessor_results), predecessor_results)
    check("foundation-admitted", load(LAB / data["predecessors"][0]["path"])["status"] == "owner-admitted", load(LAB / data["predecessors"][0]["path"])["status"])
    source_results = []
    for item in data["external_source_selectors"]:
        actual = hashlib.sha256(selected(SOURCE / item["path"], item["selector"])).hexdigest()
        source_results.append({"id": item["source_id"], "expected": item["sha256"], "actual": actual})
    check("external-source-selectors-current", all(item["expected"] == item["actual"] for item in source_results), source_results)
    stage_ids = {item["stage_id"] for item in data["stages"]}
    check("stage-dependencies-resolve", all(set(item["depends_on"]) <= stage_ids for item in data["stages"]), sorted(stage_ids))
    seen = set()
    ordered = True
    for item in data["stages"]:
        ordered = ordered and set(item["depends_on"]) <= seen
        seen.add(item["stage_id"])
    check("stage-order-topological", ordered, [item["stage_id"] for item in data["stages"]])
    outputs = [output for stage in data["stages"] for output in stage["outputs"]]
    check("output-paths-unique", len(outputs) == len(set(outputs)), len(outputs))
    check("product-project-carriers-separate", any(path.startswith("product/products/craft/") for path in outputs) and any(path.startswith("coordination/projects/craft/") for path in outputs), outputs)
    check("no-bounded-context-output", not any(path.startswith("contexts/") for path in outputs), outputs)
    required = {"Product", "Project", "Method", "Goal", "Product Capability", "Bounded Context", "directory"}
    guard_text = " ".join(data["non_regression_guarantees"])
    check("identity-non-collapse-explicit", all(term in guard_text for term in required), sorted(required))
    check("single-final-human-boundary", data["non_regression_guarantees"][-1].endswith("final digest-bound CML-07 bundle boundary."), data["non_regression_guarantees"][-1])
    check("machine-human-direction", data["source_direction"]["canonical"] == "chain.json" and data["source_direction"]["projection_policy"] == "generated-only", data["source_direction"])
    check("chain-projection-parity", (ROOT / "CHAIN.md").read_text(encoding="utf-8") == chain_md.rstrip() + "\n", sha(ROOT / "CHAIN.md"))
    check("layering-projection-parity", layering_path.read_text(encoding="utf-8") == layering_md.rstrip() + "\n", sha(layering_path))
    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-craft-identity-chain-validation/v1",
        "subject": data["chain_id"],
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {"chain_sha256": sha(CHAIN), "chain_projection_sha256": sha(ROOT / "CHAIN.md"), "layering_projection_sha256": sha(layering_path)},
        "recommended_next_unit": data["recommended_next_unit"],
        "claim_ceiling": "PASS proves the CML-07 candidate chain is current, acyclic, path-orthogonal, projection-deterministic, and bounded to one final human checkpoint. It does not admit or implement any stage."
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"CRAFT_IDENTITY_CHAIN={'PASS' if not failed else 'FAIL'}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    print(f"CHAIN_SHA256={receipt['materials']['chain_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
