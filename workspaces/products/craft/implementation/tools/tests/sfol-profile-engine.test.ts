import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  NODE_PROJECTION_ADMISSION_VERSION,
  NODE_PROOF_CONTEXT_VERSION,
  projectNodeLogic,
} from "../../test-derivation-engine/src/sfol/node-source/index";
import {
  MintedProjectCompilerError,
  compileMintedProject,
  type MintedProjectCompileOptions,
} from "../minted-project/compiler";
import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
} from "../minted-project/views";

type JsonObject = Record<string, any>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const registryPath = resolve(implRoot, "spec/sfol-profile/minted-project-profile.json");

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function json(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function span(sourceId: string, path: string): JsonObject {
  return {
    source_id: sourceId,
    path,
    start: { line: 1, column: 1 },
    end: { line: 1, column: 8 },
  };
}

function logic(nodeId: string, sourcePath: string, clauseId: string): JsonObject {
  return {
    schema_version: "domainspec-node-logic/v1",
    language_version: "domainspec-sfol/v1",
    module_id: `${nodeId}-logic`,
    source: {
      feature_id: "sfol-test",
      node_id: nodeId,
      source_id: nodeId,
      source_path: sourcePath,
    },
    declarations: [],
    clauses: [
      {
        clause_id: clauseId,
        kind: "invariant",
        status: "admitted",
        inputs: [],
        result_sort: { tag: "primitive", name: "boolean" },
        expression: {
          tag: "literal",
          value: { tag: "boolean", value: true },
          span: span(nodeId, "body.logic.clauses[0].expression"),
        },
        observation_sort: null,
        span: span(nodeId, "body.logic.clauses[0]"),
      },
    ],
  };
}

function expectCompilerCode(action: () => unknown, code: string): void {
  assert.throws(action, (error: unknown) => {
    assert.ok(error instanceof MintedProjectCompilerError);
    assert.equal(error.code, code);
    return true;
  });
}

function makeProject(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-sfol-profile-"));
  mkdirSync(resolve(root, "nodes"), { recursive: true });
  const registry = json(registryPath);
  writeJson(resolve(root, "project.json"), {
    schema_version: "minted-project/v1",
    project_id: "sfol-test",
    language: {
      profile: {
        id: "sfol-development",
        version: "0.1",
        digest: sha256(readFileSync(registryPath)),
      },
      registries: {
        kinds_digest: registry.registry_bindings.kinds.sha256,
        relationships_digest: registry.registry_bindings.relationships.sha256,
      },
    },
    features: ["feature.json"],
    generated_root: ".domainspec/generated",
  });
  writeJson(resolve(root, "feature.json"), {
    schema_version: "minted-feature/v1",
    feature_id: "sfol-test",
    source_layout: "per-node-connections",
    node_sources: [
      "nodes/calculation.json",
      "nodes/operation.json",
      "nodes/event.json",
    ],
  });
  writeJson(resolve(root, "nodes/calculation.json"), {
    schema_version: "minted-node/v1",
    node_id: "sfol-test.FeeCalculation",
    feature_id: "sfol-test",
    kind: "Calculation",
    intent: "Derive the fee used by settlement.",
    body: {
      formal_return_type: "value",
      logic: logic(
        "sfol-test.FeeCalculation",
        "nodes/calculation.json",
        "sfol-test.fee-is-defined",
      ),
    },
    connections: [
      {
        edge_id: "sfol-test.edge.fee-calculates-settlement",
        type: "calculates",
        to: "sfol-test.GenerateSettlement",
      },
    ],
  });
  writeJson(resolve(root, "nodes/operation.json"), {
    schema_version: "minted-node/v1",
    node_id: "sfol-test.GenerateSettlement",
    feature_id: "sfol-test",
    kind: "Operation",
    intent: "Generate one settlement.",
    body: {
      state_change: "yes",
      logic: logic(
        "sfol-test.GenerateSettlement",
        "nodes/operation.json",
        "sfol-test.settlement-is-defined",
      ),
    },
    connections: [
      {
        edge_id: "sfol-test.edge.settlement-produces-event",
        type: "produces",
        to: "sfol-test.SettlementGenerated",
      },
    ],
  });
  writeJson(resolve(root, "nodes/event.json"), {
    schema_version: "minted-node/v1",
    node_id: "sfol-test.SettlementGenerated",
    feature_id: "sfol-test",
    kind: "Event",
    intent: "Record that settlement generation completed.",
    body: { temporal: "past" },
    connections: [],
  });
  return {
    root,
    cleanup: () => rmSync(root, { recursive: true, force: true }),
  };
}

function options(path = registryPath): MintedProjectCompileOptions {
  return {
    developmentProfileRegistry: {
      path,
      handle: "sfol-development-explicit-v0.1",
    },
  };
}

function withRegistryMutation(
  root: string,
  mutate: (registry: JsonObject) => void,
): MintedProjectCompileOptions {
  const registry = json(registryPath);
  mutate(registry);
  const path = resolve(root, "mutated-profile.json");
  writeJson(path, registry);
  const projectPath = resolve(root, "project.json");
  const project = json(projectPath);
  project.language.profile.digest = sha256(readFileSync(path));
  writeJson(projectPath, project);
  return options(path);
}

test("SFOL development profile compiles deterministically and projects canonical node logic", () => {
  const project = makeProject();
  try {
    const first = buildMintedProjectViews(project.root, options());
    const second = buildMintedProjectViews(project.root, options());
    assert.equal(first.graphBytes, second.graphBytes);
    assert.equal(first.sourceManifestBytes, second.sourceManifestBytes);
    assert.deepEqual(
      first.graph.nodes.find((node) => node.node_id === "sfol-test.FeeCalculation")?.body.logic,
      json(resolve(project.root, "nodes/calculation.json")).body.logic,
    );
    assert.deepEqual(verifyMintedProjectBuild(project.root, first), {
      status: "pass",
      codes: [],
    });

    const projected = projectNodeLogic(
      {
        schema_version: NODE_PROOF_CONTEXT_VERSION,
        route: "canonical-minted-project-build",
        graph_bytes: first.graphBytes,
        source_manifest_bytes: first.sourceManifestBytes,
        build_receipt_bytes: first.buildReceiptBytes,
      },
      {
        schema_version: NODE_PROJECTION_ADMISSION_VERSION,
        profile_id: "sfol-development",
        profile_version: "0.1",
        logic_schema_versions: ["domainspec-node-logic/v1"],
        admitted_node_ids: [
          "sfol-test.FeeCalculation",
          "sfol-test.GenerateSettlement",
        ],
      },
    );
    assert.equal(projected.ok, true);
    assert.deepEqual(
      projected.ok ? projected.value.map((entry) => entry.node.node_id) : [],
      ["sfol-test.FeeCalculation", "sfol-test.GenerateSettlement"],
    );
    assert.ok(projected.ok && projected.value.every((entry) => entry.logic_digest.length === 64));
  } finally {
    project.cleanup();
  }
});

test("SFOL node logic fails closed across profile, kind, version, schema, and schema binding", () => {
  const unsupported = makeProject();
  try {
    const mutatedOptions = withRegistryMutation(unsupported.root, (registry) => {
      delete registry.profiles[0].logic_contract;
    });
    expectCompilerCode(
      () => compileMintedProject(unsupported.root, mutatedOptions),
      "NODE_LOGIC_PROFILE_UNSUPPORTED",
    );
  } finally {
    unsupported.cleanup();
  }

  const kind = makeProject();
  try {
    const eventPath = resolve(kind.root, "nodes/event.json");
    const event = json(eventPath);
    event.body.logic = logic(
      "sfol-test.SettlementGenerated",
      "nodes/event.json",
      "sfol-test.event-is-defined",
    );
    writeJson(eventPath, event);
    expectCompilerCode(
      () => compileMintedProject(kind.root, options()),
      "NODE_LOGIC_KIND_UNSUPPORTED",
    );
  } finally {
    kind.cleanup();
  }

  const version = makeProject();
  try {
    const path = resolve(version.root, "nodes/calculation.json");
    const node = json(path);
    node.body.logic.schema_version = "domainspec-node-logic/v2";
    writeJson(path, node);
    expectCompilerCode(
      () => compileMintedProject(version.root, options()),
      "NODE_LOGIC_VERSION_UNSUPPORTED",
    );
  } finally {
    version.cleanup();
  }

  const malformed = makeProject();
  try {
    const path = resolve(malformed.root, "nodes/calculation.json");
    const node = json(path);
    delete node.body.logic.language_version;
    writeJson(path, node);
    expectCompilerCode(
      () => compileMintedProject(malformed.root, options()),
      "NODE_LOGIC_SCHEMA_INVALID",
    );
  } finally {
    malformed.cleanup();
  }

  const binding = makeProject();
  try {
    const mutatedOptions = withRegistryMutation(binding.root, (registry) => {
      registry.profiles[0].logic_contract.envelope_schema.sha256 = "0".repeat(64);
    });
    expectCompilerCode(
      () => compileMintedProject(binding.root, mutatedOptions),
      "NODE_LOGIC_SCHEMA_BINDING_INVALID",
    );
  } finally {
    binding.cleanup();
  }
});
