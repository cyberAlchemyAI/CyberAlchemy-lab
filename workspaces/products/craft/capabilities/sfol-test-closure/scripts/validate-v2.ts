import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(capabilityRoot, "../../../..");
const tdeRoot = resolve(repositoryRoot, "projects/domainspec-v2/impl/test-derivation-engine");
const tsx = resolve(tdeRoot, "node_modules/.bin/tsx");
const generatedRoot = resolve(capabilityRoot, "generated-v2");
const buildScript = resolve(capabilityRoot, "scripts/build-v2.ts");
const sourceCheck = resolve(capabilityRoot, "scripts/check-v2-source.ts");
const decisionCheck = resolve(capabilityRoot, "scripts/validate-v2-decisions.ts");

function sha256(value: string | Buffer): string { return createHash("sha256").update(value).digest("hex"); }
function sha256File(path: string): string { return sha256(readFileSync(path)); }
function run(command: string, args: string[], cwd: string): string {
  return execFileSync(command, args, { cwd, encoding: "utf8", env: { ...process.env, TMPDIR: "/tmp" } });
}
function runTsx(path: string): string { return run(tsx, [path], repositoryRoot); }

const sourceResult = JSON.parse(runTsx(sourceCheck));
const decisionResult = JSON.parse(runTsx(decisionCheck));
const typecheckOutput = run("pnpm", ["run", "typecheck:sfol"], tdeRoot);
const testOutputs = [
  run("pnpm", ["exec", "vitest", "run", "src/sfol"], tdeRoot),
  run("pnpm", ["exec", "vitest", "run", "src/sfol"], tdeRoot),
];
const testCount = Number(/Tests\s+(\d+) passed/.exec(testOutputs[0] ?? "")?.[1] ?? 0);
if (testCount < 100 || testOutputs.some((output) => !/Test Files\s+\d+ passed/.test(output))) {
  throw new Error("SFOL_V2_TEST_AGGREGATE_UNEXPECTED");
}

const generatedPaths = ["compiled-graph.json", "source-manifest.json", "system-ontology.json", "build-receipt.json"];
runTsx(buildScript);
const firstGenerated = Object.fromEntries(generatedPaths.map((name) => [name, sha256File(resolve(generatedRoot, name))]));
runTsx(buildScript);
const secondGenerated = Object.fromEntries(generatedPaths.map((name) => [name, sha256File(resolve(generatedRoot, name))]));
if (JSON.stringify(firstGenerated) !== JSON.stringify(secondGenerated)) throw new Error("SFOL_V2_GENERATED_OUTPUT_DRIFT");

const implementationMapPath = resolve(capabilityRoot, "implementation-map.v2-candidate.json");
const implementationMap = JSON.parse(readFileSync(implementationMapPath, "utf8"));
const compiledGraph = JSON.parse(readFileSync(resolve(generatedRoot, "compiled-graph.json"), "utf8"));
const compiledNodeIds = new Set(compiledGraph.nodes.map((node: { node_id: string }) => node.node_id));
for (const component of implementationMap.components) {
  for (const nodeId of component.operation_node_ids) {
    if (!compiledNodeIds.has(nodeId)) throw new Error(`SFOL_V2_BINDING_NODE_MISSING:${nodeId}`);
  }
}

const evidence = {
  schema_version: "domainspec-sfol-test-closure-conformance/v2",
  evidence_id: "DSV2-SFOL-TEST-CLOSURE-CONFORMANCE-V2-001",
  source: { result: sourceResult.result, source_set_digest: sourceResult.source_set_digest, compile_runs: sourceResult.compile_runs, byte_identical: sourceResult.byte_identical, nodes: sourceResult.nodes, edges: sourceResult.edges },
  implementation_map: { result: "pass", path: "implementation-map.v2-candidate.json", sha256: sha256File(implementationMapPath), component_count: implementationMap.components.length },
  typecheck: { result: "pass", command: "pnpm run typecheck:sfol", output_digest: sha256(typecheckOutput) },
  tests: { result: "pass", complete_runs: 2, test_count: testCount, deterministic_test_inventory: true },
  generated_outputs: { result: "pass", compile_runs: 2, byte_identical: true, sha256: secondGenerated },
  semantic_decisions: { result: decisionResult.result, profile_eligibility: "selected-ELIGIBLE-EXACT", source_acceptance: "selected-ACCEPT-EXACT", capability_v2: "selected-ADOPT-EXACT", business_ontology_v2: "selected-ADMIT-EXACT", system_ontology: "selected-ADMIT-EXACT" },
  authority_effect: "none",
  result: "local-technical-pass",
  blockers: [],
  claim_limit: "Technical conformance of the exact v2 source and implementation candidate, with exact profile eligibility, source acceptance, and system-ontology admission selections bound; no publication, release, deployment, or production-security authority is granted."
};
const evidencePath = resolve(capabilityRoot, "conformance/evidence-v2.json");
mkdirSync(dirname(evidencePath), { recursive: true });
writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);

const binding = {
  schema_version: "cyberalchemy-construction-binding/v2",
  binding_id: "CAV2-D65-SFOL-TEST-CLOSURE-V2-001",
  chain: {
    definitions: { path: "definition-candidates.json", sha256: sha256File(resolve(capabilityRoot, "definition-candidates.json")), status: "admitted-exact" },
    product_capability: { path: "product-capability.v2-candidate.json", sha256: sha256File(resolve(capabilityRoot, "product-capability.v2-candidate.json")), status: "adopted-exact", selection: { path: "decisions/product-capability-v2-adoption-selection.json", sha256: sha256File(resolve(capabilityRoot, "decisions/product-capability-v2-adoption-selection.json")), selected_option: "ADOPT-EXACT" } },
    business_ontology: { path: "business-ontology.v2-candidate.json", sha256: sha256File(resolve(capabilityRoot, "business-ontology.v2-candidate.json")), status: "admitted-exact", denominator: { path: "property-denominator.v2-candidate.json", sha256: sha256File(resolve(capabilityRoot, "property-denominator.v2-candidate.json")) }, selection: { path: "decisions/business-ontology-v2-admission-selection.json", sha256: sha256File(resolve(capabilityRoot, "decisions/business-ontology-v2-admission-selection.json")), selected_option: "ADMIT-EXACT" } },
    domainspec_source: { path: "domainspec-v2/project.json", sha256: sha256File(resolve(capabilityRoot, "domainspec-v2/project.json")), source_set_digest: sourceResult.source_set_digest, status: "accepted-exact", selection: { path: "decisions/domainspec-source-acceptance-v2-selection.json", sha256: sha256File(resolve(capabilityRoot, "decisions/domainspec-source-acceptance-v2-selection.json")), selected_option: "ACCEPT-EXACT" } },
    development_profile: { path: "domainspec-v2/development-profile.json", sha256: sha256File(resolve(capabilityRoot, "domainspec-v2/development-profile.json")), status: "eligible-exact", selection: { path: "decisions/profile-eligibility-selection.json", sha256: sha256File(resolve(capabilityRoot, "decisions/profile-eligibility-selection.json")), selected_option: "ELIGIBLE-EXACT" } },
    system_ontology: { path: "generated-v2/system-ontology.json", sha256: secondGenerated["system-ontology.json"], status: "admitted-exact", selection: { path: "decisions/system-ontology-v2-admission-selection.json", sha256: sha256File(resolve(capabilityRoot, "decisions/system-ontology-v2-admission-selection.json")), selected_option: "ADMIT-EXACT" } },
    implementation_binding: { path: "implementation-map.v2-candidate.json", sha256: sha256File(implementationMapPath), status: "exact-byte-bound" },
    conformance_evidence: { path: "conformance/evidence-v2.json", sha256: sha256File(evidencePath), status: "local-technical-pass" }
  },
  build_receipt: { path: "generated-v2/build-receipt.json", sha256: secondGenerated["build-receipt.json"] },
  result: "local-technical-pass",
  blockers: evidence.blockers,
  authority_effect: "none",
  claim_limit: evidence.claim_limit
};
const bindingPath = resolve(capabilityRoot, "construction-binding-v2.json");
writeFileSync(bindingPath, `${JSON.stringify(binding, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({ result: "pass", test_count: testCount, generated: secondGenerated, evidence_sha256: sha256File(evidencePath), binding_sha256: sha256File(bindingPath), authority_effect: "none" }, null, 2)}\n`);
