#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    model = load(ROOT / "model.json")
    checks = []

    def check(check_id: str, passed: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "BLOCK", "detail": detail})

    predecessor = model["predecessor"]
    check("predecessor-current", sha(LAB / predecessor["path"]) == predecessor["sha256"], predecessor)
    entries = model["entries"]
    ids = [entry["relation_kind_id"] for entry in entries]
    axes = [entry["axis_id"] for entry in entries]
    questions = [entry["unique_question"] for entry in entries]
    check("41-orthogonal-axes", len(ids) == len(set(ids)) == len(set(axes)) == len(set(questions)) == 41, {"relations": len(ids), "axes": len(set(axes)), "questions": len(set(questions))})
    pair_checks = []
    for entry in entries:
        pairs = [(p["source_kind"], p["target_kind"]) for p in entry["allowed_endpoint_pairs"]]
        pair_checks.append({
            "relation_kind_id": entry["relation_kind_id"],
            "nonempty": bool(pairs),
            "unique": len(pairs) == len(set(pairs)),
            "no_wildcards": all("*" not in value for pair in pairs for value in pair),
            "projections": entry["source_kinds"] == sorted({p[0] for p in pairs}) and entry["target_kinds"] == sorted({p[1] for p in pairs}),
        })
    check("closed-explicit-pairs", all(all(value for key, value in row.items() if key != "relation_kind_id") for row in pair_checks), pair_checks)
    extensions = model["connection_extensions"]
    check("extension-rule-gates", len(extensions) == 4 and all(item["added_pairs"] and item["unique_question"] and item["required_qualifier_axes"] and item["forbidden_inferences"] and item["lifecycle_rule"] for item in extensions), extensions)
    by_id = {entry["relation_kind_id"]: entry for entry in entries}
    materializes = by_id["relation.materializes-consequence"]
    expected_targets = {"generated-output", "project-governance-event-history", "project-semantic-event-history", "project-state"}
    check("materialization-axis-closed", materializes["source_kinds"] == ["admission-transaction"] and set(materializes["target_kinds"]) == expected_targets, materializes)
    assessment = model["non_collapse_assessment"]
    check("no-collapse", len(assessment) == 3 and {item["right"] for item in assessment} == {"relation.produces", "relation.declares-effect-on", "payload references"}, assessment)
    new_kinds = {"admission-transaction", "authority-boundary", "decision-bundle", "decision-checkpoint", "user-decision-preference", "workflow-decision-profile"}
    role_kinds = {kind for entry in entries for pair in entry["allowed_endpoint_pairs"] for kind in pair.values()}
    check("new-carriers-have-typed-roles", new_kinds <= role_kinds, sorted(new_kinds - role_kinds))
    manifest = load(ROOT / "relation-kind-successor-manifest.json")
    relation_schema = load(LAB / "authority/artifact-types/relation-kind/v2/schema.json")
    instance_results = []
    for item in manifest["entries"]:
        instance = load(LAB / item["path"])
        errors = [error.message for error in jsonschema.Draft202012Validator(relation_schema).iter_errors(instance)]
        entry = by_id[item["relation_kind_id"]]
        instance_results.append({"relation_kind_id": item["relation_kind_id"], "schema_valid": not errors, "digest_current": sha(LAB / item["path"]) == item["sha256"], "pairs_exact": instance["payload"]["allowed_endpoint_pairs"] == entry["allowed_endpoint_pairs"], "errors": errors})
    check("relation-kind-instances", len(instance_results) == 4 and all(item["schema_valid"] and item["digest_current"] and item["pairs_exact"] for item in instance_results), instance_results)
    before = [(ROOT / name).read_bytes() for name in ("model.json", "MODEL.md", "relation-kind-successor-manifest.json")]
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    after = [(ROOT / name).read_bytes() for name in ("model.json", "MODEL.md", "relation-kind-successor-manifest.json")]
    check("deterministic", before == after, {"model_sha256": sha(ROOT / "model.json"), "projection_sha256": sha(ROOT / "MODEL.md")})
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-governance-transaction-relation-validation/v1",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {"model_sha256": sha(ROOT / "model.json"), "projection_sha256": sha(ROOT / "MODEL.md"), "relation_kind_manifest_sha256": sha(ROOT / "relation-kind-successor-manifest.json")},
        "claim_ceiling": "PASS establishes a closed candidate relation extension and its no-collapse distinctions. It admits no relation or endpoint pair.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
