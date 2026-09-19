import {readFileSync, readdirSync, statSync} from "node:fs";
import {resolve} from "node:path";

import {
  appendReasoningCounterevidence,
  createMemoryReasoningStateSink,
  createReasoningStateLedger,
  deriveReasoningReplayFixture,
  executeReasoningStateTransition,
  planReasoningStateTransition,
  sealReasoningStateEpoch,
  verifyReasoningStateTransitionReceipt,
} from "../../../packages/reasoning-state-runtime/index.mjs";
import {runCoreBenchmark} from "./core.mjs";
import {runIntegrationBenchmark} from "./integration.mjs";
import {ratio, repositoryRoot, sha256} from "./common.mjs";

function allCases(evidence) {
  return [
    ...(evidence.core.cases.routing ?? []),
    ...(evidence.core.cases.context ?? []),
    ...(evidence.integration.cases.lifecycle ?? []),
    ...(evidence.integration.cases.failure_safety ?? []),
  ];
}

function caseRate(evidence, ids) {
  const selected = allCases(evidence).filter((entry) => ids.includes(entry.scenario_id));
  return ratio(selected.filter((entry) => entry.passed).length, selected.length);
}

export function scoreVector(evidence) {
  const failure = evidence.integration.cases.failure_safety ?? [];
  const lifecycle = evidence.integration.cases.lifecycle ?? [];
  return {
    safety: {
      failure_safety_rate: ratio(failure.filter((entry) => entry.passed).length, failure.length),
      lifecycle_rate: ratio(lifecycle.filter((entry) => entry.passed).length, lifecycle.length),
      false_direct_ambiguities: evidence.core.summary.false_direct_ambiguities,
      determinism_mismatches: evidence.core.summary.determinism_mismatches,
      authority_violations: Number.isSafeInteger(evidence.authority_measurement?.violations) ? evidence.authority_measurement.violations : null,
      authority_observed: evidence.authority_measurement?.observed === true
    },
    quality: {
      route_accuracy: evidence.core.summary.route_accuracy,
      definition_recall: evidence.core.summary.definition_recall,
      context_precision: evidence.core.summary.context_precision
    },
    performance: {
      route_p95_ms: evidence.core.metrics.route.p95_ms,
      request_selection_p95_ms: evidence.core.metrics.request_selection.p95_ms,
      preflight_p95_ms: evidence.core.metrics.preflight.p95_ms
    }
  };
}

export function targetValue(evidence, target) {
  if (target.metric === "case_pass_rate") return caseRate(evidence, target.case_ids);
  if (Object.hasOwn(evidence.core.summary, target.metric)) return evidence.core.summary[target.metric];
  if (target.metric === "route_p95_ms") return evidence.core.metrics.route.p95_ms;
  throw new Error(`Unsupported improvement metric: ${target.metric}`);
}

export async function collectImprovementEvidence(benchmark, options = {}) {
  const fast = options.fast === true;
  const sampling = benchmark.profile.improvement_loop.fast_sampling;
  const coreOptions = fast ? {...sampling, enforce_performance: false} : {};
  const core = await runCoreBenchmark(benchmark, coreOptions);
  const integration = await runIntegrationBenchmark(benchmark);
  const authorityCases = integration.cases.failure_safety ?? [];
  return {sampling_mode: fast ? "fast" : "full", core, integration, authority_measurement: {observed: true, violations: authorityCases.filter((entry) => !entry.passed).length, case_ids: authorityCases.map((entry) => entry.scenario_id).sort(), basis: "explicit-failure-safety-cases"}};
}

export function diagnoseEvidence(benchmark, evidence) {
  const targets = benchmark.profile.improvement_loop.targets;
  return Object.entries(targets).map(([targetId, target]) => {
    const value = targetValue(evidence, target);
    const failedCases = allCases(evidence).filter((entry) => target.case_ids.includes(entry.scenario_id) && !entry.passed).map((entry) => entry.scenario_id);
    const threshold = target.metric === "route_accuracy" ? benchmark.profile.thresholds.route_accuracy
      : target.metric === "context_precision" ? benchmark.profile.thresholds.context_precision
      : target.metric === "route_p95_ms" ? benchmark.profile.thresholds.route_p95_ms
      : 1;
    const meetsTarget = target.direction === "lower" ? value <= threshold : value >= threshold;
    return {target_id: targetId, priority: target.priority, metric: target.metric, value, threshold, meets_target: meetsTarget, failed_cases: failedCases, classification: targetId === "routing-accuracy" ? "mixed-engine-and-oracle-review" : "candidate-engine-defect", mutation_allowlist: target.mutation_allowlist};
  }).sort((a, b) => Number(a.meets_target) - Number(b.meets_target) || a.priority - b.priority);
}

function safetyComparison(baseline, candidate) {
  return {
    failure_safety: candidate.safety.failure_safety_rate === 1 && candidate.safety.failure_safety_rate >= baseline.safety.failure_safety_rate,
    lifecycle: candidate.safety.lifecycle_rate === 1 && candidate.safety.lifecycle_rate >= baseline.safety.lifecycle_rate,
    ambiguity: candidate.safety.false_direct_ambiguities <= baseline.safety.false_direct_ambiguities && candidate.safety.false_direct_ambiguities === 0,
    determinism: candidate.safety.determinism_mismatches <= baseline.safety.determinism_mismatches && candidate.safety.determinism_mismatches === 0,
    authority: baseline.safety.authority_observed === true && candidate.safety.authority_observed === true && candidate.safety.authority_violations !== null && candidate.safety.authority_violations <= baseline.safety.authority_violations && candidate.safety.authority_violations === 0
  };
}

export function compareCandidate(profile, targetId, baselineEvidence, candidateEvidence) {
  const loop = profile.improvement_loop;
  const target = loop.targets[targetId];
  if (!target) throw new Error(`Unknown target: ${targetId}`);
  if (baselineEvidence.sampling_mode !== candidateEvidence.sampling_mode) return {keep: false, reason_codes: ["improvement.sampling-mode-mismatch"]};
  const baseline = scoreVector(baselineEvidence);
  const candidate = scoreVector(candidateEvidence);
  const safety = safetyComparison(baseline, candidate);
  const baselineTarget = targetValue(baselineEvidence, target);
  const candidateTarget = targetValue(candidateEvidence, target);
  const delta = target.direction === "lower" ? baselineTarget - candidateTarget : candidateTarget - baselineTarget;
  const threshold = target.metric === "route_accuracy" ? profile.thresholds.route_accuracy
    : target.metric === "context_precision" ? profile.thresholds.context_precision
    : target.metric === "route_p95_ms" ? profile.thresholds.route_p95_ms
    : 1;
  const targetAlreadyMet = target.direction === "lower" ? baselineTarget <= threshold : baselineTarget >= threshold;
  const targetImproved = delta >= loop.minimum_quality_delta || (targetAlreadyMet && delta >= 0);
  const qualityChecks = Object.fromEntries(Object.entries(candidate.quality).map(([metric, value]) => [metric, metric === target.metric || value >= baseline.quality[metric] - loop.non_target_quality_tolerance]));
  const performanceChecks = Object.fromEntries(Object.entries(candidate.performance).map(([metric, value]) => [metric, candidateEvidence.sampling_mode === "fast" || metric === target.metric || value <= baseline.performance[metric] * (1 + loop.latency_regression_ratio)]));
  const reasonCodes = [];
  if (!Object.values(safety).every(Boolean)) reasonCodes.push("improvement.safety-regression");
  if (!targetImproved) reasonCodes.push("improvement.target-not-improved");
  if (!Object.values(qualityChecks).every(Boolean)) reasonCodes.push("improvement.non-target-quality-regression");
  if (!Object.values(performanceChecks).every(Boolean)) reasonCodes.push("improvement.latency-regression");
  return {keep: reasonCodes.length === 0, reason_codes: reasonCodes, target: {target_id: targetId, metric: target.metric, direction: target.direction, baseline: baselineTarget, candidate: candidateTarget, delta}, safety_checks: safety, quality_checks: qualityChecks, performance_checks: performanceChecks, baseline_score: baseline, candidate_score: candidate};
}

function mutationSnapshot(target) {
  return target.mutation_allowlist.map((path) => {
    const absolute = resolve(repositoryRoot, path);
    if (!absolute.startsWith(`${repositoryRoot}/`)) throw new Error(`Mutation path escapes repository: ${path}`);
    try { return {path, sha256: sha256(readFileSync(absolute))}; }
    catch { return {path, sha256: null, unreadable: true}; }
  });
}

function walkFiles(relativeRoot, excludedPrefixes) {
  const absoluteRoot = resolve(repositoryRoot, relativeRoot);
  const selected = [];
  function visit(absolute) {
    for (const name of readdirSync(absolute).sort()) {
      const child = resolve(absolute, name);
      const relative = child.slice(repositoryRoot.length + 1);
      if (excludedPrefixes.some((prefix) => relative === prefix || relative.startsWith(`${prefix}/`))) continue;
      const metadata = statSync(child);
      if (metadata.isDirectory()) visit(child);
      else if (metadata.isFile()) selected.push(relative);
    }
  }
  visit(absoluteRoot);
  return selected;
}

function scopeSnapshot(profile) {
  const loop = profile.improvement_loop;
  const roots = loop.mutation_scope_roots ?? ["cyberAlchemy-v2/implementation/agent-reasoning-engine"];
  const exclusions = loop.mutation_scope_exclusions ?? ["cyberAlchemy-v2/implementation/agent-reasoning-engine/benchmarks/real-reasoning-v1/runs"];
  return [...new Set(roots.flatMap((root) => walkFiles(root, exclusions)))].sort().map((path) => ({path, sha256: sha256(readFileSync(resolve(repositoryRoot, path)))}));
}

function changedPaths(before, after) {
  const prior = new Map((before ?? []).map((entry) => [entry.path, entry.sha256]));
  const current = new Map((after ?? []).map((entry) => [entry.path, entry.sha256]));
  return [...new Set([...prior.keys(), ...current.keys()])].filter((path) => prior.get(path) !== current.get(path)).sort();
}

function iterationMaterial(report) {
  const {iteration_id: _iterationId, iteration_digest: _iterationDigest, observed_at: _observedAt, ...material} = report;
  return material;
}

function iteration(mode, targetId, status, fields = {}) {
  const {observed_at: suppliedObservation, ...semanticFields} = fields;
  const material = {schema_version: "are.reasoning-improvement-iteration/v1", mode, target_id: targetId, status, evidence_digest: sha256(semanticFields.evidence ?? semanticFields.comparison ?? semanticFields), ...semanticFields, authority_effect: "none", claim_limit: "Candidate improvement evidence only; no source mutation, acceptance, conformance, publication, deployment, or effect authority."};
  const iterationDigest = sha256(material);
  return {iteration_id: `are-improvement:${iterationDigest}`, iteration_digest: iterationDigest, observed_at: suppliedObservation ?? new Date().toISOString(), ...material};
}

export function verifyImprovementReport(report) {
  const reasons = [];
  if (report?.schema_version !== "are.reasoning-improvement-iteration/v1") reasons.push("improvement.report-schema-invalid");
  if (report?.authority_effect !== "none") reasons.push("improvement.report-authority-invalid");
  const expected = report && typeof report === "object" ? sha256(iterationMaterial(report)) : null;
  if (report?.iteration_digest !== expected) reasons.push("improvement.report-digest-invalid");
  if (report?.iteration_id !== `are-improvement:${expected}`) reasons.push("improvement.report-id-invalid");
  if (report?.evidence && report.evidence_digest !== sha256(report.evidence)) reasons.push("improvement.report-evidence-digest-invalid");
  return {ok: reasons.length === 0, reason_codes: [...new Set(reasons)].sort(), digest: expected, authority_effect: "none"};
}

export async function diagnoseImprovement(benchmark, options = {}) {
  const evidence = await collectImprovementEvidence(benchmark, options);
  const findings = diagnoseEvidence(benchmark, evidence);
  return iteration("diagnose", null, "DIAGNOSED", {benchmark_profile_digest: sha256(benchmark.profile), sampling_mode: evidence.sampling_mode, score_vector: scoreVector(evidence), findings, recommended_target: findings.find((entry) => !entry.meets_target)?.target_id ?? null, evidence});
}

export async function prepareIteration(benchmark, targetId, options = {}) {
  const diagnosis = options.baseline ?? await diagnoseImprovement(benchmark, options);
  const selected = targetId ?? diagnosis.recommended_target;
  const target = benchmark.profile.improvement_loop.targets[selected];
  if (!target) return iteration("iterate", selected ?? null, "BLOCKED", {reason_codes: ["improvement.target-required"]});
  return iteration("iterate", selected, "READY_FOR_CHANGE", {benchmark_profile_digest: sha256(benchmark.profile), sampling_mode: diagnosis.sampling_mode, baseline_iteration_id: diagnosis.iteration_id, baseline_digest: diagnosis.iteration_digest ?? sha256(diagnosis), score_vector: diagnosis.score_vector, evidence: diagnosis.evidence, source_snapshot_before: mutationSnapshot(target), scope_snapshot_before: scopeSnapshot(benchmark.profile), target: {...target, target_id: selected}, next_command: `node bin/improve.mjs --mode verify-candidate --target ${selected} --baseline <this-report>`});
}

function materializeCandidateReasoningState(baselineReport, targetId, candidateDigest, comparison) {
  const ledger = createReasoningStateLedger({ledger_id: `reasoning:improvement:${sha256({baseline: baselineReport.iteration_digest, targetId})}`, sink: createMemoryReasoningStateSink()});
  const baseline = ledger.append({event_kind: "improvement-baseline-bound", idempotency_key: `improvement-baseline:${baselineReport.iteration_digest}`, content: {baseline_iteration_id: baselineReport.iteration_id, baseline_iteration_digest: baselineReport.iteration_digest, benchmark_profile_digest: baselineReport.benchmark_profile_digest, target_id: targetId}});
  const baseEpoch = sealReasoningStateEpoch(ledger, {event_digests: [baseline.event.event_digest], consumer_ref: "are:improvement-loop", request_ref: targetId, selected_dependencies: baselineReport.source_snapshot_before, frontier: {kind: "improvement-baseline", iteration_digest: baselineReport.iteration_digest}});
  const candidate = ledger.append({event_kind: "improvement-candidate-observed", idempotency_key: `improvement-candidate:${candidateDigest}:${sha256(comparison)}`, content: {candidate_digest: candidateDigest, comparison}});
  const additional = [candidate.event.event_digest];
  let counterevidence = null;
  if (!comparison.keep) {
    const recorded = appendReasoningCounterevidence(ledger, {claim_ref: `improvement:${targetId}:keep`, evidence_ref: `comparison:${sha256(comparison)}`, source_identity: `candidate:${candidateDigest}`, source_digest: candidateDigest, content: {reason_codes: comparison.reason_codes}});
    if (!recorded.ok) throw new Error(`Counterevidence materialization failed: ${recorded.reason_codes.join(",")}`);
    counterevidence = recorded.counterevidence;
    additional.push(recorded.event.event_digest);
  }
  const planned = planReasoningStateTransition({current_epoch: baseEpoch.value, requested_action: "branch", branch_ref: `improvement-candidate:${candidateDigest}`, additional_event_digests: additional, boundary: "observation", transition_basis: {target_id: targetId, candidate_digest: candidateDigest}});
  if (!planned.ok) throw new Error(`Improvement transition planning failed: ${planned.reason_codes.join(",")}`);
  const executed = executeReasoningStateTransition(ledger, planned.value);
  if (!executed.ok || !verifyReasoningStateTransitionReceipt(executed.receipt).ok) throw new Error("Improvement transition execution failed");
  const fixture = deriveReasoningReplayFixture(ledger, executed.result.epoch, {fixture_ref: `improvement:${candidateDigest}`});
  if (!fixture.ok) throw new Error(`Improvement replay fixture failed: ${fixture.reason_codes.join(",")}`);
  return {base_epoch: baseEpoch.value, transition_plan: planned.value, transition_receipt: executed.receipt, candidate_epoch: executed.result.epoch, replay_fixture: fixture.value, counterevidence, authority_effect: "none"};
}

export async function verifyCandidate(benchmark, baselineReport, targetId, options = {}) {
  const baselineVerification = verifyImprovementReport(baselineReport);
  if (!baselineVerification.ok) return iteration("verify-candidate", targetId, "BLOCKED", {benchmark_profile_digest: sha256(benchmark.profile), reason_codes: baselineVerification.reason_codes});
  if (!baselineReport?.evidence || !baselineReport?.score_vector || !Array.isArray(baselineReport.source_snapshot_before) || !Array.isArray(baselineReport.scope_snapshot_before)) return iteration("verify-candidate", targetId, "BLOCKED", {benchmark_profile_digest: sha256(benchmark.profile), reason_codes: ["improvement.baseline-evidence-required"]});
  if (!benchmark.profile.improvement_loop.targets[targetId]) return iteration("verify-candidate", targetId ?? null, "BLOCKED", {reason_codes: ["improvement.target-required"]});
  const profileDigest = sha256(benchmark.profile);
  if (baselineReport.benchmark_profile_digest !== profileDigest) return iteration("verify-candidate", targetId, "BLOCKED", {benchmark_profile_digest: profileDigest, reason_codes: ["improvement.benchmark-profile-drift"]});
  const evidence = await collectImprovementEvidence(benchmark, {fast: baselineReport.sampling_mode === "fast"});
  const comparison = compareCandidate(benchmark.profile, targetId, baselineReport.evidence, evidence);
  const target = benchmark.profile.improvement_loop.targets[targetId];
  const currentSnapshot = mutationSnapshot(target);
  const currentScopeSnapshot = scopeSnapshot(benchmark.profile);
  const changed = changedPaths(baselineReport.source_snapshot_before, currentSnapshot);
  const changedScope = changedPaths(baselineReport.scope_snapshot_before, currentScopeSnapshot);
  const allowed = new Set(target.mutation_allowlist);
  const changedOutsideAllowlist = changedScope.filter((path) => !allowed.has(path));
  if (baselineReport.source_snapshot_before && changed.length === 0) {
    comparison.keep = false;
    if (!comparison.reason_codes.includes("improvement.no-allowlisted-source-change")) comparison.reason_codes.push("improvement.no-allowlisted-source-change");
  }
  if (changedOutsideAllowlist.length > 0) {
    comparison.keep = false;
    if (!comparison.reason_codes.includes("improvement.outside-allowlist-change")) comparison.reason_codes.push("improvement.outside-allowlist-change");
  }
  comparison.reason_codes.sort();
  const candidateDigest = sha256({target_id: targetId, benchmark_profile_digest: profileDigest, scope_snapshot: currentScopeSnapshot});
  const reasoningState = materializeCandidateReasoningState(baselineReport, targetId, candidateDigest, comparison);
  return iteration("verify-candidate", targetId, comparison.keep ? "KEEP" : "REJECT", {benchmark_profile_digest: profileDigest, sampling_mode: evidence.sampling_mode, baseline_iteration_id: baselineReport.iteration_id, baseline_digest: baselineReport.iteration_digest, candidate_digest: candidateDigest, source_snapshot_before: baselineReport.source_snapshot_before, source_snapshot_after: currentSnapshot, scope_snapshot_before: baselineReport.scope_snapshot_before, scope_snapshot_after: currentScopeSnapshot, changed_allowlisted_paths: changed, changed_outside_allowlist: changedOutsideAllowlist, comparison, reasoning_state: reasoningState, score_vector: scoreVector(evidence), evidence, next_action: comparison.keep ? "repeat-for-stability" : "revise-or-discard-candidate"});
}

export async function runImprovementLoop(benchmark, baselineReport, targetId, options = {}) {
  const required = benchmark.profile.improvement_loop.required_pass_streak;
  const maximum = options.max_attempts ?? benchmark.profile.improvement_loop.max_attempts;
  const evaluator = options.evaluator ?? ((...args) => verifyCandidate(...args));
  const attempts = [];
  let streak = 0;
  let stableCandidateDigest = null;
  for (let number = 1; number <= maximum && streak < required; number += 1) {
    const result = await evaluator(benchmark, baselineReport, targetId, options);
    let status = result.status;
    if (status === "KEEP" && (!result.candidate_digest || (stableCandidateDigest !== null && result.candidate_digest !== stableCandidateDigest))) status = "REJECT";
    if (status === "KEEP") stableCandidateDigest = result.candidate_digest;
    attempts.push({attempt: number, iteration_id: result.iteration_id, iteration_digest: result.iteration_digest ?? null, candidate_digest: result.candidate_digest ?? null, status, comparison: result.comparison ?? null});
    streak = status === "KEEP" ? streak + 1 : 0;
    if (status !== "KEEP") break;
  }
  return iteration("loop", targetId, streak >= required ? "STABLE" : "REJECT", {benchmark_profile_digest: sha256(benchmark.profile), baseline_iteration_id: baselineReport?.iteration_id ?? null, stable_candidate_digest: stableCandidateDigest, required_pass_streak: required, achieved_pass_streak: streak, max_attempts: maximum, attempts, live_holdout_checkpoint_required: streak >= required, next_action: streak >= required ? "checkpoint-then-run-live-holdout" : "revise-or-discard-candidate"});
}

export function loadImprovementReport(path) {
  const report = JSON.parse(readFileSync(path, "utf8"));
  const verified = verifyImprovementReport(report);
  if (!verified.ok) throw new Error(`Invalid improvement baseline: ${verified.reason_codes.join(",")}`);
  return report;
}
