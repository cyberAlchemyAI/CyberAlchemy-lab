import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  INTEGRATION_PROJECT_LAYOUT_V1,
  IntegrationGenerationError,
  compileExternalApiCompositionV2,
  compileIntegrationKernelV2,
  compileMessagingCompositionV2,
  compilePersistenceCompositionV2,
  planIntegrationProjectV2,
  projectIntegrationObservation,
  type IntegrationGenerationSourceV2,
} from "../../src/index.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(here, "../../../system-integration/fixtures");
const read = (relative: string) => JSON.parse(fs.readFileSync(path.join(fixtureRoot, relative), "utf8"));

const source: IntegrationGenerationSourceV2 = {
  schema_version: "domainspec.integration-generation-source/v2-candidate",
  source_id: "integration-source:public-commerce-v2",
  persistence: read("persistence-composition-v2/commerce-postgresql.json"),
  messaging: read("messaging-composition-v2/order-submitted-topic.json"),
  external_api: read("external-api-composition-v2/payments-http.json"),
  disclosure_policy: { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["provider", "statusCode"], max_attribute_count: 2, max_string_length: 64, forbidden_key_fragments: ["authorization", "credential", "secret", "token"], authority_effect: "none" },
  orodi_binding: { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "observation-input-only-no-admission", authority_effect: "none" },
};

test("R9 root package exports the complete integration candidate surface", () => {
  assert.equal(typeof compileIntegrationKernelV2, "function");
  assert.equal(typeof compilePersistenceCompositionV2, "function");
  assert.equal(typeof compileMessagingCompositionV2, "function");
  assert.equal(typeof compileExternalApiCompositionV2, "function");
  assert.equal(typeof projectIntegrationObservation, "function");
  assert.equal(INTEGRATION_PROJECT_LAYOUT_V1.schema_version, "domainspec.integration-project-layout/v1-candidate");
  assert.equal(planIntegrationProjectV2(source, "typescript").language, "typescript");
});

test("R9 public planner fails closed at its aggregate boundary", () => {
  assert.throws(() => planIntegrationProjectV2({ ...source, extra: true } as never, "typescript"), IntegrationGenerationError);
});
