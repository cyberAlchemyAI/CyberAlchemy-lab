import {EventEmitter} from "node:events";
import {spawn} from "node:child_process";
import {createInterface} from "node:readline";

import {digestValue, isRecord, nonEmptyString} from "./canonical.mjs";
import {GATEWAY_REQUEST_META_KEY} from "./gateway.mjs";
import {signHostedInput, validHostedInputAttestationKey} from "./hosted-input-attestation.mjs";
import {CONTINUITY_NOTIFICATION} from "./protocol.mjs";
import {classifyBackendDiagnostic} from "./diagnostics.mjs";
import {declineElicitationResult, defaultApprovalResult, isApprovalRequest} from "./server-request-contract.mjs";

export class AppServerRpcError extends Error {
  constructor(code, message, details = null) {
    super(message);
    this.name = "AppServerRpcError";
    this.code = code;
    this.details = details;
  }
}

export function spawnAppServerRpcTransport(options = {}) {
  const closeTimeout = options.close_timeout_ms ?? 5000;
  if (!Number.isSafeInteger(closeTimeout) || closeTimeout < 1 || closeTimeout > 30000) {
    throw new TypeError("Invalid transport close timeout.");
  }
  const child = (options.spawn_impl ?? spawn)(options.command, options.args ?? [], {stdio: ["pipe", "pipe", "pipe"], env: options.env ?? process.env});
  const failure = new EventEmitter();
  let stderr = "";
  let stdoutTail = "";
  let closing = false;
  let failed = false;
  let failureError = null;
  let reaped = false;
  let closePromise = null;
  child.stderr.on("data", (chunk) => { stderr = `${stderr}${chunk}`.slice(-16384); });
  child.stdout.on("data", (chunk) => { stdoutTail = `${stdoutTail}${chunk}`.slice(-16384); });
  child.on("error", (error) => {
    if (closing || failed) return;
    failed = true;
    failureError = new AppServerRpcError("rpc.transport-spawn-failed", `App-server transport failed to start: ${error.message}`, {cause: error.message});
    failure.emit("failure", failureError);
  });
  child.on("close", (code, signal) => {
    reaped = true;
    if (closing || failed) return;
    failed = true;
    const diagnostic = classifyBackendDiagnostic(stderr.trim() || stdoutTail.trim(), {classification: "rpc-transport-exit"});
    failureError = new AppServerRpcError("rpc.transport-exited", `App-server transport exited: ${signal ?? code}`, {code, signal, diagnostic});
    failure.emit("failure", failureError);
  });
  async function close() {
    if (closePromise === null) {
      closing = true;
      closePromise = Promise.resolve().then(() => new Promise((resolveValue, reject) => {
        if (reaped) return resolveValue();
        let forceTimer = null;
        let finalTimer = null;
        const settle = error => {
          clearTimeout(forceTimer);
          clearTimeout(finalTimer);
          child.off("close", onReaped);
          if (error) reject(error); else resolveValue();
        };
        const onReaped = () => settle();
        child.once("close", onReaped);
        try {
          child.stdin.end();
          if (reaped) return settle();
          if (child.exitCode === null && child.signalCode === null) child.kill("SIGTERM");
          if (reaped) return settle();
          forceTimer = setTimeout(() => {
            try {
              if (reaped) return settle();
              if (child.exitCode === null && child.signalCode === null) child.kill("SIGKILL");
              if (reaped) return settle();
              finalTimer = setTimeout(() => settle(new AppServerRpcError("rpc.transport-close-timeout",
                "Owned app-server transport did not close within its teardown budget.", {authority_effect: "none"})), closeTimeout);
            } catch (error) {settle(error);}
          }, closeTimeout);
        } catch (error) {settle(error);}
      }));
    }
    return closePromise;
  }
  return Object.freeze({
    kind: "spawned-stdio",
    input: child.stdin,
    output: child.stdout,
    failure,
    ready: Promise.resolve({kind: "spawned-stdio", authority_effect: "none"}),
    get_failure: () => failureError,
    close,
    inspect: () => ({kind: "spawned-stdio", closing, failed, reaped, diagnostic: classifyBackendDiagnostic(stderr), exit_code: child.exitCode,
      signal_code: child.signalCode, authority_effect: "none"}),
  });
}

function unsupportedServerRequest(id) {
  return {jsonrpc: "2.0", id, error: {code: -32601, message: "ARE client does not support this host request",
    data: {reason_codes: ["rpc.server-request-unsupported"], authority_effect: "none"}}};
}

function agentText(completed, deltas) {
  const items = completed?.turn?.items ?? [];
  const messages = items.filter((item) => item?.type === "agentMessage" && typeof item.text === "string");
  return messages.length > 0 ? messages[messages.length - 1].text : deltas;
}

const validTurnIdentity = value => nonEmptyString(value) && value === value.trim()
  && Buffer.byteLength(value, "utf8") <= 256;
const turnIdentityKey = (threadId, turnId) => JSON.stringify([threadId, turnId]);

export function createAppServerRpcClient(options = {}) {
  const transport = options.transport;
  if (!transport?.input || !transport?.output || !transport?.ready) throw new TypeError("An app-server RPC transport is required.");
  const hostedInputKey = options.hosted_input_attestation_key ?? null;
  const hostedInputConsumer = options.hosted_input_consumer_id ?? null;
  if (hostedInputKey !== null && (!validHostedInputAttestationKey(hostedInputKey)
    || !nonEmptyString(hostedInputConsumer))) throw new TypeError("A hosted input attestation key requires its consumer identity.");
  const requestTimeout = options.request_timeout_ms ?? 180000;
  const completionTimeout = options.completion_timeout_ms ?? 300000;
  const maxNotifications = options.max_notifications ?? 512;
  const serverRequestTimeout = options.server_request_timeout_ms ?? 120000;
  const maxPendingServerRequests = options.max_pending_server_requests ?? 64;
  const dynamicToolHandler = options.dynamic_tool_handler ?? null;
  const dynamicToolName = options.dynamic_tool_name ?? null;
  if ((dynamicToolHandler !== null || dynamicToolName !== null)
    && (typeof dynamicToolHandler !== "function" || !nonEmptyString(dynamicToolName)
      || !/^[A-Za-z][A-Za-z0-9_]{0,63}$/.test(dynamicToolName))) {
    throw new TypeError("A dynamic tool handler requires one exact tool name.");
  }
  if (!Number.isSafeInteger(serverRequestTimeout) || serverRequestTimeout < 1 || serverRequestTimeout > 600000) throw new TypeError("Invalid server request timeout.");
  if (!Number.isSafeInteger(maxPendingServerRequests) || maxPendingServerRequests < 1 || maxPendingServerRequests > 1024) throw new TypeError("Invalid pending server request limit.");
  const pending = new Map();
  const pendingServerRequests = new Map();
  const activeServerHandlers = new Set();
  const notifications = [];
  const waiters = new Set();
  const deltas = new Map();
  const events = new EventEmitter();
  let sequence = 0;
  let closed = false;
  let failure = null;
  let closePromise = null;
  let initializationReuseCount = 0;

  function failAll(error) {
    if (failure) return;
    failure = error instanceof Error ? error : new AppServerRpcError("rpc.transport-failed", String(error));
    closed = true;
    for (const entry of pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(failure);
    }
    pending.clear();
    for (const entry of pendingServerRequests.values()) {
      clearTimeout(entry.timer);
      entry.abort_controller.abort();
    }
    pendingServerRequests.clear();
    for (const waiter of waiters) {
      clearTimeout(waiter.timer);
      waiter.reject(failure);
    }
    waiters.clear();
    lines.close();
    events.emit("failure", failure);
  }

  function send(value) {
    if (closed) throw failure ?? new AppServerRpcError("rpc.closed", "App-server RPC client is closed.");
    transport.input.write(`${JSON.stringify(value)}\n`);
  }

  function rememberNotification(message) {
    notifications.push(message);
    if (notifications.length > maxNotifications) notifications.splice(0, notifications.length - maxNotifications);
    for (const waiter of [...waiters]) {
      let matched = false;
      try { matched = waiter.predicate(message); } catch (error) {
        clearTimeout(waiter.timer);
        waiters.delete(waiter);
        waiter.reject(error);
        continue;
      }
      if (!matched) continue;
      clearTimeout(waiter.timer);
      waiters.delete(waiter);
      waiter.resolve(message);
    }
    events.emit("notification", message);
  }

  function handleServerRequest(message) {
    const key = `${typeof message.id}:${String(message.id)}`;
    if (pendingServerRequests.has(key)) {
      failAll(new AppServerRpcError("rpc.server-request-id-collision", "App-server reused a pending server request id."));
      return;
    }
    if (activeServerHandlers.size >= maxPendingServerRequests) {
      send({jsonrpc: "2.0", id: message.id, error: {code: -32099, message: "ARE client server-request capacity exceeded",
        data: {reason_codes: ["rpc.server-request-capacity"], authority_effect: "none"}}});
      return;
    }
    const entry = {timer: null, abort_controller: new AbortController(), thread_id: message.params?.threadId};
    pendingServerRequests.set(key, entry);
    const finish = (response) => {
      if (pendingServerRequests.get(key) !== entry) return;
      clearTimeout(entry.timer);
      pendingServerRequests.delete(key);
      entry.abort_controller.abort();
      try { send(response); } catch (error) { failAll(error); }
    };
    entry.timer = setTimeout(() => finish({jsonrpc: "2.0", id: message.id, error: {code: -32098, message: "ARE client server request timed out",
      data: {reason_codes: ["rpc.server-request-timeout"], authority_effect: "none"}}}), serverRequestTimeout);
    const handler = Promise.resolve().then(async () => {
      if (entry.abort_controller.signal.aborted) return;
      if (isApprovalRequest(message.method)) {
        try {
          const result = await (options.approval_handler?.(message, {signal: entry.abort_controller.signal}) ?? defaultApprovalResult(message.method));
          if (!result || typeof result !== "object" || Array.isArray(result)) throw new TypeError("invalid approval response");
          return {jsonrpc: "2.0", id: message.id, result};
        } catch {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32603, message: "ARE approval handler failed",
            data: {reason_codes: ["rpc.approval-handler-failed"], authority_effect: "none"}}};
        }
      }
      if (message.method === "mcpServer/elicitation/request") {
        if (!options.elicitation_handler) return {jsonrpc: "2.0", id: message.id, result: declineElicitationResult()};
        try {
          const result = await options.elicitation_handler(message, {signal: entry.abort_controller.signal});
          if (!result || typeof result !== "object" || Array.isArray(result)
            || !["accept", "decline", "cancel"].includes(result.action)
            || (result.action === "accept" && (!result.content || typeof result.content !== "object" || Array.isArray(result.content)))
            || (result.action !== "accept" && result.content !== null)) throw new TypeError("invalid elicitation response");
          return {jsonrpc: "2.0", id: message.id, result};
        } catch {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32603, message: "ARE elicitation handler failed",
            data: {reason_codes: ["rpc.elicitation-handler-failed"], authority_effect: "none"}}};
        }
      }
      if (message.method === "currentTime/read") {
        const threadId = message.params?.threadId;
        if (!nonEmptyString(threadId) || threadId !== threadId.trim() || Buffer.byteLength(threadId, "utf8") > 256) {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32602, message: "ARE current-time request requires a valid thread id",
            data: {reason_codes: ["rpc.current-time-thread-id-required"], authority_effect: "none"}}};
        }
        const currentTimeAt = Math.floor(Date.now() / 1000);
        if (!Number.isSafeInteger(currentTimeAt) || currentTimeAt < 0) {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32603, message: "ARE current-time clock is unavailable",
            data: {reason_codes: ["rpc.current-time-unavailable"], authority_effect: "none"}}};
        }
        return {jsonrpc: "2.0", id: message.id, result: {currentTimeAt}};
      }
      if (message.method === "item/tool/requestUserInput" && options.user_input_handler) {
        try {
          const result = await options.user_input_handler(message, {signal: entry.abort_controller.signal});
          if (!result || typeof result !== "object" || Array.isArray(result) || !result.answers || typeof result.answers !== "object" || Array.isArray(result.answers)) {
            throw new TypeError("invalid user input response");
          }
          return {jsonrpc: "2.0", id: message.id, result};
        } catch {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32603, message: "ARE user input handler failed",
            data: {reason_codes: ["rpc.user-input-handler-failed"], authority_effect: "none"}}};
        }
      }
      if (message.method === "item/tool/call" && dynamicToolHandler) {
        const params = message.params;
        const bounded = value => nonEmptyString(value) && value === value.trim()
          && Buffer.byteLength(value, "utf8") <= 256;
        let argumentBytes;
        try { argumentBytes = Buffer.byteLength(JSON.stringify(params?.arguments), "utf8"); }
        catch { argumentBytes = Infinity; }
        if (!isRecord(params) || Object.keys(params).some(key => ![
          "threadId", "turnId", "callId", "namespace", "tool", "arguments"].includes(key))
          || !bounded(params.threadId) || !bounded(params.turnId) || !bounded(params.callId)
          || params.namespace !== null || params.tool !== dynamicToolName
          || !isRecord(params.arguments) || argumentBytes > 65536) {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32602,
            message: "ARE dynamic tool request is invalid",
            data: {reason_codes: ["rpc.dynamic-tool-request-invalid"], authority_effect: "none"}}};
        }
        try {
          const result = await dynamicToolHandler(message, {signal: entry.abort_controller.signal});
          let outputBytes;
          try { outputBytes = Buffer.byteLength(JSON.stringify(result), "utf8"); }
          catch { outputBytes = Infinity; }
          if (!isRecord(result) || Object.keys(result).some(key => !["contentItems", "success"].includes(key))
            || typeof result.success !== "boolean" || !Array.isArray(result.contentItems)
            || result.contentItems.length > 16 || outputBytes > 65536
            || result.contentItems.some(item => !isRecord(item)
              || Object.keys(item).sort().join(",") !== "text,type"
              || item.type !== "inputText" || typeof item.text !== "string")) {
            throw new TypeError("invalid dynamic tool response");
          }
          return {jsonrpc: "2.0", id: message.id, result};
        } catch {
          return {jsonrpc: "2.0", id: message.id, error: {code: -32603,
            message: "ARE dynamic tool handler failed",
            data: {reason_codes: ["rpc.dynamic-tool-handler-failed"], authority_effect: "none"}}};
        }
      }
      return unsupportedServerRequest(message.id);
    });
    activeServerHandlers.add(handler);
    handler.then((response) => {
      activeServerHandlers.delete(handler);
      finish(response);
    }, () => {
      activeServerHandlers.delete(handler);
      finish({jsonrpc: "2.0", id: message.id, error: {code: -32603, message: "ARE server request handling failed",
        data: {reason_codes: ["rpc.server-request-failed"], authority_effect: "none"}}});
    });
  }

  async function handleMessage(message) {
    if (Object.hasOwn(message, "id") && !message.method) {
      const entry = pending.get(String(message.id));
      if (!entry) return;
      clearTimeout(entry.timer);
      pending.delete(String(message.id));
      if (message.error) entry.reject(new AppServerRpcError("rpc.response-error", `${entry.method}: ${message.error.message ?? "JSON-RPC error"}`, message.error));
      else entry.resolve(message.result);
      return;
    }
    if (message.method === "item/agentMessage/delta") {
      const {threadId, turnId, delta} = message.params ?? {};
      if (validTurnIdentity(threadId) && validTurnIdentity(turnId) && typeof delta === "string") {
        const key = turnIdentityKey(threadId, turnId);
        deltas.set(key, `${deltas.get(key) ?? ""}${delta}`);
      }
    }
    if (typeof message.method === "string" && Object.hasOwn(message, "id")) {
      handleServerRequest(message);
      return;
    }
    if (message.method === "serverRequest/resolved") {
      const {requestId, threadId} = isRecord(message.params) ? message.params : {};
      const validId = (typeof requestId === "string" && nonEmptyString(requestId)
        && requestId === requestId.trim() && Buffer.byteLength(requestId, "utf8") <= 256)
        || Number.isSafeInteger(requestId);
      const validThread = nonEmptyString(threadId) && threadId === threadId.trim()
        && Buffer.byteLength(threadId, "utf8") <= 256;
      const key = validId ? `${typeof requestId}:${String(requestId)}` : null;
      const entry = key === null ? null : pendingServerRequests.get(key);
      if (validThread && entry?.thread_id === threadId) {
        // The host has already resolved this request. Retire it before abort
        // listeners or UI notification subscribers can produce a late reply.
        // Keep uncooperative handlers charged against capacity until they settle.
        pendingServerRequests.delete(key);
        clearTimeout(entry.timer);
        entry.abort_controller.abort();
      }
    }
    if (message.method === CONTINUITY_NOTIFICATION && options.continuity_consumer) {
      if (typeof options.continuity_consumer.consume !== "function") {
        throw new AppServerRpcError("rpc.continuity-consumer-invalid", "The continuity consumer must expose consume(message).", {authority_effect: "none"});
      }
      const consumed = await options.continuity_consumer.consume(message);
      if (closed) return;
      if (!consumed?.ok) {
        throw new AppServerRpcError("rpc.continuity-notification-invalid", "The continuity notification failed host validation.", consumed);
      }
      events.emit("continuity", consumed);
    }
    rememberNotification(message);
  }

  const lines = createInterface({input: transport.output, crlfDelay: Infinity});
  let ordered = Promise.resolve();
  lines.on("line", (line) => {
    ordered = ordered.then(async () => {
      // readline may already have queued more frames when failure or owner
      // teardown closes it. Terminal state must also fence the queued work.
      if (closed) return;
      let message;
      try { message = JSON.parse(line); } catch {
        throw new AppServerRpcError("rpc.invalid-json", "App-server transport emitted invalid JSON.", {line: line.slice(0, 1024)});
      }
      await handleMessage(message);
    }).catch(failAll);
  });
  lines.on("error", failAll);
  transport.failure?.on("failure", failAll);
  const retainedTransportFailure = transport.get_failure?.();
  if (retainedTransportFailure) failAll(retainedTransportFailure);

  async function request(method, params, requestOptions = {}) {
    await transport.ready;
    if (closed) throw failure ?? new AppServerRpcError("rpc.closed", "App-server RPC client is closed.");
    const id = requestOptions.request_id ?? `are-rpc-${++sequence}`;
    if (!(["string", "number"].includes(typeof id))) throw new TypeError("request_id must be a string or number.");
    const key = String(id);
    if (pending.has(key)) throw new AppServerRpcError("rpc.request-id-collision", "A client request id is already pending.");
    if (requestOptions.idempotency_key !== undefined && (!nonEmptyString(requestOptions.idempotency_key) || requestOptions.idempotency_key.length > 256)) {
      throw new TypeError("idempotency_key must be a non-empty string of at most 256 characters.");
    }
    if (requestOptions.hosted_input === true && hostedInputKey === null) {
      throw new TypeError("Hosted input attestation is unavailable.");
    }
    const gatewayMetadata = requestOptions.idempotency_key
      ? {request_key: requestOptions.idempotency_key} : {};
    if (requestOptions.hosted_input === true) {
      gatewayMetadata.hosted_input_attestation = signHostedInput({key: hostedInputKey,
        consumer_id: hostedInputConsumer, method, params,
        request_key: requestOptions.idempotency_key ?? null});
    }
    const timeoutMs = requestOptions.timeout_ms ?? requestTimeout;
    return new Promise((resolveValue, reject) => {
      const timer = setTimeout(() => {
        pending.delete(key);
        reject(new AppServerRpcError("rpc.request-timeout", `${method} timed out after ${timeoutMs} ms.`, {method, timeout_ms: timeoutMs}));
      }, timeoutMs);
      pending.set(key, {method, resolve: resolveValue, reject, timer});
      const requestMessage = {jsonrpc: "2.0", id, method, params,
        ...(Object.keys(gatewayMetadata).length > 0 ? {[GATEWAY_REQUEST_META_KEY]: gatewayMetadata} : {})};
      try { send(requestMessage); } catch (error) {
        clearTimeout(timer);
        pending.delete(key);
        reject(error);
      }
    });
  }

  async function ready() {
    return transport.ready;
  }

  async function notify(method, params = {}) {
    await transport.ready;
    if (!nonEmptyString(method)) throw new TypeError("notification method must be a non-empty string.");
    send({jsonrpc: "2.0", method, params});
  }

  function waitForNotification(predicate, waitOptions = {}) {
    const existing = notifications.find(predicate);
    if (existing) return Promise.resolve(existing);
    if (closed) return Promise.reject(failure ?? new AppServerRpcError("rpc.closed", "App-server RPC client is closed."));
    const timeoutMs = waitOptions.timeout_ms ?? completionTimeout;
    return new Promise((resolveValue, reject) => {
      const waiter = {predicate, resolve: resolveValue, reject, timer: null};
      waiter.timer = setTimeout(() => {
        waiters.delete(waiter);
        reject(new AppServerRpcError("rpc.notification-timeout", `App-server notification timed out after ${timeoutMs} ms.`, {timeout_ms: timeoutMs}));
      }, timeoutMs);
      waiters.add(waiter);
    });
  }

  async function initialize(params) {
    const receipt = await transport.ready;
    const retained = receipt?.resumed === true ? receipt.initialization : null;
    if (retained?.status === "complete") {
      const actualBindingDigest = digestValue({method: "initialize", params});
      if (actualBindingDigest !== retained.binding_digest) {
        throw new AppServerRpcError("rpc.initialize-binding-mismatch", "Reconnect initialization does not match the retained app-server session.", {
          expected_binding_digest: retained.binding_digest,
          actual_binding_digest: actualBindingDigest,
          authority_effect: "none",
        });
      }
      const actualResultDigest = digestValue(retained.result);
      if (actualResultDigest !== retained.result_digest) {
        throw new AppServerRpcError("rpc.initialize-result-digest-mismatch", "Retained app-server initialization result failed digest verification.", {
          expected_result_digest: retained.result_digest,
          actual_result_digest: actualResultDigest,
          authority_effect: "none",
        });
      }
      initializationReuseCount += 1;
      return retained.result;
    }
    return request("initialize", params);
  }

  async function startThread(params, requestOptions = {}) {
    return request("thread/start", params, {...requestOptions, timeout_ms: requestOptions.timeout_ms ?? options.thread_start_timeout_ms ?? 240000});
  }

  async function runTurn(params, requestOptions = {}) {
    const threadId = params?.threadId;
    if (!validTurnIdentity(threadId)) throw new AppServerRpcError("rpc.thread-id-invalid", "turn/start requires a bounded thread identity.");
    const started = await request("turn/start", {...params, threadId}, requestOptions);
    const turnId = started?.turn?.id;
    if (!validTurnIdentity(turnId)) throw new AppServerRpcError("rpc.turn-id-missing", "turn/start did not return a bounded turn identity.");
    const key = turnIdentityKey(threadId, turnId);
    try {
      const notification = await waitForNotification(
        (message) => message.method === "turn/completed" && message.params?.threadId === threadId
          && message.params?.turn?.id === turnId,
        {timeout_ms: options.completion_timeout_ms ?? completionTimeout},
      );
      return {started, completed: notification.params, text: agentText(notification.params, deltas.get(key) ?? "")};
    } finally {deltas.delete(key);}
  }

  async function close() {
    if (closePromise === null) {
      // Failure stops admission; it does not mean owned transport cleanup ran.
      // Publish the shared teardown promise before notifying failure listeners
      // so concurrent/reentrant closes retain the same cleanup outcome.
      closePromise = Promise.resolve().then(() => transport.close?.());
      if (!closed) failAll(new AppServerRpcError("rpc.closed", "App-server RPC client was closed."));
      lines.close();
    }
    return closePromise;
  }

  return Object.freeze({
    ready,
    request,
    notify,
    initialize,
    startThread,
    runTurn,
    waitForNotification,
    close,
    events,
    inspect: () => ({closed, failure: failure?.message ?? null, pending_requests: pending.size, pending_server_requests: pendingServerRequests.size, active_server_handlers: activeServerHandlers.size, notification_waiters: waiters.size, initialization_reuse_count: initializationReuseCount, transport: transport.inspect?.() ?? null, authority_effect: "none"}),
  });
}
