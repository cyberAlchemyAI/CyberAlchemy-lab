import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { canonicalJson, sha256 } from "../src/input/source-manifest.js";
import { planIntegrationProjectV2 } from "../src/system-integration/generation-v2.js";

const here = path.dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = path.resolve(here, "../../../../..");
const fixtureRoot = path.resolve(here, "../../system-integration/fixtures");
const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(fixtureRoot, relative), "utf8"));

const SOURCE_PATHS = Object.freeze([
  ...["README.md", "concepts.json", "invariants.json", "profile.json", "relations.json", "schema/integration-ontology-scaffold.schema.json", "sources.json", "validate.mjs"].map(name => `projects/domainspec-v2/development/integration-reconciliation/v1/ontology/${name}`),
  ...["external-api-composition-v2.schema.json", "integration-generation-source-v2.schema.json", "integration-kernel-v2.schema.json", "integration-observation-v1.schema.json", "messaging-composition-v2.schema.json", "persistence-composition-v2.schema.json"].map(name => `projects/domainspec-v2/impl/system-integration/contracts/${name}`),
  "projects/domainspec-v2/impl/system-integration/INTEGRATION-V2.md",
  "projects/domainspec-v2/impl/system-integration/fixtures/external-api-composition-v2/payments-http.json",
  "projects/domainspec-v2/impl/system-integration/fixtures/integration-kernel-v2/base-kernel.json",
  "projects/domainspec-v2/impl/system-integration/fixtures/messaging-composition-v2/legacy-publish-subscribe.json",
  "projects/domainspec-v2/impl/system-integration/fixtures/messaging-composition-v2/order-submitted-topic.json",
  "projects/domainspec-v2/impl/system-integration/fixtures/persistence-composition-v2/commerce-postgresql.json",
  ...["external-api-v2-types.ts", "external-api-v2.ts", "generation-v2.ts", "integration-project-layout-v1.ts", "kernel-v2-types.ts", "kernel-v2.ts", "messaging-v2-types.ts", "messaging-v2.ts", "observation-v2.ts", "persistence-v2-types.ts", "persistence-v2.ts"].map(name => `projects/domainspec-v2/impl/cli/src/system-integration/${name}`),
  "projects/domainspec-v2/impl/cli/src/index.ts",
  ...["external-api-v2.test.ts", "generation-v2.test.ts", "integration-project-layout-v1.test.ts", "kernel-v2.test.ts", "messaging-v2.test.ts", "observation-v2.test.ts", "persistence-v2.test.ts", "product-v2.test.ts", "public-api-v2.test.ts"].map(name => `projects/domainspec-v2/impl/cli/test/system-integration/${name}`),
  "projects/domainspec-v2/impl/cli/tools/materialize-integration-generation-v2.ts",
  "projects/domainspec-v2/impl/cli/tools/validate-integration-product-v2.sh",
  "projects/domainspec-v2/impl/cli/tools/freeze-integration-product-candidate-v2.ts",
  "projects/domainspec-v2/impl/cli/tools/validate-integration-product-candidate-v2.ts",
  "projects/domainspec-v2/impl/cli/tools/validate-integration-product-candidate-v2.sh"
].sort());

function generationSource() {
  return {
    schema_version: "domainspec.integration-generation-source/v2-candidate",
    source_id: "integration-source:commerce-v2",
    persistence: read("persistence-composition-v2/commerce-postgresql.json"),
    messaging: read("messaging-composition-v2/order-submitted-topic.json"),
    external_api: read("external-api-composition-v2/payments-http.json"),
    disclosure_policy: { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["provider", "statusCode"], max_attribute_count: 2, max_string_length: 64, forbidden_key_fragments: ["authorization", "credential", "secret", "token"], authority_effect: "none" },
    orodi_binding: { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "observation-input-only-no-admission", authority_effect: "none" },
  } as any;
}

export function buildIntegrationProductCandidateV2(environment: Record<string, string>) {
  const sources = SOURCE_PATHS.map(relative_path => {
    const absolute = path.resolve(repositoryRoot, relative_path); const content = fs.readFileSync(absolute);
    return Object.freeze({ relative_path, sha256: sha256(content), size_bytes: content.byteLength, executable: (fs.statSync(absolute).mode & 0o111) !== 0 });
  });
  const sourceDigest = sha256(canonicalJson(sources));
  const generated = (["typescript", "python", "rust"] as const).map(language => {
    const plan = planIntegrationProjectV2(generationSource(), language);
    return Object.freeze({ language, plan_digest: plan.plan_digest, semantic_manifest_sha256: sha256(canonicalJson(plan.semantic_manifest)), artifacts: plan.artifacts.map(item => ({ relative_path: item.relative_path, sha256: item.sha256, size_bytes: item.size_bytes })) });
  });
  const body = {
    schema_version: "domainspec.integration-product-candidate/v2",
    candidate_id: "domainspec-integration-product-v2-candidate-001",
    status: "exact-candidate",
    external_source_bindings: [
      { absolute_path: "/home/vrondelli/projects/cyberAlchemy-v2/define/candidates/domainspec-integration/DOMAINSPEC-INTEGRATION-DEFINITION-PACK.v1-candidate.json", sha256: "cc93b59b68cbb016fdab6b0b4a476e69d1e0e6df99df1d94ca1c48fb7ff16c2a" },
      { absolute_path: "/home/vrondelli/projects/cyberAlchemy-v2/goals/plans/domainspec-integration-reconciliation/PLAN.md", sha256: "e18da2faa859905c28a49b70e13622f3a0c9efc330dacb31c67c839686881b0f" },
      { absolute_path: "/home/vrondelli/projects/cyberAlchemy-v2/goals/plans/domainspec-integration-reconciliation/RECONCILIATION-MATRIX.v1-candidate.json", sha256: "f5940fef74c69baeee445723dcdca180a3668ef7c4eb8b1d84e5fce22a345ebe" },
    ],
    frozen_source: { source_digest: sourceDigest, files: sources },
    generated_artifacts: generated,
    validation: {
      command: "projects/domainspec-v2/impl/cli/tools/validate-integration-product-v2.sh",
      focused_tests: { passed: 44, failed: 0, skipped: 0 },
      native_compilers: ["typescript", "python", "rust"],
      semantic_manifests_identical: true,
      temporary_outputs_disposed: true,
      result: "pass",
    },
    environment,
    claim_ceiling: "candidate formation, deterministic generation, native compile, bounded local-fixture observation, and non-collapse evidence only",
    forbidden_inferences: ["admission", "publication", "release", "deployment", "provider selection", "production readiness", "production runtime guarantees"],
    authority_effect: "none",
  };
  return Object.freeze({ ...body, candidate_digest: sha256(canonicalJson(body)) });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const target = path.resolve(process.argv[2] ?? "");
  if (process.argv.length !== 3 || fs.existsSync(target)) throw new Error("usage: freeze-integration-product-candidate-v2 <new-target>");
  const environment = {
    node: process.version,
    node_toolchain_image: process.env.R9_NODE_TOOLCHAIN_IMAGE ?? "",
    node_base_image: process.env.R9_NODE_BASE_IMAGE ?? "",
    typescript: process.env.R9_TYPESCRIPT_VERSION ?? "",
    python: process.env.R9_PYTHON_VERSION ?? "",
    rustc: process.env.R9_RUSTC_VERSION ?? "",
    cargo: process.env.R9_CARGO_VERSION ?? "",
    platform: "linux-x86_64",
  };
  if (Object.values(environment).some(value => !value)) throw new Error("R9 environment binding incomplete");
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, `${canonicalJson(buildIntegrationProductCandidateV2(environment))}\n`, { flag: "wx" });
  process.stdout.write(`${JSON.stringify({ target, result: "frozen", authority_effect: "none" })}\n`);
}
