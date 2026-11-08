import assert from "node:assert/strict";
import test from "node:test";

import { INTEGRATION_PROJECT_LAYOUT_V1, integrationResponsibilityPathsV1 } from "../../src/system-integration/integration-project-layout-v1.ts";

test("R7 assigns every integration responsibility without a generic runtime directory", () => {
  const expectedExtensions = { typescript: "ts", python: "py", rust: "rs" } as const;
  for (const [language, extension] of Object.entries(expectedExtensions)) {
    const paths = integrationResponsibilityPathsV1(language as keyof typeof expectedExtensions);
    assert.equal(paths.application_contracts, `src/features/integration/application/contracts.${extension}`);
    assert.equal(paths.provider_adapters, `src/integrations/providers/bindings.${extension}`);
    assert.equal(paths.mappings, `src/integrations/mappings/definitions.${extension}`);
    assert.equal(paths.configuration, `src/config/integrations/manifest.${extension}`);
    assert.equal(paths.migrations, `migrations/manifest.${extension}`);
    assert.equal(paths.observation, `src/observability/integrations/observation.${extension}`);
    assert.equal(Object.values(paths).some(path => path === "runtime" || path.startsWith("runtime/")), false);
  }
  assert.equal(INTEGRATION_PROJECT_LAYOUT_V1.authority_effect, "none");
});
