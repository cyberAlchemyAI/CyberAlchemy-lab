import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { relative, resolve } from "node:path";
import test from "node:test";

import {
  MintedProjectMinterError,
  mintMintedProject,
  type MintedProjectMintOptions,
} from "../minted-project/minter";
import { buildMintedProjectViews } from "../minted-project/views";

type JsonObject = Record<string, any>;

function json(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function filesBelow(root: string): string[] {
  const visit = (directory: string): string[] => readdirSync(directory, { withFileTypes: true })
    .flatMap((entry) => {
      const path = resolve(directory, entry.name);
      return entry.isDirectory() ? visit(path) : [relative(root, path).replaceAll("\\", "/")];
    });
  return visit(root).sort();
}

function treeDigest(root: string): string {
  const hash = createHash("sha256");
  for (const path of filesBelow(root)) {
    hash.update(path);
    hash.update("\0");
    hash.update(readFileSync(resolve(root, path)));
    hash.update("\0");
  }
  return hash.digest("hex");
}

function expectCode(action: () => unknown, code: string): void {
  assert.throws(action, (error: unknown) => {
    assert.ok(error instanceof MintedProjectMinterError);
    assert.equal(error.code, code);
    return true;
  });
}

function temporaryParent(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(resolve(tmpdir(), "domainspec-minted-minter-"));
  return { root, cleanup: () => rmSync(root, { force: true, recursive: true }) };
}

test("clean mints are example-free, deterministic, and immediately rebuildable", () => {
  const parent = temporaryParent();
  try {
    const first = mintMintedProject({
      destination: resolve(parent.root, "first"),
      projectId: "empty-world",
    });
    const second = mintMintedProject({
      destination: resolve(parent.root, "second"),
      projectId: "empty-world",
    });

    assert.deepEqual(first.receipt, second.receipt);
    assert.equal(treeDigest(first.projectRoot), treeDigest(second.projectRoot));
    assert.deepEqual(filesBelow(first.projectRoot), [
      ".domainspec/generated/SPEC.md",
      ".domainspec/generated/build-receipt.json",
      ".domainspec/generated/graph.json",
      ".domainspec/generated/markdown-view.json",
      ".domainspec/generated/source-manifest.json",
      "README.md",
      "project.json",
      "specs/.gitkeep",
    ]);
    const project = json(resolve(first.projectRoot, "project.json"));
    assert.deepEqual(project.features, []);
    assert.equal(project.generated_root, ".domainspec/generated");
    const rebuilt = buildMintedProjectViews(first.projectRoot);
    assert.equal(
      readFileSync(resolve(first.projectRoot, ".domainspec/generated/graph.json"), "utf8"),
      rebuilt.graphBytes,
    );
    assert.equal(
      readFileSync(resolve(first.projectRoot, ".domainspec/generated/build-receipt.json"), "utf8"),
      rebuilt.buildReceiptBytes,
    );
    assert.equal(first.receipt.schema_handles.length, 12);
    assert.deepEqual(first.receipt.tool_handles.map((handle) => handle.id), [
      "compiler",
      "minter",
      "views",
    ]);
  } finally {
    parent.cleanup();
  }
});

test("existing destinations are non-destructive and require explicit empty acceptance", () => {
  const parent = temporaryParent();
  try {
    const nonempty = resolve(parent.root, "nonempty");
    mkdirSync(nonempty);
    writeFileSync(resolve(nonempty, "owned.txt"), "preserve\n");
    expectCode(
      () => mintMintedProject({ destination: nonempty, projectId: "safe-project" }),
      "DESTINATION_NOT_EMPTY",
    );
    assert.equal(readFileSync(resolve(nonempty, "owned.txt"), "utf8"), "preserve\n");

    const empty = resolve(parent.root, "empty");
    mkdirSync(empty);
    expectCode(
      () => mintMintedProject({ destination: empty, projectId: "safe-project" }),
      "DESTINATION_EXISTS",
    );
    const result = mintMintedProject({
      destination: empty,
      projectId: "safe-project",
      acceptExistingEmpty: true,
    });
    assert.equal(result.projectRoot, empty);
    assert.ok(existsSync(resolve(empty, "project.json")));
  } finally {
    parent.cleanup();
  }
});

test("generated roots reject absolute, traversal, source overlap, and project-root output", () => {
  const parent = temporaryParent();
  try {
    const cases: Array<[string, string]> = [
      ["/tmp/out", "GENERATED_ROOT_INVALID"],
      ["../out", "GENERATED_ROOT_ESCAPE"],
      ["specs/generated", "GENERATED_ROOT_CONFLICT"],
      [".", "GENERATED_ROOT_ESCAPE"],
    ];
    for (const [index, [generatedRoot, code]] of cases.entries()) {
      const destination = resolve(parent.root, `case-${index}`);
      const options: MintedProjectMintOptions = {
        destination,
        projectId: "bounded-project",
        generatedRoot,
      };
      expectCode(() => mintMintedProject(options), code);
      assert.ok(!existsSync(destination));
    }
  } finally {
    parent.cleanup();
  }
});

test("staging leakage and interruption roll back without partial authority", () => {
  const parent = temporaryParent();
  try {
    const leaked = resolve(parent.root, "leaked");
    expectCode(
      () => mintMintedProject(
        { destination: leaked, projectId: "clean-project" },
        {
          afterStageWrite: (stagingRoot) => {
            writeFileSync(resolve(stagingRoot, "leak.txt"), "financial-settlement\n");
          },
        },
      ),
      "LEAKAGE_DETECTED",
    );
    assert.ok(!existsSync(leaked));

    const interrupted = resolve(parent.root, "interrupted");
    expectCode(
      () => mintMintedProject(
        { destination: interrupted, projectId: "clean-project" },
        { afterStageWrite: () => { throw new Error("simulated interruption"); } },
      ),
      "MINT_FAILED",
    );
    assert.ok(!existsSync(interrupted));
    assert.deepEqual(
      readdirSync(parent.root).filter((name) => name.includes(".staging-")),
      [],
    );
  } finally {
    parent.cleanup();
  }
});

test("invalid identity and unsupported language fail before destination creation", () => {
  const parent = temporaryParent();
  try {
    expectCode(
      () => mintMintedProject({
        destination: resolve(parent.root, "bad-id"),
        projectId: "Bad Project",
      }),
      "PROJECT_ID_INVALID",
    );
    expectCode(
      () => mintMintedProject({
        destination: resolve(parent.root, "bad-language"),
        projectId: "good-project",
        profile: { id: "unknown", version: "9" },
      }),
      "LANGUAGE_UNSUPPORTED",
    );
    assert.deepEqual(readdirSync(parent.root), []);
  } finally {
    parent.cleanup();
  }
});

test("emitted bytes contain no fixture IDs, private-spine terms, or checkout paths", () => {
  const parent = temporaryParent();
  try {
    const result = mintMintedProject({
      destination: resolve(parent.root, "leakage-scan"),
      projectId: "clean-project",
    });
    const content = filesBelow(result.projectRoot)
      .map((path) => readFileSync(resolve(result.projectRoot, path), "utf8").toLowerCase())
      .join("\n");
    for (const forbidden of [
      "key-and-door",
      "financial-settlement",
      "agent-execution-orchestrator",
      "domainspec-core",
      "cyberalchemy-v2",
      "authority spine",
      "three pillars",
      "saturn",
      "/home/",
    ]) {
      assert.ok(!content.includes(forbidden), forbidden);
    }
  } finally {
    parent.cleanup();
  }
});
