import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const DOMAINSPEC_PACKAGE = "@domainspec-v2/cli" as const;
export const DOMAINSPEC_VERSION = "1.0.0" as const;

// These are the fields consumed by AlchLang's projection, not a second graph schema.
export interface DomainSpecGraph {
  project_root: string;
  project_id: string;
  nodes: Array<{ selector: string; kind: string; meta_type_id: string; body: unknown }>;
  relationships: Array<{ edge_id: string; relationship: string; source: { feature_id: string; node_id: string }; target: { feature_id: string; node_id: string } }>;
  source_manifest: { manifest_sha256: string };
  authority_effect: "none";
}
export interface DomainSpecIo { stdout(value: string): void; stderr(value: string): void }
export interface DomainSpecCompiler {
  normalizeCompositionOntology(value: unknown): Record<string, unknown>;
  compileEventBindings(value: unknown, language: "typescript" | "rust"): { manifest: unknown; source: string };
  supportsExactUInt64: boolean;
  applicationPaths: Readonly<Record<string,string>>;
  outputImport(from:string,to:string):string;
  applicationLayoutId: string;
  compileDeclarativeFunction(value:unknown):{source:string;contract:unknown;trace:unknown};
  binding: { package: typeof DOMAINSPEC_PACKAGE; version: typeof DOMAINSPEC_VERSION; package_root: string; package_sha256: string; entry_sha256: string };
  compileProject(sourceRoot: string): { graph: DomainSpecGraph; certificate: { compiler: { package: string; version: string }; authority_effect: "none" } };
  runCli(args: readonly string[], io?: DomainSpecIo): number;
}

export function defaultDomainSpecPackageRoot(): string {
  const checkout = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../../../..");
  return resolveDomainSpecPackageRoot(checkout, process.env.ALCHLANG_DOMAINSPEC_PACKAGE_ROOT);
}

/** The two documented checkout layouts; ambiguity requires an explicit binding. */
export function resolveDomainSpecPackageRoot(checkout: string, explicitRoot?: string): string {
  if (explicitRoot) return path.resolve(explicitRoot);
  const parent = path.dirname(checkout);
  const relative = "projects/domainspec-v2/impl/cli";
  const candidates = [path.join(parent, relative), path.join(parent, "domainspec-core", relative)]
    .filter((root) => existsSync(path.join(root, "package.json")));
  if (candidates.length !== 1) throw new Error(candidates.length
    ? "DOMAINSPEC_PACKAGE_AMBIGUOUS: set ALCHLANG_DOMAINSPEC_PACKAGE_ROOT"
    : "DOMAINSPEC_PACKAGE_MISSING: set ALCHLANG_DOMAINSPEC_PACKAGE_ROOT");
  return candidates[0]!;
}

export async function loadDomainSpecCompiler(packageRoot = defaultDomainSpecPackageRoot()): Promise<DomainSpecCompiler> {
  const root = path.resolve(packageRoot);
  const packageBytes = readFileSync(path.join(root, "package.json"));
  const manifest = JSON.parse(packageBytes.toString("utf8"));
  if (manifest.name !== DOMAINSPEC_PACKAGE || manifest.version !== DOMAINSPEC_VERSION) {
    throw new Error(`DOMAINSPEC_VERSION_MISMATCH: expected ${DOMAINSPEC_PACKAGE}@${DOMAINSPEC_VERSION}; got ${manifest.name}@${manifest.version}`);
  }
  const entry = manifest.exports?.["."]?.import;
  if (typeof entry !== "string" || !entry.startsWith("./") || path.relative(root, path.resolve(root, entry)).startsWith("..")) {
    throw new Error("DOMAINSPEC_PUBLIC_ENTRY_REQUIRED: package must export its public ESM entry");
  }
  const entryPath = path.resolve(root, entry);
  let entryBytes: Buffer;
  try { entryBytes = readFileSync(entryPath); }
  catch { throw new Error(`DOMAINSPEC_BUILD_REQUIRED: build ${root} before using AlchLang`); }
  const api = await import(pathToFileURL(entryPath).href);
  if (api.CLI_PACKAGE_NAME !== DOMAINSPEC_PACKAGE || api.CLI_VERSION !== DOMAINSPEC_VERSION || typeof api.compileProject !== "function" || typeof api.runCli !== "function") {
    throw new Error(`DOMAINSPEC_BUILD_MISMATCH: rebuild ${DOMAINSPEC_PACKAGE}@${DOMAINSPEC_VERSION}; manifest and built public API disagree`);
  }
  let version = "";
  const versionCode = api.runCli(["--version"], { stdout(value: string) { version += value; }, stderr() {} });
  if (versionCode !== 0 || version.trim() !== DOMAINSPEC_VERSION) throw new Error("DOMAINSPEC_BUILD_MISMATCH: CLI version does not match public API");
  const sha256 = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
  const requireLayout=()=>{if(api.APPLICATION_LAYOUT?.id!=="domainspec.application-layout/v1" || !api.APPLICATION_PATHS || typeof api.outputImport!=="function")throw Error("DOMAINSPEC_APPLICATION_LAYOUT_BUILD_REQUIRED");};
  return {
    normalizeCompositionOntology(value) {
      if (api.COMPOSITION_ONTOLOGY_SCHEMA !== "domainspec.composition-ontology/v1" || typeof api.normalizeCompositionOntology !== "function") throw Error("DOMAINSPEC_COMPOSITION_ONTOLOGY_BUILD_REQUIRED");
      return api.normalizeCompositionOntology(value);
    },
    compileEventBindings(value, language) {
      if (typeof api.compileSystemIntegrationManifest !== "function" || typeof api.renderSystemIntegrationContract !== "function") throw Error("DOMAINSPEC_MESSAGE_BUILD_REQUIRED");
      const manifest = api.compileSystemIntegrationManifest(value, language);
      return { manifest, source: api.renderSystemIntegrationContract(manifest) };
    },
    get applicationPaths() {
      if(api.APPLICATION_LAYOUT?.id!=="domainspec.application-layout/v1" || !api.APPLICATION_PATHS || typeof api.outputImport!=="function")throw Error("DOMAINSPEC_APPLICATION_LAYOUT_BUILD_REQUIRED");
      return api.APPLICATION_PATHS;
    },
    get applicationLayoutId(){requireLayout();return api.APPLICATION_LAYOUT.id;},
    outputImport(from,to){requireLayout();return api.outputImport(from,to);},
    supportsExactUInt64: api.EXACT_UINT64_PROFILE === "domainspec.typescript-exact-uint64/v1",
    compileDeclarativeFunction(value) {
      if(api.DECLARATIVE_FUNCTION_PROFILE!=="domainspec.declarative-function/v1"||typeof api.compileDeclarativeFunction!=="function")throw Error("DOMAINSPEC_DECLARATIVE_BUILD_REQUIRED");
      return api.compileDeclarativeFunction(value);
    },
    binding: { package: DOMAINSPEC_PACKAGE, version: DOMAINSPEC_VERSION, package_root: root, package_sha256: sha256(packageBytes), entry_sha256: sha256(entryBytes) },
    compileProject(sourceRoot) {
      const result = api.compileProject(path.resolve(sourceRoot));
      if (result.certificate?.compiler?.package !== DOMAINSPEC_PACKAGE || result.certificate?.compiler?.version !== DOMAINSPEC_VERSION || result.certificate?.authority_effect !== "none" || result.graph?.authority_effect !== "none") {
        throw new Error("DOMAINSPEC_CERTIFICATE_MISMATCH: compilation is not bound to the selected compiler");
      }
      return result;
    },
    runCli(args, io) { return api.runCli(args, io); },
  };
}

// Deliberately excludes experimental execution, source authoring and deployment recipes.
const COMPILER_COMMANDS = new Set(["--version", "--help", "capabilities", "doctor", "lint", "receipt", "compile", "build", "verify", "instantiate", "instantiate-project", "verify-project", "formalize", "formalize-check", "certify", "certify-check"]);
export async function runDomainSpecCli(args: readonly string[], io?: DomainSpecIo, packageRoot?: string): Promise<number> {
  const command = args[0] ?? "--help";
  if (!COMPILER_COMMANDS.has(command)) throw new Error(`DOMAINSPEC_COMMAND_UNSUPPORTED:${command}`);
  const compiler = await loadDomainSpecCompiler(packageRoot);
  return compiler.runCli(args.length ? args : ["--help"], io);
}
