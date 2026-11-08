import assert from "node:assert/strict";
import { cpSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  MintedProjectCompilerError,
  classifyRelationshipType,
  compileMintedProject,
} from "../minted-project/compiler";

type JsonObject = Record<string, any>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const fixtureRoot = resolve(
  implRoot,
  "test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door",
);

function json(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function temporaryProject(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-minted-compiler-"));
  cpSync(fixtureRoot, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { force: true, recursive: true }) };
}

function mutateNode(root: string, name: string, mutate: (node: JsonObject) => void): void {
  const path = resolve(root, `specs/key-and-door/nodes/${name}.json`);
  const node = json(path);
  mutate(node);
  writeJson(path, node);
}

function expectCode(root: string, code: string): void {
  assert.throws(() => compileMintedProject(root), (error: unknown) => {
    assert.ok(error instanceof MintedProjectCompilerError);
    assert.equal(error.code, code);
    return true;
  });
}

test("Key and Door compiles to exact deterministic graph and provenance bytes", () => {
  const first = compileMintedProject(fixtureRoot);
  const second = compileMintedProject(fixtureRoot);
  assert.equal(first.graphBytes, second.graphBytes);
  assert.equal(first.sourceManifestBytes, second.sourceManifestBytes);
  assert.deepEqual(first.graph, json(resolve(fixtureRoot, "expected/graph.json")));
  assert.deepEqual(
    first.sourceManifest,
    json(resolve(fixtureRoot, "expected/source-manifest.json")),
  );
  assert.deepEqual(
    first.sourceManifest.records.map((record) => record.graph_id).sort(),
    [
      ...first.graph.nodes.map((node) => node.node_id),
      ...first.graph.edges.map((edge) => edge.edge_id),
    ].sort(),
  );
});

test("zero-feature and zero-node projects compile to valid empty read models", () => {
  const cases = ["featureless", "nodeless"] as const;
  for (const kind of cases) {
    const project = temporaryProject();
    try {
      if (kind === "featureless") {
        const manifest = json(resolve(project.root, "project.json"));
        manifest.features = [];
        writeJson(resolve(project.root, "project.json"), manifest);
      } else {
        const featurePath = resolve(project.root, "specs/key-and-door/feature.json");
        const feature = json(featurePath);
        feature.node_sources = [];
        writeJson(featurePath, feature);
      }

      const first = compileMintedProject(project.root);
      const second = compileMintedProject(project.root);
      assert.equal(first.graphBytes, second.graphBytes);
      assert.equal(first.sourceManifestBytes, second.sourceManifestBytes);
      assert.deepEqual(first.graph.nodes, []);
      assert.deepEqual(first.graph.edges, []);
      assert.deepEqual(first.sourceManifest.records, []);
      assert.deepEqual(
        first.sourceManifest.inputs.map((input) => input.path),
        kind === "featureless"
          ? ["project.json"]
          : ["project.json", "specs/key-and-door/feature.json"],
      );
    } finally {
      project.cleanup();
    }
  }
});

test("unsupported kind and invalid formation fail independently", () => {
  const kind = temporaryProject();
  try {
    mutateNode(kind.root, "player", (node) => {
      node.kind = "Value Object";
    });
    expectCode(kind.root, "KIND_UNSUPPORTED");
  } finally {
    kind.cleanup();
  }

  const formation = temporaryProject();
  try {
    mutateNode(formation.root, "unlock-door", (node) => {
      node.body.state_change = "no";
    });
    expectCode(formation.root, "FORMATION_INVALID");
  } finally {
    formation.cleanup();
  }
});

test("formation diagnostics preserve criterion IDs, rules, and machine codes", () => {
  const project = temporaryProject();
  try {
    mutateNode(project.root, "unlock-door", (node) => {
      node.body.state_change = "no";
    });
    assert.throws(() => compileMintedProject(project.root), (error: unknown) => {
      assert.ok(error instanceof MintedProjectCompilerError);
      assert.equal(error.code, "FORMATION_INVALID");
      assert.match(error.message, /"criterionId":"writes_state"/);
      assert.match(error.message, /"rule":"attribute-equals"/);
      assert.match(error.message, /"code":"ATTRIBUTE-VALUE-MISMATCH"/);
      return true;
    });
  } finally {
    project.cleanup();
  }
});

test("duplicate node and edge IDs fail before graph emission", () => {
  const nodeDuplicate = temporaryProject();
  try {
    mutateNode(nodeDuplicate.root, "player", (node) => {
      node.node_id = "key-and-door.DoorUnlocked";
    });
    expectCode(nodeDuplicate.root, "NODE_ID_DUPLICATE");
  } finally {
    nodeDuplicate.cleanup();
  }

  const edgeDuplicate = temporaryProject();
  try {
    mutateNode(edgeDuplicate.root, "player", (node) => {
      node.connections[0].edge_id = "key-and-door.edge.has-key-rule-enforces-unlock-door";
    });
    expectCode(edgeDuplicate.root, "EDGE_ID_DUPLICATE");
  } finally {
    edgeDuplicate.cleanup();
  }
});

test("relationship type classes and endpoint failures remain distinct", () => {
  const cases = [
    ["unknown-edge", "EDGE_TYPE_UNKNOWN"],
    ["owned-by", "EDGE_TYPE_GENERATED"],
    ["emits", "EDGE_TYPE_UNSUPPORTED_PROFILE"],
  ] as const;
  for (const [type, code] of cases) {
    const project = temporaryProject();
    try {
      mutateNode(project.root, "player", (node) => {
        node.connections[0].type = type;
      });
      expectCode(project.root, code);
    } finally {
      project.cleanup();
    }
  }

  const missing = temporaryProject();
  try {
    mutateNode(missing.root, "player", (node) => {
      node.connections[0].to = "key-and-door.Missing";
    });
    expectCode(missing.root, "EDGE_ENDPOINT_MISSING");
  } finally {
    missing.cleanup();
  }

  const mismatch = temporaryProject();
  try {
    mutateNode(mismatch.root, "player", (node) => {
      node.connections[0].to = "key-and-door.DoorUnlocked";
    });
    expectCode(mismatch.root, "EDGE_ENDPOINT_KIND_MISMATCH");
  } finally {
    mismatch.cleanup();
  }
});

test("deprecated and deferred classifiers are testable without inventing registry entries", () => {
  const profile = [{
    id: "legacy",
    source_kind: "Entity",
    target_kind: "Operation",
    registry_status: "active",
  }];
  assert.equal(
    classifyRelationshipType(
      "queries",
      {
        signatures: [{ id: "reads", status: "active" }],
        deprecated: [{ id: "queries", replacement: "reads" }],
      },
      [{ ...profile[0], id: "reads" }],
    ),
    "EDGE_TYPE_DEPRECATED",
  );
  assert.equal(
    classifyRelationshipType(
      "legacy",
      { signatures: [{ id: "legacy", status: "deprecated" }] },
      profile,
    ),
    "EDGE_TYPE_DEPRECATED",
  );
  assert.equal(
    classifyRelationshipType(
      "legacy",
      { signatures: [{ id: "legacy", status: "deferred" }] },
      profile,
    ),
    "EDGE_TYPE_DEFERRED",
  );
});

test("relationship scope rejects a cross-feature use of a same-feature signature", () => {
  const project = temporaryProject();
  try {
    mkdirSync(resolve(project.root, "specs/other/nodes"), { recursive: true });
    writeJson(resolve(project.root, "specs/other/feature.json"), {
      schema_version: "minted-feature/v1",
      feature_id: "other",
      source_layout: "per-node-connections",
      node_sources: ["nodes/target.json"],
    });
    writeJson(resolve(project.root, "specs/other/nodes/target.json"), {
      schema_version: "minted-node/v1",
      node_id: "other.Target",
      feature_id: "other",
      kind: "Operation",
      intent: "Cross-feature target used only to prove the current boundary.",
      body: { state_change: "yes" },
      connections: [],
    });
    const manifest = json(resolve(project.root, "project.json"));
    manifest.features.push("specs/other/feature.json");
    writeJson(resolve(project.root, "project.json"), manifest);
    mutateNode(project.root, "player", (node) => {
      node.connections[0].to = "other.Target";
    });
    expectCode(project.root, "EDGE_FEATURE_SCOPE_MISMATCH");
  } finally {
    project.cleanup();
  }
});
