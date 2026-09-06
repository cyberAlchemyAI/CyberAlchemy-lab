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
EXPECTED = json.loads("{\"schema_version\":\"cal-event-runtime-adoption-decision/v1\",\"decision_id\":\"CAL-EVENT-RUNTIME-ADOPTION-0048\",\"gate_id\":\"G-CAL-ONTOLOGY-EVENT-RUNTIME-ADOPTION\",\"decided_at\":\"2026-09-06T04:44:22Z\",\"decision_source\":{\"kind\":\"explicit-user-authorization\",\"verbatim\":\"admit\",\"resolution_basis\":\"User selected adoption after presentation of candidate 0048 and EVRT-RADOPT-1; applies only to the exact Rust library behind admitted binding v2.\"},\"selected_option\":\"EVRT-RADOPT-1\",\"status\":\"adopted\",\"authority_effect\":\"runtime-adoption-only\",\"subject\":{\"runtime_id\":\"cal.runtime.ontology-lifecycle-rust/v1\",\"binding_id\":\"cal.binding.ontology-product-event-runtime/v2\",\"path\":\"ontology-lifecycle/runtime/src/lib.rs\",\"sha256\":\"f1b3f7cf463ebcc6e7b887b374d75adeac29ba38acfec3bafacfe4d3159f3a7b\"},\"references\":{\"candidate\":{\"path\":\"candidate.json\",\"sha256\":\"e326a4fb79829c78d796e63a876bca4ddcca7a1dd607024c486aa3f51c4a47c0\"},\"preacceptance\":{\"path\":\"receipts/preacceptance.json\",\"sha256\":\"a8705616c7b713686363e25159f418839c85112e6b72585e6e8c134cd40839ca\"},\"request\":{\"path\":\"admissibility-request.json\",\"sha256\":\"7d40f1d4cf6e55a719892db213922f4279431ba2ffd46eaa839466676ab478e6\"},\"admissibility\":{\"path\":\"receipts/admissibility.json\",\"sha256\":\"31f275f594b8b0ad05a3d276d73328443acea53bfda5c605114bc7a59d9c2373\"}},\"scope\":\"Select the exact Rust lifecycle library as provider behind admitted binding v2 for approved Product 0006: frozen navigation input, materialize/observe CLI, per-subject replay, latest snapshots, checkpoint recovery and Context projections.\",\"excluded_effects\":[\"standalone-runtime-cli-adoption\",\"runtime-activation\",\"service-start\",\"repository-enforcement\",\"legacy-migration\",\"cutover\",\"child-ontology-admission\",\"publication\",\"release\",\"deployment\",\"source-retirement\",\"external-effects\"],\"limitations_preserved_from\":\"candidate.json#/limitations\",\"next_frontier\":\"Activation target and startup-envelope preparation; no activation authorized.\",\"work_lane\":\"operational support: runtime adoption\",\"record_policy\":\"This external decision supplies runtime adoption status. Frozen candidate, library, manifest, lockfile and binding remain unchanged.\"}")

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
            bad.append("runtime-library")
        require(not bad, str(bad))
        receipt = load(ROOT / "receipts/preacceptance.json")
        for ref in receipt["inputs"]:
            require((LAB / ref["path"]).is_file() and sha(LAB / ref["path"]) == ref["sha256"], "Preacceptance input drift: " + ref["path"])
        return "Candidate, preacceptance, request, admissibility and runtime library current"
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
        for key, value in [("selected_option", "EVRT-RADOPT-2"), ("authority_effect", "runtime-activation"),
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
        "schema_version": "cal-event-runtime-adoption-decision-validation/v1",
        "decision_id": EXPECTED["decision_id"], "result": "PASS" if passed else "BLOCK",
        "stage_state": "RUNTIME_ADOPTED" if passed else "not_evaluable",
        "runtime_library_sha256": EXPECTED["subject"]["sha256"],
        "authority_effect": EXPECTED["authority_effect"] if passed else "none",
        "runtime_adopted": passed, "runtime_activated": False, "checks": checks,
        "inputs": [{"path": str(p.relative_to(LAB)), "sha256": sha(p)} for p in inputs if p.is_file()],
        "claim_ceiling": "Verifies the recorded user authorization for the exact runtime library behind binding v2 only. No activation, standalone CLI adoption, migration, publication or external effect."
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
            raise ValueError("Decision validation failed; no successful adoption receipt written")
        if path.exists() and path.read_text() != encoded:
            raise ValueError("Existing receipt differs; preserve it and use a successor")
        if not path.exists():
            with path.open("x") as handle:
                handle.write(encoded)
    print(encoded, end="")
    return 0 if result["result"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
