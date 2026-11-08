import { createHash } from "node:crypto";
import {
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, posix, resolve } from "node:path";

import { validateJsonSchema } from "../../../../../tools/minted-project/schema-validator";

type JsonObject = Record<string, any>;

const REQUIRED_SOURCE_BINDINGS = [
  "financial-settlement.deal-service",
  "financial-settlement.generate-settlement",
  "financial-settlement.operations",
  "financial-settlement.settlement-service",
];
const REQUIRED_FIXTURES = [
  "financial-settlement.C3.above-threshold",
  "financial-settlement.C3.at-threshold",
  "financial-settlement.C3.below-threshold",
  "financial-settlement.P4.eligible-payout",
];
const REQUIRED_RESIDUE = [
  "C1",
  "C2",
  "C4",
  "P1",
  "P2",
  "P3",
  "P4-converse-duplicate-payout",
  "P4-converse-zero-payout",
  "R1",
  "R2",
  "R3",
  "R4",
  "R5",
];

function parseArguments(): {
  repositoryRoot: string;
  proposalPath: string;
  outputPath: string;
} {
  const values = new Map<string, string>();
  for (let index = 2; index < process.argv.length; index += 2) {
    const key = process.argv[index];
    const value = process.argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error("arguments must be --repository-root, --proposal, and --output pairs");
    }
    values.set(key, value);
  }
  const repositoryRoot = values.get("--repository-root");
  const proposalPath = values.get("--proposal");
  const outputPath = values.get("--output");
  if (!repositoryRoot || !proposalPath || !outputPath) {
    throw new Error("--repository-root, --proposal, and --output are required");
  }
  return { repositoryRoot, proposalPath, outputPath };
}

function readJson(path: string): JsonObject {
  return JSON.parse(readFileSync(path, "utf8")) as JsonObject;
}

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function canonical(value: unknown): string {
  if (
    value === null ||
    typeof value === "boolean" ||
    typeof value === "string" ||
    typeof value === "number"
  ) {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(canonical).join(",")}]`;
  }
  if (typeof value === "object") {
    const record = value as JsonObject;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical(record[key])}`)
      .join(",")}}`;
  }
  throw new Error(`unsupported canonical value: ${typeof value}`);
}

function digest(value: unknown): string {
  return sha256(canonical(value));
}

function exactSet(actual: string[], expected: string[]): boolean {
  const left = [...new Set(actual)].sort();
  const right = [...expected].sort();
  return left.length === actual.length && canonical(left) === canonical(right);
}

function safeRepositoryPath(repositoryRoot: string, rawPath: string): string | null {
  const normalized = rawPath.replaceAll("\\", "/");
  if (
    !normalized ||
    isAbsolute(normalized) ||
    normalized.split("/").includes("..") ||
    posix.normalize(normalized) !== normalized
  ) {
    return null;
  }
  const root = resolve(repositoryRoot);
  const target = resolve(root, normalized);
  return target.startsWith(`${root}/`) ? target : null;
}

function forbiddenFixtureKey(value: unknown, path = "$"): string | null {
  if (Array.isArray(value)) {
    for (const [index, item] of value.entries()) {
      const found = forbiddenFixtureKey(item, `${path}[${index}]`);
      if (found) return found;
    }
    return null;
  }
  if (!value || typeof value !== "object") return null;
  for (const [key, item] of Object.entries(value as JsonObject)) {
    if (/^(expected|oracle|verdict|assertion|acceptance)(?:_|$)/i.test(key)) {
      return `${path}.${key}`;
    }
    const found = forbiddenFixtureKey(item, `${path}.${key}`);
    if (found) return found;
  }
  return null;
}

function main(): number {
  const args = parseArguments();
  const repositoryRoot = resolve(args.repositoryRoot);
  const proposalPath = resolve(repositoryRoot, args.proposalPath);
  const outputPath = resolve(repositoryRoot, args.outputPath);
  const proposal = readJson(proposalPath);
  const errors: string[] = [];

  const schemaPath = resolve(dirname(proposalPath), "source-proposal.schema.json");
  for (const violation of validateJsonSchema(schemaPath, proposal)) {
    errors.push(`schema:${violation.path}:${violation.keyword}:${violation.detail}`);
  }

  const sourceBindings = proposal.source_bindings as JsonObject[];
  if (
    !Array.isArray(sourceBindings) ||
    !exactSet(
      sourceBindings.map((entry) => entry.binding_id),
      REQUIRED_SOURCE_BINDINGS,
    )
  ) {
    errors.push("source binding IDs are not the exact required four-source set");
  } else {
    for (const binding of sourceBindings) {
      const path = safeRepositoryPath(repositoryRoot, binding.path);
      if (path === null) {
        errors.push(`unsafe source path: ${String(binding.path)}`);
        continue;
      }
      let bytes: Buffer;
      try {
        bytes = readFileSync(path);
      } catch {
        errors.push(`missing source binding: ${binding.path}`);
        continue;
      }
      if (sha256(bytes) !== binding.sha256) {
        errors.push(`source digest drift: ${binding.binding_id}`);
      }
    }
  }

  const clauses = proposal.clauses as JsonObject[];
  if (
    !Array.isArray(clauses) ||
    !exactSet(clauses.map((clause) => clause.clause_id), ["C3", "P4"])
  ) {
    errors.push("proposal clause set must be exactly C3 and P4");
  }
  for (const clause of Array.isArray(clauses) ? clauses : []) {
    if (digest(clause.normalized_semantic) !== clause.semantic_digest) {
      errors.push(`semantic digest drift: ${clause.clause_id}`);
    }
    if (digest(clause.proposed_ast) !== clause.ast_digest) {
      errors.push(`AST digest drift: ${clause.clause_id}`);
    }
  }

  const c3 = clauses?.find((clause) => clause.clause_id === "C3");
  if (
    !c3 ||
    c3.class !== "pure-function" ||
    c3.normalized_semantic?.result?.conditional?.operator !== "gte" ||
    c3.normalized_semantic?.result?.conditional?.threshold !== 100 ||
    canonical(c3.normalized_semantic?.result?.conditional?.when_true) !==
      canonical({ numerator: 1, denominator: 2 }) ||
    canonical(c3.normalized_semantic?.result?.conditional?.when_false) !==
      canonical({ numerator: 2, denominator: 5 }) ||
    c3.proposed_ast?.node_kind !== "Calculation" ||
    c3.proposed_ast?.clause?.clause_id !== "financial-settlement.C3" ||
    !exactSet(c3.fixture_ids ?? [], REQUIRED_FIXTURES.filter((id) => id.includes(".C3.")))
  ) {
    errors.push("C3 normalized semantic, AST, or fixture boundary drifted");
  }

  const p4 = clauses?.find((clause) => clause.clause_id === "P4");
  const observations = p4?.normalized_semantic?.consequent?.ordered_observations;
  if (
    !p4 ||
    p4.class !== "effect-relation" ||
    p4.normalized_semantic?.logical_form !== "implication" ||
    p4.normalized_semantic?.converse_admitted !== false ||
    !Array.isArray(observations) ||
    canonical(observations.map((entry: JsonObject) => [entry.sequence, entry.kind, entry.name])) !==
      canonical([[0, "write", "PAYOUT"], [1, "event", "PayoutCreated"]]) ||
    observations.some(
      (entry: JsonObject) =>
        entry.payload?.amount !== "totalPayout" ||
        entry.payload?.date !== "endDate",
    ) ||
    p4.proposed_ast?.node_kind !== "Operation" ||
    p4.proposed_ast?.clause?.logical_form !== "implication" ||
    !exactSet(p4.fixture_ids ?? [], ["financial-settlement.P4.eligible-payout"])
  ) {
    errors.push("P4 implication, ordered observation, AST, or fixture boundary drifted");
  }

  const effectContract = proposal.effect_contract?.contract;
  if (
    proposal.effect_contract?.clause_id !== "P4" ||
    digest(effectContract) !== proposal.effect_contract?.contract_digest ||
    effectContract?.schema_version !== "domainspec-sfol-effect-trace-contract/v1" ||
    canonical(
      effectContract?.effect_sequence?.map((entry: JsonObject) => [
        entry.kind,
        entry.name,
        entry.payload_tag,
      ]),
    ) !== canonical([["write", "PAYOUT", "record"], ["event", "PayoutCreated", "record"]]) ||
    effectContract?.max_effects !== 2 ||
    effectContract?.observation_identity?.adapter_may_manufacture_observations !== false
  ) {
    errors.push("P4 effect observation contract or digest drifted");
  }

  const manifestPath = safeRepositoryPath(
    repositoryRoot,
    proposal.fixture_manifest?.path,
  );
  let fixtureManifest: JsonObject | null = null;
  if (manifestPath === null) {
    errors.push("unsafe fixture manifest path");
  } else {
    const bytes = readFileSync(manifestPath);
    if (sha256(bytes) !== proposal.fixture_manifest?.sha256) {
      errors.push("fixture manifest digest drift");
    }
    fixtureManifest = JSON.parse(bytes.toString("utf8")) as JsonObject;
  }
  const manifestFixtures = fixtureManifest?.fixtures as JsonObject[] | undefined;
  if (
    !Array.isArray(manifestFixtures) ||
    !exactSet(
      manifestFixtures.map((fixture) => fixture.fixture_id),
      REQUIRED_FIXTURES,
    )
  ) {
    errors.push("fixture manifest is not the exact four-fixture set");
  } else {
    for (const entry of manifestFixtures) {
      const path = safeRepositoryPath(repositoryRoot, entry.path);
      if (path === null) {
        errors.push(`unsafe fixture path: ${String(entry.path)}`);
        continue;
      }
      const bytes = readFileSync(path);
      if (sha256(bytes) !== entry.sha256) {
        errors.push(`fixture digest drift: ${entry.fixture_id}`);
      }
      const fixture = JSON.parse(bytes.toString("utf8")) as JsonObject;
      if (
        fixture.fixture_id !== entry.fixture_id ||
        fixture.clause_id !== entry.clause_id ||
        fixture.coverage_key !== entry.coverage_key
      ) {
        errors.push(`fixture identity mismatch: ${entry.fixture_id}`);
      }
      const forbidden = forbiddenFixtureKey(fixture);
      if (forbidden) {
        errors.push(`fixture contains forbidden oracle field: ${forbidden}`);
      }
    }
  }

  const residue = proposal.residue as JsonObject[];
  if (
    !Array.isArray(residue) ||
    !exactSet(residue.map((entry) => entry.id), REQUIRED_RESIDUE)
  ) {
    errors.push("residue is not the exact non-admitted clause and P4-converse set");
  }

  const operations = readFileSync(
    resolve(
      repositoryRoot,
      "projects/domainspec-v2/impl/test-derivation-engine/__fixtures__/financial-settlement/operations.md",
    ),
    "utf8",
  );
  const deal = readFileSync(
    resolve(repositoryRoot, "validation/poker-team/backend/src/domain/deal/deal.service.ts"),
    "utf8",
  );
  const settlement = readFileSync(
    resolve(
      repositoryRoot,
      "validation/poker-team/backend/src/domain/settlement/settlement.service.ts",
    ),
    "utf8",
  );
  const useCase = readFileSync(
    resolve(
      repositoryRoot,
      "validation/poker-team/backend/src/use-cases/financial-settlement/generate-settlement.ts",
    ),
    "utf8",
  );
  for (const [label, content, required] of [
    ["operations C3", operations, "| C3  | Deal split"],
    ["operations P4", operations, "| P4  | Integration Guarantee"],
    ["deal symbol", deal, "export const getDealSplit"],
    ["deal threshold", deal, "if (value >= 100)"],
    ["eligibility", settlement, "shouldCreatePayoutEvent:"],
    ["PAYOUT write", useCase, 'type: "PAYOUT"'],
    ["PayoutCreated event", useCase, 'type: "PayoutCreated"'],
  ] as const) {
    if (!content.includes(required)) errors.push(`missing source anchor: ${label}`);
  }

  const claims = proposal.claims;
  if (
    proposal.authority?.authority_effect !== "none" ||
    proposal.authority?.formal_owner_approval !== "absent" ||
    proposal.authority?.release_admission !== "not-granted" ||
    claims?.formal_source_approval !== false ||
    claims?.full_financial_settlement_coverage !== false ||
    claims?.release_ready !== false ||
    claims?.production_ready !== false
  ) {
    errors.push("proposal exceeds experimental non-authoritative claim boundary");
  }

  const receipt = {
    schema_version: "financial-settlement-sfol-source-proposal-validation/v1",
    proposal_id: proposal.proposal_id,
    proposal_sha256: sha256(readFileSync(proposalPath)),
    status: errors.length === 0 ? "pass" : "fail",
    admitted_clause_ids: ["C3", "P4"],
    fixture_ids: REQUIRED_FIXTURES,
    semantic_digests: Object.fromEntries(
      clauses.map((clause) => [clause.clause_id, clause.semantic_digest]),
    ),
    ast_digests: Object.fromEntries(
      clauses.map((clause) => [clause.clause_id, clause.ast_digest]),
    ),
    effect_contract_digest: proposal.effect_contract?.contract_digest,
    formal_owner_approval: false,
    release_admission: "not-granted",
    errors: [...new Set(errors)].sort(),
  };
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, `${JSON.stringify(receipt, null, 2)}\n`);
  if (errors.length > 0) {
    for (const error of receipt.errors) console.error(error);
    return 1;
  }
  console.log(
    `Financial Settlement SFOL source proposal: PASS (${receipt.admitted_clause_ids.length} clauses, ${receipt.fixture_ids.length} fixtures)`,
  );
  return 0;
}

process.exitCode = main();
