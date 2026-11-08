#!/usr/bin/env python3
"""Fresh proof replay, hostile claims, strict transports and all ten stressors."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

import stress_cli as cli

BASE, FORMAL, ROOT = cli.BASE, cli.FORMAL, cli.ROOT
helpers = cli.helpers
MODULES = ["StressTypes", "DelegationSemantics", "ObligationSemantics", "StressLaws",
           "StressCheckers", "StressProofs", "StressWitnesses", "StressStatementAudit", "StressRuntime"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write audit, result and plan receipt only after all checks pass")
    args = parser.parse_args()
    lean = cli.pinned_lean()
    # Bind the prior selection and the accepted F0 proof sources without changing them.
    selection = json.loads((BASE.parent / "schema-stress-audit.json").read_text())
    for b in selection["source_bindings"]:
        helpers.require(helpers.digest(ROOT / b["path"]) == b["sha256"], "selection source drift: " + b["path"])
    parent_file = FORMAL / "proofs/l0/statement-and-axiom-audit.json"
    parent = json.loads(parent_file.read_text())
    helpers.require(parent["result"] == "pass", "missing accepted F0 result")
    for b in parent["source_bindings"] + parent["relation_sources"]:
        helpers.require(helpers.digest(ROOT / b["path"]) == b["sha256"], "F0 source drift: " + b["path"])
    for b in parent["standard_library_imports"]:
        helpers.require(helpers.digest(lean.parent.parent / b["path"]) == b["sha256"], "pinned core dependency drift")
    for name in MODULES:
        code = (BASE / (name + ".lean")).read_text()
        helpers.require(helpers.source_policy(code), "proof bypass in " + name)
        imports = set(re.findall(r"^import ([A-Za-z0-9_.]+)$", code, re.M))
        extra = {"Lean.Data.Json.FromToJson", "Lean.Data.Json.Printer"} if name == "StressRuntime" else set()
        helpers.require(imports <= set(MODULES) | {"Init"} | extra, "unexpected import in " + name)
        if name in {"DelegationSemantics", "ObligationSemantics", "StressLaws"}:
            helpers.require(not re.search(r"\b(checkActs|checkInheritance|checkCertificate|StressCheckers|closure)\b", code),
                            "checker dependency in independent semantic layer")
    for name in ["request", "response"]:
        cli.Draft202012Validator.check_schema(cli.schema(name))
    controls, integration, logs = [], [], []
    with tempfile.TemporaryDirectory(prefix="stress-profile-replay-") as folder:
        build = Path(folder)
        logs = cli.compile_into(build, lean, MODULES)
        report = helpers.axiom_report(next(x["output"] for x in logs if x["module"] == "StressStatementAudit"))
        expected = set()
        for name in ["StressLaws", "StressProofs", "StressWitnesses", "StressStatementAudit"]:
            prefix = "Stress.Witnesses." if name == "StressWitnesses" else "Stress.Audit." if name == "StressStatementAudit" else "Stress."
            expected |= {prefix + n for n in re.findall(r"^theorem ([a-z_]+)", (BASE / (name + ".lean")).read_text(), re.M)}
        helpers.require(set(report) == expected, "omitted or substituted audited declaration")
        helpers.require(all(set(a) <= helpers.ALLOW for a in report.values()), "unapproved transitive axiom")
        print("PASS fresh Lean replay:", len(MODULES), "modules;", len(report), "audited declarations", flush=True)
        env = {**os.environ, "LEAN_PATH": str(build)}

        def reject(name, body, assumed=False):
            file = build / ("Hostile" + str(len(controls)) + ".lean")
            file.write_text("import StressStatementAudit\nopen Stress Stress.Audit Stress.Witnesses\n" + body)
            result = subprocess.run([str(lean), str(file)], cwd=build, env=env, capture_output=True, text=True, timeout=60)
            output = result.stdout + result.stderr
            logs.append({"module": file.stem, "output": output, "returncode": result.returncode})
            if assumed:
                helpers.require(result.returncode == 0 and not helpers.policy_accepts(output), "assumed theorem escaped audit: " + name)
            else:
                helpers.require(result.returncode != 0, "hostile theorem accepted: " + name)
                helpers.require(not any(s in output for s in ["Unknown identifier", "unknown module", "unexpected token"]),
                                "hostile control failed before its intended check: " + name)
            controls.append({"name": name, "result": "rejected", "mechanism": "axiom policy" if assumed else "Lean type or kernel check"})

        reject("weakened restriction conclusion", "theorem weak : True := True.intro\nexample : RequiredRestriction := weak\n")
        reject("circular origin statement", "theorem weak (g : Graph) (f : Fact) : Origin g f → Origin g f := id\nexample : RequiredOrigin := weak\n")
        reject("recorded edge grants perpetual effectiveness", 'example : Effective delegation expired edge "read" false := by decide\n')
        reject("revocation epoch remains eligible", 'example : checkActs [revoked] snapshot revokedEdge "read" false = .yes := by decide\n')
        reject("inheritance grants conformance", "example : Conforms graph inheritance := by decide\n")
        reject("conflict derives unrelated norm", "example : Origin conflictGraph unsupportedFact := by decide\n")
        reject("self-referencing certificate is valid", "example : checkCertificate graph cycle = true := by decide\n")
        reject("partial closure claims completeness", "example : checkInheritance graph 0 = .yes := by decide\n")
        reject("assumed closure proof", "theorem invented : RequiredClosure := by sorry\n#print axioms invented\n", True)
        reject("custom restriction axiom", "axiom injected : RequiredRestriction\ntheorem invented : RequiredRestriction := injected\n#print axioms invented\n", True)
        for name, specimen in [("native proof evaluation", "example : 1 = 1 := by native_decide"),
                               ("skip kernel check", "set_option debug.skipKernelTC true")]:
            helpers.require(not helpers.source_policy(specimen), "source policy bypass")
            controls.append({"name": name, "result": "rejected", "mechanism": "source policy"})

        examples = {n: json.loads((BASE / "examples" / (n + ".json")).read_text())
                    for n in ["acts-for", "inherits-contract", "certificate"]}

        def evaluate(name, key, mutate=None, status="yes", reason=None, verify=None):
            request = deepcopy(examples[key])
            if mutate:
                mutate(request)
            response = cli.evaluate(request, build, lean)
            helpers.require(response["status"] == status, name + ": unexpected verdict " + str(response))
            if reason:
                helpers.require(response["reason"] == reason, name + ": wrong explanation")
            if verify:
                helpers.require(verify(response), name + ": wrong result payload")
            integration.append({"name": name, "status": status, "reason": response["reason"]})
            return response

        evaluate("positive temporal model", "acts-for")
        evaluate("before period start", "acts-for", lambda q: q["snapshot"].update(epoch=0) or q["delegations"][0]["period"].update(start=1) or q["edge"]["period"].update(start=1), "no")
        evaluate("start epoch inclusive", "acts-for", lambda q: q["snapshot"].update(epoch=0))
        evaluate("stop epoch exclusive", "acts-for", lambda q: q["snapshot"].update(epoch=10), "no")
        evaluate("historic edge after expiration", "acts-for", lambda q: q["snapshot"].update(epoch=11), "no")
        def revoke(q):
            q["delegations"][0]["revokedAt"] = 5
            q["edge"]["revokedAt"] = 5
        evaluate("revocation epoch exclusive", "acts-for", revoke, "no")
        evaluate("before revocation epoch", "acts-for", lambda q: revoke(q) or q["snapshot"].update(epoch=4))
        evaluate("wrong principal", "acts-for", lambda q: q["edge"]["principal"].update(id="other"), "no")
        evaluate("wrong agent", "acts-for", lambda q: q["edge"]["agent"].update(id="other"), "no")
        evaluate("wrong delegation revision", "acts-for", lambda q: q["edge"]["delegation"].update(version="v2"), "unknown", "unresolved-delegation")
        evaluate("scope widening", "acts-for", lambda q: q["edge"].update(scope="all-repos"), "no")
        evaluate("action widening", "acts-for", lambda q: q.update(action="publish"), "no")
        evaluate("missing policy", "acts-for", lambda q: q["delegations"][0].update(policies=[{"id":"policy","version":"v1"}]), "unknown")
        def policy(q, accepted):
            q["delegations"][0]["policies"] = [{"id":"policy","version":"v1"}]
            q["snapshot"]["policies"] = [{"ref":{"id":"policy","version":"v1"},"accepted":accepted}]
        evaluate("rejected policy", "acts-for", lambda q: policy(q,False), "no")
        evaluate("accepted policy", "acts-for", lambda q: policy(q,True))
        evaluate("missing gate", "acts-for", lambda q: q["delegations"][0].update(gates=[{"id":"gate","version":"v1"}]), "unknown")
        evaluate("forbidden redelegation", "acts-for", lambda q: q.update(redelegated=True), "no")
        evaluate("permitted redelegation still needs a chain", "acts-for", lambda q: q.update(redelegated=True) or q["delegations"][0].update(redelegationAllowed=True), "unknown", "redelegation-chain-unsupported")
        evaluate("ambiguous delegation identity", "acts-for", lambda q: q["delegations"].append(deepcopy(q["delegations"][0])), "invalid")
        evaluate("empty period", "acts-for", lambda q: q["delegations"][0]["period"].update(stop=0), "invalid")
        evaluate("duplicate policy assessments", "acts-for", lambda q: policy(q,True) or q["snapshot"]["policies"].append(deepcopy(q["snapshot"]["policies"][0])), "invalid")
        evaluate("snapshot result cannot upgrade later epoch", "acts-for", lambda q: q["snapshot"].update(epoch=10,ref={"id":"snapshot","version":"v2"}), "no", verify=lambda r:r["epoch"]==10 and r["snapshot"]["version"]=="v2")

        result = evaluate("positive obligation closure", "inherits-contract", verify=lambda r:r["complete"] and len(r["facts"])==1 and len(r["certificate"])==1)
        evaluate("binding points to another instance", "inherits-contract", lambda q:q["graph"]["bindings"][0]["subject"].update(id="other"), "invalid")
        evaluate("binding omits named contract", "inherits-contract", lambda q:q["graph"]["bindings"][0].update(contracts=[]), "invalid")
        evaluate("contract revision substitution", "inherits-contract", lambda q:q["graph"]["inheritances"][0]["contract"].update(version="v2"), "unknown")
        evaluate("unknown obligation interpretation", "inherits-contract", lambda q:q["graph"]["contracts"][0].update(interpreted=False), "unknown")
        evaluate("missing binding", "inherits-contract", lambda q:q["graph"].update(bindings=[]), "unknown")
        evaluate("unsupported override", "inherits-contract", lambda q:q["graph"]["bindings"][0].update(overrides=[{"id":"override","version":"v1"}]), "unknown")
        evaluate("suspended binding", "inherits-contract", lambda q:q["graph"]["bindings"][0].update(active=False), "invalid")
        evaluate("condition mismatch", "inherits-contract", lambda q:q["graph"]["inheritances"][0].update(condition="after-review"), "invalid")
        evaluate("scope mismatch", "inherits-contract", lambda q:q["graph"]["inheritances"][0].update(scope="other"), "invalid")
        evaluate("duplicate contract revision", "inherits-contract", lambda q:q["graph"]["contracts"].append(deepcopy(q["graph"]["contracts"][0])), "invalid")
        evaluate("budget exhaustion", "inherits-contract", lambda q:q.update(budget=0), "unknown", "closure-budget-exceeded", verify=lambda r:not r["complete"] and not r["facts"])
        evaluate("pair-comparison budget counted", "inherits-contract", lambda q:q.update(budget=1), "unknown", "closure-budget-exceeded")
        evaluate("exact minimal budget", "inherits-contract", lambda q:q.update(budget=2))
        def conformance(q):
            e=q["graph"]["inheritances"][0]
            q["graph"]["conformance"]=[{"subject":e["subject"],"contract":e["contract"],"scope":e["scope"],"accepted":True}]
        evaluate("independent conformance preserves norms", "inherits-contract", conformance, verify=lambda r:r["facts"]==result["facts"])
        def conflict(q):
            q["graph"]["contracts"][0]["norms"].append({"mode":"forbid","action":"receipt"})
        evaluate("same-contract normative conflict", "inherits-contract", conflict, verify=lambda r:len(r["facts"])==2 and len(r["conflicts"])==1)
        def two_contracts(q):
            g=q["graph"];c=deepcopy(g["contracts"][0]);c["ref"]["id"]="contract-2";c["norms"]=[{"mode":"forbid","action":"receipt"}]
            g["contracts"].append(c);g["bindings"][0]["contracts"].append(c["ref"])
            e=deepcopy(g["inheritances"][0]);e["id"]="inherits-2";e["contract"]=c["ref"];g["inheritances"].append(e)
        evaluate("different-contract normative conflict", "inherits-contract", two_contracts, verify=lambda r:len(r["facts"])==2 and len(r["conflicts"])==1)
        evaluate("permission stays a distinct norm", "inherits-contract", lambda q:q["graph"]["contracts"][0]["norms"].append({"mode":"permit","action":"read"}), verify=lambda r:len(r["facts"])==2 and not r["conflicts"])

        evaluate("valid propagation and forwarding", "certificate", verify=lambda r:r["accepted"])
        evaluate("self-cycle rejected", "certificate", lambda q:q["steps"][0].update(rule="forward",parent=0), "no")
        evaluate("forward future reference rejected", "certificate", lambda q:q["steps"][0].update(rule="forward",parent=1), "no")
        evaluate("forward missing parent rejected", "certificate", lambda q:q["steps"][1].update(parent=None), "no")
        evaluate("propagate extraneous parent rejected", "certificate", lambda q:q["steps"][0].update(parent=0), "no")
        evaluate("forward changes fact rejected", "certificate", lambda q:q["steps"][1]["fact"]["norm"].update(action="publish"), "no")
        evaluate("invented origin rejected", "certificate", lambda q:q["steps"][0]["fact"]["norm"].update(action="publish"), "no")
        evaluate("certificate version substitution rejected", "certificate", lambda q:q["steps"][0]["fact"]["edge"]["contract"].update(version="v2"), "no")
        evaluate("certificate needs complete request", "certificate", lambda q:q.update(budget=0), "unknown")
        evaluate("emitted closure certificate replays", "certificate", lambda q:q.update(steps=result["certificate"]))

        # Literal strings must survive the transport, including syntax-like text.
        marker = 'ação 漢字 " \\ ; #eval false --'
        evaluate("unicode and syntax-like text round trip", "acts-for", lambda q:q["edge"].update(id=marker), verify=lambda r:r["assertionId"]==marker)
        for name, text in [("duplicate JSON member", '{"profile":1,"profile":2}'),
                           ("nonfinite JSON number", '{"x":NaN}'),
                           ("malformed JSON", '{'),
                           ("isolated surrogate", '"\\ud800"')]:
            try:
                value=cli.decode(text);cli.validate_request(value)
            except (ValueError, UnicodeError):
                controls.append({"name":name,"result":"rejected","mechanism":"strict JSON decoder"})
            else:
                raise ValueError("invalid transport accepted: "+name)
        for name, key, mutate in [
            ("extra request property","acts-for",lambda q:q.update(extra=True)),
            ("missing exact revision","acts-for",lambda q:q["edge"]["delegation"].pop("version")),
            ("negative epoch","acts-for",lambda q:q["snapshot"].update(epoch=-1)),
            ("boolean epoch","acts-for",lambda q:q["snapshot"].update(epoch=True)),
            ("legacy period string","acts-for",lambda q:q["edge"].update(period="until-revoked")),
            ("unknown producer rule","certificate",lambda q:q["steps"][0].update(rule="conforms")),
            ("unknown norm mode","inherits-contract",lambda q:q["graph"]["contracts"][0]["norms"][0].update(mode="satisfied")),
            ("control character string","acts-for",lambda q:q.update(action="read\n")),
        ]:
            request=deepcopy(examples[key]);mutate(request)
            try:cli.validate_request(request)
            except (ValueError, UnicodeError):controls.append({"name":name,"result":"rejected","mechanism":"strict request schema"})
            else:raise ValueError("invalid typed transport accepted: "+name)
        print("PASS integration:",len(integration),"cases; hostile controls:",len(controls),flush=True)
        # Capture all serialized imports used by the proof core and JSON renderer.
        library=lean.parent.parent/"lib/lean"
        output=subprocess.check_output([str(lean),"--run",str(FORMAL/"proofs/l0/DependencyAudit.lean"),str(library),"Init","Lean.Data.Json.FromToJson","Lean.Data.Json.Printer"],cwd=build,env=env,text=True,timeout=60)
        dependency_files=set()
        for name in output.splitlines():
            f=library/(name.replace(".","/")+".olean")
            helpers.require(f.is_file(),"missing runtime import")
            dependency_files.add(f)
            for suffix in [".private",".server"]:
                extra=Path(str(f)+suffix)
                if extra.is_file():dependency_files.add(extra)
        dependencies=[{"path":str(f.relative_to(lean.parent.parent)),"sha256":helpers.digest(f)} for f in sorted(dependency_files)]

    sources=sorted([f for f in BASE.rglob("*") if f.is_file() and ".build" not in f.parts and "__pycache__" not in f.parts
                    and f.name not in {"audit.json","lean-replay.log","RESULT.md","plan.json"}])
    receipt={"schema":"relational.stress-implementation-audit/v1","result":"pass",
             "status":"candidate-local-implemented","review_mode":"Codex author self-review",
             "source_bindings":[{"path":str(f.relative_to(ROOT)),"sha256":helpers.digest(f)} for f in sources],
             "selection_receipt":{"path":str((BASE.parent/"schema-stress-audit.json").relative_to(ROOT)),"sha256":helpers.digest(BASE.parent/"schema-stress-audit.json")},
             "parent_f0_receipt":{"path":str(parent_file.relative_to(ROOT)),"sha256":helpers.digest(parent_file)},
             "modules":[x for x in logs if "source_sha256" in x],"transitive_axioms":report,
             "standard_library_imports":dependencies,"integration_controls":integration,"hostile_controls":controls,
             "stressors_covered":10,"public_operations":3,"schema_count":2,
             "claim_ceiling":"Typed-input temporal and finite two-rule semantics, kernel-checked laws and checker proofs; JSON adapter tested but not formally proved, no source admission, evidence authentication, runtime permission or general L3 implementation."}
    if args.write:
        (BASE/"audit.json").write_text(json.dumps(receipt,indent=2)+"\n")
        (BASE/"lean-replay.log").write_text("\n".join(x["module"]+"\n"+x["output"] for x in logs))
        tasks=[{"id":"S0"+str(i),"depends_on":deps,"status":"complete","evidence":"audit.json"}
               for i,deps in [(1,[]),(2,["S01"]),(3,["S01"]),(4,["S02","S03"]),(5,["S04"]),(6,["S05"]),(7,["S06"])]]
        (BASE/"plan.json").write_text(json.dumps({"schema":"relational.stress-plan/v1","scope":"candidate-local profiles; original accepted plan unchanged","tasks":tasks,"completion_receipt_sha256":helpers.digest(BASE/"audit.json")},indent=2)+"\n")
        (BASE/"RESULT.md").write_text("# Candidate implementation result\n\nAll seven local DAG tasks are complete. The original F0 acceptance, authority sources and general L3 plan are unchanged.\n\n"
            +f"Validation passed: {len(MODULES)} Lean modules, {len(report)} audited declarations, {len(integration)} integration cases, {len(controls)} rejected hostile controls, and {len(dependencies)} hashed transitive import files. Actual theorem axioms are `propext` and `Quot.sound`; no custom assumptions or bypasses.\n\n"
            +"Implemented: snapshot-bound delegation evaluation; complete finite obligation closure with origins and conflict reporting; replay of propagation/forward certificates; strict JSON CLI operations. See `README.md` for commands and `SEMANTICS.md` for the contracts.\n\n"
            +"Claim ceiling: candidate typed-input proof and local reference implementation. The JSON adapter is tested, not proved equivalent; supplied snapshots and assessments are not authenticated. Legacy string interpretation, override precedence, redelegation chains, general rule languages, global profile admission and network deployment remain outside this profile.\n")
    print(json.dumps({"result":"pass","modules":len(MODULES),"audited_declarations":len(report),"integration_cases":len(integration),"hostile_controls":len(controls),"import_files":len(dependencies)},indent=2))


if __name__=="__main__":
    main()
