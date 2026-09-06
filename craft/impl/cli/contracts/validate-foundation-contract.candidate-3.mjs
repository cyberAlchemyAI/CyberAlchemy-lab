#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { canonicalJson } from "../tools/validate-foundation-contract.mjs";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_REPO_ROOT = path.resolve(moduleDir, "../../../../..");
export const DEFAULT_CONTRACT_PATH = path.resolve(moduleDir, "foundation-contract.candidate-3.json");
export const DEFAULT_SCHEMA_PATH = path.resolve(moduleDir, "foundation-contract.candidate-3.schema.json");
export const EXPECTED_INPUT_DIGEST = "6cbf72ce404665f59ed29130eccc89caf9331bd4f6850533528f8d223882bef8";
export const EXPECTED_CONTRACT_DIGEST = "d57806f96c4c31c05a4913a17da7317fa262c99db354cba3504b767fbbab2fec";

const accepted = JSON.parse(fs.readFileSync(DEFAULT_CONTRACT_PATH, "utf8"));

export class Candidate3ContractError extends Error {
  constructor(code, pointer, message) {
    super(message);
    this.name = "Candidate3ContractError";
    this.code = code;
    this.pointer = pointer;
  }
}

export function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

export function computeInputDigest(contract) {
  return sha256(Buffer.from(canonicalJson({
    supersedes: contract.supersedes,
    decision_bindings: contract.decision_bindings,
    baseline_binding: contract.baseline_binding
  }), "utf8"));
}

export function computeContractDigest(contract) {
  const { contract_digest: ignored, ...body } = contract;
  return sha256(Buffer.from(canonicalJson(body), "utf8"));
}

export function sealCandidate3Contract(contract) {
  const sealed = structuredClone(contract);
  sealed.input_digest = computeInputDigest(sealed);
  sealed.contract_digest = computeContractDigest(sealed);
  return sealed;
}

function fail(code, pointer, message) {
  throw new Candidate3ContractError(code, pointer, message);
}

function requireExact(actual, expected, code, pointer) {
  if (canonicalJson(actual) !== canonicalJson(expected)) fail(code, pointer, "value differs from candidate-3");
}

function requireLiveFile(repoRoot, binding, pointer) {
  if (path.isAbsolute(binding.path)) fail("MTCLI_CONTRACT_SOURCE_PATH", `${pointer}/path`, "path must be repository-relative");
  const root = fs.realpathSync(repoRoot);
  const lexical = path.resolve(root, binding.path);
  const relative = path.relative(root, lexical);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("MTCLI_CONTRACT_SOURCE_PATH", `${pointer}/path`, "path escapes repository root");
  const real = fs.realpathSync(lexical);
  const realRelative = path.relative(root, real);
  if (realRelative.startsWith("..") || path.isAbsolute(realRelative) || !fs.statSync(real).isFile()) {
    fail("MTCLI_CONTRACT_SOURCE_PATH", `${pointer}/path`, "binding is not a contained regular file");
  }
  const observed = sha256(fs.readFileSync(real));
  if (observed !== binding.sha256) fail("MTCLI_CONTRACT_SOURCE_STALE", `${pointer}/sha256`, `expected ${binding.sha256}; observed ${observed}`);
}

export function validateCandidate3Contract(contract, options = {}) {
  const repoRoot = options.repoRoot ?? DEFAULT_REPO_ROOT;
  const schema = options.schema ?? JSON.parse(fs.readFileSync(DEFAULT_SCHEMA_PATH, "utf8"));
  const required = [...schema.required].sort();
  requireExact(Object.keys(contract).sort(), required, "MTCLI_CONTRACT_SCHEMA", "$");
  requireExact(schema.$id, "domainspec.stable-foundation-cli.foundation-contract/v3", "MTCLI_CONTRACT_SCHEMA", "/$schema/$id");
  requireExact(schema.additionalProperties, false, "MTCLI_CONTRACT_SCHEMA", "/$schema/additionalProperties");
  requireExact(contract.schema_version, schema.$id, "MTCLI_CONTRACT_SCHEMA", "/schema_version");
  requireExact(contract.contract_id, "stable-foundation-cli", "MTCLI_CONTRACT_SCHEMA", "/contract_id");
  requireExact(contract.candidate_version, "candidate-3", "MTCLI_CONTRACT_SCHEMA", "/candidate_version");
  requireExact(contract.authority_effect, "none", "MTCLI_CONTRACT_AUTHORITY", "/authority_effect");
  requireExact(contract.supersedes, accepted.supersedes, "MTCLI_CONTRACT_SUPERSESSION", "/supersedes");
  requireExact(contract.decision_bindings, accepted.decision_bindings, "MTCLI_CONTRACT_DECISION", "/decision_bindings");
  requireExact(contract.selections, accepted.selections, "MTCLI_CONTRACT_SELECTION", "/selections");
  requireExact(contract.baseline_binding, accepted.baseline_binding, "MTCLI_CONTRACT_BASELINE", "/baseline_binding");
  requireExact(contract.supported_surface, accepted.supported_surface, "MTCLI_CONTRACT_WRITE_SCOPE", "/supported_surface");
  requireExact(contract.invariants, accepted.invariants, "MTCLI_CONTRACT_INVARIANT", "/invariants");
  requireExact(contract.claim_ceiling, accepted.claim_ceiling, "MTCLI_CONTRACT_CLAIM_CEILING", "/claim_ceiling");

  requireExact(contract.input_digest, computeInputDigest(contract), "MTCLI_CONTRACT_INPUT_DIGEST", "/input_digest");
  requireExact(contract.input_digest, EXPECTED_INPUT_DIGEST, "MTCLI_CONTRACT_INPUT_DIGEST", "/input_digest");
  requireExact(contract.contract_digest, computeContractDigest(contract), "MTCLI_CONTRACT_DIGEST", "/contract_digest");
  requireExact(contract.contract_digest, EXPECTED_CONTRACT_DIGEST, "MTCLI_CONTRACT_DIGEST", "/contract_digest");
  requireExact(schema.properties.input_digest.const, EXPECTED_INPUT_DIGEST, "MTCLI_CONTRACT_SCHEMA", "/$schema/properties/input_digest/const");
  requireExact(schema.properties.contract_digest.const, EXPECTED_CONTRACT_DIGEST, "MTCLI_CONTRACT_SCHEMA", "/$schema/properties/contract_digest/const");

  requireLiveFile(repoRoot, contract.supersedes.contract, "/supersedes/contract");
  requireLiveFile(repoRoot, contract.supersedes.schema, "/supersedes/schema");
  for (const [name, binding] of Object.entries(contract.decision_bindings)) requireLiveFile(repoRoot, binding, `/decision_bindings/${name}`);
  requireLiveFile(repoRoot, contract.baseline_binding.manifest, "/baseline_binding/manifest");
  for (const name of ["source", "provider", "binding"]) requireLiveFile(repoRoot, contract.baseline_binding.selected_realization[name], `/baseline_binding/selected_realization/${name}`);

  const baseline = JSON.parse(fs.readFileSync(path.resolve(repoRoot, contract.baseline_binding.manifest.path), "utf8"));
  requireExact(baseline.baseline_id, contract.baseline_binding.baseline_id, "MTCLI_CONTRACT_BASELINE", "/baseline_binding/baseline_id");
  requireExact(baseline.baseline_digest, contract.baseline_binding.baseline_digest, "MTCLI_CONTRACT_BASELINE", "/baseline_binding/baseline_digest");
  const exactRows = baseline.realization_rows.filter((row) => canonicalJson(row) === canonicalJson(contract.baseline_binding.selected_realization));
  requireExact(exactRows.length, 1, "MTCLI_CONTRACT_BASELINE", "/baseline_binding/selected_realization");

  return {
    schema_version: "domainspec.stable-foundation-cli.foundation-contract-validation/v3",
    result: "pass",
    candidate_version: contract.candidate_version,
    selected_realization: `${contract.baseline_binding.selected_realization.meta_type_id}/${contract.baseline_binding.selected_realization.language}`,
    input_digest: contract.input_digest,
    contract_digest: contract.contract_digest,
    authority_effect: "none"
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const contractPath = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_CONTRACT_PATH;
  try {
    process.stdout.write(`${JSON.stringify(validateCandidate3Contract(JSON.parse(fs.readFileSync(contractPath, "utf8"))))}\n`);
  } catch (error) {
    if (error instanceof Candidate3ContractError) {
      process.stderr.write(`${JSON.stringify({ result: "fail", code: error.code, pointer: error.pointer })}\n`);
      process.exitCode = 4;
    } else {
      process.stderr.write(`${JSON.stringify({ result: "fail", code: "MTCLI_CONTRACT_INTERNAL" })}\n`);
      process.exitCode = 24;
    }
  }
}
