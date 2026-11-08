import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const qualificationPath = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/c06-hardening/qualification.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

test("C06 qualification binds the closed hostile corpus, current implementation and claim ceiling", () => {
  const value = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  assert.equal(value.schema_version, "alchlang.c06-hardening-qualification/v1-candidate");
  assert.equal(value.task, "C06"); assert.equal(value.result, "pass"); assert.equal(value.authority_effect, "none");
  for (const binding of Object.values(value.bindings) as Array<{ path: string; sha256: string }>) {
    assert.equal(sha256(path.join(repo, binding.path)), binding.sha256, binding.path);
  }
  assert.equal(sha256(path.join(repo, value.adversarial_corpus.path)), value.adversarial_corpus.sha256);
  const corpus = JSON.parse(fs.readFileSync(path.join(repo, value.adversarial_corpus.path), "utf8"));
  assert.equal(corpus.cases.length, 16);
  assert.deepEqual({cases: value.adversarial_corpus.cases, passed: value.adversarial_corpus.passed,
    failed: value.adversarial_corpus.failed, skipped: value.adversarial_corpus.skipped},
  {cases: 16, passed: 16, failed: 0, skipped: 0});
  assert.equal(new Set(corpus.cases.map((row: any) => row.id)).size, 16);
  assert.equal(value.currentness_receipt.schema_version, "alchlang.application-currentness-receipt/v1-candidate");
  assert.equal(value.currentness_receipt.repeat_build_inventories_equal, true);
  assert.equal(value.currentness_receipt.unsupported_residue_count, 0);
  assert.deepEqual(value.validation.focused, {tests: 2, passed: 2, failed: 0, skipped: 0});
  assert.deepEqual({tests: value.validation.application_regression.tests, passed: value.validation.application_regression.passed,
    failed: value.validation.application_regression.failed, skipped: value.validation.application_regression.skipped},
  {tests: 108, passed: 108, failed: 0, skipped: 0});
  assert.equal(value.validation.parallel_attempt.used_as_completion_evidence, false);
  assert.deepEqual(value.hard_stops, {partial_output_appears_complete: false, failed_build_mutates_destination: false});
  assert.match(value.claim_ceiling, /does not establish installed-package behavior/u);
  assert.ok(value.open_questions.length > 0);
});

test("C06 qualification validator rejects stale bindings and missing hostile cases", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.bindings.application_output.sha256 = "0".repeat(64); },
    (value: any) => { value.adversarial_corpus.cases = 15; },
    (value: any) => { value.hard_stops.failed_build_mutates_destination = true; },
  ]) {
    const changed = structuredClone(original); mutate(changed);
    assert.throws(() => {
      for (const binding of Object.values(changed.bindings) as Array<{ path: string; sha256: string }>) assert.equal(sha256(path.join(repo, binding.path)), binding.sha256);
      assert.equal(changed.adversarial_corpus.cases, 16);
      assert.deepEqual(changed.hard_stops, {partial_output_appears_complete: false, failed_build_mutates_destination: false});
    });
  }
});
