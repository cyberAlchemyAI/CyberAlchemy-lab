#!/usr/bin/env python3
"""Build and validate the CML-07 S2 identity Artifact Type pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
PACK_PATH = ROOT / "pack.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_pack(pack: dict[str, Any], receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is pack.json. -->",
        "",
        "# CML-07 S2 Orthogonal Identity Artifact Types",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Artifact Types: `{len(pack['artifact_types'])}`",
        f"- Aggregate checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        f"- Status: `{pack['status']}`",
        "",
        "## Artifact Types",
        "",
    ]
    for item in pack["artifact_types"]:
        lines.append(f"- `{item['artifact_type_ref']}` — [machine](../../../{item['artifact_path']}) — [human](../../../{item['projection_path']})")
    lines.extend(["", "## Promotion blockers", ""])
    lines.extend(f"- {item}" for item in pack["promotion_blockers"])
    lines.extend(["", "## Claim ceiling", "", pack["claim_ceiling"]])
    return "\n".join(lines)


def render_layering(pack: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical layers are in pack.json. -->",
        "",
        "# CML-07 S2 Artifact Types Implementation Layering",
        "",
        "Layer value is the decision unlocked, visible outcome, and risk reduced. Layer cost is authoring, verification, and coordination. Each boundary ends at the smallest slice that unlocks the next responsible decision.",
        "",
        "| Layer | Decision question | Minimum working unit | Outcome | Risk reduced | Promotion |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for layer in pack["implementation_layers"]:
        lines.append(f"| `{layer['layer_id']}` | {layer['decision_question']} | {layer['minimum_working_unit']} | {layer['outcome']} | {layer['risk_reduced']} | {layer['promotion_decision']} |")
    lines.extend(["", "## Layer details", ""])
    for layer in pack["implementation_layers"]:
        lines.extend([
            f"### {layer['layer_id']}",
            "",
            f"- Included: {'; '.join(layer['included'])}",
            f"- Deferred: {'; '.join(layer['deferred'])}",
            f"- Exit evidence: {'; '.join(layer['exit_evidence'])}",
            "",
        ])
    lines.extend(["## Non-regression guardrails", ""])
    lines.extend(f"- {item}" for item in pack["non_regression_guardrails"])
    lines.extend(["", "## Recommended next layer", "", f"`{pack['recommended_next_stage']['stage_id']}` is `{pack['recommended_next_stage']['posture']}`.", "", "## Major deferred scope", "", "Artifact Type admission, real Craft identity carriers, identity-contract conformance, implementation/runtime conformance, publication, and stable release."])
    return "\n".join(lines)


def main() -> int:
    pack = load(PACK_PATH)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id":check_id,"result":"PASS" if ok else "BLOCK","detail":detail})

    predecessor = LAB / pack["predecessor_decision"]["path"]
    decision = load(predecessor)
    check("admitted-s2-predecessor-current", sha(predecessor) == pack["predecessor_decision"]["sha256"] and decision["status"] == pack["predecessor_decision"]["required_status"], {"sha256":sha(predecessor),"status":decision["status"]})
    chain_path = LAB / pack["selected_chain"]["path"]
    chain = load(chain_path)
    stage = next((x for x in chain["stages"] if x["stage_id"] == pack["selected_chain"]["stage_id"]), None)
    check("selected-chain-and-stage-current", sha(chain_path) == pack["selected_chain"]["sha256"] and stage is not None, {"chain_sha256":sha(chain_path),"stage_found":stage is not None})

    artifacts = []
    receipts = []
    material_results = []
    for item in pack["artifact_types"]:
        paths = {
            "artifact":(LAB / item["artifact_path"],item["artifact_sha256"]),
            "schema":(LAB / item["schema_path"],item["schema_sha256"]),
            "projection":(LAB / item["projection_path"],item["projection_sha256"]),
            "receipt":(LAB / item["receipt_path"],item["receipt_sha256"]),
        }
        observed = {name:sha(path) if path.is_file() else "missing" for name,(path,_) in paths.items()}
        expected = {name:digest for name,(_,digest) in paths.items()}
        material_results.append({"artifact_type_ref":item["artifact_type_ref"],"expected":expected,"observed":observed})
        artifacts.append(load(paths["artifact"][0]))
        receipts.append(load(paths["receipt"][0]))
    check("six-type-materials-current", len(material_results) == 6 and all(x["expected"] == x["observed"] for x in material_results), material_results)
    check("six-type-receipts-pass", all(x["result"] == "PASS" for x in receipts), [{"subject":x["subject"],"result":x["result"]} for x in receipts])
    check("six-type-schema-conformance-only", all(x["assessment"]["schema_conformance"] == "PASS" and x["assessment"]["admission_posture"] == "candidate-unadmitted" and x["assessment"]["implementation_conformance"] == x["assessment"]["runtime_conformance"] == "not_evaluable" for x in receipts), [x["assessment"] for x in receipts])

    type_refs = [x["artifact_type_ref"] for x in artifacts]
    schema_refs = [x["schema_ref"] for x in artifacts]
    identities = [x["instance_contract"]["identity_field"] for x in artifacts]
    check("orthogonal-type-schema-and-instance-identities", len(type_refs) == len(set(type_refs)) == len(schema_refs) == len(set(schema_refs)) == len(identities) == len(set(identities)) == 6, {"types":type_refs,"schemas":schema_refs,"identity_fields":identities})
    check("canonical-machine-generated-human", all(x["source_direction"]["canonical"] == "artifact.json" and x["source_direction"]["projection_policy"] == "generated-only" for x in artifacts), [x["source_direction"] for x in artifacts])
    check("all-types-candidate-non-effectful", all(x["status"] == "candidate-unadmitted" and x["authority_effect"] == "none" for x in artifacts), type_refs)

    suite = pack["conformance_suite"]
    suite_path = LAB / suite["path"]
    suite_receipt_path = LAB / suite["receipt_path"]
    suite_receipt = load(suite_receipt_path)
    check("aggregate-suite-current-pass", sha(suite_path) == suite["sha256"] and sha(suite_receipt_path) == suite["receipt_sha256"] and suite_receipt["result"] == "PASS", {"suite":sha(suite_path),"receipt":sha(suite_receipt_path),"result":suite_receipt["result"]})
    check("thirteen-hostile-fixtures-covered", sum(len(x["validation_contract"]["negative_witnesses"]) for x in artifacts) == 13, 13)
    check("four-progressive-layers-complete", [x["layer_id"] for x in pack["implementation_layers"]] == ["S2-L0","S2-L1","S2-L2","S2-L3"], [x["layer_id"] for x in pack["implementation_layers"]])
    check("s3-remains-blocked-on-admission", pack["recommended_next_stage"]["posture"] == "blocked-pending-s2-artifact-type-admission" and any("candidate-unadmitted" in x for x in pack["promotion_blockers"]), pack["promotion_blockers"])

    blocked = [x for x in checks if x["result"] == "BLOCK"]
    manifest = {
        "schema_version":"cyberalchemy-lab-cml07-s2-artifact-type-manifest/v1",
        "manifest_id":"CAL-CML07-S2-IDENTITY-ARTIFACT-TYPES-MANIFEST-0003",
        "status":"candidate-ready-for-review" if not blocked else "blocked",
        "authority_effect":"none",
        "pack_path":str(PACK_PATH.relative_to(LAB)),
        "pack_sha256":sha(PACK_PATH),
        "predecessor_decision":pack["predecessor_decision"],
        "selected_chain":pack["selected_chain"],
        "artifact_types":pack["artifact_types"],
        "conformance_suite":pack["conformance_suite"],
        "promotion_blockers":pack["promotion_blockers"],
        "claim_ceiling":"This manifest binds the exact S2 candidate cohort for review. It does not request or perform admission and does not authorize S3."
    }
    dump(ROOT / "manifest.json",manifest)
    receipt = {
        "schema_version":"cyberalchemy-lab-cml07-s2-artifact-type-pack-validation/v1",
        "subject":manifest["manifest_id"],
        "result":"PASS" if not blocked else "BLOCK",
        "authority_effect":"none",
        "assessment":{"validation_result":"PASS" if not blocked else "BLOCK","schema_and_artifact_type_contract_conformance":"PASS" if not blocked else "NOT_ESTABLISHED","artifact_type_admission":"not_evaluable-without-owner-decision","identity_contract_conformance":"not_evaluable-until-s3","implementation_conformance":"not_evaluable","runtime_conformance":"not_evaluable"},
        "checks":checks,
        "summary":{"passed":len(checks)-len(blocked),"blocked":len(blocked),"total":len(checks)},
        "materials":{"pack_sha256":sha(PACK_PATH),"manifest_sha256":sha(ROOT / "manifest.json"),"suite_receipt_sha256":sha(suite_receipt_path)},
        "claim_ceiling":pack["claim_ceiling"]
    }
    dump(ROOT / "receipts/validation.json",receipt)
    write(ROOT / "PACK.md",render_pack(pack,receipt))
    write(ROOT / "IMPLEMENTATION-LAYERING.md",render_layering(pack))
    print(f"CML07_S2_ARTIFACT_TYPE_PACK={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
