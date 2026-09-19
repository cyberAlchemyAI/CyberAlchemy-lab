import {appendFileSync, closeSync, existsSync, fsyncSync, mkdirSync, openSync, readFileSync, unlinkSync} from "node:fs";
import {dirname} from "node:path";

import {digestValue, freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";

export const GATEWAY_SESSION_EVENT_SCHEMA = "are.gateway-session-event/v1";
export const GATEWAY_SESSION_INDEX_SCHEMA = "are.gateway-session-index/v1";

function replay(records, expectedStoreId = null) {
  const sessions = new Map();
  let previous = null;
  let sequence = 0;
  for (const event of records) {
    if (!isRecord(event) || event.schema_version !== GATEWAY_SESSION_EVENT_SCHEMA) throw new Error("gateway.session-store-record-invalid");
    if (expectedStoreId && event.store_id !== expectedStoreId) throw new Error("gateway.session-store-id-mismatch");
    if (event.sequence !== ++sequence || event.previous_event_digest !== previous) throw new Error("gateway.session-store-chain-invalid");
    const material = {...event};
    delete material.event_digest;
    if (digestValue(material) !== event.event_digest) throw new Error("gateway.session-store-digest-invalid");
    previous = event.event_digest;
    const prior = sessions.get(event.consumer_id) ?? {consumer_id: event.consumer_id, lane: null, resume_token_digest: null, status: "missing", acknowledged_through: 0, delivery_sequence: 0, deliveries: new Map(), requests: new Map(), server_requests: new Map(), expiration: null};
    if (event.event_kind === "session-started") Object.assign(prior, {lane: event.content.lane, resume_token_digest: event.content.resume_token_digest, status: "active", expiration: null});
    else if (event.event_kind === "delivery-enqueued") {
      const delivery = event.content.delivery;
      if (!isRecord(delivery) || !Number.isSafeInteger(delivery.sequence) || delivery.sequence !== prior.delivery_sequence + 1) throw new Error("gateway.session-store-delivery-sequence-invalid");
      prior.delivery_sequence = delivery.sequence;
      if (delivery.sequence > prior.acknowledged_through) prior.deliveries.set(delivery.sequence, delivery);
    }
    else if (event.event_kind === "delivery-acknowledged") {
      const through = event.content.through_sequence;
      if (!Number.isSafeInteger(through) || through < prior.acknowledged_through || through > prior.delivery_sequence) throw new Error("gateway.session-store-ack-sequence-invalid");
      prior.acknowledged_through = through;
      for (const deliverySequence of [...prior.deliveries.keys()]) if (deliverySequence <= through) prior.deliveries.delete(deliverySequence);
    }
    else if (event.event_kind === "dispatch-intent") prior.requests.set(event.content.request_key, {...event.content, status: "outcome-unknown"});
    else if (event.event_kind === "dispatch-outcome") prior.requests.set(event.content.request_key, {...prior.requests.get(event.content.request_key), ...event.content, status: "complete"});
    else if (event.event_kind === "server-request-observed") prior.server_requests.set(String(event.content.request_id), {...event.content, status: "pending"});
    else if (event.event_kind === "server-response-intent") prior.server_requests.set(String(event.content.request_id), {...prior.server_requests.get(String(event.content.request_id)), ...event.content, status: "outcome-unknown"});
    else if (event.event_kind === "server-response-forwarded") prior.server_requests.set(String(event.content.request_id), {...prior.server_requests.get(String(event.content.request_id)), ...event.content, status: "forwarded"});
    else if (event.event_kind === "session-expired") Object.assign(prior, {status: "expired", expiration: event.content.expiration});
    else if (event.event_kind === "session-closed") prior.status = "closed";
    sessions.set(event.consumer_id, prior);
  }
  return {sessions, sequence, head: previous};
}

function publicSession(value) {
  if (!value) return null;
  return freezeResult({...value, deliveries: [...value.deliveries.values()].sort((a, b) => a.sequence - b.sequence), requests: [...value.requests.values()].sort((a, b) => a.request_key.localeCompare(b.request_key)), server_requests: [...value.server_requests.values()].sort((a, b) => String(a.request_id).localeCompare(String(b.request_id))), authority_effect: "none"});
}

function createStore({storeId, initialRecords = [], appendRecord = () => {}, closeStore = () => {}, durability = "process-memory"}) {
  if (!nonEmptyString(storeId)) throw new TypeError("A gateway session-store id is required.");
  const state = replay(initialRecords, storeId);
  function append({event_kind, consumer_id, content = {}}) {
    if (!nonEmptyString(event_kind) || !nonEmptyString(consumer_id) || !isRecord(content)) return freezeResult({ok: false, reason_codes: ["gateway.session-store-event-invalid"], authority_effect: "none"});
    const material = freezeResult({schema_version: GATEWAY_SESSION_EVENT_SCHEMA, store_id: storeId, sequence: state.sequence + 1, previous_event_digest: state.head, event_kind: event_kind.trim(), consumer_id: consumer_id.trim(), content, authority_effect: "none"});
    const event = freezeResult({...material, event_digest: digestValue(material)});
    try { appendRecord(event); } catch (error) {
      return freezeResult({ok: false, reason_codes: [`gateway.session-store-append-failed:${error?.code ?? error?.name ?? "Error"}`], authority_effect: "none"});
    }
    const next = replay([...initialRecords, event], storeId);
    initialRecords.push(event);
    state.sessions = next.sessions;
    state.sequence = next.sequence;
    state.head = next.head;
    return freezeResult({ok: true, event, authority_effect: "none"});
  }
  return Object.freeze({
    append,
    getSession: (consumerId) => publicSession(state.sessions.get(consumerId)),
    inspect: () => freezeResult({schema_version: GATEWAY_SESSION_INDEX_SCHEMA, store_id: storeId, durability, event_count: state.sequence, head_event_digest: state.head, sessions: [...state.sessions.values()].map(publicSession).sort((a, b) => a.consumer_id.localeCompare(b.consumer_id)), authority_effect: "none"}),
    close: closeStore,
  });
}

export function createMemoryGatewaySessionStore({store_id = "are-gateway-sessions:memory"} = {}) {
  return createStore({storeId: store_id});
}

export function createFileGatewaySessionStore({path, store_id = "are-gateway-sessions:file"} = {}) {
  if (!nonEmptyString(path)) throw new TypeError("A gateway session-store path is required.");
  mkdirSync(dirname(path), {recursive: true});
  const lockPath = `${path}.writer.lock`;
  let lock;
  try { lock = openSync(lockPath, "wx", 0o600); } catch { throw new Error("gateway.session-store-writer-lock-held"); }
  let records = [];
  try {
    if (existsSync(path)) {
      const source = readFileSync(path, "utf8");
      if (source.length > 0 && !source.endsWith("\n")) throw new Error("gateway.session-store-torn-tail");
      records = source.split("\n").filter(Boolean).map((line) => JSON.parse(line));
    }
    replay(records, store_id);
  } catch (error) {
    closeSync(lock);
    unlinkSync(lockPath);
    throw error;
  }
  let closed = false;
  return createStore({
    storeId: store_id,
    initialRecords: records,
    durability: "append-only-file-fsync",
    appendRecord(event) {
      if (closed) throw new Error("gateway.session-store-closed");
      appendFileSync(path, `${JSON.stringify(event)}\n`, {encoding: "utf8", mode: 0o600});
      const fd = openSync(path, "r");
      try { fsyncSync(fd); } finally { closeSync(fd); }
    },
    closeStore() {
      if (closed) return freezeResult({ok: true, already_closed: true, authority_effect: "none"});
      closed = true;
      closeSync(lock);
      unlinkSync(lockPath);
      return freezeResult({ok: true, authority_effect: "none"});
    },
  });
}
