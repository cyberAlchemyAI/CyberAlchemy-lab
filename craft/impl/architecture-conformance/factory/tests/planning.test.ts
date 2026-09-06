import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { repositoryRoot } from "../cli/index.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";

const load = async () => decodeFactoryRunRequestV1(JSON.parse(await readFile(resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/reference-suite.request.json",
), "utf8")));

describe("factory planning", () => {
  it("resolves the same request and bytes to the same lock", async () => {
    const request = await load();
    const first = await planFactoryRun({ repositoryRoot, request });
    const second = await planFactoryRun({ repositoryRoot, request });
    expect(first.lock.lock_sha256).toBe(second.lock.lock_sha256);
    expect(first.run_id).toBe(second.run_id);
    const rule = first.lock.nodes.find(({ provider_id: id }) => id === "typescript-rule-v1");
    expect(rule?.inputs).toHaveLength(6);
    expect(rule?.components.length).toBeGreaterThan(1);
  });

  it("fails a cyclic graph before execution", async () => {
    const request = await load();
    const cyclic = Object.freeze({
      ...request,
      nodes: Object.freeze([Object.freeze({
        ...request.nodes[0]!,
        depends_on: Object.freeze([request.nodes[0]!.node_id]),
      })]),
    });
    await expect(planFactoryRun({ repositoryRoot, request: cyclic }))
      .rejects.toThrow("FACTORY_GRAPH_INVALID");
  });
});
