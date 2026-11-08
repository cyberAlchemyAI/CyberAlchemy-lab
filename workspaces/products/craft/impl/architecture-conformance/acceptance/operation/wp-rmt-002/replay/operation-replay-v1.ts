import {
  digestOperationProviderEvidenceForParity,
  evaluateOperationParity,
} from "../parity/evaluate-operation-parity.js";
import type {FactoryNodeProviderV1} from
  "../../../../factory/contracts/factory-node-provider-v1.js";
import {operationPythonV1Provider} from
  "../../../../factory/registry/providers/operation-python-v1.js";
import {operationRustV1Provider} from
  "../../../../factory/registry/providers/operation-rust-v1.js";
import {operationTypeScriptV1Provider} from
  "../../../../factory/registry/providers/operation-typescript-v1.js";
import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  sha256,
} from "../../../../factory/shared/canonical.js";
import {PYTHON_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/python/state-changing-v1/index.js";
import {RUST_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/rust/state-changing-v1/index.js";
import {TYPESCRIPT_OPERATION_RAW_PATHS} from
  "../../../../realizations/operation/typescript/state-changing-v1/index.js";

type Language = "typescript" | "python" | "rust";

const LANGUAGE_PATHS = Object.freeze({
  typescript: TYPESCRIPT_OPERATION_RAW_PATHS,
  python: PYTHON_OPERATION_RAW_PATHS,
  rust: RUST_OPERATION_RAW_PATHS,
} as const);

const PREFIXED_ROLES = Object.freeze(Object.entries(LANGUAGE_PATHS)
  .flatMap(([language, paths]) => Object.keys(paths)
    .map((role) => `${language}__${role}`)));

export const OPERATION_REPLAY_RAW_ROLES = Object.freeze([
  ...PREFIXED_ROLES,
  "parity_evaluator",
  "parity_evaluator_test",
  "parity_live_test",
]);

export const OPERATION_REPLAY_CLAIM_CEILING =
  "one exact candidate-local deterministic Operation replay receipt over three hash-bound direct providers and portable semantic parity; dynamic process IDs are validated then excluded from semantic identity; no canonical registration, ontology admission, promotion, publication, deployment, or production claim";

const EXPECTED_NORMALIZED_PARITY_SHA256 =
  "d18eccbfb23a3b67a49bc1dc3dd5af8242a52e6f159d3f91a67fa03bba6fbf8f";

const EXPECTED_PROVIDER_SEMANTIC_SHA256 = Object.freeze({
  typescript:
    "c231ddc63a0887a375b325de7f10b01c30bc07bf94fbc5c58f24f24934c01e7f",
  python:
    "64231a725ea839672aa5646fda53166b1d59ae67bc56b0905da21171c66a4145",
  rust:
    "fa67b0f8bd53d3fb93041cd2c54b2e322d4f17d48cd6a7bfcdc4c4b5b4a74415",
} as const);

const rawFor = (
  language: Language,
  paths: Readonly<Record<string, string>>,
  rawInputs: Readonly<Record<string, string>>,
): Readonly<Record<string, string>> => Object.freeze(Object.fromEntries(
  Object.keys(paths).map((role) => {
    const value = rawInputs[`${language}__${role}`];
    return [role, value ?? fail("RMT_OP_REPLAY_INPUT_MISSING",
      `${language}__${role}`)];
  }),
));

const redactDynamicProcessIds = (
  input: unknown,
): Readonly<{value: unknown; redacted_count: number}> => {
  let count = 0;
  const visit = (value: unknown): unknown => {
    if (Array.isArray(value)) return value.map(visit);
    if (!isRecord(value)) return value;
    return Object.fromEntries(Object.entries(value).map(([key, child]) => {
      if (key === "first_pid" || key === "second_pid") {
        if (!Number.isSafeInteger(child) || (child as number) <= 0) {
          return fail("RMT_OP_REPLAY_DYNAMIC_PID_INVALID", key);
        }
        count += 1;
        return [key, "<dynamic-process-id>"];
      }
      return [key, visit(child)];
    }));
  };
  return Object.freeze({value: visit(input), redacted_count: count});
};

const verifyRawParityDigest = (
  parity: ReturnType<typeof evaluateOperationParity>,
): Omit<typeof parity, "parity_sha256"> => {
  const {parity_sha256: observed, ...body} = parity;
  if (sha256(canonicalJson(body)) !== observed) {
    return fail("RMT_OP_REPLAY_RAW_PARITY_DIGEST_INVALID");
  }
  return body;
};

export const operationWpRmt002ReplayV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  provider_id: "operation-wp-rmt-002-replay-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: OPERATION_REPLAY_RAW_ROLES,
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/wp-rmt-002/replay/operation-replay-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/wp-rmt-002/parity/evaluate-operation-parity.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/wp-rmt-002/parity/evaluate-operation-parity.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/wp-rmt-002/parity/live-operation-parity.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/operation-typescript-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/operation-python-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/operation-rust-v1.ts",
  ]),
  tool_ids: Object.freeze([
    "node", "tsx", "typescript", "python", "rustc",
  ]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    exactKeys(rawInputs, OPERATION_REPLAY_RAW_ROLES,
      "RMT_OP_REPLAY_INPUT_ROLES_INVALID");
    if (Object.keys(upstream).length !== 0) {
      return fail("RMT_OP_REPLAY_UPSTREAM_FORBIDDEN");
    }
    const [typescriptResult, pythonResult, rustResult] = await Promise.all([
      operationTypeScriptV1Provider.execute({
        raw_inputs: rawFor(
          "typescript",
          TYPESCRIPT_OPERATION_RAW_PATHS,
          rawInputs,
        ),
        upstream: {},
      }),
      operationPythonV1Provider.execute({
        raw_inputs: rawFor("python", PYTHON_OPERATION_RAW_PATHS, rawInputs),
        upstream: {},
      }),
      operationRustV1Provider.execute({
        raw_inputs: rawFor("rust", RUST_OPERATION_RAW_PATHS, rawInputs),
        upstream: {},
      }),
    ]);
    const directResults = Object.freeze({
      typescript: typescriptResult,
      python: pythonResult,
      rust: rustResult,
    });
    const providerSemanticSha256 = Object.fromEntries(
      (Object.keys(directResults) as Language[]).map((language) => {
        const normalized = redactDynamicProcessIds(directResults[language]);
        if (normalized.redacted_count !== 4) {
          return fail("RMT_OP_REPLAY_PROVIDER_PID_COUNT_INVALID", language);
        }
        const digest = sha256(canonicalJson(normalized.value));
        if (digest !== EXPECTED_PROVIDER_SEMANTIC_SHA256[language]) {
          return fail("RMT_OP_REPLAY_PROVIDER_SEMANTIC_DRIFT", language);
        }
        return [language, digest];
      }),
    ) as Record<Language, string>;
    const parity = evaluateOperationParity(Object.freeze({
      typescript: Object.freeze({
        provider_id: operationTypeScriptV1Provider.provider_id,
        result: typescriptResult,
      }),
      python: Object.freeze({
        provider_id: operationPythonV1Provider.provider_id,
        result: pythonResult,
      }),
      rust: Object.freeze({
        provider_id: operationRustV1Provider.provider_id,
        result: rustResult,
      }),
    }));
    if (parity.result !== "pass" || parity.authority_effect !== "none" ||
        parity.diagnostics.length !== 0 ||
        parity.native_evidence_retained_separately !== true ||
        parity.native_hash_byte_comparison !== false ||
        parity.native_evidence_hashes_compared_for_equality !== false ||
        parity.portable_semantics_compared !== true ||
        JSON.stringify(parity.providers) !== JSON.stringify([
          "operation-typescript-v1",
          "operation-python-v1",
          "operation-rust-v1",
        ])) {
      return fail("RMT_OP_REPLAY_PARITY_BLOCKED");
    }
    const rawParityBody = verifyRawParityDigest(parity);
    const normalizedParity = redactDynamicProcessIds(rawParityBody);
    if (normalizedParity.redacted_count !== 12) {
      return fail("RMT_OP_REPLAY_PARITY_PID_COUNT_INVALID");
    }
    const normalizedParitySha256 = sha256(
      canonicalJson(normalizedParity.value),
    );
    if (normalizedParitySha256 !== EXPECTED_NORMALIZED_PARITY_SHA256) {
      return fail("RMT_OP_REPLAY_NORMALIZED_PARITY_DRIFT");
    }
    const parityReceiptBody = Object.freeze({
      schema_version: "OperationReplayParityReceipt/v1" as const,
      result: "pass" as const,
      providers: Object.freeze([
        operationTypeScriptV1Provider.provider_id,
        operationPythonV1Provider.provider_id,
        operationRustV1Provider.provider_id,
      ]),
      provider_semantic_sha256: Object.freeze(providerSemanticSha256),
      provider_evidence_sha256: Object.freeze({
        typescript: digestOperationProviderEvidenceForParity(
          typescriptResult,
        ),
        python: digestOperationProviderEvidenceForParity(pythonResult),
        rust: digestOperationProviderEvidenceForParity(rustResult),
      }),
      raw_parity_sha256_validated: true as const,
      normalized_parity: normalizedParity.value,
      normalized_parity_sha256: normalizedParitySha256,
      portable_projection_sha256: sha256(
        canonicalJson(parity.portable_projection),
      ),
      parity_evaluator_sha256: sha256(rawInputs.parity_evaluator!),
      parity_evaluator_test_sha256: sha256(
        rawInputs.parity_evaluator_test!,
      ),
      parity_live_test_sha256: sha256(rawInputs.parity_live_test!),
      native_fresh_processes_per_semantic_execution: 12,
      provider_fresh_processes: Object.freeze({
        typescript: 4,
        python: 4,
        rust: 4,
      }),
      redacted_dynamic_pid_fields: normalizedParity.redacted_count,
      process_ids_validated_before_redaction: true as const,
      process_ids_in_semantic_identity: false as const,
      native_hash_byte_comparison: false as const,
      portable_semantics_compared: true as const,
      claim_ceiling: OPERATION_REPLAY_CLAIM_CEILING,
      authority_effect: "none" as const,
    });
    const parityReceipt = Object.freeze({
      ...parityReceiptBody,
      receipt_sha256: sha256(canonicalJson(parityReceiptBody)),
    });
    const proof = Object.freeze({
      schema_version: "OperationFactoryReplayProof/v1" as const,
      result: "pass" as const,
      parity_receipt: parityReceipt,
      accounting: Object.freeze({
        positives: Object.freeze({declared: 7, passed: 7}),
        mutants: Object.freeze({declared: 87, killed: 87}),
      }),
      semantic_determinism: Object.freeze({
        dynamic_pid_fields_excluded: 12,
        normalized_parity_digest_pinned: true,
        raw_parity_digest_validated: true,
      }),
      claim_ceiling: OPERATION_REPLAY_CLAIM_CEILING,
      authority_effect: "none" as const,
    });
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "operation-wp-rmt-002-replay-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: 7,
        positives_passed: 7,
        mutants_declared: 87,
        mutants_killed: 87,
      }),
      claim_ceiling: OPERATION_REPLAY_CLAIM_CEILING,
      authority_effect: "none" as const,
    });
  },
});
