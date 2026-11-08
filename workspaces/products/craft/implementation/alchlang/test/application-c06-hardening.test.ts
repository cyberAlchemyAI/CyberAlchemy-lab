import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { buildApplicationFile, verifyApplicationFile } from "../src/application-file-build.js";
import { checkApplicationFile } from "../src/application-file-check.js";
import { APPLICATION_MANIFEST, writeApplicationOutput } from "../src/application-output.js";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { digest, json } from "../src/domainspec-profile.js";
import { CompilationRejected } from "../src/model.js";
import { parseDomainSource } from "../src/parser.js";
import { realizationFixture } from "./fixtures/application-realization-fixture.js";

type CorpusCase = { id: string; phase: string; expected_diagnostic: string | null; publication_state: string };
const corpusPath = path.resolve(defaultDomainSpecPackageRoot(), "../../development/authoring-to-runtime-v1/c06-adversarial-cases.json");
const corpus = JSON.parse(fs.readFileSync(corpusPath, "utf8")) as { schema_version: string; authority_effect: string; cases: CorpusCase[] };

function materialize(root: string, name: string) {
  const f = realizationFixture(), dir = path.join(root, name); fs.mkdirSync(dir);
  const write = (relative: string, bytes: string | Buffer) => {
    const target = path.join(dir, relative); fs.mkdirSync(path.dirname(target), { recursive: true }); fs.writeFileSync(target, bytes);
    return { path: relative, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true };
  };
  write("commerce.alch", f.source);
  const manifest: any = { schema_version: "alchlang.application-file/v1-candidate", source_sha256: digest(f.source),
    bindings: write("inputs/bindings.json", json(f.bindings)), interpretation: write("inputs/interpretation.json", json(f.interpretation)),
    execution: write("inputs/execution.json", json(f.execution)), evidence: [...f.sources].map(([file, bytes]) => write(file, bytes)) };
  const save = () => write("commerce.alch.application.json", json(manifest)); save();
  return { f, dir, source: path.join(dir, "commerce.alch"), manifest, save, write };
}

function inventory(root: string): Record<string, string> {
  const result: Record<string, string> = {};
  const walk = (directory: string) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0)) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) walk(file);
      else if (entry.isFile()) result[path.relative(root, file).split(path.sep).join("/")] = digest(fs.readFileSync(file));
      else assert.fail(`unexpected output entry ${file}`);
    }
  };
  walk(root); return result;
}

async function rejection(action: () => unknown | Promise<unknown>): Promise<unknown> {
  try { await action(); } catch (error) { return error; }
  assert.fail("expected rejection");
}

function diagnostic(error: unknown): string {
  if (error instanceof CompilationRejected) return error.issues[0]!.code;
  return error instanceof Error ? error.message : String(error);
}

test("C06 currentness receipt is explicit and complete application builds are byte-repeatable", async t => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-c06-repeat-")); t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const p = materialize(root, "application");
  const firstCheck = await checkApplicationFile(p.source), secondCheck = await checkApplicationFile(p.source);
  assert.deepEqual(secondCheck, firstCheck);
  assert.deepEqual(firstCheck.unsupported_residue, []);
  assert.equal(firstCheck.currentness_receipt.status, "current");
  assert.equal(firstCheck.currentness_receipt.authority_effect, "none");
  assert.equal(firstCheck.currentness_receipt_sha256, digest(json(firstCheck.currentness_receipt)));
  const first = path.join(root, "first"), second = path.join(root, "second");
  const firstResult = await buildApplicationFile(p.source, first), secondResult = await buildApplicationFile(p.source, second);
  assert.equal(firstResult.manifest_sha256, secondResult.manifest_sha256);
  assert.deepEqual(inventory(first), inventory(second));
  const manifest = JSON.parse(fs.readFileSync(path.join(first, APPLICATION_MANIFEST), "utf8"));
  assert.equal(manifest.currentness_receipt_sha256, firstCheck.currentness_receipt_sha256);
  assert.equal(manifest.source_sha256, firstCheck.source_sha256);
  assert.equal(manifest.domain_manifest_sha256, firstCheck.domain_manifest_sha256);
  assert.deepEqual(manifest.unsupported_residue, []);
  assert.equal((await verifyApplicationFile(p.source, first)).status, "verified");
  t.diagnostic(JSON.stringify({ currentness_receipt_sha256: firstCheck.currentness_receipt_sha256,
    manifest_sha256: firstResult.manifest_sha256, files: Object.keys(manifest.files).length,
    unsupported_residue: firstCheck.unsupported_residue.length }));
});

test("C06 adversarial corpus fails closed with exact diagnostics and publication states", async t => {
  assert.equal(corpus.schema_version, "alchlang.c06-adversarial-corpus/v1-candidate");
  assert.equal(corpus.authority_effect, "none");
  assert.equal(new Set(corpus.cases.map(row => row.id)).size, corpus.cases.length);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "alch-c06-hostile-")); t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const observed = new Map<string, { diagnostic: string | null; publication_state: string }>();
  const record = (row: CorpusCase, error: unknown, publicationState = row.publication_state) => {
    const actual = diagnostic(error); assert.equal(actual, row.expected_diagnostic, row.id);
    observed.set(row.id, { diagnostic: actual, publication_state: publicationState });
  };
  const row = (id: string) => corpus.cases.find(item => item.id === id)!;

  {
    const item = row("unsupported-source-declaration");
    record(item, await rejection(() => parseDomainSource(realizationFixture().source + "unknown-declaration Mystery:\n")));
  }
  {
    const item = row("invalid-source-utf8"), p = materialize(root, item.id), bytes = Buffer.from([0xff]);
    fs.writeFileSync(p.source, bytes); p.manifest.source_sha256 = digest(bytes); p.save();
    const out = path.join(p.dir, "out"); record(item, await rejection(() => buildApplicationFile(p.source, out))); assert.equal(fs.existsSync(out), false);
  }
  {
    const item = row("source-currentness-drift"), p = materialize(root, item.id); fs.appendFileSync(p.source, "\n");
    const out = path.join(p.dir, "out"); record(item, await rejection(() => buildApplicationFile(p.source, out))); assert.equal(fs.existsSync(out), false);
  }
  {
    const item = row("selected-input-currentness-drift"), p = materialize(root, item.id); fs.appendFileSync(path.join(p.dir, p.manifest.bindings.path), " ");
    const out = path.join(p.dir, "out"); record(item, await rejection(() => buildApplicationFile(p.source, out))); assert.equal(fs.existsSync(out), false);
  }
  {
    const item = row("escaping-input-reference"), p = materialize(root, item.id); p.manifest.bindings.path = "../outside.json"; p.save();
    const out = path.join(p.dir, "out"); record(item, await rejection(() => buildApplicationFile(p.source, out))); assert.equal(fs.existsSync(out), false);
  }
  {
    const item = row("symlink-input-reference"), p = materialize(root, item.id), selected = path.join(p.dir, p.manifest.bindings.path), outside = path.join(p.dir, "outside.json");
    fs.renameSync(selected, outside); fs.symlinkSync(outside, selected);
    const out = path.join(p.dir, "out"); record(item, await rejection(() => buildApplicationFile(p.source, out))); assert.equal(fs.existsSync(out), false);
  }

  const baseFiles = { "src/main.ts": "export {};\n", ".alch/check.json": "{}\n", [APPLICATION_MANIFEST]: "manifest\n" };
  for (const [id, extra] of [
    ["output-traversal", { "../escape": "x" }],
    ["reserved-device-output", { "CON.txt": "x" }],
    ["case-output-alias", { "SRC/other.ts": "x" }],
    ["unicode-output-alias", { "ＳＲＣ/other.ts": "x" }],
    ["file-directory-output-alias", { src: "x" }],
  ] as const) {
    const item = row(id), out = path.join(root, id);
    record(item, await rejection(() => writeApplicationOutput(out, { ...baseFiles, ...extra }, () => {})));
    assert.equal(fs.existsSync(out), false, id);
  }
  {
    const item = row("existing-destination"), out = path.join(root, item.id); fs.mkdirSync(out); fs.writeFileSync(path.join(out, "keep"), "keep");
    record(item, await rejection(() => writeApplicationOutput(out, baseFiles, () => {})));
    assert.equal(fs.readFileSync(path.join(out, "keep"), "utf8"), "keep");
  }
  {
    const item = row("late-input-currentness-drift"), out = path.join(root, item.id); let calls = 0;
    record(item, await rejection(() => writeApplicationOutput(out, baseFiles, () => { if (++calls === 2) throw Error("CURRENTNESS_TEST_DRIFT"); })));
    assert.equal(fs.existsSync(out), false);
  }
  {
    const item = row("replaced-output-root"), out = path.join(root, item.id), displaced = path.join(root, item.id + "-displaced"); let calls = 0;
    const error = await rejection(() => writeApplicationOutput(out, baseFiles, () => { if (++calls === 2) { fs.renameSync(out, displaced); fs.mkdirSync(out); fs.writeFileSync(path.join(out, "foreign"), "keep"); } }));
    record(item, error); assert.equal(fs.existsSync(path.join(out, APPLICATION_MANIFEST)), false); assert.equal(fs.readFileSync(path.join(out, "foreign"), "utf8"), "keep");
  }
  {
    const item = row("generated-output-drift"), p = materialize(root, item.id), out = path.join(p.dir, "out"); await buildApplicationFile(p.source, out);
    const manifest = JSON.parse(fs.readFileSync(path.join(out, APPLICATION_MANIFEST), "utf8"));
    const target = Object.keys(manifest.files).find(name => name.endsWith(".ts"))!; fs.appendFileSync(path.join(out, target), "\n// drift\n");
    record(item, await rejection(() => verifyApplicationFile(p.source, out)));
  }
  observed.set("repeatable-complete-build", { diagnostic: null, publication_state: "two-identical-complete-builds" });
  assert.deepEqual([...observed.keys()].sort(), corpus.cases.map(item => item.id).sort());
  for (const item of corpus.cases) assert.deepEqual(observed.get(item.id), { diagnostic: item.expected_diagnostic, publication_state: item.publication_state });
});
