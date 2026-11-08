import assert from "node:assert/strict";
import {chmodSync, mkdirSync, mkdtempSync, rmSync, writeFileSync} from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";
import test from "node:test";
import {packageRoot, resolveNodeTool, resolveRustTool} from "../scripts/run-toolchain.mjs";

const runner = path.join(packageRoot, "scripts/run-toolchain.mjs");
function temporary(t: {after(fn: () => void): void}): string {
  const root = mkdtempSync(path.join(os.tmpdir(), "alch-o01-toolchain-"));
  t.after(() => rmSync(root, {recursive: true, force: true}));
  return root;
}

test("package-local tsc and tsx resolve to their exact package-lock bin targets", () => {
  for (const tool of ["tsc", "tsx"] as const) {
    const identity = resolveNodeTool(tool);
    assert.equal(identity.source, "package-lock");
    assert.equal(identity.lock_path, path.join(packageRoot, "package-lock.json"));
    assert.ok(identity.real_executable.startsWith(path.join(packageRoot, "node_modules") + path.sep));
    assert.ok(identity.lock_package.startsWith("node_modules/"));
    assert.ok(identity.package_version);
  }
});

test("Node tool resolution rejects a PATH-only compiler instead of using an ambient fallback", t => {
  const root = temporary(t), bin = path.join(root, "bin");
  mkdirSync(bin);
  const ambient = path.join(bin, "tsc");
  writeFileSync(ambient, "#!/bin/sh\necho ambient\n"); chmodSync(ambient, 0o755);
  const previous = process.env.PATH;
  process.env.PATH = `${bin}:${previous ?? ""}`;
  try { assert.throws(() => resolveNodeTool("tsc", root), /ALCHLANG_TOOLCHAIN_LOCK_MISSING/); }
  finally { process.env.PATH = previous; }
});

test("Cargo and rustc identities are version-bound to the repository Rust lock", () => {
  for (const tool of ["cargo", "rustc"] as const) {
    const identity = resolveRustTool(tool);
    assert.equal(identity.expected_version, "1.98.1");
    assert.equal(identity.observed_version, identity.expected_version);
    assert.ok(["explicit-version-bound", "repository-lock-launcher"].includes(identity.source));
  }
});

test("an explicit executable with a non-Cargo identity fails closed", () => {
  assert.throws(() => resolveRustTool("cargo", {...process.env, ALCHLANG_CARGO: process.execPath}), /ALCHLANG_RUST_TOOL_VERSION/);
});

test("the command wrapper reports four declared identities without ambient Node tools", () => {
  const run = spawnSync(process.execPath, [runner, "--identity-all"], {encoding: "utf8", env: {...process.env, PATH: "/usr/bin:/bin"}});
  assert.equal(run.status, 0, run.stderr);
  const identities = JSON.parse(run.stdout);
  assert.deepEqual(identities.map((item: any) => item.tool), ["tsc", "tsx", "cargo", "rustc"]);
  assert.deepEqual(identities.map((item: any) => item.family), ["node", "node", "rust", "rust"]);
});
