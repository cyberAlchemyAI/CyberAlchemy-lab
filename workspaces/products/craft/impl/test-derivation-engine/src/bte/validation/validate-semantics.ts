import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  readFileSync,
  realpathSync,
  statSync,
} from "node:fs";
import { dirname, isAbsolute, relative, resolve, win32 } from "node:path";
import { fileURLToPath } from "node:url";

import {
  CONTRACT_FILES,
  canonicalize,
  validateContractInstance,
} from "../contract-publication.js";
import { BTE_DIAGNOSTICS } from "./diagnostics.js";

type JsonObject = Record<string, unknown>;
type ContractRegistry = Map<string, JsonObject>;

export type BteDiagnosticCode = (typeof BTE_DIAGNOSTICS)[number]["code"];

export type BteDiagnostic = {
  schema_version: "bte-diagnostic/v1";
  code: BteDiagnosticCode;
  precedence: number;
  stage: (typeof BTE_DIAGNOSTICS)[number]["stage"];
  subject: string;
  detail: string;
};

export type BteValidationResult = {
  result: "pass" | "fail";
  diagnostics: BteDiagnostic[];
};

export type LogicalIdentity = {
  schema_version: "bte-logical-identity/v1";
  domain: string;
  namespace: string;
  kind: string;
  key: string;
  version: number;
};

export type AuthorityClass = {
  schema_version: "bte-authority-class/v1";
  class: "semantic" | "admission" | "evidence" | "aggregate" | "lifecycle";
  owner: LogicalIdentity;
  owner_digest: string;
};

export type ArtifactHandle = {
  schema_version: "bte-artifact-handle/v1";
  root_id: string;
  path: string;
  schema_id: string;
  logical_identity: LogicalIdentity;
  sha256: string;
  bytes: number;
  producer: {
    id: string;
    version: string;
    digest: string;
  };
  authority: AuthorityClass;
};

export type ExactSetMember = {
  logical_identity: LogicalIdentity;
  content_sha256: string;
};

export type ExactSet = {
  schema_version: "bte-exact-set/v1";
  set_id: LogicalIdentity;
  membership_digest: string;
  members: ExactSetMember[];
};

export type RedFixtureCase = {
  case_id: string;
  subject_contract_id: string;
  fixture: ArtifactHandle;
  expected_diagnostic: BteDiagnostic;
};

export type RedFixtureManifest = {
  schema_version: "bte-red-fixture-manifest/v1";
  manifest_id: LogicalIdentity;
  contract_publication_sha256: string;
  validation_owner: AuthorityClass;
  cases: RedFixtureCase[];
};

export type RedFixtureFreezeReceipt = {
  schema_version: "bte-red-fixture-freeze-receipt/v1";
  receipt_id: LogicalIdentity;
  manifest_handle: ArtifactHandle;
  contract_publication_receipt_handle: ArtifactHandle;
  validation_owner: AuthorityClass;
  frozen_cases: ExactSet;
  admission: "not-granted";
};

export type ArtifactRoots = Readonly<Record<string, string>>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const contractsDir = resolve(thisDir, "../contracts");
const diagnosticByCode = new Map(BTE_DIAGNOSTICS.map((entry) => [entry.code, entry]));
const shaPattern = /^[a-f0-9]{64}$/;

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

export function logicalIdentityKey(identity: LogicalIdentity): string {
  return [
    identity.domain,
    identity.namespace,
    identity.kind,
    identity.key,
    String(identity.version),
  ].join("/");
}

export function diagnostic(
  code: BteDiagnosticCode,
  subject: string,
  detail: string,
): BteDiagnostic {
  const registered = diagnosticByCode.get(code);
  if (!registered) {
    throw new Error(`unknown BTE diagnostic code: ${code}`);
  }
  return {
    schema_version: "bte-diagnostic/v1",
    code,
    precedence: registered.precedence,
    stage: registered.stage,
    subject,
    detail,
  };
}

function normalizeDiagnostics(diagnostics: BteDiagnostic[]): BteDiagnostic[] {
  return [...diagnostics].sort(
    (left, right) =>
      left.precedence - right.precedence ||
      left.subject.localeCompare(right.subject) ||
      left.detail.localeCompare(right.detail),
  );
}

function result(diagnostics: BteDiagnostic[]): BteValidationResult {
  const normalized = normalizeDiagnostics(diagnostics);
  return {
    result: normalized.length === 0 ? "pass" : "fail",
    diagnostics: normalized,
  };
}

function loadContractRegistry(): ContractRegistry {
  const registry: ContractRegistry = new Map();
  for (const file of CONTRACT_FILES) {
    const schema = JSON.parse(readFileSync(resolve(contractsDir, file), "utf8")) as JsonObject;
    if (typeof schema.$id !== "string") {
      throw new Error(`published BTE contract has no $id: ${file}`);
    }
    registry.set(schema.$id, schema);
  }
  return registry;
}

const contractRegistry = loadContractRegistry();

function validateShape(
  schemaId: string,
  value: unknown,
  subject: string,
): BteDiagnostic[] {
  const schema = contractRegistry.get(schemaId);
  if (!schema) {
    return [diagnostic("BTE_SCHEMA_INVALID", subject, `unknown schema ${schemaId}`)];
  }
  try {
    validateContractInstance(schema, value, contractRegistry);
    return [];
  } catch (error) {
    return [
      diagnostic(
        "BTE_SCHEMA_INVALID",
        subject,
        error instanceof Error ? error.message : String(error),
      ),
    ];
  }
}

function identityDiagnostics(
  identities: LogicalIdentity[],
  subject: string,
): BteDiagnostic[] {
  const diagnostics: BteDiagnostic[] = [];
  const seen = new Set<string>();
  for (const identity of identities) {
    const key = logicalIdentityKey(identity);
    if (seen.has(key)) {
      diagnostics.push(
        diagnostic("BTE_LOGICAL_ID_DUPLICATE", subject, `duplicate identity ${key}`),
      );
    }
    seen.add(key);
  }
  return diagnostics;
}

function resolveContainedPath(
  handle: ArtifactHandle,
  roots: ArtifactRoots,
): { path?: string; diagnostics: BteDiagnostic[] } {
  const diagnostics: BteDiagnostic[] = [];
  const subject = logicalIdentityKey(handle.logical_identity);
  const portable = handle.path.replaceAll("\\", "/");
  if (isAbsolute(handle.path) || win32.isAbsolute(handle.path) || portable.startsWith("//")) {
    diagnostics.push(
      diagnostic("BTE_PATH_ABSOLUTE", subject, `absolute path is forbidden: ${handle.path}`),
    );
    return { diagnostics };
  }
  if (
    portable.length === 0 ||
    portable.split("/").some((segment) => segment === "..")
  ) {
    diagnostics.push(
      diagnostic("BTE_PATH_TRAVERSAL", subject, `path traversal is forbidden: ${handle.path}`),
    );
    return { diagnostics };
  }
  const root = roots[handle.root_id];
  if (!root) {
    diagnostics.push(
      diagnostic("BTE_ROOT_UNDECLARED", subject, `undeclared root ${handle.root_id}`),
    );
    return { diagnostics };
  }
  const rootReal = realpathSync(root);
  const candidate = resolve(rootReal, ...portable.split("/"));
  const delta = relative(rootReal, candidate);
  if (delta.startsWith("..") || isAbsolute(delta)) {
    diagnostics.push(
      diagnostic("BTE_PATH_TRAVERSAL", subject, `resolved path escapes ${handle.root_id}`),
    );
    return { diagnostics };
  }
  if (!existsSync(candidate)) {
    diagnostics.push(
      diagnostic("BTE_DIGEST_MISMATCH", subject, `artifact does not exist: ${handle.path}`),
    );
    return { diagnostics };
  }
  const candidateReal = realpathSync(candidate);
  const realDelta = relative(rootReal, candidateReal);
  if (realDelta.startsWith("..") || isAbsolute(realDelta) || lstatSync(candidate).isSymbolicLink()) {
    diagnostics.push(
      diagnostic("BTE_PATH_SYMLINK_ESCAPE", subject, `symlink escapes or aliases the root`),
    );
    return { diagnostics };
  }
  if (!statSync(candidateReal).isFile()) {
    diagnostics.push(
      diagnostic("BTE_DIGEST_MISMATCH", subject, `artifact is not a regular file`),
    );
    return { diagnostics };
  }
  return { path: candidateReal, diagnostics };
}

export function validateArtifactHandle(
  handle: unknown,
  roots: ArtifactRoots,
  options: {
    expectedProducer?: string;
    expectedAuthority?: AuthorityClass["class"];
  } = {},
): BteValidationResult {
  if (isObject(handle) && typeof handle.path === "string") {
    const portable = handle.path.replaceAll("\\", "/");
    if (isAbsolute(handle.path) || win32.isAbsolute(handle.path) || portable.startsWith("//")) {
      return result([
        diagnostic("BTE_PATH_ABSOLUTE", "artifact-handle", `absolute path is forbidden: ${handle.path}`),
      ]);
    }
    if (portable.split("/").some((segment) => segment === "..")) {
      return result([
        diagnostic("BTE_PATH_TRAVERSAL", "artifact-handle", `path traversal is forbidden: ${handle.path}`),
      ]);
    }
  }
  const shape = validateShape(
    "urn:domainspec-v2:bte:artifact-handle:v1",
    handle,
    "artifact-handle",
  );
  if (shape.length > 0 || !isObject(handle)) {
    return result(shape);
  }
  const typed = handle as ArtifactHandle;
  const diagnostics: BteDiagnostic[] = [];
  if (!shaPattern.test(typed.sha256) || !shaPattern.test(typed.producer.digest)) {
    diagnostics.push(
      diagnostic("BTE_DIGEST_MALFORMED", logicalIdentityKey(typed.logical_identity), "malformed SHA-256"),
    );
  }
  if (options.expectedProducer && typed.producer.id !== options.expectedProducer) {
    diagnostics.push(
      diagnostic(
        "BTE_PRODUCER_MISMATCH",
        logicalIdentityKey(typed.logical_identity),
        `expected producer ${options.expectedProducer}; got ${typed.producer.id}`,
      ),
    );
  }
  if (options.expectedAuthority && typed.authority.class !== options.expectedAuthority) {
    diagnostics.push(
      diagnostic(
        "BTE_AUTHORITY_SUBSTITUTED",
        logicalIdentityKey(typed.logical_identity),
        `expected ${options.expectedAuthority}; got ${typed.authority.class}`,
      ),
    );
  }
  const resolved = resolveContainedPath(typed, roots);
  diagnostics.push(...resolved.diagnostics);
  if (resolved.path) {
    const bytes = readFileSync(resolved.path);
    if (typed.bytes !== bytes.byteLength || typed.sha256 !== sha256(bytes)) {
      diagnostics.push(
        diagnostic(
          "BTE_DIGEST_MISMATCH",
          logicalIdentityKey(typed.logical_identity),
          `declared bytes or digest do not match ${typed.path}`,
        ),
      );
    }
  }
  return result(diagnostics);
}

function sortedMembers(members: ExactSetMember[]): ExactSetMember[] {
  return [...members].sort((left, right) =>
    logicalIdentityKey(left.logical_identity).localeCompare(
      logicalIdentityKey(right.logical_identity),
    ),
  );
}

export function exactSetDigest(members: ExactSetMember[]): string {
  return sha256(canonicalize(sortedMembers(members)));
}

export function createExactSet(
  setId: LogicalIdentity,
  members: ExactSetMember[],
): ExactSet {
  return {
    schema_version: "bte-exact-set/v1",
    set_id: setId,
    membership_digest: exactSetDigest(members),
    members: sortedMembers(members),
  };
}

export function validateExactSet(set: unknown): BteValidationResult {
  const shape = validateShape("urn:domainspec-v2:bte:exact-set:v1", set, "exact-set");
  if (shape.length > 0 || !isObject(set)) {
    return result(shape);
  }
  const typed = set as ExactSet;
  const diagnostics = identityDiagnostics(
    typed.members.map(({ logical_identity }) => logical_identity),
    logicalIdentityKey(typed.set_id),
  );
  if (typed.members.length === 0) {
    diagnostics.push(
      diagnostic("BTE_EXACT_SET_EMPTY", logicalIdentityKey(typed.set_id), "set is empty"),
    );
  }
  if (new Set(typed.members.map(({ content_sha256 }) => content_sha256)).size !== typed.members.length) {
    diagnostics.push(
      diagnostic(
        "BTE_EXACT_SET_DUPLICATE",
        logicalIdentityKey(typed.set_id),
        "content digest appears more than once",
      ),
    );
  }
  if (typed.members.some(({ content_sha256 }) => !shaPattern.test(content_sha256))) {
    diagnostics.push(
      diagnostic("BTE_DIGEST_MALFORMED", logicalIdentityKey(typed.set_id), "member digest malformed"),
    );
  } else if (typed.membership_digest !== exactSetDigest(typed.members)) {
    diagnostics.push(
      diagnostic(
        "BTE_DIGEST_MISMATCH",
        logicalIdentityKey(typed.set_id),
        "membership digest does not recompute",
      ),
    );
  }
  return result(diagnostics);
}

export function compareExactSets(
  expected: ExactSet,
  actual: ExactSet,
): BteValidationResult {
  const diagnostics: BteDiagnostic[] = [
    ...validateExactSet(expected).diagnostics,
    ...validateExactSet(actual).diagnostics,
  ];
  const expectedMembers = new Set(
    expected.members.map(({ logical_identity }) => logicalIdentityKey(logical_identity)),
  );
  const actualMembers = new Set(
    actual.members.map(({ logical_identity }) => logicalIdentityKey(logical_identity)),
  );
  for (const member of expectedMembers) {
    if (!actualMembers.has(member)) {
      diagnostics.push(
        diagnostic("BTE_RECOMPOSITION_MISSING", member, "expected member is absent"),
      );
    }
  }
  for (const member of actualMembers) {
    if (!expectedMembers.has(member)) {
      diagnostics.push(
        diagnostic("BTE_RECOMPOSITION_EXTRA", member, "unexpected member is present"),
      );
    }
  }
  return result(diagnostics);
}

function caseMembers(cases: RedFixtureCase[]): ExactSetMember[] {
  return cases.map((entry) => ({
    logical_identity: {
      schema_version: "bte-logical-identity/v1",
      domain: "domainspec-v2",
      namespace: "bte.red-fixtures",
      kind: "red-case",
      key: entry.case_id,
      version: 1,
    },
    content_sha256: sha256(canonicalize(entry)),
  }));
}

export function validateRedFixtureBundle(input: {
  manifest: unknown;
  freeze: unknown;
  roots: ArtifactRoots;
  publicationReceiptSha256: string;
  implementationProducerIds?: readonly string[];
}): BteValidationResult {
  const manifestShape = validateShape(
    "urn:domainspec-v2:bte:red-fixture-manifest:v1",
    input.manifest,
    "red-fixture-manifest",
  );
  const freezeShape = validateShape(
    "urn:domainspec-v2:bte:red-fixture-freeze-receipt:v1",
    input.freeze,
    "red-fixture-freeze",
  );
  if (
    manifestShape.length > 0 ||
    freezeShape.length > 0 ||
    !isObject(input.manifest) ||
    !isObject(input.freeze)
  ) {
    return result([...manifestShape, ...freezeShape]);
  }
  const manifest = input.manifest as RedFixtureManifest;
  const freeze = input.freeze as RedFixtureFreezeReceipt;
  const diagnostics: BteDiagnostic[] = [];
  const subject = logicalIdentityKey(manifest.manifest_id);
  if (manifest.contract_publication_sha256 !== input.publicationReceiptSha256) {
    diagnostics.push(
      diagnostic("BTE_CONTRACT_STALE", subject, "manifest targets a different publication receipt"),
    );
  }
  if (
    manifest.validation_owner.class !== "evidence" ||
    freeze.validation_owner.class !== "evidence" ||
    canonicalize(manifest.validation_owner) !== canonicalize(freeze.validation_owner)
  ) {
    diagnostics.push(
      diagnostic("BTE_AUTHORITY_SUBSTITUTED", subject, "validation owner is missing or inconsistent"),
    );
  }
  const ownerKey = manifest.validation_owner.owner.key;
  if (input.implementationProducerIds?.includes(ownerKey)) {
    diagnostics.push(
      diagnostic(
        "BTE_EXPECTATION_SELF_AUTHORED",
        subject,
        `implementation producer ${ownerKey} authored the expected outcomes`,
      ),
    );
  }
  diagnostics.push(
    ...identityDiagnostics(
      manifest.cases.map((entry) => ({
        schema_version: "bte-logical-identity/v1",
        domain: "domainspec-v2",
        namespace: "bte.red-fixtures",
        kind: "red-case",
        key: entry.case_id,
        version: 1,
      })),
      subject,
    ),
  );
  for (const entry of manifest.cases) {
    if (!diagnosticByCode.has(entry.expected_diagnostic.code)) {
      diagnostics.push(
        diagnostic("BTE_DIAGNOSTIC_UNKNOWN", entry.case_id, "expected diagnostic is not registered"),
      );
    } else {
      const registered = diagnosticByCode.get(entry.expected_diagnostic.code)!;
      if (
        entry.expected_diagnostic.precedence !== registered.precedence ||
        entry.expected_diagnostic.stage !== registered.stage
      ) {
        diagnostics.push(
          diagnostic(
            "BTE_DIAGNOSTIC_PRECEDENCE",
            entry.case_id,
            "expected diagnostic precedence or stage differs from the registry",
          ),
        );
      }
    }
    diagnostics.push(
      ...validateArtifactHandle(entry.fixture, input.roots, {
        expectedAuthority: "evidence",
      }).diagnostics,
    );
  }
  const expectedCases = createExactSet(freeze.frozen_cases.set_id, caseMembers(manifest.cases));
  diagnostics.push(...compareExactSets(expectedCases, freeze.frozen_cases).diagnostics);
  diagnostics.push(
    ...validateArtifactHandle(freeze.manifest_handle, input.roots, {
      expectedAuthority: "evidence",
    }).diagnostics,
  );
  diagnostics.push(
    ...validateArtifactHandle(freeze.contract_publication_receipt_handle, input.roots, {
      expectedAuthority: "evidence",
    }).diagnostics,
  );
  if (freeze.manifest_handle.sha256 !== sha256(`${canonicalize(manifest)}\n`)) {
    diagnostics.push(
      diagnostic("BTE_EXPECTATION_REWRITTEN", subject, "manifest bytes differ from frozen handle"),
    );
  }
  if (freeze.contract_publication_receipt_handle.sha256 !== input.publicationReceiptSha256) {
    diagnostics.push(
      diagnostic("BTE_CONTRACT_STALE", subject, "freeze targets a stale publication receipt"),
    );
  }
  return result(diagnostics);
}
