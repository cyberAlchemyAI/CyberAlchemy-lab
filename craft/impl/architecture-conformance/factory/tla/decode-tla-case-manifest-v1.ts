import type {
  TlaCaseManifestV1,
  TlaCaseV1,
  TlaExecutionPolicyV1,
} from "./contracts/tla-case-manifest-v1.js";
import type { TlcSuccessfulOutcomeClassV1 } from "./contracts/tlc-outcome-classification-v1.js";
import { canonicalJson, exactKeys, fail, isRecord, safeRelativePath } from "../shared/canonical.js";

const idPattern = /^[a-z0-9][a-z0-9._-]*$/u;
const tlaNamePattern = /^[A-Za-z][A-Za-z0-9_]*$/u;
const findingPattern = /^[A-Z][A-Z0-9_]*$/u;
const sha256Pattern = /^[a-f0-9]{64}$/u;
const drivePathPattern = /^[A-Za-z]:\//u;

const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));

const string = (value: unknown, detail: string): string =>
  typeof value === "string" && value.length > 0
    ? value
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", detail);

const safeVirtualPath = (value: string): boolean =>
  safeRelativePath(value) && !drivePathPattern.test(value) && !value.includes("\0");

const sortedUnique = (values: readonly string[]): boolean =>
  values.every((value, index) => index === 0 || compareUtf8(values[index - 1]!, value) < 0);

const identifierArray = (value: unknown, detail: string): readonly string[] => {
  if (!Array.isArray(value) || value.some((item) =>
    typeof item !== "string" || !tlaNamePattern.test(item))) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", detail);
  }
  const values = value as string[];
  if (!sortedUnique(values)) fail("FACTORY_TLA_CASE_MANIFEST_INVALID", `${detail}-order`);
  return Object.freeze([...values]);
};

const virtualPathArray = (value: unknown): readonly string[] => {
  if (!Array.isArray(value) || value.length === 0 || value.some((item) =>
    typeof item !== "string" || !safeVirtualPath(item) || !item.endsWith(".tla"))) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "module-paths");
  }
  const values = value as string[];
  if (!sortedUnique(values)) fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "module-path-order");
  return Object.freeze([...values]);
};

const positiveSafeInteger = (value: unknown, detail: string): number =>
  Number.isSafeInteger(value) && (value as number) > 0
    ? value as number
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", detail);

const decodeCase = (value: unknown, corpusId: string): TlaCaseV1 => {
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "case");
  exactKeys(record, [
    "case_id",
    "accounting_id",
    "proof_role",
    "module_paths",
    "config_path",
    "spec_name",
    "expected_class",
    "expected_exit_status",
    "expected_property",
    "required_trace_markers",
    "finding_code",
    "timeout_ms",
    "output_limit_bytes",
    "state_limit",
  ], "FACTORY_TLA_CASE_MANIFEST_INVALID");

  const caseId = string(record.case_id, "case-id");
  const accountingId = string(record.accounting_id, "accounting-id");
  if (!idPattern.test(caseId) || !idPattern.test(accountingId) ||
      !caseId.startsWith(`${corpusId}.`) || !accountingId.startsWith(`${corpusId}.`)) {
    fail("FACTORY_TLA_CASE_ID_INVALID", caseId);
  }
  const proofRole = record.proof_role === "obligation" || record.proof_role === "mutant"
    ? record.proof_role
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "proof-role");
  const configPath = string(record.config_path, "config-path");
  if (!safeVirtualPath(configPath) || !configPath.endsWith(".cfg")) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "config-path");
  }
  const specName = string(record.spec_name, "spec-name");
  if (!tlaNamePattern.test(specName)) fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "spec-name");

  const expectedClass = record.expected_class;
  if (expectedClass !== "BOUNDED_NO_COUNTEREXAMPLE" &&
      expectedClass !== "EXPECTED_NAMED_COUNTEREXAMPLE") {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "expected-class");
  }
  const expectedExitStatus = record.expected_exit_status;
  if (!Number.isSafeInteger(expectedExitStatus) || (expectedExitStatus as number) < 0 ||
      (expectedExitStatus as number) > 255 ||
      (expectedClass === "BOUNDED_NO_COUNTEREXAMPLE" && expectedExitStatus !== 0) ||
      (expectedClass === "EXPECTED_NAMED_COUNTEREXAMPLE" && expectedExitStatus === 0)) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "expected-exit-status");
  }
  const expectedProperty = record.expected_property;
  if ((expectedClass === "BOUNDED_NO_COUNTEREXAMPLE" && expectedProperty !== null) ||
      (expectedClass === "EXPECTED_NAMED_COUNTEREXAMPLE" &&
        (typeof expectedProperty !== "string" || !tlaNamePattern.test(expectedProperty)))) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "expected-property");
  }
  const requiredTraceMarkers = identifierArray(record.required_trace_markers, "trace-markers");
  if (expectedClass === "BOUNDED_NO_COUNTEREXAMPLE" && requiredTraceMarkers.length !== 0) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "trace-markers-nullability");
  }
  const findingCode = record.finding_code;
  if ((proofRole === "obligation" && findingCode !== null) ||
      (proofRole === "mutant" &&
        (typeof findingCode !== "string" || !findingPattern.test(findingCode)))) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "finding-code");
  }
  if (record.timeout_ms !== 120_000) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "timeout-ms");
  }

  return Object.freeze({
    case_id: caseId,
    accounting_id: accountingId,
    proof_role: proofRole,
    module_paths: virtualPathArray(record.module_paths),
    config_path: configPath,
    spec_name: specName,
    expected_class: expectedClass as TlcSuccessfulOutcomeClassV1,
    expected_exit_status: expectedExitStatus as number,
    expected_property: expectedProperty as string | null,
    required_trace_markers: requiredTraceMarkers,
    finding_code: findingCode as string | null,
    timeout_ms: 120_000,
    output_limit_bytes: positiveSafeInteger(record.output_limit_bytes, "output-limit-bytes"),
    state_limit: positiveSafeInteger(record.state_limit, "state-limit"),
  });
};

const decodeExecutionPolicy = (value: unknown): TlaExecutionPolicyV1 => {
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "execution-policy");
  exactKeys(record, [
    "worker_count",
    "fingerprint_index",
    "seed",
    "network_access",
    "environment",
  ], "FACTORY_TLA_CASE_MANIFEST_INVALID");
  if (record.worker_count !== 1 || record.network_access !== "forbidden" ||
      !Array.isArray(record.environment) || record.environment.length !== 0 ||
      !(record.fingerprint_index === null ||
        (Number.isSafeInteger(record.fingerprint_index) && (record.fingerprint_index as number) >= 0)) ||
      !(record.seed === null ||
        (Number.isSafeInteger(record.seed) && (record.seed as number) >= 0))) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "execution-policy");
  }
  return Object.freeze({
    worker_count: 1,
    fingerprint_index: record.fingerprint_index as number | null,
    seed: record.seed as number | null,
    network_access: "forbidden",
    environment: Object.freeze([]),
  });
};

const parseCanonical = (source: string): unknown => {
  if (typeof source !== "string" || source.length === 0) {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "source");
  }
  let value: unknown;
  try {
    value = JSON.parse(source);
  } catch {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "json");
  }
  if (canonicalJson(value) !== source) {
    fail("FACTORY_TLA_CONTRACT_NON_CANONICAL", "bytes");
  }
  return value;
};

export const decodeTlaCaseManifestV1 = (source: string): TlaCaseManifestV1 => {
  const value = parseCanonical(source);
  const record = isRecord(value)
    ? value
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "root");
  exactKeys(record, [
    "schema_version",
    "manifest_id",
    "corpus_id",
    "corpus_version",
    "model_bundle_sha256",
    "execution_policy",
    "cases",
    "claim_ceiling",
    "authority_effect",
  ], "FACTORY_TLA_CASE_MANIFEST_INVALID");
  const corpusId = string(record.corpus_id, "corpus-id");
  const caseValues = Array.isArray(record.cases)
    ? record.cases
    : fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "cases");
  if (record.schema_version !== "TlaCaseManifest/v1" || record.authority_effect !== "none" ||
      !idPattern.test(corpusId) || !idPattern.test(string(record.manifest_id, "manifest-id")) ||
      !sha256Pattern.test(string(record.model_bundle_sha256, "model-bundle-sha256")) ||
      caseValues.length === 0) {
    fail("FACTORY_TLA_CASE_MANIFEST_INVALID", "header");
  }
  const cases = caseValues.map((item: unknown) => decodeCase(item, corpusId));
  const caseIds = cases.map(({ case_id: caseId }) => caseId);
  const accountingIds = cases.map(({ accounting_id: accountingId }) => accountingId);
  if (!sortedUnique(caseIds) || new Set(accountingIds).size !== accountingIds.length) {
    fail("FACTORY_TLA_CASE_ID_INVALID", "duplicate-or-order");
  }

  return Object.freeze({
    schema_version: "TlaCaseManifest/v1",
    manifest_id: record.manifest_id as string,
    corpus_id: corpusId,
    corpus_version: string(record.corpus_version, "corpus-version"),
    model_bundle_sha256: record.model_bundle_sha256 as string,
    execution_policy: decodeExecutionPolicy(record.execution_policy),
    cases: Object.freeze(cases),
    claim_ceiling: string(record.claim_ceiling, "claim-ceiling"),
    authority_effect: "none",
  });
};
