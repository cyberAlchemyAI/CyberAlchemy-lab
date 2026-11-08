import path from "node:path";
import { planApplicationFile } from "./application-file-check.js";
import { assertApplicationFileCurrent, type ApplicationFileOptions } from "./application-file-input.js";
import { APPLICATION_MANIFEST, assertApplicationOutputTarget, validateApplicationOutput, verifyApplicationOutput, writeApplicationOutput } from "./application-output.js";
import { digest, json } from "./domainspec-profile.js";
import { CompilationRejected } from "./model.js";

const fail = (message: string): never => { throw new CompilationRejected([{ code: "APPLICATION_BUILD", path: "$artifacts", message }]); };

async function bundle(sourcePath: string, options: ApplicationFileOptions) {
  const plan = await planApplicationFile(sourcePath, options), files: Record<string, string> = Object.create(null);
  const add = (name: string, bytes: string) => {
    if (Object.hasOwn(files, name)) fail("artifact path collision");
    files[name] = bytes;
  };
  for (const artifact of plan.whole?.application.artifacts ?? plan.executable.view.artifacts) {
    if (artifact.relative_path.split("/")[0]!.toLowerCase() === ".alch") fail("reserved metadata path");
    if (digest(artifact.content) !== artifact.sha256 || Buffer.byteLength(artifact.content) !== artifact.size_bytes) fail("artifact digest differs");
    add(artifact.relative_path, artifact.content);
  }
  for (const [name, bytes] of Object.entries(plan.loaded.candidate.projectFiles)) add(`.alch/project/${name}`, bytes);
  for (const [name, bytes] of Object.entries(plan.loaded.candidate.projection.formation.files)) add(`.alch/formation/${name}`, bytes);
  for (const [name, bytes] of Object.entries(plan.whole?.files ?? {})) add(`.alch/whole/${name}`, bytes);
  add(".alch/check.json", json(plan.report));
  add(".alch/inputs.json", json(plan.loaded.inputs));
  add(".alch/executable-trace.json", json(plan.executable.trace));
  if (plan.loaded.entry_manifest) add(".alch/entry-manifest.json", json(plan.loaded.entry_manifest));
  validateApplicationOutput(files);
  const ordered = Object.fromEntries(Object.entries(files).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0));
  const manifest = { schema_version: "alchlang.application-build/v1-candidate", profile: "application-v1", scope: plan.report.scope,
    source_sha256: plan.report.source_sha256, inputs_sha256: plan.report.inputs_sha256,
    domain_manifest_sha256: plan.report.domain_manifest_sha256,
    executable_trace_sha256: plan.report.executable_trace_sha256,
    currentness_receipt_sha256: plan.report.currentness_receipt_sha256,
    unsupported_residue: plan.report.unsupported_residue,
    ...(plan.loaded.entry_manifest ? { entry_manifest_sha256: digest(json(plan.loaded.entry_manifest)),
      selected_entry: plan.loaded.entry_manifest.selected_entry } : {}),
    ...(plan.whole ? { whole_application_plan_sha256: plan.whole.wholeApplication.plan_sha256,
      provider_application_plan_sha256: plan.whole.application.plan_sha256 } : {}),
    files: Object.fromEntries(Object.entries(ordered).map(([name, bytes]) => [name, { sha256: digest(bytes), size_bytes: Buffer.byteLength(bytes) }])),
    runtime_guarantees_observed: false, authority_effect: "none" };
  return { ...plan, files: Object.freeze({ ...ordered, [APPLICATION_MANIFEST]: json(manifest) }), manifest };
}

export async function buildApplicationFile(sourcePath: string, outputPath: string, options: ApplicationFileOptions = {}) {
  assertApplicationOutputTarget(outputPath);
  const result = await bundle(sourcePath, options);
  writeApplicationOutput(outputPath, result.files, () => assertApplicationFileCurrent(result.loaded));
  return { ...result.report, status: "built" as const, output_directory: path.resolve(outputPath), manifest_sha256: digest(json(result.manifest)) };
}

export async function verifyApplicationFile(sourcePath: string, outputPath: string, options: ApplicationFileOptions = {}) {
  const result = await bundle(sourcePath, options);
  verifyApplicationOutput(outputPath, result.files);
  assertApplicationFileCurrent(result.loaded);
  return { ...result.report, status: "verified" as const, output_directory: path.resolve(outputPath), manifest_sha256: digest(json(result.manifest)) };
}
