import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync, realpathSync } from "node:fs";
import path from "node:path";
import { TextDecoder } from "node:util";
import { CompilationRejected } from "./model.js";
import { digest } from "./domainspec-profile.js";
import { loadDomainSpecCompiler } from "./domainspec-cli.js";
import { prepareApplicationExecutable } from "./application-executable.js";
import { deriveApplicationIntegrationBindings } from "./application-integration-derivation.js";
import { loadApplicationEvidenceFiles } from "./application-evidence-files.js";
import { validateExactFormalSourceRef, type ExactFormalSourceRef } from "./formal-claim-lowering.js";
import { parseDomainSource } from "./parser.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { ApplicationInboundEndpoint } from "./application-integration.js";

const fail = (message: string): never => {
  throw new CompilationRejected([{ code: "APPLICATION_FILE_INPUT", path: "$application", message }]);
};
const MAX_FILE = 16 * 1024 * 1024, MAX_TOTAL = 64 * 1024 * 1024;
const utf8 = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });
const required = ["schema_version", "source_sha256", "bindings", "interpretation", "execution", "evidence"];
const optional = ["persistence", "messaging", "external_api", "runtime_profile", "observation"];
const referenceKeys = ["bindings", "interpretation", "execution", "persistence", "messaging", "external_api", "observation"];
const namespacePattern = /^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)*$/;
const runtimeIdentityPattern = /^[a-z][a-z0-9]*(?:[.:-][a-z0-9]+)*$/;
const entryIdPattern = /^[A-Za-z_][A-Za-z0-9_-]*$/;

/** Bootstrap files have no containing reference yet; still read bounded regular bytes only. */
function readInput(root: string, relative: string): Buffer {
  validateExactFormalSourceRef({ path: relative, sha256: "0".repeat(64), size_bytes: 1, current: true }, "$application/path");
  let target = root;
  for (const part of relative.split("/")) {
    target = path.join(target, part);
    if (lstatSync(target).isSymbolicLink()) fail("symlink input path");
  }
  if (realpathSync(target) !== target) fail("input path changed");
  const fd = openSync(target, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const before = fstatSync(fd);
    if (!before.isFile() || before.size > MAX_FILE) fail("input must be a bounded regular file");
    const bytes = readFileSync(fd), after = fstatSync(fd), current = lstatSync(target);
    if (bytes.length !== before.size || before.size !== after.size || before.mtimeMs !== after.mtimeMs || before.ctimeMs !== after.ctimeMs
      || current.isSymbolicLink() || current.ino !== after.ino || current.dev !== after.dev || realpathSync(target) !== target) fail("input changed while reading");
    return bytes;
  } finally { closeSync(fd); }
}
function decode(bytes: Buffer, role: string): unknown {
  try { return JSON.parse(utf8.decode(bytes)); } catch { return fail(`invalid UTF-8 JSON for ${role}`); }
}
function freezeJson<T>(value: T): T {
  if (value && typeof value === "object") { Object.values(value).forEach(freezeJson); Object.freeze(value); }
  return value;
}
type Snapshot = { root: string; source: string; companion: string; sourceHash: string; companionHash: string; refs: ExactFormalSourceRef[] };
const snapshots = new WeakMap<object, Snapshot>();
function current(snapshot: Snapshot): void {
  if (realpathSync(snapshot.root) !== snapshot.root || !lstatSync(snapshot.root).isDirectory()) fail("application root changed");
  if (digest(readInput(snapshot.root, snapshot.source)) !== snapshot.sourceHash
    || digest(readInput(snapshot.root, snapshot.companion)) !== snapshot.companionHash) fail("source or companion changed");
  loadApplicationEvidenceFiles(snapshot.root, snapshot.refs);
}

export interface ApplicationFileOptions {
  /** Relative to the selected .alch source directory; defaults to <source>.application.json. */
  companion?: string;
  packageRoot?: string;
  /** Required for a v2 composition. There is deliberately no first-entry default. */
  entry?: string;
}

interface CompositionSource extends ExactFormalSourceRef { namespace: string }
interface CompositionEntry {
  id: string;
  namespace: string;
  runtime_identity: string;
  sources: string[];
  endpoint: string;
  runtime_profile?: string;
  bindings: ExactFormalSourceRef;
  interpretation: ExactFormalSourceRef;
  execution: ExactFormalSourceRef;
  evidence: ExactFormalSourceRef[];
  persistence?: ExactFormalSourceRef;
  messaging?: ExactFormalSourceRef;
  external_api?: ExactFormalSourceRef;
  observation?: ExactFormalSourceRef;
}

function exactKeys(value: Record<string, unknown>, allowed: readonly string[], label: string): void {
  if (Object.keys(value).some(key => !allowed.includes(key))) fail(`closed ${label} required`);
}

function refWithNamespace(value: unknown, index: number): CompositionSource {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("composition source must be an object");
  const row = value as Record<string, unknown>;
  exactKeys(row, ["namespace", "path", "sha256", "size_bytes", "current"], "composition source");
  if (typeof row.namespace !== "string" || !namespacePattern.test(row.namespace)) fail(`invalid source namespace at ${index}`);
  return { namespace: row.namespace as string, ...validateExactFormalSourceRef({ path: row.path, sha256: row.sha256, size_bytes: row.size_bytes, current: row.current }, `$application/sources/${index}`) };
}

function parseCompositionEntry(value: unknown, index: number): CompositionEntry {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail("composition entry must be an object");
  const row = value as Record<string, unknown>;
  const requiredKeys = ["id", "namespace", "runtime_identity", "sources", "endpoint", "bindings", "interpretation", "execution", "evidence"];
  const allowed = [...requiredKeys, "runtime_profile", "persistence", "messaging", "external_api", "observation"];
  exactKeys(row, allowed, "composition entry");
  if (requiredKeys.some(key => !Object.hasOwn(row, key))) fail(`composition entry ${index} is incomplete`);
  if (typeof row.id !== "string" || !entryIdPattern.test(row.id)) fail(`invalid composition entry id at ${index}`);
  if (typeof row.namespace !== "string" || !namespacePattern.test(row.namespace)) fail(`invalid entry namespace at ${index}`);
  if (typeof row.runtime_identity !== "string" || !runtimeIdentityPattern.test(row.runtime_identity)) fail(`invalid runtime identity at ${index}`);
  if (!Array.isArray(row.sources) || row.sources.length < 2 || row.sources.some(item => typeof item !== "string" || !namespacePattern.test(item))) fail(`entry ${row.id} requires at least two exact source namespaces`);
  const id = row.id as string, namespace = row.namespace as string, runtimeIdentity = row.runtime_identity as string;
  const sourceNames = row.sources as string[];
  if (new Set(sourceNames).size !== sourceNames.length) fail(`entry ${id} repeats a source namespace`);
  if (typeof row.endpoint !== "string" || !entryIdPattern.test(row.endpoint)) fail(`entry ${row.id} requires one endpoint`);
  if (Object.hasOwn(row, "runtime_profile") && (typeof row.runtime_profile !== "string" || !entryIdPattern.test(row.runtime_profile))) fail(`entry ${row.id} has an invalid runtime profile`);
  if (!Array.isArray(row.evidence) || row.evidence.length > 256) fail(`entry ${row.id} requires bounded evidence references`);
  const endpoint = row.endpoint as string, evidenceRows = row.evidence as unknown[];
  const parsed: CompositionEntry = {
    id, namespace, runtime_identity: runtimeIdentity,
    sources: [...sourceNames], endpoint,
    bindings: validateExactFormalSourceRef(row.bindings, `$application/entries/${index}/bindings`),
    interpretation: validateExactFormalSourceRef(row.interpretation, `$application/entries/${index}/interpretation`),
    execution: validateExactFormalSourceRef(row.execution, `$application/entries/${index}/execution`),
    evidence: evidenceRows.map((ref, evidenceIndex) => validateExactFormalSourceRef(ref, `$application/entries/${index}/evidence/${evidenceIndex}`)),
  };
  if (typeof row.runtime_profile === "string") parsed.runtime_profile = row.runtime_profile;
  for (const role of ["persistence", "messaging", "external_api", "observation"] as const) {
    if (Object.hasOwn(row, role)) parsed[role] = validateExactFormalSourceRef(row[role], `$application/entries/${index}/${role}`);
  }
  const integrations = [parsed.persistence, parsed.messaging, parsed.external_api].filter(Boolean);
  if (integrations.length !== 0 && integrations.length !== 3) fail(`entry ${row.id} integration companions must be supplied together or derived together`);
  return parsed;
}

function sourceIdentity(source: string, role: string) {
  const domains = [...source.matchAll(/^domain\s+([A-Za-z_][\w.-]*)(?:\s+"([^"]+)")?$/gm)];
  const owners = [...source.matchAll(/^owner\s+([A-Za-z_][\w.-]*)$/gm)];
  const profiles = [...source.matchAll(/^profile\s+(.+)$/gm)];
  if (domains.length !== 1 || owners.length !== 1 || profiles.length !== 1 || profiles[0]![1] !== "application-v1") fail(`${role} must declare exactly one domain, owner, and application-v1 profile`);
  return { domain: domains[0]![1]!, title: domains[0]![2] ?? domains[0]![1]!, owner: owners[0]![1]! };
}

function withoutIdentity(source: string): string {
  return source.split(/\r?\n/).filter(line => !/^(?:domain\s+|owner\s+|profile\s+application-v1\s*$)/.test(line)).join("\n").replace(/^\n+|\n+$/g, "");
}

function sourceDeclarations(source: string) {
  const pattern = /^(formal-claim|entity|value-object|enum|state-machine|invariant|rule|operation|event|query|calculation|mapping|policy|workflow|interface|subscription|publication|inbound-endpoint|outbound-call|outbound-write|persistence|runtime-profile|realization)\s+([A-Za-z_][\w.-]*):?$/gm;
  return [...source.matchAll(pattern)].map(match => ({ kind: match[1]!, id: match[2]! }));
}

function composeSources(rows: CompositionSource[], bytes: ReadonlyMap<string, Buffer>, expected: { domain: string; title: string; owner: string }): string {
  return rows.map((row, index) => {
    let source: string;
    try { source = utf8.decode(bytes.get(row.path)!); } catch { return fail(`source namespace ${row.namespace} must be valid UTF-8`); }
    const identity = sourceIdentity(source, `source namespace ${row.namespace}`);
    if (identity.domain !== expected.domain || identity.title !== expected.title || identity.owner !== expected.owner) fail(`source namespace ${row.namespace} changes application identity`);
    return index === 0 ? source.replace(/\s+$/, "") : withoutIdentity(source);
  }).join("\n\n") + "\n";
}

/** File transport only. Meaning, interpretation, profile choices and acceptance remain explicit. */
export async function loadApplicationFile(sourcePath: string, options: ApplicationFileOptions = {}) {
  const absolute = path.resolve(sourcePath), root = path.dirname(absolute), sourceName = path.basename(absolute);
  if (path.extname(absolute) !== ".alch" || realpathSync(root) !== root) fail("a real application directory and .alch source are required");
  const companion = options.companion ?? `${sourceName}.application.json`;
  const sourceBytes = readInput(root, sourceName), companionBytes = readInput(root, companion);
  let source: string;
  try { source = utf8.decode(sourceBytes); } catch { return fail("source must be valid UTF-8"); }
  const parsed = decode(companionBytes, "companion");
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return fail("companion must be an object");
  const manifest = parsed as Record<string, unknown>;
  if (manifest.source_sha256 !== digest(sourceBytes)) fail("companion source digest differs");

  let applicationSource = source;
  let roles = new Map<string, ExactFormalSourceRef>();
  let evidence: ExactFormalSourceRef[] = [];
  let refs: ExactFormalSourceRef[] = [];
  let runtimeProfile: string | undefined;
  let entryManifest: Record<string, unknown> | undefined;

  if (manifest.schema_version === "alchlang.application-file/v1-candidate") {
    if (options.entry !== undefined) fail("v1 application files do not accept an entry selection");
    if (required.some(k => !Object.hasOwn(manifest, k)) || Object.keys(manifest).some(k => ![...required, ...optional].includes(k))) return fail("closed application companion required");
    if (!Array.isArray(manifest.evidence) || manifest.evidence.length > 256) return fail("bounded explicit evidence references required");
    if (Object.hasOwn(manifest, "runtime_profile") && (typeof manifest.runtime_profile !== "string" || !manifest.runtime_profile.trim())) fail("explicit runtime profile name required");
    for (const role of referenceKeys) if (Object.hasOwn(manifest, role)) roles.set(role, validateExactFormalSourceRef(manifest[role], `$application/${role}`));
    evidence = manifest.evidence.map((ref, i) => validateExactFormalSourceRef(ref, `$application/evidence/${i}`));
    refs = [...roles.values(), ...evidence];
    runtimeProfile = typeof manifest.runtime_profile === "string" ? manifest.runtime_profile : undefined;
  } else if (manifest.schema_version === "alchlang.application-file/v2-candidate") {
    exactKeys(manifest, ["schema_version", "source_sha256", "sources", "entries"], "application composition companion");
    if (!Array.isArray(manifest.sources) || manifest.sources.length < 2 || manifest.sources.length > 32) fail("composition requires 2..32 bounded sources");
    if (!Array.isArray(manifest.entries) || manifest.entries.length < 2 || manifest.entries.length > 32) fail("composition requires 2..32 explicit entries");
    if (!options.entry) fail("composition requires an explicit entry selection");
    const sourceRows = (manifest.sources as unknown[]).map(refWithNamespace);
    const entries = (manifest.entries as unknown[]).map(parseCompositionEntry);
    if (new Set(sourceRows.map(row => row.namespace)).size !== sourceRows.length) fail("duplicate source namespace");
    if (new Set(sourceRows.map(row => row.path)).size !== sourceRows.length) fail("one source path cannot carry multiple namespaces");
    if (new Set(entries.map(entry => entry.id)).size !== entries.length) fail("duplicate composition entry id");
    if (new Set(entries.map(entry => entry.namespace)).size !== entries.length) fail("duplicate entry namespace");
    if (new Set(entries.map(entry => entry.runtime_identity)).size !== entries.length) fail("duplicate runtime identity");
    const byNamespace = new Map(sourceRows.map(row => [row.namespace, row]));
    for (const entry of entries) for (const selected of entry.sources) if (!byNamespace.has(selected)) fail(`entry ${entry.id} selects unknown source namespace ${selected}`);
    for (const row of sourceRows) if (!entries.some(entry => entry.sources.includes(row.namespace))) fail(`source namespace ${row.namespace} is unreachable from every entry`);
    const allRefs = [...sourceRows.map(({ namespace: _namespace, ...ref }) => ref), ...entries.flatMap(entry => [entry.bindings, entry.interpretation, entry.execution,
      ...entry.evidence, ...[entry.persistence, entry.messaging, entry.external_api, entry.observation].filter((ref): ref is ExactFormalSourceRef => ref !== undefined)])];
    const refByPath = new Map<string, ExactFormalSourceRef>();
    for (const ref of allRefs) {
      const prior = refByPath.get(ref.path);
      if (prior && (prior.sha256 !== ref.sha256 || prior.size_bytes !== ref.size_bytes || prior.current !== ref.current)) fail(`conflicting exact references for ${ref.path}`);
      refByPath.set(ref.path, ref);
    }
    refs = [...refByPath.values()];
    const selected = entries.find(entry => entry.id === options.entry) ?? fail(`unknown composition entry ${options.entry}`);
    const preliminaryTotal = refs.reduce((total, ref) => total + ref.size_bytes, sourceBytes.length + companionBytes.length);
    if (preliminaryTotal > MAX_TOTAL) fail("selected input byte limit exceeded");
    const allFiles = loadApplicationEvidenceFiles(root, refs);
    const control = sourceIdentity(source, "composition root");
    const controlResidue = source.split(/\r?\n/).filter(line => line.trim() && !line.trimStart().startsWith("#")
      && !/^(?:domain\s+|owner\s+|profile\s+application-v1\s*$)/.test(line));
    if (controlResidue.length) fail("composition root may contain identity only; declarations belong to named source partitions");
    const records = entries.map(entry => {
      const selectedSources = entry.sources.map(namespace => byNamespace.get(namespace)!);
      const combined = composeSources(selectedSources, allFiles, control);
      const partitions = selectedSources.map(row => ({ namespace: row.namespace,
        declarations: sourceDeclarations(utf8.decode(allFiles.get(row.path)!)) }));
      const carrier = parseDomainSource(combined).carrier as unknown as ApplicationFormalSource;
      const endpoint = carrier.integrations.find((integration): integration is ApplicationInboundEndpoint => integration.kind === "inbound-endpoint" && integration.id === entry.endpoint)
        ?? fail(`entry ${entry.id} selects an undeclared inbound endpoint ${entry.endpoint}`);
      if (entry.runtime_profile && !carrier.runtime_profiles?.some(profile => profile.id === entry.runtime_profile)) fail(`entry ${entry.id} selects an undeclared runtime profile ${entry.runtime_profile}`);
      const routeKeys = new Set<string>();
      for (const route of carrier.integrations.filter((integration): integration is ApplicationInboundEndpoint => integration.kind === "inbound-endpoint")) {
        const key = `${route.protocol.method} ${route.protocol.path}`;
        if (routeKeys.has(key)) fail(`duplicate composition route ${key} in entry ${entry.id}`);
        routeKeys.add(key);
      }
      return { id: entry.id, namespace: entry.namespace, runtime_identity: entry.runtime_identity,
        sources: [...entry.sources], partitions, endpoint: entry.endpoint, operation: endpoint.operation.ref,
        route: { method: endpoint.protocol.method, path: endpoint.protocol.path }, runtime_profile: entry.runtime_profile ?? null,
        source_sha256: digest(combined), source_bytes: Buffer.byteLength(combined), source: combined };
    });
    const selectedRecord = records.find(record => record.id === selected.id)!;
    applicationSource = selectedRecord.source;
    runtimeProfile = selected.runtime_profile;
    roles = new Map<string, ExactFormalSourceRef>([["bindings", selected.bindings], ["interpretation", selected.interpretation], ["execution", selected.execution]]);
    for (const role of ["persistence", "messaging", "external_api", "observation"] as const) if (selected[role]) roles.set(role, selected[role]!);
    evidence = selected.evidence;
    entryManifest = freezeJson({ schema_version: "alchlang.application-entry-manifest/v1-candidate",
      application: { domain: control.domain, title: control.title, owner: control.owner }, selected_entry: selected.id,
      sources: sourceRows.map(row => ({ namespace: row.namespace, path: row.path, sha256: row.sha256, size_bytes: row.size_bytes })),
      entries: records.map(({ source: _source, ...record }) => record), authority_effect: "none" });
  } else return fail("closed application companion required");

  if (refs.some(ref => ref.size_bytes > MAX_FILE) || refs.reduce((total, ref) => total + ref.size_bytes, sourceBytes.length + companionBytes.length) > MAX_TOTAL) fail("selected input byte limit exceeded");
  if (refs.some(ref => ref.path === sourceName || ref.path === companion)) fail("source and companion cannot be selected as payload references");
  const files = loadApplicationEvidenceFiles(root, refs);
  const value = (role: string) => decode(files.get(roles.get(role)!.path)!, role);
  const sources = new Map(evidence.map(ref => [ref.path, files.get(ref.path)!]));
  const compiler = await loadDomainSpecCompiler(options.packageRoot);
  const integrationRoles = ["persistence", "messaging", "external_api"] as const;
  const suppliedIntegrations = integrationRoles.filter(role => roles.has(role));
  if (suppliedIntegrations.length !== 0 && suppliedIntegrations.length !== integrationRoles.length) fail("integration companions must be supplied together or derived together");
  const derived = suppliedIntegrations.length === 0 && runtimeProfile
    ? deriveApplicationIntegrationBindings(applicationSource, runtimeProfile, compiler) : undefined;
  const candidate = prepareApplicationExecutable(applicationSource, value("bindings"), sources, value("interpretation"), value("execution"), compiler,
    roles.has("persistence") ? { binding: value("persistence"), compiler } : derived ? { binding: derived.persistence, compiler } : undefined,
    roles.has("messaging") ? { binding: value("messaging"), compiler } : derived ? { binding: derived.messaging, compiler } : undefined,
    roles.has("external_api") ? { binding: value("external_api"), compiler } : derived ? { binding: derived.externalApi, compiler } : undefined,
    runtimeProfile ? { profile: runtimeProfile, compiler } : undefined);
  const snapshot: Snapshot = { root, source: sourceName, companion, sourceHash: digest(sourceBytes), companionHash: digest(companionBytes), refs };
  current(snapshot);
  const inputs = Object.freeze(Object.fromEntries([[sourceName, snapshot.sourceHash], [companion, snapshot.companionHash], ...refs.map(ref => [ref.path, ref.sha256])]));
  const result = Object.freeze({ candidate, compiler, ...(derived ? { integration_derivation: derived.trace } : {}),
    ...(roles.has("observation") ? { observation: freezeJson(value("observation")) } : {}),
    ...(entryManifest ? { entry_manifest: entryManifest } : {}),
    inputs, source_path: absolute, authority_effect: "none" as const });
  snapshots.set(result, snapshot);
  return result;
}

/** Re-read exact selected inputs before a caller publishes generated output. */
export function assertApplicationFileCurrent(loaded: Awaited<ReturnType<typeof loadApplicationFile>>): void {
  const snapshot = snapshots.get(loaded);
  if (!snapshot) return fail("use the current file-loaded application");
  current(snapshot);
}
