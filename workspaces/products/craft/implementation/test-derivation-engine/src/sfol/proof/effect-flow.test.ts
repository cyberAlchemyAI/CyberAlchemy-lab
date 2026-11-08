import { describe, expect, it } from "vitest";

import {
  deriveEffectCases,
  effectContractAdmissionDigest,
  effectFixtureDigest,
  runDerivedEffectCase,
  type DerivedEffectCase,
  type EffectCaseDerivationInput,
  type EffectContractAdmission,
  type EffectFixture,
  type RawEffectObservation,
} from "../cases/effect.js";
import { digestSfolValue } from "../cases/index.js";
import { buildClauseDenominator } from "../denominator/index.js";
import {
  effectBindingSelectorForCase,
  resolveEffectBinding,
  type EffectBindingRegistry,
  type ResolvedEffectBinding,
} from "../bindings/effect.js";
import {
  integerValue,
  type SemanticValue,
} from "../evaluator/index.js";
import type {
  LogicClause,
  LogicDeclaration,
  LogicTerm,
  NodeLogicModuleV1,
} from "../language/ast.js";
import {
  type TypedLogicModule,
  typecheckLogicModule,
} from "../language/typecheck.js";
import {
  EFFECT_TRACE_CONTRACT_VERSION,
  EFFECT_TRACE_VERSION,
  validateEffectTrace,
  type EffectTraceContract,
} from "../runners/effect/contracts.js";
import {
  EFFECT_HARNESS_ADAPTER_VERSION,
  type EffectHarnessAdapter,
} from "../runners/effect/harness.js";
import {
  buildEffectProofReceipt,
  evaluateEffectObservation,
  replayEffectProofReceipt,
  type EffectCaseEvaluation,
  type EffectProofBuildInput,
  type EffectProofReceipt,
} from "./effect.js";

const A = "a".repeat(64);
const B = "b".repeat(64);
const C = "c".repeat(64);
const D = "d".repeat(64);
const E = "e".repeat(64);
const F = "f".repeat(64);
const SOURCE_PROPOSAL_DIGEST = "8".repeat(64);
const TOOL_DIGEST = "9".repeat(64);
const SOURCE_ID = "framework.IncrementEffect";
const CLAUSE_ID = "framework.increment-effect";
const intSort = { tag: "primitive", name: "integer" } as const;
const stringSort = { tag: "primitive", name: "string" } as const;
const boolSort = { tag: "primitive", name: "boolean" } as const;
const stateSort = {
  tag: "named",
  declaration_id: "framework.State",
} as const;
const effectSort = {
  tag: "named",
  declaration_id: "framework.Effect",
} as const;

function span(path: string) {
  return {
    source_id: SOURCE_ID,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 10 },
  };
}

function literal(
  tag: "integer" | "string",
  value: string,
  path: string,
): LogicTerm {
  return {
    tag: "literal",
    value: { tag, value },
    span: span(path),
  };
}

function variable(name: string, path: string): LogicTerm {
  return { tag: "variable", name, span: span(path) };
}

function field(
  target: LogicTerm,
  name: string,
  path: string,
): LogicTerm {
  return { tag: "field", target, field: name, span: span(path) };
}

function effectRecord(
  sequence: number,
  kind: string,
  name: string,
  payload: string,
): LogicTerm {
  const root = `body.logic.effects.${sequence}`;
  return {
    tag: "record",
    declaration_id: "framework.Effect",
    fields: [
      {
        name: "sequence",
        value: literal("integer", sequence.toString(), `${root}.sequence`),
      },
      {
        name: "kind",
        value: literal("string", kind, `${root}.kind`),
      },
      {
        name: "name",
        value: literal("string", name, `${root}.name`),
      },
      {
        name: "payload",
        value: literal("string", payload, `${root}.payload`),
      },
    ],
    span: span(root),
  };
}

function moduleFixture(
  status: LogicClause["status"] = "admitted",
): NodeLogicModuleV1 {
  const declarations: readonly LogicDeclaration[] = [
    {
      tag: "record",
      declaration_id: "framework.State",
      fields: [
        {
          name: "balance",
          sort: intSort,
          required: true,
          span: span("body.logic.declarations.state.balance"),
        },
      ],
      span: span("body.logic.declarations.state"),
    },
    {
      tag: "record",
      declaration_id: "framework.Effect",
      fields: [
        {
          name: "sequence",
          sort: intSort,
          required: true,
          span: span("body.logic.declarations.effect.sequence"),
        },
        {
          name: "kind",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.kind"),
        },
        {
          name: "name",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.name"),
        },
        {
          name: "payload",
          sort: stringSort,
          required: true,
          span: span("body.logic.declarations.effect.payload"),
        },
      ],
      span: span("body.logic.declarations.effect"),
    },
  ];
  const effectsSort = {
    tag: "list",
    element: effectSort,
  } as const;
  const clause: LogicClause = {
    clause_id: CLAUSE_ID,
    kind: "effect-relation",
    status,
    inputs: [
      { name: "pre", sort: stateSort, span: span("body.logic.inputs.pre") },
      {
        name: "post",
        sort: stateSort,
        span: span("body.logic.inputs.post"),
      },
      {
        name: "effects",
        sort: effectsSort,
        span: span("body.logic.inputs.effects"),
      },
    ],
    result_sort: boolSort,
    expression: {
      tag: "boolean",
      operator: "and",
      operands: [
        {
          tag: "comparison",
          operator: "eq",
          left: field(
            variable("post", "body.logic.relation.post"),
            "balance",
            "body.logic.relation.post.balance",
          ),
          right: {
            tag: "arithmetic",
            operator: "add",
            left: field(
              variable("pre", "body.logic.relation.pre"),
              "balance",
              "body.logic.relation.pre.balance",
            ),
            right: literal(
              "integer",
              "1",
              "body.logic.relation.one",
            ),
            span: span("body.logic.relation.increment"),
          },
          span: span("body.logic.relation.state"),
        },
        {
          tag: "comparison",
          operator: "eq",
          left: variable(
            "effects",
            "body.logic.relation.effects",
          ),
          right: {
            tag: "list",
            items: [
              effectRecord(0, "call", "authorize", "ok"),
              effectRecord(1, "write", "balance", "1"),
              effectRecord(2, "event", "incremented", "1"),
              effectRecord(3, "error", "none", "none"),
            ],
            span: span("body.logic.relation.effect-list"),
          },
          span: span("body.logic.relation.effect-order"),
        },
      ],
      span: span("body.logic.relation"),
    },
    observation_sort: effectsSort,
    span: span("body.logic.clauses.increment-effect"),
  };
  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "framework.increment-effect-module",
    source: {
      feature_id: "framework",
      node_id: SOURCE_ID,
      source_id: SOURCE_ID,
      source_path: "nodes/increment-effect.yaml",
    },
    declarations,
    clauses: [clause],
  };
}

function typedFixture(
  status: LogicClause["status"] = "admitted",
): TypedLogicModule {
  const result = typecheckLogicModule(moduleFixture(status));
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

function denominatorFixture(typed: TypedLogicModule) {
  const clause = typed.source.clauses[0];
  if (clause === undefined) {
    throw new Error("missing framework effect clause");
  }
  const moduleDigest = digestSfolValue(typed.source);
  const clauseDigest = digestSfolValue(clause);
  const proofContext = {
    graph_id: "framework.graph",
    graph_digest: A,
    manifest_id: "framework.manifest",
    manifest_digest: B,
    build_id: "framework.build",
    build_digest: C,
    source_set_digest: D,
    profile_id: "framework.profile",
    profile_version: "1.0.0",
    profile_digest: E,
  };
  const denominator = buildClauseDenominator({
    schema_version: "domainspec-sfol-clause-admission-manifest/v1",
    source_form: "canonical-node-graph-manifest-build",
    unsupported_residue_policy: "reject",
    proof_context: proofContext,
    clause_membership: [clause.clause_id],
    clauses: [
      {
        clause_id: clause.clause_id,
        clause_digest: clauseDigest,
        node_id: SOURCE_ID,
        node_digest: F,
        module_id: typed.source.module_id,
        module_digest: moduleDigest,
        kind: clause.kind,
        required_roles: ["effects"],
        status: "admitted",
        proof_context: {
          graph_digest: proofContext.graph_digest,
          manifest_digest: proofContext.manifest_digest,
          build_digest: proofContext.build_digest,
          source_set_digest: proofContext.source_set_digest,
          profile_id: proofContext.profile_id,
          profile_version: proofContext.profile_version,
          profile_digest: proofContext.profile_digest,
        },
      },
    ],
  });
  return { denominator, moduleDigest, clauseDigest };
}

function contractFixture(): EffectTraceContract {
  return {
    schema_version: EFFECT_TRACE_CONTRACT_VERSION,
    contract_id: "framework.increment-effect-contract",
    pre_record_declaration_id: "framework.State",
    post_record_declaration_id: "framework.State",
    effect_record_declaration_id: "framework.Effect",
    pre_fields: [{ name: "balance", value_tag: "integer" }],
    post_fields: [{ name: "balance", value_tag: "integer" }],
    effect_sequence: [
      { kind: "call", name: "authorize", payload_tag: "string" },
      { kind: "write", name: "balance", payload_tag: "string" },
      { kind: "event", name: "incremented", payload_tag: "string" },
      { kind: "error", name: "none", payload_tag: "string" },
    ],
    return_observation: null,
    max_effects: 4,
  };
}

function admissionFixture(
  proofContext: ReturnType<typeof denominatorFixture>["denominator"]["proof_context"],
  contract = contractFixture(),
  sourceProposalDigest = SOURCE_PROPOSAL_DIGEST,
): EffectContractAdmission {
  const unsigned = {
    schema_version:
      "domainspec-sfol-effect-contract-admission/v1" as const,
    admission_id: "framework.effect-contract-admission",
    proof_context: proofContext,
    source_proposal_digest: sourceProposalDigest,
    contract_bindings: [
      {
        contract_id: contract.contract_id,
        contract_digest: digestSfolValue(contract),
        source_proposal_digest: sourceProposalDigest,
      },
    ],
  };
  return {
    ...unsigned,
    admission_digest: effectContractAdmissionDigest(unsigned),
  };
}

function fixture(
  coverageKey: string,
  fixtureId = "fixture-001",
  contractId = contractFixture().contract_id,
): EffectFixture {
  const unsigned = {
    fixture_id: fixtureId,
    coverage_key: coverageKey,
    contract_id: contractId,
    inputs: {},
    universes: {},
  };
  return {
    ...unsigned,
    fixture_digest: effectFixtureDigest(unsigned),
  };
}

function derivationFixture(
  status: LogicClause["status"] = "admitted",
): EffectCaseDerivationInput {
  const typed = typedFixture(status);
  const { denominator, moduleDigest, clauseDigest } =
    denominatorFixture(typed);
  const coverageKey = denominator.coverage_keys[0];
  if (coverageKey === undefined) {
    throw new Error("missing effect denominator coverage");
  }
  const contract = contractFixture();
  return {
    typed,
    typed_module_digest: moduleDigest,
    typed_clause_digests: { [CLAUSE_ID]: clauseDigest },
    denominator,
    fixtures: [fixture(coverageKey)],
    contracts: [contract],
    contract_admission: admissionFixture(
      denominator.proof_context,
      contract,
    ),
    source_proposal_digest: SOURCE_PROPOSAL_DIGEST,
  };
}

function derivedFixture(
  input = derivationFixture(),
): DerivedEffectCase {
  const result = deriveEffectCases(input);
  if (!result.ok || result.value[0] === undefined) {
    throw new Error(JSON.stringify(result));
  }
  return result.value[0];
}

function registryFor(
  derived: DerivedEffectCase,
): EffectBindingRegistry {
  return {
    schema_version: "domainspec-sfol-effect-binding/v1",
    registry_id: "framework.effect-bindings",
    bindings: [
      {
        binding_id: "framework.increment-effect-binding",
        selector: effectBindingSelectorForCase(derived),
        target: {
          adapter_kind: "effect-harness",
          module: "@framework/domain",
          symbol: "incrementEffect",
          target_digest: A,
          runtime_digest: B,
          adapter_id: "framework.increment-effect-adapter",
          adapter_digest: C,
        },
      },
    ],
  };
}

function resolvedBinding(
  derived: DerivedEffectCase,
  registry = registryFor(derived),
): ResolvedEffectBinding {
  const result = resolveEffectBinding(
    {
      selector: effectBindingSelectorForCase(derived),
      adapter_kind: "effect-harness",
    },
    registry,
  );
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

interface CounterResource {
  balance: string;
}

function adapterFixture(
  changes: Partial<EffectHarnessAdapter<CounterResource>> = {},
): EffectHarnessAdapter<CounterResource> {
  return {
    schema_version: EFFECT_HARNESS_ADAPTER_VERSION,
    adapter_id: "framework.increment-effect-adapter",
    adapter_digest: C,
    contract_id: contractFixture().contract_id,
    async setup(runtime) {
      runtime.openResource("framework-counter");
      return { balance: "0" };
    },
    async capturePreState(resource) {
      return { balance: integerValue(resource.balance) };
    },
    async run(resource, runtime) {
      runtime.recordEffect(
        "call",
        "authorize",
        stringValue("ok"),
      );
      resource.balance = "1";
      runtime.recordEffect(
        "write",
        "balance",
        stringValue("1"),
      );
      runtime.recordEffect(
        "event",
        "incremented",
        stringValue("1"),
      );
      runtime.recordEffect(
        "error",
        "none",
        stringValue("none"),
      );
      return null;
    },
    async capturePostState(resource) {
      return { balance: integerValue(resource.balance) };
    },
    async teardown(_resource, runtime) {
      runtime.closeResource("framework-counter");
    },
    ...changes,
  };
}

interface VerticalFixture {
  readonly typed: TypedLogicModule;
  readonly derived: DerivedEffectCase;
  readonly binding: ResolvedEffectBinding;
  readonly observation: RawEffectObservation;
  readonly evaluation: EffectCaseEvaluation;
  readonly proofInput: EffectProofBuildInput;
  readonly receipt: EffectProofReceipt;
}

async function verticalFixture(): Promise<VerticalFixture> {
  const derivation = derivationFixture();
  const derived = derivedFixture(derivation);
  const binding = resolvedBinding(derived);
  const contract = contractFixture();
  const observation = await runDerivedEffectCase(
    derived,
    binding,
    contract,
    adapterFixture(),
    { timeout_ms: 50, max_open_resources: 1 },
  );
  const evaluation = evaluateEffectObservation(
    derivation.typed,
    derived,
    binding,
    observation,
    contract,
  );
  const proofInput: EffectProofBuildInput = {
    denominator: derivation.denominator,
    typed_artifact_digest: digestSfolValue(derivation.typed),
    upstream_case_sets: {
      C_spec: [derived.case_id],
      C_projected: [derived.case_id],
      C_validated: [derived.case_id],
      C_typed: [derived.case_id],
    },
    cases: [derived],
    bindings: [binding],
    observations: [observation],
    evaluations: [evaluation],
    trace_contracts: [contract],
    contract_admission: derivation.contract_admission,
    source_proposal_digest: SOURCE_PROPOSAL_DIGEST,
    tool_digest: TOOL_DIGEST,
  };
  const proof = buildEffectProofReceipt(proofInput);
  if (!proof.ok) {
    throw new Error(JSON.stringify(proof.diagnostics));
  }
  return {
    typed: derivation.typed,
    derived,
    binding,
    observation,
    evaluation,
    proofInput,
    receipt: proof.value,
  };
}

function allowlist(vertical: VerticalFixture) {
  return {
    receipt_digest: vertical.receipt.receipt_digest,
    denominator_digest: vertical.proofInput.denominator.digest,
    typed_artifact_digest:
      vertical.proofInput.typed_artifact_digest,
    contract_admission_digest:
      vertical.proofInput.contract_admission.admission_digest,
    source_proposal_digest: SOURCE_PROPOSAL_DIGEST,
    tool_digest: TOOL_DIGEST,
  };
}

function mutateObservation(
  observation: RawEffectObservation,
): RawEffectObservation {
  if (observation.trace === null) {
    throw new Error("missing raw trace");
  }
  const { trace_digest: _traceDigest, ...unsignedTrace } =
    observation.trace;
  const changedTraceUnsigned = {
    ...unsignedTrace,
    post_state: { balance: integerValue("2") },
  };
  const changedTrace = {
    ...changedTraceUnsigned,
    trace_digest: digestSfolValue(changedTraceUnsigned),
  };
  const { observation_digest: _digest, ...unsigned } = observation;
  const changed = { ...unsigned, trace: changedTrace };
  return {
    ...changed,
    observation_digest: digestSfolValue(changed),
  };
}

function stringValue(value: string): SemanticValue {
  return Object.freeze({ tag: "string", value });
}

describe("DS-SFOL generic effect proof vertical", () => {
  it("closes all eight exact stage sets and replays immutable raw evidence", async () => {
    const vertical = await verticalFixture();

    expect(vertical.observation.status).toBe("observed");
    expect(vertical.evaluation.status).toBe("pass");
    expect(vertical.receipt.stage_sets.map((set) => set.stage)).toEqual([
      "C_spec",
      "C_projected",
      "C_validated",
      "C_typed",
      "T_generated",
      "C_bound",
      "O_run",
      "R_evaluated",
    ]);
    expect(
      new Set(
        vertical.receipt.stage_sets.map((set) =>
          JSON.stringify(set.case_ids),
        ),
      ).size,
    ).toBe(1);
    expect(
      replayEffectProofReceipt(
        vertical.receipt,
        vertical.proofInput,
        allowlist(vertical),
      ),
    ).toMatchObject({ ok: true, value: { status: "pass" } });
  });

  it("uses independent denominator admission for a candidate source clause", () => {
    expect(deriveEffectCases(derivationFixture("candidate"))).toMatchObject({
      ok: true,
      value: [{ clause_id: CLAUSE_ID, status: "ready" }],
    });
  });

  it("rejects missing, extra, duplicate, and oracle-bearing fixtures", () => {
    const input = derivationFixture();
    const coverageKey = input.denominator.coverage_keys[0]!;

    expect(
      deriveEffectCases({ ...input, fixtures: [] }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_CASE_EMPTY" }],
    });
    expect(
      deriveEffectCases({
        ...input,
        fixtures: [
          input.fixtures[0]!,
          fixture("framework.extra#effects", "fixture-extra"),
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_CASE_DENOMINATOR_MISMATCH" },
      ],
    });
    expect(
      deriveEffectCases({
        ...input,
        fixtures: [
          input.fixtures[0]!,
          input.fixtures[0]!,
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_CASE_DUPLICATE_FIXTURE" },
      ],
    });
    expect(
      deriveEffectCases({
        ...input,
        fixtures: [
          input.fixtures[0]!,
          fixture(coverageKey, "fixture-002"),
        ],
      }),
    ).toMatchObject({
      ok: true,
      value: [
        { fixture_id: "fixture-001" },
        { fixture_id: "fixture-002" },
      ],
    });
    const oracleFixture = {
      ...fixture(coverageKey),
      expected_trace: [],
    } as unknown as EffectFixture;
    expect(
      deriveEffectCases({ ...input, fixtures: [oracleFixture] }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_CASE_ORACLE_FIELD" }],
    });
  });

  it("rejects unadmitted contracts and source/contract digest mismatches", () => {
    const input = derivationFixture();
    const admission = input.contract_admission;
    const unsignedUnadmitted = {
      schema_version: admission.schema_version,
      admission_id: admission.admission_id,
      proof_context: admission.proof_context,
      source_proposal_digest: admission.source_proposal_digest,
      contract_bindings: [],
    };
    expect(
      deriveEffectCases({
        ...input,
        contract_admission: {
          ...unsignedUnadmitted,
          admission_digest:
            effectContractAdmissionDigest(unsignedUnadmitted),
        },
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_CASE_CONTRACT_UNADMITTED" },
      ],
    });

    const staleBinding = {
      ...admission.contract_bindings[0]!,
      contract_digest: A,
    };
    const unsignedStale = {
      schema_version: admission.schema_version,
      admission_id: admission.admission_id,
      proof_context: admission.proof_context,
      source_proposal_digest: admission.source_proposal_digest,
      contract_bindings: [staleBinding],
    };
    expect(
      deriveEffectCases({
        ...input,
        contract_admission: {
          ...unsignedStale,
          admission_digest:
            effectContractAdmissionDigest(unsignedStale),
        },
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_CASE_CONTRACT_STALE" }],
    });

    expect(
      deriveEffectCases({
        ...input,
        source_proposal_digest: A,
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_CASE_SOURCE_MISMATCH" }],
    });
  });

  it("rejects a denominator member with an unsupported execution role", () => {
    const input = derivationFixture();
    const member = input.denominator.members[0]!;
    const coverageKey = `${member.clause_id}#state`;
    const denominator = {
      ...input.denominator,
      coverage_keys: [coverageKey],
      members: [
        {
          ...member,
          coverage_key: coverageKey,
          role: "state" as const,
        },
      ],
    };
    expect(
      deriveEffectCases({
        ...input,
        denominator,
        fixtures: [fixture(coverageKey)],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_CASE_ROLE_UNSUPPORTED" },
      ],
    });
  });

  it("rejects stale bindings and adapter implementation mutation", async () => {
    const input = derivationFixture();
    const derived = derivedFixture(input);
    const registry = registryFor(derived);
    const stale = {
      ...registry.bindings[0]!,
      selector: {
        ...registry.bindings[0]!.selector,
        trace_contract_digest: A,
      },
    };
    expect(
      resolveEffectBinding(
        {
          selector: effectBindingSelectorForCase(derived),
          adapter_kind: "effect-harness",
        },
        { ...registry, bindings: [stale] },
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_BINDING_STALE" }],
    });

    const binding = resolvedBinding(derived);
    const observation = await runDerivedEffectCase(
      derived,
      binding,
      contractFixture(),
      adapterFixture({ adapter_digest: D }),
      { timeout_ms: 50, max_open_resources: 1 },
    );
    expect(observation).toMatchObject({
      status: "indeterminate",
      diagnostics: [{ code: "SFOL_HARNESS_ADAPTER_INVALID" }],
    });
  });

  it("rejects wrong trace order and semantic payload type", () => {
    const contract = contractFixture();
    const trace = {
      schema_version: EFFECT_TRACE_VERSION,
      trace_id: "framework.trace",
      contract_id: contract.contract_id,
      pre_state: { balance: integerValue("0") },
      post_state: { balance: integerValue("1") },
      effects: [
        {
          sequence: 0,
          kind: "write",
          name: "balance",
          payload: stringValue("1"),
        },
        {
          sequence: 1,
          kind: "call",
          name: "authorize",
          payload: stringValue("ok"),
        },
        {
          sequence: 2,
          kind: "event",
          name: "incremented",
          payload: stringValue("1"),
        },
        {
          sequence: 3,
          kind: "error",
          name: "none",
          payload: stringValue("none"),
        },
      ],
      return_value: null,
    };
    expect(validateEffectTrace(contract, trace)).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_ORDER_MISMATCH" }],
    });
    const wrongType = {
      ...trace,
      effects: [
        {
          sequence: 0,
          kind: "call",
          name: "authorize",
          payload: integerValue("1"),
        },
        ...trace.effects.slice(1),
      ],
    };
    expect(validateEffectTrace(contract, wrongType)).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_WRONG_TYPE" }],
    });
  });

  it("fails a partial stage set and replayed observation/tool mutation", async () => {
    const vertical = await verticalFixture();
    expect(
      buildEffectProofReceipt({
        ...vertical.proofInput,
        upstream_case_sets: {
          ...vertical.proofInput.upstream_case_sets,
          C_projected: [],
        },
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_EFFECT_PROOF_SET_MISMATCH" }],
    });

    expect(
      replayEffectProofReceipt(
        vertical.receipt,
        {
          ...vertical.proofInput,
          observations: [
            mutateObservation(vertical.observation),
          ],
        },
        allowlist(vertical),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_REPLAY_REBUILD_FAILED" },
      ],
    });
    expect(
      replayEffectProofReceipt(
        vertical.receipt,
        {
          ...vertical.proofInput,
          tool_digest: A,
        },
        allowlist(vertical),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        { code: "SFOL_EFFECT_REPLAY_ARTIFACT_MUTATED" },
      ],
    });
  });
});
