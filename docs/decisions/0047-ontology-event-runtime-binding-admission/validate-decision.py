#!/usr/bin/env python3
"""Verify the exact user-authorized decision; validation grants no new effects."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
EXPECTED = json.loads("{\"schema_version\":\"cal-event-runtime-binding-admission-decision/v1\",\"decision_id\":\"CAL-EVENT-RUNTIME-BINDING-ADMISSION-0047\",\"gate_id\":\"G-CAL-ONTOLOGY-EVENT-RUNTIME-BINDING-ADMISSION\",\"decided_at\":\"2026-09-06T04:34:37Z\",\"decision_source\":{\"kind\":\"explicit-user-authorization\",\"verbatim\":\"authorized\",\"resolution_basis\":\"User authorized EVRT-BADM-1 immediately after presentation of candidate 0047 and its binding-only admission scope.\"},\"selected_option\":\"EVRT-BADM-1\",\"status\":\"admitted\",\"authority_effect\":\"implementation-binding-admission-only\",\"subject\":{\"binding_id\":\"cal.binding.ontology-product-event-runtime/v2\",\"path\":\"implementation/bindings/ontology-product-event-runtime/v2/binding.json\",\"sha256\":\"28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d\"},\"references\":{\"candidate\":{\"path\":\"candidate.json\",\"sha256\":\"ca3e2c381c7f5bc1c7a51d004c035161d92f76430e19b9224928d23936375867\"},\"preacceptance\":{\"path\":\"receipts/preacceptance.json\",\"sha256\":\"b321cf6cafbcf6f743a88fe31298343118c58ccda6a0347b15b8e15024a13af6\"},\"request\":{\"path\":\"admissibility-request.json\",\"sha256\":\"e4b19da1cd41ad24210244b1c181a8639c09ad2adfe68bcf87fa42717d173ebd\"},\"admissibility\":{\"path\":\"receipts/admissibility.json\",\"sha256\":\"a840da48dd79064f842c79464d928a18a039a9a3f8ea7159aae2aab70bb89409\"}},\"scope\":\"Recognize this exact binding as an implementation bridge for approved Ontology Product candidate 0006, scoped to the frozen 14-node and 15-relation navigation input and exact Rust source.\",\"excluded_effects\":[\"runtime-adoption\",\"runtime-activation\",\"child-ontology-admission\",\"repository-enforcement\",\"migration\",\"cutover\",\"publication\",\"release\",\"deployment\",\"source-retirement\",\"external-effects\"],\"limitations_preserved_from\":\"candidate.json#/limitations\",\"next_frontier\":\"Runtime adoption preparation; any adoption or activation requires its separate owner decision.\",\"work_lane\":\"operational support: implementation-binding admission\",\"record_policy\":\"This external decision supplies admission status. The frozen binding and Product candidate remain unchanged.\"}")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def semantic_errors(document):
    # Closed exact decision envelope, including all excluded effects.
    return [key for key in sorted(set(document) | set(EXPECTED))
            if document.get(key) != EXPECTED.get(key) or key not in document or key not in EXPECTED]

def validate():
    checks = []
    def check(name, action, deps=()):
        if any(next(x for x in checks if x["id"] == dep)["result"] != "PASS" for dep in deps):
            checks.append({"id": name, "result": "not_evaluable", "detail": list(deps)})
            return
        try:
            detail = action()
            checks.append({"id": name, "result": "PASS", "detail": detail})
        except Exception as exc:
            checks.append({"id": name, "result": "BLOCK", "detail": str(exc)})

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    def decision():
        errors = semantic_errors(load(ROOT / "decision.json"))
        require(not errors, str(errors))
        return "Exact authorized option, subject and effect ceiling"
    check("decision-envelope", decision)

    def sources():
        bad = [key for key, ref in EXPECTED["references"].items()
               if not (ROOT / ref["path"]).is_file() or sha(ROOT / ref["path"]) != ref["sha256"]]
        subject = EXPECTED["subject"]
        if not (LAB / subject["path"]).is_file() or sha(LAB / subject["path"]) != subject["sha256"]:
            bad.append("binding")
        require(not bad, str(bad))
        receipt = load(ROOT / "receipts/preacceptance.json")
        for ref in receipt["inputs"]:
            require((LAB / ref["path"]).is_file() and sha(LAB / ref["path"]) == ref["sha256"], "Preacceptance input drift: " + ref["path"])
        return "Candidate, preacceptance, request, admissibility and binding current"
    check("exact-evidence", sources)

    def gate():
        request = load(ROOT / "admissibility-request.json")
        receipt = load(ROOT / "receipts/admissibility.json")
        digest = hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        require(receipt["requestDigest"] == digest, "Admissibility request digest mismatch")
        require(request["decisionId"] == receipt["decisionId"] == EXPECTED["decision_id"], "Wrong decision")
        require(receipt["routeOutcome"] == "gate" and EXPECTED["selected_option"] in receipt["admissibleOptionIds"], "Option not admissible")
        selected = next(x for x in request["candidates"] if x["optionId"] == EXPECTED["selected_option"])
        require(selected["ownerGate"] == EXPECTED["gate_id"] and selected["structuralStatus"] == "admissible", "Wrong owner gate")
        return EXPECTED["selected_option"]
    check("owner-gate-selection", gate, ("exact-evidence",))

    def current():
        run = subprocess.run(["python3", str(ROOT / "validate.py")], cwd=LAB,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                             capture_output=True, text=True, timeout=300)
        require(run.returncode == 0, run.stdout + run.stderr)
        fresh = json.loads(run.stdout)
        require(fresh == load(ROOT / "receipts/preacceptance.json"), "Fresh preacceptance differs from reviewed evidence")
        return {"result": fresh["result"], "checks": len(fresh["checks"])}
    check("fresh-preacceptance", current, ("decision-envelope", "exact-evidence", "owner-gate-selection"))

    def probes():
        variants = []
        for key, value in [("selected_option", "EVRT-BADM-2"), ("authority_effect", "runtime-adoption"),
                           ("excluded_effects", []), ("status", "active")]:
            x = copy.deepcopy(EXPECTED); x[key] = value; variants.append(x)
        x = copy.deepcopy(EXPECTED); del x["decision_source"]; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["subject"]["sha256"] = "0" * 64; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["deployment_authorized"] = True; variants.append(x)
        require(all(semantic_errors(x) for x in variants), "Authority or identity mutation accepted")
        return {"rejected_mutations": len(variants)}
    check("hostile-decision-probes", probes)

    passed = all(x["result"] == "PASS" for x in checks)
    inputs = [ROOT / name for name in ("decision.json", "validate-decision.py", "DECISION.md")]
    return {
        "schema_version": "cal-event-runtime-binding-admission-decision-validation/v1",
        "decision_id": EXPECTED["decision_id"], "result": "PASS" if passed else "BLOCK",
        "stage_state": "BINDING_ADMITTED" if passed else "not_evaluable",
        "binding_sha256": EXPECTED["subject"]["sha256"],
        "authority_effect": EXPECTED["authority_effect"] if passed else "none",
        "runtime_adopted": False, "runtime_activated": False, "checks": checks,
        "inputs": [{"path": str(p.relative_to(LAB)), "sha256": sha(p)} for p in inputs if p.is_file()],
        "claim_ceiling": "Verifies the recorded user authorization for this binding only. No runtime adoption, activation, migration, publication or external effect."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    path = ROOT / "receipts/decision-validation.json"
    if args.write_receipt:
        if result["result"] != "PASS":
            raise ValueError("Decision validation failed; no successful admission receipt written")
        if path.exists() and path.read_text() != encoded:
            raise ValueError("Existing receipt differs; preserve it and use a successor")
        if not path.exists():
            with path.open("x") as handle:
                handle.write(encoded)
    print(encoded, end="")
    return 0 if result["result"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
