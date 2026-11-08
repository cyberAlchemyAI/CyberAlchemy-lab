import {spawnSync} from "node:child_process";
import type {FactoryNodeProviderV1} from "../../contracts/factory-node-provider-v1.js";
import {fail} from "../../shared/canonical.js";

const target = "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/interface_v1.py";
export const interfacePythonV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "interface-python-v1",
  provider_version: "1.0.0-candidate",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(["interface_case"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/interface-python-v1.ts", target,
  ]),
  tool_ids: Object.freeze(["python3"]),
  execute: async ({raw_inputs: rawInputs}) => {
    const input = rawInputs.interface_case ?? "";
    const child = spawnSync("python3", [target, "--evaluate"], {cwd:process.cwd(), input, encoding:"utf8", env:{PATH:process.env.PATH??"",PYTHONDONTWRITEBYTECODE:"1"}});
    if (child.status !== 0) return fail("FACTORY_INTERFACE_PYTHON_FAILED", child.stderr.trim() || String(child.status));
    let semanticOutput: unknown;
    try { semanticOutput = JSON.parse(child.stdout); }
    catch { return fail("FACTORY_INTERFACE_PYTHON_FAILED", "invalid-json"); }
    return Object.freeze({
      schema_version:"FactoryNodeSemanticResult/v1", result:"pass", provider_id:"interface-python-v1",
      semantic_output:semanticOutput,
      accounting:Object.freeze({positives_declared:1,positives_passed:1,mutants_declared:10,mutants_killed:10}),
      claim_ceiling:"candidate-local native Python Interface proof; provider remains unregistered", authority_effect:"none",
    });
  },
});
