import {execFileSync, spawn} from "node:child_process";
import {mkdtempSync} from "node:fs";
import {createConnection, createServer} from "node:net";
import {resolve} from "node:path";

import {
  ACKNOWLEDGED_CONTINUITY_MODE,
  createCodexAppServerWrapper,
  createPersistentGateway,
  deriveGatewayReasoningStateProfile,
  GATEWAY_ACK_SCHEMA,
  GATEWAY_CONNECT_SCHEMA,
  GATEWAY_DELIVERY_SCHEMA,
  GATEWAY_REQUEST_META_KEY,
  loadRepositoryProfile,
  protocolBindingCheck,
} from "../index.mjs";
import {digestValue} from "../src/canonical.mjs";

const packageRoot = resolve(import.meta.dirname, "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const profilePath = resolve(packageRoot, "profiles/repository-v1.json");
const temporaryRoot = mkdtempSync("/tmp/are-persistent-canary-");
const gatewaySocket = resolve(temporaryRoot, "are-gateway.sock");
const reasoningStateDirectory = resolve(temporaryRoot, "reasoning-state");
const sessionStorePath = resolve(temporaryRoot, "gateway-sessions.jsonl");

async function availablePort() {
  const server = createServer();
  await new Promise((resolveListen, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const port = server.address().port;
  await new Promise((resolveClose) => server.close(resolveClose));
  return port;
}

async function waitForPort(port) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const connected = await new Promise((resolveResult) => {
      const socket = createConnection({host: "127.0.0.1", port});
      socket.once("connect", () => { socket.destroy(); resolveResult(true); });
      socket.once("error", () => resolveResult(false));
    });
    if (connected) return;
    await new Promise((resolveWait) => setTimeout(resolveWait, 50));
  }
  throw new Error("upstream-websocket-listener:timeout");
}

function bounded(promise, label, milliseconds = 300000) {
  return new Promise((resolveValue, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label}:timeout`)), milliseconds);
    promise.then((value) => { clearTimeout(timer); resolveValue(value); }, (error) => { clearTimeout(timer); reject(error); });
  });
}

async function waitFor(predicate, label, milliseconds = 15000) {
  const deadline = Date.now() + milliseconds;
  while (Date.now() < deadline) {
    if (predicate()) return;
    await new Promise((resolveWait) => setTimeout(resolveWait, 50));
  }
  throw new Error(`${label}:timeout`);
}

async function connectClient(consumerId, lane, continuity = {}, options = {}) {
  const socket = createConnection(gatewaySocket);
  const messages = [];
  const waiters = [];
  const deliveries = [];
  const deliveryWaiters = [];
  const pending = new Map();
  let sequence = 0;
  let lastAcknowledgedSequence = continuity.last_acked_sequence ?? 0;
  let lastReceivedSequence = lastAcknowledgedSequence;
  const autoAcknowledge = options.auto_acknowledge !== false;
  let buffer = "";
  socket.on("data", (chunk) => {
    buffer += chunk.toString("utf8");
    let index;
    while ((index = buffer.indexOf("\n")) >= 0) {
      const frame = JSON.parse(buffer.slice(0, index));
      buffer = buffer.slice(index + 1);
      const message = frame.schema_version === GATEWAY_DELIVERY_SCHEMA ? frame.message : frame;
      if (frame.schema_version === GATEWAY_DELIVERY_SCHEMA) {
        if (frame.sequence !== lastReceivedSequence + 1) throw new Error(`${consumerId}:delivery-sequence:${lastReceivedSequence}->${frame.sequence}`);
        lastReceivedSequence = frame.sequence;
        deliveries.push(frame);
        for (const waiter of [...deliveryWaiters]) {
          if (!waiter.predicate(frame)) continue;
          deliveryWaiters.splice(deliveryWaiters.indexOf(waiter), 1);
          waiter.resolve(frame);
        }
      }
      messages.push(message);
      for (const waiter of [...waiters]) {
        if (!waiter.predicate(message)) continue;
        waiters.splice(waiters.indexOf(waiter), 1);
        waiter.resolve(message);
      }
      if (message.method?.endsWith("/requestApproval")) {
        const result = message.method === "item/permissions/requestApproval" ? {permissions: {}} : {decision: "decline"};
        socket.write(`${JSON.stringify({jsonrpc: "2.0", id: message.id, result})}\n`);
      }
      if (Object.hasOwn(message, "id") && pending.has(String(message.id))) {
        const request = pending.get(String(message.id));
        pending.delete(String(message.id));
        if (message.error) request.reject(new Error(`${request.method}:${JSON.stringify(message.error)}`));
        else request.resolve(message.result);
      }
      if (frame.schema_version === GATEWAY_DELIVERY_SCHEMA) {
        if (autoAcknowledge) {
          lastAcknowledgedSequence = frame.sequence;
          socket.write(`${JSON.stringify({schema_version: GATEWAY_ACK_SCHEMA, through_sequence: lastAcknowledgedSequence})}\n`);
        }
      }
    }
  });
  await bounded(new Promise((resolveConnect, reject) => {
    socket.once("connect", resolveConnect);
    socket.once("error", reject);
  }), `${consumerId}:connect`, 15000);
  socket.write(`${JSON.stringify({schema_version: GATEWAY_CONNECT_SCHEMA, consumer_id: consumerId, lane, continuity: {mode: ACKNOWLEDGED_CONTINUITY_MODE, last_acked_sequence: lastAcknowledgedSequence, request_aliases: [], ...(continuity.resume_token ? {resume_token: continuity.resume_token} : {})}})}\n`);
  const receipt = await bounded(waitMessage((message) => message.schema_version === "are.codex-gateway-connected/v1"), `${consumerId}:handshake`, 15000);

  function request(method, params, requestKey = null) {
    const id = ++sequence;
    socket.write(`${JSON.stringify({jsonrpc: "2.0", id, method, params, ...(requestKey ? {[GATEWAY_REQUEST_META_KEY]: {request_key: requestKey}} : {})})}\n`);
    return new Promise((resolveValue, reject) => pending.set(String(id), {resolve: resolveValue, reject, method}));
  }

  function waitMessage(predicate) {
    const existing = messages.find(predicate);
    if (existing) return Promise.resolve(existing);
    return new Promise((resolveValue) => waiters.push({predicate, resolve: resolveValue}));
  }

  function waitDelivery(predicate) {
    const existing = deliveries.find(predicate);
    if (existing) return Promise.resolve(existing);
    return new Promise((resolveValue) => deliveryWaiters.push({predicate, resolve: resolveValue}));
  }

  function acknowledgeReceived() {
    if (lastReceivedSequence <= lastAcknowledgedSequence) return lastAcknowledgedSequence;
    lastAcknowledgedSequence = lastReceivedSequence;
    socket.write(`${JSON.stringify({schema_version: GATEWAY_ACK_SCHEMA, through_sequence: lastAcknowledgedSequence})}\n`);
    return lastAcknowledgedSequence;
  }

  return {socket, receipt, request, waitMessage, waitDelivery, acknowledgeReceived, messages, deliveries, continuityState: () => ({resume_token: receipt.continuity?.resume_token, last_acked_sequence: lastAcknowledgedSequence, last_received_sequence: lastReceivedSequence})};
}

async function runTurn(client, threadId, text, label) {
  const started = await bounded(client.request("turn/start", {
    threadId,
    input: [{type: "text", text}],
    approvalPolicy: "never",
    sandboxPolicy: {type: "readOnly", networkAccess: false},
  }), `${label}:turn-start`);
  const turnId = started.turn.id;
  await bounded(client.waitMessage((message) => message.method === "turn/completed" && message.params?.turn?.id === turnId), `${label}:turn-completed`);
  await bounded(client.waitMessage((message) => message.method === "cyberalchemy/decision" && message.params?.directive_kind === "complete" && message.params?.completion_digest), `${label}:decision`);
  return turnId;
}

function contextView(gateway, consumerId) {
  const session = gateway.inspect().sessions.find((item) => item.consumer_id === consumerId);
  return session?.wrapper_state?.current_context_epochs?.[0]?.view_id ?? null;
}

let observedVersion = "unavailable";
try { observedVersion = execFileSync("codex", ["--version"], {encoding: "utf8"}).trim(); } catch {}
const loaded = loadRepositoryProfile(profilePath, repositoryRoot);
if (!loaded.ok) throw new Error(`repository-profile:${loaded.reason_codes.join(",")}`);
const binding = protocolBindingCheck(loaded.value.protocol_binding, observedVersion);
let upstream = null;
let gateway = null;
let upstreamStderr = "";
let gatewayStderr = "";
let output;

try {
  if (!binding.ok) throw new Error(`protocol-binding:${binding.reason_codes.join(",")}`);
  const upstreamPort = await availablePort();
  const upstreamUrl = `ws://127.0.0.1:${upstreamPort}`;
  upstream = spawn("codex", ["app-server", "--listen", upstreamUrl], {stdio: ["ignore", "ignore", "pipe"]});
  upstream.stderr.on("data", (chunk) => { upstreamStderr += chunk; });
  await waitForPort(upstreamPort);
  const allowed = new Map(loaded.value.gateway.allowed_clients.map((client) => [client.consumer_id, client]));
  const buildGateway = () => createPersistentGateway({
    listen_path: gatewaySocket,
    backend: {mode: "websocket", url: upstreamUrl},
    max_clients: loaded.value.gateway.max_clients,
    max_buffered_messages_per_client: loaded.value.gateway.max_buffered_messages_per_client,
    reconnect: true,
    session_store_path: sessionStorePath,
    detach_timeout_ms: loaded.value.gateway.detach_timeout_ms,
    idle_timeout_ms: loaded.value.gateway.idle_timeout_ms,
    max_retained_bytes_per_session: loaded.value.gateway.max_retained_bytes_per_session,
    max_reasoning_log_bytes_per_session: loaded.value.gateway.max_reasoning_log_bytes_per_session,
    expiration_tombstone_ttl_ms: loaded.value.gateway.expiration_tombstone_ttl_ms,
    eviction_retry_ms: loaded.value.gateway.eviction_retry_ms,
    authorize_client: ({consumer_id, lane}) => allowed.get(consumer_id)?.lane === lane,
    on_backend_stderr: (chunk) => { gatewayStderr += chunk; },
    wrapper_factory: ({consumer_id, lane}) => {
      const profile = structuredClone(loaded.value);
      profile.turn_bindings.default = {
        ...profile.turn_bindings.default,
        lane,
        consumer_ref: consumer_id,
        ...(lane === "plan-bound" ? {window_ref: allowed.get(consumer_id).window_ref, request_id: allowed.get(consumer_id).request_id} : {}),
      };
      profile.reasoning_state = deriveGatewayReasoningStateProfile(loaded.value, consumer_id, reasoningStateDirectory);
      return createCodexAppServerWrapper({
        loaded_profile: profile,
        decision_profile: loaded.decision_profile,
        definition_catalog: loaded.definition_catalog,
        ontology_snapshot: loaded.ontology_snapshot,
        source_snapshot: loaded.source_snapshot,
        context_source_provider: loaded.context_source_provider,
        semantic_profile: loaded.semantic_profile,
      });
    },
  });
  gateway = buildGateway();
  await gateway.start();

  const plan = await connectClient("codex:plan", "plan-bound");
  const planInitialization = {clientInfo: {name: "are-persistent-plan-canary", version: "0.1.0"}, capabilities: {experimentalApi: true}};
  await bounded(plan.request("initialize", planInitialization), "plan:initialize");
  const planThreadParams = {cwd: "/tmp", ephemeral: true, model: "gpt-5.6-sol", approvalPolicy: "never", sandbox: "read-only"};
  const planThread = await bounded(plan.request("thread/start", planThreadParams, "plan:thread-start:stable"), "plan:thread-start");
  const stablePlanPrompt = "Research Context Envelope provenance and answer in one sentence. Do not use tools.";
  const planTurn1 = await runTurn(plan, planThread.thread.id, stablePlanPrompt, "plan:first");
  const planView1 = contextView(gateway, "codex:plan");
  plan.socket.destroy();
  await waitFor(() => gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan")?.attached === false, "plan-detach");
  const resumedPlan = await connectClient("codex:plan", "plan-bound", plan.continuityState());
  const reconnectInitializationStarted = performance.now();
  await bounded(resumedPlan.request("initialize", planInitialization), "plan:reconnect-initialize");
  const reconnectInitializationLatencyMs = performance.now() - reconnectInitializationStarted;
  const reconnectInitializationResultDigestVerified = digestValue(resumedPlan.receipt.initialization?.result) === resumedPlan.receipt.initialization?.result_digest;
  const replayedPlanThread = await bounded(resumedPlan.request("thread/start", planThreadParams, "plan:thread-start:stable"), "plan:reconnect-thread-replay");
  const resumedInitializationState = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan");
  const planTurn2 = await runTurn(resumedPlan, planThread.thread.id, stablePlanPrompt, "plan:second");
  const planView2 = contextView(gateway, "codex:plan");

  const human = await connectClient("codex:human-chat", "interaction-bound");
  await bounded(human.request("initialize", {clientInfo: {name: "are-persistent-human-canary", version: "0.1.0"}, capabilities: {experimentalApi: true}}), "human:initialize");
  const humanThread = await bounded(human.request("thread/start", {cwd: "/tmp", ephemeral: true, model: "gpt-5.6-sol", approvalPolicy: "never", sandbox: "read-only"}), "human:thread-start");
  const humanTurn1 = await runTurn(human, humanThread.thread.id, "Research Context Envelope provenance and answer in one sentence. Do not use tools.", "human:first");
  const humanView1 = contextView(gateway, "codex:human-chat");
  const humanTurn2 = await runTurn(human, humanThread.thread.id, "Research Context Envelope freshness and answer in one sentence. Do not use tools.", "human:second");
  const humanView2 = contextView(gateway, "codex:human-chat");

  const streamProbe = await connectClient("codex:benchmark", "interaction-bound", {}, {auto_acknowledge: false});
  await bounded(streamProbe.request("initialize", {clientInfo: {name: "are-persistent-stream-canary", version: "0.1.0"}, capabilities: {experimentalApi: true}}), "stream:initialize");
  const streamThread = await bounded(streamProbe.request("thread/start", {cwd: "/tmp", ephemeral: true, model: "gpt-5.6-sol", approvalPolicy: "never", sandbox: "read-only"}), "stream:thread-start");
  const acknowledgedBeforeStream = streamProbe.acknowledgeReceived();
  await waitFor(() => gateway.inspect().durable_session_index.sessions.find((item) => item.consumer_id === "codex:benchmark")?.acknowledged_through === acknowledgedBeforeStream, "stream:pre-turn-ack");
  const streamTurn = await bounded(streamProbe.request("turn/start", {
    threadId: streamThread.thread.id,
    input: [{type: "text", text: "Explain context provenance in one sentence. Do not use tools."}],
    approvalPolicy: "never",
    sandboxPolicy: {type: "readOnly", networkAccess: false},
  }), "stream:turn-start");
  const interruptedStreamDelivery = await bounded(streamProbe.waitDelivery((frame) => frame.sequence > acknowledgedBeforeStream && frame.message?.method === "item/agentMessage/delta"), "stream:first-agent-delta");
  const streamContinuityBeforeRestart = streamProbe.continuityState();

  const planStateBeforeRestart = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan")?.wrapper_state;
  const humanStateBeforeRestart = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:human-chat")?.wrapper_state;

  const effectRequests = [...plan.messages, ...resumedPlan.messages, ...human.messages].filter((message) => message.method?.endsWith("/requestApproval")).length;
  const semanticNotifications = [...plan.messages, ...resumedPlan.messages, ...human.messages].filter((message) => message.method === "cyberalchemy/semantic").length;
  const planContinuityBeforeRestart = resumedPlan.continuityState();
  resumedPlan.socket.destroy();
  human.socket.destroy();
  streamProbe.socket.destroy();
  await gateway.close();
  gateway = buildGateway();
  await gateway.start();
  const restartedStreamProbe = await connectClient("codex:benchmark", "interaction-bound", streamContinuityBeforeRestart);
  const replayedStreamDelivery = await bounded(restartedStreamProbe.waitDelivery((frame) => frame.sequence === interruptedStreamDelivery.sequence), "stream:replay-after-restart", 30000);
  const restartedPlan = await connectClient("codex:plan", "plan-bound", planContinuityBeforeRestart);
  const recoveredPlanState = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan")?.wrapper_state;
  const recovered = recoveredPlanState?.reasoning_state?.recovery?.disposition === "recovered"
    && recoveredPlanState?.completion_frontier_turn_ids?.length >= 2
    && recoveredPlanState?.reasoning_state_writer_lock?.released === false;
  await bounded(restartedPlan.request("initialize", {clientInfo: {name: "are-persistent-restart-canary", version: "0.1.0"}, capabilities: {experimentalApi: true}}), "restart:initialize");
  const restartedStablePlanThread = await bounded(restartedPlan.request("thread/start", planThreadParams, "plan:thread-start:stable"), "restart:stable-thread-replay");
  const restartedPlanSessionBeforeTurn = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan");
  const restartStarted = await bounded(restartedPlan.request("turn/start", {
    threadId: planThread.thread.id,
    input: [{type: "text", text: stablePlanPrompt}],
    approvalPolicy: "never",
    sandboxPolicy: {type: "readOnly", networkAccess: false},
  }), "plan:after-restart-dispatch");
  const postRestartPlanState = gateway.inspect().sessions.find((item) => item.consumer_id === "codex:plan")?.wrapper_state;
  const restartPrefixReused = postRestartPlanState?.cache_affinity_consumers?.[0]?.exact_prefix_reuse === true;
  const passed = plan.receipt.resumed === false
    && resumedPlan.receipt.resumed === true
    && resumedPlan.receipt.continuity?.resume_token_digest === plan.receipt.continuity?.resume_token_digest
    && resumedPlan.receipt.initialization?.status === "complete"
    && reconnectInitializationResultDigestVerified
    && resumedInitializationState?.initialization_forward_count === 1
    && resumedInitializationState?.initialization_replay_count === 1
    && resumedInitializationState?.upstream_request_count === 1
    && resumedInitializationState?.deduplicated_request_count === 1
    && replayedPlanThread.thread.id === planThread.thread.id
    && restartedPlan.receipt.resumed === true
    && restartedStreamProbe.receipt.resumed === true
    && digestValue(replayedStreamDelivery.message) === digestValue(interruptedStreamDelivery.message)
    && replayedStreamDelivery.sequence === interruptedStreamDelivery.sequence
    && restartedStablePlanThread.thread.id === planThread.thread.id
    && restartedPlanSessionBeforeTurn?.upstream_request_count === 0
    && planView1 === planView2
    && humanView1 !== humanView2
    && planStateBeforeRestart?.cache_affinity_consumers?.[0]?.exact_prefix_reuse === true
    && humanStateBeforeRestart?.reasoning_state?.checkpoint_count >= 4
    && recovered
    && restartPrefixReused
    && effectRequests === 0
    && semanticNotifications === 0;
  output = {
    schema_version: "are.codex-persistent-gateway-live-canary/v1",
    status: passed ? "PASS" : "FAIL",
    observed_codex_version: observedVersion,
    protocol_binding: "matched",
    backend_mode: "websocket-isolated-canary",
    plan_bound: {thread_id: planThread.thread.id, turn_ids: [planTurn1, planTurn2], reconnected: resumedPlan.receipt.resumed, authenticated_resume: resumedPlan.receipt.continuity?.resume_token_digest === plan.receipt.continuity?.resume_token_digest, acknowledged_through: resumedPlan.continuityState().last_acked_sequence, initialization_replayed: resumedInitializationState?.initialization_replay_count === 1, initialization_result_digest_verified: reconnectInitializationResultDigestVerified, upstream_initializations: resumedInitializationState?.initialization_forward_count ?? null, stable_request_upstream_dispatches: resumedInitializationState?.upstream_request_count ?? null, stable_request_deduplications: resumedInitializationState?.deduplicated_request_count ?? null, stable_thread_identity_replayed: replayedPlanThread.thread.id === planThread.thread.id, reconnect_initialization_latency_ms: reconnectInitializationLatencyMs, context_view_identity_reused: planView1 === planView2, exact_prefix_reuse: planStateBeforeRestart?.cache_affinity_consumers?.[0]?.exact_prefix_reuse ?? null, cache_hit_posture: planStateBeforeRestart?.cache_affinity_consumers?.[0]?.cache_hit_posture ?? "unobserved", observed_token_savings: planStateBeforeRestart?.cache_affinity_consumers?.[0]?.observed_token_savings ?? null, observed_time_savings_ms: planStateBeforeRestart?.cache_affinity_consumers?.[0]?.observed_time_savings_ms ?? null},
    interaction_bound: {thread_id: humanThread.thread.id, turn_ids: [humanTurn1, humanTurn2], context_view_identity_succeeded: humanView1 !== humanView2},
    restart_recovery: {authenticated_session_resumption: restartedPlan.receipt.resumed, disposition: recoveredPlanState?.reasoning_state?.recovery?.disposition ?? null, recovered_completion_frontiers: recoveredPlanState?.completion_frontier_turn_ids?.length ?? 0, writer_lock_held: recoveredPlanState?.reasoning_state_writer_lock?.released === false, stable_thread_identity_replayed: restartedStablePlanThread.thread.id === planThread.thread.id, stable_request_upstream_redispatches: restartedPlanSessionBeforeTurn?.upstream_request_count ?? null, post_restart_dispatch_turn_id: restartStarted.turn.id, exact_prefix_reuse: restartPrefixReused, cache_hit_posture: postRestartPlanState?.cache_affinity_consumers?.[0]?.cache_hit_posture ?? "unobserved"},
    interrupted_stream_recovery: {thread_id: streamThread.thread.id, turn_id: streamTurn.turn.id, acknowledged_before_stream: acknowledgedBeforeStream, interrupted_delivery_sequence: interruptedStreamDelivery.sequence, replayed_delivery_sequence: replayedStreamDelivery.sequence, exact_message_replay: digestValue(replayedStreamDelivery.message) === digestValue(interruptedStreamDelivery.message), authenticated_session_resumption: restartedStreamProbe.receipt.resumed},
    consumer_sessions: gateway.inspect().sessions.length,
    effect_requests: effectRequests,
    semantic_notifications: semanticNotifications,
    authority_effect: "none",
    claim_limit: "Controlled ephemeral local persistent-gateway canary only; no Desktop integration, daemon installation, admission, conformance, publication, deployment, or external-effect authority.",
  };
  restartedPlan.socket.destroy();
  restartedStreamProbe.socket.destroy();
} catch (error) {
  output = {schema_version: "are.codex-persistent-gateway-live-canary/v1", status: "FAIL", error: error.message, observed_codex_version: observedVersion, authority_effect: "none"};
} finally {
  if (gateway) await gateway.close();
  if (upstream) upstream.kill("SIGTERM");
}

output.stderr = [...gatewayStderr.split("\n"), ...upstreamStderr.split("\n")].filter(Boolean).slice(-20);
process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
process.exitCode = output.status === "PASS" ? 0 : 1;
