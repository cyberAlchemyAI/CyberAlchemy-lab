import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import test from "node:test";
import {fileURLToPath} from "node:url";

import {composeContextLifecycle} from "../../context-basis-runtime/index.mjs";
import {loadVerifiedDecisionProfile} from "../../request-decision-router/index.mjs";
import {
  bindSemanticRequestToContextEnvelope,
  digestValue,
  evaluateContextBoundSemanticJudgment,
  evaluateSemanticJudgment,
  omitDigestFields,
  OUTCOMES,
  sealRecord,
} from "../index.mjs";
import {buildRequest, readFixture} from "./fixture-builder.mjs";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const contextRoot = resolve(packageRoot, "../context-basis-runtime");
const profileResult = loadVerifiedDecisionProfile(resolve(packageRoot, "../request-decision-router/profiles/cyberalchemy-v1.json"), repositoryRoot);
assert.equal(profileResult.ok, true, profileResult.reason_codes?.join(","));
const catalog = JSON.parse(readFileSync(resolve(contextRoot, "test/fixtures/definition-catalog.json"), "utf8"));
const ontology = JSON.parse(readFileSync(resolve(contextRoot, "test/fixtures/ontology-snapshot.json"), "utf8"));
const refund = await readFixture(new URL("../../../fixtures/evaluator-v1/refund-eligibility.json", import.meta.url));

function contextEnvelope(overrides = {}) {
  const result = composeContextLifecycle({
    request_context: {schema_version: "are.request-context/v1", request_id: "SEM-CTX-1", raw_request: "Research current context management approaches.", objective_kind: null, requested_effects: [], target_refs: [], constraints: [], evidence_refs: ["test"]},
    decision_profile: profileResult.value,
    definition: {catalog, seed_definition_ids: ["RequestContext"], universal_relation_classes: ["requires"], route_relation_classes_by_route: {"CA2-ROUTE-RESEARCH": ["route-context"]}},
    ontology: {snapshot: ontology, initial_node_ids: ["Request"], required_edge_ids: [], omission_candidate_ids: ["Unrelated"]},
    authority_posture: "candidate-context-only",
    effect_posture: "non-effectful",
    view: {lane: "plan-bound", consumer_ref: "semantic:test", window_ref: "semantic:window", purpose: "semantic-evaluation", source_epoch: "epoch:semantic:1", turn_id: "turn:semantic:1"},
    current_sources: [
      {source_identity: catalog.source_identity, source_digest: catalog.source_digest},
      {source_identity: ontology.source_identity, source_digest: ontology.snapshot_digest},
    ],
    contradictions: [{ref: "contradiction:test"}],
    exclusions: [{ref: "optional:test", reason: "not-required"}],
    gaps: [{ref: "gap:test"}],
    residue: [{ref: "residue:test"}],
    ...overrides,
  });
  assert.equal(result.ok, true);
  return result.value.context_envelope;
}

function staleEnvelope(envelopeResult) {
  const value = structuredClone(envelopeResult.value);
  value.freshness_state = "stale";
  delete value.context_epoch_id;
  value.context_epoch_id = `context-epoch:${digestValue(value)}`;
  return {schema_version: "are.context-envelope/v1", ok: true, value, digest: digestValue(value), inline_bytes: value.inline_bytes, authority_effect: "none"};
}

test("a real Context Envelope deterministically drives semantic evaluation and receipt binding", () => {
  const envelope = contextEnvelope();
  const request = buildRequest(refund);
  const originalFrameDigest = request.frame.digest;
  const first = evaluateContextBoundSemanticJudgment({context_envelope: envelope, semantic_request: request}, {});
  const second = evaluateContextBoundSemanticJudgment({context_envelope: envelope, semantic_request: request}, {});
  assert.equal(first.ok, true);
  assert.equal(first.semantic.outcome, OUTCOMES.RECOMMENDED);
  assert.equal(first.evaluator_calls, 1);
  assert.equal(first.request.context_envelope_binding.context_envelope_digest, envelope.digest);
  assert.equal(first.reasoning_receipt.context_epoch_id, envelope.value.context_epoch_id);
  assert.equal(first.reasoning_receipt.input_digests.context_envelope, envelope.digest);
  assert.equal(first.reasoning_receipt.context_envelope_binding_digest, first.request.context_envelope_binding.digest);
  assert.equal(first.reasoning_receipt.input_digests.context_envelope_binding, first.request.context_envelope_binding.digest);
  assert.deepEqual(first.reasoning_receipt.input_digests.context_items, [...envelope.value.included_item_digests].sort());
  assert.equal(first.reasoning_receipt_exact_bytes_digest, second.reasoning_receipt_exact_bytes_digest);
  assert.equal(request.frame.digest, originalFrameDigest);
  assert.equal(Object.isFrozen(first.request), true);
});

test("envelope or Context Item substitution blocks before an evaluator call", () => {
  const envelope = structuredClone(contextEnvelope());
  envelope.value.included_items[0].content.text = "substituted context";
  const telemetry = {};
  const result = evaluateContextBoundSemanticJudgment({context_envelope: envelope, semantic_request: buildRequest(refund)}, telemetry);
  assert.equal(result.ok, false);
  assert.equal(result.reason_codes.includes("context.envelope-digest-mismatch"), true);
  assert.equal(result.reason_codes.includes("context.item-digest-mismatch"), true);
  assert.equal(telemetry.evaluator_calls ?? 0, 0);
});

test("a cryptographically valid but stale envelope is rejected before evaluation", () => {
  const telemetry = {};
  const result = evaluateContextBoundSemanticJudgment({context_envelope: staleEnvelope(contextEnvelope()), semantic_request: buildRequest(refund)}, telemetry);
  assert.equal(result.ok, false);
  assert.deepEqual(result.reason_codes, ["context.envelope-not-current"]);
  assert.equal(telemetry.evaluator_calls ?? 0, 0);
});

test("a bound ProblemFrame cannot be replaced without invalidating semantic input", () => {
  const bound = bindSemanticRequestToContextEnvelope({context_envelope: contextEnvelope(), semantic_request: buildRequest(refund)});
  assert.equal(bound.ok, true);
  const request = structuredClone(bound.value);
  request.frame = sealRecord({...omitDigestFields(request.frame), question: "Substituted after binding?"});
  const semantic = evaluateSemanticJudgment(request, {});
  assert.equal(semantic.outcome, OUTCOMES.INVALID_INPUT);
  assert.equal(semantic.residue.includes("context-envelope-binding:mismatch"), true);
});

test("a separately resealed entry gate cannot replace the bound frame subject", () => {
  const bound = bindSemanticRequestToContextEnvelope({context_envelope: contextEnvelope(), semantic_request: buildRequest(refund)});
  assert.equal(bound.ok, true);
  const request = structuredClone(bound.value);
  request.entry_gate = sealRecord({...omitDigestFields(request.entry_gate), subject_digest: "0".repeat(64)});
  const semantic = evaluateSemanticJudgment(request, {});
  assert.equal(semantic.outcome, OUTCOMES.INVALID_INPUT);
  assert.equal(semantic.residue.includes("context-envelope-binding:mismatch"), true);
});

test("context contradictions, exclusions, gaps, and residue are bound without being promoted to facts", () => {
  const envelope = contextEnvelope();
  const bound = bindSemanticRequestToContextEnvelope({context_envelope: envelope, semantic_request: buildRequest(refund)});
  assert.equal(bound.ok, true);
  assert.equal(bound.binding.contradictions_digest, digestValue(envelope.value.contradictions));
  assert.equal(bound.binding.exclusions_digest, digestValue(envelope.value.exclusions));
  assert.equal(bound.binding.gaps_digest, digestValue(envelope.value.gaps));
  assert.equal(bound.binding.residue_digest, digestValue(envelope.value.residue));
  assert.equal(Object.hasOwn(bound.value.frame, "facts"), false);
  assert.equal(bound.binding.authority_effect, "none");
});
