import {digestValue, fail, freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";
import {evaluateDualLaneContinuation, normalizeContinuationProposals, projectObjectiveFrontierForTurnStart} from "./continuation.mjs";
import {bindApprovalResponse, evaluateEffectRequest} from "./effect-boundary.mjs";
import {createEvidenceLedger} from "./evidence-ledger.mjs";
import {evaluateTurnPreflight} from "./preflight.mjs";
import {evaluateSemanticCompletion} from "./semantic-completion.mjs";
import {emitCompletionImprovementSignals} from "./evolution-signals.mjs";
import {addIntentLifecycleContext, prepareCodexIntentLifecycle, INTENT_CONTEXT_KEY} from "./intent-lifecycle.mjs";
import {addObjectiveContext, createCodexObjectiveLifecycle, OBJECTIVE_CONTEXT_KEY} from "./objective-lifecycle.mjs";
import {createInteractionLearningLifecycle, addInteractionLearningContext, LEARNING_CONTEXT_KEY} from "./interaction-learning-lifecycle.mjs";
import {deriveReasoningReceiptConstraints} from "./reasoning-receipt-constraints.mjs";
import {
  acquireReasoningStateWriterLock,
  bindCacheTelemetryObservation,
  createReasoningStateLedger,
  createRequestSeriesHeader,
  materializeContextBoundCacheAffinityProjection,
  materializeReasoningDispatch,
  recoverReasoningStateLedger,
  verifyReasoningDispatch,
} from "../../reasoning-state-runtime/index.mjs";
import {composeReasoningEvolution} from "../../reasoning-policy-runtime/index.mjs";
import {extractProviderCacheUsage} from "./cache-telemetry.mjs";
import {createCodexContextWindowTracker} from "./context-window-telemetry.mjs";
import {applyIntentControl, assessIntentRealization, materializeUserControlProfile, projectIntentInspection} from "../../request-intent-runtime/index.mjs";
import {createAlchSemanticModulePort} from "../../module-port/alch-semantic-adapter.mjs";
import {
  admitJsonRpcMessage,
  addContextFragment,
  denyApprovalResult,
  directiveNotification,
  EFFECT_METHODS,
  EVIDENCE_METHODS,
  extractTurnIdentity,
  jsonRpcError,
  PROTOCOL_VERSION,
  semanticNotification,
  successorNotification,
  TURN_COMPLETED,
  TURN_START,
  TURN_STARTED,
} from "./protocol.mjs";

const REGISTER_PLAN = "cyberalchemy/continuation/registerPlan";
const REGISTER_INTERACTION = "cyberalchemy/continuation/registerInteraction";
const INTENT_GET = "cyberalchemy/intent/get";
const INTENT_PROJECT = "cyberalchemy/intent/project";
const INTENT_CONTROL = "cyberalchemy/intent/control";

function response(id, result) {
  return freezeResult({jsonrpc: PROTOCOL_VERSION, id, result});
}

function emptyActions() {
  return {to_server: [], to_client: []};
}

export function createCodexAppServerWrapper(options) {
  if (!isRecord(options)
    || !isRecord(options.loaded_profile)
    || !isRecord(options.decision_profile)) {
    throw new TypeError("A loaded repository profile and verified decision profile are required.");
  }
  const ledger = options.ledger ?? createEvidenceLedger({profile: options.loaded_profile.runtime_journal});
  const modulePort = Object.hasOwn(options, "module_port") ? options.module_port : createAlchSemanticModulePort();
  const contextModulePort = Object.hasOwn(options, "context_module_port") ? options.context_module_port : modulePort;
  const reasoningLedgerId = options.loaded_profile.reasoning_state?.ledger_id ?? `are-reasoning-state:${options.loaded_profile.profile_id}`;
  let reasoningRecovery = null;
  let reasoningLedger = options.reasoning_ledger ?? null;
  let reasoningWriterLock = null;
  let closed = false;
  if (reasoningLedger === null && options.reasoning_sink) {
    reasoningLedger = createReasoningStateLedger({ledger_id: reasoningLedgerId, sink: options.reasoning_sink});
  }
  if (reasoningLedger === null && options.loaded_profile.reasoning_state?.storage_mode === "append-only-file-fsync") {
    if (options.loaded_profile.reasoning_state.single_writer === true) {
      const acquired = acquireReasoningStateWriterLock({
        path: options.loaded_profile.reasoning_state.log_path,
        owner_id: `${reasoningLedgerId}:${process.pid}`,
      });
      if (!acquired.ok) throw new TypeError(`Reasoning state writer lock failed: ${acquired.reason_codes.join(",")}`);
      reasoningWriterLock = acquired.lock;
    }
    const recovered = recoverReasoningStateLedger({
      path: options.loaded_profile.reasoning_state.log_path,
      ledger_id: reasoningLedgerId,
    });
    if (!recovered.ok) {
      reasoningWriterLock?.release();
      throw new TypeError(`Reasoning state recovery failed: ${recovered.reason_codes.join(",")}`);
    }
    reasoningLedger = recovered.ledger;
    reasoningRecovery = recovered.assessment;
  }
  if (reasoningLedger === null) reasoningLedger = createReasoningStateLedger({ledger_id: reasoningLedgerId});
  reasoningRecovery ??= reasoningLedger.inspect().recovery;
  if (reasoningRecovery) {
    ledger.record({
      event_kind: "reasoning-state-recovered",
      direction: "wrapper",
      method: "startup",
      reasoning_state_recovery_digest: reasoningRecovery.recovery_digest,
      recovered_checkpoint_digest: reasoningRecovery.recovered_checkpoint_digest,
      recovered_record_count: reasoningRecovery.record_count,
      authority_effect: "none",
    });
  }
  const pendingApprovals = new Map();
  const currentViews = new Map();
  const proposalsByThread = new Map();
  const completionByThread = new Map();
  const completionByTurn = new Map();
  const pendingTurnStates = new Map();
  const activeTurnStates = new Map();
  const semanticCompletions = new Map();
  const evolutionSignalEmissions = new Map();
  const intentContractsByThread = new Map();
  const intentRealizationsByTurn = new Map();
  const completionFrontiers = new Map();
  const cacheAffinityByConsumer = new Map();
  const reasoningEpochByConsumer = new Map();
  const contextWindowTracker = createCodexContextWindowTracker();
  const internalRequests = new Set();
  let activeDecisionProfile = options.decision_profile;
  let internalSequence = 0;
  let objectiveLifecycle;
  try {
    objectiveLifecycle = createCodexObjectiveLifecycle({ledger: reasoningLedger, profile_id: options.loaded_profile.profile_id,
      configuration: options.loaded_profile.objective_resolution, provider: options.objective_provider,
      requirement_seed_provider: options.requirement_seed_provider, module_port: modulePort});
  } catch (error) { reasoningWriterLock?.release(); throw error; }
  const objectiveTurnsInFlight = new Set();
  const learningEnabled = options.loaded_profile.interaction_learning?.enabled === true;
  let learning;
  try { learning = createInteractionLearningLifecycle({ledger: reasoningLedger,
    configuration: options.loaded_profile.interaction_learning, input_provider: options.interaction_input_provider,
    evolution: options.interaction_evolution});
  } catch (error) {reasoningWriterLock?.release(); throw error;}

  for (const event of reasoningLedger.snapshot()) {
    const consumerRef = event.content?.consumer_ref;
    if (!nonEmptyString(consumerRef)) continue;
    if (event.event_kind === "dispatch-materialized") {
      const persisted = event.content?.cache_affinity_state;
      if (!isRecord(persisted?.projection) || !isRecord(persisted?.assessment) || !isRecord(persisted?.receipt)) continue;
      cacheAffinityByConsumer.set(consumerRef, freezeResult({projection: persisted.projection, assessment: persisted.assessment, receipt: persisted.receipt, authority_effect: "none"}));
      if (typeof persisted.projection.wire_value !== "string") ledger.record({event_kind: "cache-affinity-recovery-miss", direction: "wrapper", method: "startup", reason_code: "cache.recovered-summary-is-not-full-projection"});
      const recoveredEpoch = isRecord(event.content.reasoning_epoch)
        ? event.content.reasoning_epoch
        : reasoningLedger.getEpoch?.(event.content.dispatch?.epoch_digest);
      if (isRecord(recoveredEpoch)) reasoningEpochByConsumer.set(consumerRef, recoveredEpoch);
    } else if (event.event_kind === "cache-telemetry-observed" && isRecord(event.content?.observation)) {
      const current = cacheAffinityByConsumer.get(consumerRef);
      if (current && event.content.observation.projection_digest === current.projection.projection_digest) {
        cacheAffinityByConsumer.set(consumerRef, freezeResult({...current, telemetry: event.content.observation, authority_effect: "none"}));
      }
    }
  }

  function turnKey(threadId, turnId) {
    return `${threadId}:${turnId}`;
  }

  function completionSurface(message) {
    const texts = [];
    const visit = (value) => {
      if (typeof value === "string") texts.push(value);
      else if (Array.isArray(value)) value.forEach(visit);
      else if (isRecord(value)) for (const [key, child] of Object.entries(value)) if (["text", "content", "output", "items"].includes(key)) visit(child);
    };
    visit(message?.params?.turn?.items ?? []);
    return texts.join("\n");
  }

  function completionFrontierKey(threadId, turnId) {
    return `codex-turn:${turnKey(threadId, turnId)}`;
  }

  for (const entry of reasoningLedger.frontiers()) {
    const persisted = entry.frontier.state;
    if (persisted?.schema_version !== "are.codex-completion-frontier-state/v1"
      || !nonEmptyString(persisted.thread_id)
      || !nonEmptyString(persisted.turn_id)
      || entry.frontier.frontier_key !== completionFrontierKey(persisted.thread_id, persisted.turn_id)) continue;
    const key = turnKey(persisted.thread_id, persisted.turn_id);
    completionFrontiers.set(key, entry);
    semanticCompletions.set(key, persisted.semantic_completion);
    if (persisted.evolution_signal_emission) evolutionSignalEmissions.set(key, persisted.evolution_signal_emission);
    if (persisted.intent_realization) intentRealizationsByTurn.set(key, persisted.intent_realization);
    completionByTurn.set(key, persisted.continuation_result);
    completionByThread.set(persisted.thread_id, {completion: persisted.completion, directive: persisted.continuation_result});
  }

  function rememberTurnStart(message, result, reasoning, intentLifecycle = null) {
    const threadId = message.params?.threadId;
    if (!nonEmptyString(threadId) || !Object.hasOwn(message, "id")) return;
    const routeDecision = result.composition?.value?.route_decision;
    if (!isRecord(result.request_context) || !isRecord(routeDecision) || !isRecord(result.context_envelope)) return;
    pendingTurnStates.set(String(message.id), freezeResult({
      schema_version: "are.codex-semantic-turn-state/v1",
      rpc_id: message.id,
      thread_id: threadId,
      request_context: result.request_context,
      route_decision: routeDecision,
      context_envelope: result.context_envelope,
      context_epoch_id: result.context_envelope.value.context_epoch_id,
      context_envelope_digest: result.context_envelope.digest,
      preflight_decision_digest: result.directive.decision_digest,
      reasoning_epoch: reasoning.epoch,
      reasoning_epoch_id: reasoning.epoch.epoch_id,
      reasoning_epoch_digest: reasoning.epoch.epoch_digest,
      reasoning_evolution_disposition: reasoning.reasoning_evolution.disposition,
      reasoning_evolution_result_digest: reasoning.reasoning_evolution.result_digest,
      consumer_ref: reasoning.epoch.consumer_ref,
      reasoning_dispatch_digest: reasoning.dispatch.dispatch_digest,
      reasoning_checkpoint_digest: reasoning.checkpoint.checkpoint_digest,
      intent_contract: intentLifecycle?.intent_contract ?? null,
      intent_contract_digest: intentLifecycle?.intent_contract?.intent_contract_digest ?? null,
      intent_reflection_digest: intentLifecycle?.reflection?.reflection_digest ?? null,
      authority_effect: "none",
    }));
  }

  function checkpointBoundary({checkpoint_kind, event_kind, content, subject_digest, consumer_ref, request_ref}) {
    const appended = reasoningLedger.append({event_kind, content});
    if (!appended.ok) return fail("reasoning-state", appended.reason_codes, appended.residue);
    const sealed = reasoningLedger.seal({
      event_digests: [appended.event.event_digest],
      consumer_ref,
      request_ref,
      frontier: {checkpoint_kind},
    });
    if (!sealed.ok) return fail("reasoning-state", sealed.reason_codes, sealed.residue);
    const checkpoint = reasoningLedger.checkpoint({checkpoint_kind, epoch: sealed.value, subject_digest});
    if (!checkpoint.ok) return fail("reasoning-state", checkpoint.reason_codes, checkpoint.residue);
    return freezeResult({ok: true, epoch: sealed.value, checkpoint: checkpoint.value, authority_effect: "none"});
  }

  function prepareModelDispatch(message, result, binding, intentLifecycle = null) {
    const requestContext = result.request_context;
    const routeDecision = result.composition?.value?.route_decision;
    const envelope = result.context_envelope?.value;
    const requestEvent = reasoningLedger.append({
      event_kind: "request-interpreted",
      content: {
        request_id: requestContext?.request_id ?? String(message.id),
        thread_id: message.params?.threadId ?? null,
        request_context_digest: routeDecision?.request_context_digest ?? null,
        route_id: routeDecision?.selected?.route_id ?? null,
        route_decision_digest: routeDecision?.decision_digest ?? result.directive.decision_digest,
      },
      provenance_refs: requestContext?.evidence_refs ?? [],
    });
    if (!requestEvent.ok) return fail("reasoning-dispatch", requestEvent.reason_codes, requestEvent.residue);
    const contextEvent = reasoningLedger.append({
      event_kind: "context-projected",
      content: {
        context_epoch_id: envelope?.context_epoch_id ?? null,
        context_envelope_digest: result.context_envelope?.digest ?? null,
        selected_dependencies: envelope?.selected_dependencies ?? [],
        exclusions: envelope?.exclusions ?? [],
        contradictions: envelope?.contradictions ?? [],
        gaps: envelope?.gaps ?? [],
        residue: envelope?.residue ?? [],
        freshness_state: envelope?.freshness_state ?? null,
      },
    });
    if (!contextEvent.ok) return fail("reasoning-dispatch", contextEvent.reason_codes, contextEvent.residue);
    let intentEvent = null;
    if (intentLifecycle?.intent_contract) {
      intentEvent = reasoningLedger.append({
        event_kind: intentLifecycle.reflection ? "request-intent-corrected" : "request-intent-compiled",
        idempotency_key: `intent-contract:${intentLifecycle.intent_contract.intent_contract_digest}`,
        content: {
          intent_contract: intentLifecycle.intent_contract,
          reflection: intentLifecycle.reflection,
          inspection_projection_digest: intentLifecycle.inspection?.projection_digest ?? null,
        },
        provenance_refs: [`context-envelope:${result.context_envelope?.digest ?? "unknown"}`],
      });
      if (!intentEvent.ok) return fail("reasoning-dispatch", intentEvent.reason_codes, intentEvent.residue);
    }
    const currentReasoningEpoch = reasoningEpochByConsumer.get(binding.view_key) ?? null;
    const candidateEventDigests = [...new Set([
      ...(currentReasoningEpoch?.event_digests ?? []),
      requestEvent.event.event_digest,
      contextEvent.event.event_digest,
      ...(result.objective_lifecycle?.event_digest ? [result.objective_lifecycle.event_digest] : []),
      ...(intentEvent ? [intentEvent.event.event_digest] : []),
    ])];
    const sealed = reasoningLedger.seal({
      event_digests: candidateEventDigests,
      consumer_ref: binding.view_key,
      request_ref: requestContext?.request_id ?? String(message.id),
      selected_dependencies: envelope?.selected_dependencies ?? [],
      context_envelope_digest: result.context_envelope?.digest ?? null,
      frontier: {kind: "model-request-ready", lane: binding.lane},
    });
    if (!sealed.ok) return fail("reasoning-dispatch", sealed.reason_codes, sealed.residue);
    const evolution = composeReasoningEvolution({
      ledger: reasoningLedger,
      profile: options.loaded_profile.reasoning_policy,
      current_epoch: currentReasoningEpoch,
      candidate_epoch: sealed.value,
      events: reasoningLedger.snapshot(),
      lane: binding.lane,
      refresh_assessment: result.refresh_assessment,
      exploration: message.params?._are?.reasoning?.exploration === true,
      branch_ref: message.params?._are?.reasoning?.branch_ref,
    });
    if (!evolution.ok) return fail("reasoning-evolution", evolution.reason_codes, evolution.residue);
    const selectedEpoch = evolution.epoch;
    const header = createRequestSeriesHeader(result.forwarded_message, options.request_series_header ?? {});
    if (header.ok === false) return fail("reasoning-dispatch", header.reason_codes, header.residue);
    const reusableItems = (envelope?.included_items ?? []).filter((item) => item.item_kind !== "request");
    const volatileItems = (envelope?.included_items ?? []).filter((item) => item.item_kind === "request");
    const selectedDependenciesDigest = digestValue(result.refresh_assessment?.value?.current_selected_dependencies ?? []);
    const cacheAffinity = materializeContextBoundCacheAffinityProjection({
      request_header: header,
      current_reusable_reasoning_state: {
        route_id: routeDecision?.selected?.route_id ?? null,
        capability_ref: routeDecision?.selected?.capability_ref ?? null,
        selected_dependencies_digest: selectedDependenciesDigest,
        selected_dependencies: (envelope?.selected_dependencies ?? []).filter((dependency) => !["request", "selection", "route"].includes(dependency.dependency_kind)),
        included_items: reusableItems,
        exclusions: envelope?.exclusions ?? [],
        contradictions: envelope?.contradictions ?? [],
        gaps: envelope?.gaps ?? [],
        residue: envelope?.residue ?? [],
        claim_ceiling: envelope?.claim_ceiling ?? null,
      },
      volatile_current_turn_suffix: {
        request_id: requestContext?.request_id ?? String(message.id),
        request_context_digest: routeDecision?.request_context_digest ?? null,
        decision_digest: routeDecision?.decision_digest ?? result.directive.decision_digest,
        view_id: result.directive.view_id,
        context_epoch_id: envelope?.context_epoch_id ?? null,
        context_envelope_digest: result.context_envelope?.digest ?? null,
        freshness_state: envelope?.freshness_state ?? null,
        refresh_disposition: result.refresh_assessment?.value?.disposition ?? null,
        request_items: volatileItems,
        intent_contract_digest: intentLifecycle?.intent_contract?.intent_contract_digest ?? null,
      },
      previous_projection: typeof cacheAffinityByConsumer.get(binding.view_key)?.projection?.wire_value === "string"
        ? cacheAffinityByConsumer.get(binding.view_key).projection : null,
      refresh_assessment: result.refresh_assessment,
    });
    if (!cacheAffinity.ok) return fail("reasoning-dispatch", cacheAffinity.reason_codes, cacheAffinity.residue);
    const forwardedMessage = addIntentLifecycleContext(addContextFragment(result.forwarded_message, result.fragment, cacheAffinity), intentLifecycle);
    if (result.objective_lifecycle?.requirement_continuity || result.interaction_learning?.view) {
      const budget = Math.min(options.loaded_profile.context_projection?.max_inline_bytes ?? 32768, 32768);
      // Charge additional semantic input against the existing selected-content
      // budget. Cache projections and envelope metadata repeat that content on
      // the wire and are not what max_inline_bytes measures.
      const extraBytes = [OBJECTIVE_CONTEXT_KEY, INTENT_CONTEXT_KEY, LEARNING_CONTEXT_KEY].reduce((sum, key) =>
        sum + Buffer.byteLength(forwardedMessage.params.additionalContext[key]?.value ?? '', "utf8"), 0);
      const bytes = result.context_envelope.value.inline_bytes + extraBytes;
      if (!Number.isSafeInteger(budget) || budget < 1 || !Number.isSafeInteger(bytes) || bytes > budget) return fail("reasoning-dispatch", ["requirements.shared-context-budget-exceeded"]);
    }
    const dispatch = materializeReasoningDispatch({epoch: selectedEpoch, message: forwardedMessage, request_header: header});
    if (!dispatch.ok) return fail("reasoning-dispatch", dispatch.reason_codes, dispatch.residue);
    const verified = verifyReasoningDispatch(dispatch.value, {epoch: selectedEpoch, message: forwardedMessage});
    if (!verified.ok) return fail("reasoning-dispatch", verified.reason_codes, [verified.verification]);
    const dispatchEvent = reasoningLedger.append({
      event_kind: "dispatch-materialized",
      content: {
        consumer_ref: binding.view_key,
        reasoning_epoch: selectedEpoch,
        reasoning_evolution: evolution.decision,
        reasoning_evolution_result_digest: evolution.result_digest,
        dispatch: dispatch.value,
        verification_digest: verified.value.verification_digest,
        cache_affinity_state: {
          projection: {
            schema_version: cacheAffinity.projection.schema_version,
            projection_digest: cacheAffinity.projection.projection_digest,
            stable_request_prefix: cacheAffinity.projection.stable_request_prefix,
            reusable_reasoning_digest: cacheAffinity.projection.reusable_reasoning_digest,
            exact_prefix_digest: cacheAffinity.projection.exact_prefix_digest,
            exact_reusable_prefix_bytes: cacheAffinity.projection.exact_reusable_prefix_bytes,
            estimated_reusable_tokens: cacheAffinity.projection.estimated_reusable_tokens,
          },
          assessment: cacheAffinity.assessment,
          receipt: cacheAffinity.receipt,
          authority_effect: "none",
        },
      },
      provenance_refs: [
        `reasoning-epoch:${selectedEpoch.epoch_digest}`,
        `context-envelope:${result.context_envelope?.digest ?? "unknown"}`,
      ],
    });
    if (!dispatchEvent.ok) return fail("reasoning-dispatch", dispatchEvent.reason_codes, dispatchEvent.residue);
    const checkpoint = reasoningLedger.checkpoint({checkpoint_kind: "before-model-request", epoch: selectedEpoch, subject_digest: dispatch.value.dispatch_digest});
    if (!checkpoint.ok) return fail("reasoning-dispatch", checkpoint.reason_codes, checkpoint.residue);
    if (learningEnabled) {
      const recorded = learning.dispatch(result.interaction_learning, dispatch.value.dispatch_digest, result.context_envelope.digest, intentLifecycle?.intent_contract);
      if (!recorded.ok) return fail("interaction-learning", recorded.reason_codes);
    }
    cacheAffinityByConsumer.set(binding.view_key, cacheAffinity);
    reasoningEpochByConsumer.set(binding.view_key, selectedEpoch);
    return freezeResult({
      ok: true,
      epoch: selectedEpoch,
      reasoning_evolution: evolution,
      dispatch: dispatch.value,
      verification: verified.value,
      checkpoint: checkpoint.value,
      cache_affinity: cacheAffinity,
      forwarded_message: forwardedMessage,
      authority_effect: "none",
    });
  }

  function bindPendingTurn(rpcId, turnId) {
    const pending = pendingTurnStates.get(String(rpcId));
    if (!pending || !nonEmptyString(turnId)) return null;
    pendingTurnStates.delete(String(rpcId));
    const state = freezeResult({...pending, turn_id: turnId});
    const learningBinding = learning.bind(pending.rpc_id ?? rpcId, state.thread_id, turnId);
    if (!learningBinding.ok) ledger.record({event_kind: "interaction-learning-blocked", direction: "wrapper", reason_codes: learningBinding.reason_codes});
    activeTurnStates.set(turnKey(state.thread_id, turnId), state);
    ledger.record({
      event_kind: "turn-state-bound",
      direction: "wrapper",
      method: TURN_START,
      rpc_id: rpcId,
      thread_id: state.thread_id,
      turn_id: turnId,
      context_epoch_id: state.context_epoch_id,
      context_envelope_digest: state.context_envelope_digest,
      decision_digest: state.preflight_decision_digest,
    });
    return state;
  }

  function recordCacheTelemetry(input = {}) {
    if (!nonEmptyString(input.consumer_ref)) return fail("cache-telemetry", ["cache-telemetry.consumer-ref-required"]);
    const current = cacheAffinityByConsumer.get(input.consumer_ref.trim());
    if (!current) return fail("cache-telemetry", ["cache-telemetry.current-projection-required"]);
    const observed = bindCacheTelemetryObservation({projection: current.projection, assessment: current.assessment, provider_usage: input.provider_usage ?? null});
    if (!observed.ok) return observed;
    const appended = reasoningLedger.append({
      event_kind: "cache-telemetry-observed",
      idempotency_key: `cache-telemetry:${observed.value.observation_digest}`,
      content: {consumer_ref: input.consumer_ref.trim(), observation: observed.value, authority_effect: "none"},
      provenance_refs: [
        `cache-affinity-projection:${current.projection.projection_digest}`,
        `context-bound-reuse-receipt:${current.receipt.receipt_digest}`,
      ],
    });
    if (!appended.ok) return fail("cache-telemetry", appended.reason_codes, appended.residue);
    const telemetryEpoch = reasoningLedger.seal({event_digests: [appended.event.event_digest], consumer_ref: input.consumer_ref.trim(), request_ref: `cache-telemetry:${observed.value.observation_digest}`, frontier: {kind: "cache-telemetry-observed"}});
    if (!telemetryEpoch.ok) return fail("cache-telemetry", telemetryEpoch.reason_codes, telemetryEpoch.residue);
    const telemetryCheckpoint = reasoningLedger.checkpoint({checkpoint_kind: "manual", epoch: telemetryEpoch.value, subject_digest: observed.value.observation_digest});
    if (!telemetryCheckpoint.ok) return fail("cache-telemetry", telemetryCheckpoint.reason_codes, telemetryCheckpoint.residue);
    cacheAffinityByConsumer.set(input.consumer_ref.trim(), freezeResult({...current, telemetry: observed.value, authority_effect: "none"}));
    ledger.record({
      event_kind: "cache-telemetry-observed",
      direction: "wrapper",
      cache_affinity_projection_digest: current.projection.projection_digest,
      cache_affinity_assessment_digest: current.assessment.assessment_digest,
      context_bound_reuse_receipt_digest: current.receipt.receipt_digest,
      cache_telemetry_observation_digest: observed.value.observation_digest,
      cache_hit_posture: observed.value.cache_hit_posture,
      observed_input_tokens: observed.value.observed_input_tokens,
      observed_cached_input_tokens: observed.value.observed_cached_input_tokens,
      observed_token_savings: observed.value.observed_token_savings,
      observed_time_savings_ms: observed.value.observed_time_savings_ms,
    });
    return freezeResult({ok: true, disposition: observed.value.cache_hit_posture, observation: observed.value, authority_effect: "none"});
  }

  function prepareForEviction(input = {}) {
    const blockers = [];
    if (pendingApprovals.size > 0) blockers.push("session.pending-approval");
    if (pendingTurnStates.size > 0) blockers.push("session.pending-turn-start");
    if (activeTurnStates.size > 0) blockers.push("session.active-turn");
    if (internalRequests.size > 0) blockers.push("session.pending-internal-request");
    if (blockers.length > 0) return fail("session-eviction", blockers);
    const reason = nonEmptyString(input.reason) ? input.reason.trim() : "session-lifecycle-expiry";
    const material = freezeResult({schema_version: "are.codex-session-eviction-preparation/v1", reason, consumer_id: input.consumer_id ?? null, lane: input.lane ?? null, authority_effect: "none"});
    const checkpoint = checkpointBoundary({
      checkpoint_kind: "manual",
      event_kind: "session-eviction-prepared",
      content: material,
      subject_digest: digestValue(material),
      consumer_ref: input.consumer_id ?? "codex-session",
      request_ref: `session-eviction:${reason}`,
    });
    if (!checkpoint.ok) return checkpoint;
    return freezeResult({ok: true, disposition: "checkpointed-for-eviction", reason, preparation_digest: digestValue(material), epoch_id: checkpoint.epoch.epoch_id, epoch_digest: checkpoint.epoch.epoch_digest, checkpoint_digest: checkpoint.checkpoint.checkpoint_digest, authority_effect: "none"});
  }

  function bindTurnResponse(message) {
    const turnId = message.result?.turn?.id;
    return bindPendingTurn(message.id, turnId);
  }

  function bindTurnStarted(message) {
    const identity = extractTurnIdentity(message);
    if (!nonEmptyString(identity.thread_id) || !nonEmptyString(identity.turn_id)) return null;
    const matches = [...pendingTurnStates.values()].filter((state) => state.thread_id === identity.thread_id);
    if (matches.length !== 1) return null;
    return bindPendingTurn(matches[0].rpc_id, identity.turn_id);
  }

  function threadProposals(threadId) {
    if (!proposalsByThread.has(threadId)) proposalsByThread.set(threadId, {plan_bound: [], interaction_bound: []});
    return proposalsByThread.get(threadId);
  }

  function resolveTurnBinding(message, override = null) {
    const bindings = options.loaded_profile.turn_bindings ?? {};
    const params = message.params ?? {};
    const explicit = override
      ?? bindings.by_client_message_id?.[params.clientUserMessageId]
      ?? bindings.by_thread_id?.[params.threadId]
      ?? bindings.default;
    if (!isRecord(explicit)) return null;
    const viewKey = explicit.consumer_ref ?? `${explicit.lane}:${params.threadId}`;
    const predecessorState = currentViews.get(viewKey) ?? null;
    return {
      ...explicit,
      view_key: viewKey,
      predecessor_view: predecessorState?.view ?? null,
    };
  }

  async function loadCurrentSources() {
    if (typeof options.context_source_provider !== "function") {
      return {ok: true, decision_profile: activeDecisionProfile, definition_catalog: options.definition_catalog, ontology_snapshot: options.ontology_snapshot, instructions: options.instructions ?? [], supplemental_context_items: options.supplemental_context_items ?? [], source_snapshot: options.source_snapshot ?? [], authority_effect: "none"};
    }
    const current = await options.context_source_provider();
    if (!isRecord(current) || current.ok !== true) return current ?? fail("context-source-refresh", ["context.source-provider-failed"]);
    activeDecisionProfile = current.decision_profile;
    return current;
  }

  async function preflight(message, bindingOverride = null) {
    const binding = resolveTurnBinding(message, bindingOverride);
    if (!binding) return fail("preflight", ["preflight.turn-binding-unresolved"]);
    let selectedSources = null;
    const interaction = learning.prepare(message);
    if (!interaction.ok) return fail("interaction-learning", interaction.reason_codes);
    const objective = await objectiveLifecycle.prepare(message, binding, async () => {
      selectedSources = await loadCurrentSources();
      return selectedSources;
    }, interaction.view ? [{source_ref: `interaction-view:${interaction.view.record_digest}`, content: JSON.stringify(interaction.view)}] : []);
    if (!objective.ok) return freezeResult({ok: false, stage: "objective-resolution", ...objective, authority_effect: "none"});
    if (objective.resolution) ledger.record({event_kind: "objective-transition-resolved", direction: "wrapper", method: TURN_START,
      rpc_id: message.id, thread_id: message.params.threadId, objective_resolution_digest: objective.resolution.resolution_digest,
      objective_state_digest: objective.resolution.next_state.state_digest, objective_transition: objective.resolution.transition});
    const previousState = currentViews.get(binding.view_key) ?? null;
    const current = selectedSources ?? await loadCurrentSources();
    if (!current?.ok) return fail("context-source-refresh", current?.reason_codes ?? ["context.source-refresh-failed"], current?.residue ?? []);
    const result = {...evaluateTurnPreflight({
      message: addInteractionLearningContext(addObjectiveContext(message, objective), interaction),
      objective_resolution: objective.resolution,
      turn_binding: binding,
      decision_profile: current.decision_profile,
      definition_catalog: current.definition_catalog,
      ontology_snapshot: current.ontology_snapshot,
      instructions: current.instructions ?? [],
      supplemental_context_items: current.supplemental_context_items ?? [],
      context: options.loaded_profile.context,
      context_dependencies: binding.context_dependencies ?? options.loaded_profile.context?.dependencies,
      previous_envelope: previousState?.envelope ?? null,
      current_sources: current.source_snapshot ?? [],
      projection_policy: options.loaded_profile.context_projection,
    }, {module_port: modulePort, context_module_port: contextModulePort}), objective_lifecycle: objective, interaction_learning: interaction};
    if (result.ok && result.action === "forward") {
      const view = result.composition.value.context_window_view.value;
      const envelope = result.context_envelope.value;
      currentViews.set(binding.view_key, {view, envelope, selected_dependencies: envelope.selected_dependencies, source_snapshot: envelope.source_snapshot});
      const refresh = result.refresh_assessment;
      ledger.record({
        event_kind: "context-refresh-assessed",
        direction: "wrapper",
        method: TURN_START,
        rpc_id: message.id,
        thread_id: message.params?.threadId ?? null,
        message_digest: digestValue(message),
        refresh_digest: refresh.digest,
        context_epoch_id: envelope.context_epoch_id,
        freshness_state: envelope.freshness_state,
        content_projection_digest: envelope.content_projection_digest,
        projection_reuse_disposition: envelope.projection_reuse_receipt === null ? "assembled" : "reused-exact-content",
        projection_reuse_receipt_digest: envelope.projection_reuse_receipt?.receipt_digest ?? null,
        selected_change_count: refresh.value.changed_selected_dependencies.length,
        unrelated_drift_count: refresh.value.unrelated_source_drift.length,
      });
      ledger.record({
        event_kind: "context-envelope-created",
        direction: "wrapper",
        method: TURN_START,
        rpc_id: message.id,
        thread_id: message.params?.threadId ?? null,
        context_epoch_id: envelope.context_epoch_id,
        context_envelope_digest: result.context_envelope.digest,
        inline_bytes: envelope.inline_bytes,
        freshness_state: envelope.freshness_state,
        content_projection_digest: envelope.content_projection_digest,
        projection_reuse_disposition: envelope.projection_reuse_receipt === null ? "assembled" : "reused-exact-content",
        projection_reuse_receipt_digest: envelope.projection_reuse_receipt?.receipt_digest ?? null,
      });
    }
    return result;
  }

  async function effectMetadata(message) {
    if (typeof options.effect_metadata_provider === "function") return await options.effect_metadata_provider(message);
    return options.loaded_profile.effect_defaults?.[message.method] ?? null;
  }

  function registerProposal(message, lane) {
    const params = isRecord(message.params) ? message.params : {};
    if (!nonEmptyString(params.threadId) || !isRecord(params.proposal)) {
      return {error: jsonRpcError(message.id, -32602, "Invalid continuation proposal", {reason_codes: ["proposal.thread-and-value-required"]})};
    }
    const bucket = threadProposals(params.threadId);
    bucket[lane].push(params.proposal);
    const event = ledger.record({
      event_kind: lane === "plan_bound" ? "plan-proposal-registered" : "interaction-proposal-registered",
      direction: "client-to-wrapper",
      method: message.method,
      rpc_id: message.id,
      thread_id: params.threadId,
      message_digest: digestValue(message),
    });
    return {response: response(message.id, {registered: true, lane, event_digest: event.event_digest, authority_effect: "none"})};
  }

  async function processClientMessage(message) {
    const admitted = admitJsonRpcMessage(message);
    if (!admitted.ok) return {...emptyActions(), to_client: [jsonRpcError(message?.id, -32600, "Invalid JSON-RPC message", admitted)]};

    if (message.method === REGISTER_PLAN) {
      const registered = registerProposal(message, "plan_bound");
      return {...emptyActions(), to_client: [registered.response ?? registered.error]};
    }
    if (message.method === REGISTER_INTERACTION) {
      const registered = registerProposal(message, "interaction_bound");
      return {...emptyActions(), to_client: [registered.response ?? registered.error]};
    }
    if ([INTENT_GET, INTENT_PROJECT, INTENT_CONTROL].includes(message.method)) {
      const threadId = message.params?.threadId;
      const contract = nonEmptyString(threadId) ? intentContractsByThread.get(threadId) : null;
      if (!contract) return {...emptyActions(), to_client: [jsonRpcError(message.id, -32077, "Intent Contract not found", {reason_codes: ["intent.contract-not-found"]})]};
      if (message.method === INTENT_GET) return {...emptyActions(), to_client: [response(message.id, {intent_contract: contract, authority_effect: "none"})]};
      if (message.method === INTENT_PROJECT) {
        let profile;
        try { profile = materializeUserControlProfile({...options.loaded_profile.intent_compilation?.control_profile, visibility: message.params?.mode ?? options.loaded_profile.intent_compilation?.control_profile?.visibility}); }
        catch { return {...emptyActions(), to_client: [jsonRpcError(message.id, -32602, "Invalid intent projection", {reason_codes: ["intent.projection-invalid"]})]}; }
        const projection = projectIntentInspection({contract, control_profile: profile, mode: message.params?.mode});
        return {...emptyActions(), to_client: [projection.ok ? response(message.id, projection.value) : jsonRpcError(message.id, -32602, "Invalid intent projection", projection)]};
      }
      const controlled = applyIntentControl(contract, message.params?.operation);
      if (!controlled.ok) return {...emptyActions(), to_client: [jsonRpcError(message.id, -32602, "Invalid intent control operation", controlled)]};
      intentContractsByThread.set(threadId, controlled.value.successor);
      reasoningLedger.append({event_kind: "intent-contract-controlled", idempotency_key: `intent-control:${controlled.value.receipt.control_receipt_digest}`, content: controlled.value});
      ledger.record({event_kind: "intent-contract-controlled", direction: "wrapper", method: INTENT_CONTROL, thread_id: threadId, intent_contract_digest: controlled.value.successor.intent_contract_digest, control_receipt_digest: controlled.value.receipt.control_receipt_digest});
      return {...emptyActions(), to_client: [response(message.id, controlled.value)]};
    }

    if (admitted.kind === "response" && pendingApprovals.has(String(message.id))) {
      const pending = pendingApprovals.get(String(message.id));
      const bound = bindApprovalResponse({pending, response: message});
      if (!bound.ok) {
        return {...emptyActions(), to_client: [jsonRpcError(message.id, -32073, "Approval binding failed", bound)]};
      }
      if (bound.accepted) {
        const barrier = checkpointBoundary({
          checkpoint_kind: "before-effect",
          event_kind: "effect-approval-bound",
          content: {
            rpc_id: message.id,
            thread_id: pending.thread_id,
            turn_id: pending.turn_id,
            item_id: pending.item_id,
            effect_digest: pending.effect_digest,
            decision_digest: pending.decision_digest,
            binding_digest: bound.binding?.binding_digest ?? null,
          },
          subject_digest: bound.binding?.binding_digest ?? pending.effect_digest,
          consumer_ref: `codex-effect:${pending.thread_id}:${pending.turn_id}`,
          request_ref: `effect:${pending.effect_digest}`,
        });
        if (!barrier.ok) return {...emptyActions(), to_client: [jsonRpcError(message.id, -32074, "Reasoning-state effect checkpoint failed", barrier)]};
        ledger.record({
          event_kind: "reasoning-state-checkpoint",
          direction: "wrapper",
          method: pending.method,
          rpc_id: message.id,
          thread_id: pending.thread_id,
          turn_id: pending.turn_id,
          item_id: pending.item_id,
          effect_digest: pending.effect_digest,
          reasoning_epoch_id: barrier.epoch.epoch_id,
          reasoning_epoch_digest: barrier.epoch.epoch_digest,
          checkpoint_digest: barrier.checkpoint.checkpoint_digest,
          checkpoint_kind: "before-effect",
        });
      }
      pendingApprovals.delete(String(message.id));
      ledger.record({
        event_kind: "approval-response-forwarded",
        direction: "client-to-server",
        method: pending.method,
        rpc_id: message.id,
        thread_id: pending.thread_id,
        turn_id: pending.turn_id,
        item_id: pending.item_id,
        message_digest: digestValue(message),
        effect_digest: pending.effect_digest,
        binding_digest: bound.binding?.binding_digest ?? null,
      });
      return {...emptyActions(), to_server: [message]};
    }

    if (message.method !== TURN_START) return {...emptyActions(), to_server: [message]};
    const threadId = message.params?.threadId;
    const effectiveMessage = projectObjectiveFrontierForTurnStart(message, completionByThread.get(threadId)?.directive ?? null);
    const result = await preflight(effectiveMessage);
    if (!result.ok) {
      return {...emptyActions(), to_client: [jsonRpcError(message.id, -32070, "ARE preflight failed", result)]};
    }
    ledger.record({
      event_kind: "preflight-decision",
      direction: "wrapper",
      method: TURN_START,
      rpc_id: message.id,
      thread_id: threadId,
      message_digest: digestValue(effectiveMessage),
      decision_digest: result.directive.decision_digest,
    });
    if (result.action !== "forward") {
      return {...emptyActions(), to_client: [jsonRpcError(message.id, result.action === "gate" ? -32071 : -32072, `ARE preflight ${result.action}`, result.directive)]};
    }
    const binding = resolveTurnBinding(effectiveMessage);
    const intentLifecycle = await prepareCodexIntentLifecycle({
      configuration: learningEnabled ? {...options.loaded_profile.intent_compilation, enabled: true} : options.loaded_profile.intent_compilation,
      objective_resolution: result.objective_lifecycle?.resolution,
      message: effectiveMessage,
      request_ref: `codex-rpc:${message.id}`,
      context_envelope_digest: result.context_envelope?.digest,
      reasoning_epoch_digest: reasoningEpochByConsumer.get(binding.view_key)?.epoch_digest ?? null,
      route_candidate: result.composition?.value?.route_decision?.selected?.route_id ?? null,
      source_refs: result.context_envelope?.value?.selected_dependencies?.map((entry) => `${entry.source_identity}:${entry.source_digest}`) ?? [],
      previous_contract: intentContractsByThread.get(threadId) ?? null,
      intent_provider: learningEnabled ? undefined : options.intent_provider,
      correction_provider: learningEnabled ? undefined : options.correction_provider,
    });
    if (!intentLifecycle.ok) {
      return {...emptyActions(), to_client: [jsonRpcError(message.id, -32076, "Request intent compilation failed", intentLifecycle)]};
    }
    const reasoning = prepareModelDispatch(effectiveMessage, result, binding, intentLifecycle);
    if (!reasoning.ok) {
      return {...emptyActions(), to_client: [jsonRpcError(message.id, -32075, "Reasoning-state dispatch preparation failed", reasoning)]};
    }
    ledger.record({
      event_kind: "reasoning-dispatch-verified",
      direction: "wrapper",
      method: TURN_START,
      rpc_id: message.id,
      thread_id: threadId,
      message_digest: reasoning.dispatch.message_digest,
      reasoning_epoch_id: reasoning.epoch.epoch_id,
      reasoning_epoch_digest: reasoning.epoch.epoch_digest,
      checkpoint_digest: reasoning.checkpoint.checkpoint_digest,
      checkpoint_kind: "before-model-request",
      dispatch_digest: reasoning.dispatch.dispatch_digest,
      dispatch_verification_digest: reasoning.verification.verification_digest,
      request_header_digest: reasoning.dispatch.request_header_digest,
      cache_affinity_projection_digest: reasoning.cache_affinity.projection.projection_digest,
      cache_affinity_assessment_digest: reasoning.cache_affinity.assessment.assessment_digest,
      context_bound_reuse_receipt_digest: reasoning.cache_affinity.receipt.receipt_digest,
      cache_affinity_posture: reasoning.cache_affinity.assessment.posture,
      exact_prefix_reuse: reasoning.cache_affinity.assessment.exact_prefix_reuse,
      reusable_prefix_bytes: reasoning.cache_affinity.assessment.reusable_prefix_bytes,
      reused_prefix_bytes: reasoning.cache_affinity.assessment.reused_prefix_bytes,
      cache_hit_posture: reasoning.cache_affinity.assessment.cache_hit_posture,
      estimated_reused_tokens: reasoning.cache_affinity.assessment.estimated_reused_tokens,
      observed_time_savings_ms: reasoning.cache_affinity.assessment.observed_time_savings_ms,
      observed_token_savings: reasoning.cache_affinity.assessment.observed_token_savings,
      cache_invalidation_reasons: reasoning.cache_affinity.assessment.invalidation_reasons,
      intent_contract_digest: intentLifecycle.intent_contract?.intent_contract_digest ?? null,
      intent_reflection_digest: intentLifecycle.reflection?.reflection_digest ?? null,
    });
    if (intentLifecycle.intent_contract) {
      intentContractsByThread.set(threadId, intentLifecycle.intent_contract);
      ledger.record({
        event_kind: intentLifecycle.reflection ? "request-intent-corrected" : "request-intent-compiled",
        direction: "wrapper",
        method: TURN_START,
        rpc_id: message.id,
        thread_id: threadId,
        intent_contract_digest: intentLifecycle.intent_contract.intent_contract_digest,
        intent_reflection_digest: intentLifecycle.reflection?.reflection_digest ?? null,
        inspection_projection_digest: intentLifecycle.inspection?.projection_digest ?? null,
      });
    }
    ledger.record({
      event_kind: "turn-start-forwarded",
      direction: "client-to-server",
      method: TURN_START,
      rpc_id: message.id,
      thread_id: threadId,
      message_digest: digestValue(reasoning.forwarded_message),
      decision_digest: result.directive.decision_digest,
    });
    rememberTurnStart(effectiveMessage, result, reasoning, intentLifecycle);
    return {...emptyActions(), to_server: [reasoning.forwarded_message]};
  }

  async function assessSemanticCompletion(message) {
    const identity = extractTurnIdentity(message);
    const key = turnKey(identity.thread_id, identity.turn_id);
    if (semanticCompletions.has(key)) return semanticCompletions.get(key);
    const state = activeTurnStates.get(key) ?? null;
    const journalCut = ledger.cut({thread_id: identity.thread_id, turn_id: identity.turn_id});
    const result = await evaluateSemanticCompletion({
      configuration: options.loaded_profile.semantic_evaluation,
      semantic_profile: options.semantic_profile,
      turn_state: state,
      completion_message: message,
      semantic_input_provider: options.semantic_input_provider,
      semantic_lifecycle: options.semantic_lifecycle,
      runtime_journal_cut: journalCut.ok ? journalCut.value : null,
    });
    semanticCompletions.set(key, result);
    activeTurnStates.delete(key);
    return result;
  }

  async function emitEvolutionSignals(message, turnState, semantic, continuation, completionDigest) {
    const identity = extractTurnIdentity(message);
    const key = turnKey(identity.thread_id, identity.turn_id);
    if (evolutionSignalEmissions.has(key)) return evolutionSignalEmissions.get(key);
    const result = await emitCompletionImprovementSignals({
      configuration: options.loaded_profile.evolution_signals,
      completion_message: message,
      completion_digest: completionDigest,
      turn_state: turnState,
      semantic_completion: semantic,
      continuation_result: continuation,
      signal_provider: options.evolution_signal_provider,
      signal_sink: options.evolution_signal_sink,
    });
    evolutionSignalEmissions.set(key, result);
    return result;
  }

  async function assessCompletion(message, semantic) {
    const params = message.params ?? {};
    const turn = params.turn ?? {};
    const threadId = params.threadId;
    const turnId = turn.id;
    const key = turnKey(threadId, turnId);
    if (completionByTurn.has(key)) {
      const cut = ledger.cut({thread_id: threadId, turn_id: turnId});
      const replay = cut.ok ? ledger.replay(cut.value) : cut;
      if (!replay.ok || replay.value.continuation_decision_count !== 1) return fail("continuation-replay", ["continuation.journal-cache-disagreement"]);
      return completionByTurn.get(key);
    }
    const registered = threadProposals(threadId);
    let provided = {plan_bound: [], interaction_bound: []};
    if (typeof options.continuation_provider === "function") {
      provided = await options.continuation_provider({message, evidence: ledger.snapshot(), registered}) ?? provided;
    }
    const plan = [...registered.plan_bound, ...(provided.plan_bound ?? [])];
    const interaction = [...registered.interaction_bound, ...(provided.interaction_bound ?? [])];
    const objectiveFrontier = provided.objective_frontier ?? null;
    const continuationRequired = objectiveFrontier
      ? objectiveFrontier.state !== "complete"
      : plan.length > 0 || interaction.length > 0 || provided.continuation_required === true;
    const completion = {
      completion_id: `codex-turn:${turnId}`,
      status: turn.status === "completed" ? "completed" : turn.status,
      continuation_required: continuationRequired,
      evidence_refs: [
        ...ledger.snapshot().filter((event) => event.thread_id === threadId && (!event.turn_id || event.turn_id === turnId)).map((event) => `event:${event.event_digest}`),
        ...(Array.isArray(objectiveFrontier?.evidence_refs) ? objectiveFrontier.evidence_refs : []),
      ],
    };
    const normalized = normalizeContinuationProposals({plan_bound: plan, interaction_bound: interaction});
    const semanticConstraints = deriveReasoningReceiptConstraints({
      semantic_completion: semantic,
      turn_identity: {thread_id: threadId, turn_id: turnId},
      plan_bound: normalized.ok ? normalized.plan_bound : [],
    });
    if (semanticConstraints.proposal_constraints.length > 0) {
      ledger.record({
        event_kind: "reasoning-receipt-constraints-derived",
        direction: "wrapper",
        method: TURN_COMPLETED,
        thread_id: threadId,
        turn_id: turnId,
        constraint_digest: semanticConstraints.constraint_digest,
        constraint_disposition: semanticConstraints.disposition,
        semantic_outcome: semanticConstraints.semantic_outcome,
        reasoning_receipt_digest: semanticConstraints.reasoning_receipt_digest,
        constrained_proposal_count: semanticConstraints.proposal_constraints.length,
      });
    }
    const result = evaluateDualLaneContinuation({completion, plan_bound: plan, interaction_bound: interaction, normalized_proposals: normalized, objective_frontier: objectiveFrontier, semantic_constraints: semanticConstraints}, activeDecisionProfile);
    proposalsByThread.delete(threadId);
    completionByThread.set(threadId, {completion, directive: result});
    completionByTurn.set(key, result);
    return result;
  }

  function successorBinding(proposal) {
    const base = options.loaded_profile.turn_bindings?.plan_successor ?? {};
    return {
      ...base,
      lane: "plan-bound",
      consumer_ref: base.consumer_ref ?? `codex-plan:${proposal.declared_plan_digest}`,
      window_ref: base.window_ref ?? `plan:${proposal.declared_plan_digest}`,
      purpose: base.purpose ?? proposal.action_ref,
      source_epoch: base.source_epoch ?? options.loaded_profile.context.source_epoch,
      objective_kind: proposal.objective_kind,
      requested_effects: proposal.effect_classes,
      evidence_refs: [...(proposal.evidence_refs ?? []), `plan:${proposal.declared_plan_digest}`, `proposal:${proposal.proposal_digest}`],
    };
  }

  async function processServerMessage(message) {
    const admitted = admitJsonRpcMessage(message);
    if (!admitted.ok) return {...emptyActions(), to_client: [jsonRpcError(message?.id, -32600, "Invalid app-server JSON-RPC message", admitted)]};

    learning.observe(message);
    const contextWindowObservation = contextWindowTracker.observe(message);
    if (contextWindowObservation.ok && contextWindowObservation.disposition === "observed") {
      const observation = contextWindowObservation.observation;
      ledger.record({
        event_kind: observation.event_kind,
        direction: "server-to-client",
        method: observation.method,
        thread_id: observation.thread_id,
        turn_id: observation.turn_id,
        item_id: observation.item_id,
        observation_digest: observation.observation_digest,
        token_usage: observation.token_usage,
        observed_last_total_to_model_window_ratio: observation.observed_last_total_to_model_window_ratio,
      });
    } else if (!contextWindowObservation.ok) {
      ledger.record({event_kind: "context-window-telemetry-rejected", direction: "wrapper", method: message.method, reason_codes: contextWindowObservation.reason_codes});
    } else if (contextWindowObservation.disposition === "duplicate") {
      ledger.record({event_kind: "context-window-telemetry-duplicate", direction: "wrapper", method: message.method, observation_digest: contextWindowObservation.observation_digest});
    }

    const boundTurnState = admitted.kind === "response" ? bindTurnResponse(message) : null;
    if (boundTurnState?.consumer_ref) {
      const current = cacheAffinityByConsumer.get(boundTurnState.consumer_ref);
      const extracted = extractProviderCacheUsage(message, current?.projection, options.loaded_profile.cache_telemetry);
      if (extracted.ok && extracted.disposition === "observed") recordCacheTelemetry({consumer_ref: boundTurnState.consumer_ref, provider_usage: extracted.provider_usage});
      else if (!extracted.ok) ledger.record({event_kind: "cache-telemetry-rejected", direction: "wrapper", rpc_id: message.id, cache_invalidation_reasons: extracted.reason_codes});
    }

    if (admitted.kind === "response" && internalRequests.has(String(message.id))) {
      internalRequests.delete(String(message.id));
      return {...emptyActions(), to_client: [successorNotification({kind: "turn-start-response", rpc_id: message.id, response: message, authority_effect: "none"})]};
    }

    if (admitted.kind === "request" && EFFECT_METHODS.includes(message.method)) {
      const metadata = await effectMetadata(message);
      const evaluated = evaluateEffectRequest({message, effect_metadata: metadata, decision_profile: activeDecisionProfile});
      if (!evaluated.ok) return {...emptyActions(), to_server: [{jsonrpc: PROTOCOL_VERSION, id: message.id, result: denyApprovalResult(message.method)}], to_client: [directiveNotification(evaluated)]};
      const directive = evaluated.value;
      ledger.record({
        event_kind: "effect-decision",
        direction: "wrapper",
        method: message.method,
        rpc_id: message.id,
        thread_id: directive.thread_id,
        turn_id: directive.turn_id,
        item_id: directive.item_id,
        message_digest: digestValue(message),
        decision_digest: directive.decision_digest,
        effect_digest: directive.effect_digest,
      });
      if (directive.directive_kind === "block") {
        const denial = {jsonrpc: PROTOCOL_VERSION, id: message.id, result: evaluated.deny_result};
        ledger.record({event_kind: "approval-response-forwarded", direction: "wrapper-to-server", method: message.method, rpc_id: message.id, thread_id: directive.thread_id, turn_id: directive.turn_id, item_id: directive.item_id, message_digest: digestValue(denial), decision_digest: directive.decision_digest, effect_digest: directive.effect_digest});
        return {...emptyActions(), to_server: [denial], to_client: [directiveNotification(directive)]};
      }
      pendingApprovals.set(String(message.id), directive);
      return {...emptyActions(), to_client: directive.directive_kind === "gate" ? [message, directiveNotification(directive)] : [message]};
    }

    if (admitted.kind === "notification" && EVIDENCE_METHODS.includes(message.method)) {
      if (message.method === TURN_STARTED) bindTurnStarted(message);
      const identity = extractTurnIdentity(message);
      ledger.record({
        event_kind: message.method === TURN_COMPLETED ? "turn-completed-observed" : "lifecycle-observed",
        direction: "server-to-client",
        method: message.method,
        thread_id: identity.thread_id,
        turn_id: identity.turn_id,
        item_id: identity.item_id,
        message_digest: admitted.message_digest,
      });
      if (message.method === TURN_COMPLETED) {
        const learningCompletion = learning.complete(message);
        if (!learningCompletion.ok) ledger.record({event_kind: "interaction-learning-rejected", direction: "wrapper", method: TURN_COMPLETED, reason_codes: learningCompletion.reason_codes});
        const completionKey = turnKey(identity.thread_id, identity.turn_id);
        const recoveredFrontier = completionFrontiers.get(completionKey);
        if (recoveredFrontier) {
          if (recoveredFrontier.frontier.subject_digest !== admitted.message_digest) {
            const mismatch = fail("completion-frontier-replay", ["reasoning.frontier-subject-mismatch"]);
            return {...emptyActions(), to_client: [message, directiveNotification(mismatch)]};
          }
          const persisted = recoveredFrontier.frontier.state;
          const persistedSemantic = persisted.semantic_completion;
          const persistedContinuation = persisted.continuation_result;
          const persistedDirective = persistedContinuation.ok ? persistedContinuation.value : persistedContinuation;
          ledger.record({event_kind: "reasoning-frontier-replayed", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, message_digest: admitted.message_digest, decision_digest: persisted.decision_digest, replay_digest: recoveredFrontier.frontier.frontier_digest});
          return {
            ...emptyActions(),
            to_client: [
              message,
              ...(persistedSemantic.notify ? [semanticNotification(persistedSemantic)] : []),
              directiveNotification(persistedDirective),
              successorNotification({kind: "replayed", turn_id: identity.turn_id, replay_digest: recoveredFrontier.frontier.frontier_digest, authority_effect: "none"}),
            ],
          };
        }
        const completionTurnState = activeTurnStates.get(completionKey) ?? null;
        const replayedCompletion = completionByTurn.has(completionKey);
        let intentRealization = null;
        if (completionTurnState?.intent_contract) {
          const surface = completionSurface(message);
          if (surface) {
            const assessed = assessIntentRealization(completionTurnState.intent_contract, {surface_text: surface});
            if (assessed.ok) {
              intentRealization = assessed.value;
              intentRealizationsByTurn.set(completionKey, intentRealization);
              ledger.record({event_kind: "intent-realization-assessed", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, intent_contract_digest: completionTurnState.intent_contract_digest, intent_realization_digest: intentRealization.assessment_digest, intent_realization_disposition: intentRealization.disposition});
            }
          }
        }
        const semantic = await assessSemanticCompletion(message);
        if (semantic.notify) {
          ledger.record({
            event_kind: semantic.disposition === "evaluated" ? "semantic-evaluation-completed" : `semantic-evaluation-${semantic.disposition}`,
            direction: "wrapper",
            method: TURN_COMPLETED,
            thread_id: identity.thread_id,
            turn_id: identity.turn_id,
            message_digest: admitted.message_digest,
            semantic_disposition: semantic.disposition,
            semantic_materialization_id: semantic.semantic_materialization_id,
            semantic_outcome: semantic.semantic_outcome,
            reasoning_receipt_digest: semantic.reasoning_receipt_digest,
            evaluator_calls: semantic.evaluator_calls,
            journal_cut_digest: semantic.reasoning_receipt_binding?.runtime_journal_cut_digest ?? null,
          });
        }
        const continuation = await assessCompletion(message, semantic);
        const directive = continuation.ok ? continuation.value : continuation;
        ledger.record({event_kind: "continuation-decision", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, message_digest: admitted.message_digest, decision_digest: directive.decision_digest ?? digestValue(directive)});
        const evolutionSignalEmission = await emitEvolutionSignals(message, completionTurnState, semantic, continuation, admitted.message_digest);
        if (evolutionSignalEmission.disposition !== "disabled" && evolutionSignalEmission.disposition !== "no-signals") {
          ledger.record({
            event_kind: "evolution-signals-assessed",
            direction: "wrapper",
            method: TURN_COMPLETED,
            thread_id: identity.thread_id,
            turn_id: identity.turn_id,
            message_digest: admitted.message_digest,
            signal_disposition: evolutionSignalEmission.disposition,
            signal_count: evolutionSignalEmission.signal_count,
            provider_calls: evolutionSignalEmission.provider_calls,
            sink_calls: evolutionSignalEmission.sink_calls,
            signal_refs: evolutionSignalEmission.signal_refs,
          });
        }
        const completionRecord = completionByThread.get(identity.thread_id)?.completion ?? {
          completion_id: `codex-turn:${identity.turn_id}`,
          status: message.params?.turn?.status ?? null,
          continuation_required: false,
          evidence_refs: [],
        };
        const completionFrontier = reasoningLedger.sealFrontier({
          frontier_key: completionFrontierKey(identity.thread_id, identity.turn_id),
          subject_digest: admitted.message_digest,
          consumer_ref: `codex-completion:${identity.thread_id}`,
          request_ref: `turn:${identity.turn_id}`,
          context_envelope_digest: completionTurnState?.context_envelope_digest ?? null,
          prior_reasoning_epoch_digest: completionTurnState?.reasoning_epoch_digest ?? null,
          provenance_refs: [
            `completion:${admitted.message_digest}`,
            ...(semantic.reasoning_receipt_digest ? [`reasoning-receipt:${semantic.reasoning_receipt_digest}`] : []),
            ...(directive.decision_digest ? [`continuation-decision:${directive.decision_digest}`] : []),
          ],
          state: {
            schema_version: "are.codex-completion-frontier-state/v1",
            thread_id: identity.thread_id,
            turn_id: identity.turn_id,
            completion_message_digest: admitted.message_digest,
            completion: completionRecord,
            semantic_completion: semantic,
            evolution_signal_emission: evolutionSignalEmission,
            intent_realization: intentRealization,
            continuation_result: continuation,
            decision_digest: directive.decision_digest ?? digestValue(directive),
            selected_proposal_digest: continuation.selected_proposal?.proposal_digest ?? null,
            automatic_successor_posture: continuation.ok && directive.directive_kind === "direct" && continuation.selected_proposal
              ? "committed-at-most-once-no-retry-after-recovery"
              : "not-applicable",
            authority_effect: "none",
          },
        });
        if (!completionFrontier.ok) {
          const stopped = fail("completion-frontier", completionFrontier.reason_codes, completionFrontier.residue);
          return {...emptyActions(), to_client: [message, ...(semantic.notify ? [semanticNotification(semantic)] : []), directiveNotification(stopped)]};
        }
        completionFrontiers.set(completionKey, completionFrontier);
        ledger.record({
          event_kind: "reasoning-state-checkpoint",
          direction: "wrapper",
          method: TURN_COMPLETED,
          thread_id: identity.thread_id,
          turn_id: identity.turn_id,
          reasoning_epoch_id: completionFrontier.epoch.epoch_id,
          reasoning_epoch_digest: completionFrontier.epoch.epoch_digest,
          checkpoint_digest: completionFrontier.checkpoint.checkpoint_digest,
          checkpoint_kind: "after-turn-completion",
          decision_digest: directive.decision_digest ?? digestValue(directive),
        });
        const actions = {...emptyActions(), to_client: [message, ...(semantic.notify ? [semanticNotification(semantic)] : []), directiveNotification(directive)]};
        if (!replayedCompletion && continuation.ok && directive.directive_kind === "direct" && continuation.selected_proposal) {
          const proposal = continuation.selected_proposal;
          const continuationBarrier = checkpointBoundary({
            checkpoint_kind: "before-continuation",
            event_kind: "continuation-selected",
            content: {
              thread_id: identity.thread_id,
              turn_id: identity.turn_id,
              decision_digest: directive.decision_digest,
              proposal_id: proposal.proposal_id,
              proposal_digest: proposal.proposal_digest,
            },
            subject_digest: proposal.proposal_digest,
            consumer_ref: `codex-continuation:${identity.thread_id}`,
            request_ref: `turn:${identity.turn_id}`,
          });
          if (!continuationBarrier.ok) {
            actions.to_client.push(successorNotification({kind: "stopped", proposal_id: proposal.proposal_id, checkpoint: continuationBarrier, authority_effect: "none"}));
            ledger.record({event_kind: "successor-stopped", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest, successor_proposal_id: proposal.proposal_id});
            ledger.record({event_kind: "turn-closed", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest ?? digestValue(directive)});
            ledger.evict();
            return actions;
          }
          ledger.record({
            event_kind: "reasoning-state-checkpoint",
            direction: "wrapper",
            method: TURN_COMPLETED,
            thread_id: identity.thread_id,
            turn_id: identity.turn_id,
            reasoning_epoch_id: continuationBarrier.epoch.epoch_id,
            reasoning_epoch_digest: continuationBarrier.epoch.epoch_digest,
            checkpoint_digest: continuationBarrier.checkpoint.checkpoint_digest,
            checkpoint_kind: "before-continuation",
            successor_proposal_id: proposal.proposal_id,
          });
          internalSequence += 1;
          const nextMessage = freezeResult({jsonrpc: PROTOCOL_VERSION, id: `ca2-successor-${internalSequence}`, method: TURN_START, params: proposal.next_turn.params});
          const successorThread = learningEnabled ? "learning-product" : nextMessage.params.threadId;
          let preflightResult;
          if ((learningEnabled || options.loaded_profile.objective_resolution?.enabled === true) && objectiveTurnsInFlight.has(successorThread)) {
            preflightResult = fail("objective-resolution", ["objective.concurrent-turn-in-progress"]);
          } else {
            if (learningEnabled || options.loaded_profile.objective_resolution?.enabled === true) objectiveTurnsInFlight.add(successorThread);
            try { preflightResult = await preflight(nextMessage, successorBinding(proposal)); }
            finally { objectiveTurnsInFlight.delete(successorThread); }
          }
          if (preflightResult.ok && preflightResult.action === "forward") {
            const successorIntent = await prepareCodexIntentLifecycle({
              configuration: learningEnabled ? {...options.loaded_profile.intent_compilation, enabled: true} : options.loaded_profile.intent_compilation,
              objective_resolution: preflightResult.objective_lifecycle?.resolution, message: nextMessage,
              request_ref: `codex-rpc:${nextMessage.id}`, context_envelope_digest: preflightResult.context_envelope?.digest,
              previous_contract: intentContractsByThread.get(nextMessage.params.threadId) ?? null,
            });
            const successorReasoning = successorIntent.ok
              ? prepareModelDispatch(nextMessage, preflightResult, resolveTurnBinding(nextMessage, successorBinding(proposal)), successorIntent)
              : successorIntent;
            if (!successorReasoning.ok) {
              actions.to_client.push(successorNotification({kind: "stopped", proposal_id: proposal.proposal_id, reasoning_dispatch: successorReasoning, authority_effect: "none"}));
              ledger.record({event_kind: "successor-stopped", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest, successor_proposal_id: proposal.proposal_id});
              ledger.record({event_kind: "turn-closed", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest ?? digestValue(directive)});
              ledger.evict();
              return actions;
            }
            rememberTurnStart(nextMessage, preflightResult, successorReasoning, successorIntent);
            internalRequests.add(String(nextMessage.id));
            ledger.record({event_kind: "preflight-decision", direction: "wrapper", method: TURN_START, rpc_id: nextMessage.id, thread_id: nextMessage.params.threadId, message_digest: digestValue(nextMessage), decision_digest: preflightResult.directive.decision_digest});
            ledger.record({event_kind: "reasoning-dispatch-verified", direction: "wrapper", method: TURN_START, rpc_id: nextMessage.id, thread_id: nextMessage.params.threadId, message_digest: successorReasoning.dispatch.message_digest, reasoning_epoch_id: successorReasoning.epoch.epoch_id, reasoning_epoch_digest: successorReasoning.epoch.epoch_digest, checkpoint_digest: successorReasoning.checkpoint.checkpoint_digest, checkpoint_kind: "before-model-request", dispatch_digest: successorReasoning.dispatch.dispatch_digest, dispatch_verification_digest: successorReasoning.verification.verification_digest, request_header_digest: successorReasoning.dispatch.request_header_digest});
            ledger.record({event_kind: "turn-start-forwarded", direction: "wrapper-to-server", method: TURN_START, rpc_id: nextMessage.id, thread_id: nextMessage.params.threadId, message_digest: digestValue(preflightResult.forwarded_message), decision_digest: preflightResult.directive.decision_digest});
            actions.to_server.push(successorReasoning.forwarded_message);
            actions.to_client.push(successorNotification({kind: "started", proposal_id: proposal.proposal_id, proposal_digest: proposal.proposal_digest, preflight_decision_digest: preflightResult.directive.decision_digest, authority_effect: "none"}));
            ledger.record({event_kind: "successor-started", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest, successor_proposal_id: proposal.proposal_id});
          } else {
            actions.to_client.push(successorNotification({kind: "stopped", proposal_id: proposal.proposal_id, preflight: preflightResult, authority_effect: "none"}));
            ledger.record({event_kind: "successor-stopped", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest, successor_proposal_id: proposal.proposal_id});
          }
        } else if (replayedCompletion) {
          const replayCut = ledger.cut({thread_id: identity.thread_id, turn_id: identity.turn_id});
          const replay = replayCut.ok ? ledger.replay(replayCut.value) : replayCut;
          actions.to_client.push(successorNotification({kind: "replayed", turn_id: identity.turn_id, replay_digest: replay.ok ? replay.value.replay_digest : null, authority_effect: "none"}));
        }
        ledger.record({event_kind: "turn-closed", direction: "wrapper", method: TURN_COMPLETED, thread_id: identity.thread_id, turn_id: identity.turn_id, decision_digest: directive.decision_digest ?? digestValue(directive)});
        ledger.evict();
        return actions;
      }
    }
    return {...emptyActions(), to_client: [message]};
  }

  return Object.freeze({
    processClientMessage: async (message) => {
      if ((!learningEnabled && options.loaded_profile.objective_resolution?.enabled !== true) || message?.method !== TURN_START) return processClientMessage(message);
      const key = learningEnabled ? "learning-product" : message.params?.threadId;
      if (objectiveTurnsInFlight.has(key)) return {...emptyActions(), to_client: [jsonRpcError(message.id, -32078, "Objective turn is already in progress", {reason_codes: ["objective.concurrent-turn-in-progress"]})]};
      objectiveTurnsInFlight.add(key);
      try { return await processClientMessage(message); }
      finally { objectiveTurnsInFlight.delete(key); }
    },
    processServerMessage,
    runLearningEvolution: learning.runEvolution,
    inspectLearningState: learning.inspect,
    controlLearning: learning.control,
    prepareForEviction,
    recordCacheTelemetry,
    ledger,
    close: () => {
      if (closed) return freezeResult({ok: true, disposition: "already-closed", authority_effect: "none"});
      const ledgerResult = reasoningLedger.close();
      const lockResult = reasoningWriterLock?.release() ?? null;
      closed = true;
      return freezeResult({ok: ledgerResult?.ok !== false && lockResult?.ok !== false, disposition: "closed", ledger: ledgerResult, writer_lock: lockResult, authority_effect: "none"});
    },
    inspectState: () => freezeResult({
      context_dependencies: {
        definition_catalog: isRecord(options.definition_catalog)
          ? "available-inline"
          : contextModulePort?.capability_ids?.includes("context.definition-catalog/v1") ? "available-module" : "unavailable",
        ontology_snapshot: isRecord(options.ontology_snapshot)
          ? "available-inline"
          : contextModulePort?.capability_ids?.includes("context.ontology-snapshot/v1") ? "available-module" : "unavailable",
      },
      pending_approval_ids: [...pendingApprovals.keys()].sort(),
      proposal_thread_ids: [...proposalsByThread.keys()].sort(),
      current_view_consumers: [...currentViews.keys()].sort(),
      current_context_epochs: [...currentViews.entries()].map(([consumer, state]) => ({consumer, view_id: state.view.view_id, view_lane: state.view.lane, context_epoch_id: state.envelope.context_epoch_id, freshness_state: state.envelope.freshness_state, content_projection_digest: state.envelope.content_projection_digest, projection_reused: state.envelope.projection_reuse_receipt !== null, projection_reuse_receipt_digest: state.envelope.projection_reuse_receipt?.receipt_digest ?? null})).sort((a, b) => a.consumer.localeCompare(b.consumer)),
      completion_thread_ids: [...completionByThread.keys()].sort(),
      pending_semantic_rpc_ids: [...pendingTurnStates.keys()].sort(),
      active_semantic_turn_ids: [...activeTurnStates.values()].map((state) => state.turn_id).sort(),
      semantic_completion_turn_ids: [...semanticCompletions.keys()].sort(),
      evolution_signal_turn_ids: [...evolutionSignalEmissions.keys()].sort(),
      intent_contract_threads: [...intentContractsByThread.entries()].map(([thread_id, contract]) => ({thread_id, intent_contract_digest: contract.intent_contract_digest, predecessor_contract_digest: contract.predecessor_contract_digest})).sort((a, b) => a.thread_id.localeCompare(b.thread_id)),
      intent_realization_turn_ids: [...intentRealizationsByTurn.keys()].sort(),
      objective_states: objectiveLifecycle.inspect(),
      completion_turn_ids: [...completionByTurn.keys()].sort(),
      completion_frontier_turn_ids: [...completionFrontiers.keys()].sort(),
      cache_affinity_consumers: [...cacheAffinityByConsumer.entries()].map(([consumer, value]) => ({consumer, posture: value.assessment.posture, exact_prefix_reuse: value.assessment.exact_prefix_reuse, reusable_prefix_bytes: value.assessment.reusable_prefix_bytes, reused_prefix_bytes: value.assessment.reused_prefix_bytes, invalidation_reasons: value.assessment.invalidation_reasons, projection_digest: value.projection.projection_digest, exact_prefix_digest: value.projection.exact_prefix_digest, provider_ref: value.projection.stable_request_prefix.provider_ref, model_ref: value.projection.stable_request_prefix.model_ref, assessment_digest: value.assessment.assessment_digest, context_bound_reuse_disposition: value.receipt.disposition, context_bound_reuse_receipt_digest: value.receipt.receipt_digest, refresh_assessment_digest: value.receipt.refresh_assessment_digest, selected_dependencies_digest: value.receipt.selected_dependencies_digest, cache_hit_posture: value.telemetry?.cache_hit_posture ?? value.assessment.cache_hit_posture, observed_input_tokens: value.telemetry?.observed_input_tokens ?? null, observed_cached_input_tokens: value.telemetry?.observed_cached_input_tokens ?? null, observed_token_savings: value.telemetry?.observed_token_savings ?? value.assessment.observed_token_savings, observed_time_savings_ms: value.telemetry?.observed_time_savings_ms ?? value.assessment.observed_time_savings_ms, cache_telemetry_observation_digest: value.telemetry?.observation_digest ?? null})).sort((a, b) => a.consumer.localeCompare(b.consumer)),
      context_window_telemetry: contextWindowTracker.snapshot(),
      reasoning_evolution_consumers: [...reasoningEpochByConsumer.entries()].map(([consumer, epoch]) => ({consumer, epoch_id: epoch.epoch_id, epoch_digest: epoch.epoch_digest, event_count: epoch.event_digests.length})).sort((a, b) => a.consumer.localeCompare(b.consumer)),
      runtime_journal: ledger.inspect(),
      reasoning_state: reasoningLedger.inspect(),
      reasoning_state_writer_lock: reasoningWriterLock?.inspect() ?? null,
      authority_effect: "none",
    }),
  });
}
