#!/usr/bin/env node
import {mkdirSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";

import {validateRuntimeConfiguration} from "./validate.mjs";

const result = await validateRuntimeConfiguration();
if (result.status !== "PASS") throw new Error("ARE_V2_RUNTIME_CONFORMANCE_BLOCKED");
const evidence = {
  schema_version: "are.module-configuration-runtime-evidence/v2-candidate",
  configuration_id: result.configuration_id,
  status: result.status,
  checks: result.checks,
  module_set_digest: result.module_set_digest,
  bindings: {
    runtime_configuration_sha256: result.configuration_sha256,
    entrypoints_sha256: result.entrypoints_sha256,
    adapter_source_sha256: result.adapter_source_sha256,
    runtime_source_sha256: result.runtime_source_sha256,
    compiled_source_sha256: result.compiled_source_sha256,
  },
  entry_points: ["RequestIntentContainsPhrase", "RequestIntentSemanticKey", "RouterContainsPhrase"],
  runtime_admitted: false,
  enforcement_active: false,
  effect_authorized: false,
  authority_effect: "none",
};
const directory = resolve(import.meta.dirname, "evidence");
mkdirSync(directory, {recursive: true});
const output = resolve(directory, "runtime-conformance.json");
writeFileSync(output, `${JSON.stringify(evidence, null, 2)}\n`, {flag: "wx"});
process.stdout.write(`${JSON.stringify({status: "built", output, runtime_admitted: false, authority_effect: "none"})}\n`);
