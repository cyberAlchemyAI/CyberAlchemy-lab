import {
  canonicalJson,
  canonicalizeJson,
  deepFreeze,
  sha256HexText,
} from "../intent-route-resolver/index.mjs";
import {
  createReasoningStateLedger,
  replayReasoningStateEpoch,
  sealReasoningStateEpoch,
} from "../reasoning-state-runtime/index.mjs";
import {readFileSync} from "node:fs";
import {isAbsolute, relative, resolve} from "node:path";

export {createVariantWorkspaceFactory} from "./src/variant-workspace.mjs";
export {applyUpgradeDecision, createServingVersionStore} from "./src/upgrade-controller.mjs";
export {createEvolutionScheduler} from "./src/scheduler.mjs";
export {REPLICATION_SOURCE_PATHS, materializeReplicationManifest, verifyReplicationManifest, scoreReplicationRun, materializeReplicationResult} from "./src/requirement-replication.mjs";
export {LATENCY_SOURCE_PATHS, materializeLatencyManifest, verifyLatencyManifest, scoreLatencyRun, materializeLatencyResult} from "./src/requirement-latency-control.mjs";

export const EVOLUTION_PROFILE_SCHEMA = "are.evolution-profile/v1";
export const IMPROVEMENT_SIGNAL_SCHEMA = "are.improvement-signal/v1";
export const IMPROVEMENT_TARGET_SCHEMA = "are.improvement-target/v1";
export const IMPROVEMENT_RETENTION_SCHEMA = "are.improvement-retention/v1";
export const RESEARCH_RESULT_SCHEMA = "are.research-result/v1";
export const RESEARCH_HYPOTHESIS_SCHEMA = "are.research-hypothesis/v1";
export const FAILURE_HYPOTHESIS_PROJECTION_SCHEMA = "are.failure-hypothesis-projection/v1";
export const HYPOTHESIS_OBSERVATION_SCHEMA = "are.hypothesis-observation/v1";
export const RESEARCH_EXPERIMENT_SCHEMA = "are.research-experiment/v1";
export const LEARNING_DECISION_SCHEMA = "are.learning-decision/v1";
export const TECHNIQUE_CANDIDATE_SCHEMA = "are.technique-candidate/v1";
export const REPRODUCTION_TRIAL_SCHEMA = "are.reproduction-trial/v1";
export const ENGINE_VARIANT_SCHEMA = "are.engine-variant/v1";
export const VARIANT_COMPARISON_SCHEMA = "are.variant-comparison/v1";
export const UPGRADE_DECISION_SCHEMA = "are.upgrade-decision/v1";
export const EVOLUTION_CYCLE_SCHEMA = "are.evolution-cycle/v1";

const RECORD_PREFIX = new Map([
  [IMPROVEMENT_SIGNAL_SCHEMA, "improvement-signal"],
  [IMPROVEMENT_TARGET_SCHEMA, "improvement-target"],
  [IMPROVEMENT_RETENTION_SCHEMA, "improvement-retention"],
  [RESEARCH_RESULT_SCHEMA, "research-result"],
  [RESEARCH_HYPOTHESIS_SCHEMA, "research-hypothesis"],
  [FAILURE_HYPOTHESIS_PROJECTION_SCHEMA, "failure-hypothesis-projection"],
  [HYPOTHESIS_OBSERVATION_SCHEMA, "hypothesis-observation"],
  [RESEARCH_EXPERIMENT_SCHEMA, "research-experiment"],
  [LEARNING_DECISION_SCHEMA, "learning-decision"],
  [TECHNIQUE_CANDIDATE_SCHEMA, "technique-candidate"],
  [REPRODUCTION_TRIAL_SCHEMA, "reproduction-trial"],
  [ENGINE_VARIANT_SCHEMA, "engine-variant"],
  [VARIANT_COMPARISON_SCHEMA, "variant-comparison"],
  [UPGRADE_DECISION_SCHEMA, "upgrade-decision"],
  [EVOLUTION_CYCLE_SCHEMA, "evolution-cycle"],
]);

function object(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function text(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function finite(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function freeze(value) {
  return deepFreeze(canonicalizeJson(value));
}

function digest(value) {
  return sha256HexText(canonicalJson(canonicalizeJson(value)));
}

function uniqueText(values) {
  return [...new Set((Array.isArray(values) ? values : []).filter(text).map((value) => value.trim()))].sort();
}

const SHA256_PATTERN = /^[a-f0-9]{64}$/;

function exactBindings(values, label) {
  if (!Array.isArray(values) || values.length === 0) throw new TypeError(`${label} requires at least one exact binding.`);
  const bindings = values.map((binding) => {
    if (!object(binding) || !text(binding.path) || !text(binding.sha256) || !SHA256_PATTERN.test(binding.sha256.trim())) throw new TypeError(`${label} contains an invalid exact binding.`);
    if (binding.selector !== undefined && (!text(binding.selector) || !binding.selector.trim().startsWith("/"))) throw new TypeError(`${label} contains an invalid selector.`);
    return {path: binding.path.trim(), sha256: binding.sha256.trim(), ...(binding.selector === undefined ? {} : {selector: binding.selector.trim()})};
  }).sort((left, right) => left.path.localeCompare(right.path));
  if (new Set(bindings.map((binding) => binding.path)).size !== bindings.length) throw new TypeError(`${label} contains a duplicate path.`);
  return bindings;
}

const UNRESOLVED_SELECTOR = Symbol("unresolved-selector");

function selectJsonPointer(document, selector) {
  let selected = document;
  for (const rawToken of selector.slice(1).split("/")) {
    const token = rawToken.replace(/~1/g, "/").replace(/~0/g, "~");
    if (!object(selected) && !Array.isArray(selected)) return UNRESOLVED_SELECTOR;
    if (!Object.hasOwn(selected, token)) return UNRESOLVED_SELECTOR;
    selected = selected[token];
  }
  return selected;
}

function fail(stage, reasonCodes, residue = []) {
  return freeze({
    schema_version: "are.evolution-failure/v1",
    ok: false,
    stage,
    reason_codes: uniqueText(reasonCodes),
    residue: Array.isArray(residue) ? residue : [],
    authority_effect: "none",
  });
}

function seal(schemaVersion, fields) {
  const prefix = RECORD_PREFIX.get(schemaVersion);
  if (!prefix) throw new TypeError(`Unsupported evolution record schema: ${schemaVersion}`);
  const material = canonicalizeJson({schema_version: schemaVersion, ...fields, authority_effect: "none"});
  const recordDigest = digest(material);
  return freeze({...material, record_id: `${prefix}:${recordDigest}`, record_digest: recordDigest});
}

function recordMaterial(record) {
  const {record_id: _id, record_digest: _digest, ...material} = record;
  return material;
}

export function verifyEvolutionRecord(record, expectedSchema = null) {
  const reasons = [];
  if (!object(record) || !RECORD_PREFIX.has(record.schema_version)) reasons.push("evolution.record-schema-invalid");
  if (expectedSchema !== null && record?.schema_version !== expectedSchema) reasons.push("evolution.record-schema-mismatch");
  const prefix = RECORD_PREFIX.get(record?.schema_version);
  if (prefix) {
    const expectedDigest = digest(recordMaterial(record));
    if (record.record_digest !== expectedDigest) reasons.push("evolution.record-digest-invalid");
    if (record.record_id !== `${prefix}:${expectedDigest}`) reasons.push("evolution.record-id-invalid");
  }
  if (record?.authority_effect !== "none") reasons.push("evolution.record-authority-invalid");
  return reasons.length > 0 ? fail("record-verification", reasons) : freeze({ok: true, value: record, authority_effect: "none"});
}

export function verifyEvolutionProfile(profile) {
  const reasons = [];
  if (!object(profile) || profile.schema_version !== EVOLUTION_PROFILE_SCHEMA) reasons.push("evolution.profile-schema-invalid");
  if (!text(profile?.profile_id)) reasons.push("evolution.profile-id-required");
  if (!object(profile?.research) || typeof profile.research.enabled !== "boolean" || !Number.isSafeInteger(profile.research.maximum_results_per_provider) || profile.research.maximum_results_per_provider < 1) reasons.push("evolution.profile-research-invalid");
  if (!object(profile?.target_selection) || !Number.isSafeInteger(profile.target_selection.minimum_signal_count) || profile.target_selection.minimum_signal_count < 1) reasons.push("evolution.profile-target-selection-invalid");
  if (!object(profile?.upgrade) || !["recommend-only", "controlled-local"].includes(profile.upgrade.mode) || !Number.isSafeInteger(profile.upgrade.required_keep_streak) || profile.upgrade.required_keep_streak < 1) reasons.push("evolution.profile-upgrade-invalid");
  if (profile?.authority_effect !== "none") reasons.push("evolution.profile-authority-invalid");
  return reasons.length > 0 ? fail("profile-verification", reasons) : freeze({ok: true, value: profile, authority_effect: "none"});
}

export function createImprovementSignal(input) {
  if (!object(input) || !text(input.kind) || !text(input.source_result_ref) || !text(input.scope)) throw new TypeError("Improvement signal requires kind, source_result_ref, and scope.");
  if (!finite(input.observed_value) && !text(input.observed_value)) throw new TypeError("Improvement signal requires a finite numeric or non-empty textual observed_value.");
  return seal(IMPROVEMENT_SIGNAL_SCHEMA, {
    kind: input.kind.trim(),
    source_result_ref: input.source_result_ref.trim(),
    scope: input.scope.trim(),
    observed_value: input.observed_value,
    expected_value: input.expected_value ?? null,
    metric: text(input.metric) ? input.metric.trim() : null,
    occurred_at: text(input.occurred_at) ? input.occurred_at.trim() : null,
    provenance_refs: uniqueText(input.provenance_refs),
    confidence: finite(input.confidence) ? input.confidence : null,
  });
}

export function createImprovementTarget(input) {
  if (!object(input) || !text(input.target_key) || !text(input.metric) || !["higher", "lower"].includes(input.direction) || !finite(input.threshold)) throw new TypeError("Improvement target requires target_key, metric, direction, and finite threshold.");
  const signalRefs = uniqueText(input.signal_refs);
  if (signalRefs.length === 0) throw new TypeError("Improvement target requires at least one signal_ref.");
  return seal(IMPROVEMENT_TARGET_SCHEMA, {
    target_key: input.target_key.trim(),
    signal_refs: signalRefs,
    metric: input.metric.trim(),
    direction: input.direction,
    baseline_ref: text(input.baseline_ref) ? input.baseline_ref.trim() : null,
    baseline_value: finite(input.baseline_value) ? input.baseline_value : null,
    threshold: input.threshold,
    priority: Number.isSafeInteger(input.priority) ? input.priority : 100,
    protected_metrics: canonicalizeJson(object(input.protected_metrics) ? input.protected_metrics : {}),
    test_sets: uniqueText(input.test_sets),
    mutation_allowlist: uniqueText(input.mutation_allowlist),
    invalidation_rules: uniqueText(input.invalidation_rules),
  });
}

export function createImprovementRetention(input) {
  if (!object(input) || !text(input.candidate_id) || input.lifecycle_state !== "implemented-and-verified") throw new TypeError("Improvement retention requires a candidate and implemented-and-verified lifecycle state.");
  const comparison = object(input.observed_comparison) ? input.observed_comparison : {};
  if (![comparison.baseline_p95_ms, comparison.candidate_p95_ms, comparison.potential_savings_ms].every(finite)) throw new TypeError("Improvement retention requires a finite observed comparison.");
  if (!Number.isSafeInteger(comparison.valid_observations_per_arm) || comparison.valid_observations_per_arm < 1) throw new TypeError("Improvement retention requires valid observation counts.");
  return seal(IMPROVEMENT_RETENTION_SCHEMA, {
    candidate_id: input.candidate_id.trim(),
    lifecycle_state: "implemented-and-verified",
    implementation_bindings: exactBindings(input.implementation_bindings, "Improvement implementation bindings"),
    evidence_bindings: exactBindings(input.evidence_bindings, "Improvement evidence bindings"),
    observed_comparison: canonicalizeJson({
      baseline_p95_ms: comparison.baseline_p95_ms,
      candidate_p95_ms: comparison.candidate_p95_ms,
      potential_savings_ms: comparison.potential_savings_ms,
      valid_observations_per_arm: comparison.valid_observations_per_arm,
      verification: text(comparison.verification) ? comparison.verification.trim() : null,
    }),
    verification_refs: uniqueText(input.verification_refs),
    limitations: uniqueText(input.limitations),
  });
}

export function verifyImprovementRetention(retention) {
  const checked = verifyEvolutionRecord(retention, IMPROVEMENT_RETENTION_SCHEMA);
  if (!checked.ok) return checked;
  try {
    const normalized = createImprovementRetention(retention);
    if (normalized.record_id !== retention.record_id) return fail("improvement-retention-verification", ["evolution.retention-material-invalid"]);
  } catch {
    return fail("improvement-retention-verification", ["evolution.retention-material-invalid"]);
  }
  return freeze({ok: true, value: retention, authority_effect: "none"});
}

export function assessImprovementRetentionCurrentness(retention, {repository_root: repositoryRoot} = {}) {
  const checked = verifyImprovementRetention(retention);
  if (!checked.ok) return fail("improvement-retention-currentness", checked.reason_codes);
  if (!text(repositoryRoot)) return fail("improvement-retention-currentness", ["evolution.retention-repository-root-required"]);
  const root = resolve(repositoryRoot);
  const changedBindings = [];
  for (const [bindingKind, bindings] of [["implementation", retention.implementation_bindings], ["evidence", retention.evidence_bindings]]) {
    for (const binding of bindings) {
      const path = resolve(root, binding.path);
      const relativePath = relative(root, path);
      if (!relativePath || relativePath.startsWith("..") || isAbsolute(relativePath)) {
        changedBindings.push({binding_kind: bindingKind, path: binding.path, expected_sha256: binding.sha256, actual_sha256: null, reason: "binding-path-outside-repository"});
        continue;
      }
      let actual = null;
      let failureReason = "binding-unreadable";
      try {
        const sourceText = readFileSync(path, "utf8");
        if (binding.selector === undefined) actual = sha256HexText(sourceText);
        else {
          const selected = selectJsonPointer(JSON.parse(sourceText), binding.selector);
          if (selected === UNRESOLVED_SELECTOR) failureReason = "binding-selector-unresolved";
          else actual = digest(selected);
        }
      } catch {}
      if (actual !== binding.sha256) changedBindings.push({binding_kind: bindingKind, path: binding.path, selector: binding.selector ?? null, expected_sha256: binding.sha256, actual_sha256: actual, reason: actual === null ? failureReason : "binding-digest-drift"});
    }
  }
  return freeze({
    ok: true,
    candidate_id: retention.candidate_id,
    retention_ref: retention.record_id,
    disposition: changedBindings.length === 0 ? "current" : "stale",
    suppress_reselection: changedBindings.length === 0,
    changed_bindings: changedBindings,
    authority_effect: "none",
  });
}

export function createResearchResult(input) {
  if (!object(input) || !text(input.target_ref) || !text(input.provider_id) || !text(input.source_ref) || !text(input.source_version) || !text(input.mechanism)) throw new TypeError("Research result requires target, provider, source, version, and mechanism.");
  return seal(RESEARCH_RESULT_SCHEMA, {
    target_ref: input.target_ref.trim(),
    provider_id: input.provider_id.trim(),
    source_ref: input.source_ref.trim(),
    source_version: input.source_version.trim(),
    retrieved_at: text(input.retrieved_at) ? input.retrieved_at.trim() : null,
    mechanism: input.mechanism.trim(),
    evidence: uniqueText(input.evidence),
    counterevidence: uniqueText(input.counterevidence),
    limitations: uniqueText(input.limitations),
    fit_hypothesis: text(input.fit_hypothesis) ? input.fit_hypothesis.trim() : null,
  });
}

export function createResearchHypothesis(input) {
  if (!object(input) || !text(input.hypothesis_key) || !text(input.statement) || !text(input.mechanism) || !text(input.falsifier) || !text(input.scope)) throw new TypeError("Research hypothesis requires key, statement, mechanism, falsifier, and scope.");
  const metrics = uniqueText(input.metrics);
  if (metrics.length === 0) throw new TypeError("Research hypothesis requires at least one metric.");
  if (!object(input.experiment_template) || !text(input.experiment_template.research_question) || !text(input.experiment_template.baseline_ref) || !text(input.experiment_template.treatment_ref)) throw new TypeError("Research hypothesis requires an experiment template with question, baseline, and treatment.");
  const lineage = {};
  if (text(input.parent_hypothesis_ref)) lineage.parent_hypothesis_ref = input.parent_hypothesis_ref.trim();
  if (text(input.supersedes_experiment_ref)) lineage.supersedes_experiment_ref = input.supersedes_experiment_ref.trim();
  if (text(input.strategy_ref)) lineage.strategy_ref = input.strategy_ref.trim();
  if (text(input.implementation_pattern)) lineage.implementation_pattern = input.implementation_pattern.trim();
  if (text(input.implementation_ref)) lineage.implementation_ref = input.implementation_ref.trim();
  return seal(RESEARCH_HYPOTHESIS_SCHEMA, {
    hypothesis_key: input.hypothesis_key.trim(),
    statement: input.statement.trim(),
    mechanism: input.mechanism.trim(),
    falsifier: input.falsifier.trim(),
    scope: input.scope.trim(),
    metrics,
    provenance_refs: uniqueText(input.provenance_refs),
    experiment_template: canonicalizeJson({
      research_question: input.experiment_template.research_question.trim(),
      baseline_ref: input.experiment_template.baseline_ref.trim(),
      treatment_ref: input.experiment_template.treatment_ref.trim(),
      dataset_refs: uniqueText(input.experiment_template.dataset_refs),
      required_repetitions: Number.isSafeInteger(input.experiment_template.required_repetitions) && input.experiment_template.required_repetitions > 0 ? input.experiment_template.required_repetitions : 3,
      success_criteria: object(input.experiment_template.success_criteria) ? input.experiment_template.success_criteria : {},
      stop_conditions: uniqueText(input.experiment_template.stop_conditions),
    }),
    ...lineage,
  });
}

const FAILURE_IMPLEMENTATION_PATTERNS = Object.freeze({
  scenario_contracts: "bind-scenario-contract-before-reuse",
  typed_projection_beats_recent_control: "pin-typed-state-before-recency-reduction",
  reflection_improves_intent_fidelity: "apply-intent-reflection-before-context-projection",
  adaptive_eliminates_stale_reuse: "bind-refresh-assessment-before-cache-eligibility",
  eligible_exact_prefix_reuse: "canonical-stable-prefix-construction",
  mandatory_reasoning_preserved: "preserve-mandatory-reasoning-state-during-compaction",
  byte_reduction: "budgeted-structural-compaction",
  latency: "profile-context-bound-reuse-critical-path",
});

function benchmarkFailureContract(result, expectedResultDigest) {
  const reasons = [];
  if (!object(result) || result.schema_version !== "are.real-reasoning-benchmark-result/v1") reasons.push("evolution.benchmark-result-invalid");
  if (!text(expectedResultDigest) || !SHA256_PATTERN.test(expectedResultDigest)) reasons.push("evolution.benchmark-result-digest-required");
  const actualDigest = object(result) ? digest(result) : null;
  if (text(expectedResultDigest) && actualDigest !== expectedResultDigest) reasons.push("evolution.benchmark-result-digest-mismatch");
  if (!text(result?.benchmark_id) || !text(result?.profile_digest) || !text(result?.mode)) reasons.push("evolution.benchmark-result-identity-invalid");
  const notEvaluated = result?.status === "NOT_EVALUATED";
  if (!notEvaluated && (!object(result?.summary?.checks) || Object.values(result.summary.checks).some((value) => typeof value !== "boolean"))) reasons.push("evolution.benchmark-checks-invalid");
  if (result?.cases !== undefined && !Array.isArray(result.cases) && !object(result.cases)) reasons.push("evolution.benchmark-cases-invalid");
  if (!["PASS", "FAIL", "NOT_EVALUATED"].includes(result?.status)) reasons.push("evolution.benchmark-status-invalid");
  if (result?.authority_effect !== "none") reasons.push("evolution.benchmark-authority-invalid");
  if (reasons.length > 0) return fail("failure-hypothesis-projection", reasons);
  const failedChecks = notEvaluated ? [] : Object.entries(result.summary.checks).filter(([, passed]) => !passed).map(([key]) => key).sort();
  if (notEvaluated) return freeze({ok: true, actual_digest: actualDigest, failed_checks: [], not_evaluated: true, authority_effect: "none"});
  if ((result.status === "PASS") !== (failedChecks.length === 0)) return fail("failure-hypothesis-projection", ["evolution.benchmark-status-inconsistent"]);
  return freeze({ok: true, actual_digest: actualDigest, failed_checks: failedChecks, not_evaluated: false, authority_effect: "none"});
}

function benchmarkScenarioCases(value, selected = []) {
  if (Array.isArray(value)) {
    for (const item of value) benchmarkScenarioCases(item, selected);
    return selected;
  }
  if (!object(value)) return selected;
  if (text(value.scenario_id) && typeof value.passed === "boolean") {
    selected.push(value);
    return selected;
  }
  for (const child of Object.values(value)) benchmarkScenarioCases(child, selected);
  return selected;
}

export function projectBenchmarkFailuresToHypotheses({benchmark_result: result, expected_result_digest: expectedResultDigest} = {}) {
  const checked = benchmarkFailureContract(result, expectedResultDigest);
  if (!checked.ok) return checked;
  const sourceResultRef = `benchmark-result:${result.benchmark_id}:${result.mode}:${checked.actual_digest}`;
  const cases = benchmarkScenarioCases(result.cases ?? []);
  const failedScenarioIds = [...new Set(cases.filter((entry) => !entry.passed).map((entry) => entry.scenario_id))].sort();
  const signals = [];
  const hypotheses = [];
  for (const checkKey of checked.failed_checks) {
    const pattern = FAILURE_IMPLEMENTATION_PATTERNS[checkKey] ?? "localize-failure-before-selecting-a-technique";
    const signal = createImprovementSignal({
      kind: `${result.mode}.${checkKey}-failure`,
      source_result_ref: sourceResultRef,
      scope: `${result.mode}:${checkKey}`,
      observed_value: "failed",
      expected_value: "passed",
      metric: checkKey,
      provenance_refs: [checked.actual_digest, result.profile_digest, ...failedScenarioIds.map((id) => `scenario:${id}`)],
      confidence: 1,
    });
    const keyMaterial = {source_result_digest: checked.actual_digest, check_key: checkKey, pattern, failed_scenario_ids: failedScenarioIds};
    const hypothesis = createResearchHypothesis({
      hypothesis_key: `ARE-AUTO-${checkKey.replaceAll(/[^a-zA-Z0-9]+/g, "-").toUpperCase()}-${digest(keyMaterial).slice(0, 12).toUpperCase()}`,
      statement: `Applying ${pattern} will make the ${checkKey} check pass on the exact ${result.mode} benchmark without regressing its other checks.`,
      mechanism: `Use the ${pattern} code pattern at the smallest implementation boundary implicated by the failed check, then replay the exact failed scenarios.`,
      falsifier: `The ${checkKey} check remains false, any previously passing check regresses, or the exact failed scenarios cannot be reproduced.`,
      scope: `${result.benchmark_id}:${result.mode}:${checkKey}`,
      metrics: [checkKey],
      provenance_refs: [signal.record_id, sourceResultRef, result.profile_digest, ...failedScenarioIds.map((id) => `scenario:${id}`)],
      experiment_template: {
        research_question: `Does ${pattern} repair ${checkKey} without benchmark regression?`,
        baseline_ref: sourceResultRef,
        treatment_ref: `implementation-pattern:${pattern}`,
        dataset_refs: failedScenarioIds.map((id) => `scenario:${id}`),
        required_repetitions: 3,
        success_criteria: {check_key: checkKey, expected: true, preserve_previously_passing_checks: true},
        stop_conditions: ["authority effect observed", "previously passing check regressed", "source benchmark bytes drifted"],
      },
      strategy_ref: "failure-to-hypothesis/v1",
      implementation_pattern: pattern,
    });
    signals.push(signal);
    hypotheses.push(hypothesis);
  }
  const projection = seal(FAILURE_HYPOTHESIS_PROJECTION_SCHEMA, {
    source_result_ref: sourceResultRef,
    source_result_digest: checked.actual_digest,
    benchmark_id: result.benchmark_id,
    benchmark_mode: result.mode,
    disposition: checked.not_evaluated ? "not-evaluated" : checked.failed_checks.length === 0 ? "no-failures" : "hypotheses-projected",
    failed_check_keys: checked.failed_checks,
    failed_scenario_ids: failedScenarioIds,
    signal_refs: signals.map((signal) => signal.record_id),
    hypothesis_refs: hypotheses.map((hypothesis) => hypothesis.record_id),
    signals,
    hypotheses,
    claim_ceiling: "Deterministic improvement candidates only; no implementation, adoption, acceptance, publication, deployment, or effect authority.",
  });
  return freeze({ok: true, value: projection, authority_effect: "none"});
}

export function createHypothesisObservation(input) {
  if (!object(input) || !text(input.hypothesis_ref) || !text(input.source_result_ref) || !text(input.claim) || !text(input.evaluator_id)) throw new TypeError("Hypothesis observation requires hypothesis, source result, claim, and evaluator.");
  if (!["supporting", "counterevidence", "inconclusive"].includes(input.observation_kind)) throw new TypeError("Hypothesis observation kind is invalid.");
  if (!["anomaly", "replication", "experiment"].includes(input.phase)) throw new TypeError("Hypothesis observation phase is invalid.");
  return seal(HYPOTHESIS_OBSERVATION_SCHEMA, {
    hypothesis_ref: input.hypothesis_ref.trim(),
    source_result_ref: input.source_result_ref.trim(),
    source_result_digest: text(input.source_result_digest) ? input.source_result_digest.trim() : null,
    observation_kind: input.observation_kind,
    phase: input.phase,
    claim: input.claim.trim(),
    evaluator_id: input.evaluator_id.trim(),
    evidence_refs: uniqueText(input.evidence_refs),
    missing_terms: uniqueText(input.missing_terms),
    observed_markers: uniqueText(input.observed_markers),
    limitations: uniqueText(input.limitations),
  });
}

export function createResearchExperiment(input) {
  if (!object(input) || !text(input.hypothesis_ref) || !text(input.research_question) || !text(input.baseline_ref) || !text(input.treatment_ref)) throw new TypeError("Research experiment requires hypothesis, question, baseline, and treatment.");
  const metrics = uniqueText(input.metrics);
  if (metrics.length === 0 || !Number.isSafeInteger(input.required_repetitions) || input.required_repetitions < 1) throw new TypeError("Research experiment requires metrics and a positive repetition count.");
  return seal(RESEARCH_EXPERIMENT_SCHEMA, {
    hypothesis_ref: input.hypothesis_ref.trim(),
    research_question: input.research_question.trim(),
    baseline_ref: input.baseline_ref.trim(),
    treatment_ref: input.treatment_ref.trim(),
    metrics,
    dataset_refs: uniqueText(input.dataset_refs),
    required_repetitions: input.required_repetitions,
    success_criteria: canonicalizeJson(object(input.success_criteria) ? input.success_criteria : {}),
    stop_conditions: uniqueText(input.stop_conditions),
    observation_refs: uniqueText(input.observation_refs),
  });
}

export function createLearningDecision(input) {
  if (!object(input) || !text(input.hypothesis_ref) || !["collect-replications", "run-experiment", "revise-hypothesis", "candidate-supported", "inconclusive"].includes(input.disposition)) throw new TypeError("Learning decision requires hypothesis and a supported disposition.");
  return seal(LEARNING_DECISION_SCHEMA, {
    hypothesis_ref: input.hypothesis_ref.trim(),
    observation_refs: uniqueText(input.observation_refs),
    experiment_ref: text(input.experiment_ref) ? input.experiment_ref.trim() : null,
    disposition: input.disposition,
    reason_codes: uniqueText(input.reason_codes),
    supporting_count: Number.isSafeInteger(input.supporting_count) ? input.supporting_count : 0,
    counterevidence_count: Number.isSafeInteger(input.counterevidence_count) ? input.counterevidence_count : 0,
    experiment_support_count: Number.isSafeInteger(input.experiment_support_count) ? input.experiment_support_count : 0,
    next_action: text(input.next_action) ? input.next_action.trim() : null,
  });
}

function markerHits(answer, alternatives) {
  const normalized = ` ${(String(answer ?? "").toLowerCase().match(/[a-z0-9]+/g) ?? []).join(" ")} `;
  return uniqueText(alternatives).filter((alternative) => {
    const phrase = (alternative.toLowerCase().match(/[a-z0-9]+/g) ?? []).join(" ");
    return phrase.length > 0 && normalized.includes(` ${phrase} `);
  });
}

export function diagnoseLexicalScoringAnomaly(input) {
  if (!object(input) || !text(input.hypothesis_ref) || !text(input.source_result_ref) || !object(input.scenario) || !object(input.score) || !object(input.response)) throw new TypeError("Lexical diagnosis requires hypothesis, source result, scenario, score, and response.");
  const required = uniqueText(input.scenario.required_terms);
  const hits = new Set(uniqueText(input.score.required_hits));
  const missing = required.filter((term) => !hits.has(term));
  if (input.score.passed !== false || missing.length === 0) return freeze({ok: true, disposition: "no-anomaly", observation: null, authority_effect: "none"});
  const declared = object(input.concept_markers) ? input.concept_markers : {};
  const observed = missing.flatMap((term) => markerHits(input.response.answer, declared[term]));
  const covered = missing.filter((term) => markerHits(input.response.answer, declared[term]).length > 0);
  const supported = covered.length === missing.length;
  const observation = createHypothesisObservation({
    hypothesis_ref: input.hypothesis_ref,
    source_result_ref: input.source_result_ref,
    source_result_digest: input.source_result_digest,
    observation_kind: supported ? "supporting" : "inconclusive",
    phase: input.phase ?? "anomaly",
    claim: supported ? "The exact-term scorer rejected a response containing declared semantic evidence markers." : "The scorer rejected a response, but declared semantic markers do not cover every missing term.",
    evaluator_id: input.evaluator_id ?? "are.lexical-semantic-anomaly-detector/v1",
    evidence_refs: input.evidence_refs,
    missing_terms: missing,
    observed_markers: observed,
    limitations: ["Declared marker presence is diagnostic evidence, not proof that the complete answer is correct."],
  });
  return freeze({ok: true, disposition: supported ? "hypothesis-supported" : "inconclusive", observation, authority_effect: "none"});
}

export function assessResearchHypothesis(hypothesis, observations, experiment = null, policy = {}) {
  if (!verifyEvolutionRecord(hypothesis, RESEARCH_HYPOTHESIS_SCHEMA).ok) return fail("hypothesis-assessment", ["evolution.hypothesis-invalid"]);
  if (!Array.isArray(observations) || observations.some((row) => !verifyEvolutionRecord(row, HYPOTHESIS_OBSERVATION_SCHEMA).ok || row.hypothesis_ref !== hypothesis.record_id)) return fail("hypothesis-assessment", ["evolution.hypothesis-observation-invalid"]);
  if (experiment !== null && (!verifyEvolutionRecord(experiment, RESEARCH_EXPERIMENT_SCHEMA).ok || experiment.hypothesis_ref !== hypothesis.record_id)) return fail("hypothesis-assessment", ["evolution.hypothesis-experiment-invalid"]);
  const minimumReplications = Number.isSafeInteger(policy.minimum_replications) && policy.minimum_replications > 0 ? policy.minimum_replications : 2;
  const minimumExperimentSupport = Number.isSafeInteger(policy.minimum_experiment_support) && policy.minimum_experiment_support > 0 ? policy.minimum_experiment_support : 1;
  const supporting = observations.filter((row) => row.observation_kind === "supporting");
  const counter = observations.filter((row) => row.observation_kind === "counterevidence");
  const experimentSupport = supporting.filter((row) => row.phase === "experiment");
  let disposition;
  let reasonCodes;
  let nextAction;
  if (counter.length > 0) {
    disposition = "revise-hypothesis";
    reasonCodes = ["learning.counterevidence-observed"];
    nextAction = "Revise or reject the hypothesis before proposing a technique.";
  } else if (supporting.length < minimumReplications) {
    disposition = "collect-replications";
    reasonCodes = ["learning.replications-insufficient"];
    nextAction = "Collect independent benchmark replications using the registered experiment.";
  } else if (experiment === null || experimentSupport.length < minimumExperimentSupport) {
    disposition = "run-experiment";
    reasonCodes = ["learning.controlled-experiment-required"];
    nextAction = "Run the registered baseline-versus-treatment experiment.";
  } else {
    disposition = "candidate-supported";
    reasonCodes = ["learning.minimum-evidence-met"];
    nextAction = "Materialize a TechniqueCandidate and evaluate it through the existing variant benchmark path.";
  }
  return freeze({ok: true, decision: createLearningDecision({hypothesis_ref: hypothesis.record_id, observation_refs: observations.map((row) => row.record_id), experiment_ref: experiment?.record_id, disposition, reason_codes: reasonCodes, supporting_count: supporting.length, counterevidence_count: counter.length, experiment_support_count: experimentSupport.length, next_action: nextAction}), authority_effect: "none"});
}

export function runHypothesisLearningCycle({runtime, hypothesis, observations = [], policy = {}} = {}) {
  if (!runtime || typeof runtime.append !== "function") throw new TypeError("Hypothesis learning cycle requires an evolution runtime.");
  const checked = verifyEvolutionRecord(hypothesis, RESEARCH_HYPOTHESIS_SCHEMA);
  if (!checked.ok) return checked;
  if (!Array.isArray(observations) || observations.some((observation) => !verifyEvolutionRecord(observation, HYPOTHESIS_OBSERVATION_SCHEMA).ok || observation.hypothesis_ref !== hypothesis.record_id)) return fail("hypothesis-cycle", ["evolution.hypothesis-observation-invalid"]);
  const appendedHypothesis = runtime.append(hypothesis);
  if (!appendedHypothesis.ok) return appendedHypothesis;
  for (const observation of observations) {
    const appended = runtime.append(observation);
    if (!appended.ok) return appended;
  }
  const template = hypothesis.experiment_template;
  const experiment = createResearchExperiment({
    hypothesis_ref: hypothesis.record_id,
    research_question: template.research_question,
    baseline_ref: template.baseline_ref,
    treatment_ref: template.treatment_ref,
    metrics: hypothesis.metrics,
    dataset_refs: template.dataset_refs,
    required_repetitions: template.required_repetitions,
    success_criteria: template.success_criteria,
    stop_conditions: template.stop_conditions,
    observation_refs: observations.map((row) => row.record_id),
  });
  const appendedExperiment = runtime.append(experiment);
  if (!appendedExperiment.ok) return appendedExperiment;
  const assessed = assessResearchHypothesis(hypothesis, observations, experiment, policy);
  if (!assessed.ok) return assessed;
  const appendedDecision = runtime.append(assessed.decision);
  if (!appendedDecision.ok) return appendedDecision;
  const sealed = runtime.sealCycle({stage: "hypothesis-learning", hypothesis_ref: hypothesis.record_id, experiment_ref: experiment.record_id, decision_ref: assessed.decision.record_id});
  return freeze({schema_version: "are.hypothesis-learning-cycle-result/v1", ok: true, hypothesis, observations, experiment, decision: assessed.decision, sealed, authority_effect: "none"});
}

export function createTechniqueCandidate(input) {
  if (!object(input) || !text(input.target_ref) || !text(input.research_result_ref) || !text(input.mechanism) || !text(input.integration_point)) throw new TypeError("Technique candidate requires target, research result, mechanism, and integration point.");
  return seal(TECHNIQUE_CANDIDATE_SCHEMA, {
    target_ref: input.target_ref.trim(),
    research_result_ref: input.research_result_ref.trim(),
    mechanism: input.mechanism.trim(),
    integration_point: input.integration_point.trim(),
    required_dependencies: uniqueText(input.required_dependencies),
    expected_observations: uniqueText(input.expected_observations),
    limitations: uniqueText(input.limitations),
  });
}

export function createReproductionTrial(input) {
  if (!object(input) || !text(input.technique_ref) || !text(input.environment_ref) || !text(input.protocol_ref) || !["reproduced", "partially-reproduced", "not-reproduced", "not-evaluable"].includes(input.outcome)) throw new TypeError("Reproduction trial requires technique, environment, protocol, and a supported outcome.");
  return seal(REPRODUCTION_TRIAL_SCHEMA, {
    technique_ref: input.technique_ref.trim(),
    environment_ref: input.environment_ref.trim(),
    protocol_ref: input.protocol_ref.trim(),
    dependency_versions: canonicalizeJson(object(input.dependency_versions) ? input.dependency_versions : {}),
    expected_observations: uniqueText(input.expected_observations),
    actual_observations: uniqueText(input.actual_observations),
    deviations: uniqueText(input.deviations),
    outcome: input.outcome,
  });
}

export function createEngineVariant(input) {
  if (!object(input) || !text(input.baseline_ref) || !text(input.source_tree_digest) || !text(input.build_environment_ref)) throw new TypeError("Engine variant requires baseline, source tree digest, and build environment.");
  const techniqueRefs = uniqueText(input.technique_refs);
  const reproductionRefs = uniqueText(input.reproduction_refs);
  if (techniqueRefs.length === 0 || reproductionRefs.length === 0) throw new TypeError("Engine variant requires technique and reproduction references.");
  return seal(ENGINE_VARIANT_SCHEMA, {
    baseline_ref: input.baseline_ref.trim(),
    source_tree_digest: input.source_tree_digest.trim(),
    build_environment_ref: input.build_environment_ref.trim(),
    interface_version: text(input.interface_version) ? input.interface_version.trim() : "are-evolution/v1",
    technique_refs: techniqueRefs,
    reproduction_refs: reproductionRefs,
    changed_paths: uniqueText(input.changed_paths),
    change_digest: text(input.change_digest) ? input.change_digest.trim() : digest(uniqueText(input.changed_paths)),
  });
}

function metricsPass(direction, candidate, baseline, minimumDelta) {
  return direction === "lower" ? baseline - candidate >= minimumDelta : candidate - baseline >= minimumDelta;
}

export function createVariantComparison(input) {
  if (!object(input) || !text(input.variant_ref) || !text(input.baseline_ref) || !text(input.target_ref) || !text(input.manifest_ref) || !text(input.environment_ref)) throw new TypeError("Variant comparison requires variant, baseline, target, manifest, and environment references.");
  if (!object(input.fitness) || !["higher", "lower"].includes(input.fitness.direction) || !finite(input.fitness.minimum_delta)) throw new TypeError("Variant comparison requires a valid fitness rule.");
  if (!object(input.baseline_metrics) || !object(input.candidate_metrics)) throw new TypeError("Variant comparison requires baseline and candidate metrics.");
  const metric = input.fitness.target_metric;
  const baseline = input.baseline_metrics[metric];
  const candidate = input.candidate_metrics[metric];
  if (!text(metric) || !finite(baseline) || !finite(candidate)) throw new TypeError("Variant comparison target metric is missing from the metric vectors.");
  const reasons = [];
  if (!metricsPass(input.fitness.direction, candidate, baseline, input.fitness.minimum_delta)) reasons.push("fitness.target-not-improved");
  for (const [name, tolerance] of Object.entries(input.fitness.protected_quality ?? {})) {
    if (!finite(tolerance) || !finite(input.baseline_metrics[name]) || !finite(input.candidate_metrics[name]) || input.candidate_metrics[name] < input.baseline_metrics[name] - tolerance) reasons.push(`fitness.quality-regression:${name}`);
  }
  for (const [name, ratio] of Object.entries(input.fitness.maximum_regression_ratio ?? {})) {
    if (!finite(ratio) || !finite(input.baseline_metrics[name]) || !finite(input.candidate_metrics[name]) || input.candidate_metrics[name] > input.baseline_metrics[name] * (1 + ratio)) reasons.push(`fitness.performance-regression:${name}`);
  }
  if (input.safety_passed !== true) reasons.push("fitness.safety-failed");
  if (input.determinism_passed !== true) reasons.push("fitness.determinism-failed");
  if (input.holdout_passed !== true) reasons.push("fitness.holdout-failed");
  return seal(VARIANT_COMPARISON_SCHEMA, {
    variant_ref: input.variant_ref.trim(),
    baseline_ref: input.baseline_ref.trim(),
    target_ref: input.target_ref.trim(),
    manifest_ref: input.manifest_ref.trim(),
    environment_ref: input.environment_ref.trim(),
    baseline_metrics: canonicalizeJson(input.baseline_metrics),
    candidate_metrics: canonicalizeJson(input.candidate_metrics),
    fitness: canonicalizeJson(input.fitness),
    safety_passed: input.safety_passed === true,
    determinism_passed: input.determinism_passed === true,
    holdout_passed: input.holdout_passed === true,
    run_refs: uniqueText(input.run_refs),
    outcome: reasons.length === 0 ? "KEEP" : "REJECT",
    reason_codes: reasons.sort(),
  });
}

export function createUpgradeDecision(input) {
  if (!object(input) || !text(input.current_version_ref) || !text(input.candidate_version_ref) || !text(input.comparison_ref) || !["recommend-only", "controlled-local"].includes(input.mode)) throw new TypeError("Upgrade decision requires versions, comparison, and mode.");
  const eligible = input.comparison_outcome === "KEEP" && input.required_keep_streak_met === true && input.reproduction_passed === true && input.holdout_passed === true;
  const disposition = !eligible ? "retain-current" : input.mode === "recommend-only" ? "recommend-candidate" : input.activation_enabled === true ? "activate-candidate" : "block";
  return seal(UPGRADE_DECISION_SCHEMA, {
    current_version_ref: input.current_version_ref.trim(),
    candidate_version_ref: input.candidate_version_ref.trim(),
    comparison_ref: input.comparison_ref.trim(),
    mode: input.mode,
    required_keep_streak_met: input.required_keep_streak_met === true,
    reproduction_passed: input.reproduction_passed === true,
    holdout_passed: input.holdout_passed === true,
    activation_enabled: input.activation_enabled === true,
    disposition,
    predecessor_ref: input.current_version_ref.trim(),
    rollback_target_ref: input.current_version_ref.trim(),
    canary_policy_ref: text(input.canary_policy_ref) ? input.canary_policy_ref.trim() : null,
    reason_codes: !eligible ? ["upgrade.fitness-incomplete"] : disposition === "block" ? ["upgrade.activation-disabled"] : [],
  });
}

function targetMetricForSignal(signal, targetProfile) {
  return targetProfile.signal_kinds.includes(signal.kind) && (targetProfile.scope === undefined || targetProfile.scope === signal.scope);
}

export function selectImprovementTarget(signals, targetProfiles, options = {}) {
  if (!Array.isArray(signals) || !Array.isArray(targetProfiles)) return fail("target-selection", ["evolution.target-selection-input-invalid"]);
  const minimum = Number.isSafeInteger(options.minimum_signal_count) ? options.minimum_signal_count : 1;
  const candidates = [];
  for (const profile of targetProfiles) {
    if (!object(profile) || !text(profile.target_key) || !Array.isArray(profile.signal_kinds) || !text(profile.metric) || !["higher", "lower"].includes(profile.direction) || !finite(profile.threshold)) continue;
    const matching = signals.filter((signal) => verifyEvolutionRecord(signal, IMPROVEMENT_SIGNAL_SCHEMA).ok && targetMetricForSignal(signal, profile));
    if (matching.length < minimum) continue;
    candidates.push(createImprovementTarget({...profile, signal_refs: matching.map((signal) => signal.record_id)}));
  }
  candidates.sort((left, right) => left.priority - right.priority || left.target_key.localeCompare(right.target_key) || left.record_id.localeCompare(right.record_id));
  return freeze({ok: true, disposition: candidates.length === 0 ? "no-target" : "selected", target: candidates[0] ?? null, candidates, authority_effect: "none"});
}

export async function runResearchScout(target, providers, options = {}) {
  if (!verifyEvolutionRecord(target, IMPROVEMENT_TARGET_SCHEMA).ok) return fail("research-scout", ["evolution.target-invalid"]);
  if (options.enabled !== true) return freeze({ok: true, disposition: "disabled", results: [], provider_calls: 0, authority_effect: "none"});
  if (!Array.isArray(providers) || providers.length === 0) return freeze({ok: true, disposition: "no-providers", results: [], provider_calls: 0, authority_effect: "none"});
  const maximum = Number.isSafeInteger(options.maximum_results_per_provider) ? options.maximum_results_per_provider : 20;
  const ordered = [...providers].sort((left, right) => String(left.id).localeCompare(String(right.id)));
  const results = [];
  let providerCalls = 0;
  for (const provider of ordered) {
    if (!text(provider?.id) || typeof provider.search !== "function") return fail("research-scout", ["evolution.research-provider-invalid"]);
    providerCalls += 1;
    const rows = await provider.search(freeze({target, authority_effect: "none"}));
    if (!Array.isArray(rows)) return fail("research-scout", ["evolution.research-provider-result-invalid"]);
    for (const row of rows.slice(0, maximum)) results.push(createResearchResult({...row, target_ref: target.record_id, provider_id: provider.id}));
  }
  const unique = [...new Map(results.map((result) => [result.record_id, result])).values()].sort((left, right) => left.record_id.localeCompare(right.record_id));
  return freeze({ok: true, disposition: "completed", results: unique, provider_calls: providerCalls, authority_effect: "none"});
}

export function createEvolutionRuntime({profile, ledger = null, target_profiles = []} = {}) {
  const verified = verifyEvolutionProfile(profile);
  if (!verified.ok) throw new TypeError(`Invalid evolution profile: ${verified.reason_codes.join(",")}`);
  const stateLedger = ledger ?? createReasoningStateLedger({ledger_id: `are-evolution:${profile.profile_id}`});
  const records = new Map();

  function append(record) {
    const checked = verifyEvolutionRecord(record);
    if (!checked.ok) return checked;
    const event = stateLedger.append({
      event_kind: `evolution.${record.schema_version.split(".")[1]}`,
      idempotency_key: record.record_id,
      content: record,
      provenance_refs: uniqueText(record.provenance_refs),
    });
    if (!event.ok) return fail("evolution-append", event.reason_codes, event.residue);
    records.set(record.record_id, record);
    return freeze({ok: true, disposition: event.disposition, record, event: event.event, authority_effect: "none"});
  }

  function snapshot() {
    return freeze([...records.values()].sort((left, right) => left.record_id.localeCompare(right.record_id)));
  }

  function selectTarget() {
    const signals = snapshot().filter((record) => record.schema_version === IMPROVEMENT_SIGNAL_SCHEMA);
    const selected = selectImprovementTarget(signals, target_profiles, profile.target_selection);
    if (selected.ok && selected.target) append(selected.target);
    return selected;
  }

  function sealCycle(frontier = {}) {
    const epoch = sealReasoningStateEpoch(stateLedger, {consumer_ref: "are-evolution-runtime", frontier});
    if (!epoch.ok) return fail("cycle-seal", epoch.reason_codes, epoch.residue);
    const cycle = seal(EVOLUTION_CYCLE_SCHEMA, {profile_id: profile.profile_id, epoch_id: epoch.value.epoch_id, epoch_digest: epoch.value.epoch_digest, frontier: canonicalizeJson(frontier)});
    records.set(cycle.record_id, cycle);
    return freeze({ok: true, cycle, epoch: epoch.value, authority_effect: "none"});
  }

  function replay(cycle) {
    const checked = verifyEvolutionRecord(cycle, EVOLUTION_CYCLE_SCHEMA);
    if (!checked.ok) return checked;
    const replayed = replayReasoningStateEpoch(stateLedger, {schema_version: "are.reasoning-state-epoch/v1", ledger_id: stateLedger.inspect().ledger_id, consumer_ref: "are-evolution-runtime", request_ref: null, event_digests: stateLedger.snapshot().map((event) => event.event_digest), event_set_digest: digest(stateLedger.snapshot().map((event) => event.event_digest)), selected_dependencies: [], context_envelope_digest: null, frontier: cycle.frontier, authority_effect: "none", epoch_id: cycle.epoch_id, epoch_digest: cycle.epoch_digest});
    return replayed;
  }

  return Object.freeze({
    append,
    appendSignal: (input) => append(createImprovementSignal(input)),
    appendRetention: (input) => append(createImprovementRetention(input)),
    appendResearchResult: (input) => append(createResearchResult(input)),
    appendHypothesis: (input) => append(createResearchHypothesis(input)),
    appendHypothesisObservation: (input) => append(createHypothesisObservation(input)),
    appendResearchExperiment: (input) => append(createResearchExperiment(input)),
    appendLearningDecision: (input) => append(createLearningDecision(input)),
    appendTechnique: (input) => append(createTechniqueCandidate(input)),
    appendReproduction: (input) => append(createReproductionTrial(input)),
    appendVariant: (input) => append(createEngineVariant(input)),
    appendComparison: (input) => append(createVariantComparison(input)),
    appendUpgradeDecision: (input) => append(createUpgradeDecision({...input, mode: input.mode ?? profile.upgrade.mode})),
    selectTarget,
    snapshot,
    sealCycle,
    replay,
    inspect: () => freeze({profile_id: profile.profile_id, record_count: records.size, ledger: stateLedger.inspect(), authority_effect: "none"}),
    ledger: stateLedger,
  });
}

export {assessInteractionLearningProgress, projectInteractionLearningToHypothesis, createInteractionEvolutionAdapter} from "./src/interaction-learning.mjs";
