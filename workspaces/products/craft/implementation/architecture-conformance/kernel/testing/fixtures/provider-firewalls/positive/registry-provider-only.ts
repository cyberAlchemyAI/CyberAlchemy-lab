import type { FactoryNodeProviderV1 } from "../contracts/factory-node-provider-v1.js";
import { fail } from "../shared/canonical.js";
import { typeScriptRuleV1Provider } from "./providers/typescript-rule-v1.js";

export const registryProvider: FactoryNodeProviderV1 =
  typeScriptRuleV1Provider ?? fail("REGISTRY_PROVIDER_MISSING");
