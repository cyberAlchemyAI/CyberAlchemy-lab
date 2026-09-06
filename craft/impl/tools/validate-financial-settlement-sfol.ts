#!/usr/bin/env tsx

import { createHash } from "node:crypto";
import {
  readdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson } from "../test-derivation-engine/src/sfol/language/contracts";

type JsonObject = Record<string, any>;

const here = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(here, "..");
const repositoryRoot = resolve(implRoot, "../../..");
const featureRoot = resolve(
  implRoot,
  "spec/features/financial-settlement",
);
const adoptionRoot = resolve(featureRoot, "sfol/adoption");
const reportPath = resolve(
  option("--report") ??
    resolve(adoptionRoot, "adoption-report.json"),
);
const errors: string[] = [];

function main(): void {
  const report = readJson(reportPath);
  const schemaPath = resolveFromRepository(report.schema?.path);
  const proposalPath = resolveFromRepository(
    report.source_proposal?.path,
  );
  const projection = readJson(
    resolve(featureRoot, "generated/sfol-projection-receipt.json"),
  );
  const proposal = readJson(proposalPath);
  const fixtureManifest = readJson(
    resolve(featureRoot, "sfol/fixtures/manifest.json"),
  );

  exactKeys(
    report,
    [
      "schema_version",
      "status",
      "authority",
      "authority_effect",
      "formal_owner_approval",
      "release_admission",
      "project_id",
      "schema",
      "tool",
      "source_proposal",
      "proof_context",
      "modules",
      "stage_sets",
      "case_count",
      "fixture_ids",
      "admitted_clause_ids",
      "admitted_residue",
      "non_admitted_residue",
      "mutations",
      "core_path_audit",
      "bte",
      "claims",
      "report_digest",
    ],
    "report",
  );
  requireEqual(
    report.schema_version,
    "domainspec-sfol-adoption-report/v1",
    "schema version",
  );
  requireEqual(report.status, "pass", "report status");
  requireEqual(
    report.authority,
    "experimental-test-lane-evidence",
    "authority",
  );
  requireEqual(report.authority_effect, "none", "authority effect");
  requireEqual(
    report.formal_owner_approval,
    false,
    "formal owner approval",
  );
  requireEqual(
    report.release_admission,
    "not-granted",
    "release admission",
  );
  requireEqual(report.project_id, "financial-settlement", "project");

  verifyFileHandle(report.schema, schemaPath, "schema");
  verifyFileHandle(
    report.source_proposal,
    proposalPath,
    "source proposal",
  );
  for (const name of ["runner", "validator", "consumer_adapter"]) {
    const handle = report.tool?.[name];
    verifyFileHandle(
      handle,
      resolveFromRepository(handle?.path),
      `tool.${name}`,
    );
  }
  requireDigest(report.tool?.proof_tool_digest, "proof tool digest");

  const { report_digest: _digest, ...unsignedReport } = report;
  requireEqual(
    report.report_digest,
    digest(unsignedReport),
    "report digest",
  );

  const proofContext = report.proof_context;
  for (const [field, expected] of [
    ["graph_digest", projection.proof_context?.graph_digest],
    ["manifest_digest", projection.proof_context?.manifest_digest],
    [
      "build_digest",
      projection.proof_context?.build_receipt_digest,
    ],
    [
      "source_set_digest",
      projection.proof_context?.source_set_digest,
    ],
    ["profile_digest", projection.proof_context?.profile_digest],
  ] as const) {
    requireEqual(
      proofContext?.[field],
      expected,
      `proof_context.${field}`,
    );
  }

  const modules = requireArray(report.modules, "modules");
  requireExactSet(
    modules.map((entry) => entry.clause_id),
    ["C3", "P4"],
    "module clauses",
  );
  const projectionModules = new Map(
    requireArray(projection.modules, "projection.modules").map(
      (entry) => [entry.clause_id, entry],
    ),
  );
  for (const module of modules) {
    const projected = projectionModules.get(module.clause_id);
    if (projected === undefined) {
      errors.push(`module ${String(module.clause_id)} is not projected`);
      continue;
    }
    requireEqual(
      module.module_id,
      projected.module_id,
      `${module.clause_id}.module_id`,
    );
    requireEqual(
      module.module_digest,
      projected.module_digest,
      `${module.clause_id}.module_digest`,
    );
    requireDigest(
      module.typed_artifact_digest,
      `${module.clause_id}.typed_artifact_digest`,
    );
    requireDigest(
      module.denominator_digest,
      `${module.clause_id}.denominator_digest`,
    );
    requireDigest(
      module.proof_receipt_digest,
      `${module.clause_id}.proof_receipt_digest`,
    );
    requireDigest(
      module.replay_digest,
      `${module.clause_id}.replay_digest`,
    );
    requireSortedUnique(module.case_ids, `${module.clause_id}.case_ids`);
  }

  verifyProofArtifacts(modules);
  verifyStageSets(report.stage_sets, modules);

  const fixtureIds = requireArray(
    fixtureManifest.fixtures,
    "fixture manifest",
  ).map((entry) => entry.fixture_id);
  requireExactSet(report.fixture_ids, fixtureIds, "fixture ids");
  requireEqual(report.case_count, 4, "case count");
  requireExactSequence(
    report.admitted_clause_ids,
    ["C3", "P4"],
    "admitted clause ids",
  );
  requireExactSet(
    report.admitted_residue,
    [],
    "admitted residue",
  );
  requireExactSet(
    report.non_admitted_residue,
    requireArray(proposal.residue, "proposal residue").map(
      (entry) => entry.id,
    ),
    "non-admitted residue",
  );

  const mutationIds = [
    "C3-comparator",
    "C3-returned-value",
    "P4-missing-write",
    "P4-missing-event",
    "P4-wrong-amount",
    "P4-wrong-date",
    "P4-wrong-order",
    "P4-proof-input",
  ];
  exactKeys(report.mutations, mutationIds, "mutations");
  for (const mutationId of mutationIds) {
    requireEqual(
      report.mutations?.[mutationId],
      "detected",
      `mutation ${mutationId}`,
    );
  }

  verifyCorePathAudit(report.core_path_audit);
  requireEqual(
    report.bte?.verifier_status,
    "pass",
    "BTE verifier status",
  );
  requireEqual(
    report.bte?.structural_result,
    "expected-red",
    "BTE structural result",
  );
  requireEqual(
    report.bte?.behavioral_authority,
    false,
    "BTE behavioral authority",
  );
  requireEqual(
    report.claims?.experimental_c3_p4_profile_complete,
    true,
    "experimental profile claim",
  );
  for (const claim of [
    "full_financial_settlement_coverage",
    "formal_source_approval",
    "release_ready",
    "production_ready",
  ]) {
    requireEqual(report.claims?.[claim], false, `claim ${claim}`);
  }

  const result = {
    schema_version:
      "financial-settlement-sfol-adoption-validation/v1",
    status: errors.length === 0 ? "pass" : "fail",
    report: relative(repositoryRoot, reportPath).replaceAll("\\", "/"),
    report_digest: report.report_digest,
    cases: report.case_count,
    mutations_detected: mutationIds.length,
    core_path_status: report.core_path_audit?.status,
    formal_owner_approval: false,
    release_admission: "not-granted",
    errors: [...new Set(errors)].sort(),
  };
  console.log(JSON.stringify(result, null, 2));
  if (errors.length > 0) process.exitCode = 1;
}

function verifyProofArtifacts(modules: JsonObject[]): void {
  const artifacts = {
    C3: {
      proof: readJson(resolve(adoptionRoot, "pure-proof-receipt.json")),
      replay: readJson(
        resolve(adoptionRoot, "pure-replay-receipt.json"),
      ),
    },
    P4: {
      proof: readJson(resolve(adoptionRoot, "effect-proof-receipt.json")),
      replay: readJson(
        resolve(adoptionRoot, "effect-replay-receipt.json"),
      ),
    },
  } as const;
  for (const module of modules) {
    const artifact =
      artifacts[module.clause_id as keyof typeof artifacts];
    if (artifact === undefined) continue;
    requireEqual(
      artifact.proof.status,
      "pass",
      `${module.clause_id} proof status`,
    );
    requireEqual(
      artifact.proof.receipt_digest,
      module.proof_receipt_digest,
      `${module.clause_id} proof receipt digest`,
    );
    requireEqual(
      artifact.replay.status,
      "pass",
      `${module.clause_id} replay status`,
    );
    requireEqual(
      artifact.replay.receipt_digest,
      module.proof_receipt_digest,
      `${module.clause_id} replay receipt join`,
    );
    requireEqual(
      artifact.replay.replay_digest,
      module.replay_digest,
      `${module.clause_id} replay digest`,
    );
  }
}

function verifyStageSets(
  stageSetsInput: unknown,
  modules: JsonObject[],
): void {
  const stageSets = requireArray(stageSetsInput, "stage sets");
  const expectedStages = [
    "C_spec",
    "C_projected",
    "C_validated",
    "C_typed",
    "T_generated",
    "C_bound",
    "O_run",
    "R_evaluated",
  ];
  requireExactSet(
    stageSets.map((entry) => entry.stage),
    expectedStages,
    "stage identities",
  );
  const expectedCases = modules
    .flatMap((entry) => entry.case_ids as string[])
    .sort();
  for (const stageSet of stageSets) {
    requireExactSequence(
      stageSet.case_ids,
      expectedCases,
      `stage ${String(stageSet.stage)}`,
    );
  }
}

function verifyCorePathAudit(audit: JsonObject): void {
  const before = readJson(
    resolve(
      featureRoot,
      "generated/core-path-set-before-adoption.json",
    ),
  );
  const current = buildCorePathSet();
  const beforeByPath = new Map(
    requireArray(before.files, "core before files").map((entry) => [
      entry.path,
      entry.sha256,
    ]),
  );
  const currentByPath = new Map(
    current.files.map((entry) => [entry.path, entry.sha256]),
  );
  const added = [...currentByPath.keys()]
    .filter((path) => !beforeByPath.has(path))
    .sort();
  const removed = [...beforeByPath.keys()]
    .filter((path) => !currentByPath.has(path))
    .sort();
  const changed = [...currentByPath.keys()]
    .filter(
      (path) =>
        beforeByPath.has(path) &&
        beforeByPath.get(path) !== currentByPath.get(path),
    )
    .sort();
  requireEqual(audit?.status, "pass", "core audit status");
  requireEqual(
    audit?.before_digest,
    before.path_set_digest,
    "core before digest",
  );
  requireEqual(
    audit?.after_digest,
    current.path_set_digest,
    "core after digest",
  );
  requireExactSequence(audit?.added, added, "core added paths");
  requireExactSequence(audit?.removed, removed, "core removed paths");
  requireExactSequence(audit?.changed, changed, "core changed paths");
  if (added.length + removed.length + changed.length > 0) {
    errors.push("DS-SFOL core changed after the adoption baseline");
  }
}

function buildCorePathSet(): {
  files: Array<{ path: string; sha256: string }>;
  path_set_digest: string;
} {
  const coreRoot = resolve(
    implRoot,
    "test-derivation-engine/src/sfol",
  );
  const files = listFiles(coreRoot).map((path) => ({
    path: relative(implRoot, path).replaceAll("\\", "/"),
    sha256: sha256(readFileSync(path)),
  }));
  const unsigned = {
    schema_version: "domainspec-sfol-core-path-set/v1",
    lifecycle_point: "after-bc-003-before-bc-005",
    root: "test-derivation-engine/src/sfol",
    files,
  };
  return { files, path_set_digest: digest(unsigned) };
}

function listFiles(root: string): string[] {
  return readdirSync(root, { withFileTypes: true })
    .flatMap((entry) => {
      const path = resolve(root, entry.name);
      return entry.isDirectory() ? listFiles(path) : [path];
    })
    .filter((path) => statSync(path).isFile())
    .sort();
}

function verifyFileHandle(
  handle: JsonObject,
  path: string,
  subject: string,
): void {
  if (
    !isObject(handle) ||
    typeof handle.path !== "string" ||
    handle.path.length === 0
  ) {
    errors.push(`${subject} handle is invalid`);
    return;
  }
  requireEqual(handle.sha256, sha256(readFileSync(path)), subject);
}

function resolveFromRepository(path: unknown): string {
  if (typeof path !== "string" || path.length === 0) {
    errors.push("file handle path is missing");
    return repositoryRoot;
  }
  const resolved = resolve(repositoryRoot, path);
  const relativePath = relative(repositoryRoot, resolved);
  if (
    relativePath === ".." ||
    relativePath.startsWith("../") ||
    relativePath.startsWith("..\\")
  ) {
    errors.push(`file handle escapes repository: ${path}`);
  }
  return resolved;
}

function requireArray(value: unknown, subject: string): JsonObject[] {
  if (!Array.isArray(value)) {
    errors.push(`${subject} must be an array`);
    return [];
  }
  return value as JsonObject[];
}

function requireSortedUnique(value: unknown, subject: string): void {
  if (!Array.isArray(value)) {
    errors.push(`${subject} must be an array`);
    return;
  }
  const strings = value.filter(
    (entry): entry is string => typeof entry === "string",
  );
  if (
    strings.length !== value.length ||
    new Set(strings).size !== strings.length ||
    canonicalJson(strings) !== canonicalJson([...strings].sort())
  ) {
    errors.push(`${subject} must be a sorted unique string set`);
  }
}

function requireExactSet(
  actual: unknown,
  expected: unknown[],
  subject: string,
): void {
  if (!Array.isArray(actual)) {
    errors.push(`${subject} must be an array`);
    return;
  }
  const left = [...actual].sort();
  const right = [...expected].sort();
  if (canonicalJson(left) !== canonicalJson(right)) {
    errors.push(`${subject} differs from its exact set`);
  }
}

function requireExactSequence(
  actual: unknown,
  expected: unknown[],
  subject: string,
): void {
  if (
    !Array.isArray(actual) ||
    canonicalJson(actual) !== canonicalJson(expected)
  ) {
    errors.push(`${subject} differs from its exact sequence`);
  }
}

function exactKeys(
  value: unknown,
  expected: readonly string[],
  subject: string,
): void {
  if (!isObject(value)) {
    errors.push(`${subject} must be an object`);
    return;
  }
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (canonicalJson(actual) !== canonicalJson(wanted)) {
    errors.push(`${subject} fields differ from the schema`);
  }
}

function requireEqual(
  actual: unknown,
  expected: unknown,
  subject: string,
): void {
  if (canonicalJson(actual) !== canonicalJson(expected)) {
    errors.push(`${subject} mismatch`);
  }
}

function requireDigest(value: unknown, subject: string): void {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    errors.push(`${subject} is not a SHA-256 digest`);
  }
}

function isObject(value: unknown): value is JsonObject {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function readJson(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function digest(value: unknown): string {
  return sha256(canonicalJson(value));
}

function option(name: string): string | undefined {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

main();
