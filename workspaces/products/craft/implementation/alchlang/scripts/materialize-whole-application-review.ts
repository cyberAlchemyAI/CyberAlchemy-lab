#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { digest, json } from "../src/domainspec-profile.js";
import { wholeApplicationFixture } from "../test/fixtures/application-whole-fixture.js";

const implementation = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const review = path.join(implementation, "review/whole-application-v1");
const sourceRoot = path.join(review, "source");
const source = path.join(sourceRoot, "commerce.alch");
const output = path.join(review, "generated");
const cli = path.join(implementation, "src/core-cli.ts");
const toolchain = path.join(implementation, "scripts/run-toolchain.mjs");

function descriptor(relative: string, bytes: string | Buffer) {
  return { path: relative, sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes), current: true };
}

function write(root: string, relative: string, bytes: string | Buffer) {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, bytes);
}

function run(command: "check" | "build" | "verify", sourcePath = source, outputPath = output) {
  const args = [toolchain, "tsx", cli, command, sourcePath];
  if (command !== "check") args.push("--out", outputPath);
  const result = spawnSync(process.execPath, args, { cwd: implementation, encoding: "utf8", timeout: 120_000 });
  if (result.status !== 0) throw new Error(`${command} failed: ${result.stderr || result.stdout}`);
  const value = JSON.parse(result.stdout);
  if (value.status !== ({ check: "valid", build: "built", verify: "verified" } as const)[command]) {
    throw new Error(`${command} returned unexpected status: ${result.stdout}`);
  }
  return value;
}

async function main() {
  const mode = process.argv[2];
  if (mode !== "--write" && mode !== "--check" && mode !== "--refresh" && mode !== "--refresh-generated") {
    throw new Error("usage: materialize-whole-application-review.ts --write|--check|--refresh|--refresh-generated");
  }
  const fixture = await wholeApplicationFixture("provider-selection:commerce-runtime", true, true);
  const selected = new Map<string, string | Buffer>([
    ["commerce.alch", fixture.source],
    ["inputs/bindings.json", json(fixture.bindings)],
    ["inputs/interpretation.json", json(fixture.interpretation)],
    ["inputs/execution.json", json(fixture.execution)],
    ...fixture.sources,
    ["inputs/observation.json", json(fixture.observation)],
  ]);
  const selectedFile = (relative: string) => descriptor(relative, selected.get(relative)!);
  const manifest = {
    schema_version: "alchlang.application-file/v1-candidate",
    source_sha256: digest(fixture.source),
    bindings: selectedFile("inputs/bindings.json"),
    interpretation: selectedFile("inputs/interpretation.json"),
    execution: selectedFile("inputs/execution.json"),
    evidence: [...fixture.sources].map(([name]) => selectedFile(name)),
    runtime_profile: "CommerceRuntime",
    observation: selectedFile("inputs/observation.json"),
  };
  selected.set("commerce.alch.application.json", json(manifest));
  if (mode === "--write") {
    if (fs.existsSync(sourceRoot) || fs.existsSync(output)) {
      throw new Error("review source or output already exists; refusing to overwrite user work");
    }
    for (const [relative, bytes] of selected) write(sourceRoot, relative, bytes);
  } else if (mode === "--check" || mode === "--refresh-generated") {
    for (const [relative, bytes] of selected) {
      const actual = path.join(sourceRoot, relative);
      if (!fs.existsSync(actual) || !fs.readFileSync(actual).equals(Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes))) {
        throw new Error(`review source companion is missing or differs from the authored fixture: ${relative}`);
      }
    }
  }
  if (mode === "--refresh-generated") {
    if (!fs.existsSync(output)) throw new Error("generated review output is missing");
    const staging = fs.mkdtempSync(path.join(review, ".regenerate-"));
    const stagedOutput = path.join(staging, "generated");
    const built = run("build", source, stagedOutput);
    const verified = run("verify", source, stagedOutput);
    if (built.manifest_sha256 !== verified.manifest_sha256) throw new Error("staged build/verify differ");
    const priorManifest = fs.readFileSync(path.join(output, ".alch/manifest.json"));
    const backupBase = path.join(review, `.prior-generated-${digest(priorManifest).slice(0, 12)}`);
    let backup = backupBase;
    for (let suffix = 2; fs.existsSync(backup); suffix++) backup = `${backupBase}-${suffix}`;
    fs.renameSync(output, backup);
    try { fs.renameSync(stagedOutput, output); }
    catch (error) { fs.renameSync(backup, output); throw error; }
    fs.rmdirSync(staging);
    process.stdout.write(`${JSON.stringify({status: "pass", mode, manifest_sha256: verified.manifest_sha256,
      backup, runtime_guarantees_observed: false}, null, 2)}\n`);
    return;
  }
  if (mode === "--refresh") {
    const priorSource = fixture.source.replace("  read current <- Order key request.id\n", "  query current <- FindOrder()\n  on-absence current fail ORDER_NOT_FOUND\n");
    if (priorSource === fixture.source || !fs.existsSync(source) || fs.readFileSync(source, "utf8") !== priorSource || !fs.existsSync(output)) {
      throw new Error("prior review source/output do not match the expected repair predecessor");
    }
    const staging = fs.mkdtempSync(path.join(review, ".refresh-"));
    const stagedSource = path.join(staging, "source"), stagedOutput = path.join(staging, "generated");
    for (const [relative, bytes] of selected) write(stagedSource, relative, bytes);
    const checked = run("check", path.join(stagedSource, "commerce.alch"), stagedOutput);
    if (checked.unsupported_residue.length) throw new Error("application has unsupported residue");
    const built = run("build", path.join(stagedSource, "commerce.alch"), stagedOutput);
    const verified = run("verify", path.join(stagedSource, "commerce.alch"), stagedOutput);
    if (built.manifest_sha256 !== verified.manifest_sha256) throw new Error("staged build/verify differ");
    const backup = path.join(review, `.prior-${digest(priorSource).slice(0, 12)}`);
    if (fs.existsSync(backup)) throw new Error(`review backup already exists: ${backup}`);
    fs.mkdirSync(backup);
    fs.renameSync(sourceRoot, path.join(backup, "source"));
    fs.renameSync(output, path.join(backup, "generated"));
    try {
      fs.renameSync(stagedSource, sourceRoot);
      fs.renameSync(stagedOutput, output);
    } catch (error) {
      if (fs.existsSync(sourceRoot)) fs.renameSync(sourceRoot, stagedSource);
      if (fs.existsSync(output)) fs.renameSync(output, stagedOutput);
      fs.renameSync(path.join(backup, "source"), sourceRoot);
      fs.renameSync(path.join(backup, "generated"), output);
      throw error;
    }
    fs.rmdirSync(staging);
    process.stdout.write(`${JSON.stringify({status: "pass", mode, source_sha256: checked.source_sha256,
      generated_artifacts: checked.generated_artifacts, manifest_sha256: verified.manifest_sha256,
      backup, runtime_guarantees_observed: false}, null, 2)}\n`);
    return;
  }
  const checked = run("check");
  if (checked.unsupported_residue.length) throw new Error("application has unsupported residue");
  const built = mode === "--write" ? run("build") : null;
  const verified = run("verify");
  if (built && built.manifest_sha256 !== verified.manifest_sha256) {
    throw new Error("build and verify manifest identities differ");
  }
  process.stdout.write(`${JSON.stringify({status: "pass", mode, source_sha256: checked.source_sha256,
    generated_artifacts: checked.generated_artifacts, manifest_sha256: verified.manifest_sha256,
    runtime_guarantees_observed: false}, null, 2)}\n`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
