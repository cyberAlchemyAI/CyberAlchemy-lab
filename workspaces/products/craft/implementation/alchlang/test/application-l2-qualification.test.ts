import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const qualificationPath = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/l2-completion/qualification.json");
const sha256 = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.l2-completion-qualification/v1-candidate");
  assert.equal(value.task, "L2X"); assert.equal(value.result, "pass"); assert.equal(value.authority_effect, "none");
  assert.equal(sha256(path.join(repo, value.inherited_boundary.path)), value.inherited_boundary.sha256);
  assert.equal(sha256(path.join(repo, value.dag.path)), value.dag.sha256);
  assert.deepEqual(value.nodes.map((node: any) => node.id), ["C01", "C02", "C03", "C04", "C05", "C06"]);
  assert.ok(value.nodes.every((node: any) => node.result === "pass"));
  for (const node of value.nodes) {
    assert.equal(sha256(path.join(repo, node.completion_path)), node.completion_sha256, `${node.id} completion`);
    assert.equal(sha256(path.join(repo, node.evidence_path)), node.evidence_sha256, `${node.id} evidence`);
  }
  assert.deepEqual(value.denominators, {l2_nodes: 6, passed_l2_nodes: 6, backend_metatypes: 13, formal_syntax_cases: 18,
    domain_realization_cells: 39, application_target_languages: 3, adversarial_cases: 16, missing: 0, failed: 0, skipped: 0});
  assert.deepEqual(value.core_product_boundary.languages, ["typescript", "python", "rust"]);
  assert.equal(value.core_product_boundary.profile, "application-v1");
  assert.equal(value.core_product_boundary.optional_profiles_advertised_as_core, false);
  assert.deepEqual(value.hard_stops, {optional_prototype_advertised_as_core: false, missing_or_skipped_denominator: false,
    runtime_inferred_from_compilation: false, authority_inferred_from_evidence: false});
  assert.match(value.claim_ceiling, /L2 construction completion only/u);
  assert.equal(value.open_questions.length, 2);
}

test("L2X qualification joins every C01-C06 obligation without promoting optional prototypes", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("L2X qualification validator rejects stale node evidence, a missing denominator and prototype promotion", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.nodes[4].evidence_sha256 = "0".repeat(64); },
    (value: any) => { value.denominators.skipped = 1; },
    (value: any) => { value.core_product_boundary.optional_profiles_advertised_as_core = true; },
  ]) {
    const changed = structuredClone(original); mutate(changed); assert.throws(() => validate(changed));
  }
});
