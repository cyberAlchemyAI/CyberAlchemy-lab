import { createHash } from "node:crypto";

import {
  decodeFiniteVocabularyDenominatorV1,
  evaluateFiniteVocabulary,
  mintFiniteVocabularyObservationV1,
  type FiniteVocabularyEvaluationV1,
  type FiniteVocabularyObservationV1,
} from "../../families/finite-vocabulary/index.js";
import type { FactoryUpstreamResultV1 } from
  "../../factory/contracts/factory-node-provider-v1.js";
import { runTypeScriptEnumWireProbe } from "./typescript-wire-probe.js";

type JsonRecord = Record<string, unknown>;

const OWNER_PATH =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json";

export const ENUM_DIRECT_HANDLES = Object.freeze([
  Object.freeze({
    node_id: "enum.typescript.shipment-priority",
    provider_id: "typescript-enum-shipment-priority-semantic-slice-v1",
    target_id: "typescript.shipment-priority.owned-const-object-v1",
    language: "typescript" as const,
    protocol_id: "typescript.owned-const-object-enum/v1",
  }),
  Object.freeze({
    node_id: "enum.python.shipment-priority",
    provider_id: "python-enum-v1",
    target_id: "python.shipment-priority.nominal-enum-v1",
    language: "python" as const,
    protocol_id: "python.nominal-enum-explicit-wire/v1",
  }),
  Object.freeze({
    node_id: "enum.rust.shipment-priority",
    provider_id: "rust-enum-v1",
    target_id: "rust.shipment-priority.unit-variant-enum-v1",
    language: "rust" as const,
    protocol_id: "rust.nominal-enum-explicit-wire/v1",
  }),
] as const);

export const ENUM_COMPOSITION_NODE = Object.freeze({
  node_id: "enum.composition.shipment-priority",
  provider_id: "enum-composition-v1",
});

const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonRecord =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string, detail?: string): never => {
  throw Object.assign(new Error(detail === undefined ? code : `${code}:${detail}`), {
    code,
    detail: detail ?? null,
  });
};
const exactKeys = (actual: readonly string[], expected: readonly string[], code: string): void => {
  if (actual.length !== expected.length || actual.some((value, index) => value !== expected[index])) {
    fail(code);
  }
};
const jsonRecord = (value: unknown, code: string): JsonRecord =>
  isRecord(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && value.length > 0 ? value : fail(code);

const exactUpstream = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  expected: readonly Readonly<{ node_id: string; provider_id: string }>[],
): readonly FactoryUpstreamResultV1[] => {
  exactKeys(Object.keys(upstream), expected.map(({ node_id }) => node_id),
    "ENUM_JOIN_DEPENDENCY_ORDER_MISMATCH");
  return Object.freeze(expected.map(({ node_id, provider_id }) => {
    const handle = upstream[node_id] ?? fail("ENUM_JOIN_HANDLE_MISSING", node_id);
    if (handle.node_id !== node_id || handle.provider_id !== provider_id ||
        !/^[a-f0-9]{64}$/u.test(handle.semantic_sha256)) {
      fail("ENUM_JOIN_HANDLE_IDENTITY_MISMATCH", node_id);
    }
    return handle;
  }));
};

type OwnerMember = Readonly<{ member_id: string; member_key: string; wire_value: string }>;
type PortableTarget = Readonly<{
  node_id: string;
  provider_id: string;
  semantic_sha256: string;
  target_id: string;
  observation: FiniteVocabularyObservationV1;
  family_evaluation: FiniteVocabularyEvaluationV1;
  native_diagnostic: Readonly<{
    relation: "collapsed-literal" | "nominal" | "not-observed";
    claim_scope: "native-diagnostic-only";
    evidence: unknown;
  }>;
}>;

export type EnumCompositionResultV1 = Readonly<{
  schema_version: "EnumComposedFrom/v1";
  result: "pass";
  relation: Readonly<{
    relation_id: "composed_from";
    subject: "candidate.logistics.shipment-priority";
    family_id: "family.finite-vocabulary.portable";
    source_node_ids: readonly string[];
    status: "pass";
  }>;
  owner_catalogue_ref: Readonly<{ catalogue_id: string; path: string; sha256: string }>;
  denominator_ref: Readonly<{ denominator_id: string; denominator_sha256: string }>;
  targets: readonly PortableTarget[];
  relation_obligations: readonly Readonly<{ obligation_id: string; status: "passed" }>[];
  claim_ceiling: string;
  authority_effect: "none";
  composition_sha256: string;
}>;

type TypeScriptCase = Readonly<{
  schema_version: "EnumAcceptanceCase/v1";
  case_id: "shipment-priority-v1";
  definition: Readonly<{
    concept_id: string;
    members: readonly Readonly<{ member_id: string; semantic_value: string }>[];
  }>;
  binding: Readonly<{ member_names: Readonly<Record<string, string>> }>;
}>;

const typeScriptObservation = (input: Readonly<{
  handle: FactoryUpstreamResultV1;
  ownerMembers: readonly OwnerMember[];
  ownerRef: Readonly<{ catalogue_id: string; path: string; sha256: string }>;
  caseBytes: string;
  expectedBytes: string;
}>): Readonly<{
  observation: FiniteVocabularyObservationV1;
  evidence: unknown;
}> => {
  const proof = jsonRecord(input.handle.semantic_output, "ENUM_TS_DIRECT_OUTPUT_INVALID");
  if (proof.schema_version !== "ShipmentPriorityProof/v1" || proof.result !== "pass" ||
      proof.case_id !== "shipment-priority-v1" || proof.positive_verdict !== "pass" ||
      !Array.isArray(proof.values) || !isRecord(proof.mutation) ||
      proof.mutation.status !== "killed") {
    fail("ENUM_TS_DIRECT_OUTPUT_INVALID");
  }
  const caseValue = JSON.parse(input.caseBytes) as TypeScriptCase;
  const expected = jsonRecord(JSON.parse(input.expectedBytes), "ENUM_TS_EXPECTED_INVALID");
  if (caseValue.schema_version !== "EnumAcceptanceCase/v1" ||
      caseValue.case_id !== "shipment-priority-v1" ||
      caseValue.definition.concept_id !== "candidate.logistics.shipment-priority" ||
      !Array.isArray(caseValue.definition.members) || !isRecord(caseValue.binding.member_names) ||
      !Array.isArray(expected.expected_values)) {
    fail("ENUM_TS_CASE_INVALID");
  }
  const caseMembers = caseValue.definition.members;
  if (caseMembers.length !== input.ownerMembers.length || input.ownerMembers.some((owner) => {
    const member = caseMembers.find(({ member_id: id }) => id === owner.member_id);
    return member?.semantic_value !== owner.wire_value ||
      caseValue.binding.member_names[owner.member_id] !== owner.member_key;
  })) {
    fail("ENUM_TS_OWNER_CASE_MISMATCH");
  }
  const observedValues = (proof.values as unknown[]).map(String).sort(compareUtf8);
  const expectedValues = input.ownerMembers.map(({ wire_value }) => wire_value).sort(compareUtf8);
  if (JSON.stringify(observedValues) !== JSON.stringify(expectedValues) ||
      JSON.stringify((expected.expected_values as unknown[]).map(String).sort(compareUtf8)) !==
        JSON.stringify(expectedValues)) {
    fail("ENUM_TS_DIRECT_VALUES_MISMATCH");
  }
  const wireProbe = runTypeScriptEnumWireProbe(input.ownerMembers);
  if (wireProbe.known.length !== input.ownerMembers.length ||
      wireProbe.known.some((result, index) =>
        result.outcome !== "member" ||
        result.parsed_member_id !== input.ownerMembers[index]?.member_id)) {
    fail("ENUM_TS_KNOWN_WIRE_PROBE_MISMATCH");
  }
  const observation = mintFiniteVocabularyObservationV1({
    schema_version: "FiniteVocabularyObservation/v1",
    observation_id: "typescript.shipment-priority.owned-const-object-v1",
    source_kind: "independent-owner-bound-positive",
    target: {
      target_id: "typescript.shipment-priority.owned-const-object-v1",
      language: "typescript",
      protocol_id: "typescript.owned-const-object-enum/v1",
    },
    owner_catalogue_ref: input.ownerRef,
    catalogue_origin: "owner-authored-admission-input",
    member_order_semantics: "none",
    members: input.ownerMembers.map((member, index) => Object.freeze({
      member_id: member.member_id,
      native_keys: Object.freeze([member.member_key]),
      emitted_wire: member.wire_value,
      parsed_member_id: wireProbe.known[index]!.parsed_member_id,
    })),
    unknown_wire: wireProbe.unknown,
    native_identity_diagnostic: Object.freeze({
      relation: "collapsed-literal",
      claim_scope: "native-diagnostic-only",
    }),
    authority_effect: "none",
  });
  return Object.freeze({
    observation,
    evidence: Object.freeze({
      direct_schema_version: proof.schema_version,
      values: Object.freeze(observedValues),
      mutation: Object.freeze({ ...(proof.mutation as JsonRecord) }),
      wire_probe: wireProbe,
    }),
  });
};

const composedTarget = (
  handle: FactoryUpstreamResultV1,
  expected: typeof ENUM_DIRECT_HANDLES[number],
): Readonly<{ observation: FiniteVocabularyObservationV1; evaluation: FiniteVocabularyEvaluationV1;
  evidence: unknown }> => {
  const output = jsonRecord(handle.semantic_output, "ENUM_DIRECT_OUTPUT_INVALID");
  const proof = jsonRecord(output.proof, "ENUM_DIRECT_OUTPUT_INVALID");
  const schema = expected.language === "python"
    ? "PythonEnumComposedProof/v1" : "RustEnumComposedProof/v1";
  if (proof.schema_version !== schema || proof.result !== "pass" ||
      !isRecord(proof.observation) || !isRecord(proof.family_evaluation) ||
      !isRecord(proof.native_proof)) {
    fail("ENUM_DIRECT_OUTPUT_INVALID", expected.language);
  }
  const observation = proof.observation as FiniteVocabularyObservationV1;
  const evaluation = proof.family_evaluation as FiniteVocabularyEvaluationV1;
  if (observation.target.target_id !== expected.target_id ||
      observation.target.language !== expected.language ||
      observation.target.protocol_id !== expected.protocol_id || evaluation.verdict !== "pass" ||
      evaluation.observation_ref.observation_sha256 !== observation.observation_sha256) {
    fail("ENUM_DIRECT_TARGET_MISMATCH", expected.language);
  }
  const nativeProof = proof.native_proof as JsonRecord;
  return Object.freeze({
    observation,
    evaluation,
    evidence: Object.freeze({
      native_properties: nativeProof.native_properties,
      hostile_probes: nativeProof.hostile_probes,
      ...(expected.language === "rust" ? { compiler: nativeProof.compiler } : {}),
    }),
  });
};

export const evaluateEnumComposition = (input: Readonly<{
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>;
  raw_inputs: Readonly<Record<string, string>>;
}>): EnumCompositionResultV1 => {
  const handles = exactUpstream(input.upstream, ENUM_DIRECT_HANDLES);
  exactKeys(Object.keys(input.raw_inputs), [
    "owner_catalogue", "denominator", "typescript_case", "typescript_expected",
  ], "ENUM_COMPOSITION_INPUT_SET_MISMATCH");
  const ownerBytes = input.raw_inputs.owner_catalogue ?? fail("ENUM_OWNER_INPUT_MISSING");
  const denominatorBytes = input.raw_inputs.denominator ?? fail("ENUM_DENOMINATOR_INPUT_MISSING");
  const decoded = decodeFiniteVocabularyDenominatorV1(
    denominatorBytes,
    ownerBytes,
    OWNER_PATH,
  );
  const owner = JSON.parse(ownerBytes) as { members: readonly OwnerMember[] };
  const ts = typeScriptObservation({
    handle: handles[0]!,
    ownerMembers: owner.members,
    ownerRef: decoded.denominator.owner_catalogue_ref,
    caseBytes: input.raw_inputs.typescript_case ?? fail("ENUM_TS_CASE_MISSING"),
    expectedBytes: input.raw_inputs.typescript_expected ?? fail("ENUM_TS_EXPECTED_MISSING"),
  });
  const tsEvaluation = evaluateFiniteVocabulary({
    denominator: decoded.denominator,
    owner_catalogue: decoded.owner_catalogue,
    observation: ts.observation,
  });
  const python = composedTarget(handles[1]!, ENUM_DIRECT_HANDLES[1]);
  const rust = composedTarget(handles[2]!, ENUM_DIRECT_HANDLES[2]);
  const source = [
    Object.freeze({ observation: ts.observation, evaluation: tsEvaluation, evidence: ts.evidence }),
    python,
    rust,
  ];
  if (source.some(({ observation, evaluation }) =>
    evaluation.verdict !== "pass" ||
    observation.owner_catalogue_ref.catalogue_id !== decoded.owner_catalogue.catalogue_id ||
    observation.owner_catalogue_ref.path !== decoded.denominator.owner_catalogue_ref.path ||
    observation.owner_catalogue_ref.sha256 !== decoded.denominator.owner_catalogue_ref.sha256 ||
    evaluation.denominator_ref.denominator_id !== decoded.denominator.denominator_id ||
    evaluation.denominator_ref.denominator_sha256 !== decoded.denominator.denominator_sha256)) {
    fail("ENUM_COMPOSITION_FAMILY_BINDING_MISMATCH");
  }
  const targets = Object.freeze(ENUM_DIRECT_HANDLES.map((expected, index) => Object.freeze({
    node_id: expected.node_id,
    provider_id: expected.provider_id,
    semantic_sha256: handles[index]!.semantic_sha256,
    target_id: expected.target_id,
    observation: source[index]!.observation,
    family_evaluation: source[index]!.evaluation,
    native_diagnostic: Object.freeze({
      ...source[index]!.observation.native_identity_diagnostic,
      evidence: source[index]!.evidence,
    }),
  })));
  const obligationIds = [
    "exact-direct-node-set", "exact-provider-set", "direct-semantic-bindings",
    "shared-owner-catalogue", "shared-family-denominator", "typescript-composed",
    "python-composed", "rust-composed",
  ];
  const withoutDigest = Object.freeze({
    schema_version: "EnumComposedFrom/v1" as const,
    result: "pass" as const,
    relation: Object.freeze({
      relation_id: "composed_from" as const,
      subject: "candidate.logistics.shipment-priority" as const,
      family_id: "family.finite-vocabulary.portable" as const,
      source_node_ids: Object.freeze(ENUM_DIRECT_HANDLES.map(({ node_id }) => node_id)),
      status: "pass" as const,
    }),
    owner_catalogue_ref: decoded.denominator.owner_catalogue_ref,
    denominator_ref: Object.freeze({
      denominator_id: decoded.denominator.denominator_id,
      denominator_sha256: decoded.denominator.denominator_sha256,
    }),
    targets,
    relation_obligations: Object.freeze(obligationIds.map((obligation_id) =>
      Object.freeze({ obligation_id, status: "passed" as const }))),
    claim_ceiling: "candidate-local composed_from proof binding three exact Enum direct handles to one owner-authored finite-vocabulary denominator",
    authority_effect: "none" as const,
  });
  return Object.freeze({
    ...withoutDigest,
    composition_sha256: sha256(JSON.stringify(withoutDigest)),
  });
};

type PortableProjection = Readonly<{
  members: readonly Readonly<{
    member_id: string;
    emitted_wire: string;
    parsed_member_id: string;
  }>[];
  unknown_wire: Readonly<{
    outcome: FiniteVocabularyObservationV1["unknown_wire"]["outcome"];
    error_code: string | null;
    parsed_member_id: string | null;
  }>;
}>;

const portableProjection = (observation: FiniteVocabularyObservationV1): PortableProjection =>
  Object.freeze({
    members: Object.freeze([...observation.members].map(({ member_id, emitted_wire,
      parsed_member_id }) => Object.freeze({ member_id, emitted_wire, parsed_member_id }))
      .sort((left, right) => compareUtf8(left.member_id, right.member_id))),
    unknown_wire: Object.freeze({
      outcome: observation.unknown_wire.outcome,
      error_code: observation.unknown_wire.error_code,
      parsed_member_id: observation.unknown_wire.parsed_member_id,
    }),
  });

export type EnumParityResultV1 = Readonly<{
  schema_version: "EnumPortableParity/v1";
  result: "pass";
  targets: readonly Readonly<{
    node_id: string;
    provider_id: string;
    target_id: string;
    semantic_sha256: string;
    portable_projection: PortableProjection;
    native_diagnostic: PortableTarget["native_diagnostic"];
  }>[];
  portable_obligations: readonly Readonly<{ obligation_id: string; status: "passed" }>[];
  excluded_native_diagnostics: readonly string[];
  composition_ref: Readonly<{ node_id: string; semantic_sha256: string; composition_sha256: string }>;
  claim_ceiling: string;
  authority_effect: "none";
  parity_sha256: string;
}>;

export const evaluateEnumParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
): EnumParityResultV1 => {
  const expected = Object.freeze([...ENUM_DIRECT_HANDLES, ENUM_COMPOSITION_NODE]);
  const handles = exactUpstream(upstream, expected);
  const compositionHandle = handles[3]!;
  const composition = jsonRecord(compositionHandle.semantic_output,
    "ENUM_PARITY_COMPOSITION_INVALID") as unknown as EnumCompositionResultV1;
  if (composition.schema_version !== "EnumComposedFrom/v1" || composition.result !== "pass" ||
      composition.relation?.relation_id !== "composed_from" ||
      composition.relation.status !== "pass" || !Array.isArray(composition.targets) ||
      composition.targets.length !== 3 || composition.authority_effect !== "none" ||
      JSON.stringify(composition.relation.source_node_ids) !==
        JSON.stringify(ENUM_DIRECT_HANDLES.map(({ node_id }) => node_id))) {
    fail("ENUM_PARITY_RELATION_BYPASS");
  }
  const { composition_sha256: compositionSha256, ...compositionBody } = composition;
  if (compositionSha256 !== sha256(JSON.stringify(compositionBody))) {
    fail("ENUM_PARITY_COMPOSITION_DIGEST_MISMATCH");
  }
  const targetIds = new Set<string>();
  const semanticHandles = new Set<string>();
  const targets = ENUM_DIRECT_HANDLES.map((direct, index) => {
    const target = composition.targets[index] ?? fail("ENUM_PARITY_TARGET_MISSING");
    const directHandle = handles[index]!;
    if (target.node_id !== direct.node_id || target.provider_id !== direct.provider_id ||
        target.target_id !== direct.target_id ||
        target.observation.target.target_id !== direct.target_id ||
        target.observation.target.language !== direct.language ||
        target.observation.target.protocol_id !== direct.protocol_id) {
      fail("ENUM_PARITY_TARGET_BINDING_MISMATCH", direct.language);
    }
    if (target.semantic_sha256 !== directHandle.semantic_sha256) {
      fail("ENUM_PARITY_SEMANTIC_HANDLE_MISMATCH", direct.language);
    }
    if (target.observation.observation_id !== direct.target_id ||
        target.family_evaluation.verdict !== "pass" ||
        target.family_evaluation.observation_ref.observation_sha256 !==
          target.observation.observation_sha256) {
      fail("ENUM_PARITY_OBSERVATION_BINDING_MISMATCH", direct.language);
    }
    if (targetIds.has(target.target_id) || semanticHandles.has(target.semantic_sha256)) {
      fail("ENUM_PARITY_DUPLICATE_SEMANTIC_HANDLE");
    }
    targetIds.add(target.target_id);
    semanticHandles.add(target.semantic_sha256);
    if (target.observation.owner_catalogue_ref.catalogue_id !==
          composition.owner_catalogue_ref.catalogue_id ||
        target.observation.owner_catalogue_ref.path !== composition.owner_catalogue_ref.path ||
        target.observation.owner_catalogue_ref.sha256 !== composition.owner_catalogue_ref.sha256) {
      fail("ENUM_PARITY_OWNER_MISMATCH");
    }
    if (target.family_evaluation.denominator_ref.denominator_id !==
          composition.denominator_ref.denominator_id ||
        target.family_evaluation.denominator_ref.denominator_sha256 !==
          composition.denominator_ref.denominator_sha256) {
      fail("ENUM_PARITY_DENOMINATOR_MISMATCH");
    }
    if (target.native_diagnostic.claim_scope !== "native-diagnostic-only") {
      fail("ENUM_PARITY_NATIVE_DIAGNOSTIC_SCOPE_INVALID");
    }
    const expectedRelation = direct.language === "typescript" ? "collapsed-literal" : "nominal";
    if (target.native_diagnostic.relation !== expectedRelation) {
      fail("ENUM_PARITY_NATIVE_DIAGNOSTIC_TARGET_INVALID", direct.language);
    }
    return Object.freeze({
      node_id: target.node_id,
      provider_id: target.provider_id,
      target_id: target.target_id,
      semantic_sha256: target.semantic_sha256,
      portable_projection: portableProjection(target.observation),
      native_diagnostic: target.native_diagnostic,
    });
  });
  const baseline = targets[0]!.portable_projection;
  for (const target of targets.slice(1)) {
    const left = baseline.members;
    const right = target.portable_projection.members;
    if (left.length !== right.length || left.some((member, index) =>
      member.member_id !== right[index]?.member_id)) fail("ENUM_PARITY_MEMBER_MISMATCH");
    if (left.some((member, index) => member.emitted_wire !== right[index]?.emitted_wire)) {
      fail("ENUM_PARITY_WIRE_MISMATCH");
    }
    if (left.some((member, index) => member.parsed_member_id !== right[index]?.parsed_member_id)) {
      fail("ENUM_PARITY_PARSE_MISMATCH");
    }
    if (JSON.stringify(baseline.unknown_wire) !==
        JSON.stringify(target.portable_projection.unknown_wire)) {
      fail("ENUM_PARITY_UNKNOWN_WIRE_MISMATCH");
    }
  }
  const obligationIds = [
    "exact-target-handles", "member-id-set", "native-key-independent",
    "member-wire-map", "known-wire-parse", "unknown-wire-outcome",
    "owner-binding", "denominator-binding", "native-diagnostics-preserved",
  ];
  const withoutDigest = Object.freeze({
    schema_version: "EnumPortableParity/v1" as const,
    result: "pass" as const,
    targets: Object.freeze(targets),
    portable_obligations: Object.freeze(obligationIds.map((obligation_id) =>
      Object.freeze({ obligation_id, status: "passed" as const }))),
    excluded_native_diagnostics: Object.freeze([
      "TypeScript collapsed-literal runtime identity",
      "Python nominal identity and native hostile probes",
      "Rust nominal identity, traits, rustc version, and compiler diagnostics",
      "native member keys",
    ]),
    composition_ref: Object.freeze({
      node_id: ENUM_COMPOSITION_NODE.node_id,
      semantic_sha256: compositionHandle.semantic_sha256,
      composition_sha256: composition.composition_sha256,
    }),
    claim_ceiling: "portable owner-bound Enum member/wire/parse parity across three exact candidate-local target handles; native diagnostics remain nonportable evidence",
    authority_effect: "none" as const,
  });
  return Object.freeze({ ...withoutDigest, parity_sha256: sha256(JSON.stringify(withoutDigest)) });
};

const clone = <T>(value: T): T => structuredClone(value);
const resealComposition = (composition: any): void => {
  const { composition_sha256: _prior, ...body } = composition;
  composition.composition_sha256 = sha256(JSON.stringify(body));
};

export const proveEnumParity = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
): Readonly<{
  parity: EnumParityResultV1;
  mutants: readonly Readonly<{ mutant_id: string; expected_code: string; status: "killed" }>[];
}> => {
  const parity = evaluateEnumParity(upstream);
  const mutations: readonly Readonly<{
    mutant_id: string;
    expected_code: string;
    apply: (composition: any, handles: any) => void;
  }>[] = [
    { mutant_id: "wrong-target", expected_code: "ENUM_PARITY_TARGET_BINDING_MISMATCH",
      apply: (value) => { value.targets[1].target_id = "python.wrong"; } },
    { mutant_id: "wrong-observation", expected_code: "ENUM_PARITY_TARGET_BINDING_MISMATCH",
      apply: (value) => { value.targets[1].observation.target.target_id = "python.wrong"; } },
    { mutant_id: "wrong-owner", expected_code: "ENUM_PARITY_OWNER_MISMATCH",
      apply: (value) => { value.targets[1].observation.owner_catalogue_ref.sha256 = "0".repeat(64); } },
    { mutant_id: "wrong-denominator", expected_code: "ENUM_PARITY_DENOMINATOR_MISMATCH",
      apply: (value) => { value.targets[1].family_evaluation.denominator_ref.denominator_sha256 = "0".repeat(64); } },
    { mutant_id: "duplicate-semantic-handle", expected_code: "ENUM_PARITY_DUPLICATE_SEMANTIC_HANDLE",
      apply: (value, handles) => {
        value.targets[1].semantic_sha256 = value.targets[0].semantic_sha256;
        handles[ENUM_DIRECT_HANDLES[1].node_id].semantic_sha256 =
          value.targets[0].semantic_sha256;
      } },
    { mutant_id: "member-mismatch", expected_code: "ENUM_PARITY_MEMBER_MISMATCH",
      apply: (value) => { value.targets[1].observation.members[0].member_id = "priority.wrong"; } },
    { mutant_id: "wire-mismatch", expected_code: "ENUM_PARITY_WIRE_MISMATCH",
      apply: (value) => { value.targets[1].observation.members[0].emitted_wire = "wrong"; } },
    { mutant_id: "parse-mismatch", expected_code: "ENUM_PARITY_PARSE_MISMATCH",
      apply: (value) => { value.targets[1].observation.members[0].parsed_member_id = "priority.wrong"; } },
    { mutant_id: "unknown-outcome", expected_code: "ENUM_PARITY_UNKNOWN_WIRE_MISMATCH",
      apply: (value) => { value.targets[1].observation.unknown_wire.outcome = "member"; } },
  ];
  const killed = mutations.map((mutation) => {
    const changed = clone(upstream) as any;
    const composition = changed[ENUM_COMPOSITION_NODE.node_id].semantic_output;
    mutation.apply(composition, changed);
    resealComposition(composition);
    try {
      evaluateEnumParity(changed);
    } catch (error) {
      if ((error as { code?: string }).code === mutation.expected_code) {
        return Object.freeze({
          mutant_id: mutation.mutant_id,
          expected_code: mutation.expected_code,
          status: "killed" as const,
        });
      }
      throw error;
    }
    return fail("ENUM_PARITY_MUTANT_SURVIVED", mutation.mutant_id);
  });
  return Object.freeze({ parity, mutants: Object.freeze(killed) });
};
