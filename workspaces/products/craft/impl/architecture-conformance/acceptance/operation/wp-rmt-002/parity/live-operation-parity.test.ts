import {createHash} from "node:crypto";
import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {listFactoryNodeProvidersV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {operationPythonV1Provider} from
  "../../../../factory/registry/providers/operation-python-v1.js";
import {operationRustV1Provider} from
  "../../../../factory/registry/providers/operation-rust-v1.js";
import {operationTypeScriptV1Provider} from
  "../../../../factory/registry/providers/operation-typescript-v1.js";
import {PYTHON_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/python/state-changing-v1/index.js";
import {RUST_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/rust/state-changing-v1/index.js";
import {TYPESCRIPT_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/typescript/state-changing-v1/index.js";
import {evaluateOperationParity} from "./evaluate-operation-parity.js";

type JsonObject = Record<string, unknown>;
type RawInputs = Readonly<Record<string, string>>;
const repositoryRoot = process.cwd();
const PROVIDER_IDS = Object.freeze([
  "operation-typescript-v1",
  "operation-python-v1",
  "operation-rust-v1",
] as const);
const CASES = Object.freeze([
  Object.freeze({
    language: "typescript",
    provider: operationTypeScriptV1Provider,
    paths: TYPESCRIPT_OPERATION_RAW_PATHS,
    provider_sha256:
      "1bc82cc0284069bfaa115f4bd51e423e259c6b38428a6a8d980132e9ba05a06f",
    target_sha256:
      "abbd57adf9587ef4436524148482a9ab5b92954d49e61dc444f57036874679f4",
    binding_file_sha256:
      "c54431ee5d946415df30fffab71528df1928bc8b8f2bdfb49ccc6df7784952b1",
    binding_id: "typescript.complete-settlement.bound-operation/v1",
    bound_role_count: 34,
  }),
  Object.freeze({
    language: "python",
    provider: operationPythonV1Provider,
    paths: PYTHON_OPERATION_RAW_PATHS,
    provider_sha256:
      "04c5931e9daa3a281f49d506889058df991170f5f21b8766a5b48d7ff2f9a967",
    target_sha256:
      "d5783a8c8e52971036efd3e230ad83e7379050da63ae6383533fe9f917406d49",
    binding_file_sha256:
      "15545ea614fd9521b53f8f2605fcefbce8d6be334bd9909a7f9271cd1d6774d2",
    binding_id: "python.complete-settlement.bound-operation/v1",
    bound_role_count: 35,
  }),
  Object.freeze({
    language: "rust",
    provider: operationRustV1Provider,
    paths: RUST_OPERATION_RAW_PATHS,
    provider_sha256:
      "c34962ceef4fa5eabd6ccef9f7df100e31e3296ae7beef1f68d19aeb317f3629",
    target_sha256:
      "49723621b79c30372b9871f1ff09a595aff0a88f63d58c5dad8ce1ca7edbdb62",
    binding_file_sha256:
      "e3ab4c0f5c3cae3edebc136eea34c6277214cb5e9a1878d81bad73ff07623db2",
    binding_id: "rust.complete-settlement.bound-operation/v1",
    bound_role_count: 34,
  }),
] as const);

const isObject = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const canonical = (value: unknown): unknown => Array.isArray(value)
  ? value.map(canonical)
  : isObject(value)
    ? Object.fromEntries(Object.entries(value).sort(([left], [right]) =>
      Buffer.from(left).compare(Buffer.from(right))).map(([key, child]) =>
      [key, canonical(child)]))
    : value;
const canonicalJson = (value: unknown): string => JSON.stringify(
  canonical(value),
);
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");
const readRaw = async (
  paths: Readonly<Record<string, string>>,
): Promise<RawInputs> => Object.freeze(Object.fromEntries(await Promise.all(
  Object.entries(paths).map(async ([role, path]) => [
    role,
    await readFile(resolve(repositoryRoot, path), "utf8"),
  ]),
)));
const registryIds = (): readonly string[] => listFactoryNodeProvidersV1()
  .map(({provider_id: providerId}) => providerId);

describe("exact live Operation provider parity", () => {
  it("hash-closes all three direct providers and every binding role", async () => {
    for (const candidate of CASES) {
      const paths: Readonly<Record<string, string>> = candidate.paths;
      const raw = await readRaw(paths);
      expect(Object.keys(raw).sort()).toEqual(
        [...candidate.provider.required_input_roles].sort(),
      );
      expect(candidate.provider.provider_version).toBe("1.0.0");
      expect(candidate.provider.compatible_kinds).toEqual(["direct-proof"]);
      expect([...candidate.provider.component_paths].sort()).toEqual(
        [...new Set(Object.values(paths))].sort(),
      );
      expect(sha256(raw.provider)).toBe(candidate.provider_sha256);
      expect(sha256(raw.source)).toBe(candidate.target_sha256);
      expect(sha256(raw.binding)).toBe(candidate.binding_file_sha256);

      const binding = JSON.parse(raw.binding) as JsonObject;
      const digest = binding.binding_sha256;
      const {binding_sha256: _digest, ...body} = binding;
      expect(binding.binding_id).toBe(candidate.binding_id);
      expect(binding.authority_effect).toBe("none");
      expect(typeof digest).toBe("string");
      expect(sha256(canonicalJson(body))).toBe(digest);
      const refs = binding.refs;
      expect(isObject(refs)).toBe(true);
      if (!isObject(refs)) throw new Error("RMT_OP_PARITY_BINDING_REFS_INVALID");
      const boundRoles = Object.keys(paths)
        .filter((role) => role !== "binding").sort();
      expect(Object.keys(refs).sort()).toEqual(boundRoles);
      expect(boundRoles).toHaveLength(candidate.bound_role_count);
      for (const role of boundRoles) {
        const ref = refs[role];
        expect(isObject(ref)).toBe(true);
        if (!isObject(ref)) throw new Error("RMT_OP_PARITY_BINDING_REF_INVALID");
        expect(Object.keys(ref).sort()).toEqual(["path", "sha256"]);
        expect(ref.path).toBe(paths[role]);
        expect(ref.sha256).toBe(sha256(raw[role]));
      }
    }
  });

  it("executes the exact unregistered providers without mutating inputs", async () => {
    for (const providerId of PROVIDER_IDS) {
      expect(registryIds()).not.toContain(providerId);
    }
    const results: Record<string, unknown> = {};
    for (const candidate of CASES) {
      const raw = await readRaw(candidate.paths);
      const before = sha256(canonicalJson(raw));
      const result = await candidate.provider.execute({
        raw_inputs: raw,
        upstream: {},
      });
      expect(sha256(canonicalJson(raw))).toBe(before);
      const semanticOutput = result.semantic_output;
      expect(isObject(semanticOutput)).toBe(true);
      if (!isObject(semanticOutput)) {
        throw new Error("RMT_OP_PARITY_RESULT_OUTPUT_INVALID");
      }
      const proof = semanticOutput.proof;
      expect(isObject(proof)).toBe(true);
      if (!isObject(proof)) throw new Error("RMT_OP_PARITY_PROOF_INVALID");
      const proofTarget = proof.target;
      const proofBinding = proof.binding;
      const rawBinding = JSON.parse(raw.binding) as JsonObject;
      const rawRefs = rawBinding.refs;
      expect(isObject(proofTarget)).toBe(true);
      expect(isObject(proofBinding)).toBe(true);
      expect(isObject(rawRefs)).toBe(true);
      if (!isObject(proofTarget) || !isObject(proofBinding) ||
          !isObject(rawRefs) || !isObject(rawRefs.source) ||
          !isObject(rawRefs.provider)) {
        throw new Error("RMT_OP_PARITY_PROOF_BINDING_INVALID");
      }
      expect(proofTarget.source_sha256).toBe(rawRefs.source.sha256);
      expect(proofBinding.binding_sha256).toBe(rawBinding.binding_sha256);
      expect(proofBinding.provider_sha256).toBe(rawRefs.provider.sha256);
      expect(proofBinding.bound_role_count).toBe(candidate.bound_role_count);
      results[candidate.language] = {
        provider_id: candidate.provider.provider_id,
        result,
      };
    }
    const parity = evaluateOperationParity(results);
    expect(parity.result).toBe("pass");
    expect(parity.native_hash_byte_comparison).toBe(false);
    expect(parity.authority_effect).toBe("none");
    for (const providerId of PROVIDER_IDS) {
      expect(registryIds()).not.toContain(providerId);
    }
  }, 120_000);
});
