#!/usr/bin/env python3
"""Collect-all validation for the CML-07 W0 source, owner, and Definition candidates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")
ADMISSIONS = LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json"
OWNERS = LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owner-bindings.json"
CHAIN = LAB / "docs/identity-packs/0001-craft-identity-chain/chain.json"
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected(path: Path, item: dict) -> bytes:
    if item["selector_kind"] == "whole-file-v1":
        return path.read_bytes()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(lines[item["start_line"] - 1:item["end_line"]]).encode()


def hostile(subject: dict) -> set[str]:
    failures: set[str] = set()
    if subject.get("kind") == "identity-carrier" and subject.get("inferred_identity") is True:
        failures.add("directory-must-not-infer-identity")
    if subject.get("kind") == "identity-relation" and subject.get("merges_endpoints") is True:
        failures.add("relation-must-not-merge-endpoints")
    if subject.get("kind") == "owner-bindings" and subject.get("merges_role_scopes") is True:
        failures.add("shared-principal-must-not-merge-roles")
    return failures


def main() -> int:
    tools = ROOT.parent / "_candidate_pack.py"
    spec = importlib.util.spec_from_file_location("candidate_pack", tools)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.hostile_failures = hostile
    expected = {"cal.definition.product", "CAV2-D32", "CAV2-D20", "CAV2-D59", "CAV2-D60", "cal.definition.identity-relation"}
    base = module.validate(ROOT, expected)
    receipt = load(RECEIPT)
    admissions = load(ADMISSIONS)
    owners = load(OWNERS)
    chain = load(CHAIN)
    checks = receipt["checks"]

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    actual_sources = []
    for item in admissions["admissions"]:
        actual = hashlib.sha256(selected(SOURCE / item["source_path"], item)).hexdigest()
        actual_sources.append({"id": item["admission_id"], "expected": item["selected_sha256"], "actual": actual})
    check("eight-source-selectors-current", len(actual_sources) == 8 and all(x["expected"] == x["actual"] for x in actual_sources), actual_sources)
    chain_sources = {(x["source_id"], x["sha256"]) for x in chain["external_source_selectors"]}
    admission_sources = set()
    id_map = {"CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-CAV2-D20":"CAV2-D20","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-CAV2-D32":"CAV2-D32","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-CAV2-D59":"CAV2-D59","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-CAV2-D60":"CAV2-D60","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-PRODUCT":"CA2-PRODUCT-CRAFT","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-DECISION":"CA2-DECISION-CRAFT-IDENTITY-003","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-PROJECT":"CA2-PROJECT-CRAFT","CAL-SOURCE-ADMISSION-CRAFT-IDENTITY-GOAL":"CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION"}
    for item in admissions["admissions"]:
        admission_sources.add((id_map[item["admission_id"]], item["selected_sha256"]))
    check("source-admissions-match-chain", admission_sources == chain_sources, {"chain": sorted(chain_sources), "candidate": sorted(admission_sources)})
    check("source-candidate-no-effect", admissions["status"] == "candidate-unadmitted" and admissions["authority_effect"].startswith("none"), admissions["authority_effect"])

    predecessor = LAB / owners["predecessor_registry"]["path"]
    decision = LAB / owners["predecessor_registry"]["admission_decision_path"]
    check("owner-predecessors-current", sha(predecessor) == owners["predecessor_registry"]["sha256"] and sha(decision) == owners["predecessor_registry"]["admission_decision_sha256"], {"owner_registry": sha(predecessor), "decision": sha(decision)})
    roles = [owners["preserved_required_role"]["role_id"]] + [x["role_id"] for x in owners["assignments"]]
    scopes = [x["scope"] for x in owners["assignments"]]
    check("five-required-owner-roles-distinct", roles == chain["stages"][0]["required_roles"] and len(set(roles)) == 5, roles)
    check("shared-principal-does-not-collapse-scopes", len(set(scopes)) == 4 and all(x["decision_separation"] == "required" for x in owners["assignments"]), scopes)
    check("owner-candidate-no-effect", owners["status"] == "candidate-unadmitted" and owners["authority_effect"] == "none", owners["authority_effect"])

    source_md = ADMISSIONS.with_name("SOURCE-ADMISSIONS.md")
    owner_md = OWNERS.with_name("OWNER-BINDINGS.md")
    build_spec = importlib.util.spec_from_file_location("cml07_build", ROOT / "build.py")
    build_module = importlib.util.module_from_spec(build_spec)
    assert build_spec and build_spec.loader
    build_spec.loader.exec_module(build_module)
    check("source-projection-parity", source_md.read_text(encoding="utf-8") == build_module.render_admissions(admissions).rstrip() + "\n", sha(source_md))
    check("owner-projection-parity", owner_md.read_text(encoding="utf-8") == build_module.render_owners(owners).rstrip() + "\n", sha(owner_md))
    check("live-registry-still-preimage", sha(LAB / "authority/definitions/registry.json") == "4210c3f0805a904480e7a0c92c366612e3c3ba563ba354245c6151e4a9d96d3d", sha(LAB / "authority/definitions/registry.json"))

    failed = [x for x in checks if x["result"] == "FAIL"]
    receipt["result"] = "PASS" if not failed else "FAIL"
    receipt["promotion_eligibility"] = "blocked-by-declared-dependencies" if not failed else "not-eligible"
    receipt["summary"] = {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)}
    receipt["materials"]["source_admissions_sha256"] = sha(ADMISSIONS)
    receipt["materials"]["owner_bindings_sha256"] = sha(OWNERS)
    receipt["materials"]["construction_chain_sha256"] = sha(CHAIN)
    receipt["claim_ceiling"] = "PASS proves the six Definition candidates are schema-valid, the eight source selectors are current, five owner roles remain distinct, projections are deterministic, and the live registry is unchanged. It does not admit a source, activate an owner, admit a Definition, or authorize any successor."
    dump(RECEIPT, receipt)
    print(f"CML07_W0_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if not failed and base == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
