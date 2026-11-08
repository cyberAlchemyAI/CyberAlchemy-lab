import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  ClauseDenominatorError,
  buildClauseDenominator,
  type ClauseAdmissionManifest,
  type DenominatorErrorCode,
} from "./denominator/index.js";

type Mutable<T> = T extends readonly (infer Item)[]
  ? Mutable<Item>[]
  : T extends object
    ? { -readonly [Key in keyof T]: Mutable<T[Key]> }
    : T;

const D = {
  graph: "1".repeat(64),
  manifest: "2".repeat(64),
  build: "3".repeat(64),
  sourceSet: "4".repeat(64),
  profile: "5".repeat(64),
  nodeA: "6".repeat(64),
  nodeB: "7".repeat(64),
  moduleA: "8".repeat(64),
  moduleB: "9".repeat(64),
  clauseA: "a".repeat(64),
  clauseB: "b".repeat(64),
} as const;

function proofContext() {
  return {
    graph_id: "graph.framework-corpus",
    graph_digest: D.graph,
    manifest_id: "manifest.framework-corpus",
    manifest_digest: D.manifest,
    build_id: "build.framework-corpus",
    build_digest: D.build,
    source_set_digest: D.sourceSet,
    profile_id: "profile.domainspec-sfol",
    profile_version: "1.0.0",
    profile_digest: D.profile,
  };
}

function clauseContext() {
  return {
    graph_digest: D.graph,
    manifest_digest: D.manifest,
    build_digest: D.build,
    source_set_digest: D.sourceSet,
    profile_id: "profile.domainspec-sfol",
    profile_version: "1.0.0",
    profile_digest: D.profile,
  };
}

function manifest(): Mutable<ClauseAdmissionManifest> {
  return {
    schema_version: "domainspec-sfol-clause-admission-manifest/v1",
    source_form: "canonical-node-graph-manifest-build",
    unsupported_residue_policy: "reject",
    proof_context: proofContext(),
    clause_membership: ["framework.limit-holds", "framework.next-state"],
    clauses: [
      {
        clause_id: "framework.next-state",
        clause_digest: D.clauseB,
        node_id: "framework.ChangeState",
        node_digest: D.nodeB,
        module_id: "framework.change-state-logic",
        module_digest: D.moduleB,
        kind: "transition",
        required_roles: ["effects", "state"],
        status: "admitted",
        proof_context: clauseContext(),
      },
      {
        clause_id: "framework.limit-holds",
        clause_digest: D.clauseA,
        node_id: "framework.CheckLimit",
        node_digest: D.nodeA,
        module_id: "framework.check-limit-logic",
        module_digest: D.moduleA,
        kind: "invariant",
        required_roles: ["predicate"],
        status: "admitted",
        proof_context: clauseContext(),
      },
    ],
  };
}

function expectCode(action: () => unknown, code: DenominatorErrorCode): void {
  expect(action).toThrowError(
    expect.objectContaining<Partial<ClauseDenominatorError>>({ code }),
  );
}

describe("independent DS-SFOL clause denominator", () => {
  it("builds one deterministic exact identity/digest set from canonical handles", () => {
    const first = buildClauseDenominator(manifest());
    const secondInput = manifest();
    secondInput.clauses = [...secondInput.clauses].reverse();
    secondInput.clause_membership = [
      ...secondInput.clause_membership,
    ].reverse();
    const second = buildClauseDenominator(secondInput);

    expect(second).toEqual(first);
    expect(first.clause_ids).toEqual([
      "framework.limit-holds",
      "framework.next-state",
    ]);
    expect(first.coverage_keys).toEqual([
      "framework.limit-holds#predicate",
      "framework.next-state#effects",
      "framework.next-state#state",
    ]);
    expect(first.digest).toMatch(/^[a-f0-9]{64}$/);
    expect(Object.isFrozen(first)).toBe(true);
    expect(Object.isFrozen(first.members)).toBe(true);
    expect(Object.isFrozen(first.members[0])).toBe(true);
  });

  it("preserves every canonical node, module, clause, and proof-context handle", () => {
    const denominator = buildClauseDenominator(manifest());
    const member = denominator.members.find(
      ({ coverage_key }) => coverage_key === "framework.limit-holds#predicate",
    );
    expect(member).toEqual({
      coverage_key: "framework.limit-holds#predicate",
      role: "predicate",
      clause_id: "framework.limit-holds",
      clause_digest: D.clauseA,
      node_id: "framework.CheckLimit",
      node_digest: D.nodeA,
      module_id: "framework.check-limit-logic",
      module_digest: D.moduleA,
      kind: "invariant",
      graph_digest: D.graph,
      manifest_digest: D.manifest,
      build_digest: D.build,
      source_set_digest: D.sourceSet,
      profile_id: "profile.domainspec-sfol",
      profile_version: "1.0.0",
      profile_digest: D.profile,
    });
  });

  it("rejects empty, missing, and extra exact-set membership", () => {
    const empty = manifest();
    empty.clauses = [];
    empty.clause_membership = [];
    expectCode(
      () => buildClauseDenominator(empty),
      "SFOL_DENOMINATOR_EMPTY",
    );

    const missing = manifest();
    missing.clause_membership = ["framework.limit-holds"];
    expectCode(
      () => buildClauseDenominator(missing),
      "SFOL_DENOMINATOR_MEMBERSHIP_MISMATCH",
    );

    const extra = manifest();
    extra.clause_membership = [
      ...extra.clause_membership,
      "framework.orphan",
    ];
    expectCode(
      () => buildClauseDenominator(extra),
      "SFOL_DENOMINATOR_MEMBERSHIP_MISMATCH",
    );
  });

  it("rejects duplicate clause identities and duplicate coverage roles", () => {
    const duplicateClause = manifest();
    duplicateClause.clauses = [
      duplicateClause.clauses[0]!,
      {
        ...duplicateClause.clauses[1]!,
        clause_id: duplicateClause.clauses[0]!.clause_id,
      },
    ];
    duplicateClause.clause_membership = [
      duplicateClause.clauses[0]!.clause_id,
      duplicateClause.clauses[0]!.clause_id,
    ];
    expectCode(
      () => buildClauseDenominator(duplicateClause),
      "SFOL_DENOMINATOR_CLAUSE_DUPLICATE",
    );

    const duplicateRole = manifest();
    duplicateRole.clauses[0] = {
      ...duplicateRole.clauses[0]!,
      required_roles: ["state", "state"],
    };
    expectCode(
      () => buildClauseDenominator(duplicateRole),
      "SFOL_DENOMINATOR_COVERAGE_KEY_DUPLICATE",
    );
  });

  it("rejects stale or incompatible proof-context handles", () => {
    const stale = manifest();
    stale.clauses[0] = {
      ...stale.clauses[0]!,
      proof_context: {
        ...stale.clauses[0]!.proof_context,
        build_digest: "f".repeat(64),
      },
    };
    expectCode(
      () => buildClauseDenominator(stale),
      "SFOL_DENOMINATOR_CONTEXT_INCOMPATIBLE",
    );
  });

  it("rejects malformed digests, unknown kinds, and non-admitted clauses", () => {
    const malformed = manifest();
    malformed.clauses[0] = {
      ...malformed.clauses[0]!,
      clause_digest: "not-a-digest",
    };
    expectCode(
      () => buildClauseDenominator(malformed),
      "SFOL_DENOMINATOR_DIGEST_INVALID",
    );

    const unknownKind = manifest() as unknown as {
      clauses: Array<Record<string, unknown>>;
    };
    unknownKind.clauses[0]!.kind = "wish";
    expectCode(
      () => buildClauseDenominator(unknownKind),
      "SFOL_DENOMINATOR_KIND_UNKNOWN",
    );

    const candidate = manifest() as unknown as {
      clauses: Array<Record<string, unknown>>;
    };
    candidate.clauses[0]!.status = "candidate";
    expectCode(
      () => buildClauseDenominator(candidate),
      "SFOL_DENOMINATOR_STATUS_NOT_ADMITTED",
    );
  });

  it.each([
    ["generator-shaped", { generated_cases: [] }],
    ["Markdown-shaped", { markdown: "# inferred rules" }],
    ["direct-node-file", { node_path: "nodes/change-state.json" }],
  ])("rejects %s input without fallback parsing", (_name, residue) => {
    expectCode(
      () => buildClauseDenominator({ ...manifest(), ...residue }),
      "SFOL_DENOMINATOR_SOURCE_NONCANONICAL",
    );
  });

  it("rejects unsupported profiles and extra manifest fields", () => {
    const profile = {
      ...manifest(),
      unsupported_residue_policy: "ignore",
    };
    expectCode(
      () => buildClauseDenominator(profile),
      "SFOL_DENOMINATOR_PROFILE_UNSUPPORTED",
    );

    const extra = { ...manifest(), pass_summary: true };
    expectCode(
      () => buildClauseDenominator(extra),
      "SFOL_DENOMINATOR_SHAPE_INVALID",
    );
  });

  it("has no forbidden generator, runner, evaluator, proof, or receipt imports", () => {
    const source = readFileSync(
      new URL("./denominator/index.ts", import.meta.url),
      "utf8",
    );
    const imports = [...source.matchAll(/from\s+["']([^"']+)["']/g)].map(
      (match) => match[1]!,
    );
    expect(imports).toEqual(["node:crypto"]);
    expect(
      imports.filter((specifier) =>
        /(?:^|\/)(?:language|cases|bindings|emit|runners|evaluator|proof|generated|receipts)(?:\/|$)/.test(
          specifier,
        ),
      ),
    ).toEqual([]);
  });
});
