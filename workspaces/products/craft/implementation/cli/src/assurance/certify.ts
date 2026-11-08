import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { compileProject } from "../compilation/certificate.js";
import { materializeLeanMetaTypeFormalization } from "../formalization/projection.js";
import { FORMALIZATION_LEAN_MODULE_FILENAMES } from "../formalization/kernel.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { SUBPROCESS_TIMEOUT_MS } from "../input/limits.js";
import { CLI_VERSION } from "../version.js";
import { loadAtomicPublicationNative } from "../generation/atomic-publication-native.js";
import { createCheckedInterchange, validateCheckedInterchange, type CheckedInterchangeV1 } from "./checked-interchange.js";

export const CERTIFY_LEAN_TOOLCHAIN = "leanprover/lean4:v4.33.1" as const;
export const CERTIFY_LEAN_VERSION = "4.33.1" as const;
const INTERCHANGE_DECODER_FILENAME = "DomainSpecCheckedInterchangeDecoder.lean" as const;
const interchangeDecoderSourcePath = fileURLToPath(new URL(`../../lean/${INTERCHANGE_DECODER_FILENAME}`, import.meta.url));

export interface AssuranceCertificateV1 {
  readonly schema_version: "domainspec.assurance-certificate/v1";
  readonly result: "pass";
  readonly project_id: string;
  readonly source_manifest_sha256: string;
  readonly compiled_certificate_sha256: string;
  readonly compiled_graph_sha256: string;
  readonly checked_interchange_sha256: string;
  readonly formalization: Readonly<{
    readonly render_payload_sha256: string;
    readonly project_graph_sha256: string;
    readonly lean_module_set_sha256: string;
    readonly proof_unit_sha256: string;
  }>;
  readonly independent_decoder: Readonly<{
    readonly source_sha256: string;
    readonly decoded_summary_sha256: string;
  }>;
  readonly denominators: CheckedInterchangeV1["denominators"];
  readonly checks: readonly Readonly<{
    readonly check_id: "compiled-certificate" | "checked-interchange" | "lean-interchange-decoder" | "lean-proof-unit";
    readonly result: "pass";
  }>[];
  readonly toolchain: Readonly<{
    readonly cli_package: "@domainspec-v2/cli";
    readonly cli_version: string;
    readonly node: string;
    readonly lean_toolchain: typeof CERTIFY_LEAN_TOOLCHAIN;
    readonly lean_version: typeof CERTIFY_LEAN_VERSION;
  }>;
  readonly artifacts: Readonly<{
    readonly checked_interchange: "checked-interchange.json";
    readonly lean_decoder: "proof/DomainSpecCheckedInterchangeDecoder.lean";
    readonly lean_entry: "proof/Current.lean";
    readonly certificate: "assurance-certificate.json";
  }>;
  readonly claim_ceiling: "exact-finite-projection-and-proof-no-universal-compiler-runtime-or-authority-claim";
  readonly authority_effect: "none";
  readonly certificate_sha256: string;
}

export interface CertificationCheckV1 {
  readonly schema_version: "domainspec.certification-check/v1";
  readonly result: "pass" | "fail";
  readonly current: boolean;
  readonly target_directory: string;
  readonly expected_certificate_sha256: string;
  readonly authority_effect: "none";
}
export interface CertificationCheckV2 extends Omit<CertificationCheckV1, "schema_version"> {
  readonly schema_version: "domainspec.certification-check/v2";
  readonly retained_evidence_directory: string;
  readonly cleanup_authorized: false;
}

/** An observation made during one failed attempt, not a durable ownership
 * proof or permission to remove the named path. */
export interface RetainedCertificationStageV1 {
  readonly schema_version: "domainspec.retained-certification-stage/v1";
  readonly attempt_id: string;
  readonly target_directory: string;
  readonly staging_path: string;
  readonly created_at_ms: number;
  readonly created_dev: string;
  readonly created_ino: string;
  readonly created_uid: string;
  readonly parent_dev: string;
  readonly parent_ino: string;
  readonly parent_uid: string;
  readonly observed_at_ms: number;
  readonly named_status: "same-inode-at-check" | "changed-or-replaced-at-check" | "missing-at-check" | "unavailable-at-check";
  readonly named_dev: string | null;
  readonly named_ino: string | null;
  readonly review_after_ms: number;
  readonly review_due: boolean;
  readonly quiescence: "unverified";
  readonly cleanup_authorized: false;
}

/** Alert-only review interval. It never triggers refusal or deletion. */
export const CERTIFY_STAGING_REVIEW_AFTER_MS = 7 * 24 * 60 * 60 * 1000;

export class CertificationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string,
    readonly retained_stage?: RetainedCertificationStageV1,
    readonly retained_evidence_directory?: string) {
    super(message);
    this.name = "CertificationError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new CertificationError(code, pointer, message);
}

function leanVersion(): string {
  const result = spawnSync("lean", ["--version"], {
    encoding: "utf8",
    env: { ...process.env, ELAN_TOOLCHAIN: CERTIFY_LEAN_TOOLCHAIN },
    timeout: SUBPROCESS_TIMEOUT_MS,
  });
  if (result.status !== 0) fail("MTCLI_CERTIFY_LEAN_UNAVAILABLE", "/toolchain/lean", result.stderr?.trim() || result.error?.message || "pinned Lean toolchain is unavailable");
  const match = /^Lean \(version ([0-9]+\.[0-9]+\.[0-9]+),/.exec(result.stdout.trim());
  if (match?.[1] !== CERTIFY_LEAN_VERSION) fail("MTCLI_CERTIFY_LEAN_VERSION", "/toolchain/lean", `expected Lean ${CERTIFY_LEAN_VERSION}`);
  return match[1];
}

function normalizedNewDirectory(targetDirectory: string): void {
  if (!path.isAbsolute(targetDirectory) || path.resolve(targetDirectory) !== targetDirectory) fail("MTCLI_CERTIFY_TARGET", "/target", "certify target must be a normalized absolute directory path");
  if (fs.existsSync(targetDirectory)) fail("MTCLI_CERTIFY_TARGET_EXISTS", "/target", "certify target already exists");
  const parent = path.dirname(targetDirectory);
  let stats: fs.Stats;
  try { stats = fs.lstatSync(parent); } catch { fail("MTCLI_CERTIFY_TARGET_PARENT", "/target", "certify target parent does not exist"); }
  if (!stats.isDirectory() || stats.isSymbolicLink() || fs.realpathSync(parent) !== parent) fail("MTCLI_CERTIFY_TARGET_PARENT", "/target", "certify target parent must be a real directory");
}

type NoReplace = ReturnType<typeof loadAtomicPublicationNative>;
type StageIdentity = Readonly<{ dev: bigint; ino: bigint; uid: bigint }>;
function stageIdentity(staging: string): StageIdentity {
  const stats = fs.lstatSync(staging, { bigint: true });
  if (!stats.isDirectory() || stats.isSymbolicLink()) fail("MTCLI_CERTIFY_STAGING", "/target", "certification staging must be a real directory");
  return { dev: stats.dev, ino: stats.ino, uid: stats.uid };
}
function retainedStageObservation(staging: string, target: string, owned: StageIdentity,
  parentOwned: StageIdentity, createdAt: number): RetainedCertificationStageV1 {
  let namedStatus: RetainedCertificationStageV1["named_status"];
  let namedDev: string | null = null;
  let namedIno: string | null = null;
  try {
    const named = fs.lstatSync(staging, { bigint: true });
    namedDev = String(named.dev); namedIno = String(named.ino);
    namedStatus = named.isDirectory() && !named.isSymbolicLink() && named.dev === owned.dev && named.ino === owned.ino
      ? "same-inode-at-check" : "changed-or-replaced-at-check";
  } catch (error) {
    namedStatus = (error as NodeJS.ErrnoException).code === "ENOENT" ? "missing-at-check" : "unavailable-at-check";
  }
  const observedAt = Date.now();
  return { schema_version: "domainspec.retained-certification-stage/v1", attempt_id: path.basename(staging),
    target_directory: target, staging_path: staging, created_at_ms: createdAt,
    created_dev: String(owned.dev), created_ino: String(owned.ino), created_uid: String(owned.uid),
    parent_dev: String(parentOwned.dev), parent_ino: String(parentOwned.ino), parent_uid: String(parentOwned.uid),
    observed_at_ms: observedAt, named_status: namedStatus!, named_dev: namedDev, named_ino: namedIno,
    review_after_ms: CERTIFY_STAGING_REVIEW_AFTER_MS,
    review_due: observedAt - createdAt >= CERTIFY_STAGING_REVIEW_AFTER_MS,
    quiescence: "unverified", cleanup_authorized: false };
}
function retainedStageDiagnostic(observation: RetainedCertificationStageV1): string {
  return `staging path ${JSON.stringify(observation.staging_path)}; created dev=${observation.created_dev} ino=${observation.created_ino} uid=${observation.created_uid}; named status=${observation.named_status}; review after ${observation.review_after_ms} ms (alert only); inspect before any separate cleanup; do not delete by pathname`;
}
function withCertificationStaging<T>(target: string, run: (staging: string) => T): T {
  const parent = path.dirname(target);
  const staging = fs.mkdtempSync(path.join(parent, `.${path.basename(target)}.certify-`));
  const owned = stageIdentity(staging);
  const parentOwned = stageIdentity(parent);
  const createdAt = Date.now();
  // A pathname/inode check followed by recursive deletion has a swap window.
  // Publication moves the owned tree on success; failure leaves private residue
  // for inspection instead of risking deletion of a foreign replacement.
  try { return run(staging); }
  catch (error) {
    const observation = retainedStageObservation(staging, target, owned, parentOwned, createdAt);
    const diagnostic = retainedStageDiagnostic(observation);
    if (error instanceof CertificationError) throw new CertificationError(error.code, error.pointer, `${error.message}; ${diagnostic}`, observation);
    if (error instanceof Error) {
      const wrapped = new Error(`${error.message}; ${diagnostic}`, { cause: error });
      const coded = error as Error & { code?: unknown; pointer?: unknown };
      Object.assign(wrapped, { retained_stage: observation });
      if (typeof coded.code === "string") Object.assign(wrapped, { code: coded.code });
      if (typeof coded.pointer === "string") Object.assign(wrapped, { pointer: coded.pointer });
      throw wrapped;
    }
    throw Object.assign(new Error(`non-Error certification failure; ${diagnostic}`, { cause: error }), { retained_stage: observation });
  }
}

/** Internal failure seam; it makes no Lean or cleanup claim. */
export function withCertificationStagingForTest<T>(target: string, run: (staging: string) => T): T {
  return withCertificationStaging(target, run);
}

export interface RetainedCertificationStageInspectionV1 {
  readonly schema_version: "domainspec.retained-certification-stage-inspection/v1";
  readonly staging_path: string;
  readonly observed_at_ms: number;
  readonly status: "same-inode-snapshot" | "missing" | "changed-or-replaced" | "unavailable";
  readonly direct_entry_count: number | null;
  readonly bounded_entry_count: boolean;
  readonly contains_symlink_or_special_entry: boolean | null;
  readonly review_due: boolean;
  readonly quiescence: "unverified";
  readonly ownership: "unverified";
  readonly cleanup_authorized: false;
}

/** Read-only, no-follow snapshot for a single structured failure observation.
 * A matching inode is not an ownership or quiescence proof, even when the
 * directory name still matches at the end of inspection. */
export function inspectRetainedCertificationStage(observation: RetainedCertificationStageV1,
  maxDirectEntries = 1024): RetainedCertificationStageInspectionV1 {
  if (observation.schema_version !== "domainspec.retained-certification-stage/v1" ||
      !path.isAbsolute(observation.staging_path) || path.resolve(observation.staging_path) !== observation.staging_path ||
      !path.isAbsolute(observation.target_directory) || path.resolve(observation.target_directory) !== observation.target_directory ||
      path.dirname(observation.staging_path) !== path.dirname(observation.target_directory) ||
      !path.basename(observation.staging_path).startsWith(`.${path.basename(observation.target_directory)}.certify-`) ||
      observation.attempt_id !== path.basename(observation.staging_path) ||
      !/^\d+$/.test(observation.created_dev) || !/^\d+$/.test(observation.created_ino) ||
      !/^\d+$/.test(observation.parent_dev) || !/^\d+$/.test(observation.parent_ino) ||
      !Number.isSafeInteger(maxDirectEntries) || maxDirectEntries < 1 || maxDirectEntries > 10000) {
    fail("MTCLI_CERTIFY_STAGING_INSPECTION", "/staging", "invalid retained-stage observation or inspection bound");
  }
  const observedAt = Date.now();
  const report = (status: RetainedCertificationStageInspectionV1["status"], count: number | null,
    bounded: boolean, special: boolean | null): RetainedCertificationStageInspectionV1 => ({
    schema_version: "domainspec.retained-certification-stage-inspection/v1", staging_path: observation.staging_path,
    observed_at_ms: observedAt, status, direct_entry_count: count, bounded_entry_count: bounded,
    contains_symlink_or_special_entry: special,
    review_due: observedAt - observation.created_at_ms >= observation.review_after_ms,
    quiescence: "unverified", ownership: "unverified", cleanup_authorized: false,
  });
  let parentDescriptor: number | undefined;
  let descriptor: number | undefined;
  let directory: fs.Dir | undefined;
  try {
    const parent = path.dirname(observation.staging_path);
    parentDescriptor = fs.openSync(parent, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
    const heldParent = fs.fstatSync(parentDescriptor, { bigint: true });
    if (!heldParent.isDirectory() || String(heldParent.dev) !== observation.parent_dev ||
        String(heldParent.ino) !== observation.parent_ino) return report("changed-or-replaced", null, true, null);
    const heldStagePath = `/proc/self/fd/${parentDescriptor}/${observation.attempt_id}`;
    descriptor = fs.openSync(heldStagePath, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
    const held = fs.fstatSync(descriptor, { bigint: true });
    if (!held.isDirectory() || String(held.dev) !== observation.created_dev || String(held.ino) !== observation.created_ino) {
      return report("changed-or-replaced", null, true, null);
    }
    directory = fs.opendirSync(`/proc/self/fd/${descriptor}`);
    let count = 0; let special = false; let complete = false;
    while (count <= maxDirectEntries) {
      const entry = directory.readSync();
      if (!entry) { complete = true; break; }
      count++;
      if (entry.isSymbolicLink() || (!entry.isFile() && !entry.isDirectory())) special = true;
    }
    const bounded = complete && count <= maxDirectEntries;
    const reportedCount = bounded ? count : null;
    let named: fs.BigIntStats;
    let namedParent: fs.BigIntStats;
    try {
      named = fs.lstatSync(heldStagePath, { bigint: true });
      namedParent = fs.lstatSync(parent, { bigint: true });
    } catch { return report("changed-or-replaced", reportedCount, bounded, special); }
    if (!named.isDirectory() || named.isSymbolicLink() || named.dev !== held.dev || named.ino !== held.ino ||
        !namedParent.isDirectory() || namedParent.isSymbolicLink() ||
        namedParent.dev !== heldParent.dev || namedParent.ino !== heldParent.ino) {
      return report("changed-or-replaced", reportedCount, bounded, special);
    }
    return report("same-inode-snapshot", reportedCount, bounded, special);
  } catch (error) {
    return report((error as NodeJS.ErrnoException).code === "ENOENT" ? "missing" :
      ["ELOOP", "ENOTDIR"].includes((error as NodeJS.ErrnoException).code ?? "") ? "changed-or-replaced" : "unavailable",
      null, true, null);
  } finally {
    if (directory) directory.closeSync();
    if (descriptor !== undefined) fs.closeSync(descriptor);
    if (parentDescriptor !== undefined) fs.closeSync(parentDescriptor);
  }
}
function noReplacePrimitive(): NoReplace {
  try { return loadAtomicPublicationNative(); }
  catch (error) { fail("MTCLI_CERTIFY_PUBLICATION_UNAVAILABLE", "/target", error instanceof Error ? error.message : "atomic no-replace publication is unavailable"); }
}
function publishStagedCertification(staging: string, target: string, native: NoReplace, beforePublish?: () => void, afterPublish?: () => void): void {
  const parent = path.dirname(target);
  if (path.dirname(staging) !== parent || path.basename(staging) === path.basename(target)) fail("MTCLI_CERTIFY_STAGING", "/target", "staging and target must be distinct siblings");
  const parentIdentity = fs.lstatSync(parent, { bigint: true });
  const ownedStage = stageIdentity(staging);
  const parentFd = fs.openSync(parent, fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | fs.constants.O_NOFOLLOW);
  try {
    const currentParent = () => {
      const held = fs.fstatSync(parentFd, { bigint: true });
      const named = fs.lstatSync(parent, { bigint: true });
      if (held.dev !== parentIdentity.dev || held.ino !== parentIdentity.ino || named.dev !== parentIdentity.dev || named.ino !== parentIdentity.ino || fs.realpathSync(parent) !== parent) fail("MTCLI_CERTIFY_TARGET_PARENT", "/target", "certification parent changed");
    };
    currentParent();
    beforePublish?.();
    currentParent();
    const currentStage = stageIdentity(staging);
    if (currentStage.dev !== ownedStage.dev || currentStage.ino !== ownedStage.ino) fail("MTCLI_CERTIFY_STAGING", "/target", "certification staging changed");
    try { native.renameNoReplace(parentFd, path.basename(staging), path.basename(target)); }
    catch (error) {
      const code = (error as NodeJS.ErrnoException).code;
      if (code === "EEXIST") fail("MTCLI_CERTIFY_TARGET_EXISTS", "/target", "a competing writer created the certify target");
      if (["ENOSYS", "EOPNOTSUPP", "ENOTSUP", "EINVAL", "EXDEV"].includes(code ?? "")) fail("MTCLI_CERTIFY_PUBLICATION_UNAVAILABLE", "/target", "atomic no-replace publication is unsupported on this filesystem");
      throw error;
    }
    try {
      afterPublish?.();
      currentParent();
      const published = fs.lstatSync(target, { bigint: true });
      if (published.dev !== ownedStage.dev || published.ino !== ownedStage.ino) throw new Error("published certification identity changed");
    } catch {
      fail("MTCLI_CERTIFY_PUBLICATION_INDETERMINATE", "/target", "atomic publication may have succeeded, but target identity could not be confirmed; do not retry without inspecting the target");
    }
  } finally { fs.closeSync(parentFd); }
}

/** Internal race seam; this does not run or claim a Lean proof. */
export function publishStagedCertificationForTest(staging: string, target: string, beforePublish?: () => void, afterPublish?: () => void): void {
  publishStagedCertification(staging, target, noReplacePrimitive(), beforePublish, afterPublish);
}

export function certifyProject(sourceRoot: string, targetDirectory: string): AssuranceCertificateV1 {
  normalizedNewDirectory(targetDirectory);
  const native = noReplacePrimitive();
  const pinnedLeanVersion = leanVersion();
  const { graph, certificate: compiledCertificate } = compileProject(sourceRoot);
  const interchange = createCheckedInterchange(graph);
  validateCheckedInterchange(JSON.parse(canonicalJson(interchange)), graph);

  return withCertificationStaging(targetDirectory, (staging) => {
    const interchangePath = path.join(staging, "checked-interchange.json");
    fs.writeFileSync(interchangePath, `${canonicalJson(interchange)}\n`, { flag: "wx", mode: 0o644 });
    validateCheckedInterchange(JSON.parse(fs.readFileSync(interchangePath, "utf8")), graph);

    const leanEntry = path.join(staging, "proof", "Current.lean");
    const formalization = materializeLeanMetaTypeFormalization(graph, leanEntry);
    const proofDirectory = path.dirname(leanEntry);
    const proofEnvironment = { ...process.env, ELAN_TOOLCHAIN: CERTIFY_LEAN_TOOLCHAIN, LEAN_PATH: "." };
    const decoderPath = path.join(proofDirectory, INTERCHANGE_DECODER_FILENAME);
    const decoderSource = fs.readFileSync(interchangeDecoderSourcePath, "utf8");
    fs.writeFileSync(decoderPath, decoderSource, { flag: "wx", mode: 0o644 });
    const compiledObjects: string[] = [];
    for (const filename of FORMALIZATION_LEAN_MODULE_FILENAMES) {
      const objectName = filename.replace(/\.lean$/, ".olean");
      const moduleCheck = spawnSync("lean", ["-o", objectName, filename], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment, timeout: SUBPROCESS_TIMEOUT_MS });
      if (moduleCheck.status !== 0) fail("MTCLI_CERTIFY_LEAN_PROOF", `/formalization/${filename}`, moduleCheck.stderr.trim() || moduleCheck.stdout.trim() || `Lean rejected ${filename}`);
      compiledObjects.push(path.join(proofDirectory, objectName));
    }
    const decoder = spawnSync("lean", ["--run", INTERCHANGE_DECODER_FILENAME, "../checked-interchange.json"], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment, timeout: SUBPROCESS_TIMEOUT_MS });
    if (decoder.status !== 0) fail("MTCLI_CERTIFY_LEAN_DECODER", "/checked-interchange", decoder.stderr.trim() || decoder.stdout.trim() || "Lean rejected the checked interchange");
    const expectedSummary = ["pass", graph.project_id, graph.source_manifest.manifest_sha256, graph.source_manifest.aggregate_sha256, interchange.formalization_payload.project_graph.graph_sha256, String(interchange.denominators.node_count), String(interchange.denominators.edge_count), String(interchange.denominators.obligation_count), String(interchange.denominators.applicable_witness_count)].join("\t");
    const decodedSummary = decoder.stdout.trim();
    if (decodedSummary !== expectedSummary) fail("MTCLI_CERTIFY_LEAN_DECODER_RESULT", "/checked-interchange", "Lean decoded summary differs from the compiled projection");
    const proof = spawnSync("lean", ["Current.lean"], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment, timeout: SUBPROCESS_TIMEOUT_MS });
    if (proof.status !== 0) fail("MTCLI_CERTIFY_LEAN_PROOF", "/formalization/Current.lean", proof.stderr.trim() || proof.stdout.trim() || "Lean rejected the proof unit");
    for (const objectPath of compiledObjects) fs.rmSync(objectPath, { force: true });

    const certificateBody = {
      schema_version: "domainspec.assurance-certificate/v1" as const,
      result: "pass" as const,
      project_id: graph.project_id,
      source_manifest_sha256: graph.source_manifest.manifest_sha256,
      compiled_certificate_sha256: compiledCertificate.certificate_sha256,
      compiled_graph_sha256: compiledCertificate.graph_sha256,
      checked_interchange_sha256: interchange.interchange_sha256,
      formalization: Object.freeze({
        render_payload_sha256: formalization.render_payload_sha256,
        project_graph_sha256: formalization.project_graph_sha256,
        lean_module_set_sha256: formalization.lean_module_set_sha256,
        proof_unit_sha256: formalization.proof_unit_sha256,
      }),
      independent_decoder: Object.freeze({
        source_sha256: sha256(decoderSource),
        decoded_summary_sha256: sha256(decodedSummary),
      }),
      denominators: interchange.denominators,
      checks: Object.freeze([
        Object.freeze({ check_id: "compiled-certificate" as const, result: "pass" as const }),
        Object.freeze({ check_id: "checked-interchange" as const, result: "pass" as const }),
        Object.freeze({ check_id: "lean-interchange-decoder" as const, result: "pass" as const }),
        Object.freeze({ check_id: "lean-proof-unit" as const, result: "pass" as const }),
      ]),
      toolchain: Object.freeze({
        cli_package: "@domainspec-v2/cli" as const,
        cli_version: CLI_VERSION,
        node: process.version,
        lean_toolchain: CERTIFY_LEAN_TOOLCHAIN,
        lean_version: pinnedLeanVersion as typeof CERTIFY_LEAN_VERSION,
      }),
      artifacts: Object.freeze({
        checked_interchange: "checked-interchange.json" as const,
        lean_decoder: "proof/DomainSpecCheckedInterchangeDecoder.lean" as const,
        lean_entry: "proof/Current.lean" as const,
        certificate: "assurance-certificate.json" as const,
      }),
      claim_ceiling: "exact-finite-projection-and-proof-no-universal-compiler-runtime-or-authority-claim" as const,
      authority_effect: "none" as const,
    };
    const assurance = Object.freeze({ ...certificateBody, certificate_sha256: sha256(canonicalJson(certificateBody)) });
    fs.writeFileSync(path.join(staging, "assurance-certificate.json"), `${canonicalJson(assurance)}\n`, { flag: "wx", mode: 0o644 });
    publishStagedCertification(staging, targetDirectory, native);
    return assurance;
  });
}

function inventory(root: string): readonly string[] {
  const files: string[] = [];
  function visit(directory: string): void {
    for (const name of fs.readdirSync(directory).sort()) {
      const absolute = path.join(directory, name);
      const stat = fs.lstatSync(absolute);
      if (stat.isSymbolicLink()) fail("MTCLI_CERTIFY_CHECK_SYMLINK", "/target", "certification target must not contain symbolic links");
      if (stat.isDirectory()) visit(absolute);
      else if (stat.isFile()) files.push(path.relative(root, absolute));
      else fail("MTCLI_CERTIFY_CHECK_FILE", "/target", "certification target contains an unsupported entry");
    }
  }
  visit(root);
  return Object.freeze(files);
}

function withCertificationCheckTemporary<T>(run: (temporaryParent: string) => T): { result: T; retainedParent: string } {
  const temporaryParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-certify-check-"));
  // The temporary proof tree is retained. Recursive pathname cleanup would
  // allow a swapped foreign directory to be removed after a stale inode check.
  try { return { result: run(temporaryParent), retainedParent: temporaryParent }; }
  catch (error) {
    const diagnostic = `check evidence parent ${JSON.stringify(temporaryParent)} retained for separate inspection; do not delete by pathname`;
    if (error instanceof CertificationError) throw new CertificationError(error.code, error.pointer,
      `${error.message}; ${diagnostic}`, error.retained_stage, temporaryParent);
    if (error instanceof Error) throw Object.assign(new Error(`${error.message}; ${diagnostic}`, { cause: error }),
      { code: (error as Error & { code?: unknown }).code, retained_evidence_directory: temporaryParent });
    throw Object.assign(new Error(`non-Error certification-check failure; ${diagnostic}`, { cause: error }),
      { retained_evidence_directory: temporaryParent });
  }
}

/** Internal race seam; it retains test-owned temporary trees on all outcomes. */
export function withCertificationCheckTemporaryForTest<T>(run: (temporaryParent: string) => T): { result: T; retainedParent: string } {
  return withCertificationCheckTemporary(run);
}

export function checkCertifiedProject(sourceRoot: string, targetDirectory: string): CertificationCheckV2 {
  if (!path.isAbsolute(targetDirectory) || path.resolve(targetDirectory) !== targetDirectory) fail("MTCLI_CERTIFY_TARGET", "/target", "certify-check target must be a normalized absolute directory path");
  let targetStats: fs.Stats;
  try { targetStats = fs.lstatSync(targetDirectory); } catch { fail("MTCLI_CERTIFY_CHECK_TARGET", "/target", "certification target does not exist"); }
  if (!targetStats.isDirectory() || targetStats.isSymbolicLink() || fs.realpathSync(targetDirectory) !== targetDirectory) fail("MTCLI_CERTIFY_CHECK_TARGET", "/target", "certification target must be a real directory");
  const { result, retainedParent } = withCertificationCheckTemporary((temporaryParent) => {
    const expectedTarget = path.join(temporaryParent, "expected");
    const expected = certifyProject(sourceRoot, expectedTarget);
    const expectedInventory = inventory(expectedTarget);
    const actualInventory = inventory(targetDirectory);
    const current = canonicalJson(actualInventory) === canonicalJson(expectedInventory)
      && expectedInventory.every((relative) => fs.readFileSync(path.join(targetDirectory, relative)).equals(fs.readFileSync(path.join(expectedTarget, relative))));
    return { result: current ? "pass" as const : "fail" as const, current,
      expected_certificate_sha256: expected.certificate_sha256 };
  });
  return Object.freeze({ schema_version: "domainspec.certification-check/v2", ...result,
    target_directory: targetDirectory, retained_evidence_directory: retainedParent,
    cleanup_authorized: false, authority_effect: "none" });
}
