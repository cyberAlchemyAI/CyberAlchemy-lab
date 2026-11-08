import {createHash} from "node:crypto";

import {
  OPERATION_EXPECTED_DIAGNOSTIC,
  OPERATION_HOSTILE_IDS,
  OPERATION_MUTATION_KIND,
  OPERATION_S1_HOSTILE_IDS,
  OPERATION_S1_MUTATION_KIND,
  type OperationHostileFixtureV1,
  type OperationS1HostileFixtureV1,
  type OperationS1ResidueV1,
  type StateChangingActionDefinitionV1,
  type StateChangingActionDenominatorV1,
  type StateChangingActionObservationV1,
  type StateChangingActionObservationSetV1,
} from "../contracts/state-changing-action-contracts.js";

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const exactKeys = (
  value: Record<string, unknown>,
  expected: readonly string[],
): boolean => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  return actual.length === wanted.length &&
    actual.every((key, index) => key === wanted[index]);
};

const sorted = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(sorted);
  if (isRecord(value)) {
    return Object.fromEntries(
      Object.keys(value).sort().map((key) => [key, sorted(value[key])]),
    );
  }
  return value;
};

export const canonicalOperationJson = (value: unknown): string =>
  JSON.stringify(sorted(value));

export const sha256OperationBytes = (value: string | Buffer): string =>
  createHash("sha256").update(value).digest("hex");

export const sha256OperationValue = (value: unknown): string =>
  sha256OperationBytes(canonicalOperationJson(value));

const parseRecord = (raw: string, label: string): Record<string, unknown> => {
  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    throw new Error(`${label}_JSON_INVALID`);
  }
  if (!isRecord(value)) throw new Error(`${label}_SHAPE_INVALID`);
  return value;
};

const stringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) =>
    typeof item === "string" && item.length > 0);

const unique = (values: readonly string[]): boolean =>
  new Set(values).size === values.length;

const SHA256 = /^[a-f0-9]{64}$/u;
const nonEmptyString = (value: unknown): value is string =>
  typeof value === "string" && value.length > 0 &&
  !/[\u0000-\u001f\u007f]/u.test(value);
const primitiveValue = (
  value: unknown,
): value is string | number | boolean | null => value === null ||
  typeof value === "string" || typeof value === "boolean" ||
  (typeof value === "number" && Number.isFinite(value));
const recordWithPrimitiveValues = (
  value: unknown,
): value is Record<string, string | number | boolean | null> =>
  isRecord(value) && Object.values(value).every(primitiveValue);
const deepFreeze = <T>(value: T): Readonly<T> => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    for (const child of Object.values(value as Record<string, unknown>)) {
      deepFreeze(child);
    }
    Object.freeze(value);
  }
  return value;
};

export const decodeStateChangingActionDefinitionV1 = (
  raw: string,
  admissionPath: string,
  admissionRaw: string,
): StateChangingActionDefinitionV1 => {
  const value = parseRecord(raw, "RMT_OP_DEFINITION");
  if (!exactKeys(value, [
    "schema_version", "definition_id", "status", "authorship",
    "admission_ref", "operation_id", "architecture_type_id",
    "input_contract", "declared_reads", "declared_writes",
    "declared_external_effects", "guards", "ordered_steps", "atomicity",
    "outcome_contract", "emitted_events", "continuation", "guard_rejection",
    "relation_contracts", "authority_effect",
  ]) || value.schema_version !== "StateChangingActionDefinition/v1" ||
      !nonEmptyString(value.definition_id) ||
      !nonEmptyString(value.operation_id) ||
      value.status !== "candidate-fixture" ||
      value.authorship !== "owner-authored-admission-input" ||
      value.architecture_type_id !== "architecture.OperationImplementation" ||
      value.authority_effect !== "none") {
    throw new Error("RMT_OP_DEFINITION_CONTRACT_INVALID");
  }
  const admissionRef = value.admission_ref;
  if (!isRecord(admissionRef) ||
      !exactKeys(admissionRef, ["path", "sha256"]) ||
      admissionRef.path !== admissionPath ||
      admissionRef.sha256 !== sha256OperationBytes(admissionRaw)) {
    throw new Error("RMT_OP_DEFINITION_ADMISSION_STALE");
  }
  for (const key of [
    "declared_reads",
    "declared_writes",
    "declared_external_effects",
    "ordered_steps",
  ]) {
    const entries = value[key];
    if (!stringArray(entries) || entries.length === 0 || !unique(entries)) {
      throw new Error(`RMT_OP_DEFINITION_${key.toUpperCase()}_INVALID`);
    }
  }
  const inputContract = value.input_contract;
  const atomicity = value.atomicity;
  const outcomeContract = value.outcome_contract;
  const continuation = value.continuation;
  const guardRejection = value.guard_rejection;
  if (!isRecord(inputContract) ||
      !exactKeys(inputContract, ["required", "additional_inputs"]) ||
      !stringArray(inputContract.required) ||
      inputContract.required.length === 0 ||
      !unique(inputContract.required) ||
      inputContract.additional_inputs !== false ||
      !isRecord(atomicity) ||
      !exactKeys(atomicity, ["mode", "commit_step", "partial_success"]) ||
      atomicity.mode !== "all-or-nothing" ||
      !nonEmptyString(atomicity.commit_step) ||
      atomicity.partial_success !== false ||
      !isRecord(outcomeContract) ||
      !exactKeys(outcomeContract, [
        "success_fields", "declared_failures", "success_and_failure_disjoint",
        "exactly_once_distributed_delivery",
      ]) || !stringArray(outcomeContract.success_fields) ||
      outcomeContract.success_fields.length === 0 ||
      !unique(outcomeContract.success_fields) ||
      !stringArray(outcomeContract.declared_failures) ||
      outcomeContract.declared_failures.length === 0 ||
      !unique(outcomeContract.declared_failures) ||
      outcomeContract.success_and_failure_disjoint !== true ||
      outcomeContract.exactly_once_distributed_delivery !== false ||
      !isRecord(continuation) ||
      !exactKeys(continuation, ["closure", "pending_effects_on_close"]) ||
      continuation.closure !==
        "return-await-cancel-close-dispose-finalizer-quiescence" ||
      continuation.pending_effects_on_close !== 0 ||
      !isRecord(guardRejection) ||
      !exactKeys(guardRejection, [
        "failure_code", "transition_started", "trace",
      ]) || !nonEmptyString(guardRejection.failure_code) ||
      guardRejection.transition_started !== false ||
      !stringArray(guardRejection.trace) || guardRejection.trace.length === 0 ||
      !Array.isArray(value.guards) || value.guards.length === 0 ||
      !value.guards.every((guard) => isRecord(guard) &&
        exactKeys(guard, [
          "guard_id", "current_state_version_required", "controlled_effects",
        ]) && nonEmptyString(guard.guard_id) &&
        guard.current_state_version_required === true &&
        stringArray(guard.controlled_effects) &&
        guard.controlled_effects.length > 0 && unique(guard.controlled_effects)) ||
      !Array.isArray(value.emitted_events) ||
      value.emitted_events.length === 0 ||
      !value.emitted_events.every((event) => isRecord(event) &&
        exactKeys(event, ["event_type", "tense", "checkpoint"]) &&
        nonEmptyString(event.event_type) && event.tense === "past-tense" &&
        event.checkpoint === "after-commit") ||
      !Array.isArray(value.relation_contracts) ||
      value.relation_contracts.length !== 4 ||
      !value.relation_contracts.every((relation) => isRecord(relation) &&
        exactKeys(relation, [
          "contract_id", "architecture_relation_id", "source_types",
          "target_types", "assertion_owner", "owner_evidence_sha256",
        ]) && nonEmptyString(relation.contract_id) &&
        nonEmptyString(relation.architecture_relation_id) &&
        stringArray(relation.source_types) && relation.source_types.length > 0 &&
        unique(relation.source_types) && stringArray(relation.target_types) &&
        relation.target_types.length > 0 && unique(relation.target_types) &&
        nonEmptyString(relation.assertion_owner) &&
        typeof relation.owner_evidence_sha256 === "string" &&
        SHA256.test(relation.owner_evidence_sha256))) {
    throw new Error("RMT_OP_DEFINITION_DENOMINATOR_INVALID");
  }
  const definition = value as StateChangingActionDefinitionV1;
  if (!unique(definition.guards.map(({guard_id}) => guard_id)) ||
      !unique(definition.relation_contracts.map(({contract_id}) => contract_id)) ||
      !definition.ordered_steps.includes(definition.atomicity.commit_step) ||
      !definition.outcome_contract.declared_failures.includes(
        definition.guard_rejection.failure_code,
      )) {
    throw new Error("RMT_OP_DEFINITION_ID_COLLISION");
  }
  return deepFreeze(definition);
};

export const decodeStateChangingActionDenominatorV1 = (
  raw: string,
  definitionPath: string,
  definitionRaw: string,
  definition: StateChangingActionDefinitionV1,
): StateChangingActionDenominatorV1 => {
  const value = parseRecord(raw, "RMT_OP_DENOMINATOR");
  if (!exactKeys(value, [
    "schema_version", "denominator_id", "definition_ref",
    "portable_contract", "semantic_hostile_count", "relation_hostile_count",
    "relation_contract_count", "authority_effect",
  ]) || value.schema_version !== "StateChangingActionDenominator/v1" ||
      !nonEmptyString(value.denominator_id) ||
      value.authority_effect !== "none" ||
      value.semantic_hostile_count !== 10 ||
      value.relation_hostile_count !== 4 ||
      value.relation_contract_count !== 4) {
    throw new Error("RMT_OP_DENOMINATOR_CONTRACT_INVALID");
  }
  const definitionRef = value.definition_ref;
  if (!isRecord(definitionRef) ||
      !exactKeys(definitionRef, ["definition_id", "path", "sha256"]) ||
      definitionRef.definition_id !== definition.definition_id ||
      definitionRef.path !== definitionPath ||
      definitionRef.sha256 !== sha256OperationBytes(definitionRaw)) {
    throw new Error("RMT_OP_DENOMINATOR_DEFINITION_STALE");
  }
  const portable = value.portable_contract;
  if (!isRecord(portable) ||
      !exactKeys(portable, [
        "input_semantics", "read_semantics", "write_semantics",
        "external_effect_semantics", "guard_semantics", "atomicity_semantics",
        "outcome_semantics", "event_semantics", "continuation_semantics",
        "observer_origin",
      ]) ||
      portable.input_semantics !== "exact-declared-input-contract" ||
      portable.read_semantics !== "exact-ordered-declared-reads" ||
      portable.write_semantics !== "exact-ordered-declared-writes" ||
      portable.external_effect_semantics !==
        "exact-declared-effects-after-commit" ||
      portable.guard_semantics !==
        "invoked-current-state-decision-controls-effects" ||
      portable.atomicity_semantics !==
        "all-or-nothing-no-partial-success" ||
      portable.outcome_semantics !==
        "typed-disjoint-success-or-failure" ||
      portable.event_semantics !== "past-tense-facts-after-commit" ||
      portable.continuation_semantics !==
        "return-await-cancel-close-dispose-finalizer-quiescence" ||
      portable.observer_origin !==
        "independent-family-fixture-not-product-target") {
    throw new Error("RMT_OP_DENOMINATOR_PORTABLE_CONTRACT_INVALID");
  }
  return deepFreeze(value as StateChangingActionDenominatorV1);
};

type ObservationBody = Omit<
  StateChangingActionObservationV1,
  "observation_sha256"
>;

export const mintStateChangingActionObservationV1 = (
  body: ObservationBody,
): StateChangingActionObservationV1 => deepFreeze({
  ...body,
  observation_sha256: sha256OperationValue(body),
});

export const decodeStateChangingActionObservationV1 = (
  raw: string,
  definition: StateChangingActionDefinitionV1,
  definitionPath: string,
  definitionRaw: string,
  denominator: StateChangingActionDenominatorV1,
  denominatorRaw: string,
): StateChangingActionObservationV1 => {
  const value = parseRecord(raw, "RMT_OP_OBSERVATION");
  const {observation_sha256: digest, ...body} = value;
  if (!exactKeys(value, [
    "schema_version", "observation_id", "case_id", "source_kind",
    "definition_ref", "denominator_ref", "observer", "operation_id",
    "transition_started", "inputs", "read_attempts", "write_attempts",
    "external_effect_attempts", "guard_evaluations", "trace", "atomicity",
    "outcome", "emitted_events", "continuation", "relation_assertions",
    "authority_effect", "observation_sha256",
  ]) || value.schema_version !== "StateChangingActionObservation/v1" ||
      !nonEmptyString(value.observation_id) ||
      !["committed-success", "guard-rejected"].includes(
        value.case_id as string,
      ) || ![
        "independent-family-fixture", "mutated-family-observation",
        "target-observation",
      ].includes(value.source_kind as string) ||
      value.operation_id !== definition.operation_id ||
      typeof value.transition_started !== "boolean" ||
      value.authority_effect !== "none") {
    throw new Error("RMT_OP_OBSERVATION_CONTRACT_INVALID");
  }
  if (typeof digest !== "string" || digest !== sha256OperationValue(body)) {
    throw new Error("RMT_OP_OBSERVATION_DIGEST_STALE");
  }
  const definitionRef = value.definition_ref;
  const denominatorRef = value.denominator_ref;
  if (!isRecord(definitionRef) ||
      !exactKeys(definitionRef, ["definition_id", "path", "sha256"]) ||
      definitionRef.definition_id !== definition.definition_id ||
      definitionRef.path !== definitionPath ||
      definitionRef.sha256 !== sha256OperationBytes(definitionRaw) ||
      !isRecord(denominatorRef) ||
      !exactKeys(denominatorRef, ["denominator_id", "sha256"]) ||
      denominatorRef.denominator_id !== denominator.denominator_id ||
      denominatorRef.sha256 !== sha256OperationBytes(denominatorRaw)) {
    throw new Error("RMT_OP_OBSERVATION_PROVENANCE_STALE");
  }
  const observer = value.observer;
  if (!isRecord(observer) ||
      !exactKeys(observer, ["observer_id", "ownership"]) ||
      !nonEmptyString(observer.observer_id) ||
      observer.ownership !== "independent-proof-harness") {
    throw new Error("RMT_OP_OBSERVER_NOT_INDEPENDENT");
  }
  const inputs = value.inputs;
  const atomicity = value.atomicity;
  const outcome = value.outcome;
  const continuation = value.continuation;
  if (!recordWithPrimitiveValues(inputs) ||
      !exactKeys(inputs, definition.input_contract.required) ||
      !stringArray(value.read_attempts) ||
      !unique(value.read_attempts) ||
      !stringArray(value.write_attempts) ||
      !unique(value.write_attempts) ||
      !stringArray(value.external_effect_attempts) ||
      !unique(value.external_effect_attempts) ||
      !stringArray(value.trace) || value.trace.length === 0 ||
      !Array.isArray(value.guard_evaluations) ||
      !value.guard_evaluations.every((guard) => isRecord(guard) &&
        exactKeys(guard, [
          "guard_id", "invoked", "decision",
          "current_state_version_observed", "controlled_effects",
        ]) && nonEmptyString(guard.guard_id) &&
        typeof guard.invoked === "boolean" &&
        ["pass", "fail"].includes(guard.decision as string) &&
        typeof guard.current_state_version_observed === "boolean" &&
        stringArray(guard.controlled_effects) &&
        unique(guard.controlled_effects)) ||
      !isRecord(atomicity) ||
      !exactKeys(atomicity, ["mode", "outcome"]) ||
      !["all-or-nothing", "best-effort"].includes(atomicity.mode as string) ||
      !["committed", "rolled-back", "partial"].includes(
        atomicity.outcome as string,
      ) || !isRecord(outcome) ||
      !exactKeys(outcome, [
        "kind", "value", "failure_code",
        "exactly_once_distributed_delivery_claimed",
      ]) || !["success", "failure"].includes(outcome.kind as string) ||
      !(outcome.value === null || recordWithPrimitiveValues(outcome.value)) ||
      !(outcome.failure_code === null ||
        nonEmptyString(outcome.failure_code)) ||
      typeof outcome.exactly_once_distributed_delivery_claimed !== "boolean" ||
      !Array.isArray(value.emitted_events) ||
      !value.emitted_events.every((event) => isRecord(event) &&
        exactKeys(event, ["event_type", "tense", "trace_ordinal"]) &&
        nonEmptyString(event.event_type) &&
        ["past-tense", "imperative"].includes(event.tense as string) &&
        Number.isInteger(event.trace_ordinal) &&
        (event.trace_ordinal as number) >= 0) ||
      !isRecord(continuation) ||
      !exactKeys(continuation, [
        "closure", "closed", "pending_effect_count",
      ]) || !nonEmptyString(continuation.closure) ||
      typeof continuation.closed !== "boolean" ||
      !Number.isInteger(continuation.pending_effect_count) ||
      (continuation.pending_effect_count as number) < 0 ||
      !Array.isArray(value.relation_assertions) ||
      !value.relation_assertions.every((relation) => isRecord(relation) &&
        exactKeys(relation, [
          "contract_id", "architecture_relation_id", "source_type",
          "target_type", "assertion_owner", "owner_evidence_sha256",
          "exact_assertion",
        ]) && nonEmptyString(relation.contract_id) &&
        nonEmptyString(relation.architecture_relation_id) &&
        nonEmptyString(relation.source_type) &&
        nonEmptyString(relation.target_type) &&
        nonEmptyString(relation.assertion_owner) &&
        typeof relation.owner_evidence_sha256 === "string" &&
        SHA256.test(relation.owner_evidence_sha256) &&
        typeof relation.exact_assertion === "boolean")) {
    throw new Error("RMT_OP_OBSERVATION_SHAPE_INVALID");
  }
  return deepFreeze(value as StateChangingActionObservationV1);
};

export const decodeStateChangingActionObservationSetV1 = (
  raw: string,
  definition: StateChangingActionDefinitionV1,
  definitionPath: string,
  definitionRaw: string,
  denominator: StateChangingActionDenominatorV1,
  denominatorRaw: string,
): StateChangingActionObservationSetV1 => {
  const value = parseRecord(raw, "RMT_OP_OBSERVATION_SET");
  if (!exactKeys(value, [
    "schema_version", "observations", "authority_effect",
  ]) || value.schema_version !== "StateChangingActionPositiveObservations/v1" ||
      value.authority_effect !== "none" || !Array.isArray(value.observations) ||
      value.observations.length !== 2) {
    throw new Error("RMT_OP_OBSERVATION_SET_CONTRACT_INVALID");
  }
  const observations = value.observations.map((entry) =>
    decodeStateChangingActionObservationV1(
      JSON.stringify(entry),
      definition,
      definitionPath,
      definitionRaw,
      denominator,
      denominatorRaw,
    ));
  if (new Set(observations.map(({case_id}) => case_id)).size !== 2 ||
      !observations.some(({case_id}) => case_id === "committed-success") ||
      !observations.some(({case_id}) => case_id === "guard-rejected")) {
    throw new Error("RMT_OP_OBSERVATION_SET_CASES_INVALID");
  }
  return deepFreeze({
    schema_version: "StateChangingActionPositiveObservations/v1",
    observations: Object.freeze(observations),
    authority_effect: "none",
  });
};

export const decodeOperationHostileFixtureV1 = (
  raw: string,
): OperationHostileFixtureV1 => {
  const value = parseRecord(raw, "RMT_OP_HOSTILE");
  if (value.schema_version === "StateChangingActionS1Hostile/v1") {
    if (!exactKeys(value, [
      "schema_version", "hostile_id", "hostile_class", "mutation_kind",
      "expected_code", "fixture_owner_swu", "proof_owner_swu",
      "non_noop_required", "category", "required_observation",
      "required_outcome", "baseline", "mutation", "authority_effect",
    ]) || !(OPERATION_S1_HOSTILE_IDS as readonly unknown[]).includes(
      value.hostile_id,
    ) || value.hostile_class !== "s1-cross-boundary" ||
        value.fixture_owner_swu !== "RMT-OP-002" ||
        value.proof_owner_swu !== "RMT-OP-006" ||
        value.non_noop_required !== true ||
        !nonEmptyString(value.category) ||
        !nonEmptyString(value.required_observation) ||
        !nonEmptyString(value.required_outcome) ||
        value.authority_effect !== "none" || !isRecord(value.baseline) ||
        !isRecord(value.mutation)) {
      throw new Error("RMT_OP_S1_HOSTILE_CONTRACT_INVALID");
    }
    const hostile = value as unknown as OperationS1HostileFixtureV1;
    if (hostile.expected_code !==
        OPERATION_EXPECTED_DIAGNOSTIC[hostile.hostile_id] ||
        hostile.mutation_kind !==
          OPERATION_S1_MUTATION_KIND[hostile.hostile_id]) {
      throw new Error("RMT_OP_S1_HOSTILE_DIAGNOSTIC_MISMATCH");
    }
    const residueKeys = [
      "schema_version", "scenario", "transaction_id", "occurrence_id",
      "state_write_attempted", "outbox_append_attempted",
      "outbox_checkpoint_observed",
      "transaction_aborted", "state_durable", "outbox_occurrence_durable",
      "commit_observed", "rollback_requested", "history_erased",
      "forward_recovery_required", "closed_rejection",
    ] as const;
    const mutationKeys = residueKeys.filter((key) => key !== "schema_version");
    if (!exactKeys(hostile.baseline as unknown as Record<string, unknown>,
      residueKeys) || Object.keys(hostile.mutation).length === 0 ||
        Object.keys(hostile.mutation).some((key) =>
          !mutationKeys.includes(key as typeof mutationKeys[number]))) {
      throw new Error("RMT_OP_S1_HOSTILE_RESIDUE_INVALID");
    }
    const merged = {...hostile.baseline, ...hostile.mutation};
    const validResidue = (candidate: OperationS1ResidueV1): boolean =>
      candidate.schema_version === "OperationS1Residue/v1" &&
      [
        "normal", "before-state-write-failure",
        "between-state-and-outbox-failure", "missing-member",
        "mixed-commit", "rollback-after-commit",
      ].includes(candidate.scenario) &&
      (candidate.transaction_id === null ||
        nonEmptyString(candidate.transaction_id)) &&
      (candidate.occurrence_id === null ||
        nonEmptyString(candidate.occurrence_id)) &&
      [
        candidate.state_write_attempted, candidate.outbox_append_attempted,
        candidate.outbox_checkpoint_observed,
        candidate.transaction_aborted, candidate.state_durable,
        candidate.outbox_occurrence_durable, candidate.commit_observed,
        candidate.rollback_requested, candidate.history_erased,
        candidate.forward_recovery_required, candidate.closed_rejection,
      ].every((entry) => typeof entry === "boolean");
    if (!validResidue(hostile.baseline) ||
        !validResidue(merged as OperationS1ResidueV1) ||
        canonicalOperationJson(hostile.baseline) ===
          canonicalOperationJson(merged)) {
      throw new Error("RMT_OP_S1_HOSTILE_RESIDUE_INVALID");
    }
    return deepFreeze(hostile);
  }
  if (!exactKeys(value, [
    "schema_version", "hostile_id", "hostile_class", "mutation_kind",
    "expected_code", "fixture_owner_swu", "proof_owner_swu",
    "non_noop_required", "authority_effect",
  ]) || value.schema_version !== "StateChangingActionHostile/v1" ||
      !(OPERATION_HOSTILE_IDS as readonly unknown[]).includes(
        value.hostile_id,
      ) ||
      typeof value.mutation_kind !== "string" ||
      value.mutation_kind.length === 0 ||
      value.fixture_owner_swu !== "RMT-OP-002" ||
      !["RMT-OP-006", "RMT-OP-008"].includes(
        value.proof_owner_swu as string,
      ) || value.non_noop_required !== true ||
      value.authority_effect !== "none") {
    throw new Error("RMT_OP_HOSTILE_CONTRACT_INVALID");
  }
  const hostile = value as OperationHostileFixtureV1;
  if (hostile.expected_code !==
      OPERATION_EXPECTED_DIAGNOSTIC[hostile.hostile_id]) {
    throw new Error("RMT_OP_HOSTILE_DIAGNOSTIC_MISMATCH");
  }
  const expectedClass = hostile.hostile_id.startsWith("op/relation-") ||
    hostile.hostile_id === "op/materialized-without-exact-assertion"
    ? "rel-a-evidence"
    : "type-semantic";
  if (hostile.hostile_class !== expectedClass ||
      hostile.mutation_kind !== OPERATION_MUTATION_KIND[hostile.hostile_id] ||
      hostile.proof_owner_swu !==
        (expectedClass === "rel-a-evidence" ? "RMT-OP-008" : "RMT-OP-006")) {
    throw new Error("RMT_OP_HOSTILE_CLASS_MISMATCH");
  }
  return deepFreeze(hostile);
};
