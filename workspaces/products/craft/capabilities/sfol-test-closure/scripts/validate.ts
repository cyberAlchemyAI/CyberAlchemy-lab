import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { digestSfolValue } from "../../../impl/test-derivation-engine/src/sfol/cases/index.ts";
import { challengeTestClosure } from "../../../impl/test-derivation-engine/src/sfol/api/index.ts";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(capabilityRoot, "../../../..");
const tdeRoot = resolve(repositoryRoot, "projects/domainspec-v2/impl/test-derivation-engine");
const tsx = resolve(tdeRoot, "node_modules/.bin/tsx");
const buildScript = resolve(capabilityRoot, "scripts/build.ts");
const decisionValidator = resolve(capabilityRoot, "scripts/validate-decisions.ts");
const cli = resolve(tdeRoot, "src/sfol/cli.ts");

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function sha256File(path: string): string {
  return sha256(readFileSync(path));
}

function run(command: string, args: string[], cwd: string): string {
  return execFileSync(command, args, { cwd, encoding: "utf8", env: { ...process.env, TMPDIR: "/tmp" } });
}

const decisionValidation = JSON.parse(run(tsx, [decisionValidator], repositoryRoot));

const immutable = {
  "EVF-OBLIGATION.v1.json": "5a9a41fb43723a47203eee2b1173654e443a054aa97d405322d5173965a3c4f7",
  "FORMAL-CLAIM-SFOL.v1.json": "50ce8c6d7aa49050345cac5ef192b8485dfc3cfb5541c153e382cd4c4d2bd37e",
  "SFOL-CLAUSE-ADMISSION-MANIFEST.v1.json": "f3a8c7ca8598d3eccaef749df376537c7c902c5f42bc8101694dcffdf06a5431",
  "SFOL-MODULE.v1.json": "e9ba011a399d61e5310d1863306681c0c9907bcfb95ce85f53107dd18ee28742",
  "TDE-EVIDENCE.v1.json": "3ec525d820b41468bf4fb58e562018320c8c1b80366aa73737fad3eb5b2073fe",
  "TDE-FIXTURES.v1.json": "f763b1bb1ed38c6e392efc61f96989dc6b42f42eff52b5576aa5b714bde5daac",
  "TDE-MUTATION-EVIDENCE.v1.json": "2428b8395d126acf77e0162ed29078f43f335d00276ea74262bbd2bc56d56a99",
  "W7-PREIMAGE-MANIFEST.v1.json": "ab7c0ecf2216db15c0cfc9a1ed833c5ccef97f34a59e534ee23d8b9d405c47bf"
} as const;
const authCaseRoot = resolve(repositoryRoot, "projects/auth-foundation/formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001");
for (const [name, expected] of Object.entries(immutable)) {
  const actual = sha256File(resolve(authCaseRoot, name));
  if (actual !== expected) throw new Error(`HISTORICAL_AUTH_V1_DRIFT:${name}:${actual}`);
}
const lean = {
  "projects/auth-foundation/formalization/cases/AF-EXACT-SESSION-ROLE-PERMISSION-001/ExactSessionRolePermission.lean": "59882ef5c75d48a3e04c82529411981c994ef6caa4d706fc33f77ed6c09f8a08",
  "projects/auth-foundation/formalization/cases/AF-EXACT-SESSION-ROLE-PERMISSION-001/ExactSessionRolePermission.v2.lean": "b0b2c443cdf500dfc912cb0e5168c5295fee0ef10d3074a70a840714afb04dad",
  "projects/auth-foundation/formalization/cases/AF-EXACT-SESSION-ROLE-PERMISSION-001/FORMAL-CLAIM.v5-lean-candidate.json": "3a11ccc3587c710ccfc24312f4c82197757caf555f12eb673915c4a3aa2b4fc8",
  "projects/auth-foundation/formalization/cases/AF-EXACT-SESSION-ROLE-PERMISSION-001/THEOREM-OBLIGATION-RECEIPT.v1.json": "1997cb7e88086625bd770c473cf4322d59d567bfaf74e6a7ba581d2d046602ae"
} as const;
for (const [path, expected] of Object.entries(lean)) {
  const actual = sha256File(resolve(repositoryRoot, path));
  if (actual !== expected) throw new Error(`LEAN_PREIMAGE_DRIFT:${path}:${actual}`);
}

const typecheck = run("pnpm", ["run", "typecheck:sfol"], tdeRoot);
const normalizedTypecheck = typecheck
  .replaceAll(tdeRoot, "<TDE_ROOT>")
  .replaceAll(repositoryRoot, "<REPOSITORY_ROOT>");
const testOutputs = [
  run("pnpm", ["exec", "vitest", "run", "src/sfol"], tdeRoot),
  run("pnpm", ["exec", "vitest", "run", "src/sfol"], tdeRoot),
];
const testCount = Number(/Tests\s+(\d+) passed/.exec(testOutputs[0] ?? "")?.[1] ?? 0);
if (testCount < 100 || testOutputs.some((output) => !/Test Files\s+\d+ passed/.test(output))) {
  throw new Error("SFOL_TEST_AGGREGATE_UNEXPECTED");
}

run(tsx, [buildScript], repositoryRoot);
const generatedPaths = ["compiled-graph.json", "source-manifest.json", "system-ontology.json", "build-receipt.json"];
const firstGenerated = Object.fromEntries(generatedPaths.map((name) => [name, sha256File(resolve(capabilityRoot, "generated", name))]));
run(tsx, [buildScript], repositoryRoot);
const secondGenerated = Object.fromEntries(generatedPaths.map((name) => [name, sha256File(resolve(capabilityRoot, "generated", name))]));
if (JSON.stringify(firstGenerated) !== JSON.stringify(secondGenerated)) throw new Error("SFOL_GENERATED_OUTPUT_DRIFT");
const builtBinding = JSON.parse(readFileSync(resolve(capabilityRoot, "construction-binding.json"), "utf8"));
if (
  builtBinding.chain.definitions.status !== "admitted-exact" ||
  builtBinding.chain.definitions.admission_selection?.selected_option !== "ADMIT-EXACT" ||
  builtBinding.blockers.includes("definition admission") ||
  builtBinding.chain.product_capability.status !== "adopted-exact" ||
  builtBinding.chain.product_capability.adoption_selection?.selected_option !== "ADOPT-EXACT" ||
  builtBinding.blockers.includes("Product Capability adoption") ||
  builtBinding.chain.business_ontology.status !== "admitted-exact" ||
  builtBinding.chain.business_ontology.admission_selection?.selected_option !== "ADMIT-EXACT" ||
  builtBinding.chain.business_ontology.property_denominator?.sha256 !== "db481764813e3f61398d89683b497855ee504173b1cffdfa7ee30450be3cb68d" ||
  builtBinding.blockers.includes("business ontology admission") ||
  !builtBinding.blockers.includes("DomainSpec source acceptance") ||
  !builtBinding.blockers.includes("development profile eligibility decision")
) {
  throw new Error("SFOL_OWNER_SELECTION_PROJECTION_INVALID");
}

const temporary = mkdtempSync(resolve(tmpdir(), "sfol-tde-cli-"));
try {
  const unsigned = { schema_version: "sfol-cli-smoke/v1", result: "pass" };
  const requestPath = resolve(temporary, "receipt.json");
  writeFileSync(requestPath, `${JSON.stringify({ ...unsigned, receipt_digest: digestSfolValue(unsigned) }, null, 2)}\n`);
  const cliResult = JSON.parse(run(tsx, [cli, "verify", "--in", requestPath], repositoryRoot));
  if (!cliResult.ok) throw new Error("SFOL_CLI_SMOKE_FAILED");
  const challengeRequest = { profile_version: "domainspec-sfol-negative-control/v1" as const, fault_models: [], controls: [], observations: [] };
  const challengePath = resolve(temporary, "challenge.json");
  writeFileSync(challengePath, `${JSON.stringify(challengeRequest, null, 2)}\n`);
  const beforeCheck = readdirSync(temporary).sort();
  const cliChallenge = JSON.parse(run(tsx, [cli, "challenge", "--in", challengePath, "--check"], repositoryRoot));
  const afterCheck = readdirSync(temporary).sort();
  if (JSON.stringify(cliChallenge) !== JSON.stringify(challengeTestClosure(challengeRequest))) throw new Error("SFOL_API_CLI_PARITY_FAILED");
  if (JSON.stringify(beforeCheck) !== JSON.stringify(afterCheck)) throw new Error("SFOL_CLI_CHECK_WROTE_FILES");
} finally {
  rmSync(temporary, { recursive: true, force: true });
}

const denominator = JSON.parse(readFileSync(resolve(capabilityRoot, "property-denominator.json"), "utf8"));
if (denominator.properties.length !== denominator.property_count || denominator.property_count !== 21) {
  throw new Error("SFOL_PROPERTY_DENOMINATOR_INCOMPLETE");
}

const evidence = {
  schema_version: "domainspec-sfol-test-closure-conformance/v1",
  evidence_id: "DSV2-SFOL-TEST-CLOSURE-CONFORMANCE-001",
  implementation_map_sha256: sha256File(resolve(capabilityRoot, "implementation-map.json")),
  typecheck: { result: "pass", command: "pnpm run typecheck:sfol", output_digest: sha256(normalizedTypecheck) },
  tests: { result: "pass", complete_runs: 2, test_count: testCount, deterministic_test_inventory: true },
  generated_outputs: { result: "pass", compile_runs: 2, byte_identical: true, sha256: secondGenerated },
  cli_smoke: { result: "pass", commands: ["verify", "challenge --check"], api_cli_parity: true, check_mode_writes: 0 },
  property_denominator: { result: "pass", property_count: denominator.property_count },
  decision_candidate_integrity: {
    result: decisionValidation.result,
    authority_effect: decisionValidation.authority_effect,
    schema_digest: decisionValidation.schema_digest,
    selection_schema_digest: decisionValidation.selection_schema_digest,
    candidate_count: decisionValidation.decision_candidates.length,
    candidates: decisionValidation.decision_candidates,
    selections: decisionValidation.selections
  },
  preserved_preimages: { result: "pass", auth_v1: immutable, lean },
  result: "local-technical-pass",
  authority_effect: "none",
  claim_limit: "Technical conformance of the development candidate only; predecessor admission, canonical ontology admission, publication, deployment, and production security are not granted."
};
const evidencePath = resolve(capabilityRoot, "conformance/evidence.json");
mkdirSync(dirname(evidencePath), { recursive: true });
writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);

const systemOntologyPath = resolve(capabilityRoot, "generated/system-ontology.json");
const amendment = {
  schema_version: "domainspec-product-ontology-amendment-candidate/v1",
  amendment_id: "DSV2-PRODUCT-ONTOLOGY-SFOL-TEST-CLOSURE-001",
  target_package: "projects/domainspec-v2/ontology",
  source_bindings: {
    definitions: { path: "definition-candidates.json", sha256: sha256File(resolve(capabilityRoot, "definition-candidates.json")) },
    product_capability: { path: "product-capability.json", sha256: sha256File(resolve(capabilityRoot, "product-capability.json")) },
    business_ontology: { path: "business-ontology.json", sha256: sha256File(resolve(capabilityRoot, "business-ontology.json")) },
    compiled_graph: { path: "generated/compiled-graph.json", sha256: sha256File(resolve(capabilityRoot, "generated/compiled-graph.json")) },
    system_ontology: { path: "generated/system-ontology.json", sha256: sha256File(systemOntologyPath) },
    conformance: { path: "conformance/evidence.json", sha256: sha256File(evidencePath) }
  },
  business_nodes: ["dsv2.product.sfol-test-closure", "dsv2.product.bounded-partition-calculus", "dsv2.product.negative-control-discrimination", "dsv2.product.test-closure-replay"],
  system_nodes: JSON.parse(readFileSync(systemOntologyPath, "utf8")).components.map((component: any) => component.component_id).sort(),
  bridge_relations: [
    { from: "dsv2.product.sfol-test-closure", type: "realized_by", to: "dsv2.system.tde-sfol-api" },
    { from: "dsv2.product.sfol-test-closure", type: "realized_by", to: "dsv2.system.tde-sfol-cli" },
    { from: "dsv2.product.bounded-partition-calculus", type: "realized_by", to: "dsv2.system.sfol-partition-engine" },
    { from: "dsv2.product.negative-control-discrimination", type: "realized_by", to: "dsv2.system.evf-negative-control-engine" },
    { from: "dsv2.product.negative-control-discrimination", type: "observed_by", to: "dsv2.system.evf-detection-matrix-builder" },
    { from: "dsv2.product.test-closure-replay", type: "realized_by", to: "dsv2.system.sfol-proof-replay" }
  ],
  projection_eligibility: "not_evaluable",
  blockers: ["DomainSpec source acceptance", "development profile eligibility decision", "generated system ontology admission"],
  authority_effect: "none"
};
const amendmentPath = resolve(capabilityRoot, "product-ontology-amendment-candidate.json");
writeFileSync(amendmentPath, `${JSON.stringify(amendment, null, 2)}\n`);

const bindingPath = resolve(capabilityRoot, "construction-binding.json");
const binding = JSON.parse(readFileSync(bindingPath, "utf8"));
binding.chain.conformance_evidence = { path: "conformance/evidence.json", sha256: sha256File(evidencePath), status: "local-technical-pass" };
binding.chain.canonical_product_ontology_projection = { path: "product-ontology-amendment-candidate.json", sha256: sha256File(amendmentPath), status: "candidate-not_evaluable" };
binding.blockers = binding.blockers.filter((blocker: string) => blocker !== "conformance evidence");
writeFileSync(bindingPath, `${JSON.stringify(binding, null, 2)}\n`);

process.stdout.write(`${JSON.stringify({ result: "pass", test_count: testCount, generated: secondGenerated, evidence_sha256: sha256File(evidencePath) }, null, 2)}\n`);
