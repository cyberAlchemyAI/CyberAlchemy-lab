import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { planIntegrationProjectV2 } from "../src/system-integration/generation-v2.js";
import type { IntegrationGenerationLanguage } from "../src/system-integration/integration-project-layout-v1.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(here, "../../system-integration/fixtures");
const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(fixtureRoot, relative), "utf8"));
const language = process.argv[2] as IntegrationGenerationLanguage;
const target = path.resolve(process.argv[3] ?? "");
if (!(["typescript", "python", "rust"] as const).includes(language) || process.argv.length !== 4 || fs.existsSync(target)) throw new Error("usage: materialize-integration-generation-v2 <typescript|python|rust> <new-target>");

const source: any = {
  schema_version: "domainspec.integration-generation-source/v2-candidate",
  source_id: "integration-source:commerce-v2",
  persistence: read("persistence-composition-v2/commerce-postgresql.json"),
  messaging: read("messaging-composition-v2/order-submitted-topic.json"),
  external_api: read("external-api-composition-v2/payments-http.json"),
  disclosure_policy: { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["provider", "statusCode"], max_attribute_count: 2, max_string_length: 64, forbidden_key_fragments: ["authorization", "credential", "secret", "token"], authority_effect: "none" },
  orodi_binding: { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "observation-input-only-no-admission", authority_effect: "none" },
};

const plan = planIntegrationProjectV2(source, language);
fs.mkdirSync(target, { recursive: false });
for (const artifact of plan.artifacts) {
  const destination = path.join(target, artifact.relative_path);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, artifact.content);
}
process.stdout.write(`${JSON.stringify({ language, target, artifacts: plan.artifacts.length, plan_digest: plan.plan_digest, authority_effect: "none" })}\n`);
