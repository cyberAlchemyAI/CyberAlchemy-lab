import {EventEmitter} from "node:events";
import {spawn} from "node:child_process";
import {createInterface} from "node:readline";

import {digestValue, nonEmptyString} from "./canonical.mjs";
import {GATEWAY_REQUEST_META_KEY} from "./gateway.mjs";

export class AppServerRpcError extends Error {
  constructor(code, message, details = null) {
    super(message);
    this.name = "AppServerRpcError";
    this.code = code;
    this.details = details;
  }
}

export function spawnAppServerRpcTransport(options = {}) {
  const child = (options.spawn_impl ?? spawn)(options.command, options.args ?? [], {stdio: ["pipe", "pipe", "pipe"], env: options.env ?? process.env});
  const failure = new EventEmitter();
  let stderr = "";
  let stdoutTail = "";
  let closing = false;
  let failed = false;
  let failureError = null;
  child.stderr.on("data", (chunk) => { stderr = `${stderr}${chunk}`.slice(-16384); });
  child.stdout.on("data", (chunk) => { stdoutTail = `${stdoutTail}${chunk}`.slice(-16384); });
  child.on("error", (error) => {
    if (closing || failed) return;
    failed = true;
    failureError = new AppServerRpcError("rpc.transport-spawn-failed", `App-server transport failed to start: ${error.message}`, {cause: error.message});
    failure.emit("failure", failureError);
  });
  child.on("close", (code, signal) => {
    if (closing || failed) return;
    failed = true;
    const diagnostic = stderr.trim() || stdoutTail.trim();
    failureError = new AppServerRpcError("rpc.transport-exited", `App-server transport exited: ${signal ?? code}${diagnostic ? `: ${diagnostic}` : ""}`, {code, signal, stderr, stdout_tail: stdoutTail});
    failure.emit("failure", failureError);
  });
  async function close() {
    if (closing) return;
    closing = true;
    child.stdin.end();
    if (child.exitCode === null) child.kill("SIGTERM");
  }
  return Object.freeze({
    kind: "spawned-stdio",
    input: child.stdin,
    output: child.stdout,
    failure,
    ready: Promise.resolve({kind: "spawned-stdio", authority_effect: "none"}),
    get_failure: () => failureError,
    close,
    inspect: () => ({kind: "spawned-stdio", closing, failed, stderr, exit_code: child.exitCode, authority_effect: "none"}),
  });
}

function defaultApproval(message) {
  if (message.method === "item/permissions/requestApproval") return {permissions: {}};
  return {decision: "decline"};
}

function agentText(completed, deltas) {
  const items = completed?.turn?.items ?? [];
  const messages = items.filter((item) => item?.type === "agentMessage" && typeof item.text === "string");
  return messages.length > 0 ? messages[messages.length - 1].text : deltas;
}

export function createAppServerRpcClient(options = {}) {
  const transport = options.transport;
  if (!transport?.input || !transport?.output || !transport?.ready) throw new TypeError("An app-server RPC transport is required.");
  const requestTimeout = options.request_timeout_ms ?? 180000;
  const completionTimeout = options.completion_timeout_ms ?? 300000;
  const maxNotifications = options.max_notifications ?? 512;
  const pending = new Map();
  const notifications = [];
  const waiters = new Set();
  const deltas = new Map();
  const events = new EventEmitter();
  let sequence = 0;
  let closed = false;
  let failure = null;
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
    for (const waiter of waiters) {
      clearTimeout(waiter.timer);
      waiter.reject(failure);
    }
    waiters.clear();
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
      const turnId = message.params?.turnId;
      if (turnId) deltas.set(turnId, `${deltas.get(turnId) ?? ""}${message.params?.delta ?? ""}`);
    }
    if (message.method?.endsWith("/requestApproval") && Object.hasOwn(message, "id")) {
      const result = await (options.approval_handler?.(message) ?? defaultApproval(message));
      send({jsonrpc: "2.0", id: message.id, result});
      return;
    }
    rememberNotification(message);
  }

  const lines = createInterface({input: transport.output, crlfDelay: Infinity});
  let ordered = Promise.resolve();
  lines.on("line", (line) => {
    ordered = ordered.then(async () => {
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
    if (requestOptions.idempotency_key !== undefined && (!nonEmptyString(requestOptions.idempotency_key) || requestOptions.idempotency_key.length > 256)) {
      throw new TypeError("idempotency_key must be a non-empty string of at most 256 characters.");
    }
    const timeoutMs = requestOptions.timeout_ms ?? requestTimeout;
    return new Promise((resolveValue, reject) => {
      const timer = setTimeout(() => {
        pending.delete(id);
        reject(new AppServerRpcError("rpc.request-timeout", `${method} timed out after ${timeoutMs} ms.`, {method, timeout_ms: timeoutMs}));
      }, timeoutMs);
      pending.set(id, {method, resolve: resolveValue, reject, timer});
      const requestMessage = {jsonrpc: "2.0", id, method, params, ...(requestOptions.idempotency_key ? {[GATEWAY_REQUEST_META_KEY]: {request_key: requestOptions.idempotency_key}} : {})};
      try { send(requestMessage); } catch (error) {
        clearTimeout(timer);
        pending.delete(id);
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
    const started = await request("turn/start", params, requestOptions);
    const turnId = started?.turn?.id;
    if (!turnId) throw new AppServerRpcError("rpc.turn-id-missing", "turn/start did not return a turn identity.");
    const notification = await waitForNotification(
      (message) => message.method === "turn/completed" && message.params?.turn?.id === turnId,
      {timeout_ms: options.completion_timeout_ms ?? completionTimeout},
    );
    return {started, completed: notification.params, text: agentText(notification.params, deltas.get(turnId) ?? "")};
  }

  async function close() {
    if (closed) return;
    const error = new AppServerRpcError("rpc.closed", "App-server RPC client was closed.");
    failAll(error);
    lines.close();
    await transport.close?.();
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
    inspect: () => ({closed, failure: failure?.message ?? null, pending_requests: pending.size, notification_waiters: waiters.size, initialization_reuse_count: initializationReuseCount, transport: transport.inspect?.() ?? null, authority_effect: "none"}),
  });
}
