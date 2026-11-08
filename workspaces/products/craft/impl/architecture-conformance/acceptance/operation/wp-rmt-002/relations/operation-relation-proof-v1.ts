import {createHash} from "node:crypto";

import type {
  OperationRelationContractV1,
  StateChangingActionDefinitionV1,
} from "../../../../families/state-changing-action/contracts/state-changing-action-contracts.js";
import {
  decodeOperationHostileFixtureV1,
  decodeStateChangingActionDefinitionV1,
  decodeStateChangingActionDenominatorV1,
  decodeStateChangingActionObservationSetV1,
} from "../../../../families/state-changing-action/providers/decode-state-changing-action.js";
import {evaluateStateChangingAction} from
  "../../../../families/state-changing-action/evaluator/evaluate-state-changing-action.js";
import {applyOperationHostile} from
  "../../../../families/state-changing-action/mutations/apply-operation-hostile.js";

type JsonObject = Record<string, unknown>;
type RawInputs = Readonly<Record<string, string>>;
type ResolvedRequestInputs = Readonly<Record<string, string | Buffer>>;

export const REQUIRED_SEMANTIC_PLAN_EPOCH = "WP-RMT-002/S1/2026-08-16";
export const REQUIRED_SEMANTIC_CONTRACT_DIGEST =
  "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7";

const REQUIRED_COMMAND =
  "projects/domainspec-v2/impl/node_modules/.bin/vitest run --root " +
  "projects/domainspec-v2/impl architecture-conformance/acceptance/" +
  "operation/wp-rmt-002/relations";

export const OPERATION_RELATION_SOURCE_PATHS = Object.freeze({
  swu_contracts:
    "projects/domainspec-v2/development/refinement-runs/" +
    "20260814T193343Z-active-meta-type-implementations/refreshes/" +
    "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
    "SWU-CONTRACTS.json",
  relation_contracts:
    "projects/domainspec-v2/development/refinement-runs/" +
    "20260814T193343Z-active-meta-type-implementations/refreshes/" +
    "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
    "RELATION-CONTRACTS.json",
  write_scope_baseline:
    "projects/domainspec-v2/development/refinement-runs/" +
    "20260814T193343Z-active-meta-type-implementations/refreshes/" +
    "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
    "WRITE-SCOPE-BASELINE.json",
  task_operation:
    "projects/domainspec-v2/development/refinement-runs/" +
    "20260814T193343Z-active-meta-type-implementations/refreshes/" +
    "20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/" +
    "tasks/TASK-RMT-OP.md",
  admission:
    "projects/domainspec-v2/development/remaining-meta-types/active-types/" +
    "operation/admission/admission.json",
  op006_parity_evaluator_test:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/parity/evaluate-operation-parity.test.ts",
  op006_parity_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/parity/evaluate-operation-parity.ts",
  op006_parity_live_test:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/parity/live-operation-parity.test.ts",
  op007_replay_child:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/replay/execute-operation-replay.ts",
  op007_replay_provider:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/replay/operation-replay-v1.ts",
  op007_replay_runner:
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/" +
    "operation/wp-rmt-002/replay/run-operation-replay.ts",
  op007_factory_request:
    "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/" +
    "rmt-operation-wp-rmt-002.request.json",
  op007_factory_test:
    "projects/domainspec-v2/impl/architecture-conformance/factory/tests/" +
    "rmt-operation-wp-rmt-002.test.ts",
  family_contracts:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/contracts/state-changing-action-contracts.ts",
  family_decoder:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/providers/decode-state-changing-action.ts",
  family_evaluator:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/evaluator/evaluate-state-changing-action.ts",
  family_evaluator_test:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/evaluator/evaluate-state-changing-action.test.ts",
  family_mutator:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/mutations/apply-operation-hostile.ts",
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/fixtures/complete-settlement/operation-contract.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/fixtures/complete-settlement/denominator.json",
  positive_observations:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/fixtures/complete-settlement/positive-observation.json",
  hostile_owner:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/hostiles/relation-owner-evidence-stale.json",
  hostile_source:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/hostiles/relation-source-endpoint-mismatch.json",
  hostile_target:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/hostiles/relation-target-endpoint-mismatch.json",
  hostile_assertion:
    "projects/domainspec-v2/impl/architecture-conformance/families/" +
    "state-changing-action/hostiles/materialized-without-exact-assertion.json",
} as const);

const EXPECTED_RELATIONS = Object.freeze([
  Object.freeze({
    contract_id: "op/enforced-by-to-guards",
    domain_surface: "target_of:enforces",
    architecture_relation_id: "architecture.guards",
    translation:
      "inverse label only; architecture direction remains Rule to Operation",
    source_types: Object.freeze(["architecture.RuleImplementation"]),
    target_types: Object.freeze(["architecture.OperationImplementation"]),
    assertion_owner_mapping: "source Rule candidate",
    cycle_policy: "acyclic",
  }),
  Object.freeze({
    contract_id: "op/exposed-by-to-exposes",
    domain_surface: "target_of:exposes",
    architecture_relation_id: "architecture.exposes",
    translation:
      "inverse label only; architecture direction remains Interface to Operation",
    source_types: Object.freeze(["architecture.InterfaceImplementation"]),
    target_types: Object.freeze(["architecture.OperationImplementation"]),
    assertion_owner_mapping: "source Interface candidate",
    cycle_policy: "acyclic",
  }),
  Object.freeze({
    contract_id: "op/emitted-events-to-emits",
    domain_surface: "operation.emitted_events",
    architecture_relation_id: "architecture.emits",
    translation:
      "atomic commit persists the Event occurrence in the durable outbox; " +
      "architecture.emits remains Operation to Event and does not claim " +
      "publication or delivery",
    source_types: Object.freeze(["architecture.OperationImplementation"]),
    target_types: Object.freeze(["architecture.EventImplementation"]),
    assertion_owner_mapping: "source Operation candidate",
    cycle_policy: "acyclic",
  }),
  Object.freeze({
    contract_id: "op/workflow-step-to-binds-step",
    domain_surface: "target_of:orchestrates",
    architecture_relation_id: "architecture.binds_step",
    translation:
      "workflow step binds an exact versioned Operation transaction/effect-group " +
      "handle; this is not a direct Workflow-to-Operation edge or execution " +
      "authority",
    source_types: Object.freeze(["architecture.WorkflowStepContract"]),
    target_types: Object.freeze([
      "architecture.OperationImplementation",
      "architecture.WorkflowImplementation",
    ]),
    assertion_owner_mapping: "Workflow candidate owning the step assertion",
    cycle_policy: "acyclic",
  }),
]);

const EXPECTED_HANDLE = Object.freeze({
  handle: "operation-transaction-effect-group/v1",
  fields: Object.freeze([
    "transaction_id",
    "effect_group_id",
    "state_write_id",
    "outbox_checkpoint_id",
    "occurrence_id",
    "commit_outcome",
  ]),
  publication_authority: false,
});

const EXPECTED_FIXTURE_PLACEHOLDERS = Object.freeze({
  "op/enforced-by-to-guards": "a".repeat(64),
  "op/exposed-by-to-exposes": "b".repeat(64),
  "op/emitted-events-to-emits": "c".repeat(64),
  "op/workflow-step-to-binds-step": "d".repeat(64),
} as const);

const EXPECTED_HOSTILES = Object.freeze([
  Object.freeze({
    role: "hostile_owner",
    hostile_id: "op/relation-owner-evidence-stale",
    expected_code: "RMT_RELATION_OWNER_EVIDENCE_STALE",
  }),
  Object.freeze({
    role: "hostile_source",
    hostile_id: "op/relation-source-endpoint-mismatch",
    expected_code: "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
  }),
  Object.freeze({
    role: "hostile_target",
    hostile_id: "op/relation-target-endpoint-mismatch",
    expected_code: "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
  }),
  Object.freeze({
    role: "hostile_assertion",
    hostile_id: "op/materialized-without-exact-assertion",
    expected_code: "RMT_RELATION_ASSERTION_REQUIRED",
  }),
]);

const SHA256 = /^[a-f0-9]{64}$/u;
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const exactKeys = (value: JsonObject, keys: readonly string[]): boolean =>
  canonicalJson(Object.keys(value).sort()) === canonicalJson([...keys].sort());
const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};
const parseObject = (raw: string, code: string): JsonObject => {
  try {
    const value: unknown = JSON.parse(raw);
    if (!isObject(value)) fail(code);
    return value;
  } catch (error) {
    if (error instanceof Error && error.message === code) throw error;
    return fail(code);
  }
};

const canonicalValue = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonicalValue)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value).sort(([left], [right]) =>
      Buffer.from(left).compare(Buffer.from(right))).map(([key, child]) =>
      [key, canonicalValue(child)]))
    : value;

export const canonicalJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));
export const sha256Bytes = (value: string | Buffer): string =>
  createHash("sha256").update(value).digest("hex");
export const sha256Value = (value: unknown): string =>
  sha256Bytes(canonicalJson(value));

export const computeBindingSha256 = (value: JsonObject): string => {
  const {binding_sha256: _ignored, ...body} = value;
  return sha256Value(body);
};

type SourceBinding = Readonly<{
  role: string;
  path: string;
  sha256: string;
  size_bytes: number;
}>;

type RelationBlueprint = Readonly<{
  contract_id: string;
  architecture_relation_id: string;
  domain_surface: string;
  translation: string;
  source_types: readonly string[];
  target_types: readonly string[];
  assertion_owner_mapping: string;
  cycle_policy: "acyclic";
  evidence_mode: "blueprint" | "materialized";
  materialized: boolean;
  exact_assertion: boolean;
  owner_evidence: Readonly<{
    status: "not-materialized" | "exact";
    sha256: string | null;
  }>;
}>;

type RelationBinding = Readonly<{
  schema_version: "OperationRelationBinding/v1";
  binding_id: "operation.wp-rmt-002.relations/v1";
  semantic_plan_epoch_id: string;
  semantic_contract_digest: string;
  sources: readonly SourceBinding[];
  relation_blueprints: readonly RelationBlueprint[];
  s1_handle_blueprint: Readonly<{
    handle: string;
    fields: readonly string[];
    publication_authority: boolean;
    materialized: boolean;
    evidence_sha256: string | null;
  }>;
  claim_ceiling: string;
  authority_effect: "none";
  binding_sha256: string;
}>;

const stringArray = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) =>
    typeof item === "string" && item.length > 0);

const blueprintProjection = (value: RelationBlueprint) => ({
  contract_id: value.contract_id,
  domain_surface: value.domain_surface,
  architecture_relation_id: value.architecture_relation_id,
  translation: value.translation,
  source_types: value.source_types,
  target_types: value.target_types,
  assertion_owner_mapping: value.assertion_owner_mapping,
  cycle_policy: value.cycle_policy,
});

export const decodeOperationRelationBinding = (
  raw: string,
): RelationBinding => {
  const value = parseObject(raw, "RMT_OP_RELATION_BINDING_INVALID");
  if (!exactKeys(value, [
    "schema_version", "binding_id", "semantic_plan_epoch_id",
    "semantic_contract_digest", "sources", "relation_blueprints",
    "s1_handle_blueprint", "claim_ceiling", "authority_effect",
    "binding_sha256",
  ]) || value.schema_version !== "OperationRelationBinding/v1" ||
      value.binding_id !== "operation.wp-rmt-002.relations/v1" ||
      value.semantic_plan_epoch_id !== REQUIRED_SEMANTIC_PLAN_EPOCH ||
      value.semantic_contract_digest !== REQUIRED_SEMANTIC_CONTRACT_DIGEST ||
      value.claim_ceiling !==
        "four exact Operation relation blueprints and one exact " +
        "non-materialized S1 handle schema" ||
      value.authority_effect !== "none" ||
      typeof value.binding_sha256 !== "string" ||
      !SHA256.test(value.binding_sha256) ||
      !Array.isArray(value.sources) ||
      !Array.isArray(value.relation_blueprints)) {
    fail("RMT_OP_RELATION_BINDING_INVALID");
  }

  const sources = value.sources as unknown[];
  if (sources.length !== Object.keys(OPERATION_RELATION_SOURCE_PATHS).length ||
      !sources.every((source) => isObject(source) && exactKeys(source, [
        "role", "path", "sha256", "size_bytes",
      ]) && typeof source.role === "string" &&
        typeof source.path === "string" &&
        typeof source.sha256 === "string" && SHA256.test(source.sha256) &&
        Number.isInteger(source.size_bytes) &&
        (source.size_bytes as number) >= 0)) {
    fail("RMT_OP_RELATION_SOURCE_BINDING_INVALID");
  }
  const typedSources = sources as SourceBinding[];
  if (new Set(typedSources.map(({role}) => role)).size !== sources.length ||
      new Set(typedSources.map(({path}) => path)).size !== sources.length) {
    fail("RMT_OP_RELATION_SOURCE_BINDING_DUPLICATE");
  }
  if (canonicalJson(typedSources.map(({role}) => role)) !== canonicalJson(
    Object.keys(OPERATION_RELATION_SOURCE_PATHS),
  )) {
    fail("RMT_OP_RELATION_SOURCE_ORDER_DRIFT");
  }
  for (const [role, path] of Object.entries(OPERATION_RELATION_SOURCE_PATHS)) {
    const source = typedSources.find((candidate) => candidate.role === role);
    if (!source || source.path !== path) {
      fail("RMT_OP_RELATION_SOURCE_PATH_DRIFT");
    }
  }

  const blueprints = value.relation_blueprints as unknown[];
  if (blueprints.length !== EXPECTED_RELATIONS.length ||
      !blueprints.every((entry) => isObject(entry) && exactKeys(entry, [
        "contract_id", "architecture_relation_id", "domain_surface",
        "translation", "source_types", "target_types",
        "assertion_owner_mapping", "cycle_policy", "evidence_mode",
        "materialized", "exact_assertion", "owner_evidence",
      ]) && typeof entry.contract_id === "string" &&
        typeof entry.architecture_relation_id === "string" &&
        typeof entry.domain_surface === "string" &&
        typeof entry.translation === "string" &&
        stringArray(entry.source_types) && stringArray(entry.target_types) &&
        typeof entry.assertion_owner_mapping === "string" &&
        entry.cycle_policy === "acyclic" &&
        ["blueprint", "materialized"].includes(entry.evidence_mode as string) &&
        typeof entry.materialized === "boolean" &&
        typeof entry.exact_assertion === "boolean" &&
        isObject(entry.owner_evidence) && exactKeys(entry.owner_evidence, [
          "status", "sha256",
        ]) && ["not-materialized", "exact"].includes(
          entry.owner_evidence.status as string,
        ) && (entry.owner_evidence.sha256 === null ||
          (typeof entry.owner_evidence.sha256 === "string" &&
            SHA256.test(entry.owner_evidence.sha256))))) {
    fail("RMT_OP_RELATION_BLUEPRINT_INVALID");
  }
  const typedBlueprints = blueprints as RelationBlueprint[];
  for (const blueprint of typedBlueprints) {
    if (blueprint.materialized && !blueprint.exact_assertion) {
      fail("RMT_RELATION_ASSERTION_REQUIRED");
    }
    if (blueprint.materialized &&
        (blueprint.evidence_mode !== "materialized" ||
          blueprint.owner_evidence.status !== "exact" ||
          blueprint.owner_evidence.sha256 === null)) {
      fail("RMT_RELATION_OWNER_EVIDENCE_STALE");
    }
    if (!blueprint.materialized &&
        (blueprint.evidence_mode !== "blueprint" ||
          blueprint.exact_assertion ||
          blueprint.owner_evidence.status !== "not-materialized" ||
          blueprint.owner_evidence.sha256 !== null)) {
      fail("RMT_OP_RELATION_BLUEPRINT_AUTHORITY_OVERCLAIM");
    }
  }
  if (canonicalJson(typedBlueprints.map(blueprintProjection)) !==
      canonicalJson(EXPECTED_RELATIONS)) {
    fail("RMT_OP_RELATION_BLUEPRINT_DRIFT");
  }

  const handle = value.s1_handle_blueprint;
  if (!isObject(handle) || !exactKeys(handle, [
    "handle", "fields", "publication_authority", "materialized",
    "evidence_sha256",
  ]) || handle.handle !== EXPECTED_HANDLE.handle ||
      !stringArray(handle.fields) ||
      canonicalJson(handle.fields) !== canonicalJson(EXPECTED_HANDLE.fields) ||
      handle.publication_authority !== false || handle.materialized !== false ||
      handle.evidence_sha256 !== null) {
    fail("RMT_OP_S1_HANDLE_BLUEPRINT_DRIFT");
  }
  if (computeBindingSha256(value) !== value.binding_sha256) {
    fail("RMT_OP_RELATION_BINDING_DIGEST_STALE");
  }
  return Object.freeze(value as RelationBinding);
};

const validateFrozenSourceInventory = (binding: RelationBinding): void => {
  const sourceRows = [...binding.sources].sort((left, right) =>
    Buffer.from(left.path).compare(Buffer.from(right.path))).map((source) =>
    `${source.sha256}\t${source.size_bytes}\t${source.path}\n`).join("");
  if (binding.sources.reduce((total, source) =>
    total + source.size_bytes, 0) !== 2993281 || sha256Bytes(sourceRows) !==
      "7e6da173a9c889edd461b6dbaa524d50246e59345d057e0de7651095cf30992c") {
    fail("RMT_OP_RELATION_SOURCE_INVENTORY_DRIFT");
  }
};

const sourceRaw = (
  binding: RelationBinding,
  rawInputs: RawInputs,
  role: string,
): string => {
  const source = binding.sources.find((candidate) => candidate.role === role);
  const raw = rawInputs[role];
  if (!source || raw === undefined || sha256Bytes(raw) !== source.sha256 ||
      Buffer.byteLength(raw, "utf8") !== source.size_bytes) {
    fail("RMT_OP_RELATION_SOURCE_STALE");
  }
  return raw;
};

const relationProjection = (contract: OperationRelationContractV1) => ({
  contract_id: contract.contract_id,
  architecture_relation_id: contract.architecture_relation_id,
  source_types: contract.source_types,
  target_types: contract.target_types,
  assertion_owner_mapping: contract.assertion_owner,
});

const planProjection = (contract: typeof EXPECTED_RELATIONS[number]) => ({
  contract_id: contract.contract_id,
  architecture_relation_id: contract.architecture_relation_id,
  source_types: contract.source_types,
  target_types: contract.target_types,
  assertion_owner_mapping: contract.assertion_owner_mapping,
});

const validateSwuContract = (raw: string): void => {
  const document = parseObject(raw, "RMT_OP_SWU_CONTRACT_INVALID");
  if (document.schema_version !== "domainspec.wp-rmt-002-swu-contracts/v3" ||
      document.work_pack_id !== "WP-RMT-002" ||
      !Array.isArray(document.contracts)) {
    fail("RMT_OP_SWU_CONTRACT_INVALID");
  }
  const row = document.contracts.find((entry) =>
    isObject(entry) && entry.swu_id === "RMT-OP-008");
  if (!isObject(row) || row.type !== "Operation" || row.stage !== "relations" ||
      row.semantic_plan_epoch_id !== REQUIRED_SEMANTIC_PLAN_EPOCH ||
      row.semantic_contract_digest !== REQUIRED_SEMANTIC_CONTRACT_DIGEST ||
      !Array.isArray(row.acceptance) || !row.acceptance.includes(
        "relation-contract-id-exact",
      ) || !row.acceptance.includes(
        "rel-a-owner-source-target-evidence-exact-or-blueprint",
      ) || !row.acceptance.includes("allowed-endpoint-types-exact") ||
      !row.acceptance.includes("relation-hostiles-killed") ||
      !row.acceptance.includes("no-self-authored-authority") ||
      !row.acceptance.includes("authority-none") ||
      !isObject(row.verification) ||
      canonicalJson(row.verification.commands) !== canonicalJson([
        REQUIRED_COMMAND,
      ]) || !isObject(row.closeout_sync) ||
      row.closeout_sync.authority_effect !== "none") {
    fail("RMT_OP_SWU_CONTRACT_DRIFT");
  }
};

const validateWriteScope = (raw: string): void => {
  const document = parseObject(raw, "RMT_OP_WRITE_SCOPE_INVALID");
  if (document.schema_version !== "domainspec.wp-rmt-002-write-scope-baseline/v2" ||
      document.work_pack_id !== "WP-RMT-002" ||
      !Array.isArray(document.entries)) {
    fail("RMT_OP_WRITE_SCOPE_INVALID");
  }
  const owned = document.entries.filter((entry) =>
    isObject(entry) && entry.owner_swu === "RMT-OP-008");
  if (owned.length !== 0) {
    fail("RMT_OP_WRITE_SCOPE_DRIFT");
  }
};

const validatePlanRelations = (raw: string): void => {
  const document = parseObject(raw, "RMT_OP_RELATION_PLAN_INVALID");
  if (document.schema_version !==
      "domainspec.wp-rmt-002-relation-contracts/v1" ||
      document.work_pack_id !== "WP-RMT-002" ||
      !Array.isArray(document.type_contracts)) {
    fail("RMT_OP_RELATION_PLAN_INVALID");
  }
  const group = document.type_contracts.find((entry) =>
    isObject(entry) && entry.owner_swu === "RMT-OP-008");
  const expectedGroup = {
    prefix: "OP",
    type: "Operation",
    owner_swu: "RMT-OP-008",
    contracts: EXPECTED_RELATIONS,
    unmapped_domain_relations: [
      "creates", "produces", "produces-for", "queries", "applies",
      "calculates", "mutates", "performs", "triggers-cross",
    ],
    s1_handle_contract: EXPECTED_HANDLE,
  };
  if (!isObject(group) || canonicalJson(group) !== canonicalJson(expectedGroup)) {
    fail("RMT_OP_RELATION_CONTRACT_DRIFT");
  }
};

const validateAdmission = (raw: string): void => {
  const admission = parseObject(raw, "RMT_OP_RELATION_ADMISSION_INVALID");
  if (admission.schema_version !==
      "domainspec.wp-rmt-002.operation-admission/v1" ||
      admission.swu_id !== "RMT-OP-001" || admission.result !== "pass" ||
      admission.authority_effect !== "none" ||
      canonicalJson(admission.relation_contract_ids) !== canonicalJson(
        EXPECTED_RELATIONS.map(({contract_id}) => contract_id),
      )) {
    fail("RMT_OP_RELATION_ADMISSION_DRIFT");
  }
};

const validateTaskOperation = (raw: string): void => {
  if (!raw.includes("## Preserved semantic floor") ||
      !raw.includes("post-commit events are past-tense facts") ||
      !raw.includes("no proof implies distributed exactly-once delivery")) {
    fail("RMT_OP_TASK_CONTRACT_DRIFT");
  }
};

const validateUpstreamBlueprintCeiling = (
  binding: RelationBinding,
  raw: RawInputs,
  resolvedRequestInputs: ResolvedRequestInputs,
): Readonly<{
  request_role_count: 109;
  request_path_count: 49;
  request_ref_bytes_scanned: number;
  op006_pins_exact: true;
  s1_materialized_field_occurrences: 0;
}> => {
  const upstreamRoles = [
    "op006_parity_evaluator_test",
    "op006_parity_evaluator",
    "op006_parity_live_test",
    "op007_replay_child",
    "op007_replay_provider",
    "op007_replay_runner",
    "op007_factory_request",
    "op007_factory_test",
  ] as const;
  const instanceMarker =
    /schema_version\s*[:=]\s*["']operation-transaction-effect-group\/v1["']/u;
  const wrapperOccurrences = upstreamRoles.filter((role) =>
    instanceMarker.test(raw[role]!));

  const request = parseObject(
    raw.op007_factory_request!,
    "RMT_OP_REPLAY_REQUEST_INVALID",
  );
  if (!Array.isArray(request.nodes)) {
    fail("RMT_OP_REPLAY_REQUEST_INVALID");
  }
  const refs = request.nodes.flatMap((node) => {
    if (!isObject(node) || !Array.isArray(node.input_refs)) {
      fail("RMT_OP_REPLAY_REQUEST_INVALID");
    }
    return node.input_refs;
  });
  if (refs.length !== 109 || !refs.every((entry) => isObject(entry) &&
      typeof entry.role === "string" && isObject(entry.ref) &&
      typeof entry.ref.path === "string" &&
      typeof entry.ref.sha256 === "string" && SHA256.test(entry.ref.sha256))) {
    fail("RMT_OP_REPLAY_REQUEST_INVALID");
  }
  const typedRefs = refs as Array<{
    role: string;
    ref: {path: string; sha256: string; size_bytes?: number};
  }>;
  if (new Set(typedRefs.map(({role}) => role)).size !== 109 ||
      new Set(typedRefs.map(({ref}) => ref.path)).size !== 49) {
    fail("RMT_OP_REPLAY_REQUEST_DENOMINATOR_DRIFT");
  }
  for (const role of [
    "op006_parity_evaluator_test",
    "op006_parity_evaluator",
    "op006_parity_live_test",
  ] as const) {
    const source = binding.sources.find((candidate) => candidate.role === role)!;
    const matches = typedRefs.filter(({ref}) => ref.path === source.path);
    if (matches.length === 0 || matches.some(({ref}) =>
      ref.sha256 !== source.sha256)) {
      fail("RMT_OP_REPLAY_OP006_PIN_DRIFT");
    }
  }
  const uniquePaths = [...new Set(typedRefs.map(({ref}) => ref.path))].sort();
  if (canonicalJson(Object.keys(resolvedRequestInputs).sort()) !==
      canonicalJson(uniquePaths)) {
    fail("RMT_OP_REPLAY_RESOLVED_INPUT_SET_DRIFT");
  }
  const decoder = new TextDecoder("utf-8", {fatal: true});
  let scannedBytes = 0;
  const transitiveOccurrences: string[] = [];
  for (const path of uniquePaths) {
    const candidate = resolvedRequestInputs[path];
    if (candidate === undefined) {
      fail("RMT_OP_REPLAY_RESOLVED_INPUT_MISSING");
    }
    const bytes = Buffer.isBuffer(candidate)
      ? candidate
      : Buffer.from(candidate, "utf8");
    const occurrencesForPath = typedRefs.filter(({ref}) => ref.path === path);
    if (occurrencesForPath.some(({ref}) =>
      sha256Bytes(bytes) !== ref.sha256 ||
      (ref.size_bytes !== undefined && bytes.length !== ref.size_bytes))) {
      fail("RMT_OP_REPLAY_RESOLVED_INPUT_STALE");
    }
    let text: string;
    try {
      text = decoder.decode(bytes);
    } catch {
      fail("RMT_OP_REPLAY_RESOLVED_INPUT_UTF8_INVALID");
    }
    scannedBytes += bytes.length;
    if (path !== OPERATION_RELATION_SOURCE_PATHS.relation_contracts &&
        instanceMarker.test(text)) {
      transitiveOccurrences.push(path);
    }
  }
  if (wrapperOccurrences.length !== 0 || transitiveOccurrences.length !== 0) {
    fail("RMT_OP_S1_MATERIALIZATION_REQUIRES_REFRESH");
  }
  return Object.freeze({
    request_role_count: 109 as const,
    request_path_count: 49 as const,
    request_ref_bytes_scanned: scannedBytes,
    op006_pins_exact: true as const,
    s1_materialized_field_occurrences: 0 as const,
  });
};

const validateDefinitionRelations = (
  definition: StateChangingActionDefinitionV1,
): void => {
  if (canonicalJson(definition.relation_contracts.map(relationProjection)) !==
      canonicalJson(EXPECTED_RELATIONS.map(planProjection))) {
    fail("RMT_OP_RELATION_DEFINITION_DRIFT");
  }
  for (const contract of definition.relation_contracts) {
    const expected = EXPECTED_FIXTURE_PLACEHOLDERS[
      contract.contract_id as keyof typeof EXPECTED_FIXTURE_PLACEHOLDERS
    ];
    if (expected === undefined || contract.owner_evidence_sha256 !== expected) {
      fail("RMT_OP_RELATION_FIXTURE_PLACEHOLDER_DRIFT");
    }
  }
};

export const buildOperationRelationProof = (input: Readonly<{
  binding_raw: string;
  raw_inputs: RawInputs;
  resolved_request_inputs: ResolvedRequestInputs;
}>) => {
  const binding = decodeOperationRelationBinding(input.binding_raw);
  const expectedRoles = binding.sources.map(({role}) => role).sort();
  if (canonicalJson(Object.keys(input.raw_inputs).sort()) !==
      canonicalJson(expectedRoles)) {
    fail("RMT_OP_RELATION_RAW_INPUT_SET_DRIFT");
  }
  const raw = Object.freeze(Object.fromEntries(binding.sources.map(({role}) =>
    [role, sourceRaw(binding, input.raw_inputs, role)]))) as RawInputs;

  validateSwuContract(raw.swu_contracts!);
  validateWriteScope(raw.write_scope_baseline!);
  validatePlanRelations(raw.relation_contracts!);
  validateTaskOperation(raw.task_operation!);
  validateAdmission(raw.admission!);
  const upstreamClosure = validateUpstreamBlueprintCeiling(
    binding,
    raw,
    input.resolved_request_inputs,
  );

  const definition = decodeStateChangingActionDefinitionV1(
    raw.definition!,
    OPERATION_RELATION_SOURCE_PATHS.admission,
    raw.admission!,
  );
  validateDefinitionRelations(definition);
  const denominator = decodeStateChangingActionDenominatorV1(
    raw.denominator!,
    OPERATION_RELATION_SOURCE_PATHS.definition,
    raw.definition!,
    definition,
  );
  const observations = decodeStateChangingActionObservationSetV1(
    raw.positive_observations!,
    definition,
    OPERATION_RELATION_SOURCE_PATHS.definition,
    raw.definition!,
    denominator,
    raw.denominator!,
  );
  for (const observation of observations.observations) {
    if (observation.relation_assertions.length !== EXPECTED_RELATIONS.length) {
      fail("RMT_OP_RELATION_ASSERTION_COUNT_DRIFT");
    }
    for (const relation of EXPECTED_RELATIONS) {
      const assertion = observation.relation_assertions.find(
        ({contract_id}) => contract_id === relation.contract_id,
      );
      const definitionContract = definition.relation_contracts.find(
        ({contract_id}) => contract_id === relation.contract_id,
      );
      if (!assertion || !definitionContract ||
          assertion.architecture_relation_id !==
            relation.architecture_relation_id ||
          !relation.source_types.includes(assertion.source_type) ||
          !relation.target_types.includes(assertion.target_type) ||
          assertion.assertion_owner !== relation.assertion_owner_mapping ||
          assertion.owner_evidence_sha256 !==
            definitionContract.owner_evidence_sha256 ||
          assertion.exact_assertion !== true) {
        fail("RMT_OP_RELATION_ASSERTION_ID_DRIFT");
      }
    }
  }

  const committed = observations.observations.find(
    ({case_id}) => case_id === "committed-success",
  );
  if (!committed) fail("RMT_OP_RELATION_POSITIVE_MISSING");
  const hostileEvidence = EXPECTED_HOSTILES.map((expected) => {
    const hostile = decodeOperationHostileFixtureV1(raw[expected.role]!);
    if (hostile.hostile_id !== expected.hostile_id ||
        hostile.expected_code !== expected.expected_code ||
        hostile.proof_owner_swu !== "RMT-OP-008") {
      fail("RMT_OP_RELATION_HOSTILE_CATALOGUE_DRIFT");
    }
    const mutated = applyOperationHostile(committed, hostile.hostile_id);
    const evaluation = evaluateStateChangingAction(
      definition,
      denominator,
      mutated,
    );
    if (mutated.observation_sha256 === committed.observation_sha256 ||
        evaluation.verdict !== "fail" ||
        canonicalJson(evaluation.findings.map(({code}) => code)) !==
          canonicalJson([hostile.expected_code])) {
      fail("RMT_OP_RELATION_HOSTILE_SURVIVED");
    }
    return Object.freeze({
      hostile_id: hostile.hostile_id,
      expected_code: hostile.expected_code,
      observed_codes: Object.freeze(evaluation.findings.map(({code}) => code)),
      status: "killed" as const,
      semantic_non_noop: true as const,
    });
  });

  const relationContracts = binding.relation_blueprints.map((blueprint) => {
    const fixture = definition.relation_contracts.find(
      ({contract_id}) => contract_id === blueprint.contract_id,
    );
    if (!fixture) fail("RMT_OP_RELATION_FIXTURE_CONTRACT_MISSING");
    return Object.freeze({
      ...blueprint,
      fixture_owner_evidence_sha256: fixture.owner_evidence_sha256,
      fixture_owner_evidence_classification:
        "synthetic-family-fixture-placeholder" as const,
    });
  });
  validateFrozenSourceInventory(binding);
  const proofBody = {
    schema_version: "OperationRelationProof/v1" as const,
    proof_id: "operation.wp-rmt-002.relations/v1",
    result: "pass" as const,
    binding_sha256: binding.binding_sha256,
    semantic_plan_epoch_id: binding.semantic_plan_epoch_id,
    semantic_contract_digest: binding.semantic_contract_digest,
    relation_contracts: Object.freeze(relationContracts),
    s1_handle_blueprint: binding.s1_handle_blueprint,
    family_fixture_observation_ids: Object.freeze(
      observations.observations.map(({observation_id}) => observation_id),
    ),
    family_fixture_assertions_classification:
      "representability-only-not-live-relation-evidence" as const,
    hostile_evidence: Object.freeze(hostileEvidence),
    upstream_closure: Object.freeze({
      source_role_count: 25 as const,
      source_size_bytes: 2993281 as const,
      source_aggregate_sha256:
        "7e6da173a9c889edd461b6dbaa524d50246e59345d057e0de7651095cf30992c",
      ...upstreamClosure,
    }),
    relation_contract_count: 4 as const,
    blueprint_relation_count: 4 as const,
    materialized_relation_count: 0 as const,
    s1_handle_materialized: false as const,
    no_self_authored_authority: true as const,
    publication_authority: false as const,
    claim_ceiling: binding.claim_ceiling,
    authority_effect: "none" as const,
  };
  return Object.freeze({
    ...proofBody,
    proof_sha256: sha256Value(proofBody),
  });
};
