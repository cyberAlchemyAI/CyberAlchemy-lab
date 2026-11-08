import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { ProjectRootError, resolveProjectRoot } from "../../src/input/project-root.ts";
import { SourceManifestError, canonicalJson, sha256, validateSourceManifest } from "../../src/input/source-manifest.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");
const sourceManifestSchema = JSON.parse(
  fs.readFileSync(path.resolve(testDir, "../../contracts/source-manifest.schema.json"), "utf8")
) as {
  additionalProperties: boolean;
  properties: {
    project_id: {pattern: string};
    sources: {items: {additionalProperties: boolean; properties: {feature_id: {oneOf: Array<{pattern?: string}>}; relative_path: {pattern: string}}}};
  };
};

function createRoot(): string {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "sfc-project-root-"));
  fs.cpSync(fixtureRoot, root, { recursive: true });
  return root;
}

function removeRoot(root: string): void {
  const expectedPrefix = path.join(os.tmpdir(), "sfc-project-root-");
  assert.equal(root.startsWith(expectedPrefix), true);
  fs.rmSync(root, { recursive: true, force: true });
}

function writeJson(root: string, relativePath: string, value: unknown): void {
  fs.writeFileSync(path.join(root, relativePath), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function readJson(root: string, relativePath: string): Record<string, unknown> {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8")) as Record<string, unknown>;
}

function snapshot(root: string): string {
  const rows: string[] = [];
  const walk = (directory: string): void => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const absolute = path.join(directory, entry.name);
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile()) {
        const relative = path.relative(root, absolute).split(path.sep).join("/");
        const bytes = fs.readFileSync(absolute);
        rows.push(`${relative}\t${bytes.length}\t${crypto.createHash("sha256").update(bytes).digest("hex")}\n`);
      }
    }
  };
  walk(root);
  return crypto.createHash("sha256").update(rows.join("")).digest("hex");
}

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error) => error instanceof ProjectRootError && error.code === code && error.exitCode === 22);
}

function resealManifest(manifest: ReturnType<typeof resolveProjectRoot>): ReturnType<typeof resolveProjectRoot> {
  const mutable = structuredClone(manifest) as unknown as {
    source_count: number;
    total_size_bytes: number;
    sources: Array<{source_type: string; source_id: string; feature_id: string | null; relative_path: string; size_bytes: number; sha256: string}>;
    aggregate_sha256: string;
    manifest_sha256: string;
    [key: string]: unknown;
  };
  mutable.source_count = mutable.sources.length;
  mutable.total_size_bytes = mutable.sources.reduce((total, source) => total + source.size_bytes, 0);
  mutable.aggregate_sha256 = sha256(mutable.sources.map((source) =>
    `${source.source_type}\t${source.source_id}\t${source.feature_id ?? "-"}\t${source.relative_path}\t${source.size_bytes}\t${source.sha256}\n`
  ).join(""));
  const { manifest_sha256: ignored, ...body } = mutable;
  mutable.manifest_sha256 = sha256(canonicalJson(body));
  return mutable as unknown as ReturnType<typeof resolveProjectRoot>;
}

test("byte-identical arbitrary roots produce one normalized manifest", () => {
  const left = createRoot();
  const right = createRoot();
  try {
    const leftManifest = resolveProjectRoot(left);
    const rightManifest = resolveProjectRoot(right);
    assert.deepEqual(validateSourceManifest(leftManifest), leftManifest);
    assert.deepEqual(leftManifest, rightManifest);
    assert.equal(leftManifest.source_count, 21);
    assert.equal(leftManifest.authority_effect, "none");
    assert.deepEqual([...leftManifest.sources].map((source) => source.relative_path), [...leftManifest.sources].map((source) => source.relative_path).sort());
  } finally {
    removeRoot(left);
    removeRoot(right);
  }
});

test("closed source manifest rejects surplus members and stale digests", () => {
  const root = createRoot();
  try {
    const manifest = resolveProjectRoot(root);
    assert.throws(
      () => validateSourceManifest({ ...manifest, extension_bag: {} }),
      (error) => error instanceof SourceManifestError && error.code === "SFC_SOURCE_MANIFEST_SCHEMA"
    );
    assert.throws(
      () => validateSourceManifest({ ...manifest, aggregate_sha256: "0".repeat(64) }),
      (error) => error instanceof SourceManifestError && error.code === "SFC_SOURCE_MANIFEST_DIGEST"
    );
  } finally {
    removeRoot(root);
  }
});

test("source manifest schema closes entries and canonical path grammar", () => {
  assert.equal(sourceManifestSchema.additionalProperties, false);
  assert.equal(sourceManifestSchema.properties.sources.items.additionalProperties, false);
  const projectId = new RegExp(sourceManifestSchema.properties.project_id.pattern);
  assert.equal(projectId.test("demo-project"), true);
  assert.equal(projectId.test("../escape"), false);
  const featureId = new RegExp(sourceManifestSchema.properties.sources.items.properties.feature_id.oneOf[0]?.pattern ?? "");
  assert.equal(featureId.test("alpha"), true);
  assert.equal(featureId.test(""), false);
  const relativePath = new RegExp(sourceManifestSchema.properties.sources.items.properties.relative_path.pattern);
  for (const acceptedPath of ["project.json", "edges/alpha-to-beta.json", "specs/alpha/feature.json", "specs/alpha/nodes/customer.json", "specs/alpha/edges/customer-performs-settle.json"]) {
    assert.equal(relativePath.test(acceptedPath), true, acceptedPath);
  }
  for (const rejectedPath of [".", "a/./b", "a//b", "../escape", "/project.json", "specs\\alpha\\feature.json"]) {
    assert.equal(relativePath.test(rejectedPath), false, rejectedPath);
  }
});

test("resealed noncanonical manifest identities and paths fail closed", () => {
  const root = createRoot();
  try {
    const manifest = resolveProjectRoot(root);
    const invalidProject = structuredClone(manifest);
    (invalidProject as {project_id: string}).project_id = "../escape";
    assert.throws(
      () => validateSourceManifest(resealManifest(invalidProject)),
      (error) => error instanceof SourceManifestError && error.code === "SFC_SOURCE_MANIFEST_IDENTITY"
    );

    for (const relativePath of [".", "a/./b", "a//b"]) {
      const invalidPath = structuredClone(manifest);
      (invalidPath.sources[0] as {relative_path: string}).relative_path = relativePath;
      assert.throws(
        () => validateSourceManifest(resealManifest(invalidPath)),
        (error) => error instanceof SourceManifestError && error.code === "SFC_SOURCE_MANIFEST_PATH"
      );
    }

    const invalidFeature = structuredClone(manifest);
    const feature = invalidFeature.sources.find((source) => source.source_type === "feature");
    assert.ok(feature);
    (feature as {feature_id: string}).feature_id = "";
    assert.throws(
      () => validateSourceManifest(resealManifest(invalidFeature)),
      (error) => error instanceof SourceManifestError && error.code === "SFC_SOURCE_MANIFEST_IDENTITY"
    );

    const mismatchedNode = structuredClone(manifest);
    const node = mismatchedNode.sources.find((source) => source.source_type === "node");
    assert.ok(node);
    (node as {source_id: string}).source_id = "beta:customer";
    assert.throws(
      () => validateSourceManifest(resealManifest(mismatchedNode)),
      (error) => error instanceof SourceManifestError && ["SFC_SOURCE_MANIFEST_IDENTITY", "SFC_SOURCE_MANIFEST_PATH"].includes(error.code)
    );
  } finally {
    removeRoot(root);
  }
});

test("resolver performs no project writes", () => {
  const root = createRoot();
  try {
    const before = snapshot(root);
    resolveProjectRoot(root);
    assert.equal(snapshot(root), before);
  } finally {
    removeRoot(root);
  }
});

test("missing, relative, feature-only, and cwd-like roots fail without fallback", () => {
  expectCode(() => resolveProjectRoot(undefined), "SFC_INPUT_EXPLICIT_ROOT_REQUIRED");
  expectCode(() => resolveProjectRoot("canonical-project"), "SFC_INPUT_EXPLICIT_ROOT_REQUIRED");
  expectCode(() => resolveProjectRoot(path.join(os.tmpdir(), "missing-sfc-root")), "SFC_INPUT_ROOT_MISSING");
  const root = createRoot();
  try {
    expectCode(() => resolveProjectRoot(path.join(root, "specs/alpha")), "SFC_INPUT_MISSING");
  } finally {
    removeRoot(root);
  }
});

test("symbolic project roots and symbolic declared sources fail", () => {
  const root = createRoot();
  const componentRoot = createRoot();
  const link = `${root}-link`;
  try {
    fs.symlinkSync(root, link, "dir");
    expectCode(() => resolveProjectRoot(link), "SFC_INPUT_SYMLINK");
    expectCode(() => resolveProjectRoot(`${link}${path.sep}`), "SFC_INPUT_SYMLINK");
    const nodePath = path.join(root, "specs/alpha/nodes/customer.json");
    fs.rmSync(nodePath);
    fs.symlinkSync("settle.json", nodePath);
    expectCode(() => resolveProjectRoot(root), "SFC_INPUT_SYMLINK");

    const nodesPath = path.join(componentRoot, "specs/alpha/nodes");
    const realNodesPath = path.join(componentRoot, "specs/alpha/nodes-real");
    fs.renameSync(nodesPath, realNodesPath);
    fs.symlinkSync("nodes-real", nodesPath, "dir");
    expectCode(() => resolveProjectRoot(componentRoot), "SFC_INPUT_SYMLINK");
  } finally {
    if (fs.existsSync(link) || fs.lstatSync(link, { throwIfNoEntry: false })?.isSymbolicLink()) fs.rmSync(link, { force: true });
    removeRoot(root);
    removeRoot(componentRoot);
  }
});

test("duplicate and path-escape identifiers fail", () => {
  const duplicate = createRoot();
  const escape = createRoot();
  try {
    const duplicateProject = readJson(duplicate, "project.json");
    duplicateProject.features = ["alpha", "alpha"];
    writeJson(duplicate, "project.json", duplicateProject);
    expectCode(() => resolveProjectRoot(duplicate), "SFC_INPUT_DUPLICATE");

    const escapeProject = readJson(escape, "project.json");
    escapeProject.features = ["alpha", "../beta"];
    writeJson(escape, "project.json", escapeProject);
    expectCode(() => resolveProjectRoot(escape), "SFC_INPUT_ID");
  } finally {
    removeRoot(duplicate);
    removeRoot(escape);
  }
});

test("wrong-root identities and endpoints fail", () => {
  const wrongRoot = createRoot();
  const wrongEndpoint = createRoot();
  const sameFeature = createRoot();
  try {
    const feature = readJson(wrongRoot, "specs/alpha/feature.json");
    feature.feature_id = "beta";
    writeJson(wrongRoot, "specs/alpha/feature.json", feature);
    expectCode(() => resolveProjectRoot(wrongRoot), "SFC_INPUT_WRONG_ROOT");

    const edge = readJson(wrongEndpoint, "edges/alpha-to-beta.json");
    edge.target_node_id = "missing";
    writeJson(wrongEndpoint, "edges/alpha-to-beta.json", edge);
    expectCode(() => resolveProjectRoot(wrongEndpoint), "SFC_INPUT_ENDPOINT");

    const sameFeatureEdge = readJson(sameFeature, "edges/alpha-to-beta.json");
    sameFeatureEdge.target_feature_id = "beta";
    sameFeatureEdge.target_node_id = "audit";
    writeJson(sameFeature, "edges/alpha-to-beta.json", sameFeatureEdge);
    expectCode(() => resolveProjectRoot(sameFeature), "SFC_INPUT_ENDPOINT");
  } finally {
    removeRoot(wrongRoot);
    removeRoot(wrongEndpoint);
    removeRoot(sameFeature);
  }
});
