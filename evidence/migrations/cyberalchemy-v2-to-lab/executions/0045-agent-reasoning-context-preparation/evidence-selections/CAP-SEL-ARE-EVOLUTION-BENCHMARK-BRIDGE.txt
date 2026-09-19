import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {
  createEngineVariant,
  createEvolutionRuntime,
  createReproductionTrial,
  createTechniqueCandidate,
  createUpgradeDecision,
  createVariantComparison,
  runResearchScout,
} from "../../../packages/evolution-runtime/index.mjs";
import {diagnoseImprovement, scoreVector} from "./improvement-loop.mjs";

function flatScore(evidence) {
  const vector = scoreVector(evidence);
  return {...vector.quality, ...vector.performance, ...vector.safety};
}

export function benchmarkTargetProfiles(profile) {
  return Object.entries(profile.improvement_loop.targets).map(([targetKey, target]) => ({
    target_key: targetKey,
    signal_kinds: [`${targetKey}-failure`],
    scope: targetKey,
    metric: target.metric,
    direction: target.direction,
    threshold: target.metric === "context_precision" ? profile.thresholds.context_precision
      : target.metric === "route_accuracy" ? profile.thresholds.route_accuracy
      : target.metric === "route_p95_ms" ? profile.thresholds.route_p95_ms : 1,
    priority: target.priority,
    protected_metrics: {
      route_accuracy: profile.improvement_loop.non_target_quality_tolerance,
      definition_recall: profile.improvement_loop.non_target_quality_tolerance,
      context_precision: profile.improvement_loop.non_target_quality_tolerance,
    },
    test_sets: ["development", "regression", "holdout", "performance", "failure-safety"],
    mutation_allowlist: target.mutation_allowlist,
    invalidation_rules: ["benchmark manifest changed", "baseline changed", "target threshold changed"],
  }));
}

export function diagnosisSignals(diagnosis) {
  if (!diagnosis || diagnosis.status !== "DIAGNOSED" || !Array.isArray(diagnosis.findings)) throw new TypeError("A benchmark diagnosis is required.");
  return diagnosis.findings.filter((finding) => !finding.meets_target).map((finding) => ({
    kind: `${finding.target_id}-failure`,
    source_result_ref: diagnosis.iteration_id,
    scope: finding.target_id,
    observed_value: finding.value,
    expected_value: finding.threshold,
    metric: finding.metric,
    provenance_refs: [diagnosis.evidence_digest],
    confidence: 1,
  }));
}

export function createFixtureResearchProvider(path, providerId = "fixture-research") {
  const absolute = path instanceof URL ? fileURLToPath(path) : resolve(path);
  const value = JSON.parse(readFileSync(absolute, "utf8"));
  if (value.schema_version !== "are.research-provider-fixture/v1" || !Array.isArray(value.results)) throw new TypeError("Invalid research-provider fixture.");
  return Object.freeze({
    id: providerId,
    async search({target}) {
      return value.results.filter((result) => result.target_key === target.target_key).map(({target_key: _target, ...result}) => result);
    },
  });
}

function comparisonRecord({benchmark, target, variant, baselineEvidence, candidateEvidence, manifestRef, environmentRef, holdoutPassed}) {
  const baseline = flatScore(baselineEvidence);
  const candidate = flatScore(candidateEvidence);
  return createVariantComparison({
    variant_ref: variant.record_id,
    baseline_ref: variant.baseline_ref,
    target_ref: target.record_id,
    manifest_ref: manifestRef,
    environment_ref: environmentRef,
    baseline_metrics: baseline,
    candidate_metrics: candidate,
    fitness: {
      target_metric: target.metric,
      direction: target.direction,
      minimum_delta: benchmark.profile.improvement_loop.minimum_quality_delta,
      protected_quality: Object.fromEntries(Object.keys(baseline).filter((name) => ["route_accuracy", "definition_recall", "context_precision"].includes(name) && name !== target.metric).map((name) => [name, benchmark.profile.improvement_loop.non_target_quality_tolerance])),
      maximum_regression_ratio: Object.fromEntries(Object.keys(baseline).filter((name) => name.endsWith("_p95_ms") && name !== target.metric).map((name) => [name, benchmark.profile.improvement_loop.latency_regression_ratio])),
    },
    safety_passed: candidate.failure_safety_rate === 1 && candidate.lifecycle_rate === 1 && candidate.false_direct_ambiguities === 0 && candidate.authority_violations === 0,
    determinism_passed: candidate.determinism_mismatches === 0,
    holdout_passed: holdoutPassed === true,
    run_refs: [baselineEvidence.core.result_id, candidateEvidence.core.result_id].filter(Boolean),
  });
}

export async function runBenchmarkEvolutionCycle(benchmark, options = {}) {
  const evolutionProfile = options.evolution_profile;
  const runtime = options.runtime ?? createEvolutionRuntime({profile: evolutionProfile, target_profiles: benchmarkTargetProfiles(benchmark.profile)});
  const diagnosis = options.diagnosis ?? await diagnoseImprovement(benchmark, {fast: options.fast === true});
  for (const signal of diagnosisSignals(diagnosis)) runtime.appendSignal(signal);
  const selected = runtime.selectTarget();
  if (!selected.ok) return selected;
  if (!selected.target) return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "NO_TARGET", diagnosis, runtime: runtime.inspect(), authority_effect: "none"};

  const target = selected.target;
  const research = await runResearchScout(target, options.research_providers ?? [], evolutionProfile.research);
  if (!research.ok || research.results.length === 0) {
    const sealed = runtime.sealCycle({stage: "research", target_ref: target.record_id, disposition: research.disposition});
    return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "BLOCKED", reason_codes: research.reason_codes ?? ["evolution.research-result-required"], diagnosis, target, research, sealed, authority_effect: "none"};
  }
  for (const result of research.results) runtime.append(result);
  const researchResult = research.results[0];
  const technique = createTechniqueCandidate({target_ref: target.record_id, research_result_ref: researchResult.record_id, mechanism: researchResult.mechanism, integration_point: target.mutation_allowlist[0] ?? "unresolved", expected_observations: [researchResult.fit_hypothesis ?? `improve ${target.metric}`], limitations: researchResult.limitations});
  runtime.append(technique);

  if (typeof options.reproduce !== "function") return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "BLOCKED", reason_codes: ["evolution.reproduction-runner-required"], diagnosis, target, research, technique, authority_effect: "none"};
  const reproduction = createReproductionTrial(await options.reproduce({target, technique, research_result: researchResult}));
  runtime.append(reproduction);
  if (reproduction.outcome !== "reproduced") return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "REJECT", reason_codes: ["evolution.technique-not-reproduced"], diagnosis, target, research, technique, reproduction, authority_effect: "none"};

  if (typeof options.build_variant !== "function") return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "BLOCKED", reason_codes: ["evolution.variant-builder-required"], diagnosis, target, research, technique, reproduction, authority_effect: "none"};
  const variant = createEngineVariant(await options.build_variant({target, technique, reproduction}));
  runtime.append(variant);
  if (!options.baseline_evidence || !options.candidate_evidence) return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: "BLOCKED", reason_codes: ["evolution.comparison-evidence-required"], diagnosis, target, research, technique, reproduction, variant, authority_effect: "none"};

  const comparison = comparisonRecord({benchmark, target, variant, baselineEvidence: options.baseline_evidence, candidateEvidence: options.candidate_evidence, manifestRef: options.manifest_ref ?? "benchmark:real-reasoning-v1", environmentRef: options.environment_ref ?? `node:${process.version}`, holdoutPassed: options.holdout_passed});
  runtime.append(comparison);
  const decision = createUpgradeDecision({current_version_ref: variant.baseline_ref, candidate_version_ref: variant.record_id, comparison_ref: comparison.record_id, comparison_outcome: comparison.outcome, required_keep_streak_met: (options.keep_streak ?? 0) >= evolutionProfile.upgrade.required_keep_streak, reproduction_passed: reproduction.outcome === "reproduced", holdout_passed: comparison.holdout_passed, mode: evolutionProfile.upgrade.mode, activation_enabled: options.activation_enabled === true, canary_policy_ref: options.canary_policy_ref ?? null});
  runtime.append(decision);
  const sealed = runtime.sealCycle({stage: "upgrade-decision", target_ref: target.record_id, comparison_ref: comparison.record_id, decision_ref: decision.record_id});
  return {schema_version: "are.benchmark-evolution-cycle-result/v1", status: comparison.outcome === "REJECT" ? "REJECT" : decision.disposition === "recommend-candidate" ? "RECOMMEND" : decision.disposition === "activate-candidate" ? "ACTIVATE" : "BLOCKED", diagnosis, target, research, technique, reproduction, variant, comparison, decision, sealed, runtime: runtime.inspect(), authority_effect: "none"};
}
