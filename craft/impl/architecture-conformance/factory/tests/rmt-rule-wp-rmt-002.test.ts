import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {runRuleReplay} from
  "../../acceptance/rule/wp-rmt-002/replay/run-rule-replay.js";
import {repositoryRoot} from "../cli/index.js";
import {listFactoryNodeProvidersV1} from
  "../registry/factory-node-registry-v1.js";
import {sha256} from "../shared/canonical.js";

const requestPath = resolve(repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/" +
  "rmt-rule-wp-rmt-002.request.json");

describe("RMT-RULE-007 candidate-local factory replay request", () => {
  it("hash-locks the exact candidate proof, adapters, parity, and replay inputs", async () => {
    const request = JSON.parse(await readFile(requestPath, "utf8")) as {
      schema_version: string;
      nodes: Array<{
        provider_id: string;
        input_refs: Array<{role: string; ref: {path: string; sha256: string}}>
      }>;
      authority_effect: string;
    };
    expect(request.schema_version).toBe("FactoryRunRequest/v1");
    expect(request.nodes).toHaveLength(1);
    expect(request.nodes[0]?.provider_id).toBe("rule-wp-rmt-002-replay-v1");
    expect(request.nodes[0]?.input_refs).toHaveLength(13);
    expect(new Set(request.nodes[0]?.input_refs.map(({role}) => role)).size)
      .toBe(13);
    for (const {ref} of request.nodes[0]!.input_refs) {
      expect(sha256(await readFile(resolve(repositoryRoot, ref.path))))
        .toBe(ref.sha256);
    }
    const registeredIds = listFactoryNodeProvidersV1().map(
      ({provider_id: providerId}) => providerId);
    expect(registeredIds).not.toContain("rule-wp-rmt-002-replay-v1");
    expect(request.authority_effect).toBe("none");
  });

  it("executes the bound request through the deterministic replay runner", async () => {
    const result = await runRuleReplay();
    expect(result).toMatchObject({
      result: "pass",
      exit_code: 0,
      semantic_receipts_deterministic: true,
      fresh_process_count_declared: 2,
      workspace_cleaned: true,
      failure_exit_preserved: true,
      authority_effect: "none",
    });
  }, 120_000);
});
