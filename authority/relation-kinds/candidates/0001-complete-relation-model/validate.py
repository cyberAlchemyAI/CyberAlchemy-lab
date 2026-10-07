#!/usr/bin/env python3
"""Validate the complete candidate Relation Kind model."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[4]
ROOT = Path(__file__).resolve().parent


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    model = load(ROOT / "model.json")
    examples = load(ROOT / "examples.json")
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    entries = model["entries"]
    ids = [item["relation_kind_id"] for item in entries]
    states = {state: sum(item["revision_state"] == state for item in entries) for state in ["migration-contract-preserved", "candidate-revised", "candidate-new"]}
    check("exact-complete-counts", len(ids) == 42 and len(set(ids)) == 42 and states == {"migration-contract-preserved": 20, "candidate-revised": 5, "candidate-new": 17}, {"total": len(ids), "states": states})

    check("examples-complete", set(examples) == set(ids) and all(examples[item]["relation_kind_ref"] == item and examples[item]["authority_effect"] == "none" for item in ids), {"examples": len(examples)})

    endpoint_results = []
    for item in entries:
        example = examples[item["relation_kind_id"]]
        qualifiers = set(example["qualifiers"])
        endpoint_results.append({
            "relation": item["relation_kind_id"],
            "source_kinds": bool(item["source_kinds"]), "target_kinds": bool(item["target_kinds"]),
            "required_qualifiers_present": set(item["required_qualifiers"]) <= qualifiers,
            "distinct_endpoints": example["source_ref"] != example["target_ref"],
            "evidence_present": bool(example["evidence_refs"]),
        })
    check("contracts-and-examples-coherent", all(all(value for key, value in row.items() if key != "relation") for row in endpoint_results), endpoint_results)

    revised = {item["relation_kind_id"]: item for item in entries if item["revision_state"] == "candidate-revised"}
    check(
        "five-endpoint-revisions-present",
        set(revised) == {"relation.belongs-to-product", "relation.belongs-to-project", "relation.uses-method", "relation.evaluates", "relation.instance-of"}
        and "context" in revised["relation.belongs-to-product"]["source_kinds"]
        and {"context", "research-run", "experiment-run"} <= set(revised["relation.belongs-to-project"]["source_kinds"])
        and {"measurement-result", "observation", "project", "product"} <= set(revised["relation.uses-method"]["source_kinds"])
        and {"experiment-design", "experiment-run"} <= set(revised["relation.evaluates"]["source_kinds"])
        and "capability-instance" in revised["relation.instance-of"]["source_kinds"],
        {key: {"sources": value["source_kinds"], "targets": value["target_kinds"]} for key, value in revised.items()},
    )

    required_new = {
        "relation.carries-definition", "relation.admits", "relation.contributes-to-product", "relation.addresses-inquiry", "relation.executes-design", "relation.advances-goal", "relation.answers-inquiry", "relation.tests-thesis-proposition", "relation.conforms-to", "relation.requests-resolution-of", "relation.fulfills-request", "relation.projects-context", "relation.contains", "relation.inherits-contract", "relation.claims-identifier-for", "relation.defines-responsibility", "relation.bounded-by-authority-claim",
    }
    check("normalized-new-set-exact", {item["relation_kind_id"] for item in entries if item["revision_state"] == "candidate-new"} == required_new, sorted(required_new))

    residue = model["repository_relation_residue"]
    check("repository-residue-resolved", len(residue) == 9 and all(item["disposition"] != "unresolved" and set(item["canonical"]) <= set(ids) for item in residue), residue)
    check("candidate-no-authority-effect", model["authority_effect"] == "none" and model["status"] == "candidate-complete-awaiting-owner-review", {"status": model["status"], "authority_effect": model["authority_effect"]})

    markdown = (ROOT / "RELATIONS.md").read_text(encoding="utf-8")
    check("human-surface-complete", all(f"`{item}`" in markdown and json.dumps(examples[item], indent=2, sort_keys=True) in markdown for item in ids), {"relations": len(ids), "examples": len(examples)})

    manifest = load(ROOT / "manifest.json")
    manifest_results = []
    for item in manifest["files"] + manifest["inputs"]:
        path = LAB / item["path"]
        manifest_results.append({"path": item["path"], "ok": path.is_file() and sha(path) == item["sha256"]})
    check("manifest-current", all(item["ok"] for item in manifest_results), manifest_results)

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    receipt = {
        "schema_version": "cyberalchemy-lab-complete-relation-model-validation/v1", "subject": model["model_id"],
        "result": "PASS" if not blocked else "BLOCK", "authority_effect": "none", "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"model_sha256": sha(ROOT / "model.json"), "examples_sha256": sha(ROOT / "examples.json"), "relations_markdown_sha256": sha(ROOT / "RELATIONS.md"), "manifest_sha256": sha(ROOT / "manifest.json")},
        "claim_ceiling": "PASS establishes a complete digest-bound candidate review surface for 42 normalized Relation Kinds. It does not admit Relation Kinds or relation instances.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(f"COMPLETE_RELATION_MODEL={receipt['result']} ({receipt['summary']['passed']}/{receipt['summary']['total']})")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
