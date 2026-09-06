import {mkdir, readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {decodeFactoryRunRequestV1} from
  "../../../../factory/codecs/decode-factory-run-request-v1.js";
import type {FactoryProcessObservationV1} from
  "../../../../factory/contracts/factory-process-observation-v1.js";
import type {FactorySemanticReceiptV1} from
  "../../../../factory/contracts/factory-semantic-receipt-v1.js";
import {repositoryRoot} from "../../../../factory/cli/index.js";
import {executeFactoryRun} from
  "../../../../factory/pipeline/execute-factory-run.js";
import {planFactoryRun} from
  "../../../../factory/pipeline/plan-factory-run.js";
import {replayFactoryRun} from
  "../../../../factory/pipeline/replay-factory-run.js";
import {verifyFactoryRun} from
  "../../../../factory/pipeline/verify-factory-run.js";
import {canonicalJson, fail, isRecord, sha256} from
  "../../../../factory/shared/canonical.js";

const requestPath = resolve(
  repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-operation-wp-rmt-002.request.json",
);

const execute = async (): Promise<void> => {
  const outputParent = process.argv[2];
  const parentNonce = process.env.DOMAINSPEC_OPERATION_REPLAY_PARENT_NONCE;
  if (outputParent === undefined) {
    return fail("RMT_OP_REPLAY_OUTPUT_PARENT_MISSING");
  }
  if (typeof parentNonce !== "string" ||
      !/^[a-f0-9]{64}$/u.test(parentNonce)) {
    return fail("RMT_OP_REPLAY_PARENT_NONCE_INVALID");
  }
  await mkdir(outputParent, {recursive: false});
  const request = decodeFactoryRunRequestV1(
    JSON.parse(await readFile(requestPath, "utf8")),
  );
  const firstPlan = await planFactoryRun({repositoryRoot, request});
  const secondPlan = await planFactoryRun({repositoryRoot, request});
  if (firstPlan.lock.lock_sha256 !== secondPlan.lock.lock_sha256 ||
      firstPlan.run_id !== secondPlan.run_id ||
      canonicalJson(firstPlan.lock) !== canonicalJson(secondPlan.lock)) {
    return fail("RMT_OP_REPLAY_PLAN_DRIFT");
  }
  const run = await executeFactoryRun({
    repositoryRoot,
    outputParent,
    plan: firstPlan,
  });
  const verifiedBeforeReplay = await verifyFactoryRun(run.run_path);
  const replay = await replayFactoryRun(run.run_path);
  const verifiedAfterReplay = await verifyFactoryRun(run.run_path);
  const semanticReceipt = JSON.parse(await readFile(
    resolve(run.run_path, "semantic-receipt.json"),
    "utf8",
  )) as FactorySemanticReceiptV1;
  const processObservation = JSON.parse(await readFile(
    resolve(run.run_path, "process-observation.json"),
    "utf8",
  )) as FactoryProcessObservationV1;
  const nodeId = firstPlan.lock.ordered_node_ids[0];
  if (nodeId === undefined || firstPlan.lock.ordered_node_ids.length !== 1) {
    return fail("RMT_OP_REPLAY_NODE_SET_INVALID");
  }
  const nodeSemantic = JSON.parse(await readFile(
    resolve(run.run_path, "nodes", nodeId, "semantic.json"),
    "utf8",
  )) as unknown;
  if (!isRecord(nodeSemantic) || semanticReceipt.ordered_nodes.length !== 1 ||
      verifiedBeforeReplay.semantic_receipt_sha256 !==
        run.semantic_receipt_sha256 ||
      verifiedAfterReplay.semantic_receipt_sha256 !==
        run.semantic_receipt_sha256 ||
      replay.replayed_nodes !== 1) {
    return fail("RMT_OP_REPLAY_FACTORY_RESULT_INVALID");
  }
  const nodeReceipt = semanticReceipt.ordered_nodes[0]!;
  if (nodeReceipt.semantic_sha256 !== nodeReceipt.replay_sha256 ||
      sha256(canonicalJson(nodeSemantic)) !== nodeReceipt.semantic_sha256) {
    return fail("RMT_OP_REPLAY_SEMANTIC_RECEIPT_DRIFT");
  }
  const executeChildPids = processObservation.child_pids;
  const replayChildPids = replay.child_pids;
  const factoryPids = [...executeChildPids, ...replayChildPids];
  if (executeChildPids.length !== 1 || replayChildPids.length !== 1 ||
      factoryPids.some((pid) =>
        !Number.isSafeInteger(pid) || pid <= 0 ||
        pid === processObservation.coordinator_pid) ||
      new Set(factoryPids).size !== 2) {
    return fail("RMT_OP_REPLAY_FACTORY_PROCESS_EVIDENCE_INVALID");
  }
  process.stdout.write(`${JSON.stringify(Object.freeze({
    schema_version: "OperationFactoryReplayRun/v1",
    result: "pass",
    request_sha256: firstPlan.lock.request_sha256,
    lock_sha256: firstPlan.lock.lock_sha256,
    run_id: firstPlan.run_id,
    semantic_receipt_sha256: run.semantic_receipt_sha256,
    semantic_receipt: semanticReceipt,
    node_semantic: nodeSemantic,
    process_evidence: Object.freeze({
      coordinator_pid: processObservation.coordinator_pid,
      execute_child_pids: executeChildPids,
      replay_child_pids: replayChildPids,
      factory_fresh_processes_declared: 2,
      native_fresh_processes_per_semantic_execution: 12,
      parent_nonce: parentNonce,
    }),
    authority_effect: "none",
  }))}\n`);
};

const outputProbe = process.env.DOMAINSPEC_OPERATION_REPLAY_OUTPUT_PROBE;
const transcriptPath =
  process.env.DOMAINSPEC_OPERATION_REPLAY_TRANSCRIPT_PATH;

if (transcriptPath !== undefined) {
  process.stdout.write(await readFile(transcriptPath, "utf8"));
} else if (outputProbe === "malformed-output") {
  process.stdout.write("{not-json}\n");
} else if (outputProbe === "multiple-line-output") {
  process.stdout.write(
    '{"schema_version":"OperationFactoryReplayRun/v1","result":"pass"}\n',
  );
  process.stdout.write(
    '{"schema_version":"OperationFactoryReplayRun/v1","result":"pass"}\n',
  );
} else if (outputProbe === "surplus-output") {
  process.stdout.write(`${JSON.stringify({
    schema_version: "OperationFactoryReplayRun/v1",
    result: "pass",
    request_sha256: "0".repeat(64),
    lock_sha256: "0".repeat(64),
    run_id: "factory-000000000000000000000000",
    semantic_receipt_sha256: "0".repeat(64),
    semantic_receipt: {},
    node_semantic: {},
    process_evidence: {},
    authority_effect: "none",
    surplus: true,
  })}\n`);
} else if (outputProbe === "empty-output") {
  // Intentionally emit no protocol bytes.
} else if (process.env.DOMAINSPEC_OPERATION_REPLAY_VALID_OUTPUT_NONZERO ===
    "1") {
  process.stdout.write(
    '{"schema_version":"OperationFactoryReplayRun/v1","result":"pass"}\n',
  );
  process.exitCode = 17;
} else {
  execute().catch((error: unknown) => {
    process.stderr.write(`RMT_OP_REPLAY_CHILD_FAILED:${
      error instanceof Error ? error.message : String(error)
    }\n`);
    process.exitCode = 1;
  });
}
