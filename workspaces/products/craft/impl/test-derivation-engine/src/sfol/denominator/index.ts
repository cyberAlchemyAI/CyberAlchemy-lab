import { createHash } from "node:crypto";

const SHA256 = /^[a-f0-9]{64}$/;
const STABLE_ID = /^[A-Za-z][A-Za-z0-9._:-]*$/;

export const CLAUSE_KINDS = [
  "function",
  "predicate",
  "invariant",
  "precondition",
  "postcondition",
  "transition",
  "effect-relation",
] as const;

export type ClauseKind = (typeof CLAUSE_KINDS)[number];

export const EXECUTION_ROLES = [
  "return",
  "predicate",
  "state",
  "effects",
  "error",
] as const;

export type ExecutionRole = (typeof EXECUTION_ROLES)[number];

export const DENOMINATOR_ERROR_CODES = [
  "SFOL_DENOMINATOR_EMPTY",
  "SFOL_DENOMINATOR_SHAPE_INVALID",
  "SFOL_DENOMINATOR_SOURCE_NONCANONICAL",
  "SFOL_DENOMINATOR_PROFILE_UNSUPPORTED",
  "SFOL_DENOMINATOR_ID_INVALID",
  "SFOL_DENOMINATOR_DIGEST_INVALID",
  "SFOL_DENOMINATOR_KIND_UNKNOWN",
  "SFOL_DENOMINATOR_ROLE_INVALID",
  "SFOL_DENOMINATOR_STATUS_NOT_ADMITTED",
  "SFOL_DENOMINATOR_CONTEXT_INCOMPATIBLE",
  "SFOL_DENOMINATOR_CLAUSE_DUPLICATE",
  "SFOL_DENOMINATOR_MEMBERSHIP_MISMATCH",
  "SFOL_DENOMINATOR_COVERAGE_KEY_DUPLICATE",
] as const;

export type DenominatorErrorCode = (typeof DENOMINATOR_ERROR_CODES)[number];

export class ClauseDenominatorError extends Error {
  readonly code: DenominatorErrorCode;
  readonly subject: string;

  constructor(code: DenominatorErrorCode, subject: string, detail: string) {
    super(`${code}:${subject}:${detail}`);
    this.name = "ClauseDenominatorError";
    this.code = code;
    this.subject = subject;
  }
}

export type ProofContextHandle = Readonly<{
  graph_id: string;
  graph_digest: string;
  manifest_id: string;
  manifest_digest: string;
  build_id: string;
  build_digest: string;
  source_set_digest: string;
  profile_id: string;
  profile_version: string;
  profile_digest: string;
}>;

export type ClauseAdmission = Readonly<{
  clause_id: string;
  clause_digest: string;
  node_id: string;
  node_digest: string;
  module_id: string;
  module_digest: string;
  kind: ClauseKind;
  required_roles: readonly ExecutionRole[];
  status: "admitted";
  proof_context: Readonly<{
    graph_digest: string;
    manifest_digest: string;
    build_digest: string;
    source_set_digest: string;
    profile_id: string;
    profile_version: string;
    profile_digest: string;
  }>;
}>;

export type ClauseAdmissionManifest = Readonly<{
  schema_version: "domainspec-sfol-clause-admission-manifest/v1";
  source_form: "canonical-node-graph-manifest-build";
  unsupported_residue_policy: "reject";
  proof_context: ProofContextHandle;
  clause_membership: readonly string[];
  clauses: readonly ClauseAdmission[];
}>;

export type ClauseDenominatorMember = Readonly<{
  coverage_key: string;
  role: ExecutionRole;
  clause_id: string;
  clause_digest: string;
  node_id: string;
  node_digest: string;
  module_id: string;
  module_digest: string;
  kind: ClauseKind;
  graph_digest: string;
  manifest_digest: string;
  build_digest: string;
  source_set_digest: string;
  profile_id: string;
  profile_version: string;
  profile_digest: string;
}>;

export type ClauseDenominator = Readonly<{
  schema_version: "domainspec-sfol-clause-denominator/v1";
  source_form: "canonical-node-graph-manifest-build";
  unsupported_residue_policy: "reject";
  proof_context: ProofContextHandle;
  clause_ids: readonly string[];
  coverage_keys: readonly string[];
  members: readonly ClauseDenominatorMember[];
  digest: string;
}>;

type JsonRecord = Record<string, unknown>;

const PROOF_CONTEXT_KEYS = [
  "graph_id",
  "graph_digest",
  "manifest_id",
  "manifest_digest",
  "build_id",
  "build_digest",
  "source_set_digest",
  "profile_id",
  "profile_version",
  "profile_digest",
] as const;

const CLAUSE_CONTEXT_KEYS = [
  "graph_digest",
  "manifest_digest",
  "build_digest",
  "source_set_digest",
  "profile_id",
  "profile_version",
  "profile_digest",
] as const;

const CLAUSE_KEYS = [
  "clause_id",
  "clause_digest",
  "node_id",
  "node_digest",
  "module_id",
  "module_digest",
  "kind",
  "required_roles",
  "status",
  "proof_context",
] as const;

const MANIFEST_KEYS = [
  "schema_version",
  "source_form",
  "unsupported_residue_policy",
  "proof_context",
  "clause_membership",
  "clauses",
] as const;

const NONCANONICAL_SOURCE_KEYS = new Set([
  "generated_cases",
  "generator_records",
  "test_cases",
  "receipts",
  "markdown",
  "formal",
  "formula",
  "node_file",
  "node_path",
  "nodes",
]);

function fail(
  code: DenominatorErrorCode,
  subject: string,
  detail: string,
): never {
  throw new ClauseDenominatorError(code, subject, detail);
}

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function assertExactKeys(
  value: JsonRecord,
  expected: readonly string[],
  subject: string,
): void {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (
    actual.length !== wanted.length ||
    actual.some((key, index) => key !== wanted[index])
  ) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      subject,
      `expected keys ${wanted.join(",")}; received ${actual.join(",")}`,
    );
  }
}

function requireString(
  value: unknown,
  subject: string,
  field: string,
): string {
  if (typeof value !== "string" || value.length === 0) {
    fail("SFOL_DENOMINATOR_SHAPE_INVALID", subject, `${field} must be a string`);
  }
  return value;
}

function requireId(value: unknown, subject: string, field: string): string {
  const id = requireString(value, subject, field);
  if (!STABLE_ID.test(id)) {
    fail("SFOL_DENOMINATOR_ID_INVALID", subject, `${field} is not a stable ID`);
  }
  return id;
}

function requireDigest(value: unknown, subject: string, field: string): string {
  const digest = requireString(value, subject, field);
  if (!SHA256.test(digest)) {
    fail(
      "SFOL_DENOMINATOR_DIGEST_INVALID",
      subject,
      `${field} is not a lowercase SHA-256 digest`,
    );
  }
  return digest;
}

function parseProofContext(value: unknown): ProofContextHandle {
  if (!isRecord(value)) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      "proof_context",
      "proof context must be an object",
    );
  }
  assertExactKeys(value, PROOF_CONTEXT_KEYS, "proof_context");
  return {
    graph_id: requireId(value.graph_id, "proof_context", "graph_id"),
    graph_digest: requireDigest(
      value.graph_digest,
      "proof_context",
      "graph_digest",
    ),
    manifest_id: requireId(value.manifest_id, "proof_context", "manifest_id"),
    manifest_digest: requireDigest(
      value.manifest_digest,
      "proof_context",
      "manifest_digest",
    ),
    build_id: requireId(value.build_id, "proof_context", "build_id"),
    build_digest: requireDigest(
      value.build_digest,
      "proof_context",
      "build_digest",
    ),
    source_set_digest: requireDigest(
      value.source_set_digest,
      "proof_context",
      "source_set_digest",
    ),
    profile_id: requireId(value.profile_id, "proof_context", "profile_id"),
    profile_version: requireString(
      value.profile_version,
      "proof_context",
      "profile_version",
    ),
    profile_digest: requireDigest(
      value.profile_digest,
      "proof_context",
      "profile_digest",
    ),
  };
}

function parseClause(
  value: unknown,
  proofContext: ProofContextHandle,
  index: number,
): ClauseAdmission {
  const subject = `clauses[${index}]`;
  if (!isRecord(value)) {
    fail("SFOL_DENOMINATOR_SHAPE_INVALID", subject, "clause must be an object");
  }
  assertExactKeys(value, CLAUSE_KEYS, subject);

  const clauseId = requireId(value.clause_id, subject, "clause_id");
  const kind = requireString(value.kind, clauseId, "kind");
  if (!(CLAUSE_KINDS as readonly string[]).includes(kind)) {
    fail("SFOL_DENOMINATOR_KIND_UNKNOWN", clauseId, `unknown kind ${kind}`);
  }
  if (value.status !== "admitted") {
    fail(
      "SFOL_DENOMINATOR_STATUS_NOT_ADMITTED",
      clauseId,
      "only admitted clauses enter the exact denominator",
    );
  }
  if (!Array.isArray(value.required_roles) || value.required_roles.length === 0) {
    fail(
      "SFOL_DENOMINATOR_ROLE_INVALID",
      clauseId,
      "required_roles must be a nonempty array",
    );
  }
  const roles = value.required_roles.map((role, roleIndex) => {
    if (
      typeof role !== "string" ||
      !(EXECUTION_ROLES as readonly string[]).includes(role)
    ) {
      fail(
        "SFOL_DENOMINATOR_ROLE_INVALID",
        clauseId,
        `required_roles[${roleIndex}] is unknown`,
      );
    }
    return role as ExecutionRole;
  });
  if (new Set(roles).size !== roles.length) {
    fail(
      "SFOL_DENOMINATOR_COVERAGE_KEY_DUPLICATE",
      clauseId,
      "required_roles contains a duplicate",
    );
  }

  if (!isRecord(value.proof_context)) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      clauseId,
      "proof_context must be an object",
    );
  }
  assertExactKeys(value.proof_context, CLAUSE_CONTEXT_KEYS, clauseId);
  for (const key of CLAUSE_CONTEXT_KEYS) {
    const actual = requireString(value.proof_context[key], clauseId, key);
    if (actual !== proofContext[key]) {
      fail(
        "SFOL_DENOMINATOR_CONTEXT_INCOMPATIBLE",
        clauseId,
        `${key} does not match the canonical proof context`,
      );
    }
  }

  return {
    clause_id: clauseId,
    clause_digest: requireDigest(value.clause_digest, clauseId, "clause_digest"),
    node_id: requireId(value.node_id, clauseId, "node_id"),
    node_digest: requireDigest(value.node_digest, clauseId, "node_digest"),
    module_id: requireId(value.module_id, clauseId, "module_id"),
    module_digest: requireDigest(value.module_digest, clauseId, "module_digest"),
    kind: kind as ClauseKind,
    required_roles: roles,
    status: "admitted",
    proof_context: {
      graph_digest: proofContext.graph_digest,
      manifest_digest: proofContext.manifest_digest,
      build_digest: proofContext.build_digest,
      source_set_digest: proofContext.source_set_digest,
      profile_id: proofContext.profile_id,
      profile_version: proofContext.profile_version,
      profile_digest: proofContext.profile_digest,
    },
  };
}

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(",")}]`;
  }
  if (isRecord(value)) {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function sha256(value: unknown): string {
  return createHash("sha256").update(canonicalJson(value)).digest("hex");
}

function deepFreeze<T>(value: T): T {
  if (typeof value === "object" && value !== null && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) {
      deepFreeze(child);
    }
  }
  return value;
}

export function buildClauseDenominator(input: unknown): ClauseDenominator {
  if (!isRecord(input)) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      "manifest",
      "manifest must be an object",
    );
  }
  const noncanonicalKey = Object.keys(input).find((key) =>
    NONCANONICAL_SOURCE_KEYS.has(key),
  );
  if (noncanonicalKey !== undefined) {
    fail(
      "SFOL_DENOMINATOR_SOURCE_NONCANONICAL",
      "manifest",
      `noncanonical source field ${noncanonicalKey}`,
    );
  }
  if (input.source_form !== "canonical-node-graph-manifest-build") {
    fail(
      "SFOL_DENOMINATOR_SOURCE_NONCANONICAL",
      "manifest",
      "source_form must name the canonical graph/manifest/build boundary",
    );
  }
  assertExactKeys(input, MANIFEST_KEYS, "manifest");
  if (input.schema_version !== "domainspec-sfol-clause-admission-manifest/v1") {
    fail(
      "SFOL_DENOMINATOR_PROFILE_UNSUPPORTED",
      "manifest",
      "unsupported admission manifest schema",
    );
  }
  if (input.unsupported_residue_policy !== "reject") {
    fail(
      "SFOL_DENOMINATOR_PROFILE_UNSUPPORTED",
      "manifest",
      "admitted completeness requires reject residue policy",
    );
  }

  const proofContext = parseProofContext(input.proof_context);
  if (!Array.isArray(input.clause_membership)) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      "clause_membership",
      "membership must be an array",
    );
  }
  if (!Array.isArray(input.clauses)) {
    fail(
      "SFOL_DENOMINATOR_SHAPE_INVALID",
      "clauses",
      "clauses must be an array",
    );
  }
  if (input.clauses.length === 0 || input.clause_membership.length === 0) {
    fail(
      "SFOL_DENOMINATOR_EMPTY",
      "manifest",
      "at least one admitted clause is required",
    );
  }

  const membership = input.clause_membership.map((value, index) =>
    requireId(value, `clause_membership[${index}]`, "clause_id"),
  );
  if (new Set(membership).size !== membership.length) {
    fail(
      "SFOL_DENOMINATOR_CLAUSE_DUPLICATE",
      "clause_membership",
      "membership contains a duplicate clause ID",
    );
  }

  const clauses = input.clauses.map((value, index) =>
    parseClause(value, proofContext, index),
  );
  const clauseIds = clauses.map(({ clause_id }) => clause_id);
  if (new Set(clauseIds).size !== clauseIds.length) {
    fail(
      "SFOL_DENOMINATOR_CLAUSE_DUPLICATE",
      "clauses",
      "clauses contain a duplicate clause ID",
    );
  }
  const expected = [...membership].sort();
  const actual = [...clauseIds].sort();
  if (
    expected.length !== actual.length ||
    expected.some((id, index) => id !== actual[index])
  ) {
    fail(
      "SFOL_DENOMINATOR_MEMBERSHIP_MISMATCH",
      "manifest",
      `membership ${expected.join(",")} does not equal clauses ${actual.join(",")}`,
    );
  }

  const members = clauses
    .flatMap((clause) =>
      clause.required_roles.map(
        (role): ClauseDenominatorMember => ({
          coverage_key: `${clause.clause_id}#${role}`,
          role,
          clause_id: clause.clause_id,
          clause_digest: clause.clause_digest,
          node_id: clause.node_id,
          node_digest: clause.node_digest,
          module_id: clause.module_id,
          module_digest: clause.module_digest,
          kind: clause.kind,
          graph_digest: proofContext.graph_digest,
          manifest_digest: proofContext.manifest_digest,
          build_digest: proofContext.build_digest,
          source_set_digest: proofContext.source_set_digest,
          profile_id: proofContext.profile_id,
          profile_version: proofContext.profile_version,
          profile_digest: proofContext.profile_digest,
        }),
      ),
    )
    .sort((left, right) => left.coverage_key.localeCompare(right.coverage_key));
  const coverageKeys = members.map(({ coverage_key }) => coverage_key);
  if (new Set(coverageKeys).size !== coverageKeys.length) {
    fail(
      "SFOL_DENOMINATOR_COVERAGE_KEY_DUPLICATE",
      "manifest",
      "derived coverage keys are not unique",
    );
  }

  const unsigned = {
    schema_version: "domainspec-sfol-clause-denominator/v1" as const,
    source_form: "canonical-node-graph-manifest-build" as const,
    unsupported_residue_policy: "reject" as const,
    proof_context: proofContext,
    clause_ids: actual,
    coverage_keys: coverageKeys,
    members,
  };
  return deepFreeze({ ...unsigned, digest: sha256(unsigned) });
}
