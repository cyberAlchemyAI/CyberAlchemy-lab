import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { checkPackageBoundaries, readPackageBoundaries, validatePackageBoundaries } from "../scripts/materialize-package-boundaries.mjs";
import { packRelease, releasePlan } from "../scripts/package-release.mjs";

const root = path.resolve(import.meta.dirname, "..");

test("P01 committed package boundaries bind exact AlchLang and DomainSpec inventories", () => {
  const value = checkPackageBoundaries();
  assert.deepEqual(value.packages.map((item: any) => item.id), ["core", "rust", "local-host"]);
  assert.deepEqual(value.packages.map((item: any) => item.name), ["@cyberalchemy/alchlang", "@cyberalchemy/alchlang-rust", "@cyberalchemy/alchlang-local-host"]);
  assert.equal(value.domainspec_cli.name, "@domainspec-v2/cli"); assert.equal(value.domainspec_cli.version, "1.3.0");
  assert.ok(value.domainspec_cli.expanded_files.includes("contracts/compiled-application-graph-v1.schema.json"));
  assert.ok(value.domainspec_cli.expanded_files.includes("examples/reconciled-commerce/README.md"));
  assert.deepEqual(value.domainspec_cli.candidate_archive_files,
    [...new Set([...value.domainspec_cli.expanded_files,
      ...value.domainspec_cli.candidate_archive_generated_files.map((row: any) => row.path)])].sort());
  assert.deepEqual(value.domainspec_cli.candidate_archive_generated_files.map((row: any) => row.transform),
    ["byte-copy", "strip-typescript-and-rebind-src-to-dist", "strip-typescript-and-rebind-src-to-dist"]);
  assert.equal(value.exclusions.publication, false); assert.equal(value.exclusions.authority_effect, "none");
});

test("P01 allowlists expose only current files and every export or command target is included", () => {
  const value = readPackageBoundaries();
  for (const item of value.packages) {
    assert.equal(item.files.length, new Set(item.files).size, item.id);
    for (const file of item.files.filter((entry: string) => !["package.json", "README.md"].includes(entry))) {
      assert.equal(fs.statSync(path.join(root, file)).isFile(), true, `${item.id}:${file}`);
      assert.doesNotMatch(file, /^(?:src|test|scripts|node_modules|docs-app|package-artifacts|generated)(?:\/|$)/u);
    }
    for (const target of Object.values(item.bin) as string[]) assert.ok(item.files.includes(target), `${item.id}:${target}`);
    for (const target of Object.values(item.exports).flatMap((entry: any) => typeof entry === "string" ? [entry] : Object.values(entry)) as string[]) {
      assert.ok(item.files.includes(target.replace(/^\.\//u, "")), `${item.id}:${target}`);
    }
  }
  for (const declaration of fs.readdirSync(path.join(root, "dist")).filter(file => file.endsWith(".d.ts"))) {
    const bytes = fs.readFileSync(path.join(root, "dist", declaration), "utf8");
    assert.doesNotMatch(bytes, /from\s+["'][.]{2}\//u, declaration); assert.doesNotMatch(bytes, /craft\/projects|language\/capabilities/u, declaration);
  }
});

test("P01 boundary validation rejects drift, development residue, checkout imports and effect growth", () => {
  const original = readPackageBoundaries();
  for (const mutate of [
    (value: any) => { value.packages[0].files.push("src/parser.ts"); value.packages[0].files.sort(); },
    (value: any) => { value.packages[1].checkout_only_imports_allowed = true; },
    (value: any) => { value.packages[2].exports["."].import = "./dist/missing.js"; },
    (value: any) => { value.exclusions.publication = true; },
    (value: any) => { value.domainspec_cli.candidate_archive_files.pop(); },
    (value: any) => { value.domainspec_cli.candidate_archive_generated_files[0].source = "src/foreign.ts"; },
  ]) {
    const changed = structuredClone(original); mutate(changed); assert.throws(() => validatePackageBoundaries(changed), /PACKAGE_BOUNDARY_/u);
  }
});

test("P01 release plan preserves optional-layer separation and exact export maps", () => {
  const plan = releasePlan(); const [core, rust, host] = plan;
  assert.equal(core.id, "core"); assert.equal(core.omits_cargo_templates, true); assert.equal(core.exports["."].import, "./dist/index.js");
  assert.ok(core.omitted_modules.includes("rust-toolchain")); assert.ok(core.omitted_modules.includes("local-host"));
  assert.equal(rust.id, "rust"); assert.equal(rust.omits_cargo_templates, false); assert.equal(rust.exports["./conformance"].import, "./dist/conformance.js");
  assert.equal(host.status, "experimental-repository-bound"); assert.equal(host.checkout_only_imports_allowed, false);
});

test("P01 local archives exactly match committed allowlists without installing or publishing", () => {
  const output = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-p01-test-"));
  try {
    const result = packRelease(output); const boundary = readPackageBoundaries();
    assert.equal(result.schema_version, "alchlang.split-release/v2-candidate");
    assert.equal(result.publication_performed, false); assert.equal(result.installation_performed, false); assert.equal(result.authority_effect, "none");
    for (const artifact of result.artifacts) {
      const expected = boundary.packages.find((item: any) => item.id === artifact.id);
      assert.equal(artifact.file_count, expected.files.length, artifact.id); assert.equal(artifact.allowlist_sha256, expected.allowlist_sha256, artifact.id);
      assert.equal(fs.statSync(artifact.file).isFile(), true, artifact.id);
    }
  } finally { fs.rmSync(output, { recursive: true, force: true }); }
});
