import { createHash } from "node:crypto";
import { existsSync, mkdirSync, mkdtempSync, readdirSync, renameSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { CompilationResult } from "./model.js";

export interface WriteOptions { force?: boolean; carrier?: unknown }
export interface WriteReceipt { output_directory: string; files: Readonly<Record<string, string>>; source_digest: string; plan_digest: string }

const sha256 = (bytes: string): string => createHash("sha256").update(bytes).digest("hex");

export function writeCompilation(result: CompilationResult, outputDirectory: string, options: WriteOptions = {}): WriteReceipt {
  const target = path.resolve(outputDirectory);
  if (target === path.parse(target).root) throw new Error("OUTPUT_PATH_DENIED:filesystem-root");
  if (existsSync(target) && readdirSync(target).length && !options.force) throw new Error(`OUTPUT_EXISTS:${target}; pass --force to replace`);
  const parent = path.dirname(target); mkdirSync(parent, { recursive: true });
  const staging = mkdtempSync(path.join(parent, `.${path.basename(target)}.staging-`));
  const files = { ...result.files, ...(options.carrier === undefined ? {} : { "domain.carrier.json": `${JSON.stringify(options.carrier, null, 2)}\n` }) };
  const digests: Record<string, string> = {};
  try {
    for (const [name, bytes] of Object.entries(files).sort(([a], [b]) => a.localeCompare(b))) {
      if (path.basename(name) !== name || name.includes("..")) throw new Error(`OUTPUT_NAME_DENIED:${name}`);
      writeFileSync(path.join(staging, name), bytes, { flag: "wx" }); digests[name] = sha256(bytes);
    }
    const manifest = `${JSON.stringify({ schema_version: "domainspec.local-build-manifest/v1", source_digest: result.source_digest, plan_digest: result.plan_digest, files: digests, authority_effect: "none" }, null, 2)}\n`;
    writeFileSync(path.join(staging, "manifest.json"), manifest, { flag: "wx" }); digests["manifest.json"] = sha256(manifest);
    if (existsSync(target)) rmSync(target, { recursive: true });
    renameSync(staging, target);
  } catch (error) { if (existsSync(staging)) rmSync(staging, { recursive: true }); throw error; }
  return { output_directory: target, files: digests, source_digest: result.source_digest, plan_digest: result.plan_digest };
}
