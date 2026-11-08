import { describe, expect, it } from "vitest";

import { digestSfolValue, fixtureDigest, type PureFixture } from "../cases/index.js";
import type { LogicClause, NodeLogicModuleV1, SourceSpan } from "../language/ast.js";
import { typecheckLogicModule } from "../language/typecheck.js";
import { deriveMutationAdequacy, SFOL_MUTATION_CATALOG_VERSION } from "./index.js";

function span(path: string): SourceSpan {
  return { source_id: "mutation.fixture", path, start: { line: 1, column: 1 }, end: { line: 1, column: 2 } };
}

function fixture(a: boolean, b: boolean): PureFixture {
  const unsigned = {
    fixture_id: `fixture-${Number(a)}${Number(b)}`,
    coverage_key: "mutation.and#predicate",
    inputs: { a: { tag: "boolean" as const, value: a }, b: { tag: "boolean" as const, value: b } },
    universes: {},
  };
  return { ...unsigned, fixture_digest: fixtureDigest(unsigned) };
}

describe("SFOL mutation adequacy", () => {
  it("kills conjunction and atom-negation mutants over the exhaustive domain", () => {
    const clause: LogicClause = {
      clause_id: "mutation.and",
      kind: "predicate",
      status: "admitted",
      inputs: ["a", "b"].map((name) => ({ name, sort: { tag: "primitive" as const, name: "boolean" as const }, span: span(`inputs.${name}`) })),
      result_sort: { tag: "primitive", name: "boolean" },
      expression: {
        tag: "boolean", operator: "and",
        operands: ["a", "b"].map((name) => ({ tag: "variable" as const, name, span: span(`expression.${name}`) })),
        span: span("expression"),
      },
      observation_sort: null,
      span: span("clause"),
    };
    const source: NodeLogicModuleV1 = {
      schema_version: "domainspec-node-logic/v1", language_version: "domainspec-sfol/v1",
      module_id: "mutation.module",
      source: { feature_id: "mutation", node_id: "and", source_id: "mutation.fixture", source_path: "mutation.fixture.json" },
      declarations: [], clauses: [clause],
    };
    const typed = typecheckLogicModule(source);
    expect(typed.ok).toBe(true);
    if (!typed.ok) return;
    const result = deriveMutationAdequacy({
      typed: typed.value,
      clause_id: clause.clause_id,
      fixtures: [fixture(false, false), fixture(false, true), fixture(true, false), fixture(true, true)],
      catalog_version: SFOL_MUTATION_CATALOG_VERSION,
      evaluation_domain: {
        kind: "exhaustive-finite",
        domain_digest: "a".repeat(64),
      },
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.mutant_count).toBe(3);
    expect(result.value.killed_count).toBe(3);
    expect(result.value.surviving_supported_count).toBe(0);
    expect(result.value.result).toBe("pass");
    const { receipt_digest: _receiptDigest, ...unsigned } = result.value;
    expect(result.value.receipt_digest).toBe(digestSfolValue(unsigned));

    const sampled = deriveMutationAdequacy({
      typed: typed.value,
      clause_id: clause.clause_id,
      fixtures: [fixture(false, false)],
      catalog_version: SFOL_MUTATION_CATALOG_VERSION,
      evaluation_domain: {
        kind: "bounded-sample",
        domain_digest: "b".repeat(64),
      },
    });
    expect(sampled.ok).toBe(true);
    if (!sampled.ok) return;
    expect(sampled.value.surviving_supported_count).toBeGreaterThan(0);
    expect(sampled.value.result).toBe("fail");
  });

  it("reports an undetected mutant as a survivor over a sampled domain", () => {
    const clause: LogicClause = {
      clause_id: "mutation.literal",
      kind: "predicate",
      status: "admitted",
      inputs: [],
      result_sort: { tag: "primitive", name: "boolean" },
      expression: {
        tag: "literal",
        value: { tag: "boolean", value: true },
        span: span("expression"),
      },
      observation_sort: null,
      span: span("clause"),
    };
    const source: NodeLogicModuleV1 = {
      schema_version: "domainspec-node-logic/v1",
      language_version: "domainspec-sfol/v1",
      module_id: "mutation.literal.module",
      source: {
        feature_id: "mutation",
        node_id: "literal",
        source_id: "mutation.fixture",
        source_path: "mutation.fixture.json",
      },
      declarations: [],
      clauses: [clause],
    };
    const typed = typecheckLogicModule(source);
    expect(typed.ok).toBe(true);
    if (!typed.ok) return;
    const result = deriveMutationAdequacy({
      typed: typed.value,
      clause_id: clause.clause_id,
      fixtures: [],
      catalog_version: SFOL_MUTATION_CATALOG_VERSION,
      evaluation_domain: {
        kind: "bounded-sample",
        domain_digest: "b".repeat(64),
      },
    });
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.diagnostics[0]?.code).toBe("SFOL_MUTATION_FIXTURE_EMPTY");
  });
});
