import {
  FOUNDATIONAL_CONTROL_IDS,
  type DerivedControlFinding,
  type DerivedControlMismatch,
  type DerivedControlReceipt,
  type DerivedControlSetResult,
  type EvaluationFinding,
  type EvidenceState,
  type FoundationalControlId,
  type OperationalEvaluationBundle,
  type OperationalObservation,
} from "../contracts/operational-evidence.js";

const orderedObservations = (
  observations: readonly OperationalObservation[],
): OperationalObservation[] => [...observations].sort((a, b) =>
  a.observation_id.localeCompare(b.observation_id));

const observationRefs = (
  observations: readonly OperationalObservation[],
): readonly string[] => Object.freeze(orderedObservations(observations).map(({ observation_id }) => observation_id));

const derivedFinding = (code: string, detail: string): DerivedControlFinding =>
  Object.freeze({ code, detail });

const receipt = (
  bundle: OperationalEvaluationBundle,
  controlId: FoundationalControlId,
  state: EvidenceState,
  observations: readonly OperationalObservation[],
  findings: readonly DerivedControlFinding[],
  evaluatedAt: string,
): DerivedControlReceipt => Object.freeze({
  schema_version: "domainspec.orodi.derived-control-receipt/v1",
  control_id: controlId,
  state,
  evaluator_id: `domainspec.orodi.${controlId.toLowerCase()}-evaluator`,
  rule_version: "1.0.0-candidate-local",
  observation_refs: observationRefs(observations),
  evaluated_at: evaluatedAt,
  expires_at: bundle.binding.expires_at,
  invalidation_key_digest: bundle.binding.invalidation_key_digest,
  findings: Object.freeze([...findings]),
  authority_effect: "none",
});

const deriveC01 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => receipt(bundle, "C01", "passed", [], [], evaluatedAt);

const deriveC05 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => {
  const observations = orderedObservations(bundle.observations.filter(({ plane }) => plane === "product"));
  if (observations.length === 0) {
    return receipt(bundle, "C05", "missing", observations, [
      derivedFinding("ORODI_C05_PRODUCT_OBSERVATION_MISSING", "C05 requires at least one product observation"),
    ], evaluatedAt);
  }

  const findings: DerivedControlFinding[] = [];
  for (const observation of observations) {
    const allowlist = new Set(observation.attribute_allowlist);
    for (const key of Object.keys(observation.attributes).sort()) {
      if (!allowlist.has(key)) {
        findings.push(derivedFinding(
          "ORODI_C05_ATTRIBUTE_NOT_ALLOWLISTED",
          `${observation.observation_id} attribute ${key} is not allowlisted`,
        ));
      }
    }
    if (observation.cardinality.observed > observation.cardinality.budget) {
      findings.push(derivedFinding(
        "ORODI_C05_CARDINALITY_EXCEEDED",
        `${observation.observation_id} observed cardinality exceeds its budget`,
      ));
    }
  }
  return receipt(bundle, "C05", findings.length === 0 ? "passed" : "failed", observations, findings, evaluatedAt);
};

const deriveC11 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => {
  const observations = orderedObservations(bundle.observations.filter(({ plane, mode }) =>
    plane === "product" && mode === "simulation"));
  if (observations.length === 0) {
    return receipt(bundle, "C11", "not-run", observations, [
      derivedFinding("ORODI_C11_SIMULATION_NOT_RUN", "no product simulation observation exists"),
    ], evaluatedAt);
  }
  const effectObservations = observations.filter(({ deployment_effect }) => deployment_effect);
  if (effectObservations.length > 0) {
    return receipt(bundle, "C11", "failed", observations, [
      derivedFinding(
        "ORODI_C11_SIMULATION_EFFECT_FORBIDDEN",
        `simulation observations claim deployment effects: ${observationRefs(effectObservations).join(", ")}`,
      ),
    ], evaluatedAt);
  }
  return receipt(bundle, "C11", "passed", observations, [], evaluatedAt);
};

const deriveC12 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => {
  const observations = orderedObservations(bundle.observations.filter(({ plane, mode, kind }) =>
    plane === "product" && mode === "live" && kind === "deployment-effect"));
  if (observations.length === 0) {
    return receipt(bundle, "C12", "not-run", observations, [
      derivedFinding("ORODI_C12_LIVE_EFFECT_NOT_RUN", "no live product deployment-effect observation exists"),
    ], evaluatedAt);
  }
  const observedEffects = observations.filter(({ deployment_effect }) => deployment_effect);
  if (observedEffects.length === 0) {
    return receipt(bundle, "C12", "failed", observations, [
      derivedFinding("ORODI_C12_EFFECT_NOT_OBSERVED", "live deployment-effect observations report no effect"),
    ], evaluatedAt);
  }
  if (!observedEffects.some(({ independently_observed }) => independently_observed)) {
    return receipt(bundle, "C12", "invalid", observations, [
      derivedFinding("ORODI_C12_INDEPENDENT_OBSERVATION_MISSING", "a claimed live deployment effect lacks independent observation"),
    ], evaluatedAt);
  }
  return receipt(bundle, "C12", "passed", observations, [], evaluatedAt);
};

const deriveC14 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => {
  const observations = orderedObservations(bundle.observations);
  const at = Date.parse(evaluatedAt);
  const invalidFindings: DerivedControlFinding[] = [];
  if (Date.parse(bundle.binding.created_at) >= Date.parse(bundle.binding.expires_at)) {
    invalidFindings.push(derivedFinding("ORODI_C14_FRESHNESS_WINDOW_INVALID", "binding created_at must precede expires_at"));
  }
  for (const observation of observations) {
    if (Date.parse(observation.observed_at) > at) {
      invalidFindings.push(derivedFinding(
        "ORODI_C14_OBSERVATION_FROM_FUTURE",
        `${observation.observation_id} occurs after the explicit evaluation time`,
      ));
    }
  }
  if (invalidFindings.length > 0) {
    return receipt(bundle, "C14", "invalid", observations, invalidFindings, evaluatedAt);
  }

  const staleFindings: DerivedControlFinding[] = [];
  if (at >= Date.parse(bundle.binding.expires_at)) {
    staleFindings.push(derivedFinding("ORODI_C14_BINDING_STALE", "binding is stale at the explicit evaluation time"));
  }
  for (const observation of observations) {
    if (observation.invalidation_key_digest !== bundle.binding.invalidation_key_digest) {
      staleFindings.push(derivedFinding(
        "ORODI_C14_INVALIDATION_KEY_MISMATCH",
        `${observation.observation_id} does not match the binding invalidation key`,
      ));
    }
  }
  return receipt(bundle, "C14", staleFindings.length === 0 ? "passed" : "stale", observations, staleFindings, evaluatedAt);
};

const deriveC15 = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlReceipt => {
  const observations = orderedObservations(bundle.observations.filter(({ plane }) => plane === "product"));
  if (observations.length === 0) {
    return receipt(bundle, "C15", "missing", observations, [
      derivedFinding("ORODI_C15_PRODUCT_OBSERVATION_MISSING", "C15 requires at least one product observation"),
    ], evaluatedAt);
  }

  const failed: DerivedControlFinding[] = [];
  for (const observation of observations) {
    const telemetry = observation.telemetry;
    if (telemetry.offered !== telemetry.queued + telemetry.rejected) {
      failed.push(derivedFinding(
        "ORODI_C15_OFFERED_ACCOUNTING_FAILED",
        `${observation.observation_id} offered does not equal queued plus rejected`,
      ));
    }
    if (telemetry.queued !== telemetry.exported + telemetry.dropped + telemetry.pending) {
      failed.push(derivedFinding(
        "ORODI_C15_QUEUE_ACCOUNTING_FAILED",
        `${observation.observation_id} queued does not equal exported plus dropped plus pending`,
      ));
    }
    if (telemetry.partial_success > telemetry.exported) {
      failed.push(derivedFinding(
        "ORODI_C15_PARTIAL_SUCCESS_INVALID",
        `${observation.observation_id} partial_success exceeds exported`,
      ));
    }
  }
  if (failed.length > 0) return receipt(bundle, "C15", "failed", observations, failed, evaluatedAt);

  const partial = observations.filter(({ telemetry }) => telemetry.partial_success > 0);
  if (partial.length > 0) {
    return receipt(bundle, "C15", "inconclusive", observations, [
      derivedFinding(
        "ORODI_C15_PARTIAL_SUCCESS_INCONCLUSIVE",
        `partial-success telemetry requires further evidence: ${observationRefs(partial).join(", ")}`,
      ),
    ], evaluatedAt);
  }
  return receipt(bundle, "C15", "passed", observations, [], evaluatedAt);
};

const evaluators: Readonly<Record<FoundationalControlId, (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
) => DerivedControlReceipt>> = Object.freeze({
  C01: deriveC01,
  C05: deriveC05,
  C11: deriveC11,
  C12: deriveC12,
  C14: deriveC14,
  C15: deriveC15,
});

export const invalidDerivedControlSetResult = (
  evaluatedAt: string,
  findings: readonly EvaluationFinding[],
  bindingId = "invalid-binding",
): DerivedControlSetResult => Object.freeze({
  schema_version: "domainspec.orodi.derived-control-set-result/v1",
  validator_id: "domainspec.orodi.foundational-derived-validator",
  validator_version: "1.0.0-candidate-local",
  evidence_lane: "candidate-local-prototype",
  binding_id: bindingId,
  evaluated_at: evaluatedAt,
  verdict: "reject",
  comparison: "unavailable",
  derived_controls: Object.freeze([]),
  mismatches: Object.freeze([]),
  findings: Object.freeze([...findings]),
  authority_effect: "none",
});

export const deriveFoundationalControlSet = (
  bundle: OperationalEvaluationBundle,
  evaluatedAt: string,
): DerivedControlSetResult => {
  const derivedControls = FOUNDATIONAL_CONTROL_IDS.map((controlId) =>
    evaluators[controlId](bundle, evaluatedAt));
  const mismatches: DerivedControlMismatch[] = [];
  for (const controlId of FOUNDATIONAL_CONTROL_IDS) {
    const receipts = bundle.controls.filter(({ control_id }) => control_id === controlId);
    const derived = derivedControls.find(({ control_id }) => control_id === controlId)!;
    if (receipts.length === 0) {
      mismatches.push({
        control_id: controlId,
        claimed_state: null,
        derived_state: derived.state,
        code: "ORODI_DERIVED_CONTROL_CLAIM_MISSING",
      });
      continue;
    }
    if (receipts.length > 1) {
      mismatches.push({
        control_id: controlId,
        claimed_state: receipts[0]!.state,
        derived_state: derived.state,
        code: "ORODI_DERIVED_CONTROL_CLAIM_DUPLICATE",
      });
      continue;
    }
    const claimed = receipts[0]!;
    if (claimed.state !== derived.state) {
      mismatches.push({
        control_id: controlId,
        claimed_state: claimed.state,
        derived_state: derived.state,
        code: "ORODI_DERIVED_CONTROL_STATE_MISMATCH",
      });
    }
  }
  const allPassed = derivedControls.every(({ state }) => state === "passed");
  return Object.freeze({
    schema_version: "domainspec.orodi.derived-control-set-result/v1",
    validator_id: "domainspec.orodi.foundational-derived-validator",
    validator_version: "1.0.0-candidate-local",
    evidence_lane: "candidate-local-prototype",
    binding_id: bundle.binding.binding_id,
    evaluated_at: evaluatedAt,
    verdict: allPassed && mismatches.length === 0 ? "pass" : "reject",
    comparison: mismatches.length === 0 ? "match" : "mismatch",
    derived_controls: Object.freeze(derivedControls),
    mismatches: Object.freeze(mismatches),
    findings: Object.freeze([]),
    authority_effect: "none",
  });
};
