import {
  closeSync,
  existsSync,
  fsyncSync,
  mkdirSync,
  openSync,
  readFileSync,
  unlinkSync,
  writeSync,
} from "node:fs";
import {randomUUID} from "node:crypto";
import {dirname, resolve} from "node:path";

import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "../intent-route-resolver/index.mjs";

export const REASONING_STATE_EVENT_SCHEMA = "are.reasoning-state-event/v1";
export const REASONING_STATE_EPOCH_SCHEMA = "are.reasoning-state-epoch/v1";
export const REASONING_STATE_CHECKPOINT_SCHEMA = "are.reasoning-state-checkpoint/v1";
export const REASONING_REQUEST_HEADER_SCHEMA = "are.reasoning-request-series-header/v1";
export const REASONING_DISPATCH_SCHEMA = "are.reasoning-dispatch/v1";
export const REASONING_DISPATCH_VERIFICATION_SCHEMA = "are.reasoning-dispatch-verification/v1";
export const REASONING_STATE_INDEX_SCHEMA = "are.reasoning-state-derived-index/v1";
export const REASONING_STATE_LOG_VERIFICATION_SCHEMA = "are.reasoning-state-log-verification/v1";
export const REASONING_STATE_RECOVERY_SCHEMA = "are.reasoning-state-recovery-assessment/v1";
export const REASONING_STATE_FRONTIER_SCHEMA = "are.reasoning-state-frontier/v1";
export const REASONING_CACHE_AFFINITY_PROJECTION_SCHEMA = "are.reasoning-cache-affinity-projection/v1";
export const REASONING_CACHE_AFFINITY_ASSESSMENT_SCHEMA = "are.reasoning-cache-affinity-assessment/v1";
export const CONTEXT_BOUND_REUSE_RECEIPT_SCHEMA = "are.context-bound-reuse-receipt/v1";
export const REASONING_CACHE_TELEMETRY_OBSERVATION_SCHEMA = "are.reasoning-cache-telemetry-observation/v1";
export const REASONING_STATE_BRANCH_SCHEMA = "are.reasoning-state-branch/v1";
export const REASONING_REPLAY_FIXTURE_SCHEMA = "are.reasoning-replay-fixture/v1";
export const REASONING_STATE_REDUCTION_SCHEMA = "are.reasoning-state-reduction/v1";
export const REASONING_CHECKPOINT_POLICY_SCHEMA = "are.reasoning-checkpoint-policy/v1";
export const REASONING_COUNTEREVIDENCE_SCHEMA = "are.reasoning-counterevidence/v1";
export const PORTABLE_REASONING_EPOCH_SCHEMA = "are.portable-reasoning-epoch/v1";
export const REASONING_PROVENANCE_COMPARISON_SCHEMA = "are.reasoning-provenance-comparison/v1";
export const REASONING_STATE_TRANSITION_ASSESSMENT_SCHEMA = "are.reasoning-state-transition-assessment/v1";
export const REASONING_STATE_TRANSITION_PLAN_SCHEMA = "are.reasoning-state-transition-plan/v1";
export const REASONING_STATE_TRANSITION_RECEIPT_SCHEMA = "are.reasoning-state-transition-receipt/v1";

const ledgers = new WeakSet();
const sinks = new WeakSet();
const writerLocks = new WeakSet();
const CHECKPOINT_KINDS = new Set(["before-model-request", "before-effect", "before-continuation", "after-turn-completion", "manual"]);

function freeze(value) {
  return deepFreeze(canonicalizeJson(value));
}

function digest(value) {
  return sha256HexText(canonicalJson(canonicalizeJson(value)));
}

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function text(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function fail(stage, reasonCodes, residue = []) {
  return freeze({
    schema_version: "are.reasoning-state-failure/v1",
    ok: false,
    stage,
    reason_codes: [...new Set(reasonCodes)].sort(),
    residue,
    authority_effect: "none",
  });
}

function canonicalOrder(values) {
  return [...values].map((value) => canonicalizeJson(value)).sort((left, right) => canonicalJson(left).localeCompare(canonicalJson(right)));
}

function sinkResult(operation, disposition, details = {}) {
  return freeze({ok: true, operation, disposition, ...details, authority_effect: "none"});
}

export function createMemoryReasoningStateSink() {
  const state = {records: [], flushCount: 0, closed: false};
  const sink = Object.freeze({
    durability: "process-memory",
    append(value) {
      if (state.closed) return fail("sink-append", ["reasoning.sink-closed"]);
      state.records.push(freeze(value));
      return sinkResult("append", "appended", {record_count: state.records.length});
    },
    flush() {
      if (state.closed) return fail("sink-flush", ["reasoning.sink-closed"]);
      state.flushCount += 1;
      return sinkResult("flush", "flushed", {flush_count: state.flushCount, durability: "process-memory"});
    },
    snapshot: () => freeze([...state.records]),
    inspect: () => freeze({durability: "process-memory", record_count: state.records.length, flush_count: state.flushCount, closed: state.closed, authority_effect: "none"}),
    close() {
      state.closed = true;
      return sinkResult("close", "closed");
    },
  });
  sinks.add(sink);
  return sink;
}

export function acquireReasoningStateWriterLock({path, owner_id = "are-reasoning-state-writer"} = {}) {
  if (!text(path)) return fail("writer-lock", ["reasoning.writer-lock-path-required"]);
  if (!text(owner_id)) return fail("writer-lock", ["reasoning.writer-lock-owner-required"]);
  const absolutePath = resolve(path);
  const lockPath = `${absolutePath}.writer.lock`;
  mkdirSync(dirname(lockPath), {recursive: true});
  let descriptor;
  try {
    descriptor = openSync(lockPath, "wx", 0o600);
  } catch (error) {
    if (error?.code === "EEXIST") return fail("writer-lock", ["reasoning.writer-lock-held"], [{lock_path: lockPath}]);
    return fail("writer-lock", ["reasoning.writer-lock-create-failed"], [{lock_path: lockPath, code: error?.code ?? null}]);
  }
  const material = canonicalizeJson({
    schema_version: "are.reasoning-state-writer-lock/v1",
    owner_id: owner_id.trim(),
    ledger_path: absolutePath,
    process_id: process.pid,
    nonce: randomUUID(),
    authority_effect: "none",
  });
  const lockRecord = freeze({...material, lock_digest: digest(material)});
  try {
    writeSync(descriptor, `${canonicalJson(lockRecord)}\n`, null, "utf8");
    fsyncSync(descriptor);
  } catch (error) {
    closeSync(descriptor);
    unlinkSync(lockPath);
    return fail("writer-lock", ["reasoning.writer-lock-write-failed"], [{lock_path: lockPath, code: error?.code ?? null}]);
  }
  let released = false;
  const lock = Object.freeze({
    path: lockPath,
    record: lockRecord,
    release() {
      if (released) return sinkResult("writer-lock-release", "already-released", {lock_path: lockPath});
      let current;
      try { current = JSON.parse(readFileSync(lockPath, "utf8").trim()); } catch {
        return fail("writer-lock-release", ["reasoning.writer-lock-record-unreadable"], [{lock_path: lockPath}]);
      }
      if (current.lock_digest !== lockRecord.lock_digest) return fail("writer-lock-release", ["reasoning.writer-lock-owner-mismatch"], [{lock_path: lockPath}]);
      closeSync(descriptor);
      unlinkSync(lockPath);
      released = true;
      return sinkResult("writer-lock-release", "released", {lock_path: lockPath});
    },
    inspect: () => freeze({lock_path: lockPath, owner_id: lockRecord.owner_id, process_id: lockRecord.process_id, lock_digest: lockRecord.lock_digest, released, authority_effect: "none"}),
  });
  writerLocks.add(lock);
  return Object.freeze({ok: true, lock, value: lockRecord, authority_effect: "none"});
}

export function createAppendOnlyFileReasoningStateSink({path, create_parent = true, initial_record_count = 0} = {}) {
  if (!text(path)) throw new TypeError("An explicit reasoning-state log path is required.");
  if (!Number.isSafeInteger(initial_record_count) || initial_record_count < 0) throw new TypeError("The initial reasoning-state record count must be a non-negative safe integer.");
  const absolutePath = resolve(path);
  if (create_parent) mkdirSync(dirname(absolutePath), {recursive: true, mode: 0o700});
  const descriptor = openSync(absolutePath, "a", 0o600);
  const state = {descriptor, path: absolutePath, records: initial_record_count, flushCount: 0, closed: false};
  const sink = Object.freeze({
    durability: "append-only-file-fsync",
    path: absolutePath,
    append(value) {
      if (state.closed) return fail("sink-append", ["reasoning.sink-closed"]);
      try {
        const bytes = `${canonicalJson(canonicalizeJson(value))}\n`;
        writeSync(state.descriptor, bytes, null, "utf8");
        state.records += 1;
        return sinkResult("append", "appended", {record_count: state.records, byte_count: Buffer.byteLength(bytes)});
      } catch (error) {
        return fail("sink-append", ["reasoning.sink-append-failed"], [{message: error.message}]);
      }
    },
    flush() {
      if (state.closed) return fail("sink-flush", ["reasoning.sink-closed"]);
      try {
        fsyncSync(state.descriptor);
        state.flushCount += 1;
        return sinkResult("flush", "flushed", {flush_count: state.flushCount, durability: "append-only-file-fsync"});
      } catch (error) {
        return fail("sink-flush", ["reasoning.sink-flush-failed"], [{message: error.message}]);
      }
    },
    inspect: () => freeze({durability: "append-only-file-fsync", path: state.path, record_count: state.records, flush_count: state.flushCount, closed: state.closed, authority_effect: "none"}),
    close() {
      if (!state.closed) closeSync(state.descriptor);
      state.closed = true;
      return sinkResult("close", "closed");
    },
  });
  sinks.add(sink);
  return sink;
}

function verifiedSink(sink) {
  return sinks.has(sink) && typeof sink.append === "function" && typeof sink.flush === "function";
}

function ledgerState(ledger) {
  if (!ledgers.has(ledger)) throw new TypeError("A verified reasoning-state ledger is required.");
  return ledger._state;
}

function eventMaterial(event) {
  const {event_digest: _eventDigest, ...material} = event;
  return material;
}

function checkpointMaterial(checkpoint) {
  const {checkpoint_digest: _checkpointDigest, ...material} = checkpoint;
  return material;
}

function frontierMaterial(frontier) {
  const {frontier_digest: _frontierDigest, frontier_id: _frontierId, ...material} = frontier;
  return material;
}

export function verifyReasoningStateFrontier(frontier) {
  const reasons = [];
  if (!record(frontier) || frontier.schema_version !== REASONING_STATE_FRONTIER_SCHEMA) reasons.push("reasoning.frontier-schema-invalid");
  if (!text(frontier?.ledger_id)) reasons.push("reasoning.frontier-ledger-id-required");
  if (!text(frontier?.frontier_key)) reasons.push("reasoning.frontier-key-required");
  if (!text(frontier?.subject_digest)) reasons.push("reasoning.frontier-subject-digest-required");
  if (!record(frontier?.state)) reasons.push("reasoning.frontier-state-required");
  if (frontier?.authority_effect !== "none") reasons.push("reasoning.frontier-authority-effect-invalid");
  if (record(frontier)) {
    const expectedDigest = digest(frontierMaterial(frontier));
    if (frontier.frontier_digest !== expectedDigest) reasons.push("reasoning.frontier-digest-invalid");
    if (frontier.frontier_id !== `reasoning-frontier:${expectedDigest}`) reasons.push("reasoning.frontier-id-invalid");
  }
  return reasons.length > 0
    ? fail("frontier-verification", reasons)
    : freeze({ok: true, value: frontier, digest: frontier.frontier_digest, authority_effect: "none"});
}

function verifyCheckpoint(checkpoint) {
  return record(checkpoint)
    && checkpoint.schema_version === REASONING_STATE_CHECKPOINT_SCHEMA
    && text(checkpoint.checkpoint_digest)
    && digest(checkpointMaterial(checkpoint)) === checkpoint.checkpoint_digest
    && text(checkpoint.ledger_id)
    && CHECKPOINT_KINDS.has(checkpoint.checkpoint_kind)
    && text(checkpoint.epoch_id)
    && text(checkpoint.epoch_digest)
    && checkpoint.epoch_id === `reasoning-state:${checkpoint.epoch_digest}`
    && (checkpoint.subject_digest === null || text(checkpoint.subject_digest))
    && (checkpoint.head_event_digest === null || text(checkpoint.head_event_digest))
    && ["process-memory", "append-only-file-fsync"].includes(checkpoint.durability)
    && checkpoint.authority_effect === "none";
}

function verifyEvent(event) {
  return record(event)
    && event.schema_version === REASONING_STATE_EVENT_SCHEMA
    && text(event.event_digest)
    && digest(eventMaterial(event)) === event.event_digest
    && text(event.event_kind)
    && text(event.idempotency_key)
    && Number.isSafeInteger(event.sequence)
    && event.sequence > 0
    && digest(event.content) === event.content_digest
    && event.authority_effect === "none";
}

export function appendReasoningStateEvent(ledger, input) {
  const state = ledgerState(ledger);
  const reasons = [];
  if (!record(input)) reasons.push("reasoning.event-input-required");
  if (!text(input?.event_kind)) reasons.push("reasoning.event-kind-required");
  if (!record(input?.content)) reasons.push("reasoning.event-content-required");
  if (reasons.length > 0) return fail("event-append", reasons);
  const content = canonicalizeJson(input.content);
  const contentDigest = digest(content);
  const idempotencyKey = text(input.idempotency_key)
    ? input.idempotency_key.trim()
    : `${input.event_kind.trim()}:${contentDigest}`;
  const existing = state.eventsByKey.get(idempotencyKey);
  if (existing) {
    if (existing.content_digest !== contentDigest || existing.event_kind !== input.event_kind.trim()) {
      return fail("event-append", ["reasoning.event-idempotency-conflict"], [{idempotency_key: idempotencyKey, existing_event_digest: existing.event_digest}]);
    }
    return freeze({ok: true, disposition: "duplicate", event: existing, authority_effect: "none"});
  }
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_EVENT_SCHEMA,
    ledger_id: state.ledgerId,
    sequence: state.events.length + 1,
    event_kind: input.event_kind.trim(),
    idempotency_key: idempotencyKey,
    predecessor_digest: state.events.at(-1)?.event_digest ?? null,
    content,
    content_digest: contentDigest,
    provenance_refs: [...new Set(Array.isArray(input.provenance_refs) ? input.provenance_refs.filter(text).map((value) => value.trim()) : [])].sort(),
    authority_effect: "none",
  });
  const event = freeze({...material, event_digest: digest(material)});
  const persisted = state.sink.append({record_kind: "reasoning-state-event", value: event});
  if (!persisted?.ok) return fail("event-append", persisted?.reason_codes ?? ["reasoning.sink-append-failed"], persisted?.residue ?? []);
  state.events.push(event);
  state.eventsByKey.set(idempotencyKey, event);
  state.eventsByDigest.set(event.event_digest, event);
  return freeze({ok: true, disposition: "appended", event, authority_effect: "none"});
}

function epochMaterial(epoch) {
  const {epoch_digest: _epochDigest, epoch_id: _epochId, ...material} = epoch;
  return material;
}

export function verifyReasoningStateEpoch(epoch, events = null) {
  const reasons = [];
  if (!record(epoch) || epoch.schema_version !== REASONING_STATE_EPOCH_SCHEMA) reasons.push("reasoning.epoch-schema-invalid");
  if (!text(epoch?.epoch_digest) || (record(epoch) && digest(epochMaterial(epoch)) !== epoch.epoch_digest)) reasons.push("reasoning.epoch-digest-invalid");
  if (!text(epoch?.epoch_id) || epoch?.epoch_id !== `reasoning-state:${epoch?.epoch_digest}`) reasons.push("reasoning.epoch-id-invalid");
  if (!Array.isArray(epoch?.event_digests) || epoch.event_digests.length === 0 || new Set(epoch.event_digests).size !== epoch.event_digests.length) reasons.push("reasoning.epoch-events-invalid");
  if (Array.isArray(epoch?.event_digests) && digest(epoch.event_digests) !== epoch.event_set_digest) reasons.push("reasoning.epoch-event-set-digest-invalid");
  if (events !== null) {
    if (!Array.isArray(events) || events.some((event) => !verifyEvent(event)) || events.map((event) => event.event_digest).some((value, index) => value !== epoch?.event_digests?.[index])) {
      reasons.push("reasoning.epoch-event-binding-invalid");
    }
  }
  if (epoch?.authority_effect !== "none") reasons.push("reasoning.epoch-authority-effect-invalid");
  return reasons.length > 0
    ? fail("epoch-verification", reasons)
    : freeze({ok: true, value: epoch, digest: epoch.epoch_digest, authority_effect: "none"});
}

export function sealReasoningStateEpoch(ledger, input = {}) {
  const state = ledgerState(ledger);
  if (!record(input)) return fail("epoch-seal", ["reasoning.epoch-input-invalid"]);
  const eventDigests = Array.isArray(input.event_digests) ? [...input.event_digests] : state.events.map((event) => event.event_digest);
  if (eventDigests.length === 0 || new Set(eventDigests).size !== eventDigests.length) return fail("epoch-seal", ["reasoning.epoch-events-invalid"]);
  const events = eventDigests.map((eventDigest) => state.eventsByDigest.get(eventDigest));
  if (events.some((event) => !event)) return fail("epoch-seal", ["reasoning.epoch-event-missing"]);
  const materialWithoutIdentity = canonicalizeJson({
    schema_version: REASONING_STATE_EPOCH_SCHEMA,
    ledger_id: state.ledgerId,
    consumer_ref: text(input.consumer_ref) ? input.consumer_ref.trim() : null,
    request_ref: text(input.request_ref) ? input.request_ref.trim() : null,
    event_digests: eventDigests,
    event_set_digest: digest(eventDigests),
    selected_dependencies: Array.isArray(input.selected_dependencies) ? canonicalOrder(input.selected_dependencies) : [],
    context_envelope_digest: text(input.context_envelope_digest) ? input.context_envelope_digest.trim() : null,
    frontier: record(input.frontier) ? input.frontier : {},
    authority_effect: "none",
  });
  const stableDigest = digest(materialWithoutIdentity);
  const stableEpoch = freeze({...materialWithoutIdentity, epoch_id: `reasoning-state:${stableDigest}`, epoch_digest: stableDigest});
  const existing = state.epochs.get(stableEpoch.epoch_digest);
  if (existing) return freeze({ok: true, disposition: "duplicate", value: existing, digest: existing.epoch_digest, authority_effect: "none"});
  const persisted = state.sink.append({record_kind: "reasoning-state-epoch", value: stableEpoch});
  if (!persisted?.ok) return fail("epoch-seal", persisted?.reason_codes ?? ["reasoning.sink-append-failed"], persisted?.residue ?? []);
  state.epochs.set(stableEpoch.epoch_digest, stableEpoch);
  return freeze({ok: true, disposition: "sealed", value: stableEpoch, digest: stableEpoch.epoch_digest, authority_effect: "none"});
}

export function replayReasoningStateEpoch(ledger, epoch) {
  const state = ledgerState(ledger);
  const events = Array.isArray(epoch?.event_digests) ? epoch.event_digests.map((eventDigest) => state.eventsByDigest.get(eventDigest)) : [];
  const verified = verifyReasoningStateEpoch(epoch, events);
  if (!verified.ok) return verified;
  const material = canonicalizeJson({
    schema_version: "are.reasoning-state-replay/v1",
    ledger_id: state.ledgerId,
    epoch_id: epoch.epoch_id,
    epoch_digest: epoch.epoch_digest,
    events,
    external_calls: 0,
    authority_effect: "none",
  });
  return freeze({ok: true, value: {...material, replay_digest: digest(material)}, authority_effect: "none"});
}

export function createReasoningStateBranch(ledger, input = {}) {
  const state = ledgerState(ledger);
  const baseEpoch = input.base_epoch;
  const verified = verifyReasoningStateEpoch(baseEpoch, Array.isArray(baseEpoch?.event_digests) ? baseEpoch.event_digests.map((value) => state.eventsByDigest.get(value)) : []);
  if (!verified.ok) return fail("branch-create", verified.reason_codes);
  if (!text(input.branch_ref)) return fail("branch-create", ["reasoning.branch-ref-required"]);
  const additional = Array.isArray(input.additional_event_digests) ? [...new Set(input.additional_event_digests)] : [];
  if (additional.some((value) => !state.eventsByDigest.has(value))) return fail("branch-create", ["reasoning.branch-event-missing"]);
  const branchMaterial = canonicalizeJson({
    schema_version: REASONING_STATE_BRANCH_SCHEMA,
    base_epoch_id: baseEpoch.epoch_id,
    base_epoch_digest: baseEpoch.epoch_digest,
    branch_ref: input.branch_ref.trim(),
    additional_event_digests: additional,
    branch_basis: record(input.branch_basis) ? input.branch_basis : {},
    authority_effect: "none",
  });
  const branch = freeze({...branchMaterial, branch_digest: digest(branchMaterial), branch_id: `reasoning-branch:${digest(branchMaterial)}`});
  const appended = appendReasoningStateEvent(ledger, {
    event_kind: "reasoning-branch-created",
    idempotency_key: branch.branch_id,
    content: branch,
    provenance_refs: [`reasoning-epoch:${baseEpoch.epoch_digest}`],
  });
  if (!appended.ok) return appended;
  const sealed = sealReasoningStateEpoch(ledger, {
    event_digests: [...baseEpoch.event_digests, ...additional.filter((value) => !baseEpoch.event_digests.includes(value)), appended.event.event_digest],
    consumer_ref: input.consumer_ref ?? baseEpoch.consumer_ref,
    request_ref: input.request_ref ?? baseEpoch.request_ref,
    selected_dependencies: input.selected_dependencies ?? baseEpoch.selected_dependencies,
    context_envelope_digest: input.context_envelope_digest ?? baseEpoch.context_envelope_digest,
    frontier: {kind: "reasoning-branch", branch_id: branch.branch_id, branch_digest: branch.branch_digest},
  });
  return sealed.ok ? freeze({ok: true, disposition: appended.disposition, branch, event: appended.event, epoch: sealed.value, authority_effect: "none"}) : sealed;
}

function replayFixtureMaterial(fixture) {
  const {fixture_digest: _fixtureDigest, ...material} = fixture;
  return material;
}

export function deriveReasoningReplayFixture(ledger, epoch, options = {}) {
  const replayed = replayReasoningStateEpoch(ledger, epoch);
  if (!replayed.ok) return replayed;
  const material = canonicalizeJson({
    schema_version: REASONING_REPLAY_FIXTURE_SCHEMA,
    fixture_ref: text(options.fixture_ref) ? options.fixture_ref.trim() : `fixture:${epoch.epoch_digest}`,
    source_epoch: epoch,
    events: replayed.value.events,
    expected_replay_digest: replayed.value.replay_digest,
    external_calls: 0,
    generated_from_verified_state: true,
    authority_effect: "none",
  });
  const fixture = freeze({...material, fixture_digest: digest(material)});
  return freeze({ok: true, value: fixture, digest: fixture.fixture_digest, authority_effect: "none"});
}

export function verifyReasoningReplayFixture(fixture) {
  const reasons = [];
  if (!record(fixture) || fixture.schema_version !== REASONING_REPLAY_FIXTURE_SCHEMA) reasons.push("reasoning.fixture-schema-invalid");
  if (record(fixture) && digest(replayFixtureMaterial(fixture)) !== fixture.fixture_digest) reasons.push("reasoning.fixture-digest-invalid");
  if (!verifyReasoningStateEpoch(fixture?.source_epoch, fixture?.events).ok) reasons.push("reasoning.fixture-epoch-binding-invalid");
  if (record(fixture?.source_epoch) && Array.isArray(fixture?.events)) {
    const replayMaterial = canonicalizeJson({schema_version: "are.reasoning-state-replay/v1", ledger_id: fixture.source_epoch.ledger_id, epoch_id: fixture.source_epoch.epoch_id, epoch_digest: fixture.source_epoch.epoch_digest, events: fixture.events, external_calls: 0, authority_effect: "none"});
    if (digest(replayMaterial) !== fixture.expected_replay_digest) reasons.push("reasoning.fixture-replay-digest-invalid");
  }
  return reasons.length ? fail("fixture-verification", reasons) : freeze({ok: true, value: fixture, digest: fixture.fixture_digest, external_calls: 0, authority_effect: "none"});
}

export function appendReasoningStateReduction(ledger, input = {}) {
  const state = ledgerState(ledger);
  const sourceEpoch = input.source_epoch;
  const verified = verifyReasoningStateEpoch(sourceEpoch, Array.isArray(sourceEpoch?.event_digests) ? sourceEpoch.event_digests.map((value) => state.eventsByDigest.get(value)) : []);
  if (!verified.ok) return fail("reduction-append", verified.reason_codes);
  const retained = Array.isArray(input.retained_event_digests) ? [...new Set(input.retained_event_digests)] : [];
  if (retained.length === 0 || retained.some((value) => !sourceEpoch.event_digests.includes(value))) return fail("reduction-append", ["reasoning.reduction-retained-events-invalid"]);
  const omitted = sourceEpoch.event_digests.filter((value) => !retained.includes(value));
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_REDUCTION_SCHEMA,
    source_epoch_id: sourceEpoch.epoch_id,
    source_epoch_digest: sourceEpoch.epoch_digest,
    retained_event_digests: retained,
    omitted_event_digests: omitted,
    reduction_basis: record(input.reduction_basis) ? input.reduction_basis : {},
    destructive: false,
    generative_summary: false,
    authority_effect: "none",
  });
  const reduction = freeze({...material, reduction_digest: digest(material)});
  const appended = appendReasoningStateEvent(ledger, {event_kind: "reasoning-state-reduced", idempotency_key: `reasoning-reduction:${reduction.reduction_digest}`, content: reduction, provenance_refs: [`reasoning-epoch:${sourceEpoch.epoch_digest}`]});
  if (!appended.ok) return appended;
  const sealed = sealReasoningStateEpoch(ledger, {event_digests: [...retained, appended.event.event_digest], consumer_ref: input.consumer_ref ?? sourceEpoch.consumer_ref, request_ref: input.request_ref ?? sourceEpoch.request_ref, selected_dependencies: sourceEpoch.selected_dependencies, context_envelope_digest: sourceEpoch.context_envelope_digest, frontier: {kind: "reasoning-reduction", source_epoch_digest: sourceEpoch.epoch_digest, reduction_digest: reduction.reduction_digest}});
  return sealed.ok ? freeze({ok: true, disposition: appended.disposition, reduction, event: appended.event, epoch: sealed.value, authority_effect: "none"}) : sealed;
}

export function selectReasoningCheckpointPolicy(input = {}) {
  const boundary = input.boundary ?? "observation";
  const defaults = {
    observation: {risk: "low", checkpoint_required: false, minimum_durability: "process-memory", checkpoint_kind: "manual"},
    "model-request": {risk: "moderate", checkpoint_required: true, minimum_durability: "process-memory", checkpoint_kind: "before-model-request"},
    continuation: {risk: "high", checkpoint_required: true, minimum_durability: "append-only-file-fsync", checkpoint_kind: "before-continuation"},
    effect: {risk: "critical", checkpoint_required: true, minimum_durability: "append-only-file-fsync", checkpoint_kind: "before-effect"},
  };
  if (!Object.hasOwn(defaults, boundary)) return fail("checkpoint-policy", ["reasoning.checkpoint-boundary-invalid"]);
  const selected = canonicalizeJson({...defaults[boundary], schema_version: REASONING_CHECKPOINT_POLICY_SCHEMA, boundary, policy_ref: text(input.policy_ref) ? input.policy_ref.trim() : "are-default-risk-scaled-checkpoints/v1", authority_effect: "none"});
  return freeze({ok: true, value: {...selected, policy_digest: digest(selected)}, authority_effect: "none"});
}

export function checkpointReasoningStateByRisk(ledger, input = {}) {
  const policy = selectReasoningCheckpointPolicy(input);
  if (!policy.ok) return policy;
  if (!policy.value.checkpoint_required) return freeze({ok: true, disposition: "not-required", policy: policy.value, checkpoint: null, authority_effect: "none"});
  const durability = ledgerState(ledger).sink.durability;
  if (policy.value.minimum_durability === "append-only-file-fsync" && durability !== "append-only-file-fsync") return fail("checkpoint-by-risk", ["reasoning.checkpoint-durability-insufficient"], [{required: policy.value.minimum_durability, actual: durability, boundary: policy.value.boundary}]);
  const checkpointed = checkpointReasoningState(ledger, {checkpoint_kind: policy.value.checkpoint_kind, epoch: input.epoch, subject_digest: input.subject_digest});
  return checkpointed.ok ? freeze({ok: true, disposition: "checkpointed", policy: policy.value, checkpoint: checkpointed.value, flush: checkpointed.flush, authority_effect: "none"}) : checkpointed;
}

export function appendReasoningCounterevidence(ledger, input = {}) {
  const reasons = [];
  if (!text(input.claim_ref)) reasons.push("reasoning.counterevidence-claim-required");
  if (!text(input.evidence_ref)) reasons.push("reasoning.counterevidence-ref-required");
  if (!text(input.source_identity) || !text(input.source_digest)) reasons.push("reasoning.counterevidence-source-binding-required");
  if (reasons.length) return fail("counterevidence-append", reasons);
  const material = canonicalizeJson({schema_version: REASONING_COUNTEREVIDENCE_SCHEMA, claim_ref: input.claim_ref.trim(), evidence_ref: input.evidence_ref.trim(), source_identity: input.source_identity.trim(), source_digest: input.source_digest.trim(), posture: text(input.posture) ? input.posture.trim() : "counterevidence", temporal_scope: record(input.temporal_scope) ? input.temporal_scope : {}, content: record(input.content) ? input.content : {}, authority_effect: "none"});
  const counterevidence = freeze({...material, counterevidence_digest: digest(material)});
  const appended = appendReasoningStateEvent(ledger, {event_kind: "counterevidence-recorded", idempotency_key: `counterevidence:${counterevidence.counterevidence_digest}`, content: counterevidence, provenance_refs: [counterevidence.source_identity]});
  return appended.ok ? freeze({ok: true, disposition: appended.disposition, counterevidence, event: appended.event, authority_effect: "none"}) : appended;
}

export function selectReusableCounterevidence(ledger, input = {}) {
  const state = ledgerState(ledger);
  if (!text(input.claim_ref)) return fail("counterevidence-select", ["reasoning.counterevidence-claim-required"]);
  const current = new Map((Array.isArray(input.current_sources) ? input.current_sources : []).filter((item) => text(item?.source_identity) && text(item?.source_digest)).map((item) => [item.source_identity, item.source_digest]));
  const selected = [];
  const invalidated = [];
  for (const event of state.events.filter((value) => value.event_kind === "counterevidence-recorded" && value.content.claim_ref === input.claim_ref.trim())) {
    const entry = {event_digest: event.event_digest, counterevidence: event.content};
    if (current.get(event.content.source_identity) === event.content.source_digest) selected.push(entry);
    else invalidated.push({...entry, reason: current.has(event.content.source_identity) ? "counterevidence.source-changed" : "counterevidence.source-missing"});
  }
  const material = canonicalizeJson({schema_version: "are.reusable-counterevidence-selection/v1", claim_ref: input.claim_ref.trim(), selected, invalidated, authority_effect: "none"});
  return freeze({ok: true, value: {...material, selection_digest: digest(material)}, authority_effect: "none"});
}

function portableEpochMaterial(bundle) {
  const {bundle_digest: _bundleDigest, ...material} = bundle;
  return material;
}

export function exportPortableReasoningEpoch(ledger, epoch, input = {}) {
  if (!record(input.compatibility_profile)) return fail("portable-epoch-export", ["reasoning.portable-compatibility-profile-required"]);
  const replayed = replayReasoningStateEpoch(ledger, epoch);
  if (!replayed.ok) return replayed;
  const material = canonicalizeJson({schema_version: PORTABLE_REASONING_EPOCH_SCHEMA, source_ledger_id: epoch.ledger_id, source_epoch: epoch, events: replayed.value.events, compatibility_profile: input.compatibility_profile, compatibility_digest: digest(input.compatibility_profile), authority_effect: "none"});
  const bundle = freeze({...material, bundle_digest: digest(material)});
  return freeze({ok: true, value: bundle, digest: bundle.bundle_digest, authority_effect: "none"});
}

export function verifyPortableReasoningEpoch(bundle, compatibilityProfile = null) {
  const reasons = [];
  if (!record(bundle) || bundle.schema_version !== PORTABLE_REASONING_EPOCH_SCHEMA) reasons.push("reasoning.portable-schema-invalid");
  if (record(bundle) && digest(portableEpochMaterial(bundle)) !== bundle.bundle_digest) reasons.push("reasoning.portable-digest-invalid");
  if (!verifyReasoningStateEpoch(bundle?.source_epoch, bundle?.events).ok) reasons.push("reasoning.portable-epoch-binding-invalid");
  if (record(bundle?.compatibility_profile) && digest(bundle.compatibility_profile) !== bundle.compatibility_digest) reasons.push("reasoning.portable-compatibility-digest-invalid");
  if (compatibilityProfile !== null && digest(compatibilityProfile) !== bundle?.compatibility_digest) reasons.push("reasoning.portable-compatibility-mismatch");
  return reasons.length ? fail("portable-epoch-verification", reasons) : freeze({ok: true, value: bundle, digest: bundle.bundle_digest, authority_effect: "none"});
}

export function importPortableReasoningEpoch(ledger, bundle, input = {}) {
  const verified = verifyPortableReasoningEpoch(bundle, input.compatibility_profile);
  if (!verified.ok) return verified;
  const appended = appendReasoningStateEvent(ledger, {event_kind: "portable-reasoning-epoch-imported", idempotency_key: `portable-epoch:${bundle.bundle_digest}`, content: {source_ledger_id: bundle.source_ledger_id, source_epoch_id: bundle.source_epoch.epoch_id, source_epoch_digest: bundle.source_epoch.epoch_digest, bundle_digest: bundle.bundle_digest, compatibility_digest: bundle.compatibility_digest, authority_effect: "none"}, provenance_refs: [`reasoning-epoch:${bundle.source_epoch.epoch_digest}`]});
  if (!appended.ok) return appended;
  const sealed = sealReasoningStateEpoch(ledger, {event_digests: [appended.event.event_digest], consumer_ref: input.consumer_ref ?? null, request_ref: input.request_ref ?? bundle.source_epoch.request_ref, selected_dependencies: bundle.source_epoch.selected_dependencies, context_envelope_digest: bundle.source_epoch.context_envelope_digest, frontier: {kind: "portable-import", source_epoch_digest: bundle.source_epoch.epoch_digest, bundle_digest: bundle.bundle_digest}});
  return sealed.ok ? freeze({ok: true, disposition: appended.disposition, source_bundle_digest: bundle.bundle_digest, event: appended.event, epoch: sealed.value, authority_effect: "none"}) : sealed;
}

export function compareReasoningProvenance(leftEpoch, rightEpoch) {
  const reasons = [];
  if (!verifyReasoningStateEpoch(leftEpoch).ok || !verifyReasoningStateEpoch(rightEpoch).ok) return fail("provenance-comparison", ["reasoning.provenance-epoch-invalid"]);
  if (leftEpoch.context_envelope_digest !== rightEpoch.context_envelope_digest) reasons.push("provenance.context-envelope-changed");
  if (digest(canonicalOrder(leftEpoch.selected_dependencies ?? [])) !== digest(canonicalOrder(rightEpoch.selected_dependencies ?? []))) reasons.push("provenance.selected-dependencies-changed");
  if (digest(leftEpoch.frontier ?? {}) !== digest(rightEpoch.frontier ?? {})) reasons.push("provenance.frontier-changed");
  if (digest(leftEpoch.event_digests) !== digest(rightEpoch.event_digests)) reasons.push("provenance.event-selection-changed");
  if (leftEpoch.consumer_ref !== rightEpoch.consumer_ref) reasons.push("provenance.consumer-changed");
  if (leftEpoch.request_ref !== rightEpoch.request_ref) reasons.push("provenance.request-changed");
  const material = canonicalizeJson({schema_version: REASONING_PROVENANCE_COMPARISON_SCHEMA, left_epoch_digest: leftEpoch.epoch_digest, right_epoch_digest: rightEpoch.epoch_digest, same_provenance: reasons.length === 0, reuse_eligible: reasons.length === 0, difference_reasons: reasons.sort(), authority_effect: "none"});
  return freeze({ok: true, value: {...material, comparison_digest: digest(material)}, authority_effect: "none"});
}

const TRANSITION_ACTIONS = new Set(["auto", "reuse", "branch", "reduce", "checkpoint", "portable-export"]);

export function assessReasoningStateTransition(input = {}) {
  const currentEpoch = input.current_epoch;
  const verified = verifyReasoningStateEpoch(currentEpoch);
  if (!verified.ok) return fail("transition-assessment", ["reasoning.transition-current-epoch-invalid", ...verified.reason_codes]);
  const requestedAction = input.requested_action ?? "auto";
  if (!TRANSITION_ACTIONS.has(requestedAction)) return fail("transition-assessment", ["reasoning.transition-action-invalid"]);
  const maximumEvents = input.maximum_event_count ?? Number.MAX_SAFE_INTEGER;
  if (!Number.isSafeInteger(maximumEvents) || maximumEvents < 1) return fail("transition-assessment", ["reasoning.transition-event-budget-invalid"]);
  const checkpointPolicy = selectReasoningCheckpointPolicy({boundary: input.boundary ?? "observation", policy_ref: input.checkpoint_policy_ref});
  if (!checkpointPolicy.ok) return checkpointPolicy;
  let comparison = null;
  if (input.candidate_epoch !== undefined && input.candidate_epoch !== null) {
    comparison = compareReasoningProvenance(currentEpoch, input.candidate_epoch);
    if (!comparison.ok) return fail("transition-assessment", comparison.reason_codes);
  }
  const overBudget = currentEpoch.event_digests.length > maximumEvents;
  let selectedAction = requestedAction;
  const reasons = [];
  if (requestedAction === "auto") {
    if (overBudget) selectedAction = "reduce";
    else if (comparison && !comparison.value.reuse_eligible) selectedAction = "branch";
    else if (checkpointPolicy.value.checkpoint_required) selectedAction = "checkpoint";
    else selectedAction = "reuse";
  }
  if (overBudget && selectedAction !== "reduce") reasons.push("reasoning.transition-event-budget-exceeded");
  if (selectedAction === "reduce" && (!Array.isArray(input.retained_event_digests) || input.retained_event_digests.length === 0)) reasons.push("reasoning.transition-reduction-selection-required");
  if (selectedAction === "branch" && (!text(input.branch_ref) || !Array.isArray(input.additional_event_digests) || input.additional_event_digests.length === 0)) reasons.push("reasoning.transition-branch-input-required");
  if (selectedAction === "portable-export" && !record(input.compatibility_profile)) reasons.push("reasoning.transition-compatibility-profile-required");
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_TRANSITION_ASSESSMENT_SCHEMA,
    current_epoch_digest: currentEpoch.epoch_digest,
    candidate_epoch_digest: input.candidate_epoch?.epoch_digest ?? null,
    requested_action: requestedAction,
    selected_action: reasons.length > 0 ? "block" : selectedAction,
    boundary: checkpointPolicy.value.boundary,
    checkpoint_policy: checkpointPolicy.value,
    maximum_event_count: maximumEvents,
    current_event_count: currentEpoch.event_digests.length,
    provenance_comparison: comparison?.value ?? null,
    reason_codes: reasons.sort(),
    authority_effect: "none",
  });
  return freeze({ok: reasons.length === 0, disposition: reasons.length === 0 ? "planned" : "block", value: {...material, assessment_digest: digest(material)}, reason_codes: reasons.sort(), authority_effect: "none"});
}

function transitionPlanMaterial(plan) {
  const {plan_digest: _planDigest, plan_id: _planId, ...material} = plan;
  return material;
}

export function planReasoningStateTransition(input = {}) {
  const assessment = assessReasoningStateTransition(input);
  if (!assessment.ok) return assessment;
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_TRANSITION_PLAN_SCHEMA,
    assessment: assessment.value,
    current_epoch: input.current_epoch,
    candidate_epoch: input.candidate_epoch ?? null,
    branch_ref: text(input.branch_ref) ? input.branch_ref.trim() : null,
    additional_event_digests: Array.isArray(input.additional_event_digests) ? [...input.additional_event_digests] : [],
    retained_event_digests: Array.isArray(input.retained_event_digests) ? [...input.retained_event_digests] : [],
    compatibility_profile: record(input.compatibility_profile) ? input.compatibility_profile : null,
    transition_basis: record(input.transition_basis) ? input.transition_basis : {},
    authority_effect: "none",
  });
  const planDigest = digest(material);
  const plan = freeze({...material, plan_id: `reasoning-transition:${planDigest}`, plan_digest: planDigest});
  return freeze({ok: true, disposition: "planned", value: plan, digest: planDigest, authority_effect: "none"});
}

export function verifyReasoningStateTransitionPlan(plan) {
  const reasons = [];
  if (!record(plan) || plan.schema_version !== REASONING_STATE_TRANSITION_PLAN_SCHEMA) reasons.push("reasoning.transition-plan-schema-invalid");
  if (record(plan)) {
    const expected = digest(transitionPlanMaterial(plan));
    if (plan.plan_digest !== expected) reasons.push("reasoning.transition-plan-digest-invalid");
    if (plan.plan_id !== `reasoning-transition:${expected}`) reasons.push("reasoning.transition-plan-id-invalid");
  }
  if (!verifyReasoningStateEpoch(plan?.current_epoch).ok) reasons.push("reasoning.transition-plan-current-epoch-invalid");
  if (plan?.authority_effect !== "none" || plan?.assessment?.authority_effect !== "none") reasons.push("reasoning.transition-plan-authority-invalid");
  return reasons.length > 0 ? fail("transition-plan-verification", reasons) : freeze({ok: true, value: plan, digest: plan.plan_digest, authority_effect: "none"});
}

function transitionReceiptMaterial(receipt) {
  const {receipt_digest: _receiptDigest, receipt_id: _receiptId, ...material} = receipt;
  return material;
}

export function executeReasoningStateTransition(ledger, plan) {
  const verified = verifyReasoningStateTransitionPlan(plan);
  if (!verified.ok) return verified;
  const action = plan.assessment.selected_action;
  let result;
  if (action === "reuse") result = freeze({ok: true, disposition: "reused", epoch: plan.current_epoch, authority_effect: "none"});
  else if (action === "branch") result = createReasoningStateBranch(ledger, {base_epoch: plan.current_epoch, branch_ref: plan.branch_ref, additional_event_digests: plan.additional_event_digests, branch_basis: plan.transition_basis});
  else if (action === "reduce") result = appendReasoningStateReduction(ledger, {source_epoch: plan.current_epoch, retained_event_digests: plan.retained_event_digests, reduction_basis: plan.transition_basis});
  else if (action === "checkpoint") result = checkpointReasoningStateByRisk(ledger, {boundary: plan.assessment.boundary, epoch: plan.current_epoch, subject_digest: plan.plan_digest});
  else if (action === "portable-export") result = exportPortableReasoningEpoch(ledger, plan.current_epoch, {compatibility_profile: plan.compatibility_profile});
  else return fail("transition-execution", ["reasoning.transition-action-invalid"]);
  if (!result.ok) return result;
  const outputEpoch = result.epoch ?? null;
  let checkpoint = null;
  if (outputEpoch && plan.assessment.checkpoint_policy.checkpoint_required) {
    const checkpointed = checkpointReasoningStateByRisk(ledger, {boundary: plan.assessment.boundary, epoch: outputEpoch, subject_digest: plan.plan_digest});
    if (!checkpointed.ok) return checkpointed;
    checkpoint = checkpointed.checkpoint;
  }
  const material = canonicalizeJson({schema_version: REASONING_STATE_TRANSITION_RECEIPT_SCHEMA, plan, action, disposition: result.disposition ?? "completed", input_epoch_digest: plan.current_epoch.epoch_digest, output_epoch_digest: outputEpoch?.epoch_digest ?? plan.current_epoch.epoch_digest, result, result_digest: digest(result), checkpoint_digest: checkpoint?.checkpoint_digest ?? result.checkpoint?.checkpoint_digest ?? null, authority_effect: "none"});
  const receiptDigest = digest(material);
  const receipt = freeze({...material, receipt_id: `reasoning-transition-receipt:${receiptDigest}`, receipt_digest: receiptDigest});
  return freeze({ok: true, disposition: "completed", result, receipt, digest: receiptDigest, authority_effect: "none"});
}

export function verifyReasoningStateTransitionReceipt(receipt) {
  const reasons = [];
  if (!record(receipt) || receipt.schema_version !== REASONING_STATE_TRANSITION_RECEIPT_SCHEMA) reasons.push("reasoning.transition-receipt-schema-invalid");
  if (!verifyReasoningStateTransitionPlan(receipt?.plan).ok) reasons.push("reasoning.transition-receipt-plan-invalid");
  if (!record(receipt?.result) || receipt?.result_digest !== digest(receipt?.result)) reasons.push("reasoning.transition-receipt-result-invalid");
  if (record(receipt?.result?.epoch) && receipt.output_epoch_digest !== receipt.result.epoch.epoch_digest) reasons.push("reasoning.transition-receipt-output-epoch-invalid");
  if (record(receipt)) {
    const expected = digest(transitionReceiptMaterial(receipt));
    if (receipt.receipt_digest !== expected) reasons.push("reasoning.transition-receipt-digest-invalid");
    if (receipt.receipt_id !== `reasoning-transition-receipt:${expected}`) reasons.push("reasoning.transition-receipt-id-invalid");
  }
  if (receipt?.authority_effect !== "none") reasons.push("reasoning.transition-receipt-authority-invalid");
  return reasons.length > 0 ? fail("transition-receipt-verification", reasons) : freeze({ok: true, value: receipt, digest: receipt.receipt_digest, authority_effect: "none"});
}

export function checkpointReasoningState(ledger, input = {}) {
  const state = ledgerState(ledger);
  if (!record(input) || !CHECKPOINT_KINDS.has(input.checkpoint_kind)) return fail("checkpoint", ["reasoning.checkpoint-kind-invalid"]);
  const epoch = input.epoch;
  const events = Array.isArray(epoch?.event_digests) ? epoch.event_digests.map((eventDigest) => state.eventsByDigest.get(eventDigest)) : [];
  const verified = verifyReasoningStateEpoch(epoch, events);
  if (!verified.ok) return fail("checkpoint", verified.reason_codes, verified.residue);
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_CHECKPOINT_SCHEMA,
    ledger_id: state.ledgerId,
    checkpoint_kind: input.checkpoint_kind,
    epoch_id: epoch.epoch_id,
    epoch_digest: epoch.epoch_digest,
    subject_digest: text(input.subject_digest) ? input.subject_digest.trim() : null,
    head_event_digest: state.events.at(-1)?.event_digest ?? null,
    durability: state.sink.durability,
    authority_effect: "none",
  });
  const checkpoint = freeze({...material, checkpoint_digest: digest(material)});
  if (!state.checkpoints.has(checkpoint.checkpoint_digest)) {
    const persisted = state.sink.append({record_kind: "reasoning-state-checkpoint", value: checkpoint});
    if (!persisted?.ok) return fail("checkpoint", persisted?.reason_codes ?? ["reasoning.sink-append-failed"], persisted?.residue ?? []);
    state.checkpoints.set(checkpoint.checkpoint_digest, checkpoint);
  }
  const flushed = state.sink.flush();
  if (!flushed?.ok) return fail("checkpoint", flushed?.reason_codes ?? ["reasoning.sink-flush-failed"], flushed?.residue ?? []);
  return freeze({ok: true, value: checkpoint, digest: checkpoint.checkpoint_digest, flush: flushed, authority_effect: "none"});
}

function inspectReasoningStateRecords(records, expectedLedgerId = null) {
  const reasons = [];
  const residue = [];
  const events = [];
  const eventsByKey = new Map();
  const eventsByDigest = new Map();
  const epochs = new Map();
  const checkpoints = new Map();
  const frontierEvents = [];
  const frontiers = new Map();
  let ledgerId = text(expectedLedgerId) ? expectedLedgerId.trim() : null;

  if (!Array.isArray(records)) return {ok: false, failure: fail("log-verification", ["reasoning.log-records-invalid"])};
  for (let index = 0; index < records.length; index += 1) {
    const wrapper = records[index];
    const recordNumber = index + 1;
    if (!record(wrapper) || Object.keys(wrapper).sort().join(",") !== "record_kind,value" || !text(wrapper.record_kind) || !record(wrapper.value)) {
      reasons.push("reasoning.log-record-wrapper-invalid");
      residue.push({record_number: recordNumber});
      continue;
    }
    const value = wrapper.value;
    const valueLedgerId = text(value.ledger_id) ? value.ledger_id.trim() : null;
    if (ledgerId === null && valueLedgerId !== null) ledgerId = valueLedgerId;
    if (valueLedgerId === null || (ledgerId !== null && valueLedgerId !== ledgerId)) {
      reasons.push("reasoning.log-ledger-id-mismatch");
      residue.push({record_number: recordNumber, expected_ledger_id: ledgerId, actual_ledger_id: valueLedgerId});
      continue;
    }

    if (wrapper.record_kind === "reasoning-state-event") {
      if (!verifyEvent(value)) {
        reasons.push("reasoning.log-event-invalid");
        residue.push({record_number: recordNumber});
        continue;
      }
      const expectedSequence = events.length + 1;
      const expectedPredecessor = events.at(-1)?.event_digest ?? null;
      if (value.sequence !== expectedSequence) reasons.push("reasoning.log-event-sequence-invalid");
      if (value.predecessor_digest !== expectedPredecessor) reasons.push("reasoning.log-event-chain-invalid");
      if (eventsByDigest.has(value.event_digest)) reasons.push("reasoning.log-event-digest-duplicate");
      if (eventsByKey.has(value.idempotency_key)) reasons.push("reasoning.log-event-idempotency-duplicate");
      if (value.sequence !== expectedSequence || value.predecessor_digest !== expectedPredecessor || eventsByDigest.has(value.event_digest) || eventsByKey.has(value.idempotency_key)) {
        residue.push({record_number: recordNumber, event_digest: value.event_digest});
        continue;
      }
      events.push(value);
      eventsByDigest.set(value.event_digest, value);
      eventsByKey.set(value.idempotency_key, value);
      if (value.event_kind === "reasoning-frontier-sealed") frontierEvents.push({event: value, recordNumber});
      continue;
    }

    if (wrapper.record_kind === "reasoning-state-epoch") {
      const selectedEvents = Array.isArray(value.event_digests) ? value.event_digests.map((eventDigest) => eventsByDigest.get(eventDigest)) : [];
      if (!verifyReasoningStateEpoch(value, selectedEvents).ok || selectedEvents.some((event) => !event)) {
        reasons.push("reasoning.log-epoch-invalid");
        residue.push({record_number: recordNumber, epoch_digest: value.epoch_digest ?? null});
        continue;
      }
      if (epochs.has(value.epoch_digest)) {
        reasons.push("reasoning.log-epoch-duplicate");
        residue.push({record_number: recordNumber, epoch_digest: value.epoch_digest});
        continue;
      }
      epochs.set(value.epoch_digest, value);
      continue;
    }

    if (wrapper.record_kind === "reasoning-state-checkpoint") {
      const epoch = epochs.get(value.epoch_digest);
      if (!verifyCheckpoint(value) || !epoch || value.epoch_id !== epoch.epoch_id || value.head_event_digest !== (events.at(-1)?.event_digest ?? null)) {
        reasons.push("reasoning.log-checkpoint-invalid");
        residue.push({record_number: recordNumber, checkpoint_digest: value.checkpoint_digest ?? null});
        continue;
      }
      if (checkpoints.has(value.checkpoint_digest)) {
        reasons.push("reasoning.log-checkpoint-duplicate");
        residue.push({record_number: recordNumber, checkpoint_digest: value.checkpoint_digest});
        continue;
      }
      checkpoints.set(value.checkpoint_digest, value);
      continue;
    }

    reasons.push("reasoning.log-record-kind-unknown");
    residue.push({record_number: recordNumber, record_kind: wrapper.record_kind});
  }

  for (const {event, recordNumber} of frontierEvents) {
    const frontier = event.content;
    const verifiedFrontier = verifyReasoningStateFrontier(frontier);
    if (!verifiedFrontier.ok || frontier.ledger_id !== ledgerId) {
      reasons.push("reasoning.log-frontier-invalid");
      residue.push({record_number: recordNumber, frontier_key: frontier?.frontier_key ?? null});
      continue;
    }
    if (frontiers.has(frontier.frontier_key)) {
      reasons.push("reasoning.log-frontier-key-duplicate");
      residue.push({record_number: recordNumber, frontier_key: frontier.frontier_key});
      continue;
    }
    const matchingEpochs = [...epochs.values()].filter((epoch) => epoch.event_digests.length === 1
      && epoch.event_digests[0] === event.event_digest
      && epoch.frontier?.reasoning_frontier_digest === frontier.frontier_digest);
    const matchingCheckpoints = matchingEpochs.flatMap((epoch) => [...checkpoints.values()].filter((checkpoint) => checkpoint.checkpoint_kind === "after-turn-completion"
      && checkpoint.epoch_digest === epoch.epoch_digest
      && checkpoint.subject_digest === frontier.subject_digest));
    if (matchingEpochs.length !== 1 || matchingCheckpoints.length !== 1) {
      reasons.push("reasoning.log-frontier-checkpoint-missing");
      residue.push({record_number: recordNumber, frontier_key: frontier.frontier_key});
      continue;
    }
    frontiers.set(frontier.frontier_key, freeze({frontier, event, epoch: matchingEpochs[0], checkpoint: matchingCheckpoints[0]}));
  }

  if (reasons.length > 0) return {ok: false, failure: fail("log-verification", reasons, residue)};
  const indexMaterial = canonicalizeJson({
    schema_version: REASONING_STATE_INDEX_SCHEMA,
    ledger_id: ledgerId,
    record_count: records.length,
    event_count: events.length,
    epoch_count: epochs.size,
    checkpoint_count: checkpoints.size,
    frontier_count: frontiers.size,
    head_event_digest: events.at(-1)?.event_digest ?? null,
    event_digests: events.map((event) => event.event_digest),
    epoch_digests: [...epochs.keys()],
    checkpoint_digests: [...checkpoints.keys()],
    frontier_digests: [...frontiers.values()].map((entry) => entry.frontier.frontier_digest),
    latest_checkpoint_digest: [...checkpoints.keys()].at(-1) ?? null,
    record_stream_digest: digest(records),
    derived: true,
    authority_effect: "none",
  });
  const index = freeze({...indexMaterial, index_digest: digest(indexMaterial)});
  return {ok: true, ledgerId, events, eventsByKey, eventsByDigest, epochs, checkpoints, frontiers, index};
}

function logValue(input, options = {}) {
  if (text(input)) return verifyReasoningStateLog(input, options);
  if (record(input) && input.schema_version === REASONING_STATE_LOG_VERIFICATION_SCHEMA && Array.isArray(input.records)) {
    return freeze({ok: true, value: input, authority_effect: "none"});
  }
  if (record(input) && input.ok === true && record(input.value) && input.value.schema_version === REASONING_STATE_LOG_VERIFICATION_SCHEMA) return input;
  return fail("log-verification", ["reasoning.log-input-invalid"]);
}

export function verifyReasoningStateLog(path, {allow_missing = false, expected_ledger_id = null} = {}) {
  if (!text(path)) return fail("log-verification", ["reasoning.log-path-required"]);
  const absolutePath = resolve(path);
  const present = existsSync(absolutePath);
  if (!present && !allow_missing) return fail("log-verification", ["reasoning.log-missing"], [{path: absolutePath}]);
  let bytes = Buffer.alloc(0);
  if (present) {
    try {
      bytes = readFileSync(absolutePath);
    } catch (error) {
      return fail("log-verification", ["reasoning.log-read-failed"], [{path: absolutePath, message: error.message}]);
    }
  }
  let source;
  try {
    source = new TextDecoder("utf-8", {fatal: true}).decode(bytes);
  } catch {
    return fail("log-verification", ["reasoning.log-utf8-invalid"], [{path: absolutePath}]);
  }
  if (source.length > 0 && !source.endsWith("\n")) return fail("log-verification", ["reasoning.log-torn-tail"], [{path: absolutePath, byte_count: bytes.length}]);
  const lines = source.length === 0 ? [] : source.slice(0, -1).split("\n");
  const records = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.length === 0) return fail("log-verification", ["reasoning.log-blank-record"], [{line_number: index + 1}]);
    let parsed;
    try {
      parsed = JSON.parse(line);
    } catch {
      return fail("log-verification", ["reasoning.log-json-invalid"], [{line_number: index + 1}]);
    }
    if (canonicalJson(canonicalizeJson(parsed)) !== line) return fail("log-verification", ["reasoning.log-record-noncanonical"], [{line_number: index + 1}]);
    records.push(parsed);
  }
  const inspected = inspectReasoningStateRecords(records, expected_ledger_id);
  if (!inspected.ok) return inspected.failure;
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_LOG_VERIFICATION_SCHEMA,
    path: absolutePath,
    source_state: present ? "present" : "absent",
    byte_count: bytes.length,
    log_digest: sha256HexText(source),
    records,
    index: inspected.index,
    external_calls: 0,
    authority_effect: "none",
  });
  return freeze({ok: true, value: {...material, verification_digest: digest(material)}, authority_effect: "none"});
}

export function rebuildReasoningStateIndexes(log, options = {}) {
  const verified = logValue(log, options);
  if (!verified.ok) return verified;
  const inspected = inspectReasoningStateRecords(verified.value.records, options.expected_ledger_id ?? null);
  if (!inspected.ok) return inspected.failure;
  return freeze({ok: true, value: inspected.index, digest: inspected.index.index_digest, external_calls: 0, authority_effect: "none"});
}

export function selectRecoverableCheckpoint(log, options = {}) {
  const verified = logValue(log, options);
  if (!verified.ok) return verified;
  const records = verified.value.records;
  if (records.length === 0) return freeze({ok: true, disposition: "empty", value: null, log_digest: verified.value.log_digest, authority_effect: "none"});
  const last = records.at(-1);
  if (last.record_kind !== "reasoning-state-checkpoint") {
    return fail("checkpoint-selection", ["reasoning.log-uncheckpointed-tail"], [{record_count: records.length, last_record_kind: last.record_kind}]);
  }
  return freeze({ok: true, disposition: "recoverable", value: last.value, digest: last.value.checkpoint_digest, log_digest: verified.value.log_digest, authority_effect: "none"});
}

export function recoverReasoningStateLedger(input, options = {}) {
  const configured = text(input) ? {path: input, ...options} : input;
  if (!record(configured) || !text(configured.path)) return fail("recovery", ["reasoning.log-path-required"]);
  const expectedLedgerId = text(configured.ledger_id) ? configured.ledger_id.trim() : null;
  const verified = verifyReasoningStateLog(configured.path, {allow_missing: configured.create_if_missing !== false, expected_ledger_id: expectedLedgerId});
  if (!verified.ok) return verified;
  const selected = selectRecoverableCheckpoint(verified);
  if (!selected.ok) return selected;
  const inspected = inspectReasoningStateRecords(verified.value.records, expectedLedgerId);
  if (!inspected.ok) return inspected.failure;
  const ledgerId = inspected.ledgerId ?? expectedLedgerId;
  if (!text(ledgerId)) return fail("recovery", ["reasoning.recovery-ledger-id-required"]);
  let sink;
  try {
    sink = createAppendOnlyFileReasoningStateSink({path: verified.value.path, initial_record_count: verified.value.records.length});
  } catch (error) {
    return fail("recovery", ["reasoning.recovery-sink-open-failed"], [{message: error.message}]);
  }
  let currentSource;
  try {
    currentSource = new TextDecoder("utf-8", {fatal: true}).decode(readFileSync(verified.value.path));
  } catch (error) {
    sink.close();
    return fail("recovery", ["reasoning.recovery-source-recheck-failed"], [{message: error.message}]);
  }
  if (sha256HexText(currentSource) !== verified.value.log_digest) {
    sink.close();
    return fail("recovery", ["reasoning.recovery-source-drift"], [{expected_log_digest: verified.value.log_digest, actual_log_digest: sha256HexText(currentSource)}]);
  }
  const assessmentMaterial = canonicalizeJson({
    schema_version: REASONING_STATE_RECOVERY_SCHEMA,
    ledger_id: ledgerId,
    log_path: verified.value.path,
    source_state: verified.value.source_state,
    log_digest: verified.value.log_digest,
    record_count: verified.value.records.length,
    derived_index_digest: inspected.index.index_digest,
    recovered_checkpoint_digest: selected.value?.checkpoint_digest ?? null,
    disposition: selected.disposition === "empty" ? "empty-ledger-ready" : "recovered",
    external_calls: 0,
    authority_effect: "none",
  });
  const assessment = freeze({...assessmentMaterial, recovery_digest: digest(assessmentMaterial)});
  const ledger = createReasoningStateLedger({ledger_id: ledgerId, sink});
  const state = ledgerState(ledger);
  state.events.push(...inspected.events);
  for (const [key, value] of inspected.eventsByKey) state.eventsByKey.set(key, value);
  for (const [key, value] of inspected.eventsByDigest) state.eventsByDigest.set(key, value);
  for (const [key, value] of inspected.epochs) state.epochs.set(key, value);
  for (const [key, value] of inspected.checkpoints) state.checkpoints.set(key, value);
  for (const [key, value] of inspected.frontiers) state.frontiers.set(key, value);
  state.recovery = assessment;
  return Object.freeze({ok: true, ledger, assessment, checkpoint: selected.value, authority_effect: "none"});
}

function requestConfiguration(params) {
  if (!record(params)) return {};
  const excluded = new Set(["input", "additionalContext", "provider", "model", "tools", "developerInstructions", "systemInstructions"]);
  return Object.fromEntries(Object.entries(params).filter(([key]) => !excluded.has(key)));
}

export function createRequestSeriesHeader(message, overrides = {}) {
  if (!record(message) || !text(message.method)) return fail("request-header", ["reasoning.dispatch-message-invalid"]);
  const params = record(message.params) ? message.params : {};
  const material = canonicalizeJson({
    schema_version: REASONING_REQUEST_HEADER_SCHEMA,
    protocol: message.jsonrpc ?? null,
    method: message.method,
    provider_ref: overrides.provider_ref ?? params.provider ?? null,
    model_ref: overrides.model_ref ?? params.model ?? null,
    system_digest: digest(overrides.system ?? params.developerInstructions ?? params.systemInstructions ?? null),
    tools_digest: digest(overrides.tools ?? params.tools ?? null),
    configuration_digest: digest(overrides.configuration ?? requestConfiguration(params)),
    authority_effect: "none",
  });
  return freeze({...material, request_header_digest: digest(material)});
}

function exactCommonPrefixBytes(left, right) {
  const leftBytes = Buffer.from(left ?? "", "utf8");
  const rightBytes = Buffer.from(right ?? "", "utf8");
  const upper = Math.min(leftBytes.length, rightBytes.length);
  let index = 0;
  while (index < upper && leftBytes[index] === rightBytes[index]) index += 1;
  return index;
}

function cacheStableHeader(header) {
  return canonicalizeJson({
    schema_version: header.schema_version,
    protocol: header.protocol,
    method: header.method,
    provider_ref: header.provider_ref,
    model_ref: header.model_ref,
    system_digest: header.system_digest,
    tools_digest: header.tools_digest,
    configuration_digest: header.configuration_digest,
    request_header_digest: header.request_header_digest,
    authority_effect: "none",
  });
}

function cacheInvalidationReasons(previous, current) {
  if (!record(previous)) return ["cache-affinity.no-prior-projection"];
  const reasons = [];
  const fields = [
    ["system_digest", "cache-affinity.system-changed"],
    ["tools_digest", "cache-affinity.tools-changed"],
    ["configuration_digest", "cache-affinity.configuration-changed"],
    ["provider_ref", "cache-affinity.provider-changed"],
    ["model_ref", "cache-affinity.model-changed"],
  ];
  for (const [field, reason] of fields) {
    if (previous.stable_request_prefix?.[field] !== current.stable_request_prefix?.[field]) reasons.push(reason);
  }
  if (previous.reusable_reasoning_digest !== current.reusable_reasoning_digest) reasons.push("cache-affinity.reasoning-state-changed");
  if (reasons.length === 0 && previous.exact_prefix_digest !== current.exact_prefix_digest) reasons.push("cache-affinity.prefix-bytes-changed");
  return reasons;
}

export function materializeCacheAffinityProjection(input = {}) {
  const started = process.hrtime.bigint();
  const header = input.request_header;
  if (!record(header) || header.schema_version !== REASONING_REQUEST_HEADER_SCHEMA) {
    return fail("cache-affinity-projection", ["cache-affinity.request-header-invalid"]);
  }
  const {request_header_digest: headerDigest, ...headerMaterial} = header;
  if (digest(headerMaterial) !== headerDigest) return fail("cache-affinity-projection", ["cache-affinity.request-header-digest-invalid"]);
  if (!record(input.reusable_reasoning_state)) return fail("cache-affinity-projection", ["cache-affinity.reusable-reasoning-state-required"]);
  if (!record(input.volatile_current_turn_suffix)) return fail("cache-affinity-projection", ["cache-affinity.volatile-suffix-required"]);

  const stableRequestPrefix = cacheStableHeader(header);
  const reusableReasoningState = canonicalizeJson({...input.reusable_reasoning_state, authority_effect: "none"});
  const volatileCurrentTurnSuffix = canonicalizeJson({...input.volatile_current_turn_suffix, authority_effect: "none"});
  const stableBytes = canonicalJson(stableRequestPrefix);
  const reasoningBytes = canonicalJson(reusableReasoningState);
  const volatileBytes = canonicalJson(volatileCurrentTurnSuffix);
  const exactReusablePrefix = `${stableBytes}\n${reasoningBytes}\n`;
  const wireValue = `${exactReusablePrefix}${volatileBytes}`;
  const material = canonicalizeJson({
    schema_version: REASONING_CACHE_AFFINITY_PROJECTION_SCHEMA,
    stable_request_prefix: stableRequestPrefix,
    reusable_reasoning_state: reusableReasoningState,
    reusable_reasoning_digest: digest(reusableReasoningState),
    volatile_current_turn_suffix: volatileCurrentTurnSuffix,
    stable_prefix_bytes: Buffer.byteLength(stableBytes),
    reusable_reasoning_bytes: Buffer.byteLength(reasoningBytes),
    exact_reusable_prefix_bytes: Buffer.byteLength(exactReusablePrefix),
    volatile_suffix_bytes: Buffer.byteLength(volatileBytes),
    total_projection_bytes: Buffer.byteLength(wireValue),
    exact_prefix_digest: sha256HexText(exactReusablePrefix),
    wire_digest: sha256HexText(wireValue),
    wire_value: wireValue,
    estimated_reusable_tokens: Math.ceil(Buffer.byteLength(exactReusablePrefix) / 4),
    authority_effect: "none",
  });
  const projection = freeze({...material, projection_digest: digest(material)});
  const previous = input.previous_projection;
  const exactReuse = record(previous) && previous.exact_prefix_digest === projection.exact_prefix_digest;
  const reusedPrefixBytes = exactReuse
    ? projection.exact_reusable_prefix_bytes
    : record(previous) ? exactCommonPrefixBytes(previous.wire_value, projection.wire_value) : 0;
  const invalidationReasons = exactReuse ? [] : cacheInvalidationReasons(previous, projection);
  const assessmentMaterial = canonicalizeJson({
    schema_version: REASONING_CACHE_AFFINITY_ASSESSMENT_SCHEMA,
    projection_digest: projection.projection_digest,
    prior_projection_digest: record(previous) ? previous.projection_digest ?? null : null,
    posture: exactReuse ? "eligible-reuse" : record(previous) ? "invalidated" : "cold",
    exact_prefix_reuse: exactReuse,
    reusable_prefix_bytes: projection.exact_reusable_prefix_bytes,
    reused_prefix_bytes: reusedPrefixBytes,
    estimated_reused_tokens: exactReuse ? projection.estimated_reusable_tokens : Math.floor(reusedPrefixBytes / 4),
    cache_hit_posture: "unobserved",
    observed_time_savings_ms: null,
    observed_token_savings: null,
    invalidation_reasons: [...invalidationReasons].sort(),
    projection_time_ns: Number(process.hrtime.bigint() - started),
    claim_ceiling: "Cache-affinity eligibility and exact byte comparison only; no cache hit, freshness, provenance, correctness, or authority claim.",
    authority_effect: "none",
  });
  const assessment = freeze({...assessmentMaterial, assessment_digest: digest(assessmentMaterial)});
  return freeze({ok: true, projection, assessment, authority_effect: "none"});
}

function verifyContextRefreshAssessment(assessment) {
  const reasons = [];
  if (!record(assessment) || assessment.ok !== true || !record(assessment.value) || assessment.value.schema_version !== "are.context-refresh-assessment/v1") {
    return fail("context-bound-reuse", ["context-bound-reuse.refresh-assessment-invalid"]);
  }
  const value = assessment.value;
  if (assessment.digest !== digest(value)) reasons.push("context-bound-reuse.refresh-assessment-digest-invalid");
  if (assessment.authority_effect !== "none" || value.authority_effect !== "none") reasons.push("context-bound-reuse.refresh-assessment-authority-invalid");
  if (!Array.isArray(value.current_selected_dependencies) || !Array.isArray(value.changed_selected_dependencies) || !Array.isArray(value.unrelated_source_drift)) reasons.push("context-bound-reuse.refresh-assessment-shape-invalid");
  if (!["reuse-current", "successor-required"].includes(value.disposition)) reasons.push("context-bound-reuse.refresh-disposition-invalid");
  if (value.reuse_allowed !== (value.disposition === "reuse-current")) reasons.push("context-bound-reuse.refresh-reuse-flag-inconsistent");
  if (value.disposition === "reuse-current" && value.changed_selected_dependencies?.length !== 0) reasons.push("context-bound-reuse.refresh-change-set-inconsistent");
  if (value.disposition === "successor-required" && value.changed_selected_dependencies?.length === 0) reasons.push("context-bound-reuse.refresh-change-set-inconsistent");
  for (const dependency of value.current_selected_dependencies ?? []) {
    if (!record(dependency) || !text(dependency.dependency_id) || !text(dependency.digest)) reasons.push("context-bound-reuse.selected-dependency-invalid");
  }
  return reasons.length > 0 ? fail("context-bound-reuse", reasons) : freeze({ok: true, value, digest: assessment.digest, authority_effect: "none"});
}

function verifyPriorCacheProjection(projection) {
  if (projection === null || projection === undefined) return freeze({ok: true, value: null, authority_effect: "none"});
  const reasons = [];
  if (!record(projection) || projection.schema_version !== REASONING_CACHE_AFFINITY_PROJECTION_SCHEMA) return fail("context-bound-reuse", ["context-bound-reuse.prior-projection-invalid"]);
  const {projection_digest: projectionDigest, ...material} = projection;
  if (!text(projectionDigest) || digest(material) !== projectionDigest) reasons.push("context-bound-reuse.prior-projection-digest-invalid");
  const stableBytes = canonicalJson(projection.stable_request_prefix);
  const reasoningBytes = canonicalJson(projection.reusable_reasoning_state);
  const volatileBytes = canonicalJson(projection.volatile_current_turn_suffix);
  const exactPrefix = `${stableBytes}\n${reasoningBytes}\n`;
  const wireValue = `${exactPrefix}${volatileBytes}`;
  if (projection.exact_prefix_digest !== sha256HexText(exactPrefix) || projection.wire_digest !== sha256HexText(wireValue) || projection.wire_value !== wireValue) reasons.push("context-bound-reuse.prior-projection-bytes-invalid");
  return reasons.length > 0 ? fail("context-bound-reuse", reasons) : freeze({ok: true, value: projection, authority_effect: "none"});
}

export function materializeContextBoundCacheAffinityProjection(input = {}) {
  const refresh = verifyContextRefreshAssessment(input.refresh_assessment);
  if (!refresh.ok) return refresh;
  const prior = verifyPriorCacheProjection(input.previous_projection ?? null);
  if (!prior.ok) return prior;
  if (!record(input.current_reusable_reasoning_state)) return fail("context-bound-reuse", ["context-bound-reuse.reusable-reasoning-state-required"]);

  const selectedDependenciesDigest = digest(refresh.value.current_selected_dependencies);
  if (input.current_reusable_reasoning_state.selected_dependencies_digest !== selectedDependenciesDigest) {
    return fail("context-bound-reuse", ["context-bound-reuse.selected-dependencies-binding-mismatch"], [{expected_digest: selectedDependenciesDigest, observed_digest: input.current_reusable_reasoning_state.selected_dependencies_digest ?? null}]);
  }

  const projected = materializeCacheAffinityProjection({
    request_header: input.request_header,
    reusable_reasoning_state: input.current_reusable_reasoning_state,
    volatile_current_turn_suffix: input.volatile_current_turn_suffix,
    previous_projection: prior.value,
  });
  if (!projected.ok) return projected;

  const selectedDrift = refresh.value.disposition === "successor-required";
  if (selectedDrift && projected.assessment.exact_prefix_reuse) {
    return fail("context-bound-reuse", ["context-bound-reuse.stale-prefix-eligible"]);
  }
  if (selectedDrift && prior.value !== null && !projected.assessment.invalidation_reasons.includes("cache-affinity.reasoning-state-changed")) {
    return fail("context-bound-reuse", ["context-bound-reuse.selected-drift-not-projected"]);
  }

  const disposition = prior.value === null
    ? "cold-start"
    : projected.assessment.exact_prefix_reuse ? "reuse-current" : "successor-created";
  const reasonCodes = [...new Set([
    ...refresh.value.reason_codes,
    ...projected.assessment.invalidation_reasons,
    disposition === "reuse-current" ? "context-bound-reuse.exact-prefix-current"
      : disposition === "cold-start" ? "context-bound-reuse.no-prior-projection"
        : "context-bound-reuse.successor-projection-created",
  ])].sort();
  const material = canonicalizeJson({
    schema_version: CONTEXT_BOUND_REUSE_RECEIPT_SCHEMA,
    disposition,
    refresh_assessment_digest: refresh.digest,
    refresh_disposition: refresh.value.disposition,
    selected_dependencies_digest: selectedDependenciesDigest,
    previous_projection_digest: prior.value?.projection_digest ?? null,
    current_projection_digest: projected.projection.projection_digest,
    exact_prefix_digest: projected.projection.exact_prefix_digest,
    exact_prefix_reuse: projected.assessment.exact_prefix_reuse,
    reusable_prefix_bytes: projected.assessment.reusable_prefix_bytes,
    reused_prefix_bytes: projected.assessment.reused_prefix_bytes,
    cache_hit_posture: projected.assessment.cache_hit_posture,
    changed_selected_dependencies: refresh.value.changed_selected_dependencies,
    unrelated_source_drift: refresh.value.unrelated_source_drift,
    invalidation_reasons: projected.assessment.invalidation_reasons,
    reason_codes: reasonCodes,
    claim_ceiling: "Context currentness and exact-prefix eligibility only; no provider cache hit, semantic correctness, freshness beyond selected sources, or effect authority.",
    authority_effect: "none",
  });
  const receipt = freeze({...material, receipt_digest: digest(material)});
  return freeze({ok: true, projection: projected.projection, assessment: projected.assessment, receipt, authority_effect: "none"});
}

export function bindCacheTelemetryObservation(input = {}) {
  const projection = input.projection;
  const assessment = input.assessment;
  if (!record(projection) || projection.schema_version !== REASONING_CACHE_AFFINITY_PROJECTION_SCHEMA || !text(projection.projection_digest) || !text(projection.exact_prefix_digest)) {
    return fail("cache-telemetry", ["cache-telemetry.projection-invalid"]);
  }
  if (!record(assessment) || assessment.schema_version !== REASONING_CACHE_AFFINITY_ASSESSMENT_SCHEMA || assessment.projection_digest !== projection.projection_digest) {
    return fail("cache-telemetry", ["cache-telemetry.assessment-binding-invalid"]);
  }
  const usage = input.provider_usage;
  if (usage === null || usage === undefined) {
    const material = canonicalizeJson({
      schema_version: REASONING_CACHE_TELEMETRY_OBSERVATION_SCHEMA,
      projection_digest: projection.projection_digest,
      assessment_digest: assessment.assessment_digest,
      exact_prefix_digest: projection.exact_prefix_digest,
      cache_hit_posture: "unobserved",
      observed_input_tokens: null,
      observed_cached_input_tokens: null,
      observed_token_savings: null,
      observed_latency_ms: null,
      observed_time_savings_ms: null,
      reason_codes: ["cache-telemetry.provider-usage-unavailable"],
      claim_ceiling: "No provider cache telemetry was supplied; cache eligibility remains distinct from an observed cache hit.",
      authority_effect: "none",
    });
    return freeze({ok: true, value: {...material, observation_digest: digest(material)}, authority_effect: "none"});
  }
  const reasons = [];
  if (!record(usage) || usage.schema_version !== "are.provider-cache-usage/v1") reasons.push("cache-telemetry.provider-usage-invalid");
  if (usage?.projection_digest !== projection.projection_digest || usage?.exact_prefix_digest !== projection.exact_prefix_digest) reasons.push("cache-telemetry.projection-binding-mismatch");
  if (usage?.provider_ref !== projection.stable_request_prefix?.provider_ref) reasons.push("cache-telemetry.provider-binding-mismatch");
  if (usage?.model_ref !== projection.stable_request_prefix?.model_ref) reasons.push("cache-telemetry.model-binding-mismatch");
  for (const field of ["input_tokens", "cached_input_tokens"]) {
    if (!Number.isSafeInteger(usage?.[field]) || usage[field] < 0) reasons.push(`cache-telemetry.${field.replaceAll("_", "-")}-invalid`);
  }
  if (Number.isSafeInteger(usage?.input_tokens) && Number.isSafeInteger(usage?.cached_input_tokens) && usage.cached_input_tokens > usage.input_tokens) reasons.push("cache-telemetry.cached-input-exceeds-input");
  for (const field of ["latency_ms", "baseline_latency_ms"]) {
    if (usage?.[field] !== undefined && (typeof usage[field] !== "number" || !Number.isFinite(usage[field]) || usage[field] < 0)) reasons.push(`cache-telemetry.${field.replaceAll("_", "-")}-invalid`);
  }
  if (reasons.length > 0) return fail("cache-telemetry", reasons);
  const observedTimeSavings = usage.baseline_latency_ms === undefined || usage.latency_ms === undefined
    ? null
    : Math.max(0, usage.baseline_latency_ms - usage.latency_ms);
  const material = canonicalizeJson({
    schema_version: REASONING_CACHE_TELEMETRY_OBSERVATION_SCHEMA,
    projection_digest: projection.projection_digest,
    assessment_digest: assessment.assessment_digest,
    exact_prefix_digest: projection.exact_prefix_digest,
    provider_ref: usage.provider_ref,
    model_ref: usage.model_ref,
    cache_hit_posture: usage.cached_input_tokens > 0 ? "observed-hit" : "observed-miss",
    observed_input_tokens: usage.input_tokens,
    observed_cached_input_tokens: usage.cached_input_tokens,
    observed_token_savings: usage.cached_input_tokens,
    observed_latency_ms: usage.latency_ms ?? null,
    observed_time_savings_ms: observedTimeSavings,
    reason_codes: [],
    claim_ceiling: "Exact provider usage bound to one cache-affinity projection; no freshness, correctness, provenance, or authority claim.",
    authority_effect: "none",
  });
  return freeze({ok: true, value: {...material, observation_digest: digest(material)}, authority_effect: "none"});
}

function dispatchMaterial(dispatch) {
  const {dispatch_digest: _dispatchDigest, ...material} = dispatch;
  return material;
}

export function materializeReasoningDispatch({epoch, message, request_header = null} = {}) {
  const epochVerified = verifyReasoningStateEpoch(epoch);
  if (!epochVerified.ok) return fail("dispatch-materialization", epochVerified.reason_codes);
  if (!record(message) || !text(message.method)) return fail("dispatch-materialization", ["reasoning.dispatch-message-invalid"]);
  const header = request_header ?? createRequestSeriesHeader(message);
  if (!record(header) || header.schema_version !== REASONING_REQUEST_HEADER_SCHEMA) return fail("dispatch-materialization", ["reasoning.request-header-invalid"]);
  const {request_header_digest: headerDigest, ...headerMaterial} = header;
  if (digest(headerMaterial) !== headerDigest) return fail("dispatch-materialization", ["reasoning.request-header-digest-invalid"]);
  const canonicalRequest = canonicalJson(canonicalizeJson(message));
  const material = canonicalizeJson({
    schema_version: REASONING_DISPATCH_SCHEMA,
    epoch_id: epoch.epoch_id,
    epoch_digest: epoch.epoch_digest,
    request_header: header,
    request_header_digest: header.request_header_digest,
    canonical_request: canonicalRequest,
    canonical_request_bytes: Buffer.byteLength(canonicalRequest),
    message_digest: sha256HexText(canonicalRequest),
    authority_effect: "none",
  });
  const value = freeze({...material, dispatch_digest: digest(material)});
  return freeze({ok: true, value, digest: value.dispatch_digest, authority_effect: "none"});
}

export function verifyReasoningDispatch(dispatch, {epoch = null, message = null} = {}) {
  const reasons = [];
  if (!record(dispatch) || dispatch.schema_version !== REASONING_DISPATCH_SCHEMA) reasons.push("reasoning.dispatch-schema-invalid");
  if (!text(dispatch?.dispatch_digest) || (record(dispatch) && digest(dispatchMaterial(dispatch)) !== dispatch.dispatch_digest)) reasons.push("reasoning.dispatch-digest-invalid");
  let reconstructed = null;
  try {
    reconstructed = JSON.parse(dispatch?.canonical_request);
    if (canonicalJson(canonicalizeJson(reconstructed)) !== dispatch.canonical_request) reasons.push("reasoning.dispatch-canonical-request-invalid");
  } catch {
    reasons.push("reasoning.dispatch-request-invalid");
  }
  if (text(dispatch?.canonical_request) && sha256HexText(dispatch.canonical_request) !== dispatch.message_digest) reasons.push("reasoning.dispatch-message-digest-invalid");
  if (Buffer.byteLength(dispatch?.canonical_request ?? "") !== dispatch?.canonical_request_bytes) reasons.push("reasoning.dispatch-byte-count-invalid");
  const header = dispatch?.request_header;
  if (!record(header)) reasons.push("reasoning.request-header-invalid");
  else {
    const {request_header_digest: headerDigest, ...headerMaterial} = header;
    if (digest(headerMaterial) !== headerDigest || headerDigest !== dispatch.request_header_digest) reasons.push("reasoning.request-header-digest-invalid");
  }
  if (epoch && (dispatch?.epoch_id !== epoch.epoch_id || dispatch?.epoch_digest !== epoch.epoch_digest)) reasons.push("reasoning.dispatch-epoch-mismatch");
  if (message && canonicalJson(canonicalizeJson(message)) !== dispatch?.canonical_request) reasons.push("reasoning.dispatch-message-mismatch");
  const material = canonicalizeJson({
    schema_version: REASONING_DISPATCH_VERIFICATION_SCHEMA,
    dispatch_digest: dispatch?.dispatch_digest ?? null,
    epoch_digest: dispatch?.epoch_digest ?? null,
    message_digest: dispatch?.message_digest ?? null,
    request_header_digest: dispatch?.request_header_digest ?? null,
    valid: reasons.length === 0,
    reason_codes: [...new Set(reasons)].sort(),
    authority_effect: "none",
  });
  const verification = freeze({...material, verification_digest: digest(material)});
  return reasons.length > 0
    ? freeze({ok: false, stage: "dispatch-verification", reason_codes: verification.reason_codes, verification, authority_effect: "none"})
    : freeze({ok: true, value: verification, reconstructed_message: freeze(reconstructed), digest: verification.verification_digest, authority_effect: "none"});
}

export function reconstructReasoningDispatch(dispatch, options = {}) {
  const verified = verifyReasoningDispatch(dispatch, options);
  if (!verified.ok) return verified;
  return freeze({ok: true, value: verified.reconstructed_message, dispatch_digest: dispatch.dispatch_digest, verification_digest: verified.digest, authority_effect: "none"});
}

export function sealReasoningStateFrontier(ledger, input = {}) {
  const state = ledgerState(ledger);
  const reasons = [];
  if (!record(input)) reasons.push("reasoning.frontier-input-required");
  if (!text(input?.frontier_key)) reasons.push("reasoning.frontier-key-required");
  if (!text(input?.subject_digest)) reasons.push("reasoning.frontier-subject-digest-required");
  if (!record(input?.state)) reasons.push("reasoning.frontier-state-required");
  if (reasons.length > 0) return fail("frontier-seal", reasons);
  const material = canonicalizeJson({
    schema_version: REASONING_STATE_FRONTIER_SCHEMA,
    ledger_id: state.ledgerId,
    frontier_key: input.frontier_key.trim(),
    subject_digest: input.subject_digest.trim(),
    consumer_ref: text(input.consumer_ref) ? input.consumer_ref.trim() : null,
    request_ref: text(input.request_ref) ? input.request_ref.trim() : null,
    context_envelope_digest: text(input.context_envelope_digest) ? input.context_envelope_digest.trim() : null,
    prior_reasoning_epoch_digest: text(input.prior_reasoning_epoch_digest) ? input.prior_reasoning_epoch_digest.trim() : null,
    state: canonicalizeJson(input.state),
    authority_effect: "none",
  });
  const frontierDigest = digest(material);
  const frontier = freeze({...material, frontier_id: `reasoning-frontier:${frontierDigest}`, frontier_digest: frontierDigest});
  const existing = state.frontiers.get(frontier.frontier_key);
  if (existing) {
    if (existing.frontier.frontier_digest !== frontier.frontier_digest) {
      return fail("frontier-seal", ["reasoning.frontier-idempotency-conflict"], [{frontier_key: frontier.frontier_key, existing_frontier_digest: existing.frontier.frontier_digest}]);
    }
    return freeze({ok: true, disposition: "duplicate", ...existing, authority_effect: "none"});
  }
  const appended = appendReasoningStateEvent(ledger, {
    event_kind: "reasoning-frontier-sealed",
    idempotency_key: `reasoning-frontier:${frontier.frontier_key}`,
    content: frontier,
    provenance_refs: Array.isArray(input.provenance_refs) ? input.provenance_refs : [],
  });
  if (!appended.ok) return appended;
  const sealed = sealReasoningStateEpoch(ledger, {
    event_digests: [appended.event.event_digest],
    consumer_ref: frontier.consumer_ref,
    request_ref: frontier.request_ref,
    context_envelope_digest: frontier.context_envelope_digest,
    frontier: {reasoning_frontier_digest: frontier.frontier_digest, frontier_key: frontier.frontier_key},
  });
  if (!sealed.ok) return sealed;
  const checkpointed = checkpointReasoningState(ledger, {
    checkpoint_kind: "after-turn-completion",
    epoch: sealed.value,
    subject_digest: frontier.subject_digest,
  });
  if (!checkpointed.ok) return checkpointed;
  const entry = freeze({frontier, event: appended.event, epoch: sealed.value, checkpoint: checkpointed.value});
  state.frontiers.set(frontier.frontier_key, entry);
  return freeze({ok: true, disposition: "sealed", ...entry, authority_effect: "none"});
}

export function getReasoningStateFrontier(ledger, frontierKey) {
  const state = ledgerState(ledger);
  if (!text(frontierKey)) return fail("frontier-get", ["reasoning.frontier-key-required"]);
  const entry = state.frontiers.get(frontierKey.trim());
  return entry
    ? freeze({ok: true, disposition: "found", ...entry, authority_effect: "none"})
    : freeze({ok: true, disposition: "absent", value: null, authority_effect: "none"});
}

export function listReasoningStateFrontiers(ledger) {
  const state = ledgerState(ledger);
  return freeze([...state.frontiers.values()].sort((left, right) => left.frontier.frontier_key.localeCompare(right.frontier.frontier_key)));
}

export function getReasoningStateEpoch(ledger, epochDigest) {
  const state = ledgerState(ledger);
  if (!text(epochDigest)) return null;
  return state.epochs.get(epochDigest.trim()) ?? null;
}

export function listReasoningStateEpochs(ledger) {
  const state = ledgerState(ledger);
  return freeze([...state.epochs.values()].sort((left, right) => left.epoch_digest.localeCompare(right.epoch_digest)));
}

export function createReasoningStateLedger({ledger_id = "are-reasoning-state:local", sink = createMemoryReasoningStateSink()} = {}) {
  if (!text(ledger_id)) throw new TypeError("A reasoning-state ledger id is required.");
  if (!verifiedSink(sink)) throw new TypeError("A verified reasoning-state sink is required.");
  const state = {
    ledgerId: ledger_id.trim(),
    sink,
    events: [],
    eventsByKey: new Map(),
    eventsByDigest: new Map(),
    epochs: new Map(),
    checkpoints: new Map(),
    frontiers: new Map(),
    recovery: null,
  };
  const ledger = Object.freeze({
    _state: state,
    append: (input) => appendReasoningStateEvent(ledger, input),
    seal: (input) => sealReasoningStateEpoch(ledger, input),
    replay: (epoch) => replayReasoningStateEpoch(ledger, epoch),
    checkpoint: (input) => checkpointReasoningState(ledger, input),
    sealFrontier: (input) => sealReasoningStateFrontier(ledger, input),
    getFrontier: (frontierKey) => getReasoningStateFrontier(ledger, frontierKey),
    frontiers: () => listReasoningStateFrontiers(ledger),
    getEpoch: (epochDigest) => getReasoningStateEpoch(ledger, epochDigest),
    epochs: () => listReasoningStateEpochs(ledger),
    snapshot: () => freeze([...state.events]),
    inspect: () => freeze({ledger_id: state.ledgerId, event_count: state.events.length, epoch_count: state.epochs.size, checkpoint_count: state.checkpoints.size, frontier_count: state.frontiers.size, head_event_digest: state.events.at(-1)?.event_digest ?? null, durability: state.sink.durability, sink: state.sink.inspect?.() ?? null, recovery: state.recovery, authority_effect: "none"}),
    close: () => state.sink.close?.() ?? sinkResult("close", "unsupported"),
  });
  ledgers.add(ledger);
  return ledger;
}
