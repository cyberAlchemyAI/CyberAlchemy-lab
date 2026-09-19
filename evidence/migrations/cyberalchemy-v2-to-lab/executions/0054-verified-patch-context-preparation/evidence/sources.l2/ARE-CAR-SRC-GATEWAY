import {randomBytes, randomUUID, timingSafeEqual} from "node:crypto";
import {chmodSync, existsSync, lstatSync, statSync, unlinkSync} from "node:fs";
import {createServer} from "node:net";

import {spawnCodexBackend} from "./backend.mjs";
import {digestValue, freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";
import {createFileGatewaySessionStore, createMemoryGatewaySessionStore} from "./gateway-session-store.mjs";
import {jsonLine, jsonRpcError, parseJsonLine} from "./protocol.mjs";

export const GATEWAY_CONNECT_SCHEMA = "are.codex-gateway-connect/v1";
export const GATEWAY_CONNECTED_SCHEMA = "are.codex-gateway-connected/v1";
export const GATEWAY_DELIVERY_SCHEMA = "are.codex-gateway-delivery/v1";
export const GATEWAY_ACK_SCHEMA = "are.codex-gateway-ack/v1";
export const GATEWAY_REQUEST_META_KEY = "_are_gateway";
export const ACKNOWLEDGED_CONTINUITY_MODE = "acknowledged-v1";
export const GATEWAY_SESSION_EXPIRATION_SCHEMA = "are.codex-session-expiration/v1";
const LANES = new Set(["plan-bound", "interaction-bound"]);

function send(stream, value) {
  if (stream && !stream.destroyed) stream.write(jsonLine(value));
}

function validateHandshake(value) {
  if (!isRecord(value) || value.schema_version !== GATEWAY_CONNECT_SCHEMA || !nonEmptyString(value.consumer_id) || !LANES.has(value.lane)) {
    return {ok: false, reason: "gateway.handshake-invalid"};
  }
  if (value.consumer_id.length > 256) return {ok: false, reason: "gateway.consumer-id-too-long"};
  let continuity = null;
  if (value.continuity !== undefined) {
    if (!isRecord(value.continuity) || value.continuity.mode !== ACKNOWLEDGED_CONTINUITY_MODE) {
      return {ok: false, reason: "gateway.continuity-mode-invalid"};
    }
    if (value.continuity.resume_token !== undefined && (!nonEmptyString(value.continuity.resume_token) || value.continuity.resume_token.length > 256)) {
      return {ok: false, reason: "gateway.resume-token-invalid"};
    }
    const lastAcked = value.continuity.last_acked_sequence ?? 0;
    if (!Number.isSafeInteger(lastAcked) || lastAcked < 0) return {ok: false, reason: "gateway.ack-sequence-invalid"};
    const aliases = value.continuity.request_aliases ?? [];
    if (!Array.isArray(aliases) || aliases.length > 256 || aliases.some((alias) => !isRecord(alias) || !nonEmptyString(alias.request_key) || alias.request_key.length > 256 || !Object.hasOwn(alias, "client_id"))) {
      return {ok: false, reason: "gateway.request-aliases-invalid"};
    }
    continuity = {mode: value.continuity.mode, resume_token: value.continuity.resume_token ?? null, last_acked_sequence: lastAcked, request_aliases: aliases};
  }
  return {ok: true, value: {consumer_id: value.consumer_id, lane: value.lane, continuity}};
}

function sameSecret(left, right) {
  if (!nonEmptyString(left) || !nonEmptyString(right)) return false;
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

function requestMetadata(message) {
  const metadata = message?.[GATEWAY_REQUEST_META_KEY];
  if (metadata === undefined) return {ok: true, request_key: null, message};
  if (!isRecord(metadata) || !nonEmptyString(metadata.request_key) || metadata.request_key.length > 256) {
    return {ok: false, reason: "gateway.request-key-invalid"};
  }
  const clean = {...message};
  delete clean[GATEWAY_REQUEST_META_KEY];
  return {ok: true, request_key: metadata.request_key, message: clean};
}

function removeSocketPath(path) {
  if (!existsSync(path)) return;
  const stat = lstatSync(path);
  if (!stat.isSocket()) throw new Error(`Gateway listen path exists and is not a socket: ${path}`);
  unlinkSync(path);
}

function createLineReader(stream, onLine, onOverflow, initial = "") {
  let buffer = initial;
  const onData = (chunk) => {
    buffer += chunk.toString("utf8");
    if (buffer.length > 1024 * 1024) {
      onOverflow();
      return;
    }
    let index;
    while ((index = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, index);
      buffer = buffer.slice(index + 1);
      if (line.trim()) onLine(line);
    }
  };
  stream.on("data", onData);
  return () => stream.off("data", onData);
}

function createSession({metadata, wrapper, backend, spawnImpl, WebSocketImpl, maxBufferedMessages, reconnectEnabled, continuityMode, detachTimeoutMs, idleTimeoutMs, maxRetainedBytes, maxReasoningLogBytes, evictionRetryMs, onBackendStderr, onClosed, onExpired, onDurableEvent = () => ({ok: true}), initialStableRequests = [], initialDeliveries = [], initialAcknowledgedThrough = 0, initialDeliverySequence = 0, initialServerRequests = []}) {
  const child = spawnCodexBackend(backend, spawnImpl, WebSocketImpl);
  let client = null;
  let detachReader = null;
  let clientChain = Promise.resolve();
  let serverChain = Promise.resolve();
  let closed = false;
  let closeReason = null;
  const buffered = [];
  const resumeToken = continuityMode === ACKNOWLEDGED_CONTINUITY_MODE ? randomBytes(32).toString("base64url") : null;
  const resumeTokenDigest = resumeToken ? digestValue(resumeToken) : null;
  const deliveries = new Map();
  const deliveredThisAttachment = new Set();
  let deliverySequence = initialDeliverySequence;
  let acknowledgedThrough = initialAcknowledgedThrough;
  const stableRequests = new Map();
  const upstreamRequests = new Map();
  const attachmentRequestKeys = new Set();
  const serverRequests = new Map();
  let upstreamRequestSequence = 0;
  let deduplicatedRequestCount = 0;
  let deduplicatedServerResponseCount = 0;
  let reconnectCount = 0;
  let initialization = freezeResult({status: "not-started", binding_digest: null, request_id: null, result: null, result_digest: null});
  let initializationForwardCount = 0;
  let initializationReplayCount = 0;
  const pendingInitializationAliases = new Map();
  let lastActivityAt = Date.now();
  let detachedAt = null;
  let lifecycleTimer = null;
  let evictionInProgress = false;
  let evictionAttemptCount = 0;
  let lastEvictionBlock = null;
  let expirationReceipt = null;
  for (const recovered of initialStableRequests) {
    if (!nonEmptyString(recovered?.request_key) || !nonEmptyString(recovered?.binding_digest)) continue;
    stableRequests.set(recovered.request_key, {
      request_key: recovered.request_key,
      method: recovered.method,
      binding_digest: recovered.binding_digest,
      wrapper_id: null,
      client_id: null,
      upstream_id: null,
      status: recovered.status === "complete" ? "complete" : "outcome-unknown",
      response: recovered.response ?? null,
      response_digest: recovered.response_digest ?? null,
      recovered: true,
    });
  }
  for (const recovered of initialDeliveries) {
    if (!isRecord(recovered) || !Number.isSafeInteger(recovered.sequence) || recovered.sequence <= acknowledgedThrough || recovered.sequence > deliverySequence) continue;
    deliveries.set(recovered.sequence, structuredClone(recovered));
  }
  for (const recovered of initialServerRequests) {
    if (!isRecord(recovered) || !Object.hasOwn(recovered, "request_id") || !nonEmptyString(recovered.method)) continue;
    serverRequests.set(String(recovered.request_id), {
      method: recovered.method,
      request_digest: recovered.request_digest,
      status: recovered.status === "forwarded" ? "forwarded" : "outcome-unknown",
      response_digest: recovered.response_digest ?? null,
      recovered: true,
    });
  }

  function touch() {
    lastActivityAt = Date.now();
    if (!client) scheduleLifecycleCheck();
  }

  function reasoningLogBytes() {
    const path = wrapper.inspectState?.()?.reasoning_state?.sink?.path;
    if (!nonEmptyString(path)) return 0;
    try { return statSync(path).size; } catch { return 0; }
  }

  function retainedProtocolBytes() {
    let bytes = buffered.reduce((sum, value) => sum + Buffer.byteLength(value), 0);
    for (const delivery of deliveries.values()) bytes += Buffer.byteLength(jsonLine(delivery));
    for (const entry of stableRequests.values()) {
      bytes += Buffer.byteLength(entry.request_key) + Buffer.byteLength(entry.binding_digest);
      if (entry.response) bytes += Buffer.byteLength(JSON.stringify(entry.response));
    }
    return bytes;
  }

  function lifecycleReason(now = Date.now()) {
    if ((continuityMode === ACKNOWLEDGED_CONTINUITY_MODE ? deliveries.size : buffered.length) > maxBufferedMessages) return "buffered-message-limit";
    if (retainedProtocolBytes() > maxRetainedBytes) return "retained-byte-limit";
    if (reasoningLogBytes() > maxReasoningLogBytes) return "reasoning-log-byte-limit";
    if (client) return null;
    if (detachTimeoutMs > 0 && detachedAt !== null && now - detachedAt >= detachTimeoutMs) return "detach-timeout";
    if (idleTimeoutMs > 0 && now - lastActivityAt >= idleTimeoutMs) return "idle-timeout";
    return null;
  }

  function lifecycleDelay(now = Date.now()) {
    const candidates = [];
    if (detachTimeoutMs > 0 && detachedAt !== null) candidates.push(Math.max(1, detachTimeoutMs - (now - detachedAt)));
    if (idleTimeoutMs > 0) candidates.push(Math.max(1, idleTimeoutMs - (now - lastActivityAt)));
    return candidates.length > 0 ? Math.min(...candidates) : evictionRetryMs;
  }

  function scheduleLifecycleCheck(delay = lifecycleDelay()) {
    if (closed || client) return;
    clearTimeout(lifecycleTimer);
    lifecycleTimer = setTimeout(runLifecycleCheck, delay);
    lifecycleTimer.unref?.();
  }

  function safeToEvict() {
    if ([...stableRequests.values()].some((entry) => entry.status !== "complete")) return {ok: false, reason_codes: ["session.pending-stable-request"]};
    if ([...serverRequests.values()].some((entry) => entry.status === "pending")) return {ok: false, reason_codes: ["session.pending-server-request"]};
    if (initialization.status === "pending") return {ok: false, reason_codes: ["session.pending-initialization"]};
    if (typeof wrapper.prepareForEviction !== "function") return {ok: false, reason_codes: ["session.eviction-checkpoint-unsupported"]};
    return wrapper.prepareForEviction({reason: lifecycleReason() ?? "session-lifecycle-expiry", consumer_id: metadata.consumer_id, lane: metadata.lane});
  }

  function runLifecycleCheck() {
    lifecycleTimer = null;
    if (closed || client || evictionInProgress) return;
    const reason = lifecycleReason();
    if (!reason) {
      scheduleLifecycleCheck();
      return;
    }
    evictionInProgress = true;
    evictionAttemptCount += 1;
    const prepared = safeToEvict();
    evictionInProgress = false;
    if (!prepared?.ok) {
      lastEvictionBlock = freezeResult({reason_codes: prepared?.reason_codes ?? ["session.eviction-preparation-failed"], observed_at: new Date().toISOString()});
      scheduleLifecycleCheck(evictionRetryMs);
      return;
    }
    const expiredAt = new Date().toISOString();
    expirationReceipt = freezeResult({
      schema_version: GATEWAY_SESSION_EXPIRATION_SCHEMA,
      consumer_id: metadata.consumer_id,
      lane: metadata.lane,
      reason: `gateway.session-${reason}`,
      resume_token_digest: resumeTokenDigest,
      retained_protocol_bytes: retainedProtocolBytes(),
      reasoning_log_bytes: reasoningLogBytes(),
      checkpoint_digest: prepared.checkpoint_digest,
      reasoning_epoch_digest: prepared.epoch_digest,
      preparation_digest: prepared.preparation_digest,
      expired_at: expiredAt,
      authority_effect: "none",
    });
    onExpired(metadata.consumer_id, api, expirationReceipt);
    stop(expirationReceipt.reason);
  }

  function initializationBinding(message) {
    return digestValue({method: "initialize", params: Object.hasOwn(message, "params") ? message.params : null});
  }

  function initializationError(id, reason, actualBindingDigest) {
    return jsonRpcError(id, -32092, "Gateway initialization binding failed", {
      reason_codes: [reason],
      expected_binding_digest: initialization.binding_digest,
      actual_binding_digest: actualBindingDigest,
      authority_effect: "none",
    });
  }

  function interceptInitialization(message) {
    if (message.method !== "initialize" || !Object.hasOwn(message, "id")) return false;
    const bindingDigest = initializationBinding(message);
    if (initialization.status === "complete") {
      if (bindingDigest !== initialization.binding_digest) {
        emitClient(initializationError(message.id, "gateway.initialize-binding-mismatch", bindingDigest));
      } else {
        initializationReplayCount += 1;
        emitClient({jsonrpc: "2.0", id: message.id, result: initialization.result});
      }
      return true;
    }
    if (initialization.status === "pending") {
      if (bindingDigest !== initialization.binding_digest) {
        emitClient(initializationError(message.id, "gateway.initialize-binding-mismatch", bindingDigest));
      } else if (String(message.id) !== String(initialization.request_id)) {
        pendingInitializationAliases.set(String(message.id), message.id);
      }
      return true;
    }
    initialization = freezeResult({status: "pending", binding_digest: bindingDigest, request_id: message.id, result: null, result_digest: null});
    return false;
  }

  function observeInitializationResponse(message) {
    if (initialization.status !== "pending" || !Object.hasOwn(message, "id") || String(message.id) !== String(initialization.request_id)) return;
    if (Object.hasOwn(message, "result") && !Object.hasOwn(message, "error")) {
      initialization = freezeResult({status: "complete", binding_digest: initialization.binding_digest, request_id: initialization.request_id, result: message.result, result_digest: digestValue(message.result)});
      for (const id of pendingInitializationAliases.values()) {
        initializationReplayCount += 1;
        emitClient({jsonrpc: "2.0", id, result: initialization.result});
      }
      pendingInitializationAliases.clear();
      return;
    }
    for (const id of pendingInitializationAliases.values()) emitClient({...message, id});
    pendingInitializationAliases.clear();
    initialization = freezeResult({status: "not-started", binding_digest: null, request_id: null, result: null, result_digest: null});
  }

  function initializationReceipt() {
    return freezeResult({
      status: initialization.status,
      binding_digest: initialization.binding_digest,
      ...(initialization.status === "complete" ? {result: initialization.result, result_digest: initialization.result_digest} : {}),
      authority_effect: "none",
    });
  }

  function encodeDelivery(value, requestKey = null) {
    const sequence = deliverySequence + 1;
    const delivery = {schema_version: GATEWAY_DELIVERY_SCHEMA, sequence, message: value, ...(requestKey ? {request_key: requestKey} : {}), authority_effect: "none"};
    const persisted = onDurableEvent("delivery-enqueued", {delivery});
    if (persisted?.ok === false) return {ok: false, reason: "gateway.delivery-not-durable"};
    deliverySequence = sequence;
    deliveries.set(sequence, delivery);
    return {ok: true, encoded: jsonLine(delivery)};
  }

  function emitClient(value, requestKey = null) {
    touch();
    if (continuityMode === ACKNOWLEDGED_CONTINUITY_MODE) {
      const encoded = encodeDelivery(value, requestKey);
      if (!encoded.ok) {
        send(client, jsonRpcError(value?.id ?? null, -32096, "Gateway delivery persistence failed", {reason_codes: [encoded.reason], authority_effect: "none"}));
        stop(encoded.reason);
        return;
      }
      if (client && !client.destroyed) {
        client.write(encoded.encoded);
        deliveredThisAttachment.add(deliverySequence);
      }
      if (deliveries.size > maxBufferedMessages || retainedProtocolBytes() > maxRetainedBytes) {
        if (client && !client.destroyed) client.end();
        else scheduleLifecycleCheck(1);
      }
      return;
    }
    const encoded = jsonLine(value);
    if (client && !client.destroyed) {
      client.write(encoded);
      return;
    }
    buffered.push(encoded);
    if (buffered.length > maxBufferedMessages || retainedProtocolBytes() > maxRetainedBytes) scheduleLifecycleCheck(1);
  }

  function acknowledge(message) {
    if (continuityMode !== ACKNOWLEDGED_CONTINUITY_MODE || !isRecord(message) || message.schema_version !== GATEWAY_ACK_SCHEMA) return false;
    const through = message.through_sequence;
    if (!Number.isSafeInteger(through) || through < acknowledgedThrough || through > deliverySequence) {
      stop("gateway.ack-sequence-invalid");
      return true;
    }
    const persisted = onDurableEvent("delivery-acknowledged", {through_sequence: through});
    if (persisted?.ok === false) {
      send(client, jsonRpcError(null, -32097, "Gateway acknowledgement persistence failed", {reason_codes: ["gateway.acknowledgement-not-durable"], authority_effect: "none"}));
      stop("gateway.acknowledgement-not-durable");
      return true;
    }
    acknowledgedThrough = through;
    for (const sequence of [...deliveries.keys()]) if (sequence <= through) deliveries.delete(sequence);
    touch();
    return true;
  }

  function stableRequestError(id, reason, requestKey, expectedDigest = null, actualDigest = null) {
    return jsonRpcError(id, -32093, "Gateway stable request binding failed", {
      reason_codes: [reason], request_key: requestKey, expected_binding_digest: expectedDigest, actual_binding_digest: actualDigest, authority_effect: "none",
    });
  }

  function rebindStableRequest(requestKey, clientId) {
    const entry = stableRequests.get(requestKey);
    if (!entry) return {ok: false, reason: "gateway.request-alias-not-found"};
    entry.client_id = clientId;
    for (const delivery of deliveries.values()) {
      if (delivery.request_key !== requestKey || !Object.hasOwn(delivery.message, "id")) continue;
      delivery.message = {...delivery.message, id: clientId};
    }
    return {ok: true};
  }

  function interceptStableRequest(message, requestKey) {
    if (!requestKey || !message.method || !Object.hasOwn(message, "id")) return {intercepted: false};
    const bindingDigest = digestValue({method: message.method, params: Object.hasOwn(message, "params") ? message.params : null});
    const existing = stableRequests.get(requestKey);
    if (existing) {
      if (existing.binding_digest !== bindingDigest) {
        emitClient(stableRequestError(message.id, "gateway.request-binding-mismatch", requestKey, existing.binding_digest, bindingDigest));
      } else if (existing.status === "outcome-unknown") {
        emitClient(stableRequestError(message.id, "gateway.dispatch-outcome-unknown", requestKey, existing.binding_digest, bindingDigest));
      } else {
        deduplicatedRequestCount += 1;
        attachmentRequestKeys.add(requestKey);
        rebindStableRequest(requestKey, message.id);
        if (existing.status === "complete" && ![...deliveries.values()].some((delivery) => delivery.request_key === requestKey)) {
          emitClient({...existing.response, id: message.id}, requestKey);
        }
        flushBuffered();
      }
      return {intercepted: true};
    }
    const upstreamId = `are-gateway:${metadata.consumer_id}:${++upstreamRequestSequence}`;
    const entry = {request_key: requestKey, method: message.method, binding_digest: bindingDigest, wrapper_id: message.id, client_id: message.id, upstream_id: upstreamId, status: "preparing", response: null, response_digest: null};
    stableRequests.set(requestKey, entry);
    upstreamRequests.set(String(upstreamId), entry);
    const persisted = onDurableEvent("dispatch-intent", {request_key: requestKey, method: message.method, binding_digest: bindingDigest});
    if (persisted?.ok === false) {
      stableRequests.delete(requestKey);
      upstreamRequests.delete(String(upstreamId));
      emitClient(stableRequestError(message.id, "gateway.dispatch-intent-not-durable", requestKey));
      return {intercepted: true};
    }
    return {intercepted: false, entry};
  }

  function processClientLine(line) {
    clientChain = clientChain.then(async () => {
      touch();
      let control;
      try { control = JSON.parse(line); } catch { control = null; }
      if (control?.schema_version === GATEWAY_ACK_SCHEMA) {
        acknowledge(control);
        return;
      }
      const parsed = parseJsonLine(line);
      if (!parsed.ok) {
        emitClient(jsonRpcError(null, -32700, "Parse error", parsed));
        return;
      }
      const resourceReason = lifecycleReason();
      if (resourceReason === "retained-byte-limit" || resourceReason === "reasoning-log-byte-limit") {
        emitClient(jsonRpcError(parsed.value?.id ?? null, -32095, "Gateway session resource limit reached", {
          reason_codes: [`gateway.session-${resourceReason}`],
          retained_protocol_bytes: retainedProtocolBytes(),
          reasoning_log_bytes: reasoningLogBytes(),
          authority_effect: "none",
        }));
        if (client && !client.destroyed) client.end();
        return;
      }
      const metadataResult = requestMetadata(parsed.value);
      if (!metadataResult.ok) {
        emitClient(stableRequestError(parsed.value?.id ?? null, metadataResult.reason, null));
        return;
      }
      const message = metadataResult.message;
      const serverRequest = !message.method && Object.hasOwn(message, "id") ? serverRequests.get(String(message.id)) : null;
      if (serverRequest?.status === "outcome-unknown") {
        emitClient(jsonRpcError(message.id, -32098, "Gateway server-request outcome is unknown after recovery", {
          reason_codes: ["gateway.server-response-outcome-unknown"],
          request_digest: serverRequest.request_digest,
          authority_effect: "none",
        }));
        return;
      }
      if (serverRequest?.status === "forwarded") {
        const responseDigest = digestValue(message);
        if (responseDigest !== serverRequest.response_digest) {
          emitClient(jsonRpcError(message.id, -32094, "Gateway server-request response binding failed", {
            reason_codes: ["gateway.server-response-binding-mismatch"],
            expected_response_digest: serverRequest.response_digest,
            actual_response_digest: responseDigest,
            authority_effect: "none",
          }));
        } else deduplicatedServerResponseCount += 1;
        return;
      }
      if (interceptInitialization(message)) return;
      const stable = interceptStableRequest(message, metadataResult.request_key);
      if (stable.intercepted) return;
      let actions;
      try {
        actions = await wrapper.processClientMessage(message);
      } catch (error) {
        if (stable.entry) {
          stableRequests.delete(stable.entry.request_key);
          upstreamRequests.delete(String(stable.entry.upstream_id));
        }
        throw error;
      }
      const forwardedInitialization = actions.to_server.some((candidate) => candidate.method === "initialize" && String(candidate.id) === String(message.id));
      if (forwardedInitialization) initializationForwardCount += 1;
      else if (message.method === "initialize" && initialization.status === "pending" && String(initialization.request_id) === String(message.id)) {
        initialization = freezeResult({status: "not-started", binding_digest: null, request_id: null, result: null, result_digest: null});
      }
      let forwardedStable = false;
      for (const candidate of actions.to_server) {
        const forwardsServerResponse = serverRequest && Object.hasOwn(candidate, "id") && String(candidate.id) === String(message.id);
        if (forwardsServerResponse) {
          const responseDigest = digestValue(message);
          const intent = onDurableEvent("server-response-intent", {request_id: message.id, response_digest: responseDigest});
          if (intent?.ok === false) {
            emitClient(jsonRpcError(message.id, -32099, "Gateway server response is not durable", {reason_codes: ["gateway.server-response-intent-not-durable"], authority_effect: "none"}));
            return;
          }
        }
        if (stable.entry && candidate.method === message.method && String(candidate.id) === String(message.id)) {
          stable.entry.status = "pending";
          forwardedStable = true;
          send(child.stdin, {...candidate, id: stable.entry.upstream_id});
        } else send(child.stdin, candidate);
        if (forwardsServerResponse) {
          serverRequest.status = "forwarded";
          serverRequest.response_digest = digestValue(message);
          const outcome = onDurableEvent("server-response-forwarded", {request_id: message.id, response_digest: serverRequest.response_digest});
          if (outcome?.ok === false) {
            stop("gateway.server-response-outcome-not-durable");
            return;
          }
        }
      }
      for (const candidate of actions.to_client) {
        if (stable.entry && Object.hasOwn(candidate, "id") && String(candidate.id) === String(message.id)) {
          stable.entry.status = "complete";
          stable.entry.response = candidate;
          stable.entry.response_digest = digestValue(candidate);
          onDurableEvent("dispatch-outcome", {request_key: stable.entry.request_key, response: candidate, response_digest: stable.entry.response_digest});
          upstreamRequests.delete(String(stable.entry.upstream_id));
          emitClient(candidate, stable.entry.request_key);
        } else emitClient(candidate);
      }
      if (stable.entry && !forwardedStable && stable.entry.status === "preparing") {
        stableRequests.delete(stable.entry.request_key);
        upstreamRequests.delete(String(stable.entry.upstream_id));
      }
    }).catch((error) => emitClient(jsonRpcError(null, -32603, "Gateway client-path failure", {message: error.message})));
  }

  const detachServerReader = createLineReader(child.stdout, (line) => {
    serverChain = serverChain.then(async () => {
      touch();
      const parsed = parseJsonLine(line);
      if (!parsed.ok) {
        emitClient(jsonRpcError(null, -32700, "App-server parse error", parsed));
        return;
      }
      const stable = Object.hasOwn(parsed.value, "id") ? upstreamRequests.get(String(parsed.value.id)) : null;
      const wrapperMessage = stable ? {...parsed.value, id: stable.wrapper_id} : parsed.value;
      const actions = await wrapper.processServerMessage(wrapperMessage);
      observeInitializationResponse(wrapperMessage);
      for (const message of actions.to_server) send(child.stdin, message);
      for (const message of actions.to_client) {
        if (message.method && Object.hasOwn(message, "id")) {
          const requestRecord = {request_id: message.id, method: message.method, request_digest: digestValue(message)};
          const persisted = onDurableEvent("server-request-observed", requestRecord);
          if (persisted?.ok === false) {
            send(client, jsonRpcError(message.id, -32100, "Gateway server request is not durable", {reason_codes: ["gateway.server-request-not-durable"], authority_effect: "none"}));
            stop("gateway.server-request-not-durable");
            return;
          }
          serverRequests.set(String(message.id), {...requestRecord, status: "pending", response_digest: null});
        }
        if (stable && Object.hasOwn(message, "id") && String(message.id) === String(stable.wrapper_id)) {
          const response = {...message, id: stable.client_id};
          stable.status = "complete";
          stable.response = {...message};
          stable.response_digest = digestValue(stable.response);
          onDurableEvent("dispatch-outcome", {request_key: stable.request_key, response: stable.response, response_digest: stable.response_digest});
          upstreamRequests.delete(String(stable.upstream_id));
          emitClient(response, stable.request_key);
        } else emitClient(message);
      }
    }).catch((error) => emitClient(jsonRpcError(null, -32603, "Gateway server-path failure", {message: error.message})));
  }, () => stop("gateway.upstream-line-too-large"));

  child.stderr.on("data", (chunk) => onBackendStderr(chunk, metadata));
  child.on("exit", (code, signal) => {
    if (closed) return;
    emitClient(jsonRpcError(null, -32090, "Codex app-server backend exited", {code, signal, authority_effect: "none"}));
    stop("gateway.upstream-exited", false, false);
  });
  child.on("error", (error) => {
    if (closed) return;
    emitClient(jsonRpcError(null, -32091, "Codex app-server backend failed", {message: error.message, authority_effect: "none"}));
    stop("gateway.upstream-failed", false, false);
  });

  function attach(socket, continuity = null) {
    if (closed) return {ok: false, reason: closeReason ?? "gateway.session-closed"};
    if (client && !client.destroyed) return {ok: false, reason: "gateway.consumer-already-attached"};
    attachmentRequestKeys.clear();
    deliveredThisAttachment.clear();
    if (continuityMode === ACKNOWLEDGED_CONTINUITY_MODE) {
      if (!continuity || continuity.mode !== ACKNOWLEDGED_CONTINUITY_MODE) return {ok: false, reason: "gateway.resume-authentication-required"};
      if (reconnectCount > 0 && !sameSecret(continuity.resume_token, resumeToken)) return {ok: false, reason: "gateway.resume-authentication-failed"};
      if (continuity.last_acked_sequence > deliverySequence) return {ok: false, reason: "gateway.ack-sequence-invalid"};
      if (continuity.last_acked_sequence > acknowledgedThrough) {
        const persisted = onDurableEvent("delivery-acknowledged", {through_sequence: continuity.last_acked_sequence});
        if (persisted?.ok === false) return {ok: false, reason: "gateway.acknowledgement-not-durable"};
      }
      acknowledgedThrough = Math.max(acknowledgedThrough, continuity.last_acked_sequence);
      for (const sequence of [...deliveries.keys()]) if (sequence <= acknowledgedThrough) deliveries.delete(sequence);
      for (const alias of continuity.request_aliases) {
        if (!stableRequests.has(alias.request_key)) return {ok: false, reason: "gateway.request-alias-not-found"};
      }
      for (const alias of continuity.request_aliases) {
        const rebound = rebindStableRequest(alias.request_key, alias.client_id);
        if (!rebound.ok) return rebound;
        attachmentRequestKeys.add(alias.request_key);
      }
    }
    client = socket;
    clearTimeout(lifecycleTimer);
    lifecycleTimer = null;
    detachedAt = null;
    touch();
    reconnectCount += 1;
    detachReader = createLineReader(socket, processClientLine, () => stop("gateway.client-line-too-large"));
    const detach = () => {
      if (client !== socket) return;
      detachReader?.();
      detachReader = null;
      client = null;
      detachedAt = Date.now();
      if (!reconnectEnabled) stop("gateway.client-disconnected");
      else scheduleLifecycleCheck(lifecycleReason() ? 1 : lifecycleDelay());
    };
    socket.once("close", detach);
    socket.once("error", detach);
    return {ok: true};
  }

  function flushBuffered() {
    if (!client || client.destroyed) return;
    if (continuityMode === ACKNOWLEDGED_CONTINUITY_MODE) {
      for (const delivery of [...deliveries.values()].sort((a, b) => a.sequence - b.sequence)) {
        if (delivery.request_key && !attachmentRequestKeys.has(delivery.request_key)) break;
        if (deliveredThisAttachment.has(delivery.sequence)) continue;
        client.write(jsonLine(delivery));
        deliveredThisAttachment.add(delivery.sequence);
      }
      return;
    }
    for (const encoded of buffered.splice(0)) client.write(encoded);
  }

  function stop(reason = "gateway.closed", killChild = true, destroyClient = true) {
    if (closed) return;
    closed = true;
    closeReason = reason;
    clearTimeout(lifecycleTimer);
    lifecycleTimer = null;
    detachReader?.();
    detachServerReader();
    if (client && !client.destroyed) {
      if (destroyClient) client.destroy();
      else client.end();
    }
    client = null;
    if (killChild && typeof child.kill === "function") child.kill("SIGTERM");
    if (typeof wrapper.close === "function") wrapper.close();
    onClosed(metadata.consumer_id, api);
  }

  const api = Object.freeze({
    attach,
    flushBuffered,
    initializationReceipt,
    resumeToken: () => resumeToken,
    stop,
    metadata: freezeResult(metadata),
    child,
    inspect: () => freezeResult({
      consumer_id: metadata.consumer_id,
      lane: metadata.lane,
      attached: Boolean(client && !client.destroyed),
      buffered_messages: continuityMode === ACKNOWLEDGED_CONTINUITY_MODE ? deliveries.size : buffered.length,
      continuity_mode: continuityMode,
      resume_token_digest: resumeTokenDigest,
      delivery_sequence: deliverySequence,
      acknowledged_through: acknowledgedThrough,
      unacknowledged_deliveries: deliveries.size,
      stable_requests: [...stableRequests.values()].map((entry) => ({request_key: entry.request_key, method: entry.method, binding_digest: entry.binding_digest, status: entry.status, response_digest: entry.response_digest})).sort((a, b) => a.request_key.localeCompare(b.request_key)),
      upstream_request_count: upstreamRequestSequence,
      deduplicated_request_count: deduplicatedRequestCount,
      pending_server_requests: [...serverRequests.entries()].filter(([, entry]) => entry.status === "pending").map(([id]) => id).sort(),
      forwarded_server_responses: [...serverRequests.values()].filter((entry) => entry.status === "forwarded").length,
      deduplicated_server_response_count: deduplicatedServerResponseCount,
      reconnect_count: reconnectCount,
      initialization_status: initialization.status,
      initialization_binding_digest: initialization.binding_digest,
      initialization_forward_count: initializationForwardCount,
      initialization_replay_count: initializationReplayCount,
      pending_initialization_aliases: pendingInitializationAliases.size,
      lifecycle: {
        last_activity_at: new Date(lastActivityAt).toISOString(),
        detached_at: detachedAt === null ? null : new Date(detachedAt).toISOString(),
        detach_timeout_ms: detachTimeoutMs,
        idle_timeout_ms: idleTimeoutMs,
        retained_protocol_bytes: retainedProtocolBytes(),
        max_retained_bytes: maxRetainedBytes,
        reasoning_log_bytes: reasoningLogBytes(),
        max_reasoning_log_bytes: maxReasoningLogBytes,
        eviction_attempt_count: evictionAttemptCount,
        last_eviction_block: lastEvictionBlock,
        expiration_receipt: expirationReceipt,
      },
      closed,
      close_reason: closeReason,
      wrapper_state: typeof wrapper.inspectState === "function" ? wrapper.inspectState() : null,
      authority_effect: "none",
    }),
  });
  return api;
}

export function createPersistentGateway(options = {}) {
  if (!nonEmptyString(options.listen_path)) throw new TypeError("A Unix gateway listen_path is required.");
  if (typeof options.wrapper_factory !== "function") throw new TypeError("A wrapper_factory is required.");
  const maxClients = options.max_clients ?? 8;
  const maxBufferedMessages = options.max_buffered_messages_per_client ?? 256;
  const detachTimeoutMs = options.detach_timeout_ms ?? 300_000;
  const idleTimeoutMs = options.idle_timeout_ms ?? 1_800_000;
  const maxRetainedBytes = options.max_retained_bytes_per_session ?? 4 * 1024 * 1024;
  const maxReasoningLogBytes = options.max_reasoning_log_bytes_per_session ?? 64 * 1024 * 1024;
  const expirationTombstoneTtlMs = options.expiration_tombstone_ttl_ms ?? 3_600_000;
  const evictionRetryMs = options.eviction_retry_ms ?? 1_000;
  if (!Number.isSafeInteger(maxClients) || maxClients < 1) throw new TypeError("max_clients must be a positive safe integer.");
  if (!Number.isSafeInteger(maxBufferedMessages) || maxBufferedMessages < 1) throw new TypeError("max_buffered_messages_per_client must be a positive safe integer.");
  for (const [name, value] of [["detach_timeout_ms", detachTimeoutMs], ["idle_timeout_ms", idleTimeoutMs]]) {
    if (!Number.isSafeInteger(value) || value < 0) throw new TypeError(`${name} must be a non-negative safe integer.`);
  }
  for (const [name, value] of [["max_retained_bytes_per_session", maxRetainedBytes], ["max_reasoning_log_bytes_per_session", maxReasoningLogBytes], ["expiration_tombstone_ttl_ms", expirationTombstoneTtlMs], ["eviction_retry_ms", evictionRetryMs]]) {
    if (!Number.isSafeInteger(value) || value < 1) throw new TypeError(`${name} must be a positive safe integer.`);
  }
  const runtimeEpochId = options.runtime_epoch_id ?? `are-gateway-runtime:${randomUUID()}`;
  const reconnectEnabled = options.reconnect !== false;
  const ownsSessionStore = !options.session_store;
  const sessionStore = options.session_store ?? (nonEmptyString(options.session_store_path)
    ? createFileGatewaySessionStore({path: options.session_store_path, store_id: options.session_store_id ?? "are-codex-gateway-sessions:v1"})
    : createMemoryGatewaySessionStore({store_id: options.session_store_id ?? `are-codex-gateway-sessions:${runtimeEpochId}`}));
  const sessions = new Map();
  const expiredSessions = new Map();
  const authorizeClient = options.authorize_client ?? (() => true);
  const server = createServer();
  let started = false;

  function closeSession(consumerId, session) {
    if (sessions.get(consumerId) === session) sessions.delete(consumerId);
  }

  function recordExpiration(consumerId, session, receipt) {
    expiredSessions.set(consumerId, {session, receipt, retain_until: Date.now() + expirationTombstoneTtlMs});
    sessionStore.append({event_kind: "session-expired", consumer_id: consumerId, content: {expiration: receipt}});
  }

  function pruneExpirations() {
    const now = Date.now();
    for (const [consumerId, entry] of expiredSessions) if (entry.retain_until <= now) expiredSessions.delete(consumerId);
  }

  server.on("connection", (socket) => {
    let buffer = "";
    const onData = (chunk) => {
      buffer += chunk.toString("utf8");
      if (buffer.length > 16384) {
        send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.handshake-too-large", authority_effect: "none"});
        socket.end();
        return;
      }
      const index = buffer.indexOf("\n");
      if (index < 0) return;
      socket.off("data", onData);
      const line = buffer.slice(0, index);
      const remainder = buffer.slice(index + 1);
      let parsed;
      try { parsed = JSON.parse(line); } catch { parsed = null; }
      const handshake = validateHandshake(parsed);
      if (!handshake.ok || authorizeClient(handshake.value ?? parsed) !== true) {
        send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: handshake.ok ? "gateway.client-not-authorized" : handshake.reason, authority_effect: "none"});
        socket.end();
        return;
      }
      const metadata = handshake.value;
      pruneExpirations();
      let session = sessions.get(metadata.consumer_id);
      const durableSession = sessionStore.getSession(metadata.consumer_id);
      if (!session && durableSession?.status === "active" && durableSession.lane !== metadata.lane) {
        send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.consumer-lane-mismatch", authority_effect: "none"});
        socket.end();
        return;
      }
      if (session && session.metadata.lane !== metadata.lane) {
        send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.consumer-lane-mismatch", authority_effect: "none"});
        socket.end();
        return;
      }
      if (!session) {
        if (metadata.continuity?.resume_token) {
          const expired = expiredSessions.get(metadata.consumer_id);
          const tokenDigest = digestValue(metadata.continuity.resume_token);
          const durableExpired = durableSession?.status === "expired" && tokenDigest === durableSession.resume_token_digest;
          const authenticatedExpiration = (expired && tokenDigest === expired.receipt.resume_token_digest) || durableExpired;
          if (authenticatedExpiration) {
            send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.session-expired", expiration: expired?.receipt ?? durableSession.expiration, authority_effect: "none"});
            socket.end();
            return;
          }
          if (durableSession?.status !== "active" || tokenDigest !== durableSession.resume_token_digest) {
            send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.resume-session-missing", authority_effect: "none"});
            socket.end();
            return;
          }
        } else if (durableSession?.status === "active") {
          send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.resume-authentication-required", authority_effect: "none"});
          socket.end();
          return;
        }
        if (sessions.size >= maxClients) {
          send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.max-clients-reached", authority_effect: "none"});
          socket.end();
          return;
        }
        try {
          const wrapper = options.wrapper_factory(metadata);
          session = createSession({
            metadata,
            wrapper,
            backend: options.backend ?? {},
            spawnImpl: options.spawn_impl,
            WebSocketImpl: options.websocket_impl,
            maxBufferedMessages,
            reconnectEnabled,
            continuityMode: metadata.continuity?.mode ?? null,
            detachTimeoutMs,
            idleTimeoutMs,
            maxRetainedBytes,
            maxReasoningLogBytes,
            evictionRetryMs,
            onBackendStderr: options.on_backend_stderr ?? (() => {}),
            onClosed: closeSession,
            onExpired: recordExpiration,
            onDurableEvent: (eventKind, content) => sessionStore.append({event_kind: eventKind, consumer_id: metadata.consumer_id, content}),
            initialStableRequests: durableSession?.status === "active" ? durableSession.requests : [],
            initialDeliveries: durableSession?.status === "active" ? durableSession.deliveries : [],
            initialAcknowledgedThrough: durableSession?.status === "active" ? durableSession.acknowledged_through : 0,
            initialDeliverySequence: durableSession?.status === "active" ? durableSession.delivery_sequence : 0,
            initialServerRequests: durableSession?.status === "active" ? durableSession.server_requests : [],
          });
        } catch (error) {
          send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.session-start-failed", detail: error.message, authority_effect: "none"});
          socket.end();
          return;
        }
        sessions.set(metadata.consumer_id, session);
        const resumable = nonEmptyString(session.inspect().resume_token_digest);
        const persisted = resumable
          ? sessionStore.append({event_kind: "session-started", consumer_id: metadata.consumer_id, content: {lane: metadata.lane, resume_token_digest: session.inspect().resume_token_digest, recovered: durableSession?.status === "active"}})
          : {ok: true};
        if (!persisted.ok) {
          session.stop("gateway.session-start-not-durable");
          send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: "gateway.session-start-not-durable", authority_effect: "none"});
          socket.end();
          return;
        }
      }
      const attached = session.attach(socket, metadata.continuity);
      if (!attached.ok) {
        send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: false, reason: attached.reason, authority_effect: "none"});
        socket.end();
        return;
      }
      const state = session.inspect();
      send(socket, {schema_version: GATEWAY_CONNECTED_SCHEMA, ok: true, consumer_id: metadata.consumer_id, lane: metadata.lane, runtime_epoch_id: runtimeEpochId, resumed: durableSession?.status === "active" || state.reconnect_count > 1, initialization: session.initializationReceipt(), ...(state.continuity_mode === ACKNOWLEDGED_CONTINUITY_MODE ? {continuity: {mode: ACKNOWLEDGED_CONTINUITY_MODE, resume_token: session.resumeToken(), resume_token_digest: state.resume_token_digest, acknowledged_through: state.acknowledged_through, next_sequence: state.delivery_sequence + 1}} : {}), authority_effect: "none"});
      setImmediate(() => session.flushBuffered());
      if (remainder) socket.emit("data", Buffer.from(remainder));
    };
    socket.on("data", onData);
  });

  async function start() {
    if (started) return api;
    removeSocketPath(options.listen_path);
    await new Promise((resolveStart, reject) => {
      server.once("error", reject);
      server.listen(options.listen_path, () => {
        server.off("error", reject);
        resolveStart();
      });
    });
    chmodSync(options.listen_path, 0o600);
    started = true;
    return api;
  }

  async function close() {
    for (const session of [...sessions.values()]) session.stop("gateway.shutdown");
    if (started) await new Promise((resolveClose) => server.close(resolveClose));
    started = false;
    expiredSessions.clear();
    removeSocketPath(options.listen_path);
    if (ownsSessionStore) sessionStore.close();
  }

  const api = Object.freeze({
    start,
    close,
    server,
    inspect: () => {
      pruneExpirations();
      return freezeResult({
      schema_version: "are.codex-persistent-gateway-state/v1",
      runtime_epoch_id: runtimeEpochId,
      listen_path: options.listen_path,
      started,
      sessions: [...sessions.values()].map((session) => session.inspect()).sort((a, b) => a.consumer_id.localeCompare(b.consumer_id)),
      expired_sessions: [...expiredSessions.values()].map((entry) => entry.receipt).sort((a, b) => a.consumer_id.localeCompare(b.consumer_id)),
      durable_session_index: sessionStore.inspect(),
      authority_effect: "none",
      });
    },
  });
  return api;
}
