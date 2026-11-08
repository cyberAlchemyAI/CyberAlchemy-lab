import {createHash} from "node:crypto";
import {lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, renameSync, rmSync, writeFileSync} from "node:fs";
import path from "node:path";

type Kind = "configuration" | "module" | "capability" | "entry" | "governed-by";
type Declaration = {kind: Kind; name: string; line: number; fields: Record<string, string>};
const KINDS = new Set<Kind>(["configuration", "module", "capability", "entry", "governed-by"]);
const REQUIRED: Record<Kind, string[]> = {
  configuration: ["configuration-id", "status", "authority-effect"],
  module: ["factory-id", "factory-source", "factory-source-sha256", "module-id", "version", "adapter-protocol", "manifest-digest", "side-effects", "authority-effect"],
  capability: ["module", "capability-id", "input-protocol", "output-protocol"],
  entry: ["capability", "consumer", "posture"],
  "governed-by": ["decision", "decision-sha256", "constitution-id", "selector", "authority-effect"],
};
const POSTURES = new Set(["required-for-judgment", "required-for-operation", "optional-enrichment"]);
const fail = (message: string): never => { throw Error(`ALCH_MODULE_CONFIGURATION: ${message}`); };
const sha256 = (value: string | Buffer) => createHash("sha256").update(value).digest("hex");
const json = (value: unknown) => `${JSON.stringify(value, null, 2)}\n`;
const safe = (value: string) => /^[A-Za-z][A-Za-z0-9_-]{0,127}$/.test(value);
const identifier = (value: string) => /^[a-z0-9](?:[-a-z0-9._/:]{0,126}[a-z0-9])?$/.test(value);
const digest = (value: string) => /^[a-f0-9]{64}$/.test(value);
const unquote = (value: string): string => {
  if (!value.startsWith('"')) return value;
  try { const parsed: unknown = JSON.parse(value); if (typeof parsed === "string" && parsed.length > 0) return parsed; }
  catch {}
  return fail(`invalid quoted value ${value}`);
};
const normalize = (value: unknown): unknown => {
  if (value === null || typeof value === "string" || typeof value === "boolean" || typeof value === "number") return value;
  if (Array.isArray(value)) return value.map(normalize);
  if (!value || typeof value !== "object") return fail("non-JSON value");
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, normalize((value as Record<string, unknown>)[key])]));
};
const canonical = (value: unknown) => JSON.stringify(normalize(value));
const files = (root: string): string[] => readdirSync(root, {withFileTypes: true}).flatMap((entry) => entry.isDirectory() ? files(path.join(root, entry.name)) : [path.join(root, entry.name)]);

function parse(source: string) {
  if (source.charCodeAt(0) === 0xfeff || source.includes("```")) fail("plain UTF-8 .alch required");
  const headers: Record<string, string> = {};
  const declarations: Declaration[] = [];
  let current: Declaration | undefined;
  for (const [offset, raw] of source.split(/\r?\n/).entries()) {
    const line = offset + 1;
    if (!raw.trim() || raw.trimStart().startsWith("#")) continue;
    if (!raw.startsWith(" ")) {
      const declaration = raw.match(/^(configuration|module|capability|entry|governed-by) ([A-Za-z][A-Za-z0-9_-]{0,127}):$/);
      if (declaration) {
        current = {kind: declaration[1] as Kind, name: declaration[2]!, line, fields: {}};
        declarations.push(current);
        continue;
      }
      const header = raw.match(/^(domain|profile|owner|runtime) (.+)$/);
      if (!header) fail(`line ${line}: unsupported top-level statement`);
      if (headers[header![1]!]) fail(`line ${line}: duplicate ${header![1]}`);
      headers[header![1]!] = unquote(header![2]!);
      current = undefined;
      continue;
    }
    const target = current;
    if (target === undefined) fail(`line ${line}: clause without declaration`);
    const clause = raw.match(/^  ([a-z][a-z0-9-]*) (.+)$/);
    if (clause === null) fail(`line ${line}: invalid clause`);
    const key = clause![1]!;
    if (target!.fields[key]) fail(`line ${line}: duplicate clause`);
    target!.fields[key] = unquote(clause![2]!);
  }
  for (const header of ["domain", "profile", "owner", "runtime"]) if (!headers[header]) fail(`missing ${header}`);
  if (!["module-configuration-v1", "module-configuration-v2"].includes(headers.profile!)) fail("profile must be module-configuration-v1 or module-configuration-v2");
  if (headers.runtime !== "node>=26.8.1" || !safe(headers.owner!)) fail("runtime or owner is invalid");
  for (const kind of KINDS) if (!declarations.some((item) => item.kind === kind)) fail(`at least one ${kind} declaration is required`);
  if (declarations.filter((item) => item.kind === "configuration").length !== 1 || declarations.filter((item) => item.kind === "governed-by").length !== 1) fail("exactly one configuration and governed-by declaration are required");
  if (declarations.filter((item) => item.kind === "entry").length < 2) fail("at least two entry declarations are required");
  const names = new Set<string>();
  for (const item of declarations) {
    if (names.has(item.name)) fail(`duplicate declaration ${item.name}`);
    names.add(item.name);
    const allowed = new Set([...REQUIRED[item.kind], ...(headers.profile === "module-configuration-v2" && item.kind === "module" ? ["runtime-source", "runtime-source-sha256", "compiled-source", "compiled-source-sha256"] : [])]);
    for (const key of Object.keys(item.fields)) if (!allowed.has(key)) fail(`${item.name}: unsupported clause ${key}`);
    for (const key of allowed) if (!item.fields[key]) fail(`${item.name}: missing ${key}`);
  }
  const byName = new Map(declarations.map((item) => [item.name, item]));
  const configuration = declarations.find((item) => item.kind === "configuration")!;
  if (!identifier(configuration.fields["configuration-id"]!) || configuration.fields.status !== "candidate" || configuration.fields["authority-effect"] !== "none") fail("configuration must remain candidate and authority-effect none");
  const modules = declarations.filter((item) => item.kind === "module");
  const capabilities = declarations.filter((item) => item.kind === "capability");
  const entries = declarations.filter((item) => item.kind === "entry");
  if (new Set(modules.map((item) => item.fields["module-id"])).size !== modules.length || new Set(modules.map((item) => item.fields["factory-id"])).size !== modules.length) fail("module and factory identities must be unique");
  for (const module of modules) {
    if (!safe(module.fields["factory-id"]!)) fail(`${module.name}: invalid factory-id`);
    for (const field of ["module-id", "adapter-protocol"]) if (!identifier(module.fields[field]!)) fail(`${module.name}: invalid ${field}`);
    if (!digest(module.fields["factory-source-sha256"]!) || !digest(module.fields["manifest-digest"]!) || module.fields["side-effects"] !== "false" || module.fields["authority-effect"] !== "none") fail(`${module.name}: unsafe or invalid module boundary`);
    if (headers.profile === "module-configuration-v2") {
      for (const field of ["runtime-source", "runtime-source-sha256", "compiled-source", "compiled-source-sha256"]) if (!module.fields[field]) fail(`${module.name}: missing ${field}`);
      for (const field of ["runtime-source-sha256", "compiled-source-sha256"]) if (!digest(module.fields[field]!)) fail(`${module.name}: invalid ${field}`);
    }
  }
  for (const capability of capabilities) {
    const module = byName.get(capability.fields.module!);
    if (module?.kind !== "module") fail(`${capability.name}: module reference is invalid`);
    for (const field of ["capability-id", "input-protocol", "output-protocol"]) if (!identifier(capability.fields[field]!)) fail(`${capability.name}: invalid ${field}`);
  }
  if (new Set(capabilities.map((item) => item.fields["capability-id"])).size !== capabilities.length) fail("capability identities must be globally unique");
  const entryTuples = new Set<string>();
  for (const entry of entries) {
    const capability = byName.get(entry.fields.capability!);
    if (capability?.kind !== "capability" || !identifier(entry.fields.consumer!) || !POSTURES.has(entry.fields.posture!)) fail(`${entry.name}: invalid capability, consumer, or posture`);
    const tuple = `${entry.fields.consumer}\0${capability!.fields["capability-id"]}`;
    if (entryTuples.has(tuple)) fail(`${entry.name}: duplicate consumer capability entry`);
    entryTuples.add(tuple);
  }
  return {headers, declarations, configuration, modules, capabilities, entries, byName};
}

export function compileModuleConfiguration(sourcePath: string) {
  const resolved = realpathSync(path.resolve(sourcePath));
  if (path.extname(resolved) !== ".alch") fail("source must be .alch");
  const source = readFileSync(resolved, "utf8");
  const root = realpathSync(path.dirname(resolved));
  const parsed = parse(source);
  const governed = parsed.declarations.find((item) => item.kind === "governed-by")!;
  const decisionPath = realpathSync(path.resolve(root, governed.fields.decision!));
  const decisionBytes = readFileSync(decisionPath);
  if (sha256(decisionBytes) !== governed.fields["decision-sha256"]) fail("adoption decision digest drift");
  const decision = JSON.parse(decisionBytes.toString("utf8"));
  if (decision.decision_state !== "selected" || decision.selected_option_id !== "ARE-MPC-ADOPT" || decision.constitution_adopted !== true || decision.runtime_admitted !== false || decision.effect_authorized !== false || decision.constitution_id !== governed.fields["constitution-id"] || decision.selector !== governed.fields.selector || governed.fields["authority-effect"] !== "none") fail("exact adopted Constitution decision is required");
  const moduleRecords = parsed.modules.map((module) => {
    const sourceFile = realpathSync(path.resolve(root, module.fields["factory-source"]!));
    const sourceDigest = sha256(readFileSync(sourceFile));
    if (sourceDigest !== module.fields["factory-source-sha256"]) fail(`${module.name}: factory source digest drift`);
    const pinnedSource = (sourceKey: string, digestKey: string) => {
      const file = realpathSync(path.resolve(root, module.fields[sourceKey]!));
      const observed = sha256(readFileSync(file));
      if (observed !== module.fields[digestKey]) fail(`${module.name}: ${sourceKey} digest drift`);
      return {path: path.relative(root, file).split(path.sep).join("/"), sha256: observed};
    };
    const runtimeBinding = parsed.headers.profile === "module-configuration-v2" ? (() => {
      const runtime = pinnedSource("runtime-source", "runtime-source-sha256");
      const compiled = pinnedSource("compiled-source", "compiled-source-sha256");
      return {runtime_source: runtime.path, runtime_source_sha256: runtime.sha256, compiled_source: compiled.path, compiled_source_sha256: compiled.sha256};
    })() : {runtime_source: undefined, runtime_source_sha256: undefined, compiled_source: undefined, compiled_source_sha256: undefined};
    const capabilities = parsed.capabilities.filter((item) => item.fields.module === module.name).map((item) => ({capability_id: item.fields["capability-id"], input_protocol: item.fields["input-protocol"], output_protocol: item.fields["output-protocol"]})).sort((left, right) => left.capability_id!.localeCompare(right.capability_id!));
    if (!capabilities.length) fail(`${module.name}: at least one capability is required`);
    const manifestMaterial = {schema_version: "are.module-manifest/v1", module_id: module.fields["module-id"], version: module.fields.version, adapter_protocol: module.fields["adapter-protocol"], capabilities, required_permissions: [], side_effects: false, authority_effect: "none"};
    if (sha256(canonical(manifestMaterial)) !== module.fields["manifest-digest"]) fail(`${module.name}: manifest digest does not match declarations`);
    return {declaration: module.name, factory_id: module.fields["factory-id"], factory_source: path.relative(root, sourceFile).split(path.sep).join("/"), factory_source_sha256: sourceDigest, ...runtimeBinding, module_id: module.fields["module-id"], version: module.fields.version, manifest_digest: module.fields["manifest-digest"], capabilities};
  }).sort((left, right) => left.module_id!.localeCompare(right.module_id!));
  const moduleByDeclaration = new Map(moduleRecords.map((item) => [item.declaration, item]));
  const entryRecords = parsed.entries.map((entry) => {
    const capability = parsed.byName.get(entry.fields.capability!)!;
    const module = moduleByDeclaration.get(capability.fields.module!)!;
    return {entry_id: entry.name, consumer_id: entry.fields.consumer, capability_id: capability.fields["capability-id"], dependency_posture: entry.fields.posture, input_protocol: capability.fields["input-protocol"], output_protocol: capability.fields["output-protocol"], module_id: module.module_id};
  }).sort((left, right) => left.entry_id.localeCompare(right.entry_id));
  const configuration = {schema_version: "are.static-module-configuration/v1", configuration_id: parsed.configuration.fields["configuration-id"], modules: moduleRecords.map(({factory_id, module_id, version, manifest_digest}) => ({factory_id, module_id, version, manifest_digest})), authority_effect: "none"};
  const ontologyNodes = [{id: `configuration:${configuration.configuration_id}`, kind: "configuration", name: parsed.configuration.name}, ...moduleRecords.map((item) => ({id: `module:${item.module_id}`, kind: "module", name: item.declaration})), ...entryRecords.map((item) => ({id: `entry:${item.entry_id}`, kind: "entry", name: item.entry_id}))];
  const ontologyEdges = [...moduleRecords.map((item) => ({from: `configuration:${configuration.configuration_id}`, to: `module:${item.module_id}`, relation: "binds"})), ...entryRecords.map((item) => ({from: `entry:${item.entry_id}`, to: `module:${item.module_id}`, relation: "invokes"}))];
  const ontology = {schema_version: "alchlang.module-configuration-ontology/v1", source: {path: path.basename(resolved), sha256: sha256(source)}, nodes: ontologyNodes, edges: ontologyEdges, selector: governed.fields.selector, ontology_admitted: false, authority_effect: "none"};
  const conformance = {schema_version: "alchlang.module-configuration-conformance/v1", status: "pass", checks: ["exact-adoption-binding", "exact-factory-source-binding", ...(parsed.headers.profile === "module-configuration-v2" ? ["exact-injected-runtime-binding", "exact-compiled-artifact-binding"] : []), "exact-manifest-reconstruction", "module-identity-non-collapse", "entry-semantic-orthogonality", "multiple-explicit-entry-points"].map((check_id) => ({check_id, outcome: "PASS"})), entry_count: entryRecords.length, module_count: moduleRecords.length, runtime_admitted: false, enforcement_active: false, authority_effect: "none"};
  return {profile: parsed.headers.profile, sourcePath: resolved, source, source_sha256: sha256(source), configuration, entries: entryRecords, modules: moduleRecords, ontology, conformance, governance: {decision_path: path.relative(root, decisionPath).split(path.sep).join("/"), decision_sha256: sha256(decisionBytes), constitution_id: governed.fields["constitution-id"], selector: governed.fields.selector}, authority_effect: "none"};
}

export function checkModuleConfiguration(sourcePath: string) {
  const value = compileModuleConfiguration(sourcePath);
  return {status: "valid", profile: value.profile, configuration_id: value.configuration.configuration_id, modules: value.modules.length, entries: value.entries.length, conformance: value.conformance.status, runtime_admitted: false, authority_effect: "none"};
}

export function buildModuleConfiguration(sourcePath: string, outputPath: string) {
  const compiled = compileModuleConfiguration(sourcePath);
  const output = path.resolve(outputPath);
  try { lstatSync(output); fail("output exists"); } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
  mkdirSync(path.dirname(output), {recursive: true});
  const stage = mkdtempSync(path.join(path.dirname(output), ".alch-module-configuration-"));
  const write = (name: string, value: string) => { const target = path.join(stage, name); mkdirSync(path.dirname(target), {recursive: true}); writeFileSync(target, value, {flag: "wx"}); };
  try {
    write("runtime/configuration.json", json(compiled.configuration));
    write("runtime/entrypoints.json", json({schema_version: "are.module-entrypoints/v1-candidate", configuration_id: compiled.configuration.configuration_id, entries: compiled.entries, runtime_admitted: false, authority_effect: "none"}));
    write("provenance/alch/source.alch", compiled.source);
    write("provenance/ontology.json", json(compiled.ontology));
    write("provenance/governance-binding.json", json({...compiled.governance, constitution_adopted: true, runtime_admitted: false, authority_effect: "none"}));
    if (compiled.profile === "module-configuration-v2") write("provenance/runtime-bindings.json", json({schema_version: "alchlang.module-runtime-bindings/v1-candidate", modules: compiled.modules, authority_effect: "none"}));
    write("evidence/conformance.json", json(compiled.conformance));
    const inventory = Object.fromEntries(files(stage).sort().map((file) => [path.relative(stage, file).split(path.sep).join("/"), sha256(readFileSync(file))]));
    write("manifest.json", json({schema_version: "alchlang.module-configuration-build/v1", profile: compiled.profile, source_sha256: compiled.source_sha256, configuration_id: compiled.configuration.configuration_id, pipeline: ["alch-source", "module-configuration-ontology", "runtime-configuration", ...(compiled.profile === "module-configuration-v2" ? ["injected-runtime-binding"] : []), "entrypoint-projection", "conformance-evidence"], files: inventory, ontology_admitted: false, constitution_adopted: true, runtime_admitted: false, enforcement_active: false, authority_effect: "none"}));
    renameSync(stage, output);
    return {status: "built", profile: compiled.profile, output, files: Object.keys(inventory).length + 1, modules: compiled.modules.length, entries: compiled.entries.length, runtime_admitted: false, authority_effect: "none"};
  } catch (error) { rmSync(stage, {recursive: true, force: true}); throw error; }
}
