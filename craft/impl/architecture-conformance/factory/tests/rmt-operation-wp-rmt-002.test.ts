import {lstat, readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {
  bindOperationReplayCleanupOutcome,
  runOperationFactoryReplay,
} from
  "../../acceptance/operation/wp-rmt-002/replay/run-operation-replay.js";
import {repositoryRoot} from "../cli/index.js";
import {listFactoryNodeProvidersV1} from
  "../registry/factory-node-registry-v1.js";
import {sha256} from "../shared/canonical.js";

const REQUEST_PATH = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-operation-wp-rmt-002.request.json",
);
const REGISTRY_PATH = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/registry/factory-node-registry-v1.ts",
);
const EXPECTED_REGISTRY_SHA256 =
  "2497f2e047e023de2738bac4b815e6b0212560dcfc8053982c94f4a529a9f51b";
const ABSENT_PROVIDER_IDS = Object.freeze([
  "operation-typescript-v1",
  "operation-python-v1",
  "operation-rust-v1",
  "operation-wp-rmt-002-replay-v1",
]);

const expectAbsent = async (path: string): Promise<void> => {
  await expect(lstat(path)).rejects.toMatchObject({code: "ENOENT"});
};

describe("RMT-OP-007 deterministic factory replay", () => {
  it("hash-locks 109 exact roles while all candidate provider IDs remain canonically absent", async () => {
    const ids = listFactoryNodeProvidersV1()
      .map(({provider_id: providerId}) => providerId);
    for (const providerId of ABSENT_PROVIDER_IDS) {
      expect(ids).not.toContain(providerId);
    }
    expect(sha256(await readFile(REGISTRY_PATH)))
      .toBe(EXPECTED_REGISTRY_SHA256);
    const request = JSON.parse(await readFile(REQUEST_PATH, "utf8")) as {
      nodes: Array<{
        provider_id: string;
        input_refs: Array<{
          role: string;
          ref: {path: string; sha256: string};
        }>;
      }>;
      authority_effect: string;
    };
    expect(request.nodes).toHaveLength(1);
    expect(request.nodes[0]?.provider_id)
      .toBe("operation-wp-rmt-002-replay-v1");
    expect(request.nodes[0]?.input_refs).toHaveLength(109);
    expect(new Set(request.nodes[0]?.input_refs.map(({role}) => role)).size)
      .toBe(109);
    expect(new Set(request.nodes[0]?.input_refs.map(({ref}) => ref.path)).size)
      .toBe(49);
    expect(request.nodes[0]?.input_refs.slice(-3).map(({role}) => role))
      .toEqual([
        "parity_evaluator",
        "parity_evaluator_test",
        "parity_live_test",
      ]);
    for (const {ref} of request.nodes[0]!.input_refs) {
      expect(sha256(await readFile(resolve(repositoryRoot, ref.path))))
        .toBe(ref.sha256);
    }
    expect(request.authority_effect).toBe("none");
  });

  it("produces one exact PID-normalized semantic receipt across direct, locked-child, and replay execution", async () => {
    const registryBefore = await readFile(REGISTRY_PATH);
    const result = await runOperationFactoryReplay();
    expect(result).toMatchObject({
      result: "pass",
      exit_code: 0,
      request_sha256:
        "8d7ca1ab4c933b25abfc15fa34616a10411a6b2ea576b9c7f8d2c91527412832",
      lock_sha256:
        "d2a3042c843978d8a77ab67f2cb13b6dfc2a62007ef75c2bcf43ed1e15ec9a1e",
      failure_exit_preserved: true,
      canonical_registry_sha256: EXPECTED_REGISTRY_SHA256,
      canonical_registry_unchanged: true,
      overlay_strategy: "hardlink-copy-on-write",
      workspace_cleaned: true,
      cleanup_error: null,
      authority_effect: "none",
    });
    const receipt = result.semantic_receipt as {
      ordered_nodes: Array<{
        semantic_sha256: string;
        replay_sha256: string;
        accounting: Record<string, number>;
      }>;
    };
    expect(receipt.ordered_nodes).toHaveLength(1);
    expect(receipt.ordered_nodes[0]?.semantic_sha256)
      .toBe(receipt.ordered_nodes[0]?.replay_sha256);
    expect(receipt.ordered_nodes[0]?.accounting).toMatchObject({
      positives_declared: 7,
      positives_passed: 7,
      mutants_declared: 87,
      mutants_killed: 87,
    });
    const node = result.node_semantic as {
      semantic_output: {
        proof: {
          parity_receipt: Record<string, unknown>;
          semantic_determinism: Record<string, unknown>;
        };
      };
    };
    expect(node.semantic_output.proof.parity_receipt).toMatchObject({
      schema_version: "OperationReplayParityReceipt/v1",
      result: "pass",
      normalized_parity_sha256:
        "d18eccbfb23a3b67a49bc1dc3dd5af8242a52e6f159d3f91a67fa03bba6fbf8f",
      native_fresh_processes_per_semantic_execution: 12,
      redacted_dynamic_pid_fields: 12,
      process_ids_validated_before_redaction: true,
      process_ids_in_semantic_identity: false,
      native_hash_byte_comparison: false,
      portable_semantics_compared: true,
      authority_effect: "none",
    });
    const normalizedParity =
      node.semantic_output.proof.parity_receipt.normalized_parity as {
        portable_projection: unknown;
        native_evidence: unknown;
      };
    expect(normalizedParity.portable_projection).toBeDefined();
    expect(normalizedParity.native_evidence).toBeDefined();
    const processEvidence = result.process_evidence as {
      coordinator_pid: number;
      execute_child_pids: number[];
      replay_child_pids: number[];
      factory_fresh_processes_declared: number;
      native_fresh_processes_per_semantic_execution: number;
    };
    const factoryPids = [
      ...processEvidence.execute_child_pids,
      ...processEvidence.replay_child_pids,
    ];
    expect(factoryPids).toHaveLength(2);
    expect(new Set(factoryPids).size).toBe(2);
    expect(factoryPids).not.toContain(processEvidence.coordinator_pid);
    expect(processEvidence.factory_fresh_processes_declared).toBe(2);
    expect(processEvidence.native_fresh_processes_per_semantic_execution)
      .toBe(12);
    expect(result.spawned_coordinator_pid)
      .toBe(processEvidence.coordinator_pid);
    expect(sha256(await readFile(REGISTRY_PATH))).toBe(sha256(registryBefore));
    await expectAbsent(String(result.workspace_path));
    const replayedTranscript = await runOperationFactoryReplay({
      probe: "replayed-transcript",
      transcript: String(result.child_stdout),
    });
    expect(replayedTranscript).toMatchObject({
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID",
      exit_code: 0,
      output_validation_failure_preserved: true,
      canonical_registry_unchanged: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_exit: true,
      authority_effect: "none",
    });
    await expectAbsent(String(replayedTranscript.workspace_path));
  }, 120_000);

  it("preserves stale-input failure before cleanup", async () => {
    const result = await runOperationFactoryReplay({
      probe: "tampered-input",
    });
    expect(result).toMatchObject({
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CHILD_NONZERO",
      exit_code: 1,
      failure_exit_preserved: true,
      canonical_registry_unchanged: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_exit: true,
      authority_effect: "none",
    });
    expect(String(result.stderr)).toContain("FACTORY_INPUT_TAMPERED");
    await expectAbsent(String(result.workspace_path));
  }, 30_000);

  it("does not let valid-looking output mask a nonzero child exit", async () => {
    const result = await runOperationFactoryReplay({
      probe: "nonzero-with-valid-output",
    });
    expect(result).toMatchObject({
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CHILD_NONZERO",
      exit_code: 17,
      failure_exit_preserved: true,
      canonical_registry_unchanged: true,
      workspace_cleaned: true,
      cleanup_did_not_replace_primary_exit: true,
      authority_effect: "none",
    });
    expect(String(result.stdout)).toContain('"result":"pass"');
    await expectAbsent(String(result.workspace_path));
  }, 30_000);

  it("rejects malformed, empty, multi-line, and surplus child output before cleanup", async () => {
    for (const probe of [
      "malformed-output",
      "empty-output",
      "multiple-line-output",
      "surplus-output",
    ] as const) {
      const result = await runOperationFactoryReplay({probe});
      expect(result).toMatchObject({
        result: "block",
        probe,
        primary_failure: "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID",
        exit_code: 0,
        output_validation_failure_preserved: true,
        failure_exit_preserved: true,
        canonical_registry_unchanged: true,
        workspace_cleaned: true,
        cleanup_did_not_replace_primary_exit: true,
        authority_effect: "none",
      });
      await expectAbsent(String(result.workspace_path));
    }
  }, 60_000);

  it("blocks cleanup failure without replacing an earlier primary failure", () => {
    expect(bindOperationReplayCleanupOutcome({
      outcome: {result: "pass", exit_code: 0},
      cleanup_error: "cleanup-probe",
      workspace_cleaned: true,
    })).toMatchObject({
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CLEANUP_FAILED",
      cleanup_failure: "cleanup-probe",
      failure_exit_preserved: true,
    });
    expect(bindOperationReplayCleanupOutcome({
      outcome: {
        result: "block",
        primary_failure: "RMT_OP_REPLAY_CHILD_NONZERO",
        exit_code: 17,
      },
      cleanup_error: "cleanup-probe",
      workspace_cleaned: false,
    })).toMatchObject({
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CHILD_NONZERO",
      exit_code: 17,
      cleanup_failure: "cleanup-probe",
    });
  });
});
