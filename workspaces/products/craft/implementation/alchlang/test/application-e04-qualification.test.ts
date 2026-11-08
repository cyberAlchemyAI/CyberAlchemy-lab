import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const evidenceRoot = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/e04-runtime-observation-join";
const qualificationPath = path.join(repo, evidenceRoot, "qualification.v4-candidate.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const expectedBindings = ["implementation", "focused_test", "join_schema", "cleanup_schema",
  "domainspec_observation_schema", "mapping_document"];

function exact(binding: { path: string; sha256: string }): void {
  assert.match(binding.sha256, /^[0-9a-f]{64}$/u);
  assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
}

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.e04-runtime-observation-join-qualification/v4-candidate");
  assert.equal(value.task, "E04");
  assert.equal(value.result, "scoped-pass");
  assert.equal(value.authority_effect, "none");
  assert.equal(value.supersedes.path, `${evidenceRoot}/qualification.v3-candidate.json`);
  exact(value.supersedes);
  const predecessor = JSON.parse(fs.readFileSync(path.join(repo, value.supersedes.path), "utf8"));
  const expected = structuredClone(predecessor);
  expected.schema_version = "alchlang.e04-runtime-observation-join-qualification/v4-candidate";
  expected.date = "2026-10-06";
  expected.supersedes = { path: `${evidenceRoot}/qualification.v3-candidate.json`,
    sha256: sha256(path.join(repo, value.supersedes.path)) };
  expected.inherited_boundary.path = "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/e03-evf-evidence-join/qualification.v4-candidate.json";
  expected.inherited_boundary.sha256 = sha256(path.join(repo, expected.inherited_boundary.path));
  assert.deepEqual(value, expected);
  assert.deepEqual(value.bindings, predecessor.bindings);
  assert.deepEqual(value.coverage, predecessor.coverage);
  assert.equal(value.inherited_boundary.path,
    "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/e03-evf-evidence-join/qualification.v4-candidate.json");
  assert.match(value.inherited_boundary.qualified_scope, /execution-evidence\/pass is blocked/u);
  exact(value.inherited_boundary);
  assert.equal(value.dag.node, "E04");
  exact(value.dag);
  assert.deepEqual(Object.keys(value.bindings).sort(), expectedBindings.slice().sort());
  for (const binding of Object.values(value.bindings) as Array<{ path: string; sha256: string }>) exact(binding);
  assert.deepEqual(value.coverage, {
    independent_stage_slots: 4, single_stage_independence_cells: 4, complete_stage_cells: 4,
    schemas_validated: 3, static_binding_classes: 7, focused_runtime_observation_tests: 9,
    missing: 0, failed: 0, skipped: 0,
  });
  assert.deepEqual(Object.keys(value.stage_accounting),
    ["application_commit", "provider_acceptance", "transport_delivery", "business_completion"]);
  for (const stage of Object.values(value.stage_accounting) as any[]) assert.equal(stage.inferred_from_other_stage, false);
  assert.deepEqual(value.run_coherence, {
    observed_stage_receipts_match_cleanup_run: true,
    independent_cleanup_observation_by_join: false,
    inferred_causal_chain: false,
  });
  assert.deepEqual(value.validation.focused_runtime_observation, { tests: 9, passed: 9, failed: 0, skipped: 0 });
  assert.equal(value.validation.full_application_regression, "not-claimed");
  assert.deepEqual(value.hard_stops, {
    stage_inferred_from_another: false, receipt_or_observation_identity_mismatch_accepted: false,
    unobserved_stage_reported_as_observed: false, orodi_return_edge_present: false,
    orodi_runtime_control_present: false, cleanup_residue_omitted: false,
    cross_run_stage_join_accepted: false, runtime_executed_by_join: false,
    evidence_treated_as_product_approval_or_authority: false,
  });
  assert.match(value.claim_ceiling, /supplied stage receipts, observations and cleanup evidence only/u);
  assert.match(value.claim_ceiling, /execution-evidence\/pass remains blocked/u);
  assert.equal(value.open_questions.length, 2);
}

test("E04 successor binds current stage separation and same-run evidence without historical regression promotion", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("E04 successor rejects stale sources, missing stages, cross-run joins and ORODI control", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.bindings.implementation.sha256 = "0".repeat(64); },
    (value: any) => { value.stage_accounting.application_commit.domain_stage = "transport-delivered"; },
    (value: any) => { delete value.bindings.mapping_document; },
    (value: any) => { value.coverage.independent_stage_slots = 3; },
    (value: any) => { value.stage_accounting.transport_delivery.inferred_from_other_stage = true; },
    (value: any) => { value.run_coherence.observed_stage_receipts_match_cleanup_run = false; },
    (value: any) => { value.hard_stops.orodi_runtime_control_present = true; },
    (value: any) => { value.validation.full_application_regression = "pass"; },
  ]) {
    const changed = structuredClone(original);
    mutate(changed);
    assert.throws(() => validate(changed));
  }
});
