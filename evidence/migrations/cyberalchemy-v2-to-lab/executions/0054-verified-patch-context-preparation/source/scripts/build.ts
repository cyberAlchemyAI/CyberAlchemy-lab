import {createHash} from "node:crypto";
import {mkdirSync, readFileSync, writeFileSync} from "node:fs";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {buildMintedProjectViews} from "../../../../../../projects/domainspec-v2/impl/tools/minted-project/views";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(scriptDir, "..");
const repositoryRoot = resolve(packageRoot, "../../../../..");
const projectRoot = resolve(packageRoot, "domainspec");
const generatedRoot = resolve(projectRoot, "generated");

function sha256(value: string | Buffer): string { return createHash("sha256").update(value).digest("hex"); }
function bytes(value: unknown): string { return `${JSON.stringify(value, null, 2)}\n`; }

function verifySources() {
  const registry = JSON.parse(readFileSync(resolve(packageRoot, "sources.json"), "utf8"));
  for (const source of registry.sources) {
    const observed = sha256(readFileSync(resolve(repositoryRoot, source.path)));
    if (observed !== source.sha256) throw new Error(`SOURCE_BINDING_DRIFT:${source.id}:${observed}`);
  }
  return registry.sources;
}

function build() {
  const sources = verifySources();
  const options = {developmentProfileRegistry: {path: resolve(projectRoot, "development-profile.json"), handle: "are-coding-agent-runtime-development-explicit-v0.1"}};
  const first = buildMintedProjectViews(projectRoot, options);
  const second = buildMintedProjectViews(projectRoot, options);
  for (const key of ["graphBytes", "sourceManifestBytes", "markdownBytes", "markdownViewBytes", "buildReceiptBytes"] as const) if (first[key] !== second[key]) throw new Error(`NON_DETERMINISTIC_DOMAINSPEC_BUILD:${key}`);

  const implementationRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/coding-agent-runtime");
  const implementationFiles = ["index.mjs", "controller.mjs", "prompt.mjs", "model-transport.mjs", "live-session.mjs", "verifier.mjs", "schemas/next-action-candidate.schema.json", "bin/demo.mjs", "bin/live-demo.mjs", "scripts/live-gateway-canary.mjs", "test/coding-agent-runtime.test.mjs", "test/model-driven-turn.test.mjs", "test/live-session.test.mjs", "package.json"];
  const systemOntology = {
    schema_version: "cav2-are-coding-agent-runtime-system-ontology/v1",
    ontology_id: "CA2-ARE-CODING-AGENT-RUNTIME-SYSTEM-ONTOLOGY",
    authority: "generated-system-ontology-read-model",
    source_project_id: first.graph.project_id,
    source_set_digest: first.graph.source_set_digest,
    source_graph_digest: sha256(first.graphBytes),
    construction_inputs: sources,
    nodes: first.graph.nodes,
    edges: first.graph.edges,
    implementation_contract: {
      project_ref: "CA2-PROJECT-AGENT-REASONING-ENGINE",
      product_capability_ref: "CA2-CAP-PRODUCE-VERIFIED-PATCH-CANDIDATE",
      implementation_files: implementationFiles.map((path) => ({path: `cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/coding-agent-runtime/${path}`, sha256: sha256(readFileSync(resolve(implementationRoot, path)))})),
      live_model_transport: "session-entrypoint-implemented-not-live-validated",
      live_proxy_integration: true,
      production_sandbox: false,
      authority_effect: "none"
    },
    authority_effect: "none",
    enforcement_effect: "fixture-local-only",
    claim_limit: "Deterministic L2 fixture and live-session-entrypoint read model only; no adoption, admission, live-model conformance, production sandbox, publication, deployment, or external effect."
  };
  const systemOntologyBytes = bytes(systemOntology);
  const receipt = {schema_version: "cav2-are-coding-agent-runtime-system-ontology-projection/v1", status: "candidate", deterministic_runs: 2, equal_graph_bytes: true, equal_system_ontology_bytes: true, source_graph_digest: sha256(first.graphBytes), system_ontology_digest: sha256(systemOntologyBytes), profile_id: first.buildReceipt.language.profile_id, profile_version: first.buildReceipt.language.profile_version, profile_digest: first.buildReceipt.language.profile_digest, profile_release_admission: "not-granted", implementation_level: "L2-live-session-entrypoint", authority_effect: "none", enforcement_effect: "fixture-local-only"};
  return {"graph.json": first.graphBytes, "source-manifest.json": first.sourceManifestBytes, "SPEC.md": first.markdownBytes, "markdown-view.json": first.markdownViewBytes, "build-receipt.json": first.buildReceiptBytes, "system-ontology.json": systemOntologyBytes, "system-ontology-receipt.json": bytes(receipt)};
}

const artifacts = build();
if (process.argv.includes("--emit-json")) process.stdout.write(bytes(artifacts));
else {
  mkdirSync(generatedRoot, {recursive: true});
  for (const [name, content] of Object.entries(artifacts)) writeFileSync(resolve(generatedRoot, name), content, "utf8");
  process.stdout.write(`built=${Object.keys(artifacts).length}\n`);
}
