import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { compileApplicationRuntimeBindingV1 } from "../../src/system-integration/application-runtime-binding-v1.ts";
const root = fileURLToPath(new URL("../../examples/reconciled-commerce/", import.meta.url));
const read = (relative: string): any => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

test("one existing application graph joins every actual integration binding to each selected target pack", () => {
  const graph = loadCompiledProjectGraph(path.join(root, "source"));
  for (const language of ["typescript", "python", "rust"]) {
    const source = read("integrations/application.json"), providers = read(`providers/${language}.json`);
    const result = compileApplicationRuntimeBindingV1(graph, source, providers);
    assert.equal(result.providers.length, 5);
    assert.equal(result.language, language);
    assert.deepEqual([...new Set(result.providers.map(r => r.role))].sort(), ["inbound_http", "messaging", "outbound_http", "persistence"]);
    for (const row of result.providers) assert.deepEqual(row.provider, providers.providers[row.role]);
    assert.equal(result.binding.domain_source_manifest_sha256, graph.source_manifest.manifest_sha256);
    assert.equal(result.runtime_guarantees_observed, false);
    assert.equal(result.authority_effect, "none");
    assert.equal(Object.isFrozen(result.providers), true);
    assert.deepEqual(compileApplicationRuntimeBindingV1(graph, source, providers), result);
  }
});

test("a compatible unused profile cannot hide the incompatible profile of the bound realization", () => {
  const graph = loadCompiledProjectGraph(path.join(root, "source"));
  const source = read("integrations/application.json");
  const kernel = source.persistence.integration_kernel;
  kernel.provider_profiles.push({ ...structuredClone(kernel.provider_profiles[0]), profile_id: "provider-profile:incompatible", provider_kind: "sqlite" });
  kernel.provider_realizations[0].provider_profile_ref = "provider-profile:incompatible";
  for (const row of [...source.persistence.persistence_bindings, ...source.persistence.transaction_guarantees]) row.implementation_profile_ref = "provider-profile:incompatible";
  assert.throws(() => compileApplicationRuntimeBindingV1(graph, source, read("providers/typescript.json")), /DS_APPLICATION_RUNTIME_PROVIDER/);
});

test("runtime join rejects missing provider capabilities, wrong selections, and a forged domain graph", () => {
  const graph = loadCompiledProjectGraph(path.join(root, "source"));
  const source = read("integrations/application.json");
  source.messaging.integration_kernel.provider_profiles[0].capability_set = ["topic"];
  assert.throws(() => compileApplicationRuntimeBindingV1(graph, source, read("providers/typescript.json")), /DS_APPLICATION_RUNTIME_PROVIDER/);
  const providers = read("providers/typescript.json");
  providers.providers.persistence.provider_id = "postgresql:17";
  assert.throws(() => compileApplicationRuntimeBindingV1(graph, read("integrations/application.json"), providers), /DS_PROVIDER_SELECTION_REALIZATION/);
  assert.throws(() => compileApplicationRuntimeBindingV1(structuredClone(graph), read("integrations/application.json"), read("providers/typescript.json")), /unvalidated or changed/);
});
