import path from "node:path";

/** Versioned output contract shared with compiler consumers. */
export const APPLICATION_LAYOUT = Object.freeze({
  id: "domainspec.application-layout/v1" as const,
  app: "app", domain: "domain", runtime: "runtime", modules: "modules",
  provenance: "provenance", evidence: "evidence", bin: "bin",
  receipt: "evidence/project-build.json",
});
export const PROJECT_LAYOUT = Object.freeze({
  id: "domainspec.project-layout/v1" as const,
  source: "src",
  features: "features",
  shared: "shared/domain",
  receipt: ".domainspec/project-build.json",
});
export type OutputLayout = typeof APPLICATION_LAYOUT.id | typeof PROJECT_LAYOUT.id;
export function validateOutputLayout(value: unknown): OutputLayout | undefined {
  if (value === undefined) return undefined;
  if (value !== APPLICATION_LAYOUT.id && value !== PROJECT_LAYOUT.id) throw new Error("DS_OUTPUT_LAYOUT: unsupported output layout");
  return value;
}
export function applicationArtifactPath(relative: string): string {
  const core = /^src\/domainspec\/(typescript|python|rust)\/(.+)$/.exec(relative);
  if (core) return `${APPLICATION_LAYOUT.domain}/${core[1]}/src/${core[2]}`;
  const composition = /^compositions\/([a-z][a-z0-9-]*)\/(.+)$/.exec(relative);
  if (!composition) throw new Error(`DS_OUTPUT_LAYOUT: unmapped artifact ${relative}`);
  const [, id, name] = composition;
  if (name === "runtime.rs") return `${APPLICATION_LAYOUT.runtime}/${id}/runtime.rs`;
  if (name === "composition-trace.json") return `${APPLICATION_LAYOUT.evidence}/${id}/${name}`;
  if (name === "source.alch" || name?.endsWith(".json")) return `${APPLICATION_LAYOUT.provenance}/${id}/${name}`;
  return `${APPLICATION_LAYOUT.app}/${id}/${name}`;
}
export function outputImport(from: string, to: string): string {
  const relative = path.posix.relative(path.posix.dirname(from), to);
  return relative.startsWith(".") ? relative : `./${relative}`;
}

/** Conventional single-function application paths; imported modules repeat this contract. */
export const APPLICATION_PATHS = Object.freeze({
  entry: "app/function/index.mjs", launcher: "app/function/server.mjs",
  behavior: "app/function/behavior.mjs", runtime: "runtime/boundary.mjs",
  traceRuntime: "runtime/invocation-trace.mjs", api: "domain/typescript/lib/index.js",
  apiSource: "domain/typescript/src/index.ts", typescriptSource: "domain/typescript/src",
  typescriptLib: "domain/typescript/lib", model: "provenance/function/function.json",
  bindings: "provenance/function/bindings.json", ontology: "provenance/function/ontology.json",
  source: "provenance/function/source.alch", composition: "provenance/function/composition.json",
  compositionTrace: "evidence/function/composition-trace.json", modules: "provenance/modules.json",
  cargo: "app/function/Cargo.toml", rustLibrary: "app/function/src/lib.rs",
  binary: "bin/alch-function", receipt: APPLICATION_LAYOUT.receipt,
});
