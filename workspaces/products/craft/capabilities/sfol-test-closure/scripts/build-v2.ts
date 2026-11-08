import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { compileMintedProject } from "../../../impl/tools/minted-project/compiler.ts";

const capabilityRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = resolve(capabilityRoot, "domainspec-v2");
const generatedRoot = resolve(capabilityRoot, "generated-v2");
const repositoryProjectsRoot = resolve(capabilityRoot, "../..");
const profilePath = resolve(sourceRoot, "development-profile.json");
const implementationMapPath = resolve(capabilityRoot, "implementation-map.v2-candidate.json");

function sha256(value: string | Buffer): string { return createHash("sha256").update(value).digest("hex"); }
function stable(value: unknown): string { return `${JSON.stringify(value, null, 2)}\n`; }
function json(path: string): any { return JSON.parse(readFileSync(path, "utf8")); }
function write(path: string, value: unknown): string {
  const bytes = stable(value);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, bytes);
  return sha256(bytes);
}

const options = {
  developmentProfileRegistry: {
    path: profilePath,
    handle: "sfol-test-closure-v2-development-explicit-v0.2",
  },
};
const first = compileMintedProject(sourceRoot, options);
const second = compileMintedProject(sourceRoot, options);
if (first.graphBytes !== second.graphBytes || first.sourceManifestBytes !== second.sourceManifestBytes) {
  throw new Error("SFOL_V2_NONDETERMINISTIC_COMPILE");
}
const implementationMap = json(implementationMapPath);
const graphNodeIds = new Set(first.graph.nodes.map(({ node_id }) => node_id));
const components = implementationMap.components.map((component: any) => {
  for (const nodeId of component.operation_node_ids) {
    if (!graphNodeIds.has(nodeId)) throw new Error(`SFOL_V2_IMPLEMENTATION_OPERATION_MISSING:${nodeId}`);
  }
  const bindings = component.implementation_paths.map((path: string) => ({
    path,
    sha256: sha256(readFileSync(resolve(repositoryProjectsRoot, path))),
  }));
  return { ...component, bindings };
}).sort((left: any, right: any) => left.component_id.localeCompare(right.component_id));

const graphDigest = sha256(first.graphBytes);
const manifestDigest = sha256(first.sourceManifestBytes);
const systemOntology = {
  schema_version: "domainspec-compiled-system-ontology/v1",
  ontology_id: "DSV2-SYSTEM-ONTOLOGY-SFOL-TEST-CLOSURE-V2",
  authority: "generated-candidate-read-model",
  source_graph_digest: graphDigest,
  source_manifest_digest: manifestDigest,
  development_profile_digest: sha256File(profilePath),
  implementation_map_digest: sha256File(implementationMapPath),
  components,
  admission: "not-granted",
};
const systemOntologyDigest = write(resolve(generatedRoot, "system-ontology.json"), systemOntology);
writeFileSync(resolve(generatedRoot, "compiled-graph.json"), first.graphBytes);
writeFileSync(resolve(generatedRoot, "source-manifest.json"), first.sourceManifestBytes);
const buildReceipt = {
  schema_version: "domainspec-sfol-test-closure-build-receipt/v2",
  result: "pass",
  source_epoch: "sfol-test-closure-v2",
  compile_runs: 2,
  byte_identical: true,
  source_set_digest: first.graph.source_set_digest,
  compiled_graph_sha256: graphDigest,
  source_manifest_sha256: manifestDigest,
  system_ontology_sha256: systemOntologyDigest,
  development_profile_sha256: sha256File(profilePath),
  implementation_map_sha256: sha256File(implementationMapPath),
  authority_effect: "none",
};
const buildReceiptDigest = write(resolve(generatedRoot, "build-receipt.json"), buildReceipt);
process.stdout.write(`${JSON.stringify({ result: "pass", source_set_digest: first.graph.source_set_digest, compiled_graph_sha256: graphDigest, source_manifest_sha256: manifestDigest, system_ontology_sha256: systemOntologyDigest, build_receipt_sha256: buildReceiptDigest, nodes: first.graph.nodes.length, edges: first.graph.edges.length, generated_root: "generated-v2", authority_effect: "none" }, null, 2)}\n`);

function sha256File(path: string): string { return sha256(readFileSync(path)); }
