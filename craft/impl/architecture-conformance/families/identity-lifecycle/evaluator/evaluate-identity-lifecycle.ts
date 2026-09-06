import {createHash} from "node:crypto";

import {
  canonicalConstructionObservationJson,
  evaluateEntityLifecycleConstructionObservationV1,
  type DeclaredEntityLifecycleConstructionContractV1,
  type EntityLifecycleConstructionDiagnostic,
  type LockedConstructionObserverRefV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import {
  IDENTITY_LIFECYCLE_HOSTILE_CLASSES,
  IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS,
  type IdentityLifecycleDefinitionV1,
  type IdentityLifecycleDenominatorV1,
  type IdentityLifecycleEvaluationV1,
  type IdentityLifecycleFindingCode,
  type IdentityLifecycleFindingV1,
  type IdentityLifecycleObservationV1,
  type IdentityLifecyclePositiveObligation,
} from "../contracts/identity-lifecycle-contracts.js";

export type EvaluateIdentityLifecycleInput = Readonly<{
  definition: IdentityLifecycleDefinitionV1;
  denominator: IdentityLifecycleDenominatorV1;
  observation: IdentityLifecycleObservationV1 | null;
  locked_observer_ref: LockedConstructionObserverRefV1;
}>;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: unknown): string => createHash("sha256")
  .update(canonicalConstructionObservationJson(value), "utf8").digest("hex");

const OBLIGATION_BY_CODE: Readonly<Partial<Record<IdentityLifecycleFindingCode,
IdentityLifecyclePositiveObligation>>> = Object.freeze({
  FAMILY_ENTITY_ROUTE_CONVERGENCE_MISMATCH: "valid-input-one-immutable-snapshot",
  FAMILY_ENTITY_VALIDATOR_BYPASS: "validators-before-construction",
  FAMILY_ENTITY_BASE_VALIDATOR_REMOVED: "validators-before-construction",
  FAMILY_ENTITY_INVALID_INPUT_FORMED_SNAPSHOT:
    "valid-input-one-immutable-snapshot",
  FAMILY_ENTITY_MUTABLE_SNAPSHOT: "valid-input-one-immutable-snapshot",
  FAMILY_ENTITY_COMPLETE_FIELD_EQUALITY: "same-identity-different-state-equal",
  FAMILY_ENTITY_IDENTITY_STABILITY_MISMATCH:
    "lifecycle-transition-preserves-identity",
  FAMILY_ENTITY_IDENTITY_EQUALITY_OR_HASH_MISMATCH:
    "distinct-identities-remain-distinct",
  FAMILY_ENTITY_SNAPSHOT_LEDGER_MISMATCH: "valid-input-one-immutable-snapshot",
});

const finding = (
  code: IdentityLifecycleFindingCode,
  observed: string | null = null,
): IdentityLifecycleFindingV1 => Object.freeze({
  code,
  obligation_id: OBLIGATION_BY_CODE[code] ?? null,
  expected: "owner-declared stable-identity lifecycle contract",
  observed,
});

const codeForDiagnostic = (
  diagnostic: EntityLifecycleConstructionDiagnostic,
): IdentityLifecycleFindingCode => {
  if (diagnostic === "ENTITY_OBSERVATION_DIGEST_MISMATCH") {
    return "FAMILY_ENTITY_OBSERVATION_INTEGRITY_MISMATCH";
  }
  if (diagnostic === "ENTITY_OBSERVER_BINDING_MISMATCH"
      || diagnostic === "ENTITY_OBSERVER_SELF_ISSUED") {
    return "FAMILY_ENTITY_EVIDENCE_NOT_INDEPENDENT";
  }
  if (diagnostic === "ENTITY_DEFINITION_BINDING_MISMATCH") {
    return "FAMILY_ENTITY_DEFINITION_PROVENANCE_MISMATCH";
  }
  if (diagnostic === "ENTITY_FACTORY_BINDING_MISMATCH"
      || diagnostic === "ENTITY_EXTENSION_BINDING_MISMATCH"
      || diagnostic === "ENTITY_EXTENSION_NOT_ADDITIVE") {
    return "FAMILY_ENTITY_FACTORY_BINDING_MISMATCH";
  }
  if (diagnostic === "ENTITY_ROUTE_LEDGER_MISMATCH"
      || diagnostic === "ENTITY_DIRECT_CONSTRUCTOR_BYPASS"
      || diagnostic === "ENTITY_VALID_INPUT_NOT_ONE_SNAPSHOT"
      || diagnostic === "ENTITY_CONSTRUCTION_ORDER_MISMATCH") {
    return "FAMILY_ENTITY_ROUTE_CONVERGENCE_MISMATCH";
  }
  if (diagnostic === "ENTITY_VALIDATOR_BINDING_MISMATCH"
      || diagnostic === "ENTITY_VALIDATOR_ORDER_MISMATCH"
      || diagnostic === "ENTITY_IDENTITY_RESOLUTION_ORDER_MISMATCH"
      || diagnostic === "ENTITY_PER_CALL_VALIDATOR_BYPASS") {
    return "FAMILY_ENTITY_VALIDATOR_BYPASS";
  }
  if (diagnostic === "ENTITY_BASE_VALIDATOR_REMOVED") {
    return "FAMILY_ENTITY_BASE_VALIDATOR_REMOVED";
  }
  if (diagnostic === "ENTITY_IDENTITY_RESOLVER_REPLACED") {
    return "FAMILY_ENTITY_IDENTITY_RESOLVER_REPLACED";
  }
  if (diagnostic === "ENTITY_EXTENSION_CYCLE") {
    return "FAMILY_ENTITY_EXTENSION_CYCLE";
  }
  if (diagnostic === "ENTITY_INVALID_INPUT_FORMED_SNAPSHOT"
      || diagnostic === "ENTITY_FAILURE_CODE_MISMATCH") {
    return "FAMILY_ENTITY_INVALID_INPUT_FORMED_SNAPSHOT";
  }
  if (diagnostic === "ENTITY_SNAPSHOT_MUTABLE") {
    return "FAMILY_ENTITY_MUTABLE_SNAPSHOT";
  }
  if (diagnostic === "ENTITY_COMPLETE_FIELD_EQUALITY") {
    return "FAMILY_ENTITY_COMPLETE_FIELD_EQUALITY";
  }
  if (diagnostic === "ENTITY_IDENTITY_CHANGED_ACROSS_LIFECYCLE"
      || diagnostic === "ENTITY_IDENTITY_COMPONENT_MISMATCH") {
    return "FAMILY_ENTITY_IDENTITY_STABILITY_MISMATCH";
  }
  if (diagnostic === "ENTITY_IDENTITY_EQUALITY_MISMATCH"
      || diagnostic === "ENTITY_IDENTITY_HASH_INCONGRUENT") {
    return "FAMILY_ENTITY_IDENTITY_EQUALITY_OR_HASH_MISMATCH";
  }
  return "FAMILY_ENTITY_SNAPSHOT_LEDGER_MISMATCH";
};

const declaredContract = (
  definition: IdentityLifecycleDefinitionV1,
): DeclaredEntityLifecycleConstructionContractV1 => Object.freeze({
  factory_ref: definition.factories.base,
  extension_factory_ref: definition.factories.extension,
  identity_components: definition.identity_components,
  validators: definition.validators,
  construction_routes: definition.construction_routes,
  direct_constructor_policy: definition.direct_constructor_policy,
  snapshots: definition.snapshots,
  equality_probes: definition.equality_probes,
  validation_failure: definition.validation_failure,
});

export const evaluateIdentityLifecycle = (
  input: EvaluateIdentityLifecycleInput,
): IdentityLifecycleEvaluationV1 => {
  const {definition, denominator, observation,
    locked_observer_ref: lockedObserver} = input;
  const findings: IdentityLifecycleFindingV1[] = [];
  let routeObserved = 0;
  let routeConforming = 0;
  if (observation === null) {
    findings.push(finding("FAMILY_ENTITY_TARGET_OBSERVATION_MISSING", "missing"));
  } else {
    const expectedDefinitionRef = denominator.owner_definition_ref;
    if (canonicalConstructionObservationJson(observation.definition_ref)
        !== canonicalConstructionObservationJson(expectedDefinitionRef)) {
      findings.push(finding("FAMILY_ENTITY_DEFINITION_PROVENANCE_MISMATCH",
        `${observation.definition_ref.definition_id}`
        + `@${observation.definition_ref.sha256}`));
    }
    const transport = evaluateEntityLifecycleConstructionObservationV1({
      locked_observer_ref: lockedObserver,
      locked_definition_ref: expectedDefinitionRef,
      declared_contract: declaredContract(definition),
      observation,
    });
    for (const diagnostic of transport.diagnostics) {
      const code = codeForDiagnostic(diagnostic);
      if (!findings.some((item) => item.code === code)) {
        findings.push(finding(code, diagnostic));
      }
    }
    routeObserved = new Set(observation.route_traces.map(({route_id}) => route_id)).size;
    const routeFailure = transport.diagnostics.some((diagnostic) =>
      diagnostic === "ENTITY_ROUTE_LEDGER_MISMATCH"
      || diagnostic === "ENTITY_DIRECT_CONSTRUCTOR_BYPASS"
      || diagnostic === "ENTITY_VALID_INPUT_NOT_ONE_SNAPSHOT"
      || diagnostic === "ENTITY_VALIDATOR_ORDER_MISMATCH"
      || diagnostic === "ENTITY_IDENTITY_RESOLUTION_ORDER_MISMATCH"
      || diagnostic === "ENTITY_CONSTRUCTION_ORDER_MISMATCH");
    routeConforming = routeFailure ? Math.max(0, routeObserved - 1) : routeObserved;
  }
  const normalized = Object.freeze([...findings].sort((left, right) =>
    compareUtf8(left.code, right.code)));
  const failedObligations = observation === null
    ? new Set<IdentityLifecyclePositiveObligation>(
      IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS,
    )
    : new Set(normalized.flatMap(({obligation_id}) =>
      obligation_id === null ? [] : [obligation_id]));
  const denominatorRef = Object.freeze({
    denominator_id: denominator.denominator_id,
    denominator_sha256: denominator.denominator_sha256,
  });
  const observationRef = Object.freeze({
    observation_id: observation?.observation_id ?? null,
    observation_sha256: observation?.observation_sha256 ?? null,
  });
  return Object.freeze({
    schema_version: "IdentityLifecycleEvaluation/v1" as const,
    evaluation_id: `evaluation.identity-lifecycle.${sha256({denominatorRef,
      observationRef, findings: normalized})}`,
    denominator_ref: denominatorRef,
    observation_ref: observationRef,
    verdict: normalized.length === 0 ? "pass" as const : "fail" as const,
    findings: normalized,
    positive_obligation_accounting: Object.freeze({
      declared: 5 as const,
      passed: IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS.length
        - failedObligations.size,
      failed: failedObligations.size,
      unaccounted: 0 as const,
    }),
    hostile_class_accounting: Object.freeze({
      declared: 7 as const,
      represented: new Set(denominator.semantic_hostile_classes).size,
      unrepresented: IDENTITY_LIFECYCLE_HOSTILE_CLASSES.length
        - new Set(denominator.semantic_hostile_classes).size,
    }),
    construction_route_accounting: Object.freeze({
      declared: 4 as const,
      observed: routeObserved,
      conforming: routeConforming,
      unaccounted: 4 - routeObserved,
    }),
    portable_claim: "owner-bound-stable-identity-lifecycle-transport-proof" as const,
    native_runtime_claim: false as const,
    collision_freedom_claim: false as const,
    authority_effect: "none" as const,
  });
};
