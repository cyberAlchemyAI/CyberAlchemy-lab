import assert from "node:assert/strict";
import { cpSync, mkdtempSync, readFileSync, rmSync, unlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { MintedProjectCompilerError } from "../minted-project/compiler";
import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
  type MintedProjectBuildArtifacts,
} from "../minted-project/views";

type JsonObject = Record<string, any>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const fixtureRoot = resolve(
  implRoot,
  "test-derivation-engine/__fixtures__/minted-project/contract/positive/key-and-door",
);

function temporaryProject(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-minted-views-"));
  cpSync(fixtureRoot, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { force: true, recursive: true }) };
}

function clone(artifacts: MintedProjectBuildArtifacts): MintedProjectBuildArtifacts {
  return structuredClone(artifacts);
}

function json(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

test("unchanged view builds are byte-equal and verify cleanly", () => {
  const first = buildMintedProjectViews(fixtureRoot);
  const second = buildMintedProjectViews(fixtureRoot);
  assert.equal(first.graphBytes, second.graphBytes);
  assert.equal(first.sourceManifestBytes, second.sourceManifestBytes);
  assert.equal(first.markdownBytes, second.markdownBytes);
  assert.equal(first.markdownViewBytes, second.markdownViewBytes);
  assert.equal(first.buildReceiptBytes, second.buildReceiptBytes);
  assert.deepEqual(verifyMintedProjectBuild(fixtureRoot, first), { status: "pass", codes: [] });
  assert.match(first.markdownBytes, /Generated human view/);
  assert.match(first.markdownBytes, /Graph digest: `[a-f0-9]{64}`/);
  assert.ok(!first.markdownBytes.includes("state_change"));
  assert.ok(!first.markdownBytes.includes("formal_return_type"));
});

test("an example-free project produces deterministic verified empty views", () => {
  const project = temporaryProject();
  try {
    const manifest = json(resolve(project.root, "project.json"));
    manifest.features = [];
    writeJson(resolve(project.root, "project.json"), manifest);

    const first = buildMintedProjectViews(project.root);
    const second = buildMintedProjectViews(project.root);
    assert.equal(first.graphBytes, second.graphBytes);
    assert.equal(first.sourceManifestBytes, second.sourceManifestBytes);
    assert.equal(first.markdownBytes, second.markdownBytes);
    assert.equal(first.markdownViewBytes, second.markdownViewBytes);
    assert.equal(first.buildReceiptBytes, second.buildReceiptBytes);
    assert.deepEqual(first.graph.nodes, []);
    assert.deepEqual(first.graph.edges, []);
    assert.deepEqual(first.sourceManifest.records, []);
    assert.deepEqual(verifyMintedProjectBuild(project.root, first), {
      status: "pass",
      codes: [],
    });
  } finally {
    project.cleanup();
  }
});

test("source, graph, source-manifest, Markdown-view, and Markdown drift are independent", () => {
  const source = temporaryProject();
  try {
    const built = buildMintedProjectViews(source.root);
    const playerPath = resolve(source.root, "specs/key-and-door/nodes/player.json");
    const player = json(playerPath);
    player.intent = `${player.intent} Changed.`;
    writeJson(playerPath, player);
    const result = verifyMintedProjectBuild(source.root, built);
    assert.ok(result.codes.includes("STALE_SOURCE"));
    assert.ok(result.codes.includes("PROVENANCE_INVALID"));
  } finally {
    source.cleanup();
  }

  const original = buildMintedProjectViews(fixtureRoot);
  const graph = clone(original);
  const graphObject = JSON.parse(graph.graphBytes) as JsonObject;
  graphObject.nodes[0].intent = "tampered";
  graph.graphBytes = `${JSON.stringify(graphObject, null, 2)}\n`;
  assert.ok(verifyMintedProjectBuild(fixtureRoot, graph).codes.includes("STALE_GRAPH"));

  const manifest = clone(original);
  const manifestObject = JSON.parse(manifest.sourceManifestBytes) as JsonObject;
  manifestObject.records[0].source_path = "wrong.json";
  manifest.sourceManifestBytes = `${JSON.stringify(manifestObject, null, 2)}\n`;
  const manifestResult = verifyMintedProjectBuild(fixtureRoot, manifest);
  assert.ok(manifestResult.codes.includes("STALE_SOURCE_MANIFEST"));
  assert.ok(manifestResult.codes.includes("PROVENANCE_INVALID"));

  const markdownView = clone(original);
  const viewObject = JSON.parse(markdownView.markdownViewBytes) as JsonObject;
  viewObject.graph_digest = "0".repeat(64);
  markdownView.markdownViewBytes = `${JSON.stringify(viewObject, null, 2)}\n`;
  assert.ok(
    verifyMintedProjectBuild(fixtureRoot, markdownView).codes.includes("STALE_MARKDOWN_VIEW"),
  );

  const markdown = clone(original);
  markdown.markdownBytes += "hand edit\n";
  assert.ok(verifyMintedProjectBuild(fixtureRoot, markdown).codes.includes("STALE_MARKDOWN"));
});

test("deleted sources fail safely", () => {
  const project = temporaryProject();
  try {
    const built = buildMintedProjectViews(project.root);
    unlinkSync(resolve(project.root, "specs/key-and-door/nodes/player.json"));
    assert.ok(
      verifyMintedProjectBuild(project.root, built).codes.includes("SOURCE_UNAVAILABLE"),
    );
  } finally {
    project.cleanup();
  }
});

test("authored Markdown is never an input and cannot repair missing machine semantics", () => {
  const project = temporaryProject();
  try {
    const baseline = buildMintedProjectViews(project.root);
    writeFileSync(resolve(project.root, "SPEC.md"), "# Hand-authored replacement\n");
    assert.equal(buildMintedProjectViews(project.root).markdownBytes, baseline.markdownBytes);

    const playerPath = resolve(project.root, "specs/key-and-door/nodes/player.json");
    const player = json(playerPath);
    delete player.intent;
    writeJson(playerPath, player);
    writeFileSync(resolve(project.root, "SPEC.md"), "Player intent exists only here.\n");
    assert.throws(
      () => buildMintedProjectViews(project.root),
      (error: unknown) =>
        error instanceof MintedProjectCompilerError && error.code === "NODE_SCHEMA_INVALID",
    );
  } finally {
    project.cleanup();
  }
});
