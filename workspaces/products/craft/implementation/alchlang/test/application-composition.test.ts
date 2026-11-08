import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { buildApplicationFile, verifyApplicationFile } from "../src/application-file-build.js";
import { checkApplicationFile } from "../src/application-file-check.js";
import { loadApplicationFile } from "../src/application-file-input.js";
import { lowerApplicationDomain } from "../src/application-domain-lowering.js";
import { deriveApplicationIntegrationBindings } from "../src/application-integration-derivation.js";
import { lowerApplicationRuleProjections } from "../src/application-rule-projection.js";
import { digest, json } from "../src/domainspec-profile.js";
import { wholeApplicationFixture } from "./fixtures/application-whole-fixture.js";
import { testTsx } from "./toolchain.js";

type Ref = { path: string; sha256: string; size_bytes: number; current: true };

async function materialize(t: test.TestContext) {
  const base = await wholeApplicationFixture("provider-selection:commerce-runtime", false, true);
  const marker = "runtime-profile CommerceRuntime:";
  const split = base.source.indexOf(marker);
  assert.ok(split > 0);
  const first = base.source.slice(0, split).replace(/\s+$/, "");
  const identity = base.source.split(/\r?\n/).filter(line => /^(?:domain |profile application-v1$|owner )/.test(line)).join("\n");
  const runtimeBlock = base.source.slice(split).replace(/^\s+|\s+$/g, "");
  const second = `${identity}\n${runtimeBlock}\n`;
  const combined = `${first}\n\n${runtimeBlock}\n`;
  const compiler = base.compiler;
  const derived = deriveApplicationIntegrationBindings(combined, "CommerceRuntime", compiler);
  const contexts = [{ binding: derived.persistence, compiler }, { binding: derived.messaging, compiler },
    { binding: derived.externalApi, compiler }, { profile: "CommerceRuntime", compiler }] as const;
  const bindings = structuredClone(base.bindings);
  bindings.source_sha256 = digest(combined);
  bindings.formal.source_sha256 = digest(combined);
  const formation = lowerApplicationDomain(combined, bindings, base.sources, ...contexts);
  const interpretation = { ...base.interpretation, formation_sha256: digest(json(formation)) };
  const projection = lowerApplicationRuleProjections(combined, bindings, base.sources, interpretation, ...contexts);
  const execution = { ...base.execution, projection_sha256: digest(json(projection)) };

  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-application-composition-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const write = (relative: string, bytes: string | Buffer): Ref => {
    const target = path.join(root, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, bytes);
    return { path: relative, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true };
  };
  const rootSource = `${identity}\n`;
  const sourcePath = path.join(root, "commerce.composition.alch");
  write("commerce.composition.alch", rootSource);
  const sourceRefs = [
    { namespace: "commerce.domain", ...write("sources/domain.alch", `${first}\n`) },
    { namespace: "commerce.runtime", ...write("sources/runtime.alch", second) },
  ];
  const evidence = [...base.sources].map(([name, bytes]) => write(name, bytes));
  const refs = {
    bindings: write("inputs/bindings.json", json(bindings)),
    interpretation: write("inputs/interpretation.json", json(interpretation)),
    execution: write("inputs/execution.json", json(execution)),
    evidence,
  };
  const entry = (id: string, namespace: string, runtimeIdentity: string) => ({ id, namespace, runtime_identity: runtimeIdentity,
    sources: ["commerce.domain", "commerce.runtime"], endpoint: "SubmitHttp", runtime_profile: "CommerceRuntime", ...refs });
  const manifest: any = { schema_version: "alchlang.application-file/v2-candidate", source_sha256: digest(rootSource), sources: sourceRefs,
    entries: [entry("Primary", "commerce.primary", "commerce:primary"), entry("Secondary", "commerce.secondary", "commerce:secondary")] };
  const save = () => write("commerce.composition.alch.application.json", json(manifest));
  save();
  return { root, sourcePath, write, manifest, save, first, second, combined };
}

test("multi-file application composition requires and records one exact entry", async t => {
  const fixture = await materialize(t);
  await assert.rejects(loadApplicationFile(fixture.sourcePath), /explicit entry selection/);
  await assert.rejects(loadApplicationFile(fixture.sourcePath, { entry: "Missing" }), /unknown composition entry/);

  const primary = await loadApplicationFile(fixture.sourcePath, { entry: "Primary" });
  const primaryManifest = primary.entry_manifest as any;
  assert.ok(primaryManifest);
  assert.equal(primaryManifest.selected_entry, "Primary");
  assert.deepEqual(primaryManifest.sources.map((row: any) => row.namespace), ["commerce.domain", "commerce.runtime"]);
  assert.deepEqual(primaryManifest.entries.map((row: any) => ({ id: row.id, runtime: row.runtime_identity, route: row.route })), [
    { id: "Primary", runtime: "commerce:primary", route: { method: "POST", path: "/orders" } },
    { id: "Secondary", runtime: "commerce:secondary", route: { method: "POST", path: "/orders" } },
  ]);
  assert.equal(primaryManifest.entries[0].operation, "SubmitOrder");
  assert.ok(primaryManifest.entries[0].partitions.find((row: any) => row.namespace === "commerce.domain").declarations.some((row: any) => row.id === "SubmitOrder"));
  assert.ok(primaryManifest.entries[0].partitions.find((row: any) => row.namespace === "commerce.runtime").declarations.some((row: any) => row.id === "CommerceRuntime"));
  assert.ok(Object.hasOwn(primary.inputs, "sources/domain.alch"));
  assert.ok(Object.hasOwn(primary.inputs, "sources/runtime.alch"));

  const secondary = await loadApplicationFile(fixture.sourcePath, { entry: "Secondary" });
  const secondaryManifest = secondary.entry_manifest as any;
  assert.equal(secondaryManifest.selected_entry, "Secondary");
  assert.notEqual(digest(json(primaryManifest)), digest(json(secondaryManifest)));
  const checked = await checkApplicationFile(fixture.sourcePath, { entry: "Primary" });
  assert.equal(checked.selected_entry, "Primary");
  const output = path.join(fixture.root, "generated");
  const built = await buildApplicationFile(fixture.sourcePath, output, { entry: "Primary" });
  assert.equal(built.selected_entry, "Primary");
  assert.equal((await verifyApplicationFile(fixture.sourcePath, output, { entry: "Primary" })).status, "verified");
  const emitted = JSON.parse(fs.readFileSync(path.join(output, ".alch/entry-manifest.json"), "utf8"));
  assert.deepEqual(emitted, primaryManifest);

  const cli = process.env.ALCHLANG_TEST_PUBLIC_CLI
    ? [path.resolve(process.env.ALCHLANG_TEST_PUBLIC_CLI)] : [testTsx(), path.resolve(import.meta.dirname, "../src/core-cli.ts")];
  const missing = spawnSync(process.execPath, [...cli, "check", fixture.sourcePath], { encoding: "utf8", timeout: 60000 });
  assert.notEqual(missing.status, 0); assert.equal(missing.stdout, "");
  const explicit = spawnSync(process.execPath, [...cli, "check", fixture.sourcePath, "--entry", "Primary"], { encoding: "utf8", timeout: 60000 });
  assert.equal(explicit.status, 0, explicit.stderr); assert.equal(JSON.parse(explicit.stdout).selected_entry, "Primary");
});

test("composition rejects namespace, route, path, declaration and runtime identity collisions", async t => {
  const fixture = await materialize(t);
  const original = structuredClone(fixture.manifest);
  const reset = () => {
    for (const key of Object.keys(fixture.manifest)) delete fixture.manifest[key];
    Object.assign(fixture.manifest, structuredClone(original));
  };
  const rejectManifest = async (change: (manifest: any) => void, pattern: RegExp) => {
    reset();
    change(fixture.manifest);
    fixture.save();
    await assert.rejects(loadApplicationFile(fixture.sourcePath, { entry: "Primary" }), pattern);
  };
  await rejectManifest(manifest => { manifest.sources[1].namespace = manifest.sources[0].namespace; }, /duplicate source namespace/);
  await rejectManifest(manifest => { manifest.entries[1].runtime_identity = manifest.entries[0].runtime_identity; }, /duplicate runtime identity/);
  await rejectManifest(manifest => { manifest.sources[1].path = "../runtime.alch"; }, /FORMAL_BINDING_PATH|APPLICATION_FILE_INPUT/);

  reset();
  const duplicateDeclaration = `${fixture.second}\nentity Order:\n  id UInt64\n  identity id\n`;
  fixture.manifest.sources[1] = { namespace: "commerce.runtime", ...fixture.write("sources/runtime.alch", duplicateDeclaration) };
  fixture.save();
  await assert.rejects(loadApplicationFile(fixture.sourcePath, { entry: "Primary" }), /DUPLICATE_IDENTIFIER/);

  reset();
  const duplicateRoute = `${fixture.second}\ninbound-endpoint DuplicateSubmitHttp:\n  HTTP POST "/orders"\n    -> request OrderApi.SubmitRequest\n    -> operation SubmitOrder\n    -> response OrderApi.Summary\n`;
  fixture.manifest.sources[1] = { namespace: "commerce.runtime", ...fixture.write("sources/runtime.alch", duplicateRoute) };
  fixture.save();
  await assert.rejects(loadApplicationFile(fixture.sourcePath, { entry: "Primary" }), /duplicate composition route POST \/orders/);
});
