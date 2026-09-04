#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_chain(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit chain.json and run build.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Candidate construction chain; no admission, implementation, migration, or runtime authority.",
        "",
        f"- Chain: `{data['chain_id']}`",
        f"- Status: `{data['status']}`",
        f"- Predecessor: `{data['predecessor']['decision_id']}`",
        f"- Interaction mode: `{data['interaction_profile']['decision_mode']}` at `{data['interaction_profile']['checkpoint']}`",
        "",
        "## Outcome",
        "",
        data["objective"],
        "",
        "## Why the chain starts with semantic closure",
        "",
    ]
    for gap in data["current_gaps"]:
        lines.append(f"- **{gap['gap_id']}** — {gap['consequence']}")
    lines += ["", "## Sequence", ""]
    for stage in data["stages"]:
        lines += [
            f"### {stage['stage_id']}",
            "",
            stage["decision_question"],
            "",
            "Included:",
            "",
        ]
        lines += [f"- {item}" for item in stage["included"]]
        lines += ["", "Outputs:", ""]
        lines += [f"- `{item}`" for item in stage["outputs"]]
        lines += ["", "Exit evidence:", ""]
        lines += [f"- {item}" for item in stage["exit_evidence"]]
        lines += ["", f"Effect ceiling: {stage['promotion_effect']}", ""]
    lines += ["## One final interaction", "", data["interaction_profile"]["rule"], ""]
    lines += [f"- `{item['request_id']}` — {item['effect']}" for item in data["final_decision_request_set_shape"]]
    lines += ["", "Excluded from that interaction:", ""]
    lines += [f"- {item}" for item in data["interaction_profile"]["excluded_effects"]]
    lines += ["", "## Recommended next unit", "", f"`{data['recommended_next_unit']['unit_id']}` — {data['recommended_next_unit']['scope']}", "", "## Claim ceiling", "", data["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def render_layering(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit chain.json and run build.py. -->",
        "",
        "# Craft First Capability Implementation Layering",
        "",
        "> Five candidate layers from semantic closure to a final exact-byte decision checkpoint.",
        "",
    ]
    for layer in data["layers"]:
        final_stage_question = next(
            stage["decision_question"]
            for stage in data["stages"]
            if stage["stage_id"] == layer["stages"][-1]
        )
        decision_unlocked = final_stage_question.removeprefix(
            "After this stage, we know whether "
        ).rstrip(".")
        lines += [
            f"## {layer['layer_id']} — {layer['theme']}",
            "",
            f"**After this layer, we know whether:** {decision_unlocked}.",
            "",
            f"- Minimum working unit: {layer['minimum_working_unit']}",
            f"- Visible outcome: {layer['visible_outcome']}",
            f"- Risk retired: {layer['risk_retired']}",
            f"- Cost introduced: {layer['costs_introduced']}",
            f"- Exit evidence: {layer['exit_evidence']}",
            f"- Promotion rule: {layer['promotion_rule']}",
            f"- Non-regression: {layer['non_regression_guarantee']}",
            f"- Next: {layer['next_layer']}",
            "",
        ]
    lines += ["## Dependency spine", ""]
    lines += [f"{index + 1}. `{item}`" for index, item in enumerate(data["d65_order"])]
    lines += ["", "## Boundary", "", "All five layers produce candidates and evidence before one human interaction. That interaction contains separate exact requests; it does not merge their authorities. Publication, release, deployment, and stable-version declaration are outside this chain."]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = load(ROOT / "chain.json")
    (ROOT / "CHAIN.md").write_text(render_chain(data), encoding="utf-8")
    (ROOT / "IMPLEMENTATION-LAYERING.md").write_text(render_layering(data), encoding="utf-8")

    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    predecessor = data["predecessor"]
    pred_decision = load(LAB / predecessor["decision_path"])
    pred_receipt = load(LAB / predecessor["validation_receipt_path"])
    check(
        "cml07-predecessor-current-and-admitted",
        sha(LAB / predecessor["decision_path"]) == predecessor["decision_sha256"]
        and sha(LAB / predecessor["validation_receipt_path"]) == predecessor["validation_receipt_sha256"]
        and pred_decision.get("status") == predecessor["required_state"]
        and pred_receipt.get("result") == "PASS",
        {"decision_status": pred_decision.get("status"), "receipt_result": pred_receipt.get("result")},
    )

    planning = data["planning_basis"]
    check("planning-basis-current", sha(LAB / planning["path"]) == planning["sha256"], planning)

    contract_results = []
    for item in data["admitted_contracts_reused"]:
        decision = load(LAB / item["admission_decision_path"])
        current = (
            sha(LAB / item["path"]) == item["sha256"]
            and sha(LAB / item["admission_decision_path"]) == item["admission_decision_sha256"]
            and decision.get("status") == "owner-admitted"
        )
        contract_results.append({"artifact_type_ref": item["artifact_type_ref"], "current": current})
    check("reused-artifact-type-contracts-current-and-admitted", all(item["current"] for item in contract_results), contract_results)

    interaction = data["interaction_profile"]
    interaction_results = []
    for prefix in ("profile_definition", "request_set_definition", "checkpoint_definition"):
        path = LAB / interaction[f"{prefix}_path"]
        current = sha(path) == interaction[f"{prefix}_sha256"]
        interaction_results.append({"definition_ref": interaction[f"{prefix}_ref"], "current": current})
    check("interaction-definitions-current", all(item["current"] for item in interaction_results), interaction_results)

    registry = load(LAB / "authority/definitions/registry.json")
    registry_ids = {item["definition_id"] for item in registry.get("entries", [])}
    product_capability_absent = not any("product-capability" in item or item == "cal.definition.product-capability" for item in registry_ids)
    check("product-capability-semantic-gap-truthful", product_capability_absent, {"product_capability_definition_present": not product_capability_absent})

    artifact_type_names = {path.parents[1].name for path in (LAB / "authority/artifact-types").glob("*/v*/artifact.json")}
    check("product-capability-artifact-type-gap-truthful", "product-capability" not in artifact_type_names, sorted(artifact_type_names))

    stage_ids = [stage["stage_id"] for stage in data["stages"]]
    seen: set[str] = set()
    topology_ok = True
    for stage in data["stages"]:
        topology_ok = topology_ok and set(stage["depends_on"]) <= seen
        seen.add(stage["stage_id"])
    check("stage-order-topological", topology_ok and len(stage_ids) == len(set(stage_ids)), stage_ids)
    check("cml08-through-cml12-covered", [stage["phase_ref"].split("-")[1] for stage in data["stages"]] == ["08", "08", "09", "10", "11", "12"], [stage["phase_ref"] for stage in data["stages"]])
    check("d65-order-exact", data["d65_order"] == ["canonical-definitions-and-artifact-types", "product-capability", "capability-local-business-ontology", "authored-specification", "deterministic-compiled-graph-and-system-ontology", "exact-implementation-binding", "conformance-evidence"], data["d65_order"])

    required_layer_fields = {"minimum_working_unit", "visible_outcome", "risk_retired", "costs_introduced", "exit_evidence", "promotion_rule", "non_regression_guarantee", "next_layer"}
    layers_ok = len(data["layers"]) == 5 and all(required_layer_fields <= set(layer) and set(layer["stages"]) <= set(stage_ids) for layer in data["layers"])
    check("five-layer-contract-complete", layers_ok, [layer["layer_id"] for layer in data["layers"]])
    check("layer-zero-is-smallest-selection-proof", "without business ontology or implementation" in data["layers"][0]["minimum_working_unit"], data["layers"][0]["minimum_working_unit"])
    check("decision-questions-explicit", all(stage["decision_question"].startswith("After this stage, we know whether") for stage in data["stages"]), [stage["decision_question"] for stage in data["stages"]])

    placement = data["placement_resolution"]
    check(
        "no-context-placement-fails-closed",
        placement["context_selected"].startswith("contexts/")
        and placement["no_context_selected"].startswith("blocked-")
        and placement["resolved_token"] == "<resolved-instance-root>",
        placement,
    )

    outputs = [output for stage in data["stages"] for output in stage["outputs"]]
    check("output-surfaces-unique", len(outputs) == len(set(outputs)), outputs)
    check("canonical-human-direction-explicit", data["source_direction"]["canonical"] == "chain.json" and data["source_direction"]["projection_policy"] == "generated-only", data["source_direction"])

    request_ids = [item["request_id"] for item in data["final_decision_request_set_shape"]]
    check("single-final-checkpoint", interaction["decision_mode"] == "single" and interaction["checkpoint"].startswith("CML12-FINAL"), interaction)
    check("request-identities-distinct", len(request_ids) == len(set(request_ids)), request_ids)
    check("unknown-byte-approval-forbidden", "before its target and digest exist" in interaction["unknown_target_rule"], interaction["unknown_target_rule"])
    excluded = " ".join(interaction["excluded_effects"]).lower()
    check("publication-deployment-outside-boundary", "publication" in excluded and "deployment" in excluded and "git commit" in excluded, interaction["excluded_effects"])

    chain_projection = render_chain(data)
    layering_projection = render_layering(data)
    check("chain-projection-parity", (ROOT / "CHAIN.md").read_text(encoding="utf-8") == chain_projection, sha(ROOT / "CHAIN.md"))
    check("layering-projection-parity", (ROOT / "IMPLEMENTATION-LAYERING.md").read_text(encoding="utf-8") == layering_projection, sha(ROOT / "IMPLEMENTATION-LAYERING.md"))

    failed = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-construction-chain-validation/v1",
        "subject": data["chain_id"],
        "result": "PASS" if not failed else "FAIL",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "materials": {
            "chain_sha256": sha(ROOT / "chain.json"),
            "chain_projection_sha256": sha(ROOT / "CHAIN.md"),
            "layering_projection_sha256": sha(ROOT / "IMPLEMENTATION-LAYERING.md"),
        },
        "open_gaps": data["current_gaps"],
        "recommended_next_unit": data["recommended_next_unit"],
        "claim_ceiling": "PASS proves only that the candidate CML-08 through CML-12 chain is dependency-ordered, preserves current predecessor contracts, truthfully exposes Product Capability gaps, implements the five-layer planning contract, reproduces its human projections, and places one exact-byte interaction after candidate evidence. It does not admit or execute any stage.",
    }
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CRAFT_FIRST_CAPABILITY_CHAIN={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CHAIN_SHA256={receipt['materials']['chain_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
