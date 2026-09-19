import {execFileSync} from "node:child_process";
import {dirname, resolve} from "node:path";
import {EventEmitter} from "node:events";
import {PassThrough} from "node:stream";
import {fileURLToPath} from "node:url";

import {
  AppServerRpcError,
  createAppServerRpcClient,
  createCodexAppServerWrapper,
  loadRepositoryProfile,
  protocolBindingCheck,
  runStdioProxy,
} from "../index.mjs";
import {composeSemanticLifecycle, loadSemanticInputProfile} from "../../semantic-input-runtime/index.mjs";
import {digestValue} from "../../semantic-judgment-evaluator/index.mjs";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const profilePath = resolve(packageRoot, "profiles/repository-v1.json");
const semanticProfilePath = resolve(packageRoot, "test/fixtures/semantic/profile.json");
const SCENARIOS = ["recommended", "insufficient", "owner-escalation", "tampered", "disabled", "interaction-precedence"];
const REQUEST_TIMEOUT_MS = positiveMilliseconds("ARE_CANARY_REQUEST_TIMEOUT_MS", 180000);
const EVENT_TIMEOUT_MS = positiveMilliseconds("ARE_CANARY_EVENT_TIMEOUT_MS", 120000);

function positiveMilliseconds(name, fallback) {
  const parsed = Number.parseInt(process.env[name] ?? "", 10);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function progress(scenario, stage, details = {}) {
  const event = {schema_version: "are.codex-canary-progress/v1", scenario, stage, ...details, authority_effect: "none"};
  process.stderr.write(`ARE_CANARY_PROGRESS ${JSON.stringify(event)}\n`);
  return event;
}

function failureClass(error) {
  if (["rpc.request-timeout", "rpc.notification-timeout"].includes(error?.code)) return "app-server-protocol-timeout";
  if (["rpc.transport-exited", "rpc.transport-spawn-failed", "rpc.transport-failed", "rpc.invalid-json"].includes(error?.code)) return "app-server-transport";
  return "scenario-failure";
}

function semanticInput() {
  const value = {purchase_age_days: 12, purchase_amount: 75, receipt_present: true, fraud_hold: false, final_sale: false};
  const sourceDigest = digestValue(value);
  return {
    owner_ref: "commerce-policy-owner@local",
    created_at: "2026-07-23T12:00:00.000Z",
    as_of: "2026-07-23T12:05:00.000Z",
    observation_sources: [{source_ref: "fixture://wrapper/refund-case", value, digest: sourceDigest}],
    observation_candidates: Object.entries(value).map(([field, fieldValue], index) => ({
      schema_version: "are.observation-candidate/v1",
      candidate_id: `canary:candidate:${String(index + 1).padStart(2, "0")}`,
      field,
      value: fieldValue,
      issuer_ref: "commerce-policy-owner@local",
      source_ref: "fixture://wrapper/refund-case",
      source_digest: sourceDigest,
      validator_ref: "wrapper-fixture-validator@1",
      temporal_scope: {observed_at: "2026-07-23T12:05:00.000Z"},
      proposed_posture: "admitted",
    })),
    challenge_state: {required_lanes: [{lane_id: "owner-policy-challenge", status: "closed", attempt_count: 1}]},
  };
}

function planProposal(threadId, scenario) {
  return {
    proposal_id: `canary:${scenario}:successor`,
    declared_plan_digest: `canary-plan:${scenario}`,
    action_ref: "validate-canary-result",
    route_id: "CA2-ROUTE-VALIDATE",
    objective_kind: "validate",
    effect_classes: ["non-effectful-validate"],
    reversible: true,
    evidence_refs: [`canary:${scenario}`],
    semantic_dependency: {required: true, binding_id: "semantic-domain:wrapper-refund-test@1"},
    next_turn: {params: {threadId, input: [{type: "text", text: "Validate in one sentence that this is a bounded non-authorizing canary result. Do not use tools."}]}},
  };
}

function expected(scenario) {
  if (scenario === "recommended") return {semantic: "RecommendedUnderSnapshot", directive: "direct", successors: 1};
  if (scenario === "insufficient") return {semantic: "Deferred.Insufficient", directive: "block", successors: 0};
  if (scenario === "owner-escalation") return {semantic: "EscalateOwner", directive: "gate", successors: 0};
  if (scenario === "tampered") return {semantic: null, semantic_disposition: "block", directive: "block", successors: 0};
  if (scenario === "disabled") return {semantic_notifications: 0, directive: "direct", successors: 1};
  return {semantic: "RecommendedUnderSnapshot", directive: "gate", successors: 0};
}

async function runMatrix(loaded, semanticProfile, observedVersion) {
  const profile = structuredClone(loaded.value);
  profile.semantic_evaluation = {enabled: true, trigger: "turn/completed"};
  const scenarioStartedAt = new Map();
  const progressByScenario = new Map();
  const scenarioByTurn = new Map();
  const evaluatorCalls = new Map();
  let activeScenario = "matrix";
  const trace = (scenario, stage, details = {}) => {
    const startedAt = scenarioStartedAt.get(scenario) ?? Date.now();
    const event = progress(scenario, stage, {elapsed_ms: Date.now() - startedAt, ...details});
    if (!progressByScenario.has(scenario)) progressByScenario.set(scenario, []);
    progressByScenario.get(scenario).push(event);
  };
  const provider = ({turn_state: turnState}) => {
    const scenario = scenarioByTurn.get(turnState?.turn_id) ?? activeScenario;
    const input = semanticInput();
    if (scenario === "insufficient") input.observation_candidates = input.observation_candidates.filter((candidate) => candidate.field !== "receipt_present");
    if (scenario === "owner-escalation") input.challenge_state.material_disputes = [{dispute_id: "canary-owner", status: "open"}];
    return input;
  };
  const lifecycle = (input) => {
    const scenario = activeScenario;
    evaluatorCalls.set(scenario, (evaluatorCalls.get(scenario) ?? 0) + 1);
    const result = composeSemanticLifecycle(input);
    if (scenario !== "tampered" || !result.ok) return result;
    const reasoningReceipt = {...result.reasoning_receipt, terminal_outcome: "Deferred.Insufficient"};
    return {...result, reasoning_receipt: reasoningReceipt, reasoning_receipt_exact_bytes_digest: digestValue(reasoningReceipt)};
  };
  const wrapper = createCodexAppServerWrapper({
    loaded_profile: profile,
    decision_profile: loaded.decision_profile,
    definition_catalog: loaded.definition_catalog,
    ontology_snapshot: loaded.ontology_snapshot,
    source_snapshot: loaded.source_snapshot,
    context_source_provider: loaded.context_source_provider,
    semantic_profile: semanticProfile,
    semantic_input_provider: provider,
    semantic_lifecycle: lifecycle,
    continuation_provider: ({message}) => {
      const scenario = scenarioByTurn.get(message.params?.turn?.id);
      if (!scenario) return {plan_bound: [], interaction_bound: []};
      const proposal = planProposal(message.params.threadId, scenario);
      if (scenario === "interaction-precedence") {
        return {plan_bound: [proposal], interaction_bound: [{proposal_id: "canary:interaction", attributed_to: "human:canary", proposal_text: "Review before continuing.", evidence_refs: ["canary:interaction"]}]};
      }
      return {plan_bound: [proposal], interaction_bound: []};
    },
  });

  const clientInput = new PassThrough();
  const clientOutput = new PassThrough();
  const clientError = new PassThrough();
  const child = runStdioProxy({wrapper, client_input: clientInput, client_output: clientOutput, client_error: clientError});
  const transportFailure = new EventEmitter();
  let closing = false;
  let stderr = "";
  clientError.on("data", (chunk) => { stderr += chunk; });
  child.on("error", (error) => {
    if (!closing) transportFailure.emit("failure", new AppServerRpcError("rpc.transport-failed", error.message));
  });
  child.on("close", (code, signal) => {
    if (!closing) transportFailure.emit("failure", new AppServerRpcError("rpc.transport-exited", `Wrapped app-server exited: ${signal ?? code}`, {code, signal}));
  });
  const transport = {
    input: clientInput,
    output: clientOutput,
    failure: transportFailure,
    ready: Promise.resolve({kind: "semantic-canary-stdio"}),
    close: async () => {
      if (closing) return;
      closing = true;
      clientInput.end();
      if (child.exitCode === null) child.kill("SIGKILL");
    },
    inspect: () => ({kind: "semantic-canary-stdio", closing, exit_code: child.exitCode, authority_effect: "none"}),
  };
  const rpc = createAppServerRpcClient({transport, request_timeout_ms: REQUEST_TIMEOUT_MS, thread_start_timeout_ms: REQUEST_TIMEOUT_MS, completion_timeout_ms: EVENT_TIMEOUT_MS});
  const messages = [];
  rpc.events.on("notification", (message) => {
    messages.push(message);
    if (["turn/completed", "cyberalchemy/semantic", "cyberalchemy/decision", "cyberalchemy/successor"].includes(message.method)) {
      const turnId = message.params?.turn?.id ?? message.params?.turnId ?? message.params?.reasoning_receipt_binding?.turn_id;
      trace(scenarioByTurn.get(turnId) ?? activeScenario, "notification", {method: message.method, kind: message.params?.kind ?? null});
    }
  });
  const request = async (scenario, method, params) => {
    trace(scenario, "request-start", {method});
    const response = await rpc.request(method, params);
    trace(scenario, "request-complete", {method});
    return response;
  };
  const waitFor = async (scenario, predicate, label) => {
    trace(scenario, "wait-start", {label});
    const message = await rpc.waitForNotification(predicate, {timeout_ms: EVENT_TIMEOUT_MS});
    trace(scenario, "wait-complete", {label});
    return message;
  };
  const seenDecisionDigests = new Set();
  const seenSuccessorResponses = new Set();
  const nextDecision = async (scenario, label) => {
    const message = await waitFor(scenario, (candidate) => candidate.method === "cyberalchemy/decision"
      && candidate.params?.completion_digest
      && !seenDecisionDigests.has(candidate.params.completion_digest), label);
    seenDecisionDigests.add(message.params.completion_digest);
    return message;
  };
  const results = [];
  let matrixError = null;
  try {
    scenarioStartedAt.set("matrix", Date.now());
    await request("matrix", "initialize", {clientInfo: {name: "are-semantic-canary-matrix", version: "0.2.0"}, capabilities: {experimentalApi: true}});
    const started = await request("matrix", "thread/start", {cwd: "/tmp", ephemeral: true, model: "gpt-5.6-sol", approvalPolicy: "never", sandbox: "read-only"});
    for (const scenario of SCENARIOS) {
      activeScenario = scenario;
      profile.semantic_evaluation.enabled = scenario !== "disabled";
      scenarioStartedAt.set(scenario, Date.now());
      trace(scenario, "scenario-start", {request_timeout_ms: REQUEST_TIMEOUT_MS, event_timeout_ms: EVENT_TIMEOUT_MS, shared_thread: true});
      const baseline = messages.length;
      evaluatorCalls.set(scenario, 0);
      try {
        const turn = await request(scenario, "turn/start", {
          threadId: started.thread.id,
          input: [{type: "text", text: "Research whether this exact refund case is eligible. Answer in one sentence and do not use tools."}],
          approvalPolicy: "never",
          sandboxPolicy: {type: "readOnly", networkAccess: false},
        });
        const primaryTurnId = turn.turn.id;
        scenarioByTurn.set(primaryTurnId, scenario);
        await waitFor(scenario, (message) => message.method === "turn/completed" && message.params?.turn?.id === primaryTurnId, `${scenario}:primary-completion`);
        const directive = await nextDecision(scenario, `${scenario}:directive`);
        const scenarioMessages = messages.slice(baseline);
        const semantic = scenarioMessages.find((message) => message.method === "cyberalchemy/semantic") ?? null;
        let successorTurns = 0;
        if (directive.params.directive_kind === "direct") {
          const proposalId = `canary:${scenario}:successor`;
          await waitFor(scenario, (message) => message.method === "cyberalchemy/successor" && message.params?.kind === "started" && message.params?.proposal_id === proposalId, `${scenario}:successor-started`);
          const successorResponse = await waitFor(scenario, (message) => message.method === "cyberalchemy/successor"
            && message.params?.kind === "turn-start-response"
            && !seenSuccessorResponses.has(String(message.params?.rpc_id)), `${scenario}:successor-response`);
          seenSuccessorResponses.add(String(successorResponse.params?.rpc_id));
          const successorTurnId = successorResponse.params.response?.result?.turn?.id;
          if (successorTurnId) {
            await waitFor(scenario, (message) => message.method === "turn/completed" && message.params?.turn?.id === successorTurnId, `${scenario}:successor-completion`);
            await nextDecision(scenario, `${scenario}:successor-directive`);
            successorTurns = 1;
          }
        }
        const exp = expected(scenario);
        const completedMessages = messages.slice(baseline);
        const semanticNotifications = completedMessages.filter((message) => message.method === "cyberalchemy/semantic").length;
        const effectRequests = completedMessages.filter((message) => message.method?.endsWith("/requestApproval")).length;
        const pass = directive.params.directive_kind === exp.directive
          && successorTurns === exp.successors
          && effectRequests === 0
          && (exp.semantic_notifications === undefined || semanticNotifications === exp.semantic_notifications)
          && (exp.semantic_disposition === undefined || semantic?.params?.disposition === exp.semantic_disposition)
          && (exp.semantic === undefined || semantic?.params?.semantic_outcome === exp.semantic);
        results.push({
          scenario,
          status: pass ? "PASS" : "FAIL",
          observed_codex_version: observedVersion,
          thread_id: started.thread.id,
          primary_turn_id: primaryTurnId,
          semantic_disposition: semantic?.params?.disposition ?? "disabled",
          semantic_outcome: semantic?.params?.semantic_outcome ?? null,
          reasoning_receipt_digest: semantic?.params?.reasoning_receipt_digest ?? null,
          journal_cut_digest: semantic?.params?.reasoning_receipt_binding?.runtime_journal_cut_digest ?? null,
          directive_kind: directive.params.directive_kind,
          reason_codes: directive.params.reason_codes,
          successor_turns: successorTurns,
          evaluator_calls: evaluatorCalls.get(scenario) ?? 0,
          effect_requests: effectRequests,
          elapsed_ms: Date.now() - scenarioStartedAt.get(scenario),
          progress: progressByScenario.get(scenario) ?? [],
          authority_effect: "none",
        });
        trace(scenario, pass ? "scenario-pass" : "scenario-assertion-failed", {directive_kind: directive.params.directive_kind});
      } catch (error) {
        const classification = failureClass(error);
        trace(scenario, "scenario-failed", {error_code: error.code ?? "unclassified", failure_class: classification});
        results.push({scenario, status: "FAIL", error: error.message, error_code: error.code ?? null, failure_class: classification, observed_codex_version: observedVersion, elapsed_ms: Date.now() - scenarioStartedAt.get(scenario), progress: progressByScenario.get(scenario) ?? [], authority_effect: "none"});
        if (["app-server-protocol-timeout", "app-server-transport"].includes(classification)) break;
      }
    }
  } catch (error) {
    const classification = failureClass(error);
    trace("matrix", "matrix-failed", {error_code: error.code ?? "unclassified", failure_class: classification});
    matrixError = {error: error.message, error_code: error.code ?? null, failure_class: classification};
  } finally {
    await rpc.close();
  }
  return {results, matrix_error: matrixError, matrix_progress: progressByScenario.get("matrix") ?? [], stderr: stderr.split("\n").filter(Boolean).slice(-20)};
}

const loaded = loadRepositoryProfile(profilePath, repositoryRoot);
if (!loaded.ok) throw new Error(`repository-profile:${loaded.reason_codes.join(",")}`);
const semanticLoaded = loadSemanticInputProfile(semanticProfilePath, repositoryRoot);
if (!semanticLoaded.ok) throw new Error(`semantic-profile:${semanticLoaded.reason_codes.join(",")}`);
let observedVersion = "unavailable";
try {
  observedVersion = execFileSync("codex", ["--version"], {encoding: "utf8"}).trim();
} catch {
  observedVersion = "unavailable";
}
const binding = protocolBindingCheck(loaded.value.protocol_binding, observedVersion);
let results = [];
let matrixError = null;
let matrixProgress = [];
let stderr = [];
if (binding.ok) {
  const matrix = await runMatrix(loaded, semanticLoaded.value, observedVersion);
  results = matrix.results;
  matrixError = matrix.matrix_error;
  matrixProgress = matrix.matrix_progress;
  stderr = matrix.stderr;
}
const completedScenarios = new Set(results.map((item) => item.scenario));
const output = {
  schema_version: "are.codex-semantic-continuation-live-canary/v1",
  status: binding.ok && results.length === SCENARIOS.length && results.every((item) => item.status === "PASS") ? "PASS" : "FAIL",
  observed_codex_version: observedVersion,
  protocol_binding: binding.ok ? "matched" : "blocked-version-drift",
  scenarios: results,
  not_run_scenarios: SCENARIOS.filter((scenario) => !completedScenarios.has(scenario)),
  matrix_error: matrixError,
  matrix_progress: matrixProgress,
  stderr,
  shared_app_server: true,
  shared_thread: true,
  request_timeout_ms: REQUEST_TIMEOUT_MS,
  event_timeout_ms: EVENT_TIMEOUT_MS,
  authority_effect: "none",
  claim_limit: "Controlled ephemeral local canary only; no acceptance, admission, conformance, publication, deployment, or external-effect authority.",
};
process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
process.exitCode = output.status === "PASS" ? 0 : 1;
