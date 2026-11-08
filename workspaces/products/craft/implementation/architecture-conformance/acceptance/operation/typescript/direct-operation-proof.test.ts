import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { evaluateOperation } from "../../../families/state-change/evaluator/evaluate-operation.js";
import {
  inspectTypeScriptOperationSource,
  mutateTypeScriptOperationSource,
} from "../../../typescript/adapter/operation/index.js";
import { observeTypeScriptOperation } from "../../../typescript/runtime/operation/index.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixtureRoot = resolve(repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/families/state-change/fixtures/complete-settlement");
const sha256 = (value: string): string =>
  createHash("sha256").update(value, "utf8").digest("hex");

describe("direct TypeScript Operation proof", () => {
  it("observes the declared state change/postcondition and kills no-op/read-only", async () => {
    const binding = JSON.parse(await readFile(resolve(fixtureRoot,
      "typescript-binding.json"), "utf8")) as {
      binding_id: string; symbol_name: string; binding_sha256: string;
      source_ref: { path: string; sha256: string };
    };
    const source = await readFile(resolve(repositoryRoot, binding.source_ref.path), "utf8");
    expect(sha256(source)).toBe(binding.source_ref.sha256);
    const inspected = inspectTypeScriptOperationSource({
      source, modulePath: binding.source_ref.path, symbolName: binding.symbol_name,
    });
    expect(inspected).toMatchObject({
      supported: true, observed_action_order: ["payouts", "events"],
    });
    const execute = (candidate: string, mutationId: string | null) =>
      observeTypeScriptOperation({
        source: candidate, bindingId: binding.binding_id,
        bindingSourceSha256: binding.source_ref.sha256,
        symbolName: binding.symbol_name, mutationId,
        requestId: "request-001", amount: 12500,
      });
    const positive = evaluateOperation({
      observation: await execute(source, null),
      expectedBindingId: binding.binding_id,
      expectedBindingSourceSha256: binding.source_ref.sha256,
      requestId: "request-001",
    });
    expect(positive.verdict).toBe("pass");
    for (const mutationId of ["no-op", "read-only"] as const) {
      const mutated = mutateTypeScriptOperationSource({
        source, modulePath: binding.source_ref.path,
        symbolName: binding.symbol_name, mutationId,
      });
      const result = evaluateOperation({
        observation: await execute(mutated, mutationId),
        expectedBindingId: binding.binding_id,
        expectedBindingSourceSha256: binding.source_ref.sha256,
        requestId: "request-001",
      });
      expect(result.verdict).toBe("fail");
      expect(result.findings.map(({ code }) => code)).toContain("OP_STATE_CHANGE_MISSING");
    }
  });
});
