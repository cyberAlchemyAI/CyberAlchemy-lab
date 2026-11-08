import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import {
  BACKEND_KINDS,
  BACKEND_RELATIONSHIPS,
  DevelopmentEngineError,
  RELATIONSHIP_CONTRACTS,
  collectDevelopmentProjectDiagnostics,
  compileDevelopmentProject,
  replayDevelopmentBuild,
  type DevelopmentEngineErrorCode,
  type DevelopmentProject,
} from "./development-engine.js";
import { createCompleteDevelopmentProject } from "./development-fixture.js";

const thisDir = dirname(fileURLToPath(import.meta.url));
const relationshipAuthorityPath = resolve(
  thisDir,
  "../../../../definitions/relationships/relationships.yml",
);

function expectCode(
  action: () => unknown,
  code: DevelopmentEngineErrorCode,
): void {
  expect(action).toThrowError(
    expect.objectContaining<Partial<DevelopmentEngineError>>({ code }),
  );
}

function createDeclaredSubsetProject(): DevelopmentProject {
  const project = createCompleteDevelopmentProject();
  project.project_id = "bte-development-declared-subset";
  project.coverage_mode = "declared-subset";
  project.nodes = project.nodes.filter(({ node_id }) =>
    ["core.Account", "core.ChangeAccount"].includes(node_id),
  );
  project.edges = project.edges.filter(
    ({ edge_id }) => edge_id === "edge-performs",
  );
  return project;
}

describe("BTE development successor build", () => {
  it("compiles exact 13-kind/17-relationship independent inputs deterministically", () => {
    const project = createCompleteDevelopmentProject();
    const first = compileDevelopmentProject(project);
    const second = compileDevelopmentProject(project);
    expect(first).toEqual(second);
    expect([...new Set(first.graph.nodes.map(({ kind }) => kind))].sort()).toEqual(
      [...BACKEND_KINDS].sort(),
    );
    expect(first.graph.edges.map(({ family }) => family).sort()).toEqual(
      [...BACKEND_RELATIONSHIPS].sort(),
    );
    expect(first.sourceManifest.records).toHaveLength(
      project.nodes.length + project.edges.length,
    );
    expect(first.receipt.admission).toBe("development-only");
    expect(first.receipt.coverage_mode).toBe("complete-profile");
    expect(replayDevelopmentBuild(project, first)).toEqual({
      result: "pass",
      codes: [],
    });
  });

  it("matches the live DS-D8 backend denominator and endpoint/scope contracts", () => {
    const authority = JSON.parse(readFileSync(relationshipAuthorityPath, "utf8")) as {
      signatures: Array<{
        id: string;
        source_type?: string;
        source_types?: string[];
        target_type?: string;
        target_types?: string[];
        feature_scope: Array<"same-feature" | "cross-feature" | "ui" | "ui-backend">;
        status: string;
      }>;
    };
    const backendKinds = new Set<string>(BACKEND_KINDS);
    const backendSignatures = authority.signatures.filter((signature) => {
      const sources = signature.source_types ?? [signature.source_type!];
      const targets = signature.target_types ?? [signature.target_type!];
      return (
        signature.status === "active" &&
        sources.every((kind) => backendKinds.has(kind)) &&
        targets.every((kind) => backendKinds.has(kind))
      );
    });

    expect(backendSignatures.map(({ id }) => id)).toEqual([...BACKEND_RELATIONSHIPS]);
    for (const signature of backendSignatures) {
      const contract = RELATIONSHIP_CONTRACTS[signature.id as keyof typeof RELATIONSHIP_CONTRACTS];
      expect(contract, signature.id).toBeDefined();
      expect(contract.source).toEqual(signature.source_types ?? [signature.source_type]);
      expect(contract.target).toEqual(signature.target_types ?? [signature.target_type]);
      expect(contract.scopes).toEqual(signature.feature_scope);
    }
  });

  it("compiles and replays an exact declared subset", () => {
    const project = createDeclaredSubsetProject();
    const build = compileDevelopmentProject(project);
    expect(build.graph.coverage_mode).toBe("declared-subset");
    expect(build.receipt.coverage_mode).toBe("declared-subset");
    expect(build.receipt.kind_set).toEqual(["Entity", "Operation"]);
    expect(build.receipt.relationship_set).toEqual(["performs"]);
    expect(build.receipt.coverage_set_digest).toMatch(/^[a-f0-9]{64}$/);
    expect(replayDevelopmentBuild(project, build)).toEqual({
      result: "pass",
      codes: [],
    });
  });

  it("rejects empty or non-profile declared subset members", () => {
    const emptyNodes = createDeclaredSubsetProject();
    emptyNodes.nodes = [];
    expectCode(
      () => compileDevelopmentProject(emptyNodes),
      "BTE_DEV_PROFILE_INCOMPLETE",
    );

    const emptyEdges = createDeclaredSubsetProject();
    emptyEdges.edges = [];
    expectCode(
      () => compileDevelopmentProject(emptyEdges),
      "BTE_DEV_PROFILE_INCOMPLETE",
    );

    const unknownKind = createDeclaredSubsetProject();
    (unknownKind.nodes[0] as { kind: string }).kind = "Unknown";
    expectCode(
      () => compileDevelopmentProject(unknownKind),
      "BTE_DEV_PROFILE_INVALID",
    );

    const unknownRelationship = createDeclaredSubsetProject();
    (unknownRelationship.edges[0] as { family: string }).family = "unknown";
    expectCode(
      () => compileDevelopmentProject(unknownRelationship),
      "BTE_DEV_PROFILE_INVALID",
    );
  });

  it("binds declared coverage mode and sets into replay identity", () => {
    const project = createDeclaredSubsetProject();
    const build = compileDevelopmentProject(project);
    const tamperedMode = structuredClone(build);
    tamperedMode.receipt.coverage_mode = "complete-profile";
    expect(replayDevelopmentBuild(project, tamperedMode)).toEqual({
      result: "fail",
      codes: ["BTE_DEV_BUILD_REPLAY_MISMATCH"],
    });

    const tamperedSet = structuredClone(build);
    tamperedSet.receipt.kind_set = ["Entity"];
    expect(replayDevelopmentBuild(project, tamperedSet)).toEqual({
      result: "fail",
      codes: ["BTE_DEV_BUILD_REPLAY_MISMATCH"],
    });

    project.coverage_mode = "complete-profile";
    expect(replayDevelopmentBuild(project, build)).toEqual({
      result: "fail",
      codes: ["BTE_DEV_PROFILE_INCOMPLETE"],
    });
  });

  it("rejects the concrete Entity false green at formation rather than digest replay", () => {
    const project = createCompleteDevelopmentProject();
    project.nodes.find(({ node_id }) => node_id === "core.Account")!.body = {
      fields: [{ type: 7, identity: "yes" }],
    };
    expectCode(
      () => compileDevelopmentProject(project),
      "BTE_DEV_FORMATION_INVALID",
    );
  });

  it("rejects missing kind or relationship breadth", () => {
    const missingKind = createCompleteDevelopmentProject();
    missingKind.nodes = missingKind.nodes.filter(({ kind }) => kind !== "Enum");
    expectCode(
      () => compileDevelopmentProject(missingKind),
      "BTE_DEV_PROFILE_INCOMPLETE",
    );

    const missingRelationship = createCompleteDevelopmentProject();
    missingRelationship.edges = missingRelationship.edges.filter(
      ({ family }) => family !== "owns",
    );
    expectCode(
      () => compileDevelopmentProject(missingRelationship),
      "BTE_DEV_PROFILE_INCOMPLETE",
    );
  });

  it("rejects endpoint kind, feature scope, missing endpoint, and ordered-edge mutants", () => {
    const wrongKind = createCompleteDevelopmentProject();
    wrongKind.edges.find(({ family }) => family === "performs")!.to =
      "core.AccountChanged";
    expectCode(
      () => compileDevelopmentProject(wrongKind),
      "BTE_DEV_EDGE_ENDPOINT_KIND",
    );

    const calculationRead = createCompleteDevelopmentProject();
    calculationRead.edges.find(({ family }) => family === "reads")!.from =
      "core.Fee";
    expectCode(
      () => compileDevelopmentProject(calculationRead),
      "BTE_DEV_EDGE_ENDPOINT_KIND",
    );

    const wrongScope = createCompleteDevelopmentProject();
    wrongScope.edges.find(({ family }) => family === "produces-for")!.to =
      "core.Account";
    expectCode(
      () => compileDevelopmentProject(wrongScope),
      "BTE_DEV_EDGE_SCOPE",
    );

    const missing = createCompleteDevelopmentProject();
    missing.edges.find(({ family }) => family === "owns")!.to = "missing.Node";
    expectCode(
      () => compileDevelopmentProject(missing),
      "BTE_DEV_EDGE_ENDPOINT_MISSING",
    );

    const unordered = createCompleteDevelopmentProject();
    delete unordered.edges.find(({ family }) => family === "orchestrates")!.ordinal;
    expectCode(
      () => compileDevelopmentProject(unordered),
      "BTE_DEV_EDGE_ORDER",
    );
  });

  it("collects stable node and edge diagnostics while the compiler throws the first", () => {
    const project = createCompleteDevelopmentProject();
    project.nodes.find(({ node_id }) => node_id === "core.Account")!.body = {
      fields: [{ name: "account_id", type: 7, identity: "yes" }],
    };
    project.edges.find(({ edge_id }) => edge_id === "edge-performs")!.to =
      "core.AccountChanged";

    const first = collectDevelopmentProjectDiagnostics(project);
    const second = collectDevelopmentProjectDiagnostics(structuredClone(project));
    expect(first).toEqual(second);
    expect(first.result).toBe("fail");
    expect(
      first.diagnostics.map(
        ({ code, subject, criterion, source_anchor }) => ({
          code,
          subject,
          criterion,
          source_anchor,
        }),
      ),
    ).toEqual(
      expect.arrayContaining([
        {
          code: "BTE_DEV_FORMATION_INVALID",
          subject: "core.Account",
          criterion: "node-formation",
          source_anchor: "node:core.Account",
        },
        {
          code: "BTE_DEV_EDGE_ENDPOINT_KIND",
          subject: "edge-performs",
          criterion: "edge-contract",
          source_anchor: "edge:edge-performs",
        },
      ]),
    );
    expect(() => compileDevelopmentProject(project)).toThrowError(
      expect.objectContaining<Partial<DevelopmentEngineError>>({
        code: first.diagnostics[0]!.code,
        subject: first.diagnostics[0]!.subject,
      }),
    );
  });

  it("independent replay detects raw graph, manifest, and receipt tampering", () => {
    const project = createCompleteDevelopmentProject();
    const build = compileDevelopmentProject(project);
    const tampered = structuredClone(build);
    tampered.graphBytes += "tampered";
    expect(replayDevelopmentBuild(project, tampered)).toEqual({
      result: "fail",
      codes: ["BTE_DEV_BUILD_REPLAY_MISMATCH"],
    });
  });
});
