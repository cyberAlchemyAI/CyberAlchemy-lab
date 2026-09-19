import {
  digestValue,
  omitDigestFields,
  sealRecord,
  verifyRecordDigest,
} from "./canonical-json.mjs";
import {assembleReasoningReceipt} from "./receipt.mjs";
import {EVALUATOR_ID, evaluateSemanticJudgment, SCHEMA_VERSION} from "./reducer.mjs";

export const CONTEXT_ENVELOPE_SCHEMA = "are.context-envelope/v1";
export const CONTEXT_BINDING_RECORD = "ContextEnvelopeBinding";
export const CONTEXT_BOUND_EVALUATION_SCHEMA = "are.context-bound-semantic-evaluation/v1";

function deepFreeze(value) {
  if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
  Object.freeze(value);
  for (const child of Object.values(value)) deepFreeze(child);
  return value;
}

function failure(reasonCodes, residue = []) {
  return deepFreeze({
    schema_version: CONTEXT_BOUND_EVALUATION_SCHEMA,
    ok: false,
    stage: "context-envelope-binding",
    reason_codes: [...new Set(reasonCodes)].sort(),
    residue,
    evaluator_calls: 0,
    authority_effect: "none",
  });
}

function unique(values) {
  return new Set(values).size === values.length;
}

function verifyItem(item) {
  if (!item || typeof item !== "object" || item.schema_version !== "are.context-item/v1") return "context.item-schema-invalid";
  if (typeof item.item_digest !== "string") return "context.item-digest-mismatch";
  if (item.authority_effect !== "none") return "context.item-authority-effect-forbidden";
  return null;
}

function itemDigest(item) {
  const {item_digest: _digest, ...value} = item;
  return digestValue(value);
}

export function verifyFrozenContextEnvelope(contextEnvelope) {
  const reasons = [];
  const envelope = contextEnvelope?.value;
  if (!contextEnvelope || typeof contextEnvelope !== "object" || contextEnvelope.ok !== true || contextEnvelope.schema_version !== CONTEXT_ENVELOPE_SCHEMA) {
    return failure(["context.envelope-result-invalid"]);
  }
  if (!envelope || typeof envelope !== "object" || envelope.schema_version !== CONTEXT_ENVELOPE_SCHEMA) reasons.push("context.envelope-schema-invalid");
  if (typeof contextEnvelope.digest !== "string" || digestValue(envelope) !== contextEnvelope.digest) reasons.push("context.envelope-digest-mismatch");
  if (envelope?.authority_effect !== "none") reasons.push("context.envelope-authority-effect-forbidden");
  if (!new Set(["current-reused", "successor-current"]).has(envelope?.freshness_state)) reasons.push("context.envelope-not-current");
  if (typeof envelope?.claim_ceiling !== "string" || envelope.claim_ceiling.length === 0) reasons.push("context.envelope-claim-ceiling-required");

  if (envelope && typeof envelope === "object") {
    const {context_epoch_id: _epoch, ...epochMaterial} = envelope;
    if (envelope.context_epoch_id !== `context-epoch:${digestValue(epochMaterial)}`) reasons.push("context.envelope-epoch-mismatch");
    const items = Array.isArray(envelope.included_items) ? envelope.included_items : [];
    const itemIds = items.map((item) => item?.context_item_id);
    const itemDigests = items.map((item) => item?.item_digest);
    if (!unique(itemIds) || itemIds.some((id) => typeof id !== "string" || id.length === 0)) reasons.push("context.item-identity-invalid");
    if (!unique(itemDigests) || itemDigests.some((digest) => typeof digest !== "string" || digest.length === 0)) reasons.push("context.item-digest-set-invalid");
    for (const item of items) {
      const reason = verifyItem(item);
      if (reason) reasons.push(reason);
      else if (itemDigest(item) !== item.item_digest) reasons.push("context.item-digest-mismatch");
    }
    if (digestValue(itemDigests) !== digestValue(envelope.included_item_digests ?? [])) reasons.push("context.included-item-digests-mismatch");
    const dependencies = Array.isArray(envelope.selected_dependencies) ? envelope.selected_dependencies : [];
    const dependencyIds = dependencies.map((dependency) => dependency?.dependency_id);
    if (!unique(dependencyIds) || dependencies.some((dependency) => typeof dependency?.dependency_id !== "string" || typeof dependency?.digest !== "string")) {
      reasons.push("context.selected-dependencies-invalid");
    }
  }
  return reasons.length > 0
    ? failure(reasons)
    : deepFreeze({schema_version: CONTEXT_BOUND_EVALUATION_SCHEMA, ok: true, value: envelope, digest: contextEnvelope.digest, authority_effect: "none"});
}

export function bindSemanticRequestToContextEnvelope({context_envelope: contextEnvelope, semantic_request: semanticRequest} = {}) {
  const verified = verifyFrozenContextEnvelope(contextEnvelope);
  if (!verified.ok) return verified;
  if (!semanticRequest || typeof semanticRequest !== "object") return failure(["semantic.request-required"]);
  if (!verifyRecordDigest(semanticRequest.frame)) return failure(["semantic.frame-invalid"]);
  if (!verifyRecordDigest(semanticRequest.entry_gate)) return failure(["semantic.entry-gate-invalid"]);
  if (!verifyRecordDigest(semanticRequest.authority_snapshot)) return failure(["semantic.authority-snapshot-invalid"]);

  const envelope = verified.value;
  const frame = sealRecord({
    ...omitDigestFields(semanticRequest.frame),
    context_epoch_id: envelope.context_epoch_id,
    context_envelope_digest: verified.digest,
    context_item_digests: [...envelope.included_item_digests],
    context_freshness_state: envelope.freshness_state,
    context_claim_ceiling: envelope.claim_ceiling,
  });
  const binding = sealRecord({
    record_type: CONTEXT_BINDING_RECORD,
    schema_version: SCHEMA_VERSION,
    run_id: semanticRequest.run_id,
    created_at: semanticRequest.created_at,
    producer: `${EVALUATOR_ID}:context-envelope-adapter@1`,
    context_epoch_id: envelope.context_epoch_id,
    context_envelope_digest: verified.digest,
    context_item_digests: [...envelope.included_item_digests],
    selected_dependencies_digest: digestValue(envelope.selected_dependencies),
    source_snapshot_digest: digestValue(envelope.source_snapshot),
    exclusions_digest: digestValue(envelope.exclusions),
    contradictions_digest: digestValue(envelope.contradictions),
    gaps_digest: digestValue(envelope.gaps),
    residue_digest: digestValue(envelope.residue),
    freshness_state: envelope.freshness_state,
    claim_ceiling: envelope.claim_ceiling,
    original_frame_digest: semanticRequest.frame.digest,
    bound_frame_digest: frame.digest,
    authority_effect: "none",
  });
  const entryGate = sealRecord({
    ...omitDigestFields(semanticRequest.entry_gate),
    authority_snapshot_digest: semanticRequest.authority_snapshot.digest,
    subject_digest: frame.digest,
    context_envelope_binding_digest: binding.digest,
  });
  const request = deepFreeze({...semanticRequest, frame, entry_gate: entryGate, context_envelope_binding: binding});
  return deepFreeze({
    schema_version: CONTEXT_BOUND_EVALUATION_SCHEMA,
    ok: true,
    value: request,
    binding,
    context_envelope_digest: verified.digest,
    context_epoch_id: envelope.context_epoch_id,
    authority_effect: "none",
  });
}

export function evaluateContextBoundSemanticJudgment(input, telemetry = {}) {
  const bound = bindSemanticRequestToContextEnvelope(input);
  if (!bound.ok) return bound;
  const semantic = evaluateSemanticJudgment(bound.value, telemetry);
  const assembled = assembleReasoningReceipt(bound.value, semantic);
  return {
    schema_version: CONTEXT_BOUND_EVALUATION_SCHEMA,
    ok: true,
    request: bound.value,
    context_envelope_binding: bound.binding,
    semantic,
    reasoning_receipt: assembled.receipt,
    reasoning_receipt_bytes: assembled.bytes,
    reasoning_receipt_exact_bytes_digest: assembled.exact_bytes_digest,
    evaluator_calls: telemetry.evaluator_calls ?? 0,
    authority_effect: "none",
  };
}
