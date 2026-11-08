import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { resolveDomainSpecPackageRoot, loadDomainSpecCompiler } from "../src/domainspec-cli.js";
import { testTsx } from "./toolchain.js";
import { parseDeclarativeSource } from "../src/declarative-profile.js";
import { deriveOntology } from "../src/derived-ontology.js";
import { buildDomainSpec } from "../src/domainspec-project-writer.js";
import { resolveTypeScriptCompiler } from "../src/function-builder.js";

const root = path.resolve(import.meta.dirname, "..");
const fixture = path.join(root, "examples/domainspec-order.alch");
function temporary(t: { after(fn: () => void): void }): string {
  const dir = mkdtempSync(path.join(os.tmpdir(), "alch-reconciliation-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

test("default and explicit DomainSpec builds share output; compatibility is explicit", t => {
  const dir = temporary(t);
  const run = (...args: string[]) => spawnSync(testTsx(), [path.join(root, "src/cli.ts"), ...args], { cwd: dir, encoding: "utf8" });
  for (const [name, options] of [["default", []], ["explicit", ["--backend", "domainspec"]]] as const) {
    const result = run("build", fixture, "--out", path.join(dir, name), ...options);
    assert.equal(result.status, 0, result.stderr);
  }
  assert.equal(readFileSync(path.join(dir, "default/manifest.json"), "utf8"), readFileSync(path.join(dir, "explicit/manifest.json"), "utf8"));
  assert.equal(run("check", fixture).status, 0);
  const localSource = path.join(root, "examples/typed-backend.alch");
  const unsupported = run("build", localSource, "--out", path.join(dir, "unsupported"));
  assert.notEqual(unsupported.status, 0);
  assert.equal(existsSync(path.join(dir, "unsupported")), false);
  const compat = run("check", localSource, "--backend", "local-compat");
  assert.equal(compat.status, 0, compat.stderr);
  assert.equal(JSON.parse(compat.stdout).domain_id, "typed-commerce");
  const localBuild = run("build", localSource, "--backend", "local-compat", "--out", path.join(dir, "local"));
  assert.equal(localBuild.status, 0, localBuild.stderr);
  assert.ok(existsSync(path.join(dir, "local/domain.graph.json")));
  for (const flags of [["--backend", "unknown"], ["--backend", "local-compat", "--profile", "domainspec-1.0.0"], ["--force"]]) {
    assert.notEqual(run("build", fixture, "--out", path.join(dir, "bad"), ...flags).status, 0);
    assert.equal(existsSync(path.join(dir, "bad")), false);
  }
});

test("compiler checkout binding selects Craft and legacy roots require an explicit binding", t => {
  const parent = temporary(t), checkout = path.join(parent, "cyberAlchemy-v2");
  const craft = path.join(checkout, "craft/projects/domainspec-v2/impl/cli");
  const sibling = path.join(parent, "domainspec-core/projects/domainspec-v2/impl/cli");
  assert.throws(() => resolveDomainSpecPackageRoot(checkout), /PACKAGE_MISSING/);
  mkdirSync(sibling, { recursive: true }); writeFileSync(path.join(sibling, "package.json"), "{}");
  assert.throws(() => resolveDomainSpecPackageRoot(checkout), /PACKAGE_MISSING/);
  mkdirSync(craft, { recursive: true }); writeFileSync(path.join(craft, "package.json"), "{}");
  assert.equal(resolveDomainSpecPackageRoot(checkout), craft);
  assert.equal(resolveDomainSpecPackageRoot(checkout, sibling), sibling);
  assert.throws(
    () => resolveTypeScriptCompiler(craft, undefined, path.join(parent, "compiler-without-toolchain")),
    /FUNCTION_TYPESCRIPT_COMPILER_MISSING/,
  );
  assert.throws(() => resolveTypeScriptCompiler(craft, path.join(parent, "tools/tsc")), /FUNCTION_TYPESCRIPT_COMPILER_MISSING/);
});

test("AlchLang uses the public shared-ontology adapter without mutating source evidence", async () => {
  const compiler = await loadDomainSpecCompiler();
  const input = { schema_version: "alchlang.derived-ontology/v1", source: { path: "example.alch", sha256: "source-digest" } };
  const before = structuredClone(input);
  const adapted = compiler.normalizeCompositionOntology(input);
  assert.equal(adapted.schema_version, "domainspec.composition-ontology/v1");
  assert.equal(adapted.source_format, "alchlang");
  assert.deepEqual(adapted.source, input.source);
  assert.deepEqual(input, before);
  assert.throws(() => compiler.normalizeCompositionOntology({ ...input, schema_version: "unknown" }), /unsupported ontology/);
});

test("AlchLang and direct JSON compositions use the same checked executable graph", async t => {
  const dir = temporary(t), compiler = await loadDomainSpecCompiler();
  const sourcePath = path.resolve(root, "../extensions/derived-ontology-v1/quantity-price.alch");
  const source = readFileSync(sourcePath, "utf8"), parsed = parseDeclarativeSource(source);
  const behavior = compiler.compileDeclarativeFunction(parsed.contract);
  const ontology = deriveOntology(parsed, behavior.trace, sourcePath);
  const core = path.join(dir, "core.alch");
  writeFileSync(core, parsed.coreSource);
  writeFileSync(core + ".domainspec.json", JSON.stringify(parsed.bindings));
  const bundle = path.join(dir, "bundle");
  await buildDomainSpec(core, bundle, { profile: "domainspec-1.0.0-exact-uint64-v1", generate: true,
    composition: { source_text: source, contract: parsed.contract, model: parsed.model, bindings: parsed.boundaryBindings, ontology } });
  const project = path.join(bundle, "project"), compositionPath = path.join(project, "compositions/function.json");
  const direct = JSON.parse(readFileSync(compositionPath, "utf8"));
  assert.equal(direct.ontology.schema_version, "domainspec.composition-ontology/v1");
  assert.equal(direct.ontology.source_format, "alchlang");
  const before = compiler.compileProject(project) as any;
  // A direct author supplies the same typed contracts with JSON provenance.
  const { createHash } = await import("node:crypto");
  direct.source_text = JSON.stringify(direct.contract, null, 2) + "\n";
  const location = { path: "contract.json", sha256: createHash("sha256").update(direct.source_text).digest("hex") };
  direct.ontology.source = location;
  direct.ontology.source_format = "domainspec-json";
  for (const node of direct.ontology.nodes) node.source = { ...location, line: 1 };
  for (const ref of direct.ontology.references) ref.evidence = { ...location, line: 1 };
  writeFileSync(compositionPath, JSON.stringify(direct));
  const after = compiler.compileProject(project) as any;
  assert.deepEqual(after.graph.nodes, before.graph.nodes);
  assert.deepEqual(after.graph.compositions[0].dependency_graph, before.graph.compositions[0].dependency_graph);
  assert.equal(after.graph.compositions[0].artifacts["behavior.mjs"], before.graph.compositions[0].artifacts["behavior.mjs"]);
  assert.notEqual(after.certificate.graph_sha256, before.certificate.graph_sha256);
  const target = path.join(dir, "direct");
  let error = "";
  assert.equal(compiler.runCli(["build", project, "--language", "typescript", "--realization-profile", "domainspec.typescript-exact-uint64/v1", "--target-root", target], { stdout() {}, stderr(value) { error += value; } }), 0, error);
  assert.equal(readFileSync(path.join(target, "compositions/function/behavior.mjs"), "utf8"), before.graph.compositions[0].artifacts["behavior.mjs"]);
  assert.ok(existsSync(path.join(target, "compositions/function/source.json")));
  direct.ontology.references.pop();
  writeFileSync(compositionPath, JSON.stringify(direct));
  assert.throws(() => compiler.compileProject(project), /ontology dependency set/);
});
