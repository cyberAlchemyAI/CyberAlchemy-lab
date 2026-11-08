import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const qualificationPath = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/l3-completion/qualification.json");
const sha256 = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");
const fileSha256 = (file: string) => sha256(fs.readFileSync(file));

function validate(value: any): void {
  assert.equal(value.schema_version, "alchlang.l3-completion-qualification/v1-candidate");
  assert.equal(value.task, "L3X"); assert.equal(value.result, "pass"); assert.equal(value.authority_effect, "none");
  assert.equal(fileSha256(path.join(repo, value.inherited_boundary.path)), value.inherited_boundary.sha256);
  assert.equal(value.inherited_boundary.task, "L2X"); assert.equal(value.inherited_boundary.result, "pass");
  assert.equal(fileSha256(path.join(repo, value.dag.path)), value.dag.sha256); assert.equal(value.dag.node, "L3X");
  assert.deepEqual(value.nodes.map((node: any) => node.id), ["E01", "E02", "E03", "E04", "E05"]);
  for (const node of value.nodes) {
    assert.equal(node.result, "pass", node.id);
    assert.equal(fileSha256(path.join(repo, node.completion_path)), node.completion_sha256, `${node.id} completion`);
    assert.equal(fileSha256(path.join(repo, node.evidence_path)), node.evidence_sha256, `${node.id} evidence`);
    const evidence = JSON.parse(fs.readFileSync(path.join(repo, node.evidence_path), "utf8"));
    assert.equal(evidence.task, node.id); assert.equal(evidence.result, "pass"); assert.equal(evidence.authority_effect, "none");
    assert.equal(sha256(evidence.claim_ceiling), node.claim_ceiling_sha256, `${node.id} claim ceiling`);
  }
  assert.deepEqual(value.denominators, { l3_nodes: 5, passed_l3_nodes: 5, inherited_obligations: 32,
    required_evidence_classes: 7, evf_route_outcome_cells: 16, runtime_stage_subsets: 16,
    missing: 0, failed: 0, skipped: 0 });
  assert.deepEqual(value.evidence_connected_candidate, { status: "construction-evidence-candidate", formal_evidence_bound: true,
    runtime_evidence_bound: true, cross_layer_qualification_bound: true, product_owner_validation_performed: false,
    product_approval_claimed: false, production_proof_claimed: false, release_admission: "not-granted", authority_effect: "none" });
  assert.deepEqual(value.validation.inherited_application_regression, { tests: 149, passed: 149, failed: 0, skipped: 0 });
  assert.deepEqual(value.validation.focused_l3_qualification, { tests: 2, passed: 2, failed: 0, skipped: 0 });
  assert.deepEqual(value.hard_stops, { missing_or_skipped_denominator: false, stale_node_evidence: false,
    claim_ceiling_widened: false, formal_evidence_described_as_product_approval: false,
    runtime_evidence_described_as_production_proof: false, authority_inferred_from_evidence: false });
  assert.match(value.claim_ceiling, /L3 evidence-connected construction candidate only/u); assert.equal(value.open_questions.length, 2);
}

test("L3X qualification joins E01-E05 with exact claim ceilings and no approval or production inference", () => {
  validate(JSON.parse(fs.readFileSync(qualificationPath, "utf8")));
});

test("L3X qualification rejects stale node evidence, missing denominators and widened authority claims", () => {
  const original = JSON.parse(fs.readFileSync(qualificationPath, "utf8"));
  for (const mutate of [
    (value: any) => { value.nodes[2].evidence_sha256 = "0".repeat(64); },
    (value: any) => { value.denominators.skipped = 1; },
    (value: any) => { value.nodes[3].claim_ceiling_sha256 = "f".repeat(64); },
    (value: any) => { value.evidence_connected_candidate.product_approval_claimed = true; },
    (value: any) => { value.evidence_connected_candidate.production_proof_claimed = true; },
  ]) {
    const changed = structuredClone(original); mutate(changed); assert.throws(() => validate(changed));
  }
});
