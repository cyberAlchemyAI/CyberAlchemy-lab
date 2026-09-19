import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, readdirSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(scriptDir, "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const implementationRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/coding-agent-runtime");
const generatedRoot = resolve(packageRoot, "domainspec/generated");
const node = "/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node";

function sha256(value) { return createHash("sha256").update(value).digest("hex"); }
function load(path) { return JSON.parse(readFileSync(path, "utf8")); }
function run(command, args, cwd) {
  return spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    env: {...process.env, PATH: `${dirname(node)}:${process.env.PATH ?? ""}`},
    maxBuffer: 16 * 1024 * 1024,
  });
}
function file(path) {
  return {path: path.slice(repositoryRoot.length + 1).replaceAll("\\", "/"), sha256: sha256(readFileSync(path))};
}
function check(name, passed, details = {}) {
  checks.push({check: name, status: passed ? "PASS" : "BLOCK", ...details});
  if (!passed) errors.push(name);
}

const checks = [];
const errors = [];
const profile = load(resolve(packageRoot, "profile.json"));
const capability = load(resolve(packageRoot, "product-capability.json"));
const ontology = load(resolve(packageRoot, "business-ontology.json"));
const contract = load(resolve(packageRoot, "interface-contract.json"));
const productTestReceipt = load(resolve(packageRoot, "receipts/l2-product-test.json"));

check("semantic-identity-closure",
  profile.product_capability_ref === capability.capability_id
  && profile.business_ontology_ref === ontology.ontology_id
  && capability.output_contract_refs.includes(contract.contract_id)
  && [profile, capability, ontology, contract].every((item) => item.authority_effect === "none"));

const sourceDrift = [];
for (const source of load(resolve(packageRoot, "sources.l2.json")).sources) {
  const path = resolve(repositoryRoot, source.path);
  let observed = null;
  try { observed = sha256(readFileSync(path)); } catch {}
  if (observed !== source.sha256) sourceDrift.push({id: source.id, expected: source.sha256, observed});
}
check("selected-source-digests", sourceDrift.length === 0, {drift: sourceDrift});

const productCandidatePath = resolve(packageRoot, "testable-product-candidate.json");
const productTestContractPath = resolve(packageRoot, "product-test-contract.json");
check("frozen-product-test-predecessor",
  productTestReceipt.status === "PASS"
  && productTestReceipt.candidate?.sha256 === sha256(readFileSync(productCandidatePath))
  && productTestReceipt.product_test_contract?.sha256 === sha256(readFileSync(productTestContractPath)),
  {validation_ref: productTestReceipt.validation_id});

const domainspecProject = resolve(repositoryRoot, "projects/domainspec-v2/impl");
const buildArgs = ["--import", "tsx", "../../../cyberAlchemy-v2/development/agent-reasoning-engine/codex-integration/coding-agent-runtime/scripts/build.ts", "--emit-json"];
const first = run(node, buildArgs, domainspecProject);
const second = run(node, buildArgs, domainspecProject);
const deterministic = first.status === 0 && second.status === 0 && first.stdout === second.stdout;
check("domainspec-two-run-determinism", deterministic);
let generatedParity = false;
if (deterministic) {
  const artifacts = JSON.parse(first.stdout);
  generatedParity = Object.entries(artifacts).every(([name, content]) => readFileSync(resolve(generatedRoot, name), "utf8") === content);
}
check("generated-artifact-parity", generatedParity);

const testFiles = readdirSync(resolve(implementationRoot, "test"))
  .filter((name) => name.endsWith(".test.mjs"))
  .sort()
  .map((name) => `test/${name}`);
const tests = run(node, ["--test", ...testFiles], implementationRoot);
const testCount = Number(/(?:#|ℹ) tests\s+(\d+)/.exec(tests.stdout)?.[1] ?? 0);
check("coding-agent-focused-tests", tests.status === 0 && testCount > 0, {test_count: testCount, ...(tests.status === 0 ? {} : {stderr: tests.stderr.trim()})});

const rpcTests = run(node, ["--test", "test/rpc-client.test.mjs"], resolve(implementationRoot, "../codex-app-server-wrapper"));
const rpcTestCount = Number(/(?:#|ℹ) tests\s+(\d+)/.exec(rpcTests.stdout)?.[1] ?? 0);
check("rpc-client-focused-tests", rpcTests.status === 0 && rpcTestCount > 0, {test_count: rpcTestCount, ...(rpcTests.status === 0 ? {} : {stderr: rpcTests.stderr.trim()})});

const demo = run(node, ["bin/demo.mjs", "--approve"], implementationRoot);
let demoReceipt = null;
try { demoReceipt = JSON.parse(demo.stdout); } catch {}
check("approved-human-test-demo", demo.status === 0 && demoReceipt?.status === "PATCH_CANDIDATE" && demoReceipt?.verification?.status === "PASS_BOUNDED");

const live = run(node, ["scripts/live-gateway-canary.mjs"], implementationRoot);
let liveReceipt = null;
try { liveReceipt = JSON.parse(live.stdout); } catch {}
check("live-app-server-gateway-restart-canary",
  live.status === 0
  && liveReceipt?.status === "PASS"
  && liveReceipt?.authenticated_session_resumption === true
  && liveReceipt?.stable_thread_identity_replayed === true
  && liveReceipt?.stable_request_upstream_redispatches === 0
  && liveReceipt?.coding_result?.verification_status === "PASS_BOUNDED",
  {observed_codex_version: liveReceipt?.observed_codex_version ?? null, ...(live.status === 0 ? {} : {stderr: live.stderr.trim()})});

const receiptMaterial = {
  schema_version: "cav2-are-coding-agent-runtime-validation/v1",
  validation_id: "ARE-CAR-L2-VALIDATION-001",
  status: errors.length === 0 ? "PASS" : "BLOCK",
  implementation_level: "L2-live-gateway-restart-canary",
  checks,
  errors,
  test_count: testCount || null,
  rpc_test_count: rpcTestCount || null,
  product_test_predecessor: file(resolve(packageRoot, "receipts/l2-product-test.json")),
  demo_status: demoReceipt?.status ?? null,
  live_canary: liveReceipt,
  production_sandbox: false,
  authority_effect: "none",
  claim_limit: "One controlled live Codex App Server turn through the persistent ARE gateway, including authenticated restart/reconnect continuity; no general reliability, production sandbox, acceptance, publication, deployment, or external-effect claim."
};
const receipt = {...receiptMaterial, validation_digest: sha256(JSON.stringify(receiptMaterial))};
mkdirSync(resolve(packageRoot, "receipts"), {recursive: true});
writeFileSync(resolve(packageRoot, "receipts/l2-validation.json"), `${JSON.stringify(receipt, null, 2)}\n`);

const implementationFiles = [
  "index.mjs", "controller.mjs", "prompt.mjs", "model-transport.mjs", "live-session.mjs", "verifier.mjs",
  "schemas/next-action-candidate.schema.json", "bin/demo.mjs", "bin/live-demo.mjs", "scripts/live-gateway-canary.mjs",
  "test/coding-agent-runtime.test.mjs", "test/live-session.test.mjs", "test/model-driven-turn.test.mjs", "package.json",
].map((path) => file(resolve(implementationRoot, path)));
const generatedFiles = ["graph.json", "system-ontology.json", "build-receipt.json", "system-ontology-receipt.json"].map((path) => file(resolve(generatedRoot, path)));
const productIntegrationFiles = ["README.md", "bin/are.mjs", "package.json", "product.json", "test/product.test.mjs"]
  .map((path) => file(resolve(implementationRoot, "../..", path)));
const selectedDependencies = load(resolve(packageRoot, "sources.l2.json")).sources.map((source) => ({id: source.id, path: source.path, sha256: source.sha256}));
const binding = {
  schema_version: "cav2-d65-construction-binding/v1",
  binding_id: "CA2-D65-ARE-CODING-AGENT-RUNTIME-L2-001",
  predecessor_binding_ref: "CA2-D65-ARE-CODING-AGENT-RUNTIME-L1-001",
  binding_posture: "candidate-exact-byte-binding-not-accepted",
  implementation_level: "L2-live-gateway-restart-canary",
  project_ref: profile.project_ref,
  product_capability_ref: capability.capability_id,
  business_ontology_ref: ontology.ontology_id,
  domainspec_project_ref: profile.domainspec_project_ref,
  system_ontology_ref: "CA2-ARE-CODING-AGENT-RUNTIME-SYSTEM-ONTOLOGY",
  stages: [
    {stage: "canonical-definitions", status: "exact-source-bound", artifact: file(resolve(repositoryRoot, "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"))},
    {stage: "immutable-product-capability", status: "candidate-not-adopted", artifact: file(resolve(packageRoot, "product-capability.json"))},
    {stage: "capability-local-business-ontology", status: "candidate-not-admitted", artifact: file(resolve(packageRoot, "business-ontology.json"))},
    {stage: "domainspec-v2-authored-source", status: "candidate-not-admitted", artifacts: [file(resolve(packageRoot, "domainspec/project.json")), file(resolve(packageRoot, "domainspec/feature.json")), ...["coding-request.json", "live-model-session.json", "model-turn-output.json", "next-action-candidate.json", "patch-candidate.json", "safe-effect-invariant.json"].map((path) => file(resolve(packageRoot, "domainspec/nodes", path)))]},
    {stage: "deterministic-compiled-graph-and-system-ontology", status: deterministic && generatedParity ? "candidate-read-model" : "not_evaluable", artifacts: generatedFiles},
    {stage: "tested-product-candidate", status: productTestReceipt.status === "PASS" ? "bounded-static-product-test-pass" : "not_evaluable", artifacts: [file(productCandidatePath), file(productTestContractPath), file(resolve(packageRoot, "receipts/l2-product-test.json"))]},
    {stage: "exact-implementation-binding", status: "candidate-exact-byte-binding-not-accepted", artifacts: [...implementationFiles, ...productIntegrationFiles], selected_dependencies: selectedDependencies},
    {stage: "conformance-evidence", status: errors.length === 0 ? "bounded-live-canary-pass" : "not_evaluable", artifact: file(resolve(packageRoot, "receipts/l2-validation.json"))},
  ],
  live_model_transport: errors.length === 0 ? "validated-by-one-controlled-canary" : "not_evaluable",
  live_proxy_integration: true,
  production_sandbox: false,
  authority_effect: "none",
  claim_limit: receipt.claim_limit,
};
writeFileSync(resolve(packageRoot, "construction-binding.l2.json"), `${JSON.stringify(binding, null, 2)}\n`);

mkdirSync(resolve(packageRoot, "evidence"), {recursive: true});
const conformance = {
  schema_version: "cav2-are-coding-agent-runtime-conformance/v1",
  evidence_id: "ARE-CAR-L2-CONFORMANCE-001",
  result: errors.length === 0 ? "PASS_BOUNDED" : "not_evaluable",
  binding: file(resolve(packageRoot, "construction-binding.l2.json")),
  validation: file(resolve(packageRoot, "receipts/l2-validation.json")),
  scope: "one controlled live Codex App Server coding turn through the persistent ARE gateway, with authenticated restart/reconnect continuity and one independently verified mutation to an ephemeral fixture",
  residues: ["kernel-enforced network isolation not implemented", "production sandbox ownership unselected", "general multi-turn controller not implemented", "four-variant benchmark not run by this validator", "general reliability not established"],
  authority_effect: "none",
  claim_limit: receipt.claim_limit,
};
writeFileSync(resolve(packageRoot, "evidence/conformance-l2-candidate.json"), `${JSON.stringify(conformance, null, 2)}\n`);
process.stdout.write(`${JSON.stringify(receipt, null, 2)}\n`);
process.exitCode = errors.length === 0 ? 0 : 1;
