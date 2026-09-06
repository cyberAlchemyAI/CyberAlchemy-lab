#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
export const DEFAULT_REPO_ROOT = path.resolve(moduleDir, "../../../../..");
export const DEFAULT_CONTRACT_PATH = path.resolve(moduleDir, "../contracts/foundation-contract.json");
export const DEFAULT_SCHEMA_PATH = path.resolve(moduleDir, "../contracts/foundation-contract.schema.json");

export const REQUIRED_SELECTIONS = [
  ["SF-01", "A"], ["SF-02", "P2"], ["SF-03", "C2"], ["SF-04", "S1"],
  ["SF-05", "A1"], ["SF-06", "E1"], ["SF-07", "M1"], ["SF-08", "K2"],
  ["SF-09", "D1"], ["SF-10", "O1"], ["SF-11", "EC1"], ["SF-12", "B1"],
  ["SF-13", "RC1"], ["SF-14", "PK1"], ["SF-15", "SEC1"], ["SF-16", "IR1"],
  ["SF-17", "L2"], ["SF-18", "BS2"], ["SF-19", "OUT2"], ["SF-20", "RB1"],
  ["SF-21", "RET1"]
];

const EXPECTED_BINDINGS = {
  owner_decision: {
    path: "projects/domainspec-v2/development/first-production-release/decisions/2026-08-16-first-stable-foundation-candidate.md",
    sha256: "2168de08e9e0ea72a29ce74fb9a3285094aebaa05d72df34d9749e5cbdac20c9"
  },
  runtime_decision: {
    path: "projects/domainspec-v2/development/first-production-release/decisions/2026-08-29-node-26-runtime.json",
    sha256: "d1474617adf886670eeebf1f8c1a5092e61fa1d9fcd8cbfc9f6ebab1ba6fbd89"
  },
  product_contract: {
    path: "projects/domainspec-v2/development/first-production-release/decisions/2026-07-12-product-release-contract.md",
    sha256: "a5852275365563fc2378e3b6a86d9f4da03cc9efbaef249ffa41f329c3bf5b43"
  },
  profile_decision: {
    path: "projects/domainspec-v2/development/first-production-release/decisions/2026-07-17-fpr02-supported-profile-decision.md",
    sha256: "36641f3b488b4b617eb5742082c2b16049a8a7003ce26f206c27f014f2e9a491"
  }
};

const EXPECTED_SURFACE = {
  command_name: "domainspec-v2",
  commands: [
    { name: "lint", arguments: ["<explicit-project-root>"], options: ["--page-size", "--page-token"] },
    { name: "receipt", arguments: ["<explicit-project-root>"], options: [] }
  ],
  package_name: "@domainspec-v2/cli",
  development_workspace: "@domainspec-v2/impl",
  profile: {
    id: "feature-with-independent-node-and-edge-files",
    version: "1",
    backend_kind_count: 13,
    backend_relationship_signature_count: 16,
    admission_owner: "definitions/minted-project",
    admission_state: "external-required"
  },
  conformance_claim: "exact-profile-causal-implementation-conformance",
  runtime: { node: "v26.8.1", platform: "linux", arch: "x64" },
  build: { package_manager: "npm@11.19.0", lockfile_version: 3, lifecycle_scripts: "deny-except-reviewed-network-disabled-build" },
  distribution: "private-repository-local-immutable-tagged-checkout",
  writes: "none"
};

const EXPECTED_INVARIANTS = [
  "claim-cannot-exceed-profile-bound-causal-proof",
  "durable-state-and-outbox-occurrence-share-one-atomic-boundary",
  "supported-cli-starts-at-an-explicit-project-root",
  "build-and-runtime-remain-separate",
  "result-and-fault-channels-do-not-collapse",
  "compatibility-does-not-rewrite-history"
];

const EXPECTED_CEILING = {
  profile_admission: false,
  implementation_conformance: false,
  release: false,
  publication: false,
  deployment: false,
  production: false
};

export class FoundationContractError extends Error {
  constructor(code, pointer, message) {
    super(message);
    this.name = "FoundationContractError";
    this.code = code;
    this.pointer = pointer;
  }
}

export function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function fail(code, pointer, message) {
  throw new FoundationContractError(code, pointer, message);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function requireExactKeys(value, expected, pointer) {
  if (!isObject(value)) fail("SFC_CONTRACT_SCHEMA", pointer, "expected object");
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (canonicalJson(actual) !== canonicalJson(wanted)) {
    fail("SFC_CONTRACT_SCHEMA", pointer, `expected keys ${wanted.join(",")}; observed ${actual.join(",")}`);
  }
}

function requireExactValue(actual, expected, code, pointer) {
  if (canonicalJson(actual) !== canonicalJson(expected)) fail(code, pointer, "value differs from the accepted foundation contract");
}

function resolveContainedFile(repoRoot, relativePath, pointer) {
  if (path.isAbsolute(relativePath)) fail("SFC_CONTRACT_SOURCE_PATH", pointer, "source path must be repository-relative");
  const root = fs.realpathSync(repoRoot);
  const absolute = path.resolve(root, relativePath);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) fail("SFC_CONTRACT_SOURCE_PATH", pointer, "source path escapes repository root");
  const real = fs.realpathSync(absolute);
  const realRelative = path.relative(root, real);
  if (realRelative.startsWith("..") || path.isAbsolute(realRelative)) fail("SFC_CONTRACT_SOURCE_PATH", pointer, "source real path escapes repository root");
  if (!fs.statSync(real).isFile()) fail("SFC_CONTRACT_SOURCE_PATH", pointer, "source is not a regular file");
  return real;
}

export function computeInputDigest(decisionBindings) {
  return sha256(Buffer.from(canonicalJson(decisionBindings), "utf8"));
}

export function computeContractDigest(contract) {
  const { contract_digest: ignored, ...body } = contract;
  return sha256(Buffer.from(canonicalJson(body), "utf8"));
}

export function sealFoundationContract(contract) {
  const sealed = structuredClone(contract);
  sealed.input_digest = computeInputDigest(sealed.decision_bindings);
  sealed.contract_digest = computeContractDigest(sealed);
  return sealed;
}

export function validateFoundationContract(contract, options = {}) {
  const repoRoot = options.repoRoot ?? DEFAULT_REPO_ROOT;
  const schema = options.schema ?? JSON.parse(fs.readFileSync(DEFAULT_SCHEMA_PATH, "utf8"));
  requireExactValue(schema.$id, "domainspec.stable-foundation-cli.foundation-contract/v2", "SFC_CONTRACT_SCHEMA", "/$schema/$id");
  requireExactValue(schema.additionalProperties, false, "SFC_CONTRACT_SCHEMA", "/$schema/additionalProperties");
  requireExactKeys(contract, ["schema_version", "contract_id", "candidate_version", "decision_bindings", "selections", "supported_surface", "invariants", "claim_ceiling", "authority_effect", "input_digest", "contract_digest"], "$");
  requireExactValue(contract.schema_version, schema.$id, "SFC_CONTRACT_SCHEMA", "/schema_version");
  requireExactValue(contract.contract_id, "stable-foundation-cli", "SFC_CONTRACT_SCHEMA", "/contract_id");
  requireExactValue(contract.candidate_version, "candidate-2", "SFC_CONTRACT_SCHEMA", "/candidate_version");

  requireExactKeys(contract.decision_bindings, Object.keys(EXPECTED_BINDINGS), "/decision_bindings");
  for (const [name, expected] of Object.entries(EXPECTED_BINDINGS)) {
    const pointer = `/decision_bindings/${name}`;
    requireExactKeys(contract.decision_bindings[name], ["path", "sha256"], pointer);
    requireExactValue(contract.decision_bindings[name].path, expected.path, "SFC_CONTRACT_SOURCE_PATH", `${pointer}/path`);
    requireExactValue(contract.decision_bindings[name].sha256, expected.sha256, "SFC_CONTRACT_SOURCE_STALE", `${pointer}/sha256`);
    const source = resolveContainedFile(repoRoot, expected.path, `${pointer}/path`);
    const observed = sha256(fs.readFileSync(source));
    if (observed !== expected.sha256) fail("SFC_CONTRACT_SOURCE_STALE", `${pointer}/sha256`, `source digest ${observed} does not match ${expected.sha256}`);
  }

  if (!Array.isArray(contract.selections) || contract.selections.length !== REQUIRED_SELECTIONS.length) {
    fail("SFC_CONTRACT_SELECTION", "/selections", "exactly 21 ordered selections are required");
  }
  contract.selections.forEach((selection, index) => {
    requireExactKeys(selection, ["id", "option"], `/selections/${index}`);
    const [id, option] = REQUIRED_SELECTIONS[index];
    requireExactValue(selection, { id, option }, "SFC_CONTRACT_SELECTION", `/selections/${index}`);
  });

  requireExactValue(contract.supported_surface, EXPECTED_SURFACE, "SFC_CONTRACT_SELECTION", "/supported_surface");
  requireExactValue(contract.invariants, EXPECTED_INVARIANTS, "SFC_CONTRACT_SELECTION", "/invariants");
  requireExactValue(contract.claim_ceiling, EXPECTED_CEILING, "SFC_CONTRACT_CLAIM_CEILING", "/claim_ceiling");
  requireExactValue(contract.authority_effect, "none", "SFC_CONTRACT_AUTHORITY", "/authority_effect");

  const expectedInputDigest = computeInputDigest(contract.decision_bindings);
  requireExactValue(contract.input_digest, expectedInputDigest, "SFC_CONTRACT_INPUT_DIGEST", "/input_digest");
  const expectedContractDigest = computeContractDigest(contract);
  requireExactValue(contract.contract_digest, expectedContractDigest, "SFC_CONTRACT_DIGEST", "/contract_digest");
  return {
    schema_version: "domainspec.stable-foundation-cli.foundation-contract-validation/v2",
    result: "pass",
    selection_count: contract.selections.length,
    input_digest: expectedInputDigest,
    contract_digest: expectedContractDigest,
    authority_effect: "none"
  };
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const contractPath = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_CONTRACT_PATH;
  try {
    process.stdout.write(`${JSON.stringify(validateFoundationContract(readJson(contractPath)))}\n`);
  } catch (error) {
    if (error instanceof FoundationContractError) {
      process.stderr.write(`${JSON.stringify({ result: "fail", code: error.code, pointer: error.pointer })}\n`);
      process.exitCode = 4;
    } else {
      process.stderr.write(`${JSON.stringify({ result: "fail", code: "SFC_CONTRACT_INTERNAL" })}\n`);
      process.exitCode = 24;
    }
  }
}
