#!/usr/bin/env -S node --import tsx
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  buildMintedProjectViews,
  verifyMintedProjectBuild,
} from "../../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/views.ts";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(scriptDir, "..");
const projectRoot = resolve(packageRoot, "domainspec");
const developmentProfilePath = resolve(projectRoot, "development-profile.json");
const developmentProfileHandle = "ontology-lifecycle-development-explicit-v0.1";

function sha256(value: string | Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function bytes(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

const artifacts = buildMintedProjectViews(projectRoot, {
  developmentProfileRegistry: {
    path: developmentProfilePath,
    handle: developmentProfileHandle,
  },
});
const verification = verifyMintedProjectBuild(projectRoot, artifacts);
if (verification.status !== "pass") {
  process.stdout.write(bytes({ status: "BLOCK", codes: verification.codes, authority_effect: "none" }));
  process.exit(1);
}

const generated: Record<string, string> = {
  "graph.json": artifacts.graphBytes,
  "source-manifest.json": artifacts.sourceManifestBytes,
  "SPEC.md": artifacts.markdownBytes,
  "markdown-view.json": artifacts.markdownViewBytes,
  "build-receipt.json": artifacts.buildReceiptBytes,
};
const graphDigest = sha256(artifacts.graphBytes);
const buildReceiptDigest = sha256(artifacts.buildReceiptBytes);
const systemNodes = bytes({
  schema_version: "cal-ontology-lifecycle-system-nodes/v1-candidate",
  source_graph_ref: "../domainspec/.domainspec/generated/graph.json",
  source_graph_digest: graphDigest,
  nodes: artifacts.graph.nodes.map((node) => ({ ...node, authority_effect: "none" })),
});
const systemRelations = bytes({
  schema_version: "cal-ontology-lifecycle-system-relations/v1-candidate",
  source_graph_ref: "../domainspec/.domainspec/generated/graph.json",
  source_graph_digest: graphDigest,
  relations: artifacts.graph.edges.map((edge) => ({ ...edge, authority_effect: "none" })),
});
const compilerPath = fileURLToPath(import.meta.url);
const systemProfile = bytes({
  schema_version: "cal-ontology-lifecycle-system-profile/v1-candidate",
  ontology_id: "cal.ontology-lifecycle.system-runtime.v2-candidate",
  ontology_type: "system-runtime",
  branch: "system",
  status: "candidate-unadmitted",
  product_capability_ref: "../product-capability.json",
  business_ontology_ref: "../business-ontology.json",
  definition_selection_ref: "../../docs/decisions/0006-governed-node-definition-selection/decision.json",
  lifecycle_selection_ref: "../../docs/decisions/0007-ontology-lifecycle-state-vocabulary/decision.json",
  project_ref: "CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE",
  goal_ref: "CA2-GOAL-CYBERALCHEMY-LAB-EVENT-SOURCED-ONTOLOGY",
  context_ref: "CAL-CONTEXT-ONTOLOGY-LIFECYCLE",
  domainspec_project_ref: "../domainspec/project.json",
  compiled_graph_ref: "../domainspec/.domainspec/generated/graph.json",
  compiled_graph_digest: graphDigest,
  source_set_digest: artifacts.graph.source_set_digest,
  domainspec_build_receipt_ref: "../domainspec/.domainspec/generated/build-receipt.json",
  domainspec_build_receipt_digest: buildReceiptDigest,
  compiler_ref: "../scripts/compile-domainspec.ts",
  compiler_digest: sha256(readFileSync(compilerPath)),
  upstream_compiler_ref: "../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/compiler.ts",
  upstream_compiler_digest: sha256(readFileSync(resolve(scriptDir, "../../../domainspec-core/projects/domainspec-v2/impl/tools/minted-project/compiler.ts"))),
  domainspec_profile: "ontology-lifecycle-development@0.1",
  domainspec_profile_status: "development-only",
  implementation_ref: "../runtime/Cargo.toml",
  construction_binding_state: "not_evaluable_until_profile_admission_and_governed_runtime_binding",
  implementation_state: "predecessor-blocked-not-evaluated",
  authority_effect: "none",
  claim_ceiling: "Deterministic DomainSpec development-profile graph and system projection only; no profile admission, ontology admission, implementation conformance, publication, release, or deployment."
});

const outputs: Record<string, string> = {
  ...Object.fromEntries(Object.entries(generated).map(([name, value]) => [`domainspec/.domainspec/generated/${name}`, value])),
  "system-ontology/NODES.json": systemNodes,
  "system-ontology/RELATIONS.json": systemRelations,
  "system-ontology/PROFILE.json": systemProfile,
};

const checkOnly = process.argv.includes("--check");
const mismatches: string[] = [];
for (const [relativePath, content] of Object.entries(outputs)) {
  const target = resolve(packageRoot, relativePath);
  if (checkOnly) {
    try {
      if (readFileSync(target, "utf8") !== content) mismatches.push(relativePath);
    } catch {
      mismatches.push(relativePath);
    }
  } else {
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, content);
  }
}

const status = mismatches.length === 0 ? "PASS" : "BLOCK";
process.stdout.write(bytes({
  status,
  mode: checkOnly ? "check" : "write",
  outputs: Object.keys(outputs).sort(),
  mismatches,
  graph_digest: graphDigest,
  source_set_digest: artifacts.graph.source_set_digest,
  domainspec_profile: "ontology-lifecycle-development@0.1",
  domainspec_profile_status: "development-only",
  authority_effect: "none",
  claim_ceiling: "Candidate deterministic build only; final semantic verification and every admission/effect remain separate."
}));
process.exit(status === "PASS" ? 0 : 1);
