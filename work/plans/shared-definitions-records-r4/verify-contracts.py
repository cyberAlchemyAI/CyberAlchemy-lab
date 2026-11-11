from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import re

from jsonschema import Draft202012Validator

PLAN = Path(__file__).resolve().parent
ROOT = PLAN.parents[2]
ORIGINAL = PLAN.with_name("shared-definitions-records")
AUDIT = ROOT / "work/audits/shared-lab-design/20261110"

def read(path):
    return json.loads(path.read_text())

def bind(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(raw).hexdigest(), "bytes": len(raw)}

checks = []

def check(name, condition):
    assert condition, name
    checks.append(name)

for item in read(ORIGINAL / "MANIFEST.json")["files"]:
    actual = bind(ORIGINAL / item["path"])
    check("preserved original " + item["path"], actual["sha256"] == item["sha256"] and actual["bytes"] == item["bytes"])

selection = read(PLAN / "DEFINITIONS.json")["selection"]
bindings = {entry["definition_id"] + "@" + entry["version"]: entry for entry in selection["bindings"]}
for entry in bindings.values():
    check("exact selected definition " + entry["definition_id"], bind(ROOT / entry["path"])["sha256"] == entry["sha256"])
for pending in selection["pending_definition_targets"]:
    check("exact pending candidate " + pending["version"], bind(ROOT / pending["source"]["path"]) == pending["source"])
targets = set(bindings) | {item["version"] for item in selection["pending_definition_targets"]}
check("46 unique targets with five pending", len(targets) == 46 and len(selection["pending_definition_targets"]) == 5)
check("verified full target bound in model", "definition_targets List<Binding,64>" in (PLAN / "alchlang/contracts.alch").read_text())

schema = read(PLAN / "contracts/verification-ports.schema.json")
Draft202012Validator.check_schema(schema)
for port in read(PLAN / "SYSTEM.json")["ports"]:
    for direction in ("request", "response"):
        key = port[direction + "_schema"].split("/")[-1]
        check(port["name"] + " " + direction + " signature", key in schema["$defs"])
    wire = {"ref": "fixture:subject", "sha256": "a"*64, "bytes": 10}
    response = Draft202012Validator({**schema, "$ref": port["response_schema"]})
    check(port["name"] + " explicit unknown", response.is_valid({"outcome":"Unknown","subject":wire,"reason":"Inspect original subject"}))
    check(port["name"] + " rejects bare success flag", not response.is_valid({"outcome":"Verified","value":{"verified":True}}))

registry = read(ROOT / "authority/definitions/registry.json")
def exact_key(entry):
    return entry["definition_id"] + "@" + entry["version"]

original = {exact_key(entry): entry for entry in registry["entries"]}
check("189 unique canonical versions and 183 current identities", len(original) == len(registry["entries"]) == 189 and len(registry["current_lookup"]) == 183)
for key, entry in original.items():
    check("exact retained registry body " + key, bind(ROOT / entry["path"])["sha256"] == entry["sha256"])
for identity, key in registry["current_lookup"].items():
    check("canonical lookup " + identity, key in original and original[key]["definition_id"] == identity)

def retained_slice_matches(entries, lookup):
    by_key = {exact_key(entry): entry for entry in entries}
    return len(by_key) == len(entries) and by_key == original and lookup == registry["current_lookup"]

check("zero-change migration retains all original entries", retained_slice_matches(registry["entries"], registry["current_lookup"]))
check("migration refuses an omitted retained entry", not retained_slice_matches(registry["entries"][1:], registry["current_lookup"]))
check("migration refuses duplicate identities", not retained_slice_matches(registry["entries"] + registry["entries"][:1], registry["current_lookup"]))
changed = deepcopy(registry["entries"])
changed[0]["sha256"] = "0" * 64
check("migration refuses changed exact body", not retained_slice_matches(changed, registry["current_lookup"]))
lookup = dict(registry["current_lookup"])
lookup[next(iter(lookup))] = "fixture:missing"
check("migration refuses a dangling current lookup", not retained_slice_matches(registry["entries"], lookup))

bridge = read(PLAN / "BRIDGE.json")["mappings"]
findings = {row["id"] for row in read(AUDIT / "FINDINGS.json")["findings"]}
check("all ten findings have authored bridge mappings", {row["obligation"] for row in bridge} == findings)
for row in bridge:
    check("selected clauses " + row["obligation"], bool(row["definition_clauses"]))
    for declaration in row["language_declarations"]:
        header = declaration["kind"] + " " + declaration["name"] + ":"
        check("exact declaration role " + row["obligation"] + " " + declaration["name"], header in (PLAN / declaration["file"]).read_text().splitlines())
    for clause in row["definition_clauses"]:
        path = ROOT / clause["source"]["path"]
        check("exact clause source " + row["obligation"], bind(path) == clause["source"])
        value = read(path)
        for key in clause["selector"].split("/")[1:]:
            value = value[key]
        check("resolved clause " + row["obligation"], isinstance(value, str) and bool(value))

semantic_source = (PLAN / "alchlang/semantics.alch").read_text()
check("ordered outcome policies leave only the result constructor", [line for line in semantic_source.splitlines() if line.startswith("calculation ")] == ["calculation ChooseDecision:"])
check("owner dispositions remain pending", read(ORIGINAL / "DEFINE-PROCESS.json")["actual_owner_answers"] == 0)
index = read(PLAN / "INDEX.json")
for source in index["existing_artifacts"].values():
    check("existing artifact " + source, (ROOT / source).is_file())
table = read(PLAN / "JOIN-TRANSITIONS.json")
edges = re.findall(r"^  transition (\w+) (\w+) -> (\w+)$", semantic_source, re.M)
check("transition table covers the exact state-machine edges", edges == [(e["phase"], e["signal"], e["next_phase"]) for e in table["edges"]])
check("every edge declares evidence and at least one allowed outcome", all(e["predicate"] and e["domain"] and e["outcomes"] for e in table["edges"]))
projection = read(PLAN / "VERIFIED-PROJECTION.json")
check("full projection wire contracts are defined", {"VerifiedPlanningArtifact", "VerifiedPlanningReceipt"} <= set(schema["$defs"]))
check("projection source exists", (PLAN / projection["projection"]).is_file())
declared_receipts = {receipt for contract in projection["proof_contracts"].values() for receipt in contract["receipts"]}
check("every original receipt predicate specifies a complete subject", declared_receipts == set(projection["receipt_subjects"]))
previous = PLAN.with_name("shared-definitions-records-r2")
for item in read(previous / "MANIFEST.json")["files"]:
    check("preserved revision 2 " + item["path"], bind(ROOT / item["path"]) == item)
issuance = read(PLAN / "ISSUANCE-CONTRACT.json")
check("typed original receipt and issuance selection schemas", {"OriginalArtifactReceipt","IssuanceSelection","MemberProvenance"} <= set(schema["$defs"]))
check("typed journal proposal receipt and recovery schemas", {"JoinTransitionProposal","JoinJournalReceipt","JoinRecoveryObservation"} <= set(schema["$defs"]))
check("issuance covers all effect and recovery operations", {r["operation"] for r in issuance["routes"]} == {"PlanPublication", "SelectCompatibility", "PlanLifecycleImpact", "AssessConstructionEntry", "AssessConstructionCompletion", "AssessJoinTransition", "BeginJoinPlan", "PlanJoinContinuation"})
for route in issuance["routes"]:
    check("required predicates " + route["variant"], set(route["required_original_predicates"]) == set(route["source_subjects"]))
prior_revision = PLAN.with_name("shared-definitions-records-r3")
for item in read(prior_revision / "MANIFEST.json")["files"]:
    check("preserved revision 3 " + item["path"], bind(ROOT / item["path"]) == item)
check("tracked implementation and authority bytes unchanged", subprocess.check_output(["git","diff","HEAD","--name-only"], cwd=ROOT, text=True) == "")
receipt = {"status":"PASS","checks":checks,"check_count":len(checks),"scope":"Candidate contract and source verification. Migration fixtures cover unchanged retained entries and invalid deltas. Owner and runtime authority remain external."}
(PLAN / "CONTRACT-VERIFICATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(f"{len(checks)} contract and source checks passed")
