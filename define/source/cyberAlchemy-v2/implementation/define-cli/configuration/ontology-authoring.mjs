import {createModulePort} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {createBusinessOntologyStageAdapter} from "../adapters/business-ontology/index.mjs";
import {createProductOntologyStageAdapter, createDefinitionPackPrerequisiteReceipt} from "../adapters/product-ontology/index.mjs";
import {createSystemOntologyStageAdapter} from "../adapters/system-ontology/index.mjs";
import {createOntologyStagePort, ontologyStageOutputValidators} from "../packages/ontology-stage-port/index.mjs";

export function createConfiguredOntologyAuthoring({include_system = true} = {}) {
  const product = createProductOntologyStageAdapter();
  const business = createBusinessOntologyStageAdapter();
  const system = createSystemOntologyStageAdapter();
  const selected = [product, business, ...(include_system ? [system] : [])];
  const adapters = selected.map((item) => item.adapter);
  const descriptors = [product.definition_pack_descriptor, product.descriptor, business.descriptor, ...(include_system ? [system.descriptor] : [])];
  const modulePort = createModulePort({adapters, output_validators: ontologyStageOutputValidators});
  const stagePort = createOntologyStagePort({module_port: modulePort, descriptors});
  const definition_pack_receipt = createDefinitionPackPrerequisiteReceipt({stage_graph_digest: stagePort.stage_graph_digest, module_set_digest: stagePort.module_set_digest, manifest_digest: product.adapter.manifest.manifest_digest});
  return Object.freeze({stage_port: stagePort, definition_pack_receipt, adapters: Object.freeze(selected), authority_effect: "none"});
}
