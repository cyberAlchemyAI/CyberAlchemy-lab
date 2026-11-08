import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const qualificationPath = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/e01-verification-profile/qualification.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.e01-verification-profile-qualification/v1-candidate");
  assert.equal(value.task, "E01"); assert.equal(value.result, "pass"); assert.equal(value.authority_effect, "none");
  assert.equal(sha256(path.join(repo, value.inherited_boundary.path)), value.inherited_boundary.sha256);
  assert.equal(sha256(path.join(repo, value.dag.path)), value.dag.sha256);
  for (const binding of Object.values(value.bindings) as Array<{ path: string; sha256: string }>) {
    assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
  }
  assert.deepEqual(value.coverage.exact_external_reference_roles, ["route", "provider", "runtime"]);
  assert.deepEqual(value.coverage.emitted_artifacts, ["evaluation-context", "verification-request", "source-trace"]);
  assert.deepEqual({missing: value.coverage.missing, failed: value.coverage.failed, skipped: value.coverage.skipped}, {missing: 0, failed: 0, skipped: 0});
  assert.deepEqual(value.identity_evidence, {
    same_formal_claim_identity_across_provider_variants: true,
    different_evaluation_context_digest_across_provider_variants: true,
    different_verification_request_digest_across_provider_variants: true,
    provider_is_formal_claim_identity_input: false,
  });
  assert.deepEqual(value.request_boundary, {request_state: "ready", provider_execution_observed: false,
    evaluation_result_observed: false, release_admission: "not-granted", runtime_guarantees_observed: false, authority_effect: "none"});
  assert.deepEqual(value.validation.focused_e01_and_formal_identity, {tests: 13, passed: 13, failed: 0, skipped: 0});
  assert.deepEqual({tests: value.validation.application_regression.tests, passed: value.validation.application_regression.passed,
    failed: value.validation.application_regression.failed, skipped: value.validation.application_regression.skipped},
  {tests: 120, passed: 120, failed: 0, skipped: 0});
  assert.deepEqual(value.hard_stops, {provider_changes_formal_claim_identity: false, unresolved_or_stale_reference_accepted: false,
    ambient_provider_or_runtime_inferred: false, request_claims_execution_or_result: false, authority_or_release_admission_inferred: false});
  assert.match(value.claim_ceiling, /E01 construction evidence only/u);
  assert.equal(value.open_questions.length, 2);
}

test("E01 qualification binds exact verification-profile construction and non-collapse evidence", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("E01 qualification rejects stale implementation, claim-identity collapse and inferred execution", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.bindings.implementation.sha256 = "0".repeat(64); },
    (value: any) => { value.identity_evidence.provider_is_formal_claim_identity_input = true; },
    (value: any) => { value.request_boundary.provider_execution_observed = true; },
  ]) {
    const changed = structuredClone(original); mutate(changed); assert.throws(() => validate(changed));
  }
});
