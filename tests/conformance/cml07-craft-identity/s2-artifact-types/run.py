#!/usr/bin/env python3
"""Run the aggregate CML-07 S2 Artifact Type conformance suite."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SUITE_PATH = ROOT / "suite.json"
RECEIPT_PATH = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(suite: dict[str, Any], receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical suite is suite.json; result is receipts/validation.json. -->",
        "",
        "# CML-07 S2 Identity Artifact Type Conformance",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        f"- Subjects: `{len(suite['subjects'])}`",
        f"- Hostile fixtures: `{sum(x['negative_witness_count'] for x in suite['subjects'])}`",
        "",
        "## Subjects",
        "",
    ]
    for subject in suite["subjects"]:
        lines.append(f"- `{subject['artifact_type_ref']}` — identity field `{subject['identity_field']}`")
    lines.extend(["", "## Cohort invariants", ""])
    for item in suite["cohort_invariants"]:
        lines.append(f"- **{item['invariant_id']}**: {item['statement']}")
    lines.extend(["", "## Claim ceiling", "", suite["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    suite = load(SUITE_PATH)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    predecessor = LAB / suite["predecessor_decision"]["path"]
    decision = load(predecessor)
    check("s2-predecessor-admitted-current", sha(predecessor) == suite["predecessor_decision"]["sha256"] and decision["status"] == "owner-admitted" and decision["admission_result"]["s2_posture"] == suite["predecessor_decision"]["required_s2_posture"], {"sha256": sha(predecessor), "status": decision["status"], "s2_posture": decision["admission_result"]["s2_posture"]})

    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    executions = []
    artifacts = []
    receipts = []
    for subject in suite["subjects"]:
        artifact_path = LAB / subject["artifact_path"]
        validator_path = LAB / subject["validator_path"]
        run = subprocess.run([sys.executable, str(validator_path)], cwd=LAB, env=environment, text=True, capture_output=True)
        executions.append({"artifact_type_ref": subject["artifact_type_ref"], "returncode": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr.strip()})
        artifacts.append(load(artifact_path))
        receipts.append(load(LAB / subject["receipt_path"]))
    check("six-validators-pass", len(executions) == 6 and all(x["returncode"] == 0 for x in executions), executions)
    check("six-validation-receipts-pass", len(receipts) == 6 and all(x["result"] == "PASS" for x in receipts), [{"subject": x["subject"], "result": x["result"]} for x in receipts])

    type_refs = [x["artifact_type_ref"] for x in artifacts]
    type_ids = [x["artifact_type_id"] for x in artifacts]
    schema_refs = [x["schema_ref"] for x in artifacts]
    identity_fields = [x["instance_contract"]["identity_field"] for x in artifacts]
    check("six-orthogonal-type-identities", len(type_refs) == len(set(type_refs)) == len(type_ids) == len(set(type_ids)) == 6, type_refs)
    check("six-orthogonal-schema-identities", len(schema_refs) == len(set(schema_refs)) == 6, schema_refs)
    check("six-orthogonal-instance-identity-fields", len(identity_fields) == len(set(identity_fields)) == 6, identity_fields)
    check("suite-subjects-match-artifacts", type_refs == [x["artifact_type_ref"] for x in suite["subjects"]] and identity_fields == [x["identity_field"] for x in suite["subjects"]], {"types": type_refs, "identity_fields": identity_fields})

    registry = load(LAB / "authority/definitions/registry.json")
    admitted_refs = {f"{x['definition_id']}@{x['version']}" for x in registry["entries"] if x["lifecycle_state"] == "admitted"}
    check("all-semantic-definitions-admitted", all(set(x["semantic_definition_refs"]) <= admitted_refs and all(b["admission_posture"] == "admitted" for b in x["semantic_definition_bindings"]) for x in artifacts), sorted(set().union(*(set(x["semantic_definition_refs"]) for x in artifacts))))
    check("all-registered-under-artifact-type-v2", all(x["classification"]["artifact_type_ref"] == "cal.artifact-type.artifact-type/v2" and x["artifact_type_root_binding"]["admission_decision_ref"] == decision["decision_id"] for x in artifacts), [x["classification"] for x in artifacts])
    check("machine-canonical-human-generated", all(x["source_direction"]["canonical"] == "artifact.json" and x["source_direction"]["human_projection"] == "ARTIFACT.md" and x["source_direction"]["projection_policy"] == "generated-only" for x in artifacts), [x["source_direction"] for x in artifacts])

    schemas = {x["artifact_type_id"]: load(LAB / subject["schema_path"]) for x, subject in zip(artifacts, suite["subjects"])}
    check("all-schemas-closed", all(x.get("additionalProperties") is False for x in schemas.values()), list(schemas))
    check("relations-localized-to-relation-carriers", "relations" not in schemas["cal.artifact-type.product-identity"]["properties"] and "relations" not in schemas["cal.artifact-type.project-identity"]["properties"] and "relations" not in schemas["cal.artifact-type.goal"]["properties"] and {"nodes","relations"} <= set(schemas["cal.artifact-type.identity-graph"]["properties"]) and {"method_ref","subject_ref"} <= set(schemas["cal.artifact-type.method-binding"]["properties"]), "cross-identity relations exist only in Method Binding and Identity Graph contracts")
    check("product-project-goal-non-collapse", "project_id" not in schemas["cal.artifact-type.product-identity"]["properties"] and "product_id" not in schemas["cal.artifact-type.project-identity"]["properties"] and "project_id" not in schemas["cal.artifact-type.goal"]["properties"] and "product_id" not in schemas["cal.artifact-type.goal"]["properties"], "independent canonical axes preserved")

    hostile_expected = sum(x["negative_witness_count"] for x in suite["subjects"])
    hostile_observed = sum(len(x["validation_contract"]["negative_witnesses"]) for x in artifacts)
    hostile_receipt_results = [
        check_item
        for receipt in receipts
        for check_item in receipt["checks"]
        if check_item["check_id"] == "hostile-fixtures-rejected" and check_item["result"] == "PASS"
    ]
    check("thirteen-hostile-fixtures-rejected", hostile_expected == hostile_observed == 13 and len(hostile_receipt_results) == 6, {"expected": hostile_expected, "observed": hostile_observed, "passing_type_checks": len(hostile_receipt_results)})
    check("conformance-scopes-separated", all(x["assessment"] == {"validation_result":"PASS","schema_conformance":"PASS","admission_posture":"candidate-unadmitted","implementation_conformance":"not_evaluable","runtime_conformance":"not_evaluable"} for x in receipts), [x["assessment"] for x in receipts])
    check("cohort-remains-non-effectful", suite["status"] == "candidate-evidence" and suite["authority_effect"] == "none" and all(x["status"] == "candidate-unadmitted" and x["authority_effect"] == "none" for x in artifacts), suite["excluded_effects"])

    blocked = [x for x in checks if x["result"] == "BLOCK"]
    receipt = {
        "schema_version":"cyberalchemy-lab-cml07-s2-conformance-receipt/v1",
        "subject":suite["suite_id"],
        "result":"PASS" if not blocked else "BLOCK",
        "authority_effect":"none",
        "assessment":{"validation_result":"PASS" if not blocked else "BLOCK","schema_and_artifact_type_contract_conformance":"PASS" if not blocked else "NOT_ESTABLISHED","artifact_type_admission":"not_evaluable-without-owner-decision","identity_contract_conformance":"not_evaluable-until-s3","implementation_conformance":"not_evaluable","runtime_conformance":"not_evaluable"},
        "checks":checks,
        "summary":{"passed":len(checks)-len(blocked),"blocked":len(blocked),"total":len(checks)},
        "materials":{
            "suite_sha256":sha(SUITE_PATH),
            "subjects":[{"artifact_type_ref":a["artifact_type_ref"],"artifact_sha256":sha(LAB / s["artifact_path"]),"schema_sha256":sha(LAB / s["schema_path"]),"receipt_sha256":sha(LAB / s["receipt_path"])} for a,s in zip(artifacts,suite["subjects"])]
        },
        "claim_ceiling":suite["claim_ceiling"]
    }
    RECEIPT_PATH.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (ROOT / "SUITE.md").write_text(render(suite,receipt),encoding="utf-8")
    print(f"CML07_S2_CONFORMANCE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
