import { createHash } from "node:crypto";
import {
  cpSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import {
  MintedProjectCompilerError,
  classifyRelationshipType,
  compileMintedProject,
} from "../../../tools/minted-project/compiler.js";
import {
  MintedProjectMinterError,
  mintMintedProject,
} from "../../../tools/minted-project/minter.js";
import { MintedProjectResolverError } from "../../../tools/minted-project/resolver.js";
import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
  type MintedProjectBuildArtifacts,
} from "../../../tools/minted-project/views.js";
import {
  createMintedProjectConformanceReceipt,
  verifyMintedProjectConformanceReceipt,
  type ConformanceCaseResult,
  type ConformanceFixtureInput,
  type ConformanceMatrix,
} from "./conformance-receipt.js";

type JsonObject = Record<string, any>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(thisDir, "../../__fixtures__/minted-project");
const keyRoot = resolve(fixtureRoot, "contract/positive/key-and-door");
const messageRoot = resolve(fixtureRoot, "conformance/positive/message-delivery");
const matrixPath = resolve(fixtureRoot, "conformance/CONFORMANCE-MATRIX.json");
const matrix = JSON.parse(readFileSync(matrixPath, "utf8")) as ConformanceMatrix;

const fixtures: ConformanceFixtureInput[] = [
  {
    id: "key-and-door",
    path: "contract/positive/key-and-door",
    root: keyRoot,
  },
  {
    id: "message-delivery",
    path: "conformance/positive/message-delivery",
    root: messageRoot,
  },
];

function json(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function temporaryFixture(source = keyRoot): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-minted-conformance-"));
  cpSync(source, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { force: true, recursive: true }) };
}

function mutateKeyNode(root: string, name: string, mutate: (node: JsonObject) => void): void {
  const path = resolve(root, `specs/key-and-door/nodes/${name}.json`);
  const node = json(path);
  mutate(node);
  writeJson(path, node);
}

function errorCode(action: () => unknown): string {
  try {
    action();
    return "NO_FAILURE";
  } catch (error) {
    if (
      error instanceof MintedProjectCompilerError ||
      error instanceof MintedProjectResolverError ||
      error instanceof MintedProjectMinterError
    ) {
      return error.code;
    }
    throw error;
  }
}

function cloneBuild(build: MintedProjectBuildArtifacts): MintedProjectBuildArtifacts {
  return structuredClone(build);
}

function selectedCode(codes: string[], expected: string): string {
  return codes.includes(expected) ? expected : codes[0] ?? "NO_FAILURE";
}

function compileMutation(mutate: (root: string) => void): string {
  const fixture = temporaryFixture();
  try {
    mutate(fixture.root);
    return errorCode(() => compileMintedProject(fixture.root));
  } finally {
    fixture.cleanup();
  }
}

function verifyMutation(
  mutate: (root: string, build: MintedProjectBuildArtifacts) => MintedProjectBuildArtifacts,
  expected: string,
): string {
  const fixture = temporaryFixture();
  try {
    const build = buildMintedProjectViews(fixture.root);
    const changed = mutate(fixture.root, cloneBuild(build));
    return selectedCode(verifyMintedProjectBuild(fixture.root, changed).codes, expected);
  } finally {
    fixture.cleanup();
  }
}

function runCase(caseId: string, expected: string): string {
  switch (caseId) {
    case "dangling-target":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.connections[0].to = "key-and-door.MissingDoor";
      }));
    case "duplicate-edge-ownership":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.connections[0].edge_id = "key-and-door.edge.has-key-rule-enforces-unlock-door";
      }));
    case "unknown-relationship":
    case "relationship-unknown":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.connections[0].type = "opens";
      }));
    case "endpoint-invalid":
    case "relationship-wrong-endpoint":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.connections[0].to = "key-and-door.DoorUnlocked";
      }));
    case "stale-graph":
    case "damage-graph":
      return verifyMutation((_root, build) => {
        const graph = JSON.parse(build.graphBytes) as JsonObject;
        graph.nodes[0].intent = "tampered graph";
        build.graphBytes = `${JSON.stringify(graph, null, 2)}\n`;
        return build;
      }, expected);
    case "stale-markdown":
    case "damage-markdown":
      return verifyMutation((_root, build) => {
        build.markdownBytes += "tampered Markdown\n";
        return build;
      }, expected);
    case "markdown-only-machine-field":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        delete node.intent;
      }));
    case "external-source-root":
      return compileMutation((root) => {
        const project = json(resolve(root, "project.json"));
        project.features = ["../outside.json"];
        writeJson(resolve(root, "project.json"), project);
      });
    case "stale-source":
    case "damage-source":
      return verifyMutation((root, build) => {
        mutateKeyNode(root, "player", (node) => {
          node.intent = `${node.intent} Changed.`;
        });
        return build;
      }, expected);
    case "language-digest-mismatch":
      return compileMutation((root) => {
        const project = json(resolve(root, "project.json"));
        project.language.registries.relationships_digest = "0".repeat(64);
        writeJson(resolve(root, "project.json"), project);
      });
    case "formation-entity":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.body.fields[0].identity = false;
      }));
    case "formation-event":
      return compileMutation((root) => mutateKeyNode(root, "door-unlocked", (node) => {
        node.body.temporal = "future";
      }));
    case "formation-operation":
      return compileMutation((root) => mutateKeyNode(root, "unlock-door", (node) => {
        node.body.state_change = "no";
      }));
    case "formation-rule":
      return compileMutation((root) => mutateKeyNode(root, "has-key-rule", (node) => {
        node.body.formal_return_type = "string";
      }));
    case "relationship-generated":
      return compileMutation((root) => mutateKeyNode(root, "player", (node) => {
        node.connections[0].type = "owned-by";
      }));
    case "relationship-deprecated":
      return classifyRelationshipType(
        "legacy",
        { signatures: [{ id: "legacy", status: "deprecated" }] },
        [{ id: "legacy", source_kind: "Entity", target_kind: "Operation", registry_status: "active" }],
      );
    case "relationship-deferred":
      return classifyRelationshipType(
        "future",
        { signatures: [{ id: "future", status: "deferred" }] },
        [{ id: "future", source_kind: "Entity", target_kind: "Operation", registry_status: "active" }],
      );
    case "relationship-disallowed-scope":
      return compileMutation((root) => {
        cpSync(
          resolve(messageRoot, "specs/message-delivery"),
          resolve(root, "specs/message-delivery"),
          { recursive: true },
        );
        const project = json(resolve(root, "project.json"));
        project.features.push("specs/message-delivery/feature.json");
        writeJson(resolve(root, "project.json"), project);
        mutateKeyNode(root, "player", (node) => {
          node.connections[0].to = "message-delivery.SendMessage";
        });
      });
    case "damage-manifest":
      return verifyMutation((_root, build) => {
        const manifest = JSON.parse(build.sourceManifestBytes) as JsonObject;
        manifest.records[0].source_path = "wrong.json";
        build.sourceManifestBytes = `${JSON.stringify(manifest, null, 2)}\n`;
        return build;
      }, expected);
    case "damage-language-binding":
      return compileMutation((root) => {
        const project = json(resolve(root, "project.json"));
        project.language.profile.digest = "0".repeat(64);
        writeJson(resolve(root, "project.json"), project);
      });
    case "damage-generated-root": {
      const parent = mkdtempSync(resolve(tmpdir(), "domainspec-minted-root-damage-"));
      try {
        return errorCode(() => mintMintedProject({
          destination: resolve(parent, "project"),
          projectId: "damaged-root",
          generatedRoot: "../outside",
        }));
      } finally {
        rmSync(parent, { force: true, recursive: true });
      }
    }
    default:
      throw new Error(`unimplemented conformance case: ${caseId}`);
  }
}

function runMatrix(): ConformanceCaseResult[] {
  return matrix.cases.map((entry) => ({
    case_id: entry.case_id,
    actual_code: runCase(entry.case_id, entry.expected_code),
    status: "pass" as const,
  }));
}

describe("minted-project production conformance", () => {
  it("keeps the two positive corpora independent, deterministic, navigable, and mint-compatible", () => {
    const graphs = fixtures.map((fixture) => {
      const first = compileMintedProject(fixture.root);
      const second = compileMintedProject(fixture.root);
      expect(first.graphBytes).toBe(second.graphBytes);
      expect(first.sourceManifestBytes).toBe(second.sourceManifestBytes);
      const built = buildMintedProjectViews(fixture.root);
      expect(verifyMintedProjectBuild(fixture.root, built)).toEqual({ status: "pass", codes: [] });
      expect(first.sourceManifest.records.map((record) => record.graph_id).sort()).toEqual([
        ...first.graph.nodes.map((node) => node.node_id),
        ...first.graph.edges.map((edge) => edge.edge_id),
      ].sort());
      return first.graph;
    });
    expect(graphs[0]!.nodes).toHaveLength(4);
    expect(graphs[0]!.edges).toHaveLength(3);
    expect(graphs[1]!.nodes).toHaveLength(2);
    expect(graphs[1]!.edges).toHaveLength(1);
    expect(new Set(graphs.flatMap((graph) => graph.nodes.map((node) => node.node_id))).size)
      .toBe(6);
    expect(new Set(graphs.flatMap((graph) => graph.nodes.map((node) => node.intent))).size)
      .toBe(6);

    for (const [index, fixture] of fixtures.entries()) {
      const parent = mkdtempSync(resolve(tmpdir(), "domainspec-minted-positive-mint-"));
      try {
        const minted = mintMintedProject({
          destination: resolve(parent, "project"),
          projectId: index === 0 ? "conformance-primary" : "conformance-secondary",
        });
        cpSync(resolve(fixture.root, "specs"), resolve(minted.projectRoot, "specs"), {
          recursive: true,
        });
        writeFileSync(
          resolve(minted.projectRoot, "project.json"),
          readFileSync(resolve(fixture.root, "project.json")),
        );
        expect(verifyMintedProjectBuild(
          minted.projectRoot,
          buildMintedProjectViews(minted.projectRoot),
        )).toEqual({ status: "pass", codes: [] });
      } finally {
        rmSync(parent, { force: true, recursive: true });
      }
    }
  });

  it("executes all inherited, formation, relationship-state, and damage controls distinctly", () => {
    expect(matrix.cases).toHaveLength(26);
    expect(matrix.cases.filter((entry) => entry.source === "S06")).toHaveLength(8);
    expect(matrix.cases.filter((entry) => entry.source === "S08")).toHaveLength(2);
    const results = runMatrix();
    for (const [index, result] of results.entries()) {
      expect(result.actual_code, result.case_id).toBe(matrix.cases[index]!.expected_code);
    }
  });

  it("replays a digest-bound non-admission receipt and invalidates fixture/result mutations", () => {
    const results = runMatrix();
    const first = createMintedProjectConformanceReceipt({
      matrixPath,
      fixtures,
      results,
    });
    const second = createMintedProjectConformanceReceipt({
      matrixPath,
      fixtures,
      results,
    });
    expect(first).toEqual(second);
    expect(first.release_admission).toBe("not-granted");
    expect(first.inherited_control_count).toBe(10);
    expect(first.degraded_case_count).toBe(26);
    expect(verifyMintedProjectConformanceReceipt(first, matrixPath, fixtures)).toEqual({
      status: "pass",
      codes: [],
    });

    const mutated = temporaryFixture(messageRoot);
    try {
      const path = resolve(mutated.root, "specs/message-delivery/nodes/send-message.json");
      const node = json(path);
      node.intent = `${node.intent} Mutated.`;
      writeJson(path, node);
      const changedFixtures = fixtures.map((fixture) =>
        fixture.id === "message-delivery" ? { ...fixture, root: mutated.root } : fixture,
      );
      expect(
        verifyMintedProjectConformanceReceipt(first, matrixPath, changedFixtures).codes,
      ).toContain("FIXTURE_DIGEST_MISMATCH");
    } finally {
      mutated.cleanup();
    }

    const tampered = structuredClone(first);
    tampered.case_results[0]!.actual_code = "NO_FAILURE";
    expect(verifyMintedProjectConformanceReceipt(tampered, matrixPath, fixtures).codes)
      .toContain("CONTROL_RESULT_MISMATCH");
  });
});
