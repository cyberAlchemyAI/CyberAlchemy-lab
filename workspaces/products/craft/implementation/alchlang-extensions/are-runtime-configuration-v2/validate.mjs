#!/usr/bin/env node
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {pathToFileURL} from "node:url";

import {semanticTextOutputValidators} from "../../../../../../../implementation/agent-reasoning-engine/packages/module-port/semantic-text.mjs";
import {composeStaticModulePort} from "../../../../../../../implementation/agent-reasoning-engine/packages/module-port/static-composition.mjs";

const root = import.meta.dirname;
const readJson = (name) => JSON.parse(readFileSync(resolve(root, name), "utf8"));
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const sourceDigest = (relative) => sha256(readFileSync(resolve(root, relative)));
const safeSourceDigest = (relative) => {
  try { return typeof relative === "string" ? sourceDigest(relative) : null; } catch { return null; }
};

export async function validateRuntimeConfiguration() {
  const manifest = readJson("generated/manifest.json");
  const configuration = readJson("generated/runtime/configuration.json");
  const entrypoints = readJson("generated/runtime/entrypoints.json");
  const bindings = readJson("generated/provenance/runtime-bindings.json");
  const evidence = readJson("generated/evidence/conformance.json");
  const checks = [];
  const check = (check_id, condition) => checks.push({check_id, outcome: condition ? "PASS" : "BLOCK"});
  for (const [relative, expected] of Object.entries(manifest.files)) {
    const observed = safeSourceDigest(`generated/${relative}`);
    check(`generated-digest:${relative}`, observed === expected);
  }
  const module = bindings.modules?.find((item) => item.module_id === "alch-semantic-prelude");
  check("single-runtime-binding", bindings.modules?.length === 1 && module?.factory_id === "createAlchSemanticAdapter");
  for (const [name, relative, expected] of [
    ["factory", module?.factory_source, module?.factory_source_sha256],
    ["runtime", module?.runtime_source, module?.runtime_source_sha256],
    ["compiled", module?.compiled_source, module?.compiled_source_sha256],
  ]) {
    const observed = safeSourceDigest(relative);
    check(`${name}-source-binding`, observed !== null && observed === expected);
  }
  let composition = {ok: false, disposition: "unavailable", modules: [], port: null, module_set_digest: null, authority_effect: "none"};
  if (checks.every((row) => row.outcome === "PASS")) {
    try {
      const [{createAlchSemanticAdapter}, {semanticKey, containsPhrase}] = await Promise.all([
        import("../../../../../../../implementation/agent-reasoning-engine/packages/module-port/alch-semantic-adapter.mjs"),
        import("../semantic-contract-v1/consumer-runtime.mjs"),
      ]);
      composition = composeStaticModulePort({
        configuration,
        adapter_factories: {createAlchSemanticAdapter: () => createAlchSemanticAdapter({semanticKey, containsPhrase})},
        output_validators: semanticTextOutputValidators,
      });
    } catch { check("verified-source-load", false); }
  }
  check("static-composition-available", composition.ok === true && composition.disposition === "available");
  check("single-exact-module", composition.modules?.length === 1
    && composition.modules[0]?.module_id === module?.module_id
    && composition.modules[0]?.manifest_digest === configuration.modules[0]?.manifest_digest);
  const expectedEntries = [
    ["RequestIntentContainsPhrase", "request-intent-runtime", "text.contains-phrase/v1"],
    ["RequestIntentSemanticKey", "request-intent-runtime", "text.semantic-key/v1"],
    ["RouterContainsPhrase", "request-decision-router", "text.contains-phrase/v1"],
  ];
  check("entry-semantic-orthogonality", JSON.stringify(entrypoints.entries.map((entry) => [entry.entry_id, entry.consumer_id, entry.capability_id])) === JSON.stringify(expectedEntries));
  const samples = {
    RequestIntentContainsPhrase: {input: {text: "start a new workflow", phrase: "new workflow"}, expected: {matched: true}},
    RequestIntentSemanticKey: {input: {text: "Build—a—new system"}, expected: {key: "build a new system"}},
    RouterContainsPhrase: {input: {text: "predefined module", phrase: "define"}, expected: {matched: false}},
  };
  for (const entry of entrypoints.entries) {
    const sample = samples[entry.entry_id];
    const result = composition.port?.invoke({schema_version: "are.module-invocation/v1", invocation_id: `conformance:${entry.entry_id.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase()}`, consumer_id: entry.consumer_id, capability_id: entry.capability_id, input: sample?.input, dependency_posture: entry.dependency_posture, authority_effect: "none"});
    check(`entry-invocation:${entry.entry_id}`, result?.ok === true && result.disposition === "available" && JSON.stringify(result.value) === JSON.stringify(sample?.expected));
  }
  check("compiled-conformance-pass", evidence.status === "pass" && evidence.checks.every((row) => row.outcome === "PASS"));
  check("no-admission-or-effect", manifest.runtime_admitted === false && entrypoints.runtime_admitted === false
    && composition.authority_effect === "none" && evidence.authority_effect === "none");
  const blocked = checks.filter((row) => row.outcome === "BLOCK").length;
  return {schema_version: "are.module-configuration-runtime-conformance/v2-candidate", configuration_id: configuration.configuration_id,
    status: blocked === 0 ? "PASS" : "BLOCK", checks, module_set_digest: composition.module_set_digest,
    configuration_sha256: sourceDigest("generated/runtime/configuration.json"),
    entrypoints_sha256: sourceDigest("generated/runtime/entrypoints.json"),
    adapter_source_sha256: safeSourceDigest(module?.factory_source), runtime_source_sha256: safeSourceDigest(module?.runtime_source),
    compiled_source_sha256: safeSourceDigest(module?.compiled_source), runtime_admitted: false, enforcement_active: false, authority_effect: "none"};
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const result = await validateRuntimeConfiguration();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = result.status === "PASS" ? 0 : 1;
}
