import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync, type SpawnSyncReturns } from "node:child_process";
import { fileURLToPath } from "node:url";

import { compileProject } from "../compilation/certificate.js";
import { materializeLeanMetaTypeFormalization } from "../formalization/projection.js";
import { FORMALIZATION_LEAN_MODULE_FILENAMES } from "../formalization/kernel.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { CLI_VERSION } from "../version.js";
import { createCheckedInterchange, validateCheckedInterchange, type CheckedInterchangeV1 } from "./checked-interchange.js";

export const CERTIFY_LEAN_TOOLCHAIN = "leanprover/lean4:v4.33.1" as const;
export const CERTIFY_LEAN_VERSION = "4.33.1" as const;
const INTERCHANGE_DECODER_FILENAME = "DomainSpecCheckedInterchangeDecoder.lean" as const;
const interchangeDecoderSourcePath = fileURLToPath(new URL(`../../lean/${INTERCHANGE_DECODER_FILENAME}`, import.meta.url));

export interface AssuranceCertificateV1 {
  readonly schema_version: "domainspec.assurance-certificate/v1-candidate";
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
  readonly schema_version: "domainspec.certification-check/v1-candidate";
  readonly result: "pass" | "fail";
  readonly current: boolean;
  readonly target_directory: string;
  readonly expected_certificate_sha256: string;
  readonly authority_effect: "none";
}

export class CertificationError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "CertificationError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new CertificationError(code, pointer, message);
}

function leanFailure(result: SpawnSyncReturns<string>, fallback: string): string {
  return result.stderr?.trim() || result.stdout?.trim() || result.error?.message || fallback;
}

function leanVersion(): string {
  const result = spawnSync("lean", ["--version"], {
    encoding: "utf8",
    timeout: 10_000,
    env: { ...process.env, ELAN_TOOLCHAIN: CERTIFY_LEAN_TOOLCHAIN },
  });
  if (result.status !== 0) fail("MTCLI_CERTIFY_LEAN_UNAVAILABLE", "/toolchain/lean", leanFailure(result, "pinned Lean toolchain is unavailable"));
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

export function certifyProject(sourceRoot: string, targetDirectory: string): AssuranceCertificateV1 {
  normalizedNewDirectory(targetDirectory);
  const pinnedLeanVersion = leanVersion();
  const { graph, certificate: compiledCertificate } = compileProject(sourceRoot);
  const interchange = createCheckedInterchange(graph);
  validateCheckedInterchange(JSON.parse(canonicalJson(interchange)), graph);

  const parent = path.dirname(targetDirectory);
  const staging = fs.mkdtempSync(path.join(parent, `.${path.basename(targetDirectory)}.certify-`));
  try {
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
      const moduleCheck = spawnSync("lean", ["-o", objectName, filename], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment });
      if (moduleCheck.status !== 0) fail("MTCLI_CERTIFY_LEAN_PROOF", `/formalization/${filename}`, leanFailure(moduleCheck, `Lean rejected ${filename}`));
      compiledObjects.push(path.join(proofDirectory, objectName));
    }
    const decoder = spawnSync("lean", ["--run", INTERCHANGE_DECODER_FILENAME, "../checked-interchange.json"], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment });
    if (decoder.status !== 0) fail("MTCLI_CERTIFY_LEAN_DECODER", "/checked-interchange", leanFailure(decoder, "Lean rejected the checked interchange"));
    const expectedSummary = ["pass", graph.project_id, graph.source_manifest.manifest_sha256, graph.source_manifest.aggregate_sha256, interchange.formalization_payload.project_graph.graph_sha256, String(interchange.denominators.node_count), String(interchange.denominators.edge_count), String(interchange.denominators.obligation_count), String(interchange.denominators.applicable_witness_count)].join("\t");
    const decodedSummary = decoder.stdout.trim();
    if (decodedSummary !== expectedSummary) fail("MTCLI_CERTIFY_LEAN_DECODER_RESULT", "/checked-interchange", "Lean decoded summary differs from the compiled projection");
    const proof = spawnSync("lean", ["Current.lean"], { cwd: proofDirectory, encoding: "utf8", env: proofEnvironment });
    if (proof.status !== 0) fail("MTCLI_CERTIFY_LEAN_PROOF", "/formalization/Current.lean", leanFailure(proof, "Lean rejected the proof unit"));
    for (const objectPath of compiledObjects) fs.rmSync(objectPath, { force: true });

    const certificateBody = {
      schema_version: "domainspec.assurance-certificate/v1-candidate" as const,
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
    if (fs.existsSync(targetDirectory)) fail("MTCLI_CERTIFY_TARGET_EXISTS", "/target", "a competing writer created the certify target");
    fs.renameSync(staging, targetDirectory);
    return assurance;
  } catch (error) {
    if (fs.existsSync(staging)) fs.rmSync(staging, { recursive: true, force: true });
    if (["EEXIST", "ENOTEMPTY"].includes((error as NodeJS.ErrnoException).code ?? "")) fail("MTCLI_CERTIFY_TARGET_EXISTS", "/target", "a competing writer created the certify target");
    throw error;
  }
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

export function checkCertifiedProject(sourceRoot: string, targetDirectory: string): CertificationCheckV1 {
  if (!path.isAbsolute(targetDirectory) || path.resolve(targetDirectory) !== targetDirectory) fail("MTCLI_CERTIFY_TARGET", "/target", "certify-check target must be a normalized absolute directory path");
  let targetStats: fs.Stats;
  try { targetStats = fs.lstatSync(targetDirectory); } catch { fail("MTCLI_CERTIFY_CHECK_TARGET", "/target", "certification target does not exist"); }
  if (!targetStats.isDirectory() || targetStats.isSymbolicLink() || fs.realpathSync(targetDirectory) !== targetDirectory) fail("MTCLI_CERTIFY_CHECK_TARGET", "/target", "certification target must be a real directory");
  const temporaryParent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-certify-check-"));
  const expectedTarget = path.join(temporaryParent, "expected");
  try {
    const expected = certifyProject(sourceRoot, expectedTarget);
    const expectedInventory = inventory(expectedTarget);
    const actualInventory = inventory(targetDirectory);
    const current = canonicalJson(actualInventory) === canonicalJson(expectedInventory)
      && expectedInventory.every((relative) => fs.readFileSync(path.join(targetDirectory, relative)).equals(fs.readFileSync(path.join(expectedTarget, relative))));
    return Object.freeze({
      schema_version: "domainspec.certification-check/v1-candidate",
      result: current ? "pass" : "fail",
      current,
      target_directory: targetDirectory,
      expected_certificate_sha256: expected.certificate_sha256,
      authority_effect: "none",
    });
  } finally {
    fs.rmSync(temporaryParent, { recursive: true, force: true });
  }
}
