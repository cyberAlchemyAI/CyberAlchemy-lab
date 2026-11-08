import type { FactoryNodeProviderV1 } from "../contracts/factory-node-provider-v1.js";
import { fail } from "../shared/canonical.js";
import { calculationParityV1Provider } from "./providers/calculation-parity-v1.js";
import { entityParityV1Provider, registeredTypeScriptEntityV1Provider } from
  "./providers/entity-parity-v1.js";
import { entityRelationsV1Provider } from
  "./providers/entity-relations-v1.js";
import { enumCompositionV1Provider } from "./providers/enum-composition-v1.js";
import { enumParityV1Provider } from "./providers/enum-parity-v1.js";
import { pythonCalculationV1Provider } from "./providers/python-calculation-v1.js";
import { pythonEnumV1Provider } from "./providers/python-enum-v1.js";
import { pythonEntityV1Provider } from "./providers/python-entity-v1.js";
import { pythonPolicyV1Provider } from "./providers/python-policy-v1.js";
import { pythonQueryV1Provider } from "./providers/python-query-v1.js";
import { pythonRuleV1Provider } from "./providers/python-rule-v1.js";
import { pythonValueObjectV1Provider } from
  "./providers/python-value-object-v1.js";
import { rustCalculationV1Provider } from "./providers/rust-calculation-v1.js";
import { rustEnumV1Provider } from "./providers/rust-enum-v1.js";
import { rustEntityV1Provider } from "./providers/rust-entity-v1.js";
import { rustPolicyV1Provider } from "./providers/rust-policy-v1.js";
import { rustQueryV1Provider } from "./providers/rust-query-v1.js";
import { rustRuleV1Provider } from "./providers/rust-rule-v1.js";
import { rustValueObjectV1Provider } from
  "./providers/rust-value-object-v1.js";
import { ruleParityV1Provider } from "./providers/rule-parity-v1.js";
import { policyParityV1Provider } from "./providers/policy-parity-v1.js";
import { queryParityV1Provider } from "./providers/query-parity-v1.js";
import { policySelectsStrategyV1Provider } from
  "./providers/policy-selects-strategy-v1.js";
import { referenceReadinessV1Provider } from "./providers/reference-readiness-v1.js";
import { typeScriptEnforcesV1Provider } from "./providers/typescript-enforces-v1.js";
import { typeScriptEnumOrderStatusV1Provider } from "./providers/typescript-enum-order-status-v1.js";
import { typeScriptEnumShipmentPriorityV1Provider } from "./providers/typescript-enum-shipment-priority-v1.js";
import { typeScriptEnumShipmentPrioritySemanticSliceV1Provider } from
  "./providers/typescript-enum-shipment-priority-semantic-slice-v1.js";
import { typeScriptCalculationV1Provider } from
  "./providers/typescript-calculation-v1.js";
import { typeScriptOperationV1Provider } from "./providers/typescript-operation-v1.js";
import { typeScriptPolicyV1Provider } from "./providers/typescript-policy-v1.js";
import { typeScriptQueryV1Provider } from "./providers/typescript-query-v1.js";
import { typeScriptRuleV1Provider } from "./providers/typescript-rule-v1.js";
import { registeredTypeScriptValueObjectV1Provider,
  valueObjectParityV1Provider } from
  "./providers/value-object-parity-v1.js";
import { valueObjectRelationsV1Provider } from
  "./providers/value-object-relations-v1.js";
import { typeScriptW3EffectsConnectionsV1Provider } from "./providers/typescript-w3-effects-connections-v1.js";
import { typeScriptW4OrchestrationLifecycleV1Provider } from "./providers/typescript-w4-orchestration-lifecycle-v1.js";

const providers = Object.freeze([
  typeScriptRuleV1Provider,
  pythonRuleV1Provider,
  rustRuleV1Provider,
  ruleParityV1Provider,
  referenceReadinessV1Provider,
  typeScriptOperationV1Provider,
  typeScriptEnforcesV1Provider,
  typeScriptEnumOrderStatusV1Provider,
  typeScriptEnumShipmentPriorityV1Provider,
  typeScriptEnumShipmentPrioritySemanticSliceV1Provider,
  pythonEnumV1Provider,
  rustEnumV1Provider,
  enumCompositionV1Provider,
  enumParityV1Provider,
  typeScriptCalculationV1Provider,
  pythonCalculationV1Provider,
  rustCalculationV1Provider,
  calculationParityV1Provider,
  typeScriptPolicyV1Provider,
  pythonPolicyV1Provider,
  rustPolicyV1Provider,
  policyParityV1Provider,
  policySelectsStrategyV1Provider,
  typeScriptQueryV1Provider,
  pythonQueryV1Provider,
  rustQueryV1Provider,
  queryParityV1Provider,
  registeredTypeScriptValueObjectV1Provider,
  pythonValueObjectV1Provider,
  rustValueObjectV1Provider,
  valueObjectParityV1Provider,
  valueObjectRelationsV1Provider,
  registeredTypeScriptEntityV1Provider,
  pythonEntityV1Provider,
  rustEntityV1Provider,
  entityParityV1Provider,
  entityRelationsV1Provider,
  typeScriptW3EffectsConnectionsV1Provider,
  typeScriptW4OrchestrationLifecycleV1Provider,
] as const);

const byId = new Map<string, FactoryNodeProviderV1>();
for (const provider of providers) {
  if (byId.has(provider.provider_id)) fail("FACTORY_PROVIDER_DUPLICATE", provider.provider_id);
  byId.set(provider.provider_id, provider);
}

export const getFactoryNodeProviderV1 = (providerId: string): FactoryNodeProviderV1 => {
  const provider = byId.get(providerId);
  return provider ?? fail("FACTORY_PROVIDER_UNKNOWN", providerId);
};

export const listFactoryNodeProvidersV1 = (): readonly FactoryNodeProviderV1[] =>
  providers;
