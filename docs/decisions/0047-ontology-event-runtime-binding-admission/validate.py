#!/usr/bin/env python3
"""Collect-all, non-effectful preacceptance for binding admission 0047."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
REFS = {
  "subject": {
    "path": "implementation/bindings/ontology-product-event-runtime/v2/binding.json",
    "sha256": "28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d"
  },
  "product": {
    "path": "product/products/ontology/v1/candidates/0006-event-runtime-realization/candidate.json",
    "sha256": "5ebe011a083babcc383ca9ec0ea341be8448e18db65911a1a54d55dcf1e5860c"
  },
  "product_test": {
    "path": "product/products/ontology/v1/candidates/0006-event-runtime-realization/receipts/validation.json",
    "sha256": "a9aba1894ae529e39dd532ff6bd23016f9c9c38381023fa985821061522d8a95"
  },
  "product_approval": {
    "path": "docs/decisions/0046-ontology-event-runtime-product-approval/decision.json",
    "sha256": "c4cd18361c2413994feee9da83e4184649efb2129fabeb5258beead1cb789498"
  },
  "approval_validation": {
    "path": "docs/decisions/0046-ontology-event-runtime-product-approval/receipts/decision-validation.json",
    "sha256": "d5997bd3a147402b926e7a5baa483d6bf6caa2ff9cbfb4f1dfa5ac5bcd1aad4b"
  }
}
EXCLUDED = ["runtime-adoption","runtime-activation","child-ontology-admission","repository-enforcement","migration","cutover","publication","release","deployment","source-retirement","external-effects"]
PROPOSAL = {"option_id":"EVRT-BADM-1","owner_gate":"G-CAL-ONTOLOGY-EVENT-RUNTIME-BINDING-ADMISSION","effect":"implementation-binding-admission-only","meaning":"Recognize the exact tested binding as an implementation bridge for Ontology Product candidate 0006, scoped to the frozen 14-node and 15-relation navigation input and the exact Rust source.","record_policy":"Record admission in a separate owner decision; preserve the frozen binding and Product candidate."}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def semantic_errors(candidate):
    errors = []
    for key, value in [("schema_version", "cal-event-runtime-binding-admission-candidate/v1"), ("candidate_id", "CAL-EVENT-RUNTIME-BINDING-ADMISSION-CANDIDATE-0047"), ("status", "prepared-for-review"), ("authority_effect", "none")]:
        if candidate.get(key) != value:
            errors.append(key)
    for key, ref in REFS.items():
        if any(candidate.get(key, {}).get(field) != expected for field, expected in ref.items()):
            errors.append(key)
    if candidate.get("subject", {}).get("binding_id") != "cal.binding.ontology-product-event-runtime/v2":
        errors.append("binding-identity")
    if candidate.get("proposed_decision") != PROPOSAL:
        errors.append("proposed-effect")
    if candidate.get("excluded_effects") != EXCLUDED:
        errors.append("excluded-effects")
    return errors

def validate(candidate):
    checks = []
    def check(name, fn, dependencies=()):
        if any(next(c for c in checks if c["id"] == dep)["result"] != "PASS" for dep in dependencies):
            checks.append({"id": name, "result": "not_evaluable", "detail": list(dependencies)})
            return
        try:
            detail = fn()
            checks.append({"id": name, "result": "PASS", "detail": detail})
        except Exception as exc:
            checks.append({"id": name, "result": "BLOCK", "detail": str(exc)})
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    def semantics():
        errors = semantic_errors(candidate)
        require(not errors, str(errors))
        return "Exact identity, proposed effect and exclusions"
    check("candidate-contract", semantics)
    def sources():
        bad = [key for key, ref in REFS.items() if not (LAB / ref["path"]).is_file() or sha(LAB / ref["path"]) != ref["sha256"]]
        require(not bad, str(bad))
        return list(REFS)
    check("exact-sources", sources)
    def closure():
        product = load(LAB / REFS["product"]["path"])
        receipt = load(LAB / REFS["approval_validation"]["path"])
        approval = load(LAB / REFS["product_approval"]["path"])
        binding = load(LAB / REFS["subject"]["path"])
        require(approval["product_approval"]["state"] == "approved", "Product not approved")
        require(approval["subject"]["product_candidate_sha256"] == REFS["product"]["sha256"], "Wrong approved Product")
        require(approval["subject"]["binding_sha256"] == REFS["subject"]["sha256"], "Wrong approved binding")
        require(receipt["result"] == "PASS" and receipt["stage_state"] == "PRODUCT_APPROVED", "Approval evidence fails")
        require(binding["runtime_source"]["adopted"] is False, "Unexpected adoption")
        material = product["acceptance_material"] + binding["implementation_material"] + receipt["inputs"]
        bad = [r["path"] for r in material if not (LAB / r["path"]).is_file() or sha(LAB / r["path"]) != r["sha256"]]
        require(not bad, str(bad))
        return {"verified_references": len(material)}
    check("approval-and-material-closure", closure, ("exact-sources",))
    def replay():
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        validator = LAB / REFS["product"]["path"]
        run = subprocess.run(["python3", str(validator.with_name("validate.py"))], cwd=LAB, env=env, capture_output=True, text=True, timeout=300)
        require(run.returncode == 0, run.stdout + run.stderr)
        fresh = json.loads(run.stdout)
        require(fresh == load(LAB / REFS["product_test"]["path"]), "Current Product test differs from frozen receipt")
        return {"rust_tests_per_run": fresh["rust_test_cases"], "runs": fresh["deterministic_rust_runs"], "validator_tests": fresh["candidate_validator_tests"]}
    check("current-product-tests", replay, ("candidate-contract", "approval-and-material-closure"))
    def probes():
        mutations = []
        x = copy.deepcopy(candidate); x["authority_effect"] = "admit"; mutations.append(x)
        x = copy.deepcopy(candidate); x["subject"]["sha256"] = "0"*64; mutations.append(x)
        x = copy.deepcopy(candidate); x["proposed_decision"]["effect"] = "runtime-adoption"; mutations.append(x)
        x = copy.deepcopy(candidate); x["excluded_effects"] = []; mutations.append(x)
        x = copy.deepcopy(candidate); del x["product_approval"]; mutations.append(x)
        x = copy.deepcopy(candidate); x["proposed_decision"]["owner_gate"] = ""; mutations.append(x)
        require(all(semantic_errors(x) for x in mutations), "Hostile mutation escaped")
        return {"rejected_mutations": len(mutations)}
    check("hostile-contract-probes", probes)
    result = "PASS" if all(c["result"] == "PASS" for c in checks) else "BLOCK"
    return {"schema_version": "cal-event-runtime-binding-admission-preacceptance/v1", "result": result,
            "candidate_sha256": sha(ROOT / "candidate.json"), "checks": checks,
            "review_eligible": result == "PASS", "authority_effect": "none",
            "binding_admitted": False, "runtime_adopted": False,
            "inputs": [{"path": str(p.relative_to(LAB)), "sha256": sha(p)} for p in [ROOT / "candidate.json", ROOT / "validate.py", ROOT / "README.md"]]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate(load(ROOT / "candidate.json"))
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write_receipt:
        path = ROOT / "receipts/preacceptance.json"
        path.parent.mkdir(exist_ok=True)
        if path.exists() and path.read_text() != encoded:
            raise ValueError("Preserve existing receipt; use a successor epoch")
        if not path.exists():
            with path.open("x") as handle:
                handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt["result"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
