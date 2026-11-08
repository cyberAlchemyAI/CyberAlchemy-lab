import { testTsx } from "./toolchain.js";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CompilationRejected, loadAlchLangSource } from "../src/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const canonical = path.join(root, "examples/typed-backend.alch");
const legacy = path.join(root, "examples/typed-backend.md");

test(".alch is the canonical plain source format", () => {
  const loaded = loadAlchLangSource(canonical);
  assert.equal(loaded.file_format, "canonical-alch");
  assert.equal(loaded.source_kind, "plain-alchlang");
  assert.equal((loaded.carrier.identity as any).domain_id, "typed-commerce");
});

test("legacy Markdown remains fenced and explicitly classified", () => {
  const loaded = loadAlchLangSource(legacy);
  assert.equal(loaded.file_format, "legacy-markdown");
  assert.equal(loaded.source_kind, "markdown-alchlang");
});

test("unsupported suffixes and fenced .alch files fail causally", t => {
  const directory = mkdtempSync(path.join(tmpdir(), "alchlang-source-"));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const text = "domain tiny \"Tiny\"\nowner tiny-owner\n";
  const wrong = path.join(directory, "tiny.txt"); writeFileSync(wrong, text);
  const uppercase = path.join(directory, "tiny.ALCH"); writeFileSync(uppercase, text);
  const fenced = path.join(directory, "tiny.alch"); writeFileSync(fenced, `\`\`\`alchlang\n${text}\`\`\`\n`);
  assert.throws(() => loadAlchLangSource(wrong), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "SOURCE_EXTENSION");
  assert.throws(() => loadAlchLangSource(uppercase), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "SOURCE_EXTENSION");
  assert.throws(() => loadAlchLangSource(fenced), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "SOURCE_CONTAINER");
});

test("domainspec check validates .alch without writing generated output", () => {
  const tsx = testTsx();
  const result = spawnSync(tsx, [path.join(root, "src/cli.ts"), "check", canonical, "--backend", "local-compat"], { cwd: root, encoding: "utf8", env: process.env });
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.equal(receipt.status, "valid");
  assert.equal(receipt.file_format, "canonical-alch");
  assert.equal(receipt.domain_id, "typed-commerce");
  assert.equal(receipt.authority_effect, "none");
  assert.match(result.stderr, /ALCH_LEGACY_DEFAULT/);
});

test("explicit compatibility CLI diagnoses the selected profile without changing its success receipt", t => {
  const directory = mkdtempSync(path.join(tmpdir(), "alchlang-compatibility-"));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const source = path.join(directory, "compat.alch");
  writeFileSync(source, 'domain inventory "Inventory"\nowner inventory-owner\nprofile legacy-sfol-v1\nentity Item:\n  quantity: integer required\nrule Available:\n  quantity > 0\n');
  const result = spawnSync(testTsx(), [path.join(root, "src/cli.ts"), "check", source, "--backend", "local-compat"], { cwd: root, encoding: "utf8", env: process.env });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).status, "valid");
  assert.match(result.stderr, /ALCH_LEGACY_COMPATIBILITY/);
  writeFileSync(source, 'domain inventory "Inventory"\nowner inventory-owner\nprofile application-v1\n');
  const target = spawnSync(testTsx(), [path.join(root, "src/cli.ts"), "check", source, "--backend", "local-compat"], { cwd: root, encoding: "utf8", env: process.env });
  assert.notEqual(target.status, 0);
  assert.doesNotMatch(target.stderr, /ALCH_LEGACY_DEFAULT|ALCH_LEGACY_COMPATIBILITY/);
});
