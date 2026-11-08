import { describe, expect, it } from "vitest";

import { digestSfolValue } from "../cases/index.js";
import { buildClauseDenominator } from "../denominator/index.js";
import type {
  LogicClause,
  LogicDeclaration,
  NodeLogicModuleV1,
  SourceSpan,
} from "../language/ast.js";
import { typecheckLogicModule } from "../language/typecheck.js";
import {
  derivePureFixtures,
  EXHAUSTIVE_FINITE_RULESET,
  MCDC_RULESET,
} from "./index.js";

const A = "a".repeat(64);
const B = "b".repeat(64);
const C = "c".repeat(64);
const D = "d".repeat(64);
const E = "e".repeat(64);
const F = "f".repeat(64);

function span(path: string): SourceSpan {
  return {
    source_id: "partition.fixture",
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 2 },
  };
}

function clauseFixture(clause: LogicClause, declarations: LogicDeclaration[] = []) {
  const source: NodeLogicModuleV1 = {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: `partition.${clause.clause_id}.module`,
    source: { feature_id: "partition", node_id: clause.clause_id, source_id: "partition.fixture", source_path: "partition.fixture.json" },
    declarations,
    clauses: [clause],
  };
  const typedResult = typecheckLogicModule(source);
  if (!typedResult.ok) throw new Error(JSON.stringify(typedResult));
  const typed = typedResult.value;
  const moduleDigest = digestSfolValue(typed.source);
  const clauseDigest = digestSfolValue(clause);
  const proofContext = { graph_id: "partition.graph", graph_digest: A, manifest_id: "partition.manifest", manifest_digest: B, build_id: "partition.build", build_digest: C, source_set_digest: D, profile_id: "partition.profile", profile_version: "1.0.0", profile_digest: E };
  const denominator = buildClauseDenominator({
    schema_version: "domainspec-sfol-clause-admission-manifest/v1",
    source_form: "canonical-node-graph-manifest-build",
    unsupported_residue_policy: "reject",
    proof_context: proofContext,
    clause_membership: [clause.clause_id],
    clauses: [{ clause_id: clause.clause_id, clause_digest: clauseDigest, node_id: clause.clause_id, node_digest: F, module_id: source.module_id, module_digest: moduleDigest, kind: clause.kind, required_roles: ["predicate"], status: "admitted", proof_context: { graph_digest: A, manifest_digest: B, build_digest: C, source_set_digest: D, profile_id: "partition.profile", profile_version: "1.0.0", profile_digest: E } }],
  });
  return { typed, moduleDigest, clauseDigest, denominator };
}

function fixture(inputCount = 3) {
  const inputs = Array.from({ length: inputCount }, (_, index) => ({
    name: `b${inputCount - index}`,
    sort: { tag: "primitive" as const, name: "boolean" as const },
    span: span(`inputs.${index}`),
  }));
  const clause: LogicClause = {
    clause_id: "partition.boolean-and",
    kind: "predicate",
    status: "admitted",
    inputs,
    result_sort: { tag: "primitive", name: "boolean" },
    expression:
      inputs.length === 0
        ? {
            tag: "literal",
            value: { tag: "boolean", value: true },
            span: span("expression.true"),
          }
        : {
            tag: "boolean",
            operator: "and",
            operands: inputs.map(({ name }, index) => ({
              tag: "variable" as const,
              name,
              span: span(`expression.${index}`),
            })),
            span: span("expression"),
          },
    observation_sort: null,
    span: span("clause"),
  };
  const source: NodeLogicModuleV1 = {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: "partition.module",
    source: {
      feature_id: "partition",
      node_id: "boolean-and",
      source_id: "partition.fixture",
      source_path: "partition.fixture.json",
    },
    declarations: [],
    clauses: [clause],
  };
  const typedResult = typecheckLogicModule(source);
  if (!typedResult.ok) throw new Error(JSON.stringify(typedResult));
  const typed = typedResult.value;
  const moduleDigest = digestSfolValue(typed.source);
  const clauseDigest = digestSfolValue(clause);
  const proofContext = {
    graph_id: "partition.graph",
    graph_digest: A,
    manifest_id: "partition.manifest",
    manifest_digest: B,
    build_id: "partition.build",
    build_digest: C,
    source_set_digest: D,
    profile_id: "partition.profile",
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
        node_id: "partition.BooleanAnd",
        node_digest: F,
        module_id: typed.source.module_id,
        module_digest: moduleDigest,
        kind: clause.kind,
        required_roles: ["predicate"],
        status: "admitted",
        proof_context: {
          graph_digest: A,
          manifest_digest: B,
          build_digest: C,
          source_set_digest: D,
          profile_id: "partition.profile",
          profile_version: "1.0.0",
          profile_digest: E,
        },
      },
    ],
  });
  return { typed, moduleDigest, clauseDigest, denominator };
}

function derive(inputCount: number, maxCases: number) {
  const value = fixture(inputCount);
  return derivePureFixtures({
    typed: value.typed,
    typed_module_digest: value.moduleDigest,
    typed_clause_digests: {
      "partition.boolean-and": value.clauseDigest,
    },
    denominator: value.denominator,
    ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: maxCases },
  });
}

describe("finite SFOL partition derivation", () => {
  it("derives all eight three-Boolean valuations in stable order", () => {
    const first = derive(3, 8);
    const second = derive(3, 8);
    expect(first).toEqual(second);
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    expect(first.value).toHaveLength(8);
    expect(
      new Set(first.value.map((entry) => digestSfolValue(entry.inputs))).size,
    ).toBe(8);
  });

  it("treats a zero-input clause as one valuation", () => {
    const result = derive(0, 1);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value).toHaveLength(1);
    expect(result.value[0]?.inputs).toEqual({});
  });

  it("fails closed when exhaustive expansion exceeds the declared budget", () => {
    expect(derive(3, 7)).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_PARTITION_BUDGET_EXCEEDED" }],
    });
  });

  it("selects a deterministic four-case MC/DC set for a three-input conjunction", () => {
    const value = fixture(3);
    const input = {
      typed: value.typed,
      typed_module_digest: value.moduleDigest,
      typed_clause_digests: { "partition.boolean-and": value.clauseDigest },
      denominator: value.denominator,
      ruleset: { ...MCDC_RULESET, max_cases: 4, max_analysis_cases: 8 },
    } as const;
    const first = derivePureFixtures(input);
    const second = derivePureFixtures(input);
    expect(first).toEqual(second);
    expect(first.ok).toBe(true);
    if (!first.ok) return;
    expect(first.value).toHaveLength(4);
    expect(first.analyzed_case_count).toBe(8);
    expect(first.derivation_mode).toBe("mcdc");
  });

  it("rejects duplicate or type-invalid explicit domain values", () => {
    const value = fixture(1);
    const common = {
      typed: value.typed,
      typed_module_digest: value.moduleDigest,
      typed_clause_digests: { "partition.boolean-and": value.clauseDigest },
      denominator: value.denominator,
      ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: 2 },
    } as const;
    expect(derivePureFixtures({ ...common, domain: { inputs: { b1: [{ tag: "boolean", value: true }, { tag: "boolean", value: true }] } } })).toMatchObject({ ok: false, diagnostics: [{ code: "SFOL_PARTITION_DOMAIN_DUPLICATE" }] });
    expect(derivePureFixtures({ ...common, domain: { inputs: { b1: [{ tag: "string", value: "true" }] } } })).toMatchObject({ ok: false, diagnostics: [{ code: "SFOL_PARTITION_DOMAIN_TYPE_MISMATCH" }] });
  });

  it("derives integer comparison boundaries without caller-authored cases", () => {
    const clause: LogicClause = {
      clause_id: "partition.integer-boundary", kind: "predicate", status: "admitted",
      inputs: [{ name: "x", sort: { tag: "primitive", name: "integer" }, span: span("inputs.x") }],
      result_sort: { tag: "primitive", name: "boolean" },
      expression: { tag: "comparison", operator: "gte", left: { tag: "variable", name: "x", span: span("expression.x") }, right: { tag: "literal", value: { tag: "integer", value: "0" }, span: span("expression.zero") }, span: span("expression") },
      observation_sort: null, span: span("clause"),
    };
    const value = clauseFixture(clause);
    const result = derivePureFixtures({ typed: value.typed, typed_module_digest: value.moduleDigest, typed_clause_digests: { [clause.clause_id]: value.clauseDigest }, denominator: value.denominator, ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: 3 } });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.map(({ inputs }) => inputs.x).sort((left, right) => left && right && left.tag === "integer" && right.tag === "integer" ? Number(left.value) - Number(right.value) : 0)).toEqual([{ tag: "integer", value: "-1" }, { tag: "integer", value: "0" }, { tag: "integer", value: "1" }]);
  });

  it("derives collection and finite-universe variants from declared domains", () => {
    const listClause: LogicClause = {
      clause_id: "partition.list-equality", kind: "predicate", status: "admitted",
      inputs: [{ name: "xs", sort: { tag: "list", element: { tag: "primitive", name: "integer" } }, span: span("inputs.xs") }],
      result_sort: { tag: "primitive", name: "boolean" },
      expression: { tag: "comparison", operator: "eq", left: { tag: "variable", name: "xs", span: span("expression.xs") }, right: { tag: "list", items: [{ tag: "literal", value: { tag: "integer", value: "1" }, span: span("expression.one") }], span: span("expression.singleton") }, span: span("expression") },
      observation_sort: null, span: span("clause"),
    };
    const list = clauseFixture(listClause);
    const listResult = derivePureFixtures({ typed: list.typed, typed_module_digest: list.moduleDigest, typed_clause_digests: { [listClause.clause_id]: list.clauseDigest }, denominator: list.denominator, ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: 5 }, domain: { collection_elements: { xs: [{ tag: "integer", value: "1" }, { tag: "integer", value: "2" }] } } });
    expect(listResult).toMatchObject({ ok: true, value: { length: 5 } });

    const universeId = "partition.integer-universe";
    const quantified: LogicClause = {
      clause_id: "partition.forall-positive", kind: "predicate", status: "admitted", inputs: [], result_sort: { tag: "primitive", name: "boolean" },
      expression: { tag: "quantifier", operator: "forall", universe_id: universeId, variable_name: "item", variable_sort: { tag: "primitive", name: "integer" }, predicate: { tag: "comparison", operator: "gt", left: { tag: "variable", name: "item", span: span("predicate.item") }, right: { tag: "literal", value: { tag: "integer", value: "0" }, span: span("predicate.zero") }, span: span("predicate") }, span: span("expression") },
      observation_sort: null, span: span("clause"),
    };
    const universe = clauseFixture(quantified, [{ tag: "fixture-universe", declaration_id: universeId, element_sort: { tag: "primitive", name: "integer" }, admits_empty: true, span: span("universe") }]);
    const universeResult = derivePureFixtures({ typed: universe.typed, typed_module_digest: universe.moduleDigest, typed_clause_digests: { [quantified.clause_id]: universe.clauseDigest }, denominator: universe.denominator, ruleset: { ...EXHAUSTIVE_FINITE_RULESET, max_cases: 2 }, domain: { universe_variants: { [universeId]: [[], [{ tag: "integer", value: "1" }]] } } });
    expect(universeResult).toMatchObject({ ok: true, value: { length: 2 } });
  });
});
