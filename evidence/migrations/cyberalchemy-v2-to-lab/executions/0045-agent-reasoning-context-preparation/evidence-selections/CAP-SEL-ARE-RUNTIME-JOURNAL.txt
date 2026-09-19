import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "../intent-route-resolver/index.mjs";

export const RUNTIME_JOURNAL_EVENT_SCHEMA = "are.runtime-journal-event/v1";
export const RUNTIME_JOURNAL_CUT_SCHEMA = "are.runtime-journal-cut/v1";
export const RUNTIME_JOURNAL_REPLAY_SCHEMA = "are.runtime-journal-replay/v1";
export const RUNTIME_JOURNAL_EVICTION_SCHEMA = "are.runtime-journal-eviction-receipt/v1";

const journals = new WeakSet();
const verifiedCuts = new WeakSet();
const replayCache = new WeakMap();

function digest(value) {
  return sha256HexText(canonicalJson(canonicalizeJson(value)));
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function text(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function freeze(value) {
  return deepFreeze(canonicalizeJson(value));
}

function failure(stage, reasonCodes, residue = []) {
  return freeze({
    schema_version: "are.runtime-journal-failure/v1",
    ok: false,
    stage,
    reason_codes: [...new Set(reasonCodes)].sort(),
    residue,
    authority_effect: "none",
  });
}

function eventPayload(input) {
  if (!isRecord(input)) return null;
  const {idempotency_key: _key, observed_at: _observed, ...payload} = input;
  return canonicalizeJson(payload);
}

function eventKey(input, payloadDigest) {
  return text(input.idempotency_key) ? input.idempotency_key.trim() : `event:${payloadDigest}`;
}

function verifyEvent(event) {
  if (!isRecord(event) || event.schema_version !== RUNTIME_JOURNAL_EVENT_SCHEMA) return false;
  const {event_digest: eventDigest, ...material} = event;
  if (!text(eventDigest) || digest(material) !== eventDigest) return false;
  return text(event.event_kind)
    && text(event.idempotency_key)
    && Number.isSafeInteger(event.sequence)
    && event.sequence > 0
    && text(event.content_digest)
    && digest(event.content) === event.content_digest
    && event.authority_effect === "none";
}

function cutMaterial(cut) {
  const {cut_digest: _digest, ...material} = cut;
  return material;
}

export function verifyRuntimeJournalCut(cut) {
  if (isRecord(cut) && verifiedCuts.has(cut)) return freeze({ok: true, value: cut, digest: cut.cut_digest, authority_effect: "none"});
  const reasons = [];
  if (!isRecord(cut) || cut.schema_version !== RUNTIME_JOURNAL_CUT_SCHEMA) reasons.push("journal.cut-schema-invalid");
  if (!text(cut?.cut_digest) || (isRecord(cut) && digest(cutMaterial(cut)) !== cut.cut_digest)) reasons.push("journal.cut-digest-invalid");
  if (!Array.isArray(cut?.events) || cut.events.some((event) => !verifyEvent(event))) reasons.push("journal.cut-event-invalid");
  if (Array.isArray(cut?.events)) {
    const sequences = cut.events.map((event) => event.sequence);
    if (sequences.some((sequence, index) => index > 0 && sequence <= sequences[index - 1])) reasons.push("journal.cut-order-invalid");
    if (new Set(cut.events.map((event) => event.idempotency_key)).size !== cut.events.length) reasons.push("journal.cut-idempotency-key-duplicate");
    if (digest(cut.events.map((event) => event.event_digest)) !== cut.event_set_digest) reasons.push("journal.cut-event-set-digest-invalid");
  }
  if (reasons.length > 0) return failure("cut-verification", reasons);
  verifiedCuts.add(cut);
  return freeze({ok: true, value: cut, digest: cut.cut_digest, authority_effect: "none"});
}

function journalState(journal) {
  if (!journals.has(journal)) throw new TypeError("A verified in-memory runtime journal is required.");
  return journal._state;
}

export function appendRuntimeEvent(journal, input) {
  const state = journalState(journal);
  const reasons = [];
  if (!isRecord(input)) reasons.push("journal.event-input-required");
  if (!text(input?.event_kind)) reasons.push("journal.event-kind-required");
  if (input?.observed_at !== undefined && input.observed_at !== null && !text(input.observed_at)) reasons.push("journal.observed-at-invalid");
  const content = eventPayload(input);
  if (!content) reasons.push("journal.event-content-invalid");
  if (reasons.length > 0) return failure("append", reasons);
  const contentDigest = digest(content);
  const idempotencyKey = eventKey(input, contentDigest);
  const existing = state.byKey.get(idempotencyKey);
  if (existing) {
    if (existing.content_digest !== contentDigest) return failure("append", ["journal.idempotency-conflict"], [{idempotency_key: idempotencyKey, existing_event_digest: existing.event_digest, proposed_content_digest: contentDigest}]);
    return freeze({ok: true, disposition: "duplicate", event: existing, authority_effect: "none"});
  }
  const sequence = state.nextSequence;
  const material = canonicalizeJson({
    schema_version: RUNTIME_JOURNAL_EVENT_SCHEMA,
    journal_id: state.journalId,
    sequence,
    event_kind: input.event_kind.trim(),
    idempotency_key: idempotencyKey,
    observed_at: input.observed_at ?? null,
    thread_id: text(input.thread_id) ? input.thread_id.trim() : null,
    turn_id: text(input.turn_id) ? input.turn_id.trim() : null,
    predecessor_digest: state.lastEventDigest,
    content,
    content_digest: contentDigest,
    authority_effect: "none",
  });
  const event = freeze({...material, event_digest: digest(material)});
  state.events.push(event);
  state.byKey.set(idempotencyKey, event);
  state.nextSequence += 1;
  state.lastEventDigest = event.event_digest;
  return freeze({ok: true, disposition: "appended", event, authority_effect: "none"});
}

function matches(event, selector) {
  if (text(selector.thread_id) && event.thread_id !== selector.thread_id) return false;
  if (text(selector.turn_id) && event.turn_id !== selector.turn_id) return false;
  if (Number.isSafeInteger(selector.up_to_sequence) && event.sequence > selector.up_to_sequence) return false;
  if (Number.isSafeInteger(selector.from_sequence) && event.sequence < selector.from_sequence) return false;
  return true;
}

export function cutRuntimeJournal(journal, selector = {}) {
  const state = journalState(journal);
  if (!isRecord(selector)) return failure("cut", ["journal.cut-selector-invalid"]);
  const events = state.events.filter((event) => matches(event, selector));
  const material = canonicalizeJson({
    schema_version: RUNTIME_JOURNAL_CUT_SCHEMA,
    cut_id: `journal-cut:${digest({journal_id: state.journalId, selector, event_digests: events.map((event) => event.event_digest)})}`,
    journal_id: state.journalId,
    selector: canonicalizeJson(selector),
    head_sequence: state.nextSequence - 1,
    head_event_digest: state.lastEventDigest,
    first_sequence: events[0]?.sequence ?? null,
    last_sequence: events.at(-1)?.sequence ?? null,
    event_set_digest: digest(events.map((event) => event.event_digest)),
    events,
    eviction_receipt_digests: state.evictions.map((receipt) => receipt.eviction_digest),
    authority_effect: "none",
  });
  const cut = freeze({...material, cut_digest: digest(material)});
  verifiedCuts.add(cut);
  return freeze({ok: true, value: cut, digest: cut.cut_digest, authority_effect: "none"});
}

export function replayRuntimeJournal(cut) {
  if (isRecord(cut) && replayCache.has(cut)) return replayCache.get(cut);
  const verified = verifyRuntimeJournalCut(cut);
  if (!verified.ok) return verified;
  const counts = {};
  const lastByKind = {};
  for (const event of cut.events) {
    counts[event.event_kind] = (counts[event.event_kind] ?? 0) + 1;
    lastByKind[event.event_kind] = event.event_digest;
  }
  const material = canonicalizeJson({
    schema_version: RUNTIME_JOURNAL_REPLAY_SCHEMA,
    journal_id: cut.journal_id,
    cut_digest: cut.cut_digest,
    event_count: cut.events.length,
    event_digests: cut.events.map((event) => event.event_digest),
    counts_by_kind: counts,
    last_event_digest_by_kind: lastByKind,
    completion_observed: (counts["turn-completed-observed"] ?? 0) > 0,
    semantic_evaluation_count: Object.entries(counts).filter(([kind]) => kind.startsWith("semantic-evaluation-")).reduce((total, [, count]) => total + count, 0),
    constraint_derivation_count: counts["reasoning-receipt-constraints-derived"] ?? 0,
    continuation_decision_count: counts["continuation-decision"] ?? 0,
    successor_started_count: counts["successor-started"] ?? 0,
    turn_closed: (counts["turn-closed"] ?? 0) > 0,
    external_calls: 0,
    authority_effect: "none",
  });
  const replay = freeze({ok: true, value: {...material, replay_digest: digest(material)}, authority_effect: "none"});
  replayCache.set(cut, replay);
  return replay;
}

function closedTurnKeys(events) {
  return new Map(events
    .filter((event) => event.event_kind === "turn-closed" && event.thread_id && event.turn_id)
    .map((event) => [`${event.thread_id}:${event.turn_id}`, event.sequence]));
}

export function evictClosedJournalSegments(journal, policy = {}) {
  const state = journalState(journal);
  if (!isRecord(policy)) return failure("eviction", ["journal.eviction-policy-invalid"]);
  const maxEvents = Number.isSafeInteger(policy.max_events) && policy.max_events >= 0 ? policy.max_events : state.profile.max_events;
  const maxClosedTurns = Number.isSafeInteger(policy.max_closed_turns) && policy.max_closed_turns >= 0 ? policy.max_closed_turns : state.profile.max_closed_turns;
  const closed = closedTurnKeys(state.events);
  const orderedClosed = [...closed.entries()].sort((left, right) => left[1] - right[1]);
  const evictedKeys = [];
  let retainedCount = state.events.length;
  let retainedClosed = orderedClosed.length;
  for (const [key] of orderedClosed) {
    if (retainedCount <= maxEvents && retainedClosed <= maxClosedTurns) break;
    evictedKeys.push(key);
    retainedCount -= state.events.filter((event) => `${event.thread_id}:${event.turn_id}` === key).length;
    retainedClosed -= 1;
  }
  const evictedSet = new Set(evictedKeys);
  const evictedEvents = state.events.filter((event) => evictedSet.has(`${event.thread_id}:${event.turn_id}`));
  const retained = state.events.filter((event) => !evictedSet.has(`${event.thread_id}:${event.turn_id}`));
  const material = canonicalizeJson({
    schema_version: RUNTIME_JOURNAL_EVICTION_SCHEMA,
    journal_id: state.journalId,
    policy: {max_events: maxEvents, max_closed_turns: maxClosedTurns},
    evicted_turn_keys: evictedKeys,
    evicted_event_digests: evictedEvents.map((event) => event.event_digest),
    retained_event_count: retained.length,
    head_sequence: state.nextSequence - 1,
    head_event_digest: state.lastEventDigest,
    authority_effect: "none",
  });
  const receipt = freeze({...material, eviction_digest: digest(material)});
  if (evictedEvents.length > 0) {
    state.events.splice(0, state.events.length, ...retained);
    for (const event of evictedEvents) state.byKey.delete(event.idempotency_key);
    state.evictions.push(receipt);
  }
  return freeze({ok: true, disposition: evictedEvents.length > 0 ? "evicted" : "unchanged", receipt, authority_effect: "none"});
}

export function createInMemoryRuntimeJournal(profile = {}) {
  if (!isRecord(profile)) throw new TypeError("Runtime journal profile must be an object.");
  const normalized = freeze({
    journal_id: text(profile.journal_id) ? profile.journal_id.trim() : "are-runtime-journal:local",
    max_events: Number.isSafeInteger(profile.max_events) && profile.max_events >= 0 ? profile.max_events : 4096,
    max_closed_turns: Number.isSafeInteger(profile.max_closed_turns) && profile.max_closed_turns >= 0 ? profile.max_closed_turns : 256,
    authority_effect: "none",
  });
  const state = {
    journalId: normalized.journal_id,
    profile: normalized,
    events: [],
    byKey: new Map(),
    nextSequence: 1,
    lastEventDigest: null,
    evictions: [],
  };
  const journal = Object.freeze({
    _state: state,
    append: (event) => appendRuntimeEvent(journal, event),
    cut: (selector) => cutRuntimeJournal(journal, selector),
    replay: (cut) => replayRuntimeJournal(cut),
    evict: (policy) => evictClosedJournalSegments(journal, policy),
    snapshot: () => freeze([...state.events]),
    inspect: () => freeze({journal_id: state.journalId, event_count: state.events.length, next_sequence: state.nextSequence, head_event_digest: state.lastEventDigest, eviction_receipt_digests: state.evictions.map((receipt) => receipt.eviction_digest), authority_effect: "none"}),
  });
  journals.add(journal);
  return journal;
}
