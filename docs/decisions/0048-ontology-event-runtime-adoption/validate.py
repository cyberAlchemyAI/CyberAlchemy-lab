#!/usr/bin/env python3
"""Collect-all preacceptance for the bounded runtime adoption proposal."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
EXPECTED = json.loads("{\"schema_version\":\"cal-event-runtime-adoption-candidate/v1\",\"candidate_id\":\"CAL-EVENT-RUNTIME-ADOPTION-CANDIDATE-0048\",\"status\":\"prepared-for-review\",\"authority_effect\":\"none\",\"references\":{\"binding_admission\":{\"path\":\"docs/decisions/0047-ontology-event-runtime-binding-admission/decision.json\",\"sha256\":\"6f3e24581b1129d9cf460da60ef0fdd8154793a8e9f65ca310e185a8b6d99428\"},\"admission_receipt\":{\"path\":\"docs/decisions/0047-ontology-event-runtime-binding-admission/receipts/decision-validation.json\",\"sha256\":\"575ec10c6b84a8313ac9bb395b534e4ec784b7f071568502e35ddff7323dc493\"},\"binding\":{\"path\":\"implementation/bindings/ontology-product-event-runtime/v2/binding.json\",\"sha256\":\"28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d\"},\"runtime_manifest\":{\"path\":\"ontology-lifecycle/runtime/Cargo.toml\",\"sha256\":\"6e17c6f449dd7068f9d2aa4bd664e8e1e8a8a0083c3e93ceca5e78def13364dc\"},\"runtime_library\":{\"path\":\"ontology-lifecycle/runtime/src/lib.rs\",\"sha256\":\"f1b3f7cf463ebcc6e7b887b374d75adeac29ba38acfec3bafacfe4d3159f3a7b\"},\"dependency_lock\":{\"path\":\"implementation/bindings/ontology-product-event-runtime/v2/Cargo.lock\",\"sha256\":\"78e8143fa9a380c0fb4cee713aa78e3ee734400968101b04cda708e819e6f4aa\"}},\"proposed_decision\":{\"option_id\":\"EVRT-RADOPT-1\",\"owner_gate\":\"G-CAL-ONTOLOGY-EVENT-RUNTIME-ADOPTION\",\"effect\":\"runtime-adoption-only\",\"runtime_id\":\"cal.runtime.ontology-lifecycle-rust/v1\",\"binding_id\":\"cal.binding.ontology-product-event-runtime/v2\",\"meaning\":\"Select the exact Rust lifecycle library as the implementation provider behind admitted binding v2 for approved Product candidate 0006.\",\"scope\":\"The frozen navigation input, binding materialize/observe CLI, per-subject event replay, latest snapshots, checkpoint recovery and Context projections covered by Product candidate 0006.\",\"record_policy\":\"Record adoption externally against these exact bytes; do not edit frozen source or binding.\"},\"excluded_effects\":[\"standalone-runtime-cli-adoption\",\"runtime-activation\",\"service-start\",\"repository-enforcement\",\"legacy-migration\",\"cutover\",\"child-ontology-admission\",\"publication\",\"release\",\"deployment\",\"source-retirement\",\"external-effects\"],\"limitations\":[\"One exact 14-node and 15-relation navigation graph; no general legacy importer.\",\"Prototype test-empty-profile/v1 typed properties.\",\"No production storage, multi-writer or power-loss guarantee.\",\"No admission of source-owner residue or resolution of DomainSpec profile collisions.\",\"No binary reproducibility or deployment-artifact claim.\"],\"work_lanes\":{\"product_construction\":{\"frontier\":\"Product 0006 approved, binding v2 admitted\",\"runnable_now\":[],\"causal_blockers\":[]},\"operational_support\":{\"current\":\"Prepare runtime-adoption decision\",\"owner\":\"Ontology lifecycle runtime owner\",\"affected_stage\":\"post-binding-admission runtime adoption\"},\"deferred\":[{\"task\":\"activation target and startup envelope\",\"owner\":\"runtime owner\",\"affected_stage\":\"activation\"},{\"task\":\"legacy ontology migration\",\"owner\":\"source ontology owners\",\"affected_stage\":\"migration\"},{\"task\":\"commit and publication\",\"owner\":\"repository owner\",\"affected_stage\":\"none\"}]},\"claim_ceiling\":\"This is a runtime selection proposal with no adoption or activation effect. A separate owner decision must select the exact candidate. Product evidence remains limited to the frozen implementation scope.\"}")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def errors(document):
    return [k for k in sorted(set(document) | set(EXPECTED))
            if k not in document or k not in EXPECTED or document[k] != EXPECTED[k]]

def validate():
    checks = []
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    def check(name, fn, deps=()):
        if any(next(c for c in checks if c["id"] == dep)["result"] != "PASS" for dep in deps):
            checks.append({"id": name, "result": "not_evaluable", "detail": list(deps)})
            return
        try:
            checks.append({"id": name, "result": "PASS", "detail": fn()})
        except Exception as exc:
            checks.append({"id": name, "result": "BLOCK", "detail": str(exc)})
    def contract():
        found = errors(load(ROOT / "candidate.json"))
        require(not found, str(found))
        return "Exact runtime, binding, scope and exclusions"
    check("candidate-contract", contract)
    def sources():
        failures = [name for name, r in EXPECTED["references"].items()
                    if not (LAB / r["path"]).is_file() or sha(LAB / r["path"]) != r["sha256"]]
        require(not failures, str(failures))
        receipt = load(LAB / EXPECTED["references"]["admission_receipt"]["path"])
        for r in receipt["inputs"]:
            require((LAB / r["path"]).is_file() and sha(LAB / r["path"]) == r["sha256"], "Admission evidence drift: " + r["path"])
        return "Runtime source, manifest, lockfile, binding and admission evidence current"
    check("source-closure", sources)
    def admission():
        d = load(LAB / EXPECTED["references"]["binding_admission"]["path"])
        r = load(LAB / EXPECTED["references"]["admission_receipt"]["path"])
        require(d["status"] == "admitted" and d["selected_option"] == "EVRT-BADM-1", "Binding not admitted")
        require(d["subject"]["sha256"] == EXPECTED["references"]["binding"]["sha256"], "Wrong admitted binding")
        require(r["result"] == "PASS" and r["stage_state"] == "BINDING_ADMITTED", "Admission evidence not PASS")
        binding = load(LAB / EXPECTED["references"]["binding"]["path"])
        require(binding["runtime_source"]["runtime_id"] == EXPECTED["proposed_decision"]["runtime_id"], "Runtime identity mismatch")
        require(binding["runtime_source"]["source_sha256"] == EXPECTED["references"]["runtime_library"]["sha256"], "Runtime source mismatch")
        return "Runtime is the provider tested by the admitted binding"
    check("admission-runtime-join", admission, ("source-closure",))
    def current():
        parent = (LAB / EXPECTED["references"]["binding_admission"]["path"]).parent
        run = subprocess.run(["python3", str(parent / "validate-decision.py")], cwd=LAB,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, text=True, timeout=360)
        require(run.returncode == 0, run.stdout + run.stderr)
        fresh = json.loads(run.stdout)
        require(fresh == load(parent / "receipts/decision-validation.json"), "Fresh admission validation differs")
        return "Admission validation and its nested current Product tests reproduce reviewed evidence"
    check("current-admission-and-product-tests", current, ("candidate-contract", "source-closure", "admission-runtime-join"))
    def probes():
        variants = []
        for key, value in [("authority_effect", "runtime-adoption"), ("excluded_effects", []),
                           ("status", "adopted"), ("references", {})]:
            x = copy.deepcopy(EXPECTED); x[key] = value; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["proposed_decision"]["effect"] = "runtime-activation"; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["proposed_decision"]["runtime_id"] = "other"; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["references"]["runtime_library"]["sha256"] = "0"*64; variants.append(x)
        require(all(errors(x) for x in variants), "Hostile mutation escaped")
        return {"rejected_mutations": len(variants)}
    check("hostile-probes", probes)
    passed = all(c["result"] == "PASS" for c in checks)
    return {"schema_version": "cal-event-runtime-adoption-preacceptance/v1",
            "candidate_sha256": sha(ROOT / "candidate.json"),
            "result": "PASS" if passed else "BLOCK", "review_eligible": passed,
            "checks": checks, "authority_effect": "none", "runtime_adopted": False,
            "runtime_activated": False,
            "inputs": [{"path": str((ROOT / n).relative_to(LAB)), "sha256": sha(ROOT / n)}
                       for n in ("candidate.json", "validate.py", "README.md")]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = validate()
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write_receipt:
        path = ROOT / "receipts/preacceptance.json"
        path.parent.mkdir(exist_ok=True)
        if path.exists() and path.read_text() != encoded:
            raise ValueError("Preserve existing receipt; use a successor")
        if not path.exists():
            with path.open("x") as handle:
                handle.write(encoded)
    print(encoded, end="")
    return 0 if receipt["result"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
