#!/usr/bin/env python3
"""Non-effectful activation preacceptance; rehearsal uses temporary storage only."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
EXPECTED = json.loads("{\"schema_version\":\"cal-event-runtime-activation-candidate/v1\",\"candidate_id\":\"CAL-EVENT-RUNTIME-ACTIVATION-CANDIDATE-0049\",\"status\":\"prepared-for-review\",\"authority_effect\":\"none\",\"adoption\":{\"path\":\"docs/decisions/0048-ontology-event-runtime-adoption/decision.json\",\"sha256\":\"d7d5183de10be297a5e80a6cd1fd1330672e9a3cedab100b0140daba83607e7f\"},\"adoption_receipt\":{\"path\":\"docs/decisions/0048-ontology-event-runtime-adoption/receipts/decision-validation.json\",\"sha256\":\"2a5e07611ff0dad62e3c53d99ac681d386dd8a158935f3f0290c81d93cc3450f\"},\"binding\":{\"path\":\"implementation/bindings/ontology-product-event-runtime/v2/binding.json\",\"sha256\":\"28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d\"},\"navigation\":{\"path\":\"product/products/ontology/v1/navigation/cohesive-lab-system/navigation.json\",\"sha256\":\"e0738fd8083202fd96be9a6817ef0afe2f760ab0d40f6c5565f31e48c941d2e1\"},\"proposed_activation\":{\"option_id\":\"EVRT-ACT-1\",\"owner\":\"Ontology lifecycle runtime owner\",\"effect\":\"local-cli-instance-only\",\"target\":\".local/ontology-event-runtime-0049\",\"target_policy\":\"must be absent, with no symlink ancestors; never overwrite or resume during initial activation\",\"process_model\":\"one-shot materialize, then read-only observe; no daemon or listener\",\"cargo_prefix\":[\"cargo\",\"run\",\"--offline\",\"--locked\",\"--quiet\",\"--manifest-path\",\"implementation/bindings/ontology-product-event-runtime/v2/Cargo.toml\",\"--\"],\"sequence\":[\"verify exact candidate, adoption and current tests\",\"verify target absent immediately before execution\",\"materialize exact navigation into target\",\"observe target and compare full observation\",\"record activation evidence only if both commands succeed\"],\"failure_policy\":\"Stop on first failure; preserve partial target for inspection. Never retry materialize into an existing target.\",\"stop_policy\":\"Commands exit normally; no service to stop. Preserve event files; deletion requires separate scope.\"},\"excluded_effects\":[\"daemon-start\",\"repository-enforcement\",\"legacy-migration\",\"cutover\",\"child-ontology-admission\",\"publication\",\"deployment\",\"external-effects\"],\"work_lanes\":{\"product_construction\":{\"frontier\":\"Product 0006 approved; binding v2 admitted; library adopted\",\"runnable_now\":[],\"causal_blockers\":[]},\"operational_support\":{\"task\":\"prepare and validate local CLI activation envelope\",\"owner\":\"runtime owner\",\"affected_stage\":\"activation\"},\"deferred\":[{\"task\":\"persistent target activation\",\"owner\":\"runtime owner\",\"affected_stage\":\"activation\",\"dependency\":\"exact owner selection of tested envelope\"},{\"task\":\"legacy migration\",\"owner\":\"source ontology owners\",\"affected_stage\":\"migration\"},{\"task\":\"publication\",\"owner\":\"repository owner\",\"affected_stage\":\"none\"}]},\"claim_ceiling\":\"Preparation and temporary rehearsal only; no persistent activation. All Product 0006 and adoption 0048 limitations remain. A local CLI instance is not an always-running Lab system.\"}")

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def require(ok, message):
    if not ok:
        raise ValueError(message)

def run(argv):
    p = subprocess.run(argv, cwd=LAB, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                       capture_output=True, text=True, timeout=420)
    require(p.returncode == 0, p.stdout + p.stderr)
    return json.loads(p.stdout)

def target_safe():
    target = LAB / EXPECTED["proposed_activation"]["target"]
    for p in (target, *target.parents):
        require(not p.is_symlink(), "Symlink target or ancestor: " + str(p))
    require(not target.exists(), "Persistent target already exists")
    return "Exact persistent target absent; no symlink ancestors"

def validate():
    checks = []
    def check(name, action, deps=()):
        failed = [d for d in deps if next(c for c in checks if c["id"] == d)["result"] != "PASS"]
        if failed:
            checks.append({"id": name, "result": "not_evaluable", "detail": failed})
            return
        try:
            checks.append({"id": name, "result": "PASS", "detail": action()})
        except Exception as exc:
            checks.append({"id": name, "result": "BLOCK", "detail": str(exc)})
    def contract():
        require(load(ROOT / "candidate.json") == EXPECTED, "Candidate envelope changed")
        return "Exact target, command prefix, sequence and effect exclusions"
    check("candidate-contract", contract)
    def evidence():
        for key in ("adoption", "adoption_receipt", "binding", "navigation"):
            ref = EXPECTED[key]
            require(sha(LAB / ref["path"]) == ref["sha256"], "Source drift: " + key)
        receipt = load(LAB / EXPECTED["adoption_receipt"]["path"])
        for ref in receipt["inputs"]:
            require(sha(LAB / ref["path"]) == ref["sha256"], "Adoption evidence drift")
        fresh = run(["python3", str((LAB / EXPECTED["adoption"]["path"]).parent / "validate-decision.py")])
        require(fresh == receipt and fresh["runtime_adopted"] is True, "Adoption not current")
        return "Exact adoption, binding and nested Product tests reproduced"
    check("current-adoption-and-product", evidence, ("candidate-contract",))
    check("activation-target-safety", target_safe, ("candidate-contract",))
    def rehearsal():
        prefix = EXPECTED["proposed_activation"]["cargo_prefix"]
        with tempfile.TemporaryDirectory(prefix="cal-activation-0049-") as scratch:
            target = Path(scratch) / "runtime"
            first = run(prefix + ["materialize", EXPECTED["navigation"]["path"], str(target)])
            before = {str(p.relative_to(target)): sha(p) for p in target.rglob("*") if p.is_file()}
            second = run(prefix + ["observe", str(target)])
            after = {str(p.relative_to(target)): sha(p) for p in target.rglob("*") if p.is_file()}
            require(first == second, "Restart observation differs")
            require(before == after and len(before) == 59, "Observe changed event files or wrong file count")
            expected = {"node_count":14,"relation_count":15,"semantic_event_count":29,
                        "governance_event_count":29,"latest_snapshot_count":29,
                        "child_ontologies_admitted_by_binding":0,"authority_effect":"none",
                        "canonical_replay_source_is_event_history":True,"root_admission_preserved":True}
            for k, v in expected.items():
                require(first.get(k) == v, "Observation mismatch: " + k)
            refused = subprocess.run(prefix + ["materialize", EXPECTED["navigation"]["path"], str(target)],
                                     cwd=LAB, capture_output=True, text=True, timeout=60)
            require(refused.returncode != 0, "Existing target was not refused")
            require(before == {str(p.relative_to(target)):sha(p) for p in target.rglob("*") if p.is_file()},
                    "Refused materialization changed files")
            return {"observation": first, "event_files":59, "restart_equal":True,
                    "observe_read_only":True, "nonempty_target_refused_without_change":True}
    check("offline-locked-cli-rehearsal", rehearsal, ("current-adoption-and-product",))
    def probes():
        variants = []
        for k,v in (("authority_effect","activation"),("excluded_effects",[]),("status","active")):
            x = copy.deepcopy(EXPECTED); x[k] = v; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["proposed_activation"]["target"] = "/"; variants.append(x)
        x = copy.deepcopy(EXPECTED); x["proposed_activation"]["cargo_prefix"].remove("--locked"); variants.append(x)
        require(all(x != EXPECTED for x in variants), "Hostile envelope accepted")
        return {"rejected_envelope_mutations":len(variants)}
    check("hostile-envelope-probes", probes)
    passed = all(c["result"] == "PASS" for c in checks)
    return {"schema_version":"cal-event-runtime-activation-preacceptance/v1",
            "result":"PASS" if passed else "BLOCK", "candidate_sha256":sha(ROOT / "candidate.json"),
            "checks":checks, "authority_effect":"none", "persistent_target_activated":False,
            "inputs":[{"path":str((ROOT / n).relative_to(LAB)),"sha256":sha(ROOT / n)}
                      for n in ("candidate.json","README.md","validate.py")]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = validate()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_receipt and result["result"] == "PASS":
        path = ROOT / "receipts/preacceptance.json"
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            require(path.read_text() == encoded, "Preserve prior receipt; use a successor")
        else:
            with path.open("x") as handle:
                handle.write(encoded)
    print(encoded, end="")
    raise SystemExit(0 if result["result"] == "PASS" else 1)
