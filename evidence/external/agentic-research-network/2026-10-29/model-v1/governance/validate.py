#!/usr/bin/env python3
"""Structural and cross-reference checks for the candidate governance package."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[5]
STAGES = {"proposer", "reviewers", "approvers", "executors"}


def fail(message):
    raise SystemExit(f"FAIL governance: {message}")


def load(name, schema_path):
    path = ROOT / name
    value = json.loads(path.read_text())
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value),
                    key=lambda error: list(map(str, error.path)))
    if errors:
        error = errors[0]
        fail(f"{name}: {error.message} at {'/'.join(map(str, error.path))}")
    return value


def local(name, schema_name):
    return load(name, ROOT / "schemas" / f"{schema_name}.schema.json")


actors = local("actors.json", "actor-map")
rules = local("rules.json", "governance-rules")
profile = local("decision-rights.json", "decision-rights-profile")
context = load("context.json", REPO / "authority/artifact-types/context/v1/schema.json")
policy = load("policy.json", REPO / "authority/artifact-types/policy/v1/schema.json")

project = actors["project_ref"]
if any(value["project_ref"] != project for value in (rules, profile, context)):
    fail("project scope differs across governance records")
if policy["scope_ref"] != project or profile["policy_ref"] != policy["node_id"]:
    fail("policy scope or decision-rights policy reference is broken")
if profile["role_registry_ref"] != "governance/actors.json":
    fail("role registry reference changed")
if context["node_id"] not in [entry["counterpart_ref"] for entry in policy["relation_refs"]]:
    fail("policy does not reference governance context")
if any(value.get("authority_effect") != "none" for value in
       (actors, rules, profile, context, policy)):
    fail("a candidate record claims authority")

role_ids = [role["role_id"] for role in actors["roles"]]
if len(role_ids) != len(set(role_ids)):
    fail("duplicate role ID")
if any(role["assignment_state"] != "unassigned" for role in actors["roles"]):
    fail("candidate role appears assigned")
role_paths = sorted((ROOT / "roles").glob("*.json"))
role_records = [load(str(path.relative_to(ROOT)),
                     REPO / "authority/artifact-types/role/v1/schema.json")
                for path in role_paths]
if {record["node_id"] for record in role_records} != set(role_ids):
    fail("role records and actor map differ")
if len(role_records) != len(role_ids):
    fail("duplicate or missing role record")
mapped_roles = {role["role_id"]: role for role in actors["roles"]}
for record in role_records:
    mapped = mapped_roles[record["node_id"]]
    if (record["functions"] != mapped["functions"] or
            record["exclusions"] != mapped["exclusions"] or
            record["scope_ref"] != project or
            record["status"] != "candidate-unadmitted" or
            record["authority_effect"] != "none" or
            record["lifecycle_state"] != "draft"):
        fail(f"role record drift: {record['node_id']}")

rule_ids = [rule["rule_id"] for rule in rules["rules"]]
if rule_ids != [f"ARN-G{index:02d}" for index in range(1, 18)]:
    fail("governance rule registry is incomplete, duplicated or unordered")
if policy["payload"]["rule_refs"] != rule_ids:
    fail("policy rule references differ from registry")
if any(rule["owner_role_ref"] not in mapped_roles for rule in rules["rules"]):
    fail("governance rule owner role missing")

expected_actions = {
    "program.charter.admit", "mining.task.offer", "work.award",
    "research.advance.allocate", "revenue.statement.approve", "stablecoin.payout",
    "policy.change", "emergency.pause", "emergency.resume", "appeal.resolve",
    "data.use.approve", "funder.instrument.approve", "service.redemption.policy",
}
actions = profile["actions"]
if len(actions) != len(expected_actions) or {a["action_id"] for a in actions} != expected_actions:
    fail("decision-rights action set is missing, duplicated or expanded")
for action in actions:
    if not action["proposer_roles"] or not action["approver_quorum"]:
        fail(f"{action['action_id']} lacks proposer or approver")
    for role in action["proposer_roles"]:
        if role not in mapped_roles:
            fail(f"{action['action_id']} has unknown proposer role")
    for stage in ("reviewer_quorum", "approver_quorum", "executor_quorum"):
        if any(entry["role_ref"] not in mapped_roles for entry in action[stage]):
            fail(f"{action['action_id']} has unknown {stage} role")
    for left, right in action["separation_pairs"]:
        if left not in STAGES or right not in STAGES or left == right:
            fail(f"{action['action_id']} has invalid separation pair")
    if action["max_duration_seconds"] is not None and action["action_id"] != "emergency.pause":
        fail(f"{action['action_id']} has unexpected bounded duration")
    if action["action_id"] == "emergency.pause" and not action["max_duration_seconds"]:
        fail("emergency pause needs a positive maximum duration")

for name, schema in (("conflict-disclosure", "conflict-disclosure"),
                     ("appeal-case", "appeal-case")):
    record = local(f"fixtures/{name}.json", schema)
    if record["subject_ref"] != "fixture:synthetic-only" or record["authority_effect"] != "none":
        fail(f"{name} is not synthetic and non-authorizing")

print(f"PASS governance: {len(role_records)} candidate roles, {len(rule_ids)} rules, "
      f"{len(actions)} action routes, 2 synthetic fixtures; schemas and references checked.")
print("Scope: no admitted policy, assigned Principal, operative Decision or asset movement.")
