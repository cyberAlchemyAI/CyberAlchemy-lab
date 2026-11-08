#!/usr/bin/env node
import {createHash} from "node:crypto";
import {mkdtempSync, readFileSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {spawnSync} from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "alch/system-ontology/system-ontology.alch");
const generated = resolve(root, "generated/define-system-ontology");
const repositoryRoot = resolve(root, "../..");
const compiler = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js");
const manifest = JSON.parse(readFileSync(resolve(generated, "manifest.json"), "utf8"));
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
if (manifest.source_sha256 !== sha(readFileSync(source))) throw new Error("system-adapter.source-drift");
if (JSON.stringify(manifest.entries) !== JSON.stringify(["SystemOntologyQuestion", "SystemOntologyReadiness"])) throw new Error("system-adapter.entry-drift");
for (const [path, digest] of Object.entries(manifest.files)) if (sha(readFileSync(resolve(generated, path))) !== digest) throw new Error(`system-adapter.generated-drift:${path}`);
const temporary = mkdtempSync(join(tmpdir(), "define-system-adapter-"));
try {
  const rebuilt = resolve(temporary, "bundle");
  const run = spawnSync(process.execPath, [compiler, "build", source, "--out", rebuilt], {cwd: repositoryRoot, encoding: "utf8", env: process.env});
  if (run.status !== 0) throw new Error(`system-adapter.recompile:${run.stderr.trim()}`);
  if (!readFileSync(resolve(rebuilt, "manifest.json")).equals(readFileSync(resolve(generated, "manifest.json")))) throw new Error("system-adapter.recompile-manifest-drift");
  for (const path of Object.keys(manifest.files)) if (!readFileSync(resolve(rebuilt, path)).equals(readFileSync(resolve(generated, path)))) throw new Error(`system-adapter.recompile-byte-drift:${path}`);
} finally { rmSync(temporary, {recursive: true, force: true}); }
process.stdout.write(`${JSON.stringify({schema_version: "cav2.define-system-ontology-verification/v1", status: "PASS", source_sha256: manifest.source_sha256, entries: manifest.entries, generated_files: Object.keys(manifest.files).length, fresh_recompilation: "byte-identical", selected_source: "define/system-ontology", source_validation_posture: "FLAG", ontology_admitted: false, authority_effect: "none"}, null, 2)}\n`);
