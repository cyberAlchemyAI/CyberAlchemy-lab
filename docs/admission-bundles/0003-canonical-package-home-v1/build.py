#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
CORE = Path("/home/vrondelli/projects/domainspec-core")
DECISION_ID = "CAL-DECISION-0043-CANONICAL-PACKAGE-HOME-V1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_index(registry: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run the bound admission builder. -->",
        "", "# CyberAlchemy Lab Definition Index", "",
        f"- Status: `{registry['status']}`",
        f"- Admission decision: `{registry['admission_decision_ref']}`", "",
        "| ID | Version | Term | Lifecycle | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in registry["entries"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | `{item['lifecycle_state']}` | `{item['path']}` |")
    lines.extend(["", "## Current lookup", ""])
    lines.extend(f"- `{key}` -> `{value}`" for key, value in registry["current_lookup"].items())
    lines.extend(["", "## Claim ceiling", "", registry["claim_ceiling"]])
    return "\n".join(lines)


def render_drift(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit.json through its bound admission builder. -->",
        "", "# Canonical Package Home Definition Drift Audit", "",
        "> Post-admission explanatory projection; machine JSON is canonical.", "",
    ]
    for item in data["findings"]:
        lines.extend([f"## {item['finding_id']} — {item['status']}", "", item["condition"], "", f"Remediation: {item['remediation']}", ""])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_bundle(bundle: dict, manifest: dict, receipt: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit bundle.json and run build.py. -->", "",
        "# Canonical Package Home v1 admission bundle", "",
        f"- Bundle: `{bundle['bundle_id']}`",
        f"- Prospective decision: `{bundle['prospective_decision_id']}`",
        f"- Validation: `{receipt['result']}`", "",
        "## Authority-distinct requests", "",
    ]
    lines.extend(f"- `{x['request_id']}` — `{x['owner_role']}`: {x['requested_effect']}" for x in bundle["decision_requests"])
    lines.extend(["", "## Immutable boundary", "", f"- Manifest: `{sha(ROOT / 'manifest.json')}`", f"- Receipt: `{sha(ROOT / 'receipts/validation.json')}`", "", "## Claim ceiling", "", manifest["claim_ceiling"]])
    return "\n".join(lines)


def main() -> int:
    bundle = load(ROOT / "bundle.json")
    live = load(LAB / "authority/definitions/registry.json")
    candidate = load(LAB / "authority/definitions/candidates/0008-canonical-package-home/candidate.json")
    definition_path = LAB / candidate["definitions"][0]["path"]
    definition = load(definition_path)
    sources = load(LAB / "authority/decisions/source-admission/canonical-package-home/v1/admissions.json")
    checks = []
    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    bound = bundle["candidate_inputs"] + bundle["live_preimages"]
    observed = {x["path"]: sha(LAB / x["path"]) if (LAB / x["path"]).is_file() else "missing" for x in bound}
    check("all-bound-inputs-current", all(observed[x["path"]] == x["sha256"] for x in bound), observed)
    for rel in [
        "authority/decisions/source-admission/canonical-package-home/v1/receipts/validation.json",
        "authority/definitions/candidates/0008-canonical-package-home/receipts/validation.json",
    ]:
        receipt = load(LAB / rel)
        check(f"receipt-pass:{Path(rel).parent.parent.name}", receipt.get("result") == "PASS", {"path": rel, "result": receipt.get("result")})

    source_results = []
    for item in sources["admissions"]:
        path = CORE / item["source_path"]
        content = path.read_bytes()
        selected = b"".join(content.splitlines(keepends=True)[item["start_line"]-1:item["end_line"]])
        source_results.append({"id": item["admission_id"], "file": hashlib.sha256(content).hexdigest(), "selected": hashlib.sha256(selected).hexdigest(), "current": hashlib.sha256(content).hexdigest() == item["source_file_sha256_at_authoring"] and hashlib.sha256(selected).hexdigest() == item["selected_sha256"]})
    check("five-source-selections-current", len(source_results) == 5 and all(x["current"] for x in source_results), source_results)
    check("one-boundary-three-separate-requests", bundle["decision_boundary"]["mode"] == "single-checkpoint" and len({x["request_id"] for x in bundle["decision_requests"]}) == 3, [x["request_id"] for x in bundle["decision_requests"]])
    check("owners-bound-to-principal", sources["owner_principal_ref"] == bundle["decision_boundary"]["principal_ref"] == "person:<vrondelli>", bundle["decision_boundary"]["principal_ref"])

    registry = deepcopy(live)
    ref = f"{definition['definition_id']}@{definition['version']}"
    check("definition-not-already-current", definition["definition_id"] not in live["current_lookup"], definition["definition_id"])
    registry["entries"].append({
        "admission_decision_ref": DECISION_ID,
        "definition_id": definition["definition_id"],
        "lifecycle_state": "admitted",
        "path": candidate["definitions"][0]["path"],
        "sha256": sha(definition_path),
        "term": definition["term"],
        "version": definition["version"],
    })
    registry["entries"].sort(key=lambda x: (x["definition_id"], x["version"]))
    registry["current_lookup"][definition["definition_id"]] = ref
    registry["current_lookup"] = dict(sorted(registry["current_lookup"].items()))
    registry["status"] = "owner-admitted"
    registry["authority_effect"] = "thirty-three-exact-definition-versions-canonical"
    registry["admission_decision_ref"] = DECISION_ID
    registry["predecessor"] = {"path": "authority/definitions/registry.json", "sha256": bundle["live_preimages"][0]["sha256"], "entry_count": 32, "admission_decision_ref": live["admission_decision_ref"]}
    registry["source_direction"] = {"canonical": "registry.json", "human_projection": "DEFINITIONS-INDEX.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.canonical-package-home-admission/v1"}
    registry["claim_ceiling"] = "This registry admits exactly cal.definition.canonical-package-home@1.0.0-candidate.1 through CAL-DECISION-0043 while preserving all 32 predecessor versions. It does not admit an Artifact Type successor or select a package home for Registry Context."
    keys = [(x["definition_id"], x["version"]) for x in registry["entries"]]
    check("registry-33-versions-31-current-terms", len(keys) == len(set(keys)) == 33 and len(registry["current_lookup"]) == 31, {"versions": len(keys), "current": len(registry["current_lookup"])})

    post = ROOT / "postimages/authority/definitions"
    dump(post / "registry.json", registry)
    write(post / "DEFINITIONS-INDEX.md", render_index(registry))
    drift = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit/v1",
        "record_id": "CAL-DEFINITION-DRIFT-AUDIT-CANONICAL-PACKAGE-HOME-V1",
        "artifact_type_ref": "cal.artifact-type.drift-audit/v1",
        "status": "current-evidence",
        "authority_effect": "definition-drift-evidence-only",
        "owner_ref": "role:evidence-conformance-owner",
        "registry_ref": "authority/definitions/registry.json",
        "registry_sha256": sha(post / "registry.json"),
        "admission_decision_ref": DECISION_ID,
        "findings": [
            {"finding_id": "CPH-POST-001", "severity": "resolved", "status": "admitted", "target": ref, "condition": "The canonical package-home selection rule is now an admitted current Definition.", "remediation": "Use the admitted Definition as the semantic predecessor for successor Artifact Types and migration candidates."},
            {"finding_id": "CPH-POST-002", "severity": "successor-residue", "status": "open", "target": "cal.artifact-type.capability-instance/successor", "condition": "The admitted Capability Instance Artifact Type does not yet require explicit package-home, lifecycle-owner, and unit-of-change references.", "remediation": "Author and test a successor Artifact Type; do not rewrite v1."},
            {"finding_id": "CPH-POST-003", "severity": "migration-residue", "status": "open", "target": "migration:registry-context", "condition": "No Registry Context canonical package has yet been selected or migrated.", "remediation": "Author the source- and rollback-bound Registry Context migration after Artifact Type enforcement is testable."}
        ],
        "summary": {"definition_versions": 33, "current_definition_terms": 31, "new_definitions_admitted": 1, "source_selections_admitted_for_use": 5, "artifact_type_successor": "not_authored", "registry_context_migration": "not_started"},
        "source_direction": {"canonical": "drift-audit.json", "human_projection": "DEFINITION-DRIFT-AUDIT.md", "projection_policy": "generated-only", "generator_ref": "cal.generator.canonical-package-home-admission/v1"},
        "claim_ceiling": "This audit proves only the current Definition registry and named successor residue. It does not establish Artifact Type conformance or migrate Registry Context."
    }
    dump(post / "drift-audit.json", drift)
    write(post / "DEFINITION-DRIFT-AUDIT.md", render_drift(drift))
    check("four-postimages-complete", all((ROOT / x).is_file() for x in bundle["postimages"]), bundle["postimages"])

    blocked = [x for x in checks if x["result"] == "BLOCK"]
    manifest = {
        "schema_version": "cyberalchemy-lab-definition-admission-manifest/v1",
        "manifest_id": "CAL-CANONICAL-PACKAGE-HOME-V1-ADMISSION-MANIFEST",
        "status": "candidate-ready-for-bound-decision" if not blocked else "blocked",
        "authority_effect": "none",
        "bundle_path": "docs/admission-bundles/0003-canonical-package-home-v1/bundle.json",
        "bundle_sha256": sha(ROOT / "bundle.json"),
        "prospective_decision_id": DECISION_ID,
        "decision_boundary": bundle["decision_boundary"],
        "decision_requests": bundle["decision_requests"],
        "candidate_inputs": bundle["candidate_inputs"],
        "live_preimages": bundle["live_preimages"],
        "postimages": [{"path": x, "sha256": sha(ROOT / x)} for x in bundle["postimages"]],
        "rollback_policy": bundle["rollback_policy"],
        "excluded_effects": bundle["excluded_effects"],
        "claim_ceiling": "This immutable manifest binds five source selections, one Definition, and four postimages. It has no effect until the exact user-selected transaction succeeds."
    }
    dump(ROOT / "manifest.json", manifest)
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-admission-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "promotion_eligibility": "selected-by-explicit-user-instruction" if not blocked else "blocked",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks)-len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"bundle_sha256": sha(ROOT / "bundle.json"), "manifest_sha256": sha(ROOT / "manifest.json")},
        "claim_ceiling": "PASS proves exact current inputs, source selections, candidate receipts, and deterministic postimages only. It does not itself admit or publish anything."
    }
    dump(ROOT / "receipts/validation.json", receipt)
    write(ROOT / "BUNDLE.md", render_bundle(bundle, manifest, receipt))
    print(f"CANONICAL_PACKAGE_HOME_ADMISSION_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={sha(ROOT / 'manifest.json')}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
