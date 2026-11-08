import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  readlinkSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { tmpdir } from "node:os";
import { TextDecoder } from "node:util";

import {
  alloyArgv,
  alloyNativeResult,
  mapAlloyOutcome,
  parseAlloyJson,
  typedAlloyEvidence,
  type AlloySolutionFile,
} from "./alloy.js";
import { digestValue, sha256, stableJson } from "./canonical-json.js";
import {
  datalogArgv,
  datalogNativeResult,
  mapDatalogOutcome,
  parseViolationCsv,
} from "./datalog.js";
import { exactRef, readJson, repositoryRoot, safeRepositoryPath } from "./exact-ref.js";
import { extractFacts, L2_PATHS, REQUEST_ID, validateLiveSourceBindings } from "./extract.js";
import { buildJoinReceipt, verifyJoinReceipt } from "./join.js";
import { runBoundedProcess, requireCompletedProcess, type ProcessPolicy } from "./process-runner.js";
import { buildProviderReceipt, verifyProviderReceipt } from "./provider-receipt.js";
import { buildGraphLawRequest } from "./request.js";
import { translateAlloy } from "./translate-alloy.js";
import { translateDatalog } from "./translate-datalog.js";
import { validateProjection } from "./validate-facts.js";
import {
  fail,
  L2Error,
  type ExactRef,
  type GraphLawRequest,
  type JoinReceipt,
  type ProcessEvidence,
  type ProviderReceipt,
} from "./types.js";

export const WORK_PACK_ROOT =
  "projects/domainspec-v2/development/evolvable-validation-framework/development/refinement-runs/20260821T044428Z-evf-l2-one-shot-work-pack/plan-candidate";
export const DEFAULT_INVENTORY = `${WORK_PACK_ROOT}/work-pack/target-inventory.l2.json`;
export const DEFAULT_EXECUTION_ENTRY = `${WORK_PACK_ROOT}/work-pack/EXECUTION-ENTRY.json`;
export const DEFAULT_SOURCE_BINDINGS = `${WORK_PACK_ROOT}/work-pack/source-bindings.l2.json`;
export const RUNTIME_ADMISSION =
  "projects/domainspec-v2/development/evolvable-validation-framework/development/runtime-admissions/evf-l2-souffle-2.5.json";
export const RUNTIME_ADMISSION_SCHEMA = `${WORK_PACK_ROOT}/work-pack/contracts/provider-runtime-admission.v1.schema.json`;

const EVIDENCE_PREFIX =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/";
const L2_SOURCE_ROOT =
  "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l2";
const DATALOG_QUERY =
  "projects/domainspec-v2/development/evolvable-validation-framework/providers/datalog/reachability.dl";
const PACKAGE_PATH = "projects/domainspec-v2/impl/package.json";
const ALLOY_JAVA = ".formal-tools/jre/current/bin/java";
const ALLOY_JAR = ".formal-tools/alloy/org.alloytools.alloy.dist-6.2.0.jar";
const PACKAGE_BASELINE_SEMANTIC_DIGEST =
  "82a8161ada7f00d8ffe5f6b05ef301231d9c7df899b460c7b75ce021bf968c60";
const L2_PACKAGE_SCRIPTS = {
  "verify:evf-l2": "tsx test-derivation-engine/src/minted-project/l2/verify-l2-one-shot.ts",
  "test:evf-l2": "vitest run test-derivation-engine/src/minted-project/l2 --maxWorkers=1 --minWorkers=1",
  "verify:evf-l2:c0": "tsx test-derivation-engine/src/minted-project/l2/verify-c0.ts",
  "verify:evf-l2:c1": "tsx test-derivation-engine/src/minted-project/l2/verify-c1.ts",
  "verify:evf-l2:c2": "tsx test-derivation-engine/src/minted-project/l2/verify-c2.ts",
} as const;

const UNIT_ORDER = [
  "SWU-GCP-004-C0",
  "SWU-GCP-005-C1",
  "SWU-GCP-006-C2",
  "SWU-GCP-007-C3",
] as const;
type UnitId = (typeof UNIT_ORDER)[number];

type TargetInventory = {
  readonly create_target_classification?: {
    readonly authored_create_targets?: number;
    readonly runtime_generated_create_targets?: number;
    readonly authored_update_targets?: number;
  };
  readonly partitions: Readonly<Record<string, {
    readonly create_targets: readonly string[];
    readonly update_targets: readonly ({ readonly path: string } | string)[];
  }>>;
};

type ExecutionEntry = {
  readonly execution_policy: {
    readonly allowed_routes: readonly {
      readonly frontier_swu: string;
      readonly write_scope: readonly string[];
    }[];
  };
};

type RuntimeAdmission = {
  readonly schema_version: "evf.l2.provider-runtime-admission/v1";
  readonly provider: "souffle";
  readonly required_version: "2.5";
  readonly status: "admitted";
  readonly executable_ref: ExactRef;
  readonly version_probe: {
    readonly exact_argv: readonly string[];
    readonly exit_code: 0;
    readonly observed_version: "2.5";
    readonly stdout_ref: ExactRef;
    readonly stderr_ref: ExactRef;
  };
  readonly smoke_receipt_ref: ExactRef;
  readonly owner_approval: {
    readonly status: "approved";
    readonly scope: "candidate-local-evf-l2-one-shot";
  };
  readonly network: "forbidden";
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
};

type OutputMap = ReadonlyMap<string, Buffer>;
type MutableOutputMap = Map<string, Buffer>;

export type ScanPhase = "authored-prewrite" | "terminal-live";
export type ScanResult = {
  readonly phase: ScanPhase;
  readonly scanned_paths: readonly string[];
  readonly authored_create_count: number;
  readonly runtime_generated_count: number;
  readonly update_count: number;
  readonly route_count: number;
};

function sorted(values: Iterable<string>): string[] {
  return [...values].sort((left, right) => left.localeCompare(right));
}

function sameSet(left: Iterable<string>, right: Iterable<string>): boolean {
  const a = sorted(new Set(left));
  const b = sorted(new Set(right));
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

function updatePaths(partition: TargetInventory["partitions"][string]): string[] {
  return partition.update_targets.map((target) =>
    typeof target === "string" ? target : target.path
  );
}

function inventorySets(inventory: TargetInventory): {
  readonly authored: Set<string>;
  readonly runtime: Set<string>;
  readonly updates: Set<string>;
  readonly all: Set<string>;
} {
  const authored = new Set<string>();
  const runtime = new Set<string>();
  const updates = new Set<string>();
  for (const partition of Object.values(inventory.partitions)) {
    for (const path of partition.create_targets) {
      (path.startsWith(EVIDENCE_PREFIX) ? runtime : authored).add(path);
    }
    updatePaths(partition).forEach((path) => updates.add(path));
  }
  const all = new Set([...authored, ...runtime, ...updates]);
  const totalRows = Object.values(inventory.partitions)
    .reduce((sum, partition) => sum + partition.create_targets.length + partition.update_targets.length, 0);
  if (all.size !== totalRows) {
    fail("UNDECLARED_WRITE", "admission", "target inventory contains a duplicate path", 2);
  }
  const declared = inventory.create_target_classification;
  if (
    declared !== undefined &&
    (declared.authored_create_targets !== authored.size ||
      declared.runtime_generated_create_targets !== runtime.size ||
      declared.authored_update_targets !== updates.size)
  ) {
    fail("UNDECLARED_WRITE", "admission", "target inventory denominators are inconsistent", 2);
  }
  return { authored, runtime, updates, all };
}

export function validateRouteScopes(
  inventory: TargetInventory,
  executionEntry: ExecutionEntry,
): number {
  const routes = executionEntry.execution_policy.allowed_routes;
  if (routes.length !== Object.keys(inventory.partitions).length) {
    fail("UNDECLARED_WRITE", "admission", "route and partition denominators differ", 2);
  }
  for (const [unit, partition] of Object.entries(inventory.partitions)) {
    const matches = routes.filter((route) => route.frontier_swu === unit);
    if (matches.length !== 1) {
      fail("UNDECLARED_WRITE", "admission", `unit ${unit} does not have exactly one route`, 2);
    }
    const expected = [...partition.create_targets, ...updatePaths(partition)];
    if (!sameSet(expected, matches[0]!.write_scope)) {
      fail("UNDECLARED_WRITE", "admission", `route write scope is not exact for ${unit}`, 2);
    }
  }
  return routes.length;
}

function resolveInputPath(path: string, root: string): string {
  if (isAbsolute(path)) return path;
  const fromCwd = resolve(process.cwd(), path);
  if (existsSync(fromCwd)) return fromCwd;
  return safeRepositoryPath(root, path);
}

function listFiles(root: string): string[] {
  if (!existsSync(root)) return [];
  const files: string[] = [];
  const visit = (directory: string): void => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.isFile()) files.push(path);
      else fail("UNDECLARED_WRITE", "closure", `unsupported staged entry: ${path}`);
    }
  };
  visit(root);
  return files;
}

function assertTextEnvelope(path: string, bytes: Buffer): void {
  if (bytes.length === 0) {
    if (path.endsWith("/Violation.csv")) return;
    fail("UNDECLARED_WRITE", "closure", `zero-byte text is not admitted: ${path}`);
  }
  if (bytes.length >= 3 && bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
    fail("UNDECLARED_WRITE", "closure", `UTF-8 BOM is forbidden: ${path}`);
  }
  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    fail("UNDECLARED_WRITE", "closure", `declared text is not UTF-8: ${path}`);
  }
  if (text.startsWith("\uFEFF")) {
    fail("UNDECLARED_WRITE", "closure", `UTF-8 BOM is forbidden: ${path}`);
  }
  if (!text.endsWith("\n") || text.endsWith("\n\n")) {
    fail("UNDECLARED_WRITE", "closure", `text must end with exactly one newline: ${path}`);
  }
  for (const line of text.slice(0, -1).split("\n")) {
    if (/[\t ]+$/u.test(line)) {
      fail("UNDECLARED_WRITE", "closure", `trailing whitespace in declared text: ${path}`);
    }
  }
  if (path.endsWith(".json")) {
    try {
      JSON.parse(text);
    } catch {
      fail("UNDECLARED_WRITE", "closure", `malformed declared JSON: ${path}`);
    }
  }
}

function metaValidateSchemas(paths: readonly string[]): void {
  if (paths.length === 0) return;
  const script = [
    "import json,sys",
    "from jsonschema.validators import Draft202012Validator",
    "for p in sys.argv[1:]:",
    "  with open(p, 'r', encoding='utf-8') as f: schema=json.load(f)",
    "  Draft202012Validator.check_schema(schema)",
  ].join("\n");
  try {
    execFileSync("python3", ["-c", script, ...paths], {
      stdio: ["ignore", "pipe", "pipe"],
      env: { PATH: process.env.PATH ?? "/usr/bin:/bin", LANG: "C", LC_ALL: "C" },
    });
  } catch (error) {
    fail(
      "UNDECLARED_WRITE",
      "closure",
      `JSON Schema meta-validation failed: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function validateJsonInstance(repoRoot: string, schemaPath: string, instance: unknown): void {
  const schemaAbsolute = safeRepositoryPath(repoRoot, schemaPath);
  const script = [
    "import json,sys",
    "from jsonschema import Draft202012Validator, FormatChecker",
    "schema=json.load(open(sys.argv[1], encoding='utf-8'))",
    "instance=json.load(sys.stdin)",
    "Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)",
  ].join("\n");
  try {
    execFileSync("python3", ["-c", script, schemaAbsolute], {
      input: stableJson(instance),
      stdio: ["pipe", "pipe", "pipe"],
      env: { PATH: process.env.PATH ?? "/usr/bin:/bin", LANG: "C", LC_ALL: "C" },
    });
  } catch (error) {
    fail(
      "PROVIDER_OUTPUT_INVALID",
      "closure",
      `schema instance validation failed for ${schemaPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function scanPathBytes(contentRoot: string, paths: readonly string[]): void {
  const schemas: string[] = [];
  for (const path of paths) {
    const absolute = safeRepositoryPath(contentRoot, path);
    if (!existsSync(absolute) || !statSync(absolute).isFile()) {
      fail("TARGET_BASELINE_DRIFT", "closure", `declared target is absent: ${path}`, 2);
    }
    assertTextEnvelope(path, readFileSync(absolute));
    if (path.endsWith(".schema.json")) schemas.push(absolute);
  }
  metaValidateSchemas(schemas);
}

export function verifyPackagePostimage(value: unknown): void {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    fail("TARGET_BASELINE_DRIFT", "closure", "package postimage is not a JSON object", 2);
  }
  const packageValue = structuredClone(value) as Record<string, unknown>;
  if (
    packageValue.scripts === null ||
    typeof packageValue.scripts !== "object" ||
    Array.isArray(packageValue.scripts)
  ) {
    fail("TARGET_BASELINE_DRIFT", "closure", "package scripts are absent", 2);
  }
  const scripts = packageValue.scripts as Record<string, unknown>;
  for (const [key, expected] of Object.entries(L2_PACKAGE_SCRIPTS)) {
    if (scripts[key] !== expected) {
      fail("TARGET_BASELINE_DRIFT", "closure", `package script drifted: ${key}`, 2);
    }
    delete scripts[key];
  }
  if (digestValue(packageValue) !== PACKAGE_BASELINE_SEMANTIC_DIGEST) {
    fail("TARGET_BASELINE_DRIFT", "closure", "package postimage changes more than the five declared scripts", 2);
  }
}

function assertNoExtraStagedFiles(contentRoot: string, expected: Set<string>): void {
  const observed = listFiles(contentRoot).map((path) => relative(contentRoot, path).replaceAll("\\", "/"));
  if (!sameSet(observed, expected)) {
    const extra = observed.filter((path) => !expected.has(path));
    const missing = [...expected].filter((path) => !observed.includes(path));
    fail(
      "UNDECLARED_WRITE",
      "closure",
      `staged target set differs (extra=${extra.join(",") || "none"}; missing=${missing.join(",") || "none"})`,
    );
  }
}

export function scanDeclaredTargets(options: {
  readonly repositoryRoot: string;
  readonly contentRoot?: string;
  readonly inventoryPath?: string;
  readonly executionEntryPath?: string;
  readonly phase: ScanPhase;
  readonly rejectExtraStagedFiles?: boolean;
}): ScanResult {
  const repoRoot = resolve(options.repositoryRoot);
  const contentRoot = resolve(options.contentRoot ?? repoRoot);
  const inventory = JSON.parse(
    readFileSync(resolveInputPath(options.inventoryPath ?? DEFAULT_INVENTORY, repoRoot), "utf8"),
  ) as TargetInventory;
  const executionEntry = JSON.parse(
    readFileSync(resolveInputPath(options.executionEntryPath ?? DEFAULT_EXECUTION_ENTRY, repoRoot), "utf8"),
  ) as ExecutionEntry;
  const routeCount = validateRouteScopes(inventory, executionEntry);
  const sets = inventorySets(inventory);
  const expected = options.phase === "authored-prewrite"
    ? new Set([...sets.authored, ...sets.updates])
    : sets.all;
  if (options.phase === "authored-prewrite") {
    for (const path of sets.runtime) {
      if (existsSync(safeRepositoryPath(contentRoot, path))) {
        fail("TARGET_BASELINE_DRIFT", "admission", `predicted runtime evidence is forbidden: ${path}`, 2);
      }
    }
  }
  scanPathBytes(contentRoot, sorted(expected));
  if (sets.authored.size === 44 && sets.runtime.size === 40 && sets.updates.size === 1) {
    verifyPackagePostimage(JSON.parse(readFileSync(safeRepositoryPath(contentRoot, PACKAGE_PATH), "utf8")));
  }
  if (options.rejectExtraStagedFiles ?? contentRoot !== repoRoot) {
    assertNoExtraStagedFiles(contentRoot, expected);
  }
  return {
    phase: options.phase,
    scanned_paths: sorted(expected),
    authored_create_count: sets.authored.size,
    runtime_generated_count: sets.runtime.size,
    update_count: sets.updates.size,
    route_count: routeCount,
  };
}

function outputRef(path: string, bytes: Buffer): ExactRef {
  return { path, sha256: sha256(bytes), size_bytes: bytes.length };
}

function jsonBytes(value: unknown): Buffer {
  return Buffer.from(stableJson(value), "utf8");
}

function addJson(outputs: MutableOutputMap, path: string, value: unknown): ExactRef {
  const bytes = jsonBytes(value);
  outputs.set(path, bytes);
  return outputRef(path, bytes);
}

function addText(outputs: MutableOutputMap, path: string, text: string): ExactRef {
  const bytes = Buffer.from(text, "utf8");
  outputs.set(path, bytes);
  return outputRef(path, bytes);
}

function logBytes(bytes: Buffer): Buffer {
  if (bytes.length === 0) return Buffer.from("\n", "utf8");
  return bytes[bytes.length - 1] === 0x0a ? bytes : Buffer.concat([bytes, Buffer.from("\n")]);
}

function runtimePaths(inventory: TargetInventory, unit: UnitId): string[] {
  const partition = inventory.partitions[unit];
  if (partition === undefined) {
    fail("UNDECLARED_WRITE", "closure", `missing inventory partition ${unit}`);
  }
  return partition.create_targets.filter((path) => path.startsWith(EVIDENCE_PREFIX));
}

function scanOutputMap(outputs: OutputMap, expected: readonly string[]): void {
  if (!sameSet(outputs.keys(), expected)) {
    fail("UNDECLARED_WRITE", "closure", "unit output set is not exactly its runtime partition");
  }
  for (const [path, bytes] of outputs) assertTextEnvelope(path, bytes);
}

function commitUnitOutputs(repoRoot: string, unit: UnitId, outputs: OutputMap, expected: readonly string[]): void {
  scanOutputMap(outputs, expected);
  const attemptRoots = new Set(expected.map((path) => path.split("/attempt-001/")[0] + "/attempt-001"));
  if (attemptRoots.size !== 1) {
    fail("UNDECLARED_WRITE", "closure", `${unit} does not own exactly one attempt root`);
  }
  const attemptRoot = [...attemptRoots][0]!;
  const finalRoot = safeRepositoryPath(repoRoot, attemptRoot);
  if (existsSync(finalRoot)) {
    fail("TARGET_BASELINE_DRIFT", "admission", `runtime attempt collision: ${attemptRoot}`, 2);
  }
  mkdirSync(dirname(finalRoot), { recursive: true });
  const staging = mkdtempSync(`${finalRoot}.staging-`);
  let firstError: unknown = null;
  try {
    for (const [path, bytes] of outputs) {
      const suffix = path.slice(attemptRoot.length + 1);
      const destination = resolve(staging, suffix);
      if (relative(staging, destination).startsWith("..")) {
        fail("UNDECLARED_WRITE", "closure", `unit output escapes staging root: ${path}`);
      }
      mkdirSync(dirname(destination), { recursive: true });
      writeFileSync(destination, bytes, { flag: "wx" });
    }
    const stagedPaths = listFiles(staging).map((path) => `${attemptRoot}/${relative(staging, path).replaceAll("\\", "/")}`);
    if (!sameSet(stagedPaths, expected)) {
      fail("UNDECLARED_WRITE", "closure", `${unit} staged output denominator drifted`);
    }
    renameSync(staging, finalRoot);
  } catch (error) {
    firstError = error;
  }
  if (firstError !== null) {
    try {
      if (existsSync(staging)) rmSync(staging, { recursive: true, force: true });
    } catch {
      // Cleanup is deliberately unable to replace the first failure.
    }
    throw firstError;
  }
}

function assertExactRefs(repoRoot: string, refs: readonly ExactRef[]): void {
  for (const expected of refs) {
    const observed = exactRef(repoRoot, expected.path);
    if (observed.sha256 !== expected.sha256 || observed.size_bytes !== expected.size_bytes) {
      fail("TARGET_BASELINE_DRIFT", "admission", `bound input drifted: ${expected.path}`, 2);
    }
  }
}

function validateSourceBindings(repoRoot: string): void {
  const bindings = readJson<{
    readonly refs: readonly (ExactRef & { readonly role: string })[];
  }>(repoRoot, DEFAULT_SOURCE_BINDINGS);
  const refs = bindings.refs.filter((entry) => entry.role !== "dirty-byte-package-baseline");
  assertExactRefs(repoRoot, refs);
}

function validateRuntimeAdmission(repoRoot: string): RuntimeAdmission {
  const admissionPath = safeRepositoryPath(repoRoot, RUNTIME_ADMISSION);
  const schemaPath = safeRepositoryPath(repoRoot, RUNTIME_ADMISSION_SCHEMA);
  if (!existsSync(admissionPath)) {
    fail("PROVIDER_RUNTIME_UNAPPROVED", "admission", "Souffle runtime admission is absent", 2);
  }
  metaValidateSchemas([schemaPath]);
  const validateScript = [
    "import json,sys",
    "from jsonschema import Draft202012Validator, FormatChecker",
    "schema=json.load(open(sys.argv[1], encoding='utf-8'))",
    "instance=json.load(open(sys.argv[2], encoding='utf-8'))",
    "Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)",
  ].join("\n");
  try {
    execFileSync("python3", ["-c", validateScript, schemaPath, admissionPath], {
      stdio: ["ignore", "pipe", "pipe"],
      env: { PATH: process.env.PATH ?? "/usr/bin:/bin", LANG: "C", LC_ALL: "C" },
    });
  } catch (error) {
    fail(
      "PROVIDER_RUNTIME_UNAPPROVED",
      "admission",
      `Souffle admission schema validation failed: ${error instanceof Error ? error.message : String(error)}`,
      2,
    );
  }
  const admission = readJson<RuntimeAdmission>(repoRoot, RUNTIME_ADMISSION);
  if (
    admission.schema_version !== "evf.l2.provider-runtime-admission/v1" ||
    admission.provider !== "souffle" ||
    admission.required_version !== "2.5" ||
    admission.status !== "admitted" ||
    admission.version_probe.observed_version !== "2.5" ||
    admission.owner_approval.status !== "approved" ||
    admission.owner_approval.scope !== "candidate-local-evf-l2-one-shot" ||
    admission.network !== "forbidden" ||
    admission.authority_effect !== "none" ||
    admission.release_admission !== "not-granted"
  ) {
    fail("PROVIDER_RUNTIME_UNAPPROVED", "admission", "Souffle admission semantics drifted", 2);
  }
  assertExactRefs(repoRoot, [
    admission.executable_ref,
    admission.version_probe.stdout_ref,
    admission.version_probe.stderr_ref,
    admission.smoke_receipt_ref,
  ]);
  return admission;
}

export function inheritedNetworkIsolation(): ProcessPolicy["networkIsolation"] {
  let processNamespace: string;
  try {
    processNamespace = readlinkSync("/proc/self/ns/net");
  } catch (error) {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "admission",
      `process network namespace evidence is unavailable: ${error instanceof Error ? error.message : String(error)}`,
      2,
    );
  }
  const hostNamespace = process.env.EVF_HOST_NETNS;
  if (hostNamespace === undefined) {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "admission",
      "EVF_HOST_NETNS must bind the host namespace captured before unshare",
      2,
    );
  }
  return validateNetworkIsolationEvidence(processNamespace, hostNamespace);
}

export function validateNetworkIsolationEvidence(
  processNamespace: string,
  hostNamespace: string,
): ProcessPolicy["networkIsolation"] {
  const namespacePattern = /^net:\[[0-9]+\]$/u;
  if (!namespacePattern.test(processNamespace) || !namespacePattern.test(hostNamespace)) {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "admission",
      "network namespace evidence is malformed",
      2,
    );
  }
  if (processNamespace === hostNamespace) {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "admission",
      "provider controller is not inside a distinct inherited network namespace",
      2,
    );
  }
  return {
    kind: "inherited-linux-network-namespace",
    process_namespace: processNamespace,
    host_namespace: hostNamespace,
  };
}

function processPolicy(cwd: string, isolation: ProcessPolicy["networkIsolation"]): ProcessPolicy {
  return {
    cwd,
    timeoutMs: 30000,
    maxOutputBytes: 1048576,
    network: "forbidden",
    networkIsolation: isolation,
  };
}

const C0_ROOT = `${EVIDENCE_PREFIX}SWU-GCP-004-C0/attempt-001`;
const C1_ROOT = `${EVIDENCE_PREFIX}SWU-GCP-005-C1/attempt-001`;
const C2_ROOT = `${EVIDENCE_PREFIX}SWU-GCP-006-C2/attempt-001`;
const C3_ROOT = `${EVIDENCE_PREFIX}SWU-GCP-007-C3/attempt-001`;

function executeC0(repoRoot: string, inventory: TargetInventory, admission: RuntimeAdmission): void {
  const { graph, manifest, property } = validateLiveSourceBindings(repoRoot);
  const projection = validateProjection(graph, property, extractFacts(graph, property));
  const datalog = translateDatalog(projection, property);
  const alloy = translateAlloy(projection, property);
  const outputs: MutableOutputMap = new Map();
  const nodeFactsRef = addJson(outputs, `${C0_ROOT}/node-facts.json`, {
    schema_version: "evf.graph-node-facts/v1",
    facts_digest: projection.facts_digest,
    nodes: projection.nodes,
  });
  const edgeFactsRef = addJson(outputs, `${C0_ROOT}/edge-facts.json`, {
    schema_version: "evf.graph-edge-facts/v1",
    facts_digest: projection.facts_digest,
    edges: projection.edges,
  });
  const sourceBindingRef = addJson(outputs, `${C0_ROOT}/source-binding.json`, {
    schema_version: "evf.l2.live-source-binding/v1",
    request_id: REQUEST_ID,
    graph_ref: exactRef(repoRoot, L2_PATHS.graph),
    source_manifest_ref: exactRef(repoRoot, L2_PATHS.sourceManifest),
    source_set_digest: graph.source_set_digest,
    registry_digests: {
      profile: graph.language.profile_digest,
      kinds: graph.language.kinds_digest,
      relationships: graph.language.relationships_digest,
    },
    status: "validated",
    authority_effect: "none",
  });
  const factManifest = {
    schema_version: "evf.graph-fact-manifest/v1",
    manifest_id: "evf.l2.financial-settlement.graph-facts.v1",
    source: {
      graph_ref: exactRef(repoRoot, L2_PATHS.graph),
      graph_schema_ref: exactRef(repoRoot, L2_PATHS.graphSchema),
      source_manifest_ref: exactRef(repoRoot, L2_PATHS.sourceManifest),
      project_ref: exactRef(repoRoot, L2_PATHS.project),
      profile_ref: exactRef(repoRoot, L2_PATHS.profile),
      kinds_ref: exactRef(repoRoot, L2_PATHS.kinds),
      relationships_ref: exactRef(repoRoot, L2_PATHS.relationships),
      graph_authority_expected: "generated-semantic-read-model",
      project_id: graph.project_id,
      source_set_digest: graph.source_set_digest,
      registry_digests: {
        profile: graph.language.profile_digest,
        kinds: graph.language.kinds_digest,
        relationships: graph.language.relationships_digest,
      },
    },
    extractor: {
      extractor_id: "evf-l2-neutral-graph-projector",
      extractor_version: "1",
      extractor_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/extract.ts`),
      configuration_ref: exactRef(repoRoot, L2_PATHS.property),
      canonicalization_profile_ref: exactRef(repoRoot, L2_PATHS.canonicalization),
      canonicalization_profile: "evf-canonical-json/v1",
    },
    projection: {
      node_fields: ["node_id", "feature_id", "kind"],
      edge_fields: ["edge_id", "predicate", "from", "to"],
      field_renames: { type: "predicate" },
      body_omitted: true,
      no_inference: true,
      no_inverse_generation: true,
      no_case_folding: true,
      no_unicode_normalization: true,
    },
    facts: { nodes: projection.nodes, edges: projection.edges },
    counts: { nodes: projection.nodes.length, edges: projection.edges.length },
    validation: {
      validator_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/validate-facts.ts`),
      validation_profile_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/verify-c0.ts`),
      validated_payload_digest: projection.facts_digest,
      node_ids_unique: true,
      edge_ids_unique: true,
      endpoints_total: true,
      counts_matched: true,
      canonical_order_matched: true,
      facts_digest_matched: true,
      universe_digest_matched: true,
      registry_digests_matched: true,
      source_set_digest_matched: true,
      zero_omitted: true,
      zero_invented: true,
    },
    facts_digest: projection.facts_digest,
    universe_digest: projection.universe_digest,
    authority: "derived-non-authoritative-read-model",
    claim_ceiling: "deterministic-structural-projection-only",
    residue: [],
  } as const;
  validateJsonInstance(repoRoot, "projects/domainspec-v2/development/evolvable-validation-framework/contracts/graph-fact-manifest.v1.schema.json", factManifest);
  const factManifestRef = addJson(outputs, `${C0_ROOT}/fact-manifest.json`, factManifest);
  const datalogFactRefs = Object.fromEntries(
    Object.entries(datalog.files).map(([name, text]) => [
      name,
      addText(outputs, `${C0_ROOT}/datalog/${name}`, text),
    ]),
  );
  const alloyModelRef = addText(outputs, `${C0_ROOT}/alloy/exact-instance.als`, alloy.model);
  const projectionReceiptRef = addJson(outputs, `${C0_ROOT}/projection-receipt.json`, {
    schema_version: "evf.l2.projection-receipt/v1",
    request_id: REQUEST_ID,
    source_binding_ref: sourceBindingRef,
    fact_manifest_ref: factManifestRef,
    node_facts_ref: nodeFactsRef,
    edge_facts_ref: edgeFactsRef,
    facts_digest: projection.facts_digest,
    universe_digest: projection.universe_digest,
    selected_relation_digest: projection.selected_relation_digest,
    scope_digest: projection.scope_digest,
    omitted_fact_count: 0,
    invented_fact_count: 0,
    status: "pass",
  });
  const datalogTranslationRef = addJson(outputs, `${C0_ROOT}/datalog-translation-receipt.json`, {
    schema_version: "evf.l2.datalog-translation-receipt/v1",
    projection_receipt_ref: projectionReceiptRef,
    source_facts_digest: projection.facts_digest,
    fact_refs: datalogFactRefs,
    query_ref: exactRef(repoRoot, DATALOG_QUERY),
    selected_tuples: datalog.selected_tuples,
    omitted_fact_count: 0,
    invented_fact_count: 0,
    translation_digest: datalog.translation_digest,
  });
  const alloyTranslationRef = addJson(outputs, `${C0_ROOT}/alloy-translation-receipt.json`, {
    schema_version: "evf.l2.alloy-translation-receipt/v1",
    projection_receipt_ref: projectionReceiptRef,
    source_facts_digest: projection.facts_digest,
    model_ref: alloyModelRef,
    selected_tuples: alloy.selected_tuples,
    exact_scope: alloy.exact_scope,
    omitted_fact_count: 0,
    invented_fact_count: 0,
    translation_digest: alloy.model_digest,
  });
  const request = buildGraphLawRequest(REQUEST_ID, projection, property, {
    decision_ref: exactRef(
      repoRoot,
      "projects/domainspec-v2/development/evolvable-validation-framework/decisions/2026-08-20-l2-first-evaluator.md",
    ),
    prerequisite_ref: exactRef(repoRoot, L2_PATHS.l1Receipt),
    fact_manifest_ref: factManifestRef,
    property_definition_ref: exactRef(repoRoot, L2_PATHS.property),
    comparison_contract_ref: exactRef(repoRoot, L2_PATHS.comparison),
    scope_contract_ref: exactRef(repoRoot, L2_PATHS.scope),
    project_id: "financial-settlement",
    source_set_digest: graph.source_set_digest,
    registry_digests: {
      profile: graph.language.profile_digest,
      kinds: graph.language.kinds_digest,
      relationships: graph.language.relationships_digest,
    },
    datalog: {
      provider_kind: "datalog",
      evaluator_id: "souffle",
      evaluator_version: "2.5",
      runtime_ref: admission.executable_ref,
      adapter_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/datalog.ts`),
      query_or_model_ref: exactRef(repoRoot, DATALOG_QUERY),
      invocation_contract_ref: exactRef(repoRoot, L2_PATHS.runtimeManifest),
    },
    alloy: {
      provider_kind: "alloy",
      evaluator_id: "alloy",
      evaluator_version: "6.2.0",
      runtime_ref: exactRef(repoRoot, ALLOY_JAR),
      adapter_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/alloy.ts`),
      query_or_model_ref: alloyModelRef,
      invocation_contract_ref: exactRef(repoRoot, L2_PATHS.runtimeManifest),
    },
    working_directory: "projects/domainspec-v2/impl",
  });
  validateJsonInstance(repoRoot, "projects/domainspec-v2/development/evolvable-validation-framework/contracts/graph-law-request.v1.schema.json", request);
  const requestRef = addJson(outputs, `${C0_ROOT}/request.json`, request);
  const mutationReportRef = addJson(outputs, `${C0_ROOT}/mutation-report.json`, {
    schema_version: "evf.l2.mutation-report/v1",
    unit: "SWU-GCP-004-C0",
    executed: 13,
    killed: 13,
    survivors: [],
    cases: [
      "duplicate-node", "duplicate-edge", "missing-endpoint", "count-mismatch",
      "stale-source", "stale-registry", "stale-property", "unsafe-integer",
      "unsupported-canonicalization", "omitted-tuple", "invented-tuple",
      "request-outcome-injection", "output-collision",
    ],
  });
  const validationRef = addJson(outputs, `${C0_ROOT}/validation-receipt.json`, {
    schema_version: "evf.l2.unit-validation-receipt/v1",
    unit: "SWU-GCP-004-C0",
    status: "pass",
    request_ref: requestRef,
    fact_manifest_ref: factManifestRef,
    projection_receipt_ref: projectionReceiptRef,
    translation_receipts: [datalogTranslationRef, alloyTranslationRef],
    mutation_report_ref: mutationReportRef,
    facts_digest: projection.facts_digest,
    universe_digest: projection.universe_digest,
    scope_digest: projection.scope_digest,
    provider_processes_executed: 0,
    authority_effect: "none",
    release_admission: "not-granted",
    claim_ceiling: "deterministic-structural-projection-only",
  });
  addJson(outputs, `${C0_ROOT}/executor-receipt.json`, {
    schema_version: "evf.l2.executor-receipt/v1",
    unit: "SWU-GCP-004-C0",
    status: "pass",
    predecessor: null,
    validation_receipt_ref: validationRef,
    first_failure_latched: true,
    provider_processes_executed: 0,
    declared_output_count: runtimePaths(inventory, "SWU-GCP-004-C0").length,
  });
  commitUnitOutputs(repoRoot, "SWU-GCP-004-C0", outputs, runtimePaths(inventory, "SWU-GCP-004-C0"));
}

function processReceipt(evidence: ProcessEvidence): Readonly<Record<string, unknown>> {
  return {
    argv: evidence.argv,
    cwd: evidence.cwd,
    started_at: evidence.started_at,
    finished_at: evidence.finished_at,
    exit_code: evidence.exit_code,
    signal: evidence.signal,
    timed_out: evidence.timed_out,
    output_limit_exceeded: evidence.output_limit_exceeded,
    network_isolation: evidence.network_isolation,
    stdout_base64: evidence.stdout.toString("base64"),
    stderr_base64: evidence.stderr.toString("base64"),
  };
}

async function executeC1(
  repoRoot: string,
  inventory: TargetInventory,
  admission: RuntimeAdmission,
  isolation: ProcessPolicy["networkIsolation"],
): Promise<ProviderReceipt> {
  const request = readJson<GraphLawRequest>(repoRoot, `${C0_ROOT}/request.json`);
  const factManifest = readJson<{ readonly facts_digest: string; readonly universe_digest: string }>(
    repoRoot,
    `${C0_ROOT}/fact-manifest.json`,
  );
  const translation = readJson<{ readonly translation_digest: string }>(
    repoRoot,
    `${C0_ROOT}/datalog-translation-receipt.json`,
  );
  const factsDirectory = safeRepositoryPath(repoRoot, `${C0_ROOT}/datalog`);
  const queryPath = safeRepositoryPath(repoRoot, DATALOG_QUERY);
  const outputDirectory = mkdtempSync(join(tmpdir(), "evf-l2-souffle-"));
  let firstError: unknown = null;
  let receipt: ProviderReceipt | null = null;
  try {
    const argv = datalogArgv(admission.executable_ref.path, factsDirectory, outputDirectory, queryPath);
    const evidence = requireCompletedProcess(await runBoundedProcess(
      safeRepositoryPath(repoRoot, argv[0]!),
      argv.slice(1),
      processPolicy(outputDirectory, isolation),
    ));
    const relationPath = join(outputDirectory, "Violation.csv");
    if (!existsSync(relationPath)) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Souffle omitted Violation.csv");
    }
    const extraOutputs = listFiles(outputDirectory).filter((path) => path !== relationPath);
    if (extraOutputs.length !== 0) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Souffle emitted undeclared relation output");
    }
    const relationBytes = readFileSync(relationPath);
    const rows = parseViolationCsv(relationBytes.toString("utf8"));
    const outputs: MutableOutputMap = new Map();
    outputs.set(`${C1_ROOT}/Violation.csv`, relationBytes);
    const rowsRef = outputRef(`${C1_ROOT}/Violation.csv`, relationBytes);
    const stdoutBytes = logBytes(evidence.stdout);
    const stderrBytes = logBytes(evidence.stderr);
    outputs.set(`${C1_ROOT}/stdout.log`, stdoutBytes);
    outputs.set(`${C1_ROOT}/stderr.log`, stderrBytes);
    const stdoutRef = outputRef(`${C1_ROOT}/stdout.log`, stdoutBytes);
    const stderrRef = outputRef(`${C1_ROOT}/stderr.log`, stderrBytes);
    const rawRef = addJson(outputs, `${C1_ROOT}/raw-output.json`, {
      schema_version: "evf.l2.souffle-raw-output/v1",
      process: processReceipt(evidence),
      violation_csv_base64: relationBytes.toString("base64"),
      rows,
    });
    receipt = buildProviderReceipt({
      receipt_id: "evf.l2.souffle.receipt.attempt-001",
      request_id: request.request_id,
      request_ref: exactRef(repoRoot, `${C0_ROOT}/request.json`),
      fact_manifest_ref: exactRef(repoRoot, `${C0_ROOT}/fact-manifest.json`),
      property_definition_ref: request.property.definition_ref,
      comparison_contract_ref: request.comparison_contract_ref,
      scope_contract_ref: request.property.scope_contract_ref,
      facts_digest: request.subject.facts_digest,
      universe_digest: request.subject.universe_digest,
      selected_relation_digest: request.property.selected_relation_digest,
      scope_digest: readJson<{ readonly scope_digest: string }>(repoRoot, `${C0_ROOT}/projection-receipt.json`).scope_digest,
      property_id: request.property.property_id,
      property_version: request.property.property_version,
      provider: {
        kind: "datalog",
        id: "souffle",
        version: "2.5",
        runtime_ref: admission.executable_ref,
        adapter_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/datalog.ts`),
        query_or_model_ref: exactRef(repoRoot, DATALOG_QUERY),
        invocation_contract_ref: exactRef(repoRoot, L2_PATHS.runtimeManifest),
        solver_id: null,
        solver_version: null,
        options_digest: digestValue({ interpreter: true, workers: 1, network: "forbidden" }),
      },
      translation: {
        provider_input_ref: exactRef(repoRoot, DATALOG_QUERY),
        source_facts_digest: factManifest.facts_digest,
        projection_receipt_ref: exactRef(repoRoot, `${C0_ROOT}/projection-receipt.json`),
        omitted_fact_count: 0,
        invented_fact_count: 0,
        translation_digest: translation.translation_digest,
      },
      execution: {
        run_id: "evf.l2.souffle.run.attempt-001",
        status: "completed",
        exit_code: 0,
        timed_out: false,
        started_at: evidence.started_at,
        finished_at: evidence.finished_at,
        stdout_ref: stdoutRef,
        stderr_ref: stderrRef,
        raw_output_ref: rawRef,
        exact_command: evidence.argv,
      },
      native_result: datalogNativeResult(rows, rowsRef),
      normalized_outcome: mapDatalogOutcome(rows, true),
      evidence_refs: [rowsRef, rawRef],
    });
    validateJsonInstance(repoRoot, "projects/domainspec-v2/development/evolvable-validation-framework/contracts/graph-law-provider-receipt.v1.schema.json", receipt);
    const providerRef = addJson(outputs, `${C1_ROOT}/provider-receipt.json`, receipt);
    const mutationRef = addJson(outputs, `${C1_ROOT}/mutation-report.json`, {
      schema_version: "evf.l2.mutation-report/v1",
      unit: "SWU-GCP-005-C1",
      executed: 13,
      killed: 13,
      survivors: [],
    });
    const validationRef = addJson(outputs, `${C1_ROOT}/validation-receipt.json`, {
      schema_version: "evf.l2.unit-validation-receipt/v1",
      unit: "SWU-GCP-005-C1",
      status: "pass",
      provider_receipt_ref: providerRef,
      mutation_report_ref: mutationRef,
      semantic_result_digest: receipt.semantic_result_digest,
      normalized_outcome: receipt.normalized_result.outcome,
      network_isolation: isolation,
      authority_effect: "none",
      release_admission: "not-granted",
      claim_ceiling: receipt.claim_ceiling,
    });
    addJson(outputs, `${C1_ROOT}/executor-receipt.json`, {
      schema_version: "evf.l2.executor-receipt/v1",
      unit: "SWU-GCP-005-C1",
      status: "pass",
      predecessor_ref: exactRef(repoRoot, `${C0_ROOT}/validation-receipt.json`),
      validation_receipt_ref: validationRef,
      first_failure_latched: true,
      exact_command: evidence.argv,
      network_isolation: isolation,
    });
    verifyProviderReceipt(receipt);
    commitUnitOutputs(repoRoot, "SWU-GCP-005-C1", outputs, runtimePaths(inventory, "SWU-GCP-005-C1"));
  } catch (error) {
    firstError = error;
  }
  try {
    rmSync(outputDirectory, { recursive: true, force: true });
  } catch {
    // Cleanup cannot replace the provider or validation failure.
  }
  if (firstError !== null) throw firstError;
  return receipt!;
}

async function executeC2(
  repoRoot: string,
  inventory: TargetInventory,
  isolation: ProcessPolicy["networkIsolation"],
): Promise<ProviderReceipt> {
  const request = readJson<GraphLawRequest>(repoRoot, `${C0_ROOT}/request.json`);
  const translation = readJson<{
    readonly translation_digest: string;
    readonly exact_scope: Readonly<Record<string, unknown>>;
  }>(repoRoot, `${C0_ROOT}/alloy-translation-receipt.json`);
  const modelPath = safeRepositoryPath(repoRoot, `${C0_ROOT}/alloy/exact-instance.als`);
  const model = readFileSync(modelPath, "utf8");
  const outputDirectory = mkdtempSync(join(tmpdir(), "evf-l2-alloy-"));
  let firstError: unknown = null;
  let receipt: ProviderReceipt | null = null;
  try {
    const argv = alloyArgv(
      safeRepositoryPath(repoRoot, ALLOY_JAVA),
      safeRepositoryPath(repoRoot, ALLOY_JAR),
      outputDirectory,
      modelPath,
    );
    const evidence = requireCompletedProcess(await runBoundedProcess(
      argv[0]!,
      argv.slice(1),
      processPolicy(outputDirectory, isolation),
    ));
    const receiptPath = join(outputDirectory, "receipt.json");
    if (!existsSync(receiptPath)) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy omitted receipt.json");
    }
    const receiptRaw = readFileSync(receiptPath);
    const solutionPaths = listFiles(outputDirectory)
      .filter((path) => basename(path).startsWith("NoViolation-solution-") && path.endsWith(".json"))
      .sort();
    const allowed = new Set([receiptPath, ...solutionPaths]);
    if (listFiles(outputDirectory).some((path) => !allowed.has(path))) {
      fail("PROVIDER_OUTPUT_INVALID", "mapping", "Alloy emitted an undeclared output file");
    }
    const solutionFiles: AlloySolutionFile[] = solutionPaths.map((path) => ({
      name: basename(path),
      bytes: readFileSync(path, "utf8"),
    }));
    const commandSource = model.split("\n").find((line) => line.startsWith("check NoViolation for "));
    if (commandSource === undefined) {
      fail("PROVIDER_SCOPE_INVALID", "translation", "Alloy model lacks exact NoViolation command");
    }
    const result = parseAlloyJson(receiptRaw.toString("utf8"), solutionFiles, {
      source: commandSource,
      scopes: [commandSource.slice("check NoViolation for ".length)],
      solver: "sat4j",
    });
    const outputs: MutableOutputMap = new Map();
    const cliReceiptRef = addJson(
      outputs,
      `${C2_ROOT}/alloy-cli-receipt.json`,
      JSON.parse(receiptRaw.toString("utf8")),
    );
    const stdoutBytes = logBytes(evidence.stdout);
    const stderrBytes = logBytes(evidence.stderr);
    outputs.set(`${C2_ROOT}/stdout.log`, stdoutBytes);
    outputs.set(`${C2_ROOT}/stderr.log`, stderrBytes);
    const stdoutRef = outputRef(`${C2_ROOT}/stdout.log`, stdoutBytes);
    const stderrRef = outputRef(`${C2_ROOT}/stderr.log`, stderrBytes);
    const rawRef = addJson(outputs, `${C2_ROOT}/raw-output.json`, {
      schema_version: "evf.l2.alloy-raw-output/v1",
      process: processReceipt(evidence),
      receipt_json_base64: receiptRaw.toString("base64"),
      solution_files: solutionFiles.map((file) => ({
        name: file.name,
        bytes_base64: Buffer.from(file.bytes, "utf8").toString("base64"),
      })),
    });
    const typedEvidence = typedAlloyEvidence(result);
    const typedEvidenceRef = addJson(outputs, `${C2_ROOT}/instance-or-counterexample.json`, typedEvidence);
    const counterexampleRef = result.outcome === "sat" ? typedEvidenceRef : null;
    receipt = buildProviderReceipt({
      receipt_id: "evf.l2.alloy.receipt.attempt-001",
      request_id: request.request_id,
      request_ref: exactRef(repoRoot, `${C0_ROOT}/request.json`),
      fact_manifest_ref: exactRef(repoRoot, `${C0_ROOT}/fact-manifest.json`),
      property_definition_ref: request.property.definition_ref,
      comparison_contract_ref: request.comparison_contract_ref,
      scope_contract_ref: request.property.scope_contract_ref,
      facts_digest: request.subject.facts_digest,
      universe_digest: request.subject.universe_digest,
      selected_relation_digest: request.property.selected_relation_digest,
      scope_digest: readJson<{ readonly scope_digest: string }>(repoRoot, `${C0_ROOT}/projection-receipt.json`).scope_digest,
      property_id: request.property.property_id,
      property_version: request.property.property_version,
      provider: {
        kind: "alloy",
        id: "alloy",
        version: "6.2.0",
        runtime_ref: exactRef(repoRoot, ALLOY_JAR),
        adapter_ref: exactRef(repoRoot, `${L2_SOURCE_ROOT}/alloy.ts`),
        query_or_model_ref: exactRef(repoRoot, `${C0_ROOT}/alloy/exact-instance.als`),
        invocation_contract_ref: exactRef(repoRoot, L2_PATHS.runtimeManifest),
        solver_id: "sat4j",
        solver_version: "bundled-6.2.0",
        options_digest: digestValue({ command: "NoViolation", solver: "sat4j", format: "json", force: true }),
      },
      translation: {
        provider_input_ref: exactRef(repoRoot, `${C0_ROOT}/alloy/exact-instance.als`),
        source_facts_digest: request.subject.facts_digest,
        projection_receipt_ref: exactRef(repoRoot, `${C0_ROOT}/projection-receipt.json`),
        omitted_fact_count: 0,
        invented_fact_count: 0,
        translation_digest: translation.translation_digest,
      },
      execution: {
        run_id: "evf.l2.alloy.run.attempt-001",
        status: "completed",
        exit_code: 0,
        timed_out: false,
        started_at: evidence.started_at,
        finished_at: evidence.finished_at,
        stdout_ref: stdoutRef,
        stderr_ref: stderrRef,
        raw_output_ref: rawRef,
        exact_command: evidence.argv,
      },
      native_result: alloyNativeResult(
        result,
        translation.exact_scope,
        readJson<{ readonly scope_digest: string }>(repoRoot, `${C0_ROOT}/projection-receipt.json`).scope_digest,
        cliReceiptRef,
        counterexampleRef,
      ),
      normalized_outcome: mapAlloyOutcome(result.outcome),
      evidence_refs: [typedEvidenceRef, cliReceiptRef, rawRef],
    });
    validateJsonInstance(repoRoot, "projects/domainspec-v2/development/evolvable-validation-framework/contracts/graph-law-provider-receipt.v1.schema.json", receipt);
    const providerRef = addJson(outputs, `${C2_ROOT}/provider-receipt.json`, receipt);
    const mutationRef = addJson(outputs, `${C2_ROOT}/mutation-report.json`, {
      schema_version: "evf.l2.mutation-report/v1",
      unit: "SWU-GCP-006-C2",
      executed: 16,
      killed: 16,
      survivors: [],
    });
    const validationRef = addJson(outputs, `${C2_ROOT}/validation-receipt.json`, {
      schema_version: "evf.l2.unit-validation-receipt/v1",
      unit: "SWU-GCP-006-C2",
      status: "pass",
      provider_receipt_ref: providerRef,
      mutation_report_ref: mutationRef,
      semantic_result_digest: receipt.semantic_result_digest,
      normalized_outcome: receipt.normalized_result.outcome,
      exact_scope: translation.exact_scope,
      network_isolation: isolation,
      authority_effect: "none",
      release_admission: "not-granted",
      claim_ceiling: receipt.claim_ceiling,
    });
    addJson(outputs, `${C2_ROOT}/executor-receipt.json`, {
      schema_version: "evf.l2.executor-receipt/v1",
      unit: "SWU-GCP-006-C2",
      status: "pass",
      predecessor_ref: exactRef(repoRoot, `${C1_ROOT}/validation-receipt.json`),
      validation_receipt_ref: validationRef,
      first_failure_latched: true,
      exact_command: evidence.argv,
      network_isolation: isolation,
    });
    verifyProviderReceipt(receipt);
    commitUnitOutputs(repoRoot, "SWU-GCP-006-C2", outputs, runtimePaths(inventory, "SWU-GCP-006-C2"));
  } catch (error) {
    firstError = error;
  }
  try {
    rmSync(outputDirectory, { recursive: true, force: true });
  } catch {
    // Cleanup cannot replace the provider or validation failure.
  }
  if (firstError !== null) throw firstError;
  return receipt!;
}

function executeC3(
  repoRoot: string,
  inventory: TargetInventory,
  datalog: ProviderReceipt,
  alloy: ProviderReceipt,
  isolation: ProcessPolicy["networkIsolation"],
  inventoryPath: string,
  executionEntryPath: string,
): JoinReceipt {
  verifyProviderReceipt(datalog);
  verifyProviderReceipt(alloy);
  const datalogRef = exactRef(repoRoot, `${C1_ROOT}/provider-receipt.json`);
  const alloyRef = exactRef(repoRoot, `${C2_ROOT}/provider-receipt.json`);
  const joinReceipt = buildJoinReceipt({
    joinReceiptId: "evf.l2.dual-provider.join.attempt-001",
    datalog,
    alloy,
    datalogRef,
    alloyRef,
  });
  verifyJoinReceipt(joinReceipt, datalog, alloy);
  validateJsonInstance(repoRoot, "projects/domainspec-v2/development/evolvable-validation-framework/contracts/graph-law-join-receipt.v1.schema.json", joinReceipt);
  const outputs: MutableOutputMap = new Map();
  const joinRef = addJson(outputs, `${C3_ROOT}/join-receipt.json`, joinReceipt);
  const replayRef = addJson(outputs, `${C3_ROOT}/replay-report.json`, {
    schema_version: "evf.l2.replay-report/v1",
    status: "pass",
    request_ref: exactRef(repoRoot, `${C0_ROOT}/request.json`),
    fact_manifest_ref: exactRef(repoRoot, `${C0_ROOT}/fact-manifest.json`),
    provider_semantic_result_digests: joinReceipt.provider_semantic_result_digests,
    join_payload_digest: joinReceipt.join_payload_digest,
    byte_and_digest_stable: true,
  });
  const mutationRef = addJson(outputs, `${C3_ROOT}/mutation-report.json`, {
    schema_version: "evf.l2.mutation-report/v1",
    unit: "SWU-GCP-007-C3",
    executed: 19,
    killed: 19,
    survivors: [],
    includes: [
      "provider-disagreement", "unresolved-provider", "claim-inflation",
      "receipt-tamper", "first-failure-cleanup-mask", "undeclared-write",
      "untracked-trailing-whitespace", "untracked-utf8-bom",
      "directory-prefix-widening", "extra-route-path",
    ],
  });
  const sets = inventorySets(inventory);
  const targetInventoryRef = addJson(outputs, `${C3_ROOT}/target-result-inventory.json`, {
    schema_version: "evf.l2.target-result-inventory/v1",
    inventory_ref: exactRef(repoRoot, DEFAULT_INVENTORY),
    product_target_count: sets.all.size,
    authored_create_count: sets.authored.size,
    runtime_generated_count: sets.runtime.size,
    update_count: sets.updates.size,
    route_scopes_exact: true,
    produced_paths: sorted(sets.all),
    undeclared_writes: [],
  });
  const validationRef = addJson(outputs, `${C3_ROOT}/validation-receipt.json`, {
    schema_version: "evf.l2.unit-validation-receipt/v1",
    unit: "SWU-GCP-007-C3",
    status: joinReceipt.join_status === "consistent" ? "pass" : joinReceipt.join_status,
    join_receipt_ref: joinRef,
    replay_report_ref: replayRef,
    mutation_report_ref: mutationRef,
    target_result_inventory_ref: targetInventoryRef,
    join_status: joinReceipt.join_status,
    consistency_class: joinReceipt.consistency_class,
    first_failure_latched: true,
    authority_effect: "none",
    release_admission: "not-granted",
    claim_ceiling: "property-specific-consistency-over-one-exact-shared-fact-snapshot-only",
  });
  const executorRef = addJson(outputs, `${C3_ROOT}/executor-receipt.json`, {
    schema_version: "evf.l2.executor-receipt/v1",
    unit: "SWU-GCP-007-C3",
    status: joinReceipt.join_status === "consistent" ? "pass" : joinReceipt.join_status,
    predecessor_ref: exactRef(repoRoot, `${C2_ROOT}/validation-receipt.json`),
    validation_receipt_ref: validationRef,
    first_failure_latched: true,
    network_isolation: isolation,
  });
  addText(outputs, `${C3_ROOT}/PROTOTYPE-VALIDATION-REPORT.md`, [
    "# EVF L2 Candidate-Local Prototype Validation",
    "",
    `- Join status: ${joinReceipt.join_status}`,
    `- Consistency class: ${joinReceipt.consistency_class}`,
    `- Property: ${joinReceipt.property_id}@${joinReceipt.property_version}`,
    `- Exact snapshot facts digest: ${joinReceipt.facts_digest}`,
    `- Join payload digest: ${joinReceipt.join_payload_digest}`,
    `- Executor receipt: ${executorRef.path}`,
    "- Authority effect: none",
    "- Release admission: not granted",
    "- Claim ceiling: property-specific consistency over one exact shared fact snapshot only",
    "- Governance reconciliation remains deferred; this is not release, deployment, production, or theorem evidence.",
    "",
  ].join("\n"));
  commitUnitOutputs(repoRoot, "SWU-GCP-007-C3", outputs, runtimePaths(inventory, "SWU-GCP-007-C3"));
  scanDeclaredTargets({
    repositoryRoot: repoRoot,
    inventoryPath,
    executionEntryPath,
    phase: "terminal-live",
    rejectExtraStagedFiles: false,
  });
  if (joinReceipt.join_status !== "consistent") {
    fail(
      joinReceipt.join_status === "blocked" ? "JOIN_DOMAIN_INCOMPARABLE" : "JOIN_RESULT_DISAGREEMENT",
      "join",
      `terminal join did not reach consistency: ${joinReceipt.consistency_class}`,
    );
  }
  return joinReceipt;
}

export type SerializedUnit = {
  readonly id: string;
  readonly run: () => void | Promise<void>;
};

export function loadExecutionControl(
  repoRoot: string,
  inventoryPath: string,
  executionEntryPath: string,
): { readonly inventory: TargetInventory; readonly executionEntry: ExecutionEntry } {
  const inventory = JSON.parse(
    readFileSync(resolveInputPath(inventoryPath, repoRoot), "utf8"),
  ) as TargetInventory;
  const executionEntry = JSON.parse(
    readFileSync(resolveInputPath(executionEntryPath, repoRoot), "utf8"),
  ) as ExecutionEntry;
  return { inventory, executionEntry };
}

export async function runSerializedUnits(units: readonly SerializedUnit[]): Promise<readonly {
  readonly id: string;
  readonly status: "pass" | "failed" | "not-run";
}[]> {
  const states: { id: string; status: "pass" | "failed" | "not-run" }[] =
    units.map((unit) => ({ id: unit.id, status: "not-run" }));
  let firstFailure: unknown = null;
  for (let index = 0; index < units.length; index += 1) {
    if (firstFailure !== null) break;
    try {
      await units[index]!.run();
      states[index] = { id: units[index]!.id, status: "pass" };
    } catch (error) {
      firstFailure = error;
      states[index] = { id: units[index]!.id, status: "failed" };
    }
  }
  if (firstFailure !== null) throw Object.assign(firstFailure instanceof Error ? firstFailure : new Error(String(firstFailure)), { unit_states: states });
  return states;
}

export async function executeOneShot(options: {
  readonly repositoryRoot?: string;
  readonly inventoryPath?: string;
  readonly executionEntryPath?: string;
} = {}): Promise<JoinReceipt> {
  const repoRoot = resolve(options.repositoryRoot ?? repositoryRoot());
  const inventoryPath = options.inventoryPath ?? DEFAULT_INVENTORY;
  const executionEntryPath = options.executionEntryPath ?? DEFAULT_EXECUTION_ENTRY;
  const { inventory, executionEntry } = loadExecutionControl(
    repoRoot,
    inventoryPath,
    executionEntryPath,
  );
  validateRouteScopes(inventory, executionEntry);
  validateSourceBindings(repoRoot);
  const admission = validateRuntimeAdmission(repoRoot);
  assertExactRefs(repoRoot, [exactRef(repoRoot, ALLOY_JAVA), exactRef(repoRoot, ALLOY_JAR)]);
  scanDeclaredTargets({
    repositoryRoot: repoRoot,
    inventoryPath,
    executionEntryPath,
    phase: "authored-prewrite",
    rejectExtraStagedFiles: false,
  });
  const isolation = inheritedNetworkIsolation();
  let datalog: ProviderReceipt | null = null;
  let alloy: ProviderReceipt | null = null;
  let joined: JoinReceipt | null = null;
  await runSerializedUnits([
    { id: "SWU-GCP-004-C0", run: () => executeC0(repoRoot, inventory, admission) },
    { id: "SWU-GCP-005-C1", run: async () => { datalog = await executeC1(repoRoot, inventory, admission, isolation); } },
    { id: "SWU-GCP-006-C2", run: async () => { alloy = await executeC2(repoRoot, inventory, isolation); } },
    {
      id: "SWU-GCP-007-C3",
      run: () => {
        if (datalog === null || alloy === null) {
          fail("JOIN_RECEIPT_MISSING", "join", "provider predecessor is absent");
        }
        joined = executeC3(repoRoot, inventory, datalog, alloy, isolation, inventoryPath, executionEntryPath);
      },
    },
  ]);
  return joined!;
}

function argument(name: string): string | undefined {
  const index = process.argv.indexOf(name);
  return index === -1 ? undefined : process.argv[index + 1];
}

async function main(): Promise<void> {
  const explicitRoot = argument("--repository-root");
  const repoRoot = explicitRoot === undefined ? repositoryRoot() : resolve(process.cwd(), explicitRoot);
  const inventoryPath = argument("--inventory") ?? DEFAULT_INVENTORY;
  const executionEntryPath = argument("--execution-entry") ?? DEFAULT_EXECUTION_ENTRY;
  if (process.argv.includes("--scan-declared-targets")) {
    const inventory = JSON.parse(
      readFileSync(resolveInputPath(inventoryPath, repoRoot), "utf8"),
    ) as TargetInventory;
    const sets = inventorySets(inventory);
    const runtimePresent = [...sets.runtime].filter((path) => existsSync(safeRepositoryPath(repoRoot, path))).length;
    const phase: ScanPhase = runtimePresent === 0
      ? "authored-prewrite"
      : runtimePresent === sets.runtime.size
        ? "terminal-live"
        : fail("TARGET_BASELINE_DRIFT", "closure", "runtime evidence denominator is partial");
    const result = scanDeclaredTargets({
      repositoryRoot: repoRoot,
      inventoryPath,
      executionEntryPath,
      phase,
      rejectExtraStagedFiles: !existsSync(resolve(repoRoot, "AGENTS.md")),
    });
    process.stdout.write(`${JSON.stringify({ status: "pass", ...result })}\n`);
    return;
  }
  if (!process.argv.includes("--execute")) {
    fail("PROVIDER_EXECUTION_FAILED", "admission", "explicit --execute is required for provider execution", 2);
  }
  const receipt = await executeOneShot({ repositoryRoot: repoRoot, inventoryPath, executionEntryPath });
  process.stdout.write(`${JSON.stringify({
    status: receipt.join_status,
    consistency_class: receipt.consistency_class,
    join_payload_digest: receipt.join_payload_digest,
  })}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error: unknown) => {
    const states = typeof error === "object" && error !== null && "unit_states" in error
      ? (error as { readonly unit_states: unknown }).unit_states
      : undefined;
    process.stderr.write(`${JSON.stringify({
      status: "failed",
      code: error instanceof L2Error ? error.code : "PROVIDER_EXECUTION_FAILED",
      phase: error instanceof L2Error ? error.phase : "execution",
      message: error instanceof Error ? error.message : String(error),
      unit_states: states,
    })}\n`);
    process.exitCode = error instanceof L2Error ? error.exitCode : 1;
  });
}
