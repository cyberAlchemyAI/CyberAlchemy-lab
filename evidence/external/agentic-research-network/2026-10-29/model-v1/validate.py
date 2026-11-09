#!/usr/bin/env python3
"""Structural and local-reference checks for the ARN candidate package."""

import json
import hashlib
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
CATALOG = json.loads((ROOT / "artifact-types.json").read_text())
DEFINITIONS = json.loads((ROOT / "definitions.json").read_text())


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def check_schema(path, record):
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda e: list(map(str, e.path)))
    if errors:
        fail(f"{path}: {errors[0].message} at {'/'.join(map(str, errors[0].path))}")


ids = [entry["id"] for entry in DEFINITIONS["definitions"]]
if len(ids) != len(set(ids)) or any(not entry.get("formal_definition") or not entry.get("operational_interpretation") or not entry.get("intuition") for entry in DEFINITIONS["definitions"]):
    fail("definitions require unique IDs and three meaning voices")
if DEFINITIONS["status"] != "candidate-unadmitted" or DEFINITIONS["authority_effect"] != "none":
    fail("definitions must remain candidate-only")

proposed = CATALOG["proposed_types"]
if len({entry["artifact_type_ref"] for entry in proposed}) != len(proposed):
    fail("duplicate proposed type")
for entry in proposed:
    if entry["semantic_definition_ref"] not in ids:
        fail(f"missing meaning for {entry['artifact_type_ref']}")
    if entry["admission_status"] != "candidate-unadmitted":
        fail("candidate type claims admission")
    Draft202012Validator.check_schema(json.loads((ROOT / entry["schema_path"]).read_text()))

schema_by_discriminator = {}
for entry in proposed:
    schema = ROOT / entry["schema_path"]
    discriminator = json.loads(schema.read_text())["properties"]["schema_version"]["const"]
    schema_by_discriminator[discriminator] = schema
for kind in CATALOG["reused_lab_types"]:
    ref = CATALOG["reused_lab_types"][kind]
    name, version = ref.removeprefix("cal.artifact-type.").split("/")
    path = REPO / "authority" / "artifact-types" / name / version / "schema.json"
    if not path.is_file():
        fail(f"missing admitted Lab schema for {kind}: {path}")
    discriminator = json.loads(path.read_text())["properties"].get("schema_version", {}).get("const")
    if discriminator:
        schema_by_discriminator[discriminator] = path

records = {}
for path in sorted((ROOT / "records").glob("*.json")):
    record = json.loads(path.read_text())
    if record.get("status") != "candidate-unadmitted" or record.get("authority_effect") != "none":
        fail(f"{path.name} claims authority")
    discriminator = record.get("schema_version")
    if discriminator:
        schema = schema_by_discriminator.get(discriminator)
        if not schema:
            fail(f"{path.name} has no declared schema: {discriminator}")
        check_schema(schema, record)
    elif record.get("kind") == "research-inquiry":
        check_schema(REPO / "authority/artifact-types/research-inquiry/v1/schema.json", record)
    elif record.get("kind") == "experiment-design":
        check_schema(REPO / "authority/artifact-types/experiment-design/v1/schema.json", record)
    elif record.get("kind") == "product-thesis":
        check_schema(REPO / "authority/artifact-types/product-thesis/v1/schema.json", record)
    else:
        fail(f"{path.name} has no recognized type")
    for key in ("record_id", "project_id", "product_id", "goal_id", "node_id"):
        if key in record:
            if record[key] in records:
                fail(f"duplicate record identity {record[key]}")
            records[record[key]] = path.name

expected = {"product-identity", "product-thesis", "project-identity", "research-inquiry", "research-inquiry-circular-economy", "experiment-design", "research-program", "research-charter", "program-budget", "novelty-rules", "reward-policy", "participation-policy", "revenue-policy", "service-redemption-policy", "funder-instrument-policy", "rights-policy", "disclosure-snapshot", "goal-01", "goal-02", "goal-03"}
if expected - {path.stem for path in (ROOT / "records").glob("*.json")}:
    fail("missing initial records")
if {"work-award", "participation-allocation", "revenue-statement", "settlement", "novelty-review"} & {path.stem for path in (ROOT / "records").glob("*.json")}:
    fail("unadjudicated award, revenue, settlement or review in initial records")

for path in sorted((ROOT / "fixtures").glob("*.json")):
    record = json.loads(path.read_text())
    if record.get("subject_ref") != "fixture:synthetic-only":
        fail(f"{path.name} is not marked synthetic")
    schema = schema_by_discriminator.get(record.get("schema_version"))
    if not schema:
        fail(f"{path.name} has no declared schema")
    check_schema(schema, record)

rules = json.loads((ROOT / "records/novelty-rules.json").read_text())["data"]["rules"]
if [rule["id"] for rule in rules] != [f"NR-{i:02d}" for i in range(1, 8)]:
    fail("novelty rules are incomplete or out of order")

project = json.loads((ROOT / "records/project-identity.json").read_text())
product = json.loads((ROOT / "records/product-identity.json").read_text())
program = json.loads((ROOT / "records/research-program.json").read_text())
charter = json.loads((ROOT / "records/research-charter.json").read_text())
if program["subject_ref"] != project["project_id"] or program["data"]["product_ref"] != product["product_id"]:
    fail("program does not bind the intended Project and Product")
if program["data"]["charter_ref"] != charter["record_id"] or charter["data"]["novelty_rules_ref"] != "novelty-rules:arn:0.1":
    fail("program, charter and novelty rule references do not close")
participation = json.loads((ROOT / "records/participation-policy.json").read_text())
revenue = json.loads((ROOT / "records/revenue-policy.json").read_text())
if participation["data"]["revenue_policy_ref"] != revenue["record_id"]:
    fail("participation and revenue policies are not linked")
if revenue["data"]["share_bps"] is not None or revenue["data"]["fixed_unit_cap"] is not None:
    fail("unapproved live revenue parameters were set")
funder = json.loads((ROOT / "records/funder-instrument-policy.json").read_text())
if funder["data"]["instrument_kind"] != "undecided" or funder["data"]["funder_share_bps"] is not None:
    fail("unapproved funder instrument or share was set")
redemption = json.loads((ROOT / "records/service-redemption-policy.json").read_text())
if any(redemption["data"][key] is not None for key in ("price_w_units", "capacity_units", "marginal_cost_c_units", "service_budget_c_units")):
    fail("unapproved live service redemption parameters were set")

simulation_schema = ROOT / "economics/simulation-policy.schema.json"
simulation_policy = json.loads((ROOT / "economics/simulation-policy.json").read_text())
check_schema(simulation_schema, simulation_policy)
if simulation_policy["status"] != "simulation-only":
    fail("economic parameter example claims activation")
transaction_schema = ROOT / "economics/schemas/ledger-transaction.schema.json"
transaction_paths = sorted((ROOT / "economics/fixtures/transactions").glob("*.json"))
if len(transaction_paths) != 10:
    fail("synthetic transaction fixture count changed")
for path in transaction_paths:
    check_schema(transaction_schema, json.loads(path.read_text()))
economic_fixtures = {}
for path in sorted((ROOT / "economics/fixtures").glob("*.json")):
    if path.name in ("scenario.json", "loop-results.json", "multi-sponsor-results.json"):
        continue
    record = json.loads(path.read_text())
    if record.get("subject_ref") != "fixture:synthetic-only":
        fail(f"{path.name} is not marked synthetic")
    schema = schema_by_discriminator.get(record.get("schema_version"))
    if not schema:
        fail(f"{path.name} has no declared economic schema")
    check_schema(schema, record)
    economic_fixtures[path.stem] = record
task = economic_fixtures["mining-task-offer"]
epoch = economic_fixtures["mining-epoch"]
commitment = economic_fixtures["submission-commitment"]
reveal = economic_fixtures["submission-reveal"]
statement = economic_fixtures["epoch-statement"]
if task["data"]["epoch_ref"] != epoch["record_id"] or commitment["data"]["task_ref"] != task["record_id"] or reveal["data"]["commitment_ref"] != commitment["record_id"]:
    fail("economic fixture chain does not close")
if statement["data"]["ledger_root_digest"] != json.loads(transaction_paths[2].read_text())["data"]["event_digest"]:
    fail("epoch statement does not bind the task award ledger cut")
commit_body = ["arn-commit/v1", task["record_id"], commitment["data"]["slot_id"],
               commitment["data"]["miner_ref"], reveal["data"]["content_digest"], reveal["data"]["nonce"]]
computed_commitment = hashlib.sha256(json.dumps(commit_body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
if computed_commitment != commitment["data"]["commitment_digest"]:
    fail("synthetic commitment does not match reveal")

sys.path.insert(0, str(ROOT / "economics"))
from loop_scenarios import report as loop_report
from multi_sponsor_scenarios import report as multi_sponsor_report

stored_loop_result = json.loads((ROOT / "economics/fixtures/loop-results.json").read_text())
if stored_loop_result != loop_report():
    fail("synthetic loop result does not match executable model and scenarios")
stored_multi_sponsor_result = json.loads((ROOT / "economics/fixtures/multi-sponsor-results.json").read_text())
if stored_multi_sponsor_result != multi_sponsor_report():
    fail("synthetic multi-sponsor result does not match executable model and scenarios")

governance_check = subprocess.run(
    [sys.executable, str(ROOT / "governance/validate.py")],
    capture_output=True, text=True, check=False,
)
if governance_check.returncode:
    fail(governance_check.stderr.strip() or governance_check.stdout.strip())
ea_check = subprocess.run(
    [sys.executable, str(ROOT / "product-001-ea/validate.py")],
    capture_output=True, text=True, check=False,
)
if ea_check.returncode:
    fail(ea_check.stderr.strip() or ea_check.stdout.strip())

print(f"PASS: {len(ids)} candidate definitions; {len(proposed)} candidate types; {len(records)} candidate records; 3 research fixtures, {len(economic_fixtures)} economic fixtures and {len(transaction_paths)} synthetic transactions; schemas, core references and authority bounds checked.")
print(f"PASS loop: {len(stored_loop_result['cases'])} synthetic cases match the saved cash and asset-cycle result.")
print(f"PASS multi-sponsor: {len(stored_multi_sponsor_result['cases'])} synthetic cases match the saved Product 001 sponsor result.")
print(ea_check.stdout.strip())
print(governance_check.stdout.strip())
print("Scope: structural and local-reference readiness only; no Lab admission, empirical result, legal entitlement, token issuance or payment.")
