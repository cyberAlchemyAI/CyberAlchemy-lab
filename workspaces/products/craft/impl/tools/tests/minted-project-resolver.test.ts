import assert from "node:assert/strict";
import {
  cpSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  MintedProjectResolverError,
  resolveMintedProjectSources,
} from "../minted-project/resolver";

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
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-minted-resolver-"));
  cpSync(fixtureRoot, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { force: true, recursive: true }) };
}

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error: unknown) => {
    assert.ok(error instanceof MintedProjectResolverError);
    assert.equal(error.code, code);
    assert.match(error.message, new RegExp(`^${code}:`));
    return true;
  });
}

test("Key and Door resolves to the expected ordered source set deterministically", () => {
  const expectedManifest = json(resolve(fixtureRoot, "expected/source-manifest.json"));
  const first = resolveMintedProjectSources(fixtureRoot);
  const second = resolveMintedProjectSources(fixtureRoot);

  assert.deepEqual(first, second);
  assert.deepEqual(first.records, expectedManifest.inputs);
  assert.equal(first.sourceSetDigest, expectedManifest.source_set_digest);
  assert.equal(first.projectPath, "project.json");
});

test("empty project and feature source arrays resolve without inventing semantics", () => {
  const featureless = temporaryProject();
  try {
    const project = json(resolve(featureless.root, "project.json"));
    project.features = [];
    writeJson(resolve(featureless.root, "project.json"), project);
    const resolution = resolveMintedProjectSources(featureless.root);
    assert.deepEqual(resolution.records.map((record) => record.path), ["project.json"]);
  } finally {
    featureless.cleanup();
  }

  const nodeless = temporaryProject();
  try {
    const featurePath = resolve(nodeless.root, "specs/key-and-door/feature.json");
    const feature = json(featurePath);
    feature.node_sources = [];
    writeJson(featurePath, feature);
    const resolution = resolveMintedProjectSources(nodeless.root);
    assert.deepEqual(
      resolution.records.map((record) => record.path),
      ["project.json", "specs/key-and-door/feature.json"],
    );
  } finally {
    nodeless.cleanup();
  }
});

test("absolute and parent-escaping references fail before filesystem discovery", () => {
  const absolute = temporaryProject();
  try {
    const project = json(resolve(absolute.root, "project.json"));
    project.features = [resolve(absolute.root, "outside.json")];
    writeJson(resolve(absolute.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(absolute.root), "SOURCE_PATH_ABSOLUTE");
  } finally {
    absolute.cleanup();
  }

  const escaping = temporaryProject();
  try {
    const project = json(resolve(escaping.root, "project.json"));
    project.features = ["../outside.json"];
    writeJson(resolve(escaping.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(escaping.root), "SOURCE_PATH_ESCAPE");
  } finally {
    escaping.cleanup();
  }
});

test("missing, non-file, and unsupported-extension sources fail distinctly", () => {
  const missing = temporaryProject();
  try {
    const project = json(resolve(missing.root, "project.json"));
    project.features = ["missing.json"];
    writeJson(resolve(missing.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(missing.root), "SOURCE_MISSING");
  } finally {
    missing.cleanup();
  }

  const directory = temporaryProject();
  try {
    mkdirSync(resolve(directory.root, "directory.json"));
    const project = json(resolve(directory.root, "project.json"));
    project.features = ["directory.json"];
    writeJson(resolve(directory.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(directory.root), "SOURCE_NOT_FILE");
  } finally {
    directory.cleanup();
  }

  const extension = temporaryProject();
  try {
    writeFileSync(resolve(extension.root, "feature.yml"), "schema_version: minted-feature/v1\n");
    const project = json(resolve(extension.root, "project.json"));
    project.features = ["feature.yml"];
    writeJson(resolve(extension.root, "project.json"), project);
    expectCode(
      () => resolveMintedProjectSources(extension.root),
      "SOURCE_EXTENSION_UNSUPPORTED",
    );
  } finally {
    extension.cleanup();
  }
});

test("duplicate, case-colliding, and real-path alias sources fail distinctly", () => {
  const duplicate = temporaryProject();
  try {
    const project = json(resolve(duplicate.root, "project.json"));
    project.features = [project.features[0], project.features[0]];
    writeJson(resolve(duplicate.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(duplicate.root), "SOURCE_PATH_DUPLICATE");
  } finally {
    duplicate.cleanup();
  }

  const collision = temporaryProject();
  try {
    writeJson(resolve(collision.root, "A.json"), {
      schema_version: "minted-feature/v1",
      node_sources: ["specs/key-and-door/nodes/player.json"],
    });
    writeJson(resolve(collision.root, "a.json"), {
      schema_version: "minted-feature/v1",
      node_sources: ["specs/key-and-door/nodes/door-unlocked.json"],
    });
    const project = json(resolve(collision.root, "project.json"));
    project.features = ["A.json", "a.json"];
    writeJson(resolve(collision.root, "project.json"), project);
    expectCode(
      () => resolveMintedProjectSources(collision.root),
      "SOURCE_PATH_CASE_COLLISION",
    );
  } finally {
    collision.cleanup();
  }

  const alias = temporaryProject();
  try {
    symlinkSync("specs/key-and-door/feature.json", resolve(alias.root, "feature-alias.json"));
    const project = json(resolve(alias.root, "project.json"));
    project.features = ["specs/key-and-door/feature.json", "feature-alias.json"];
    writeJson(resolve(alias.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(alias.root), "SOURCE_PATH_ALIAS");
  } finally {
    alias.cleanup();
  }
});

test("a project-local symlink to an external source fails containment", () => {
  const project = temporaryProject();
  const outside = mkdtempSync(resolve(tmpdir(), "domainspec-minted-outside-"));
  try {
    writeJson(resolve(outside, "feature.json"), {
      schema_version: "minted-feature/v1",
      node_sources: ["node.json"],
    });
    symlinkSync(resolve(outside, "feature.json"), resolve(project.root, "external.json"));
    const manifest = json(resolve(project.root, "project.json"));
    manifest.features = ["external.json"];
    writeJson(resolve(project.root, "project.json"), manifest);
    expectCode(
      () => resolveMintedProjectSources(project.root),
      "SOURCE_PATH_SYMLINK_ESCAPE",
    );
  } finally {
    project.cleanup();
    rmSync(outside, { force: true, recursive: true });
  }
});

test("invalid JSON, unsupported versions, and missing discovery fields fail distinctly", () => {
  const invalid = temporaryProject();
  try {
    writeFileSync(resolve(invalid.root, "project.json"), "{not-json}\n");
    expectCode(() => resolveMintedProjectSources(invalid.root), "SOURCE_JSON_INVALID");
  } finally {
    invalid.cleanup();
  }

  const version = temporaryProject();
  try {
    const project = json(resolve(version.root, "project.json"));
    project.schema_version = "minted-project/v2";
    writeJson(resolve(version.root, "project.json"), project);
    expectCode(
      () => resolveMintedProjectSources(version.root),
      "SOURCE_VERSION_UNSUPPORTED",
    );
  } finally {
    version.cleanup();
  }

  const shape = temporaryProject();
  try {
    const project = json(resolve(shape.root, "project.json"));
    delete project.features;
    writeJson(resolve(shape.root, "project.json"), project);
    expectCode(() => resolveMintedProjectSources(shape.root), "SOURCE_SHAPE_INVALID");
  } finally {
    shape.cleanup();
  }
});
