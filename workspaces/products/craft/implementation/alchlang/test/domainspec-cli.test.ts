import { testTsx } from "./toolchain.js";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { defaultDomainSpecPackageRoot, findDomainSpecPackageRoot, loadDomainSpecCompiler, runDomainSpecCli } from "../src/domainspec-cli.js";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const project = path.resolve(packageRoot, "../domainspec");
const upstream = defaultDomainSpecPackageRoot();
const fixture = path.join(upstream, "fixtures/input-roots/canonical-project");
const io = () => {
  const output = { stdout: "", stderr: "" };
  return { output, sink: { stdout(value: string) { output.stdout += value; }, stderr(value: string) { output.stderr += value; } } };
};
const temporary = (t: { after(fn: () => void): void }) => {
  const root = mkdtempSync(path.join(os.tmpdir(), "alchlang-domainspec-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return root;
};

test("installed compiler entry resolves its owning package without a checkout layout",(t)=>{
  const root=temporary(t),nested=path.join(root,'node_modules/@domainspec-v2/cli/dist/runtime');
  mkdirSync(nested,{recursive:true});
  writeFileSync(path.join(root,'node_modules/@domainspec-v2/cli/package.json'),JSON.stringify({name:'@domainspec-v2/cli',version:'1.0.0'}));
  assert.equal(findDomainSpecPackageRoot(path.join(nested,'index.js')),path.join(root,'node_modules/@domainspec-v2/cli'));
});

test("public 1.0.0 compiler validates a real project and certificate deterministically", async () => {
  const compiler = await loadDomainSpecCompiler(upstream);
  const first = compiler.compileProject(fixture);
  assert.deepEqual(compiler.compileProject(fixture), first);
  assert.ok(first.graph.nodes.length > 0);
  assert.ok(first.graph.relationships.length > 0);
  assert.equal(first.certificate.compiler.version, "1.0.0");
  assert.equal(first.certificate.authority_effect, "none");
});

test("delegated compile produces the upstream certificate and rejects overwrite", async (t) => {
  const target = path.join(temporary(t), "certificate.json");
  const capture = io();
  assert.equal(await runDomainSpecCli(["compile", fixture, "--target", target], capture.sink, upstream), 0);
  const bytes = readFileSync(target, "utf8");
  assert.deepEqual(JSON.parse(bytes), (await loadDomainSpecCompiler(upstream)).compileProject(fixture).certificate);
  assert.equal(JSON.parse(capture.output.stdout).result, "pass");
  const duplicate = io();
  assert.notEqual(await runDomainSpecCli(["compile", fixture, "--target", target], duplicate.sink, upstream), 0);
  assert.equal(JSON.parse(duplicate.output.stderr).code, "MTCLI_COMPILED_CERTIFICATE_EXISTS");
  assert.equal(readFileSync(target, "utf8"), bytes);
});

test("upstream input failures propagate without a passing result", async (t) => {
  const capture = io();
  assert.notEqual(await runDomainSpecCli(["lint", temporary(t)], capture.sink, upstream), 0);
  assert.equal(JSON.parse(capture.output.stderr).result, "fail");
  assert.equal(capture.output.stdout, "");
});

test("manifest mismatch is rejected before importing package code", async (t) => {
  const root = temporary(t);
  writeFileSync(path.join(root, "package.json"), JSON.stringify({ name: "@domainspec-v2/cli", version: "0.1.0" }));
  await assert.rejects(loadDomainSpecCompiler(root), /DOMAINSPEC_VERSION_MISMATCH/);
});

test("a 1.0.0 label cannot disguise a missing or stale build", async (t) => {
  const root = temporary(t);
  writeFileSync(path.join(root, "package.json"), JSON.stringify({ name: "@domainspec-v2/cli", version: "1.0.0", type: "module", exports: { ".": { import: "./index.js" } } }));
  await assert.rejects(loadDomainSpecCompiler(root), /DOMAINSPEC_BUILD_REQUIRED/);
  writeFileSync(path.join(root, "index.js"), 'export const CLI_PACKAGE_NAME = "@domainspec-v2/cli"; export const CLI_VERSION = "0.1.0";');
  await assert.rejects(loadDomainSpecCompiler(root), /DOMAINSPEC_BUILD_MISMATCH/);
});

test("experimental execution and recipe commands cannot enter the compiler bridge", async () => {
  for (const command of ["run", "add", "recipe-generate", "recipe-qualify"]) await assert.rejects(runDomainSpecCli([command]), /DOMAINSPEC_COMMAND_UNSUPPORTED/);
});

test("AlchLang CLI forwards version and nonzero upstream exit status from another directory", (t) => {
  const cwd = temporary(t);
  const tsx = testTsx();
  const run = (...args: string[]) => spawnSync(tsx, [path.join(packageRoot, "src/cli.ts"), "domainspec", ...args], { cwd, encoding: "utf8", env: { ...process.env, ALCHLANG_DOMAINSPEC_PACKAGE_ROOT: upstream } });
  const version = run("--version");
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), "1.0.0");
  const invalid = run("lint", cwd);
  assert.notEqual(invalid.status, 0);
  assert.match(invalid.stderr, /"result": "fail"/);
});

test("the old AlchLang model exposes its real 1.0.0 migration blocker", async () => {
  const compiler = await loadDomainSpecCompiler(upstream);
  assert.throws(() => compiler.compileProject(project), (error: unknown) => {
    const failure = error as { code: string; pointer: string };
    assert.equal(failure.code, "MTCLI_MAPPING_DIRECTION");
    assert.equal(failure.pointer, "/specs/typed-backend/nodes/typed-mapping.json/body/direction");
    return true;
  });
});
