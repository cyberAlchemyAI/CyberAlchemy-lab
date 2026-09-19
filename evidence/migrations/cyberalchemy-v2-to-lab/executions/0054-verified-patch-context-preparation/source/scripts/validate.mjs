import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(scriptDir, "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const implementationRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/coding-agent-runtime");
const rpcClientRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/codex-app-server-wrapper");
const generatedRoot = resolve(packageRoot, "domainspec/generated");
const node = "/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node";
function sha256(value) { return createHash("sha256").update(value).digest("hex"); }
function load(path) { return JSON.parse(readFileSync(path, "utf8")); }
function run(command, args, cwd) { return spawnSync(command, args, {cwd, encoding: "utf8", env: {...process.env, PATH: `${dirname(node)}:${process.env.PATH ?? ""}`}}); }
function file(path) { return {path: path.slice(repositoryRoot.length + 1).replaceAll("\\", "/"), sha256: sha256(readFileSync(path))}; }

const checks = [];
const errors = [];
const profile = load(resolve(packageRoot, "profile.json"));
const capability = load(resolve(packageRoot, "product-capability.json"));
const ontology = load(resolve(packageRoot, "business-ontology.json"));
const contract = load(resolve(packageRoot, "interface-contract.json"));
const productTestContract = load(resolve(packageRoot, "product-test-contract.json"));
const identityOk = profile.product_capability_ref === capability.capability_id && profile.business_ontology_ref === ontology.ontology_id && capability.output_contract_refs.includes(contract.contract_id) && [profile, capability, ontology, contract].every((item) => item.authority_effect === "none");
checks.push({check: "semantic-identity-closure", status: identityOk ? "PASS" : "BLOCK"});
if (!identityOk) errors.push("semantic identity closure failed");

const sourceDrift = [];
for (const source of load(resolve(packageRoot, "sources.json")).sources) {
  const path = resolve(repositoryRoot, source.path);
  const observed = sha256(readFileSync(path));
  if (observed !== source.sha256) sourceDrift.push({id: source.id, expected: source.sha256, observed});
}
checks.push({check: "selected-source-digests", status: sourceDrift.length === 0 ? "PASS" : "BLOCK", drift: sourceDrift});
if (sourceDrift.length) errors.push("selected source drift");

const domainspecProject = resolve(repositoryRoot, "projects/domainspec-v2/impl");
const buildArgs = ["--import", "tsx", "../../../cyberAlchemy-v2/development/agent-reasoning-engine/codex-integration/coding-agent-runtime/scripts/build.ts", "--emit-json"];
const first = run(node, buildArgs, domainspecProject);
const second = run(node, buildArgs, domainspecProject);
const deterministic = first.status === 0 && second.status === 0 && first.stdout === second.stdout;
checks.push({check: "domainspec-two-run-determinism", status: deterministic ? "PASS" : "BLOCK"});
if (!deterministic) errors.push(`DomainSpec build failed or drifted: ${first.stderr} ${second.stderr}`);
let generatedParity = false;
if (deterministic) {
  const artifacts = JSON.parse(first.stdout);
  generatedParity = Object.entries(artifacts).every(([name, content]) => readFileSync(resolve(generatedRoot, name), "utf8") === content);
}
checks.push({check: "generated-artifact-parity", status: generatedParity ? "PASS" : "BLOCK"});
if (!generatedParity) errors.push("generated artifacts do not match source");

const implementationFiles = ["index.mjs", "controller.mjs", "prompt.mjs", "model-transport.mjs", "live-session.mjs", "verifier.mjs", "schemas/next-action-candidate.schema.json", "bin/demo.mjs", "bin/live-demo.mjs", "scripts/live-gateway-canary.mjs", "test/coding-agent-runtime.test.mjs", "test/model-driven-turn.test.mjs", "test/live-session.test.mjs", "package.json"].map((path) => file(resolve(implementationRoot, path)));
const generatedFiles = ["graph.json", "system-ontology.json", "build-receipt.json", "system-ontology-receipt.json"].map((path) => file(resolve(generatedRoot, path)));
const candidate = {
  schema_version: "cav2-testable-product-candidate/v1",
  candidate_id: "ARE-CAR-L2-TESTABLE-CANDIDATE-001",
  status: deterministic && generatedParity ? "testable" : "not_evaluable",
  product_capability: file(resolve(packageRoot, "product-capability.json")),
  business_ontology: file(resolve(packageRoot, "business-ontology.json")),
  domainspec_source: [file(resolve(packageRoot, "domainspec/project.json")), file(resolve(packageRoot, "domainspec/feature.json")), ...["coding-request.json", "live-model-session.json", "model-turn-output.json", "next-action-candidate.json", "patch-candidate.json", "safe-effect-invariant.json"].map((path) => file(resolve(packageRoot, "domainspec/nodes", path)))],
  compiled_system: generatedFiles,
  implementation: implementationFiles,
  runtime_dependencies: [file(resolve(rpcClientRoot, "src/rpc-client.mjs")), file(resolve(rpcClientRoot, "bin/are-codex-app-server.mjs")), file(resolve(rpcClientRoot, "profiles/repository-v1.json"))],
  product_test_contract: file(resolve(packageRoot, "product-test-contract.json")),
  product_approval: null,
  authority_effect: "none"
};
writeFileSync(resolve(packageRoot, "testable-product-candidate.json"), `${JSON.stringify(candidate, null, 2)}\n`);

const tests = run(node, ["--test", "test/*.test.mjs"], implementationRoot);
const codingTestCount = Number(/(?:ℹ|#)\s*tests\s+(\d+)/u.exec(tests.stdout)?.[1] ?? 0);
checks.push({check: "coding-agent-focused-tests", status: tests.status === 0 ? "PASS" : "BLOCK"});
if (tests.status !== 0) errors.push(`focused tests failed: ${tests.stdout} ${tests.stderr}`);
const rpcTests = run(node, ["--test", "test/rpc-client.test.mjs"], rpcClientRoot);
const rpcTestCount = Number(/(?:ℹ|#)\s*tests\s+(\d+)/u.exec(rpcTests.stdout)?.[1] ?? 0);
checks.push({check: "rpc-client-focused-tests", status: rpcTests.status === 0 ? "PASS" : "BLOCK"});
if (rpcTests.status !== 0) errors.push(`RPC client tests failed: ${rpcTests.stdout} ${rpcTests.stderr}`);
const demo = run(node, ["bin/demo.mjs", "--approve"], implementationRoot);
let demoReceipt = null;
try { demoReceipt = JSON.parse(demo.stdout); } catch {}
const demoOk = demo.status === 0 && demoReceipt?.status === "PATCH_CANDIDATE" && demoReceipt?.verification?.status === "PASS_BOUNDED";
checks.push({check: "approved-scripted-demo", status: demoOk ? "PASS" : "BLOCK"});
if (!demoOk) errors.push(`demo failed: ${demo.stdout} ${demo.stderr}`);

const receiptMaterial = {schema_version: "cav2-are-coding-agent-runtime-product-test/v1", validation_id: "ARE-CAR-L2-PRODUCT-TEST-001", candidate: file(resolve(packageRoot, "testable-product-candidate.json")), product_test_contract: file(resolve(packageRoot, "product-test-contract.json")), status: errors.length === 0 ? "PASS" : "BLOCK", implementation_level: "L2-live-session-entrypoint", checks, errors, test_counts: {coding_agent: tests.status === 0 ? codingTestCount : null, rpc_client: rpcTests.status === 0 ? rpcTestCount : null}, demo_status: demoReceipt?.status ?? null, live_model_transport: "session-entrypoint-implemented-not-live-validated", live_proxy_integration: true, live_canary_executed: false, product_approval: null, authority_request_eligible: false, production_sandbox: false, authority_effect: "none", claim_limit: "Current product-test evidence for one exact L2 candidate only; no product approval, architecture adoption, live-model conformance, production sandbox, publication, deployment, or external effect."};
const receipt = {...receiptMaterial, validation_digest: sha256(JSON.stringify(receiptMaterial))};
mkdirSync(resolve(packageRoot, "receipts"), {recursive: true});
writeFileSync(resolve(packageRoot, "receipts/l2-product-test.json"), `${JSON.stringify(receipt, null, 2)}\n`);
const binding = {
  schema_version: "cav2-d65-construction-binding/v1", binding_id: "CA2-D65-ARE-CODING-AGENT-RUNTIME-L2-001", binding_posture: "candidate-exact-byte-binding-not-accepted", implementation_level: "L2-live-session-entrypoint",
  project_ref: profile.project_ref, product_capability_ref: capability.capability_id, business_ontology_ref: ontology.ontology_id, domainspec_project_ref: profile.domainspec_project_ref, system_ontology_ref: "CA2-ARE-CODING-AGENT-RUNTIME-SYSTEM-ONTOLOGY",
  stages: [
    {stage: "prototype-definitions", status: "exact-source-bound", artifact: file(resolve(repositoryRoot, "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"))},
    {stage: "product-capability-and-business-prototypes", status: "prototyped", artifacts: [file(resolve(packageRoot, "product-capability.json")), file(resolve(packageRoot, "business-ontology.json"))]},
    {stage: "domainspec-v2-authored-prototype", status: "prototyped", artifacts: candidate.domainspec_source},
    {stage: "compiled-system-prototype", status: deterministic && generatedParity ? "prototyped" : "not_evaluable", artifacts: generatedFiles},
    {stage: "implementation-prototype", status: "prototyped", artifacts: implementationFiles},
    {stage: "testable-product-candidate", status: candidate.status, artifact: file(resolve(packageRoot, "testable-product-candidate.json"))},
    {stage: "product-test-evidence", status: errors.length === 0 ? "tested" : "test_failed", artifact: file(resolve(packageRoot, "receipts/l2-product-test.json"))},
    {stage: "product-approval", status: "absent", artifact: null},
    {stage: "post-approval-authority-decisions", status: "not_evaluable", artifacts: []}
  ],
  live_model_transport: "session-entrypoint-implemented-not-live-validated", live_proxy_integration: true, live_canary_executed: false, production_sandbox: false, authority_effect: "none", claim_limit: "Exact L2 fixture and live-session-entrypoint binding only; PASS does not establish live-model conformance, production conformance, architecture adoption, acceptance, publication, deployment, or external-effect authority."
};
writeFileSync(resolve(packageRoot, "construction-binding.json"), `${JSON.stringify(binding, null, 2)}\n`);
mkdirSync(resolve(packageRoot, "evidence"), {recursive: true});
const conformance = {schema_version: "cav2-are-coding-agent-runtime-conformance/v1", evidence_id: "ARE-CAR-L2-CONFORMANCE-001", result: errors.length === 0 ? "PASS_BOUNDED" : "not_evaluable", binding: file(resolve(packageRoot, "construction-binding.json")), validation: file(resolve(packageRoot, "receipts/l2-product-test.json")), scope: "one deterministic scripted-model fixture vertical plus a fake-client-validated live App Server lifecycle entrypoint", residues: ["live Codex App Server model turn intentionally left for user test", "kernel-enforced network isolation not implemented", "production sandbox ownership unselected", "multi-turn controller not implemented", "benchmark not approved or run"], authority_effect: "none", claim_limit: "L2 fixture and lifecycle-orchestration behavior only; no live-model, production conformance, security, performance, acceptance, publication, deployment, or external-effect claim."};
writeFileSync(resolve(packageRoot, "evidence/conformance-candidate.json"), `${JSON.stringify(conformance, null, 2)}\n`);
process.stdout.write(`${JSON.stringify(receipt, null, 2)}\n`);
process.exitCode = errors.length === 0 ? 0 : 1;
