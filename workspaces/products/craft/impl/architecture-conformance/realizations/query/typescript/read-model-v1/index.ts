import {execFile} from "node:child_process";
import {createHash} from "node:crypto";
import {promisify} from "node:util";
import ts from "typescript";

import {
  DECLARED_READ_LIFECYCLE_PATHS,
  EFFECT_CHANNELS,
  canonicalEffectObservationJson,
  mintDeclaredReadLifecycleObservationV1,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../../kernel/evidence/effect-observation/index.js";
import {
  applyReadModelQueryMutant,
  canonicalReadModelQueryJson,
  decodeReadModelQueryDefinitionV1,
  decodeReadModelQueryDenominatorV1,
  decodeReadModelQueryMutationCatalogueV1,
  decodeReadModelQueryObservationV1,
  evaluateReadModelQuery,
  mintReadModelQueryObservationV1,
  sha256ReadModelQueryBytes,
  sha256ReadModelQueryValue,
  type ReadModelQueryFindingCode,
  type ReadModelQueryObservationV1,
} from "../../../../families/read-model/index.js";
import {inspectTypeScriptQueryClosedSubset} from "./closed-subset.js";

type JsonObject = Record<string, unknown>;
type ExactRef = Readonly<{path: string; sha256: string}>;

export const TYPESCRIPT_QUERY_RAW_PATHS = Object.freeze({
  definition:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/definition.json",
  denominator:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/denominator.json",
  mutations:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/fixtures/complete-settlement/mutants.json",
  descriptor:
    "projects/domainspec-v2/development/remaining-meta-types/admissions/query/cross-language-realization-descriptor.json",
  source:
    "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/query-v1.ts",
  observer:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/closed-subset.ts",
  proof_builder:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/index.ts",
  provider:
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-query-v1.ts",
  family_api:
    "projects/domainspec-v2/impl/architecture-conformance/families/read-model/index.ts",
  kernel_api:
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/effect-observation/index.ts",
  binding:
    "projects/domainspec-v2/impl/architecture-conformance/realizations/query/typescript/read-model-v1/typescript-binding.json",
});

export type TypeScriptQueryRawInputs = Readonly<Record<
keyof typeof TYPESCRIPT_QUERY_RAW_PATHS, string
>>;

type TypeScriptQueryBindingV1 = Readonly<{
  schema_version: "TypeScriptQueryBinding/v1";
  binding_id: "typescript.complete-settlement.bound-query/v1";
  target_id: "query.typescript.complete-settlement/v1";
  protocol_id: "typescript.bound-query/v1";
  output_concept_id: "settlement.CompleteSettlementView";
  definition_ref: ExactRef;
  denominator_ref: ExactRef;
  mutation_catalogue_ref: ExactRef;
  descriptor_ref: ExactRef;
  source_ref: ExactRef;
  observer_ref: ExactRef;
  proof_builder_ref: ExactRef;
  provider_ref: ExactRef;
  family_api_ref: ExactRef;
  kernel_api_ref: ExactRef;
  observer_id: "observer.typescript-query-closed-subset/v1";
  observer_owner_ref: "typescript-query-proof-harness";
  symbol_name: "readCompleteSettlement";
  proof_mechanism:
    "exact-ast-static-exclusion-plus-harness-read-trace-in-two-fresh-processes";
  authority_effect: "none";
  binding_sha256: string;
}>;

const executeFile = promisify(execFile);
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const sha256 = (value: string | Uint8Array): string => createHash("sha256")
  .update(value)
  .digest("hex");
const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail ? `${code}:${detail}` : code), {code});
};
const exactKeys = (
  value: JsonObject,
  expected: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(value).sort(compareUtf8);
  const wanted = [...expected].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) fail(code);
};
const parseJson = (bytes: string, code: string): JsonObject => {
  try {
    const parsed: unknown = JSON.parse(bytes);
    return isObject(parsed) ? parsed : fail(code);
  } catch (error: unknown) {
    if (isObject(error) && error.code === code) throw error;
    return fail(code);
  }
};
const decodeRef = (value: unknown, path: string): ExactRef => {
  if (!isObject(value)) return fail("TS_QUERY_BINDING_REF_INVALID", path);
  exactKeys(value, ["path", "sha256"], "TS_QUERY_BINDING_REF_INVALID");
  if (value.path !== path || typeof value.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/u.test(value.sha256)) {
    return fail("TS_QUERY_BINDING_REF_INVALID", path);
  }
  return Object.freeze({path, sha256: value.sha256});
};
const bindingBody = (binding: TypeScriptQueryBindingV1): unknown => {
  const {binding_sha256: _digest, ...body} = binding;
  return body;
};
const decodeBinding = (
  bytes: string,
  raw: TypeScriptQueryRawInputs,
): TypeScriptQueryBindingV1 => {
  const value = parseJson(bytes, "TS_QUERY_BINDING_JSON_INVALID");
  exactKeys(value, [
    "schema_version", "binding_id", "target_id", "protocol_id",
    "output_concept_id", "definition_ref", "denominator_ref",
    "mutation_catalogue_ref", "descriptor_ref", "source_ref",
    "observer_ref", "proof_builder_ref", "provider_ref", "family_api_ref",
    "kernel_api_ref", "observer_id", "observer_owner_ref", "symbol_name",
    "proof_mechanism", "authority_effect", "binding_sha256",
  ], "TS_QUERY_BINDING_SHAPE_INVALID");
  if (value.schema_version !== "TypeScriptQueryBinding/v1" ||
      value.binding_id !== "typescript.complete-settlement.bound-query/v1" ||
      value.target_id !== "query.typescript.complete-settlement/v1" ||
      value.protocol_id !== "typescript.bound-query/v1" ||
      value.output_concept_id !== "settlement.CompleteSettlementView" ||
      value.observer_id !== "observer.typescript-query-closed-subset/v1" ||
      value.observer_owner_ref !== "typescript-query-proof-harness" ||
      value.symbol_name !== "readCompleteSettlement" ||
      value.proof_mechanism !==
        "exact-ast-static-exclusion-plus-harness-read-trace-in-two-fresh-processes" ||
      value.authority_effect !== "none" ||
      typeof value.binding_sha256 !== "string") {
    return fail("TS_QUERY_BINDING_POLICY_INVALID");
  }
  const binding = Object.freeze({
    schema_version: "TypeScriptQueryBinding/v1" as const,
    binding_id: "typescript.complete-settlement.bound-query/v1" as const,
    target_id: "query.typescript.complete-settlement/v1" as const,
    protocol_id: "typescript.bound-query/v1" as const,
    output_concept_id: "settlement.CompleteSettlementView" as const,
    definition_ref: decodeRef(value.definition_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.definition),
    denominator_ref: decodeRef(value.denominator_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.denominator),
    mutation_catalogue_ref: decodeRef(value.mutation_catalogue_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.mutations),
    descriptor_ref: decodeRef(value.descriptor_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.descriptor),
    source_ref: decodeRef(value.source_ref, TYPESCRIPT_QUERY_RAW_PATHS.source),
    observer_ref: decodeRef(value.observer_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.observer),
    proof_builder_ref: decodeRef(value.proof_builder_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.proof_builder),
    provider_ref: decodeRef(value.provider_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.provider),
    family_api_ref: decodeRef(value.family_api_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.family_api),
    kernel_api_ref: decodeRef(value.kernel_api_ref,
      TYPESCRIPT_QUERY_RAW_PATHS.kernel_api),
    observer_id: "observer.typescript-query-closed-subset/v1" as const,
    observer_owner_ref: "typescript-query-proof-harness" as const,
    symbol_name: "readCompleteSettlement" as const,
    proof_mechanism:
      "exact-ast-static-exclusion-plus-harness-read-trace-in-two-fresh-processes" as const,
    authority_effect: "none" as const,
    binding_sha256: value.binding_sha256,
  }) satisfies TypeScriptQueryBindingV1;
  if (sha256ReadModelQueryBytes(canonicalReadModelQueryJson(
    bindingBody(binding),
  )) !== binding.binding_sha256) fail("TS_QUERY_BINDING_DIGEST_STALE");
  const roles = Object.freeze({
    definition_ref: "definition",
    denominator_ref: "denominator",
    mutation_catalogue_ref: "mutations",
    descriptor_ref: "descriptor",
    source_ref: "source",
    observer_ref: "observer",
    proof_builder_ref: "proof_builder",
    provider_ref: "provider",
    family_api_ref: "family_api",
    kernel_api_ref: "kernel_api",
  } as const);
  for (const [refName, role] of Object.entries(roles) as readonly [
    keyof typeof roles,
    keyof TypeScriptQueryRawInputs,
  ][]) {
    if (sha256(raw[role]) !== binding[refName].sha256) {
      return fail("TS_QUERY_BINDING_INPUT_STALE", role);
    }
  }
  return binding;
};

const CHILD_SCRIPT = `
const source = Buffer.from(process.env.DS_QUERY_SOURCE ?? "", "base64").toString("utf8");
const payload = JSON.parse(Buffer.from(process.env.DS_QUERY_PAYLOAD ?? "", "base64").toString("utf8"));
const freeze = value => { if (value && typeof value === "object") { Object.freeze(value); for (const child of Object.values(value)) freeze(child); } return value; };
const input = freeze(JSON.parse(JSON.stringify(payload.input)));
const fixtures = freeze(JSON.parse(JSON.stringify(payload.fixtures)));
const trace = [];
const read = async (targetId, settlementId) => {
  if (settlementId !== input.settlement_id || !(targetId in fixtures)) process.exit(31);
  trace.push({target_id: targetId, channel: "filesystem", outcome: "success"});
  return freeze(JSON.parse(JSON.stringify(fixtures[targetId])));
};
const moduleUrl = "data:text/javascript;base64," + Buffer.from(source).toString("base64");
const target = await import(moduleUrl);
const result = await target.readCompleteSettlement(input, read);
if (!result || Object.getPrototypeOf(result) !== Object.prototype) process.exit(32);
const keys = Object.keys(result);
const expected = ["settlement_id","settlement_status","gross_amount_minor","payout_id","payout_status"];
if (JSON.stringify(keys) !== JSON.stringify(expected)) process.exit(33);
if (Object.values(result).some(value => typeof value !== "string" && !Number.isSafeInteger(value))) process.exit(34);
await new Promise(resolve => setImmediate(resolve));
process.stdout.write(JSON.stringify({pid: process.pid, trace, result: JSON.parse(JSON.stringify(result))}));
`;

const compileTarget = (source: string): string => {
  const result = ts.transpileModule(source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      strict: true,
      isolatedModules: true,
    },
    fileName: "query-v1.ts",
    reportDiagnostics: true,
  });
  if ((result.diagnostics ?? []).some((item) =>
    item.category === ts.DiagnosticCategory.Error)) {
    return fail("TS_QUERY_COMPILE_FAILED");
  }
  return result.outputText;
};

type ChildTrace = Readonly<{
  pid: number;
  trace: readonly Readonly<{
    target_id: string;
    channel: "filesystem";
    outcome: "success";
  }>[];
  result: Readonly<Record<string, string | number>>;
}>;

const runFreshProcess = async (
  compiledSource: string,
  input: Readonly<Record<string, unknown>>,
  fixtures: Readonly<Record<string, Readonly<Record<string, string | number>>>>,
): Promise<ChildTrace> => {
  const payload = Buffer.from(JSON.stringify({input, fixtures}), "utf8")
    .toString("base64");
  const {stdout, stderr} = await executeFile(process.execPath, [
    "--input-type=module",
    "--eval",
    CHILD_SCRIPT,
  ], {
    env: {
      DS_QUERY_SOURCE: Buffer.from(compiledSource, "utf8").toString("base64"),
      DS_QUERY_PAYLOAD: payload,
    },
    timeout: 10_000,
    maxBuffer: 1_048_576,
  }).catch((error: unknown) => fail("TS_QUERY_FRESH_PROCESS_FAILED",
    error instanceof Error ? error.message : String(error)));
  if (stderr.length > 0) fail("TS_QUERY_FRESH_PROCESS_STDERR", stderr);
  const result = parseJson(stdout, "TS_QUERY_FRESH_PROCESS_OUTPUT_INVALID");
  if (!Number.isSafeInteger(result.pid) || !Array.isArray(result.trace) ||
      !isObject(result.result)) {
    return fail("TS_QUERY_FRESH_PROCESS_OUTPUT_INVALID");
  }
  return Object.freeze({
    pid: result.pid as number,
    trace: Object.freeze(result.trace.map((item) => {
      if (!isObject(item) || typeof item.target_id !== "string" ||
          item.channel !== "filesystem" || item.outcome !== "success") {
        return fail("TS_QUERY_FRESH_PROCESS_TRACE_INVALID");
      }
      return Object.freeze({
        target_id: item.target_id,
        channel: "filesystem" as const,
        outcome: "success" as const,
      });
    })),
    result: Object.freeze(result.result as Record<string, string | number>),
  });
};

const SOURCE_HOSTILES = Object.freeze([
  ["swapped-reads", (source: string) => source
    .replaceAll("settlement.read.settlement-by-id", "TEMP")
    .replaceAll("settlement.read.payout-by-settlement",
      "settlement.read.settlement-by-id")
    .replaceAll("TEMP", "settlement.read.payout-by-settlement")],
  ["duplicate-read", (source: string) => source.replaceAll(
    "settlement.read.payout-by-settlement",
    "settlement.read.settlement-by-id",
  )],
  ["hidden-write", (source: string) => source.replace(
    "const settlement =", "globalThis.queryLeak = input; const settlement =",
  )],
  ["write-restore", (source: string) => source.replace(
    "const settlement =",
    "const prior = globalThis.queryLeak; globalThis.queryLeak = input; globalThis.queryLeak = prior; const settlement =",
  )],
  ["deferred-write", (source: string) => source.replace(
    "const settlement =", "queueMicrotask(() => { globalThis.queryLeak = input; }); const settlement =",
  )],
  ["dynamic-import", (source: string) => source.replace(
    "const settlement =", "await import('node:fs'); const settlement =",
  )],
  ["computed-read", (source: string) => source.replace(
    "await read(", "await read.call(globalThis,",
  )],
  ["extra-output", (source: string) => source.replace(
    "payout_status: payout.payout_status,",
    "payout_status: payout.payout_status, internal_debug_marker: 'leaked',",
  )],
] as const);

export const assertTypeScriptQueryAdapterBoundary = (input: Readonly<{
  observation_json: string;
  expected_target_id: string;
  expected_source_sha256: string;
  expected_protocol_id: "typescript.bound-query/v1";
  expected_output_concept_id: "settlement.CompleteSettlementView";
  observed_output_concept_id: string;
  lifecycle_basis: string;
}>): ReadModelQueryObservationV1 => {
  const observation = decodeReadModelQueryObservationV1(
    input.observation_json,
  );
  if (observation.target.target_id !== input.expected_target_id ||
      observation.target.target_sha256 !== input.expected_source_sha256 ||
      observation.target.language !== "typescript" ||
      observation.target.protocol_id !== input.expected_protocol_id ||
      input.observed_output_concept_id !== input.expected_output_concept_id ||
      observation.read_lifecycle_observation.declared_read_attempts.some(
        ({outcome}) => outcome !== "success",
      ) || input.lifecycle_basis !==
        "native-promise-await-plus-closed-plain-data-result-static-exclusion") {
    return fail("TS_QUERY_ADAPTER_PREFLIGHT_FAILED");
  }
  return observation;
};

export const buildTypeScriptQueryProof = async (
  raw: TypeScriptQueryRawInputs,
) => {
  const binding = decodeBinding(raw.binding, raw);
  const definition = decodeReadModelQueryDefinitionV1(
    raw.definition,
    TYPESCRIPT_QUERY_RAW_PATHS.descriptor,
    raw.descriptor,
  );
  const denominator = decodeReadModelQueryDenominatorV1(
    raw.denominator,
    raw.definition,
    definition,
    TYPESCRIPT_QUERY_RAW_PATHS.definition,
  );
  const mutationCatalogue = decodeReadModelQueryMutationCatalogueV1(
    raw.mutations,
    denominator,
  );
  const closedSubset = inspectTypeScriptQueryClosedSubset(raw.source);
  if (closedSubset.source_sha256 !== binding.source_ref.sha256 ||
      definition.output_concept.concept_id !== binding.output_concept_id ||
      canonicalReadModelQueryJson(closedSubset.ordered_read_targets) !==
        canonicalReadModelQueryJson(definition.read_targets.map(
          ({target_id: targetId}) => targetId,
        ))) {
    return fail("TS_QUERY_CLOSED_SUBSET_BINDING_STALE");
  }
  const compiled = compileTarget(raw.source);
  const ownerCase = definition.cases[0];
  if (!ownerCase) return fail("TS_QUERY_OWNER_CASE_MISSING");
  const fixtures = Object.freeze({
    "settlement.read.settlement-by-id": Object.freeze({
      settlement_status: ownerCase.expected_result.settlement_status as string,
      gross_amount_minor: ownerCase.expected_result.gross_amount_minor as number,
      payout_id: "unused-settlement-payout-id",
      payout_status: "unused-settlement-payout-status",
    }),
    "settlement.read.payout-by-settlement": Object.freeze({
      settlement_status: "unused-payout-settlement-status",
      gross_amount_minor: 0,
      payout_id: ownerCase.expected_result.payout_id as string,
      payout_status: ownerCase.expected_result.payout_status as string,
    }),
  });
  const first = await runFreshProcess(compiled, ownerCase.inputs, fixtures);
  const second = await runFreshProcess(compiled, ownerCase.inputs, fixtures);
  if (first.pid === second.pid ||
      canonicalReadModelQueryJson(first.trace) !==
        canonicalReadModelQueryJson(second.trace) ||
      sha256ReadModelQueryValue(first.result) !==
        sha256ReadModelQueryValue(second.result)) {
    return fail("TS_QUERY_FRESH_PROCESS_REPLAY_MISMATCH");
  }
  const expectedTrace = definition.read_targets.map(({target_id: targetId}) => ({
    target_id: targetId,
    channel: "filesystem",
    outcome: "success",
  }));
  if (canonicalReadModelQueryJson(first.trace) !==
      canonicalReadModelQueryJson(expectedTrace)) {
    return fail("TS_QUERY_RUNTIME_READ_TRACE_MISMATCH");
  }
  const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
    role: "independent-effect-observer" as const,
    observer_id: binding.observer_id,
    observer_sha256: binding.observer_ref.sha256,
    owner_ref: binding.observer_owner_ref,
    provider_id: "typescript-query-v1",
    provider_sha256: binding.provider_ref.sha256,
  });
  const targetRef = Object.freeze({
    target_id: binding.target_id,
    target_sha256: binding.source_ref.sha256,
  });
  const readsByChannel = new Map<string, number>();
  for (const entry of first.trace) {
    readsByChannel.set(entry.channel,
      (readsByChannel.get(entry.channel) ?? 0) + 1);
  }
  const effectObservation = mintEffectObservationV1({
    schema_version: "EffectObservation/v1",
    observation_id: "observation.effect.query.typescript.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    channels: EFFECT_CHANNELS.map((channel) => ({
      channel,
      coverage: "supported" as const,
      read_count: readsByChannel.get(channel) ?? 0,
      write_count: 0,
      escape_count: 0,
      deferred_count: 0,
    })),
    result: {consumption: "complete", mutable_alias_observed: false},
    quiescence: {observed: true, pending_count: 0},
    authority_effect: "none",
  });
  const lifecycleObservation = mintDeclaredReadLifecycleObservationV1({
    schema_version: "DeclaredReadLifecycleObservation/v1",
    observation_id:
      "observation.declared-read.query.typescript.complete-settlement/v1",
    source_kind: "independent-owner-observation",
    target_ref: targetRef,
    observer_ref: lockedObserver,
    declared_read_attempts: first.trace.map((entry, ordinal) => ({
      ordinal,
      ...entry,
      lifecycle_path: "iterate-or-await" as const,
    })),
    lifecycle_paths: DECLARED_READ_LIFECYCLE_PATHS.map((lifecycle_path) => ({
      lifecycle_path,
      coverage: "supported" as const,
    })),
    effect_observation: effectObservation,
    source_support: "supported-static",
    write_then_restore_observed: false,
    authority_effect: "none",
  });
  const minted = mintReadModelQueryObservationV1({
    schema_version: "ReadModelQueryObservation/v1",
    observation_id:
      "observation.query.typescript.complete-settlement/v1",
    source_kind: "target-observation",
    target: {
      ...targetRef,
      language: "typescript",
      protocol_id: binding.protocol_id,
    },
    definition_ref: denominator.owner_definition_ref,
    binding: {
      descriptor_id: definition.descriptor_ref.descriptor_id,
      descriptor_sha256: definition.descriptor_ref.sha256,
      provider_id: lockedObserver.provider_id,
      provider_sha256: lockedObserver.provider_sha256,
    },
    observed_result: {
      case_id: ownerCase.case_id,
      input_sha256: sha256ReadModelQueryValue(ownerCase.inputs),
      result: first.result,
      result_sha256: sha256ReadModelQueryValue(first.result),
      declared_failure: null,
    },
    read_lifecycle_observation: lifecycleObservation,
    authority_effect: "none",
  });
  const observation = assertTypeScriptQueryAdapterBoundary({
    observation_json: canonicalReadModelQueryJson(minted),
    expected_target_id: binding.target_id,
    expected_source_sha256: binding.source_ref.sha256,
    expected_protocol_id: binding.protocol_id,
    expected_output_concept_id: binding.output_concept_id,
    observed_output_concept_id: definition.output_concept.concept_id,
    lifecycle_basis: closedSubset.lifecycle_basis,
  });
  const familyEvaluation = evaluateReadModelQuery({
    definition,
    denominator,
    observation,
    locked_observer_ref: lockedObserver,
    locked_target_ref: targetRef,
  });
  if (familyEvaluation.verdict !== "pass") {
    return fail("TS_QUERY_FAMILY_EVALUATION_BLOCKED",
      familyEvaluation.findings.map(({code}) => code).join(","));
  }
  const familyControls = mutationCatalogue.mutations.map((mutation) => {
    const variants = mutation.variants.map((variant) => {
      const evaluation = evaluateReadModelQuery({
        definition,
        denominator,
        observation: applyReadModelQueryMutant(observation, mutation, variant),
        locked_observer_ref: lockedObserver,
        locked_target_ref: targetRef,
      });
      const observed = new Set(evaluation.findings.map(({code}) => code));
      const killed = evaluation.verdict === "fail" &&
        mutation.expected_finding_codes.every((code) => observed.has(
          code as ReadModelQueryFindingCode,
        ));
      if (!killed) return fail("TS_QUERY_FAMILY_CONTROL_SURVIVED",
        `${mutation.mutation_id}:${variant}`);
      return Object.freeze({variant, status: "killed" as const});
    });
    return Object.freeze({
      mutation_id: mutation.mutation_id,
      evidence_kind: "predecessor-family-observation-control" as const,
      variants: Object.freeze(variants),
    });
  });
  const sourceHostiles = SOURCE_HOSTILES.map(([hostileId, mutate]) => {
    try {
      inspectTypeScriptQueryClosedSubset(mutate(raw.source));
    } catch {
      return Object.freeze({
        hostile_id: hostileId,
        evidence_kind: "typescript-source-hostile" as const,
        status: "killed" as const,
      });
    }
    return fail("TS_QUERY_SOURCE_HOSTILE_SURVIVED", hostileId);
  });
  return Object.freeze({
    schema_version: "TypeScriptQueryProof/v1" as const,
    target: Object.freeze({
      target_id: binding.target_id,
      target_sha256: binding.source_ref.sha256,
      language: "typescript" as const,
      protocol_id: binding.protocol_id,
      output_concept_id: binding.output_concept_id,
    }),
    binding: Object.freeze({
      binding_id: binding.binding_id,
      binding_sha256: binding.binding_sha256,
    }),
    observation,
    family_evaluation: familyEvaluation,
    closed_subset: closedSubset,
    process_evidence: Object.freeze({
      executions: 2,
      distinct_pids: 2,
      trace_sha256: sha256ReadModelQueryValue(first.trace),
      result_sha256: sha256ReadModelQueryValue(first.result),
      input_materialization: "json-inert-deep-frozen" as const,
      read_fixtures: "json-inert-deep-frozen" as const,
      lifecycle_basis: closedSubset.lifecycle_basis,
    }),
    accounting: Object.freeze({
      positives: Object.freeze({declared: 4, passed: 4}),
      source_hostiles: Object.freeze({
        declared: sourceHostiles.length,
        killed: sourceHostiles.length,
      }),
      predecessor_family_controls: Object.freeze({
        declared_classes: familyControls.length,
        killed_classes: familyControls.length,
      }),
    }),
    source_hostiles: Object.freeze(sourceHostiles),
    predecessor_family_controls: Object.freeze(familyControls),
    claim_ceiling:
      "owner-fixture TypeScript exact-source Query proof over JSON-materialized inert inputs and read fixtures, two fresh child processes, an actual ordered harness read trace, a closed plain scalar result, exact adapter bindings, static exclusion of unsupported lifecycle and effect surfaces, and family evaluation; no arbitrary TypeScript or generated source, getter Proxy or mutable caller input, runtime or OS interception, failure-path behavior, business correctness beyond the fixture, parity, registration, promotion, release, deployment, or production claim",
    authority_effect: "none" as const,
  });
};
