import { describe, expect, it } from "vitest";

import {
  bindingSelectorForCase,
  derivePureCases,
  digestSfolValue,
  fixtureDigest,
  toPureInvocation,
  type DerivedPureCase,
  type PureFixture,
} from "../cases/index.js";
import { buildClauseDenominator } from "../denominator/index.js";
import {
  decodeLogicBindingRegistry,
  resolvePureBinding,
  SFOL_BINDING_SCHEMA_VERSION,
  type ResolvedPureBinding,
} from "../bindings/index.js";
import { integerValue, type SemanticValue } from "../evaluator/index.js";
import type {
  LogicClause,
  LogicTerm,
  NodeLogicModuleV1,
} from "../language/ast.js";
import {
  type TypedLogicModule,
  typecheckLogicModule,
} from "../language/typecheck.js";
import {
  buildPureProofReceipt,
  evaluatePureObservation,
  replayPureProofReceipt,
  type PureEvaluation,
  type PureProofBuildInput,
  type PureProofReceipt,
} from "./index.js";
import {
  runPureCase,
  type PureTargetHandle,
  type PureTargetResolver,
  type RawPureObservation,
} from "../runners/pure/index.js";
import {
  derivePureFixtures,
  EXHAUSTIVE_FINITE_RULESET,
} from "../partitions/index.js";

const A = "a".repeat(64);
const B = "b".repeat(64);
const C = "c".repeat(64);
const D = "d".repeat(64);
const E = "e".repeat(64);
const F = "f".repeat(64);
const TOOL_DIGEST = "9".repeat(64);
const SOURCE_ID = "framework.Increment";
const intSort = { tag: "primitive", name: "integer" } as const;

function span(path: string) {
  return {
    source_id: SOURCE_ID,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 10 },
  };
}

function literal(value: string, path: string): LogicTerm {
  return {
    tag: "literal",
    value: { tag: "integer", value },
    span: span(path),
  };
}

function moduleFixture(
  status: LogicClause["status"] = "admitted",
): NodeLogicModuleV1 {
  const clause: LogicClause = {
    clause_id: "framework.increment",
    kind: "function",
    status,
    inputs: [
      {
        name: "x",
        sort: intSort,
        span: span("body.logic.clauses.increment.inputs.x"),
      },
    ],
    result_sort: intSort,
    expression: {
      tag: "arithmetic",
      operator: "add",
      left: {
        tag: "variable",
        name: "x",
        span: span("body.logic.clauses.increment.expression.x"),
      },
      right: literal(
        "1",
        "body.logic.clauses.increment.expression.one",
      ),
      span: span("body.logic.clauses.increment.expression"),
    },
    observation_sort: null,
    span: span("body.logic.clauses.increment"),
  };
  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "framework.increment-module",
    source: {
      feature_id: "framework",
      node_id: SOURCE_ID,
      source_id: SOURCE_ID,
      source_path: "nodes/increment.yaml",
    },
    declarations: [],
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
    throw new Error("missing framework clause");
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
        required_roles: ["return"],
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

function fixture(
  coverageKey: string,
  fixtureId = "fixture-001",
  x = "2",
): PureFixture {
  const unsigned = {
    fixture_id: fixtureId,
    coverage_key: coverageKey,
    inputs: { x: integerValue(x) },
    universes: {},
  };
  return { ...unsigned, fixture_digest: fixtureDigest(unsigned) };
}

function bindingFor(derived: DerivedPureCase) {
  return {
    binding_id: "framework.increment-binding",
    selector: bindingSelectorForCase(derived),
    target: {
      adapter_kind: "pure-function",
      module: "@framework/domain",
      symbol: "increment",
      target_digest: A,
      runtime_digest: B,
    },
    argument_map: [{ parameter: "x", input_name: "x" }],
    observation_map: { kind: "return" },
  };
}

function resolvedBinding(derived: DerivedPureCase): ResolvedPureBinding {
  const decoded = decodeLogicBindingRegistry({
    schema_version: SFOL_BINDING_SCHEMA_VERSION,
    registry_id: "framework.registry",
    bindings: [bindingFor(derived)],
  });
  if (!decoded.ok) {
    throw new Error(JSON.stringify(decoded.diagnostics));
  }
  const resolved = resolvePureBinding(
    {
      selector: bindingSelectorForCase(derived),
      adapter_kind: "pure-function",
    },
    decoded.value,
  );
  if (!resolved.ok) {
    throw new Error(JSON.stringify(resolved.diagnostics));
  }
  return resolved.value;
}

function incrementHandle(
  delta = 1n,
  targetDigest = A,
  runtimeDigest = B,
): PureTargetHandle {
  return {
    target_digest: targetDigest,
    runtime_digest: runtimeDigest,
    invoke: (...arguments_: SemanticValue[]) => {
      const value = arguments_[0];
      if (value?.tag !== "integer") {
        throw new Error("integer input required");
      }
      return integerValue((BigInt(value.value) + delta).toString());
    },
  };
}

function targetResolver(handle: PureTargetHandle): PureTargetResolver {
  return {
    resolve(module, symbol) {
      return module === "@framework/domain" && symbol === "increment"
        ? handle
        : null;
    },
  };
}

interface VerticalFixture {
  readonly typed: TypedLogicModule;
  readonly derived: DerivedPureCase;
  readonly binding: ResolvedPureBinding;
  readonly observation: RawPureObservation;
  readonly evaluation: PureEvaluation;
  readonly proofInput: PureProofBuildInput;
  readonly receipt: PureProofReceipt;
}

function verticalFixture(handle = incrementHandle()): VerticalFixture {
  const typed = typedFixture();
  const { denominator, moduleDigest, clauseDigest } =
    denominatorFixture(typed);
  const coverageKey = denominator.coverage_keys[0];
  if (coverageKey === undefined) {
    throw new Error("missing denominator member");
  }
  const partitioned = derivePureFixtures({
    typed,
    typed_module_digest: moduleDigest,
    typed_clause_digests: { "framework.increment": clauseDigest },
    denominator,
    ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: 1 },
    domain: { inputs: { x: [integerValue("2")] } },
  });
  if (!partitioned.ok) throw new Error(JSON.stringify(partitioned.diagnostics));
  const derivedResult = derivePureCases({
    typed,
    typed_module_digest: moduleDigest,
    typed_clause_digests: {
      "framework.increment": clauseDigest,
    },
    denominator,
    fixtures: partitioned.value,
  });
  if (!derivedResult.ok || derivedResult.value[0] === undefined) {
    throw new Error(JSON.stringify(derivedResult));
  }
  const derived = derivedResult.value[0];
  const binding = resolvedBinding(derived);
  const observation = runPureCase(
    toPureInvocation(derived),
    binding,
    targetResolver(handle),
  );
  const evaluation = evaluatePureObservation(
    typed,
    derived,
    binding,
    observation,
  );
  const proofInput: PureProofBuildInput = {
    denominator,
    typed_artifact_digest: digestSfolValue(typed),
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
    tool_digest: TOOL_DIGEST,
  };
  const proof = buildPureProofReceipt(proofInput);
  if (!proof.ok) {
    throw new Error(JSON.stringify(proof.diagnostics));
  }
  return {
    typed,
    derived,
    binding,
    observation,
    evaluation,
    proofInput,
    receipt: proof.value,
  };
}

function allowlist(fixture_: VerticalFixture) {
  return {
    receipt_digest: fixture_.receipt.receipt_digest,
    denominator_digest: fixture_.proofInput.denominator.digest,
    typed_artifact_digest: fixture_.proofInput.typed_artifact_digest,
    tool_digest: TOOL_DIGEST,
  };
}

function mutationEvaluation(
  evaluation: PureEvaluation,
  patch: Partial<Omit<PureEvaluation, "evaluation_digest">>,
): PureEvaluation {
  const { evaluation_digest: _digest, ...unsigned } = evaluation;
  const changed = { ...unsigned, ...patch };
  return {
    ...changed,
    evaluation_digest: digestSfolValue(changed),
  };
}

function mutationObservation(
  observation: RawPureObservation,
  patch: Readonly<Record<string, unknown>>,
): RawPureObservation {
  const { observation_digest: _digest, ...unsigned } = observation;
  const changed = { ...unsigned, ...patch };
  return {
    ...changed,
    observation_digest: digestSfolValue(changed),
  } as RawPureObservation;
}

describe("DS-SFOL pure proof vertical", () => {
  it("reaches all eight exact stage sets and replays from an allowlist", () => {
    const vertical = verticalFixture();

    expect(vertical.observation.status).toBe("returned");
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
      replayPureProofReceipt(
        vertical.receipt,
        vertical.proofInput,
        allowlist(vertical),
      ),
    ).toMatchObject({ ok: true, value: { status: "pass" } });
  });

  it("keeps expected values out of the runner and binding contracts", () => {
    const vertical = verticalFixture();
    const invocation = toPureInvocation(vertical.derived);

    expect(Object.keys(invocation)).not.toContain("expected_digest");
    expect(JSON.stringify(invocation)).not.toMatch(
      /expected|predicate|oracle|acceptance/i,
    );
    expect(JSON.stringify(vertical.binding.binding)).not.toMatch(
      /expected|predicate|oracle|acceptance/i,
    );
  });

  it("uses independent denominator admission for a candidate source clause", () => {
    const typed = typedFixture("candidate");
    const { denominator, moduleDigest, clauseDigest } =
      denominatorFixture(typed);
    const coverageKey = denominator.coverage_keys[0];
    if (coverageKey === undefined) {
      throw new Error("missing candidate denominator coverage");
    }
    expect(
      derivePureCases({
        typed,
        typed_module_digest: moduleDigest,
        typed_clause_digests: {
          "framework.increment": clauseDigest,
        },
        denominator,
        fixtures: [fixture(coverageKey)],
      }),
    ).toMatchObject({
      ok: true,
      value: [{ clause_id: "framework.increment", status: "ready" }],
    });
  });

  it("rejects missing, extra, duplicate, and stale fixture/case membership", () => {
    const typed = typedFixture();
    const { denominator, moduleDigest, clauseDigest } =
      denominatorFixture(typed);
    const coverageKey = denominator.coverage_keys[0];
    if (coverageKey === undefined) {
      throw new Error("missing denominator coverage");
    }
    const base = {
      typed,
      typed_module_digest: moduleDigest,
      typed_clause_digests: {
        "framework.increment": clauseDigest,
      },
      denominator,
    };
    expect(derivePureCases({ ...base, fixtures: [] })).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_CASE_EMPTY" }],
    });
    expect(
      derivePureCases({
        ...base,
        fixtures: [
          fixture(coverageKey),
          fixture("framework.extra#return", "fixture-extra"),
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_CASE_DENOMINATOR_MISMATCH" }],
    });
    expect(
      derivePureCases({
        ...base,
        fixtures: [
          fixture(coverageKey),
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
    expect(
      derivePureCases({
        ...base,
        fixtures: [
          {
            ...fixture(coverageKey),
            fixture_digest: "0".repeat(64),
          },
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_CASE_FIXTURE_DIGEST_MISMATCH" }],
    });
  });

  it("turns target drift, wrong behavior, throws, and invalid raw values into residue", () => {
    const good = verticalFixture();
    const staleObservation = runPureCase(
      toPureInvocation(good.derived),
      good.binding,
      targetResolver(incrementHandle(1n, C, B)),
    );
    expect(staleObservation).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_RUN_TARGET_STALE" },
    });

    const throwing = runPureCase(
      toPureInvocation(good.derived),
      good.binding,
      targetResolver({
        target_digest: A,
        runtime_digest: B,
        invoke: () => {
          throw new Error("boom");
        },
      }),
    );
    expect(throwing).toMatchObject({
      status: "threw",
      raw_error: { message: "boom" },
    });

    const invalid = runPureCase(
      toPureInvocation(good.derived),
      good.binding,
      targetResolver({
        target_digest: A,
        runtime_digest: B,
        invoke: () => undefined,
      }),
    );
    expect(invalid).toMatchObject({
      status: "indeterminate",
      diagnostic: { code: "SFOL_RUN_RAW_VALUE_INVALID" },
    });
  });

  it("rejects missing, extra, duplicate, skipped, todo, stale, and indeterminate proof stages", () => {
    const vertical = verticalFixture();
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        upstream_case_sets: {
          ...vertical.proofInput.upstream_case_sets,
          C_projected: [],
        },
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_SET_MISMATCH" }],
    });
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        observations: [],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_SET_MISMATCH" }],
    });
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        observations: [
          vertical.observation,
          mutationObservation(vertical.observation, {
            case_id: "framework.extra#return@fixture-extra",
          }),
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_SET_MISMATCH" }],
    });
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        observations: [vertical.observation, vertical.observation],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_DUPLICATE_ID" }],
    });

    for (const status of ["skipped", "todo"] as const) {
      const changed = {
        ...vertical.derived,
        status,
      } as unknown as DerivedPureCase;
      expect(
        buildPureProofReceipt({
          ...vertical.proofInput,
          cases: [changed],
        }),
      ).toMatchObject({
        ok: false,
        diagnostics: [{ code: "SFOL_PROOF_NONPASS_STATE" }],
      });
    }
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        cases: [
          {
            ...vertical.derived,
            expected_digest: "0".repeat(64),
          },
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_CASE_STALE" }],
    });
    expect(
      buildPureProofReceipt({
        ...vertical.proofInput,
        evaluations: [
          mutationEvaluation(vertical.evaluation, {
            status: "indeterminate",
            detail: "forced residue",
          }),
        ],
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_NONPASS_STATE" }],
    });
  });

  it("rejects wrong target behavior before a proof receipt can exist", () => {
    const typed = typedFixture();
    const { denominator, moduleDigest, clauseDigest } =
      denominatorFixture(typed);
    const coverageKey = denominator.coverage_keys[0];
    if (coverageKey === undefined) {
      throw new Error("missing denominator coverage");
    }
    const cases = derivePureCases({
      typed,
      typed_module_digest: moduleDigest,
      typed_clause_digests: {
        "framework.increment": clauseDigest,
      },
      denominator,
      fixtures: [fixture(coverageKey)],
    });
    if (!cases.ok || cases.value[0] === undefined) {
      throw new Error(JSON.stringify(cases));
    }
    const derived = cases.value[0];
    const binding = resolvedBinding(derived);
    const observation = runPureCase(
      toPureInvocation(derived),
      binding,
      targetResolver(incrementHandle(2n)),
    );
    const evaluation = evaluatePureObservation(
      typed,
      derived,
      binding,
      observation,
    );

    expect(evaluation.status).toBe("fail");
    expect(
      buildPureProofReceipt({
        denominator,
        typed_artifact_digest: digestSfolValue(typed),
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
        tool_digest: TOOL_DIGEST,
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PROOF_NONPASS_STATE" }],
    });
  });

  it("rejects non-allowlisted and post-receipt artifact mutations", () => {
    const vertical = verticalFixture();
    expect(
      replayPureProofReceipt(vertical.receipt, vertical.proofInput, {
        ...allowlist(vertical),
        receipt_digest: "0".repeat(64),
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_REPLAY_NOT_ALLOWLISTED" }],
    });

    const mutatedEvaluation = mutationEvaluation(vertical.evaluation, {
      detail: "same pass, mutated evidence bytes",
    });
    expect(
      replayPureProofReceipt(
        vertical.receipt,
        {
          ...vertical.proofInput,
          evaluations: [mutatedEvaluation],
        },
        allowlist(vertical),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_REPLAY_ARTIFACT_MUTATED" }],
    });
  });

  it("is byte-stable across identical derivation, run, proof, and replay", () => {
    const left = verticalFixture();
    const right = verticalFixture();

    expect(JSON.stringify(left.derived)).toBe(JSON.stringify(right.derived));
    expect(JSON.stringify(left.observation)).toBe(
      JSON.stringify(right.observation),
    );
    expect(left.receipt.receipt_digest).toBe(
      right.receipt.receipt_digest,
    );
    expect(
      replayPureProofReceipt(left.receipt, left.proofInput, allowlist(left)),
    ).toEqual(
      replayPureProofReceipt(
        right.receipt,
        right.proofInput,
        allowlist(right),
      ),
    );
  });
});
