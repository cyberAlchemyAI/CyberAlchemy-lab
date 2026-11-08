import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { planEmbeddedIntegrationContributionV1 } from "../../src/system-integration/embedded-generation-v1.ts";
import { planIntegrationProjectV2 } from "../../src/system-integration/generation-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const source = JSON.parse(fs.readFileSync(path.resolve(here, "../../examples/reconciled-commerce/integrations/application.json"), "utf8"));

test("L0 embedded TypeScript contribution removes only the standalone root manifest", () => {
  const before = planIntegrationProjectV2(source, "typescript");
  const contribution = planEmbeddedIntegrationContributionV1(source, "typescript");
  const after = planIntegrationProjectV2(structuredClone(source), "typescript");
  assert.deepEqual(after, before, "embedded planning must not change standalone bytes");
  assert.equal(contribution.standalone_plan_sha256, before.plan_digest);
  assert.equal(contribution.owned_artifacts.length, before.artifacts.length - 1);
  assert.equal(contribution.owned_artifacts.some(item => item.relative_path === "tsconfig.json"), false);
  assert.equal(contribution.owned_artifacts.some(item => item.relative_path === "runtime" || item.relative_path.startsWith("runtime/")), false);
  assert.equal(Object.isFrozen(contribution), true);
  assert.equal(contribution.authority_effect, "none");
});

test("L0 embedded contribution is deterministic", () => {
  assert.deepEqual(planEmbeddedIntegrationContributionV1(source, "typescript"), planEmbeddedIntegrationContributionV1(structuredClone(source), "typescript"));
});
