import {
  digestModuleValue,
  sealModuleManifest,
} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {
  STAGE_DESCRIPTOR_SCHEMA,
  STAGE_PROTOCOLS,
} from "./index.mjs";

export const SYNTHETIC_STAGE_ID = "fixture-product-ontology";

const capabilities = Object.freeze({
  describe: "define.ontology.fixture-product.describe/v1",
  next_question: "define.ontology.fixture-product.next-question/v1",
  evaluate: "define.ontology.fixture-product.evaluate/v1",
  materialize: "define.ontology.fixture-product.materialize/v1",
  validate: "define.ontology.fixture-product.validate/v1",
});

function answer(input) {
  return input.responses?.findLast?.((item) => ["answer", "correction"].includes(item.response_kind)) ?? null;
}

export function createSyntheticOntologyStageAdapter() {
  const manifest = sealModuleManifest({
    schema_version: "are.module-manifest/v1",
    module_id: "cav2-define-fixture-product-authoring",
    version: "1-candidate",
    adapter_protocol: "are.module-adapter/v1",
    capabilities: Object.entries(capabilities).map(([operation, capability_id]) => ({
      capability_id,
      input_protocol: STAGE_PROTOCOLS[operation].input,
      output_protocol: STAGE_PROTOCOLS[operation].output,
    })),
    required_permissions: [],
    side_effects: false,
    authority_effect: "none",
  });
  const descriptor = Object.freeze({
    schema_version: STAGE_DESCRIPTOR_SCHEMA,
    stage_id: SYNTHETIC_STAGE_ID,
    ontology_type: "fixture-product",
    module_id: manifest.module_id,
    module_version: manifest.version,
    manifest_digest: manifest.manifest_digest,
    prerequisite_stage_ids: [],
    capabilities,
    alch_entrypoints: ["StageDependency", "StageResponse", "StageReadiness", "StageHandoff"],
    authority_effect: "none",
  });
  const adapter = Object.freeze({
    manifest,
    invoke(invocation) {
      const input = invocation.input;
      if (input.stage_id !== SYNTHETIC_STAGE_ID) throw new TypeError("Synthetic stage identity mismatch.");
      if (invocation.capability_id === capabilities.describe) {
        return {
          schema_version: STAGE_PROTOCOLS.describe.output,
          stage_id: SYNTHETIC_STAGE_ID,
          ontology_type: "fixture-product",
          label: "Fixture Product Ontology",
          purpose: "Prove that ontology-specific questions and materialization stay outside Define core.",
          output_artifact_kind: "fixture-product-ontology-candidate",
          owner_ref: "fixture-product-owner",
          authority_effect: "none",
        };
      }
      if (invocation.capability_id === capabilities.next_question) {
        const complete = answer(input) !== null;
        return {
          schema_version: STAGE_PROTOCOLS.next_question.output,
          stage_id: SYNTHETIC_STAGE_ID,
          complete,
          question: complete ? null : {
            question_id: "fixture-product-purpose",
            prompt: "What product meaning should this ontology preserve?",
            answer_kind: "product-purpose",
            owner_ref: "fixture-product-owner",
          },
          authority_effect: "none",
        };
      }
      if (invocation.capability_id === capabilities.evaluate) {
        const selected = answer(input);
        const checks = {
          semantic_grounding: selected?.evidence?.semantic_grounding === true,
          non_collapse: selected?.evidence?.non_collapse === true,
          orthogonality: selected?.evidence?.orthogonality === true,
        };
        return {
          schema_version: STAGE_PROTOCOLS.evaluate.output,
          stage_id: SYNTHETIC_STAGE_ID,
          interaction_complete: selected !== null,
          checks,
          reason_codes: Object.entries(checks).filter(([, passed]) => !passed).map(([check]) => `fixture.${check.replaceAll("_", "-")}-required`).sort(),
          authority_effect: "none",
        };
      }
      if (invocation.capability_id === capabilities.materialize) {
        const selected = answer(input);
        if (!selected) throw new TypeError("Synthetic answer required.");
        const candidate = {
          schema_version: "cav2.fixture-product-ontology-candidate/v1",
          ontology_type: "fixture-product",
          product_purpose: selected.response,
          status: "candidate",
          authority_effect: "none",
        };
        return {
          schema_version: STAGE_PROTOCOLS.materialize.output,
          stage_id: SYNTHETIC_STAGE_ID,
          candidate,
          candidate_digest: digestModuleValue(candidate),
          authority_effect: "none",
        };
      }
      if (invocation.capability_id === capabilities.validate) {
        const candidate = input.candidate;
        const valid = candidate?.schema_version === "cav2.fixture-product-ontology-candidate/v1"
          && candidate?.ontology_type === "fixture-product"
          && typeof candidate?.product_purpose === "string" && candidate.product_purpose.length > 0
          && candidate?.status === "candidate" && candidate?.authority_effect === "none";
        return {
          schema_version: STAGE_PROTOCOLS.validate.output,
          stage_id: SYNTHETIC_STAGE_ID,
          valid,
          reason_codes: valid ? [] : ["fixture.candidate-invalid"],
          authority_effect: "none",
        };
      }
      throw new TypeError("Synthetic capability is unsupported.");
    },
  });
  return Object.freeze({adapter, descriptor});
}

