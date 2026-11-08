import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  SyntheticCorpusError,
  UI_SYNTHETIC_FIXTURE_CLASSES,
  validateSyntheticCorpus,
} from "../lib/ui-profile-synthetic";
import { parseUiProfile } from "../validate-ui-profile";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const fixtureRoot = resolve(implRoot, "spec/ui-profile/fixtures/create-player");
const schemaRoot = resolve(implRoot, "spec/meta-types/ui");
const profile = parseUiProfile(
  readFileSync(resolve(implRoot, "spec/ui-profile/profile.yml"), "utf8"),
);

function temporaryCorpus(): { root: string; cleanup: () => void } {
  const root = mkdtempSync(join(tmpdir(), "domainspec-ui-synthetic-"));
  cpSync(fixtureRoot, root, { recursive: true });
  return { root, cleanup: () => rmSync(root, { recursive: true, force: true }) };
}

function json(path: string): any {
  return JSON.parse(readFileSync(path, "utf8"));
}

function writeJson(path: string, value: unknown): void {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function expectCode(run: () => unknown, code: string): void {
  assert.throws(run, (error: unknown) => {
    assert.ok(error instanceof SyntheticCorpusError);
    assert.equal(error.code, code);
    return true;
  });
}

test("Create Player corpus closes the exact 11 by 6 matrix with stable outcomes", () => {
  const first = validateSyntheticCorpus(fixtureRoot, profile, schemaRoot);
  const second = validateSyntheticCorpus(fixtureRoot, profile, schemaRoot);
  assert.equal(first.concepts, 11);
  assert.equal(first.fixture_classes, 6);
  assert.equal(first.cells, 66);
  assert.equal(first.accepted, 22);
  assert.equal(first.rejected, 44);
  assert.equal(first.mismatches, 0);
  assert.equal(first.digest, second.digest);
  assert.match(first.digest, /^[a-f0-9]{64}$/);
  for (const fixtureClass of UI_SYNTHETIC_FIXTURE_CLASSES) {
    assert.equal(
      first.matrix.filter((cell) => cell.fixture_class === fixtureClass).length,
      11,
      fixtureClass,
    );
  }
  assert.equal(
    first.matrix.filter((cell) => cell.fixture_class === "label-erased" && cell.actual === "accept").length,
    11,
  );
});

test("CLI reports synthetic provenance, census, and digest", () => {
  const result = spawnSync(
    process.execPath,
    [
      "--import",
      "tsx",
      "tools/validate-ui-profile.ts",
      "--profile",
      "spec/ui-profile/profile.yml",
      "--fixtures",
      "spec/ui-profile/fixtures/create-player",
    ],
    { cwd: implRoot, encoding: "utf8" },
  );
  assert.equal(result.status, 0, result.stdout + result.stderr);
  const output = JSON.parse(result.stdout) as any;
  assert.equal(output.status, "PASS");
  assert.equal(output.synthetic.corpus_kind, "synthetic-calibration");
  assert.equal(output.synthetic.cells, 66);
  assert.equal(output.synthetic.mismatches, 0);
});

test("a missing fixture class fails the closed matrix", () => {
  const corpus = temporaryCorpus();
  try {
    const path = join(corpus.root, "page.json");
    const page = json(path);
    page.cases.pop();
    writeJson(path, page);
    expectCode(
      () => validateSyntheticCorpus(corpus.root, profile, schemaRoot),
      "SYNTHETIC-CLASS-MISSING",
    );
  } finally {
    corpus.cleanup();
  }
});

test("case identities cannot be pooled between concepts", () => {
  const corpus = temporaryCorpus();
  try {
    const path = join(corpus.root, "layout.json");
    const layout = json(path);
    layout.cases[0].case_id = "DS-D1.15.positive";
    writeJson(path, layout);
    expectCode(
      () => validateSyntheticCorpus(corpus.root, profile, schemaRoot),
      "SYNTHETIC-EVIDENCE-POOLING",
    );
  } finally {
    corpus.cleanup();
  }
});

test("real or independent provenance claims fail closed", () => {
  const corpus = temporaryCorpus();
  try {
    const path = join(corpus.root, "manifest.json");
    const manifest = json(path);
    manifest.corpus_kind = "real-corpus";
    writeJson(path, manifest);
    expectCode(
      () => validateSyntheticCorpus(corpus.root, profile, schemaRoot),
      "SYNTHETIC-PROVENANCE-INVALID",
    );
  } finally {
    corpus.cleanup();
  }
});

test("semantic fixture mutation cannot keep a preregistered pass", () => {
  const corpus = temporaryCorpus();
  try {
    const path = join(corpus.root, "binding.json");
    const binding = json(path);
    binding.cases[0].payload.attributes.mode = "";
    writeJson(path, binding);
    expectCode(
      () => validateSyntheticCorpus(corpus.root, profile, schemaRoot),
      "SYNTHETIC-EXPECTATION-MISMATCH",
    );
  } finally {
    corpus.cleanup();
  }
});
