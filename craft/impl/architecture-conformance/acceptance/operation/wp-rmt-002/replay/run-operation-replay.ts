import {execFile} from "node:child_process";
import {randomBytes} from "node:crypto";
import {
  lstat,
  mkdir,
  mkdtemp,
  readFile,
  rm,
  unlink,
  writeFile,
} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";
import {promisify} from "node:util";

import {
  canonicalJson,
  exactKeys,
  fail,
  isRecord,
  sha256,
} from "../../../../factory/shared/canonical.js";
import {OPERATION_REPLAY_CLAIM_CEILING} from
  "./operation-replay-v1.js";

type ReplayProbe = "pass" | "tampered-input" |
  "nonzero-with-valid-output" | "malformed-output" |
  "multiple-line-output" | "empty-output" | "surplus-output" |
  "replayed-transcript";

type ChildFailure = Error & Readonly<{
  code?: number | string;
  stdout?: string;
  stderr?: string;
}>;

const executeFilePromise = promisify(execFile);
const here = dirname(fileURLToPath(import.meta.url));
const implementationRoot = resolve(here, "../../../../..");
const repositoryRoot = resolve(implementationRoot, "../../..");
const projectRoot = resolve(repositoryRoot, "projects/domainspec-v2");
const REGISTRY_RELATIVE =
  "projects/domainspec-v2/impl/architecture-conformance/factory/registry/factory-node-registry-v1.ts";
const REQUEST_RELATIVE =
  "projects/domainspec-v2/impl/architecture-conformance/factory/fixtures/rmt-operation-wp-rmt-002.request.json";
const CHILD_RELATIVE =
  "projects/domainspec-v2/impl/architecture-conformance/acceptance/operation/wp-rmt-002/replay/execute-operation-replay.ts";
const EXPECTED_CANONICAL_REGISTRY_SHA256 =
  "2497f2e047e023de2738bac4b815e6b0212560dcfc8053982c94f4a529a9f51b";
const EXPECTED_NORMALIZED_PARITY_SHA256 =
  "d18eccbfb23a3b67a49bc1dc3dd5af8242a52e6f159d3f91a67fa03bba6fbf8f";
const EXPECTED_REQUEST_SHA256 =
  "8d7ca1ab4c933b25abfc15fa34616a10411a6b2ea576b9c7f8d2c91527412832";
const EXPECTED_LOCK_SHA256 =
  "d2a3042c843978d8a77ab67f2cb13b6dfc2a62007ef75c2bcf43ed1e15ec9a1e";
const SHA256 = /^[a-f0-9]{64}$/u;
const PROVIDER_IDS = Object.freeze([
  "operation-typescript-v1",
  "operation-python-v1",
  "operation-rust-v1",
  "operation-wp-rmt-002-replay-v1",
]);

const patchOverlayRegistry = async (
  overlayRoot: string,
): Promise<string> => {
  const registryPath = resolve(overlayRoot, REGISTRY_RELATIVE);
  const source = await readFile(registryPath, "utf8");
  if (source.includes("operationWpRmt002ReplayV1Provider")) {
    return fail("RMT_OP_REPLAY_CANONICAL_REGISTRY_NOT_NEGATIVE");
  }
  const importAnchor =
    'import { fail } from "../shared/canonical.js";\n';
  const providerAnchor = "const providers = Object.freeze([\n";
  if (!source.includes(importAnchor) || !source.includes(providerAnchor)) {
    return fail("RMT_OP_REPLAY_REGISTRY_ANCHOR_INVALID");
  }
  const patched = source
    .replace(importAnchor, `${importAnchor}import {
  operationWpRmt002ReplayV1Provider,
} from "../../acceptance/operation/wp-rmt-002/replay/operation-replay-v1.js";
`)
    .replace(providerAnchor,
      `${providerAnchor}  operationWpRmt002ReplayV1Provider,\n`);
  await unlink(registryPath);
  await writeFile(registryPath, patched, {encoding: "utf8", flag: "wx"});
  return sha256(patched);
};

const tamperOverlayRequest = async (overlayRoot: string): Promise<void> => {
  const requestPath = resolve(overlayRoot, REQUEST_RELATIVE);
  const request = JSON.parse(await readFile(requestPath, "utf8")) as {
    nodes: Array<{input_refs: Array<{ref: {sha256?: string}}>}>;
  };
  const firstRef = request.nodes[0]?.input_refs[0]?.ref;
  if (firstRef === undefined || typeof firstRef.sha256 !== "string") {
    return fail("RMT_OP_REPLAY_FAILURE_PROBE_INVALID");
  }
  firstRef.sha256 = "0".repeat(64);
  await unlink(requestPath);
  await writeFile(requestPath, `${JSON.stringify(request, null, 2)}\n`, {
    encoding: "utf8",
    flag: "wx",
  });
};

const absent = async (path: string): Promise<boolean> => {
  try {
    await lstat(path);
    return false;
  } catch (error: unknown) {
    return error instanceof Error && "code" in error &&
      error.code === "ENOENT";
  }
};

const record = (value: unknown, detail: string): Record<string, unknown> =>
  isRecord(value) ? value
    : fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", detail);

const digest = (value: unknown, detail: string): string =>
  typeof value === "string" && SHA256.test(value) ? value
    : fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", detail);

export const decodeOperationReplayChildOutput = (
  stdout: string,
  expected: Readonly<{
    request_sha256: string;
    coordinator_pid: number;
    parent_nonce: string;
  }>,
): Record<string, unknown> => {
  if (!stdout.endsWith("\n") || stdout.includes("\r") ||
      stdout.slice(0, -1).length === 0 ||
      stdout.slice(0, -1).includes("\n")) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "single-json-line");
  }
  let decoded: unknown;
  try {
    decoded = JSON.parse(stdout.slice(0, -1));
  } catch {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "json");
  }
  const root = record(decoded, "root");
  exactKeys(root, [
    "schema_version",
    "result",
    "request_sha256",
    "lock_sha256",
    "run_id",
    "semantic_receipt_sha256",
    "semantic_receipt",
    "node_semantic",
    "process_evidence",
    "authority_effect",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  const requestSha256 = digest(root.request_sha256, "request-sha256");
  const lockSha256 = digest(root.lock_sha256, "lock-sha256");
  const semanticReceiptSha256 = digest(
    root.semantic_receipt_sha256,
    "semantic-receipt-sha256",
  );
  if (root.schema_version !== "OperationFactoryReplayRun/v1" ||
      root.result !== "pass" || root.authority_effect !== "none" ||
      requestSha256 !== expected.request_sha256 ||
      lockSha256 !== EXPECTED_LOCK_SHA256 ||
      root.run_id !== `factory-${lockSha256.slice(0, 24)}`) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "header");
  }
  const semanticReceipt = record(
    root.semantic_receipt,
    "semantic-receipt",
  );
  exactKeys(semanticReceipt, [
    "schema_version",
    "result",
    "request_sha256",
    "lock_sha256",
    "run_id",
    "ordered_nodes",
    "claim_ceiling",
    "authority_effect",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (semanticReceipt.schema_version !== "FactorySemanticReceipt/v1" ||
      semanticReceipt.result !== "pass" ||
      semanticReceipt.request_sha256 !== requestSha256 ||
      semanticReceipt.lock_sha256 !== lockSha256 ||
      semanticReceipt.run_id !== root.run_id ||
      semanticReceipt.claim_ceiling !== OPERATION_REPLAY_CLAIM_CEILING ||
      semanticReceipt.authority_effect !== "none" ||
      sha256(canonicalJson(semanticReceipt)) !== semanticReceiptSha256) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "semantic-receipt");
  }
  if (!Array.isArray(semanticReceipt.ordered_nodes) ||
      semanticReceipt.ordered_nodes.length !== 1) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "ordered-nodes");
  }
  const nodeReceipt = record(
    semanticReceipt.ordered_nodes[0],
    "node-receipt",
  );
  exactKeys(nodeReceipt, [
    "node_id",
    "provider_id",
    "depends_on",
    "semantic_sha256",
    "replay_sha256",
    "accounting",
    "claim_ceiling",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  const nodeSemanticSha256 = digest(
    nodeReceipt.semantic_sha256,
    "node-semantic-sha256",
  );
  if (nodeReceipt.node_id !== "operation.replay.wp-rmt-002" ||
      nodeReceipt.provider_id !== "operation-wp-rmt-002-replay-v1" ||
      !Array.isArray(nodeReceipt.depends_on) ||
      nodeReceipt.depends_on.length !== 0 ||
      nodeReceipt.replay_sha256 !== nodeSemanticSha256 ||
      nodeReceipt.claim_ceiling !== OPERATION_REPLAY_CLAIM_CEILING) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "node-receipt");
  }
  const receiptAccounting = record(
    nodeReceipt.accounting,
    "node-accounting",
  );
  exactKeys(receiptAccounting, [
    "positives_declared",
    "positives_passed",
    "mutants_declared",
    "mutants_killed",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (receiptAccounting.positives_declared !== 7 ||
      receiptAccounting.positives_passed !== 7 ||
      receiptAccounting.mutants_declared !== 87 ||
      receiptAccounting.mutants_killed !== 87) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "node-accounting");
  }
  const nodeSemantic = record(root.node_semantic, "node-semantic");
  exactKeys(nodeSemantic, [
    "schema_version",
    "result",
    "provider_id",
    "semantic_output",
    "accounting",
    "claim_ceiling",
    "authority_effect",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (nodeSemantic.schema_version !== "FactoryNodeSemanticResult/v1" ||
      nodeSemantic.result !== "pass" ||
      nodeSemantic.provider_id !== "operation-wp-rmt-002-replay-v1" ||
      nodeSemantic.claim_ceiling !== OPERATION_REPLAY_CLAIM_CEILING ||
      nodeSemantic.authority_effect !== "none" ||
      sha256(canonicalJson(nodeSemantic)) !== nodeSemanticSha256) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "node-semantic");
  }
  const nodeAccounting = record(
    nodeSemantic.accounting,
    "node-semantic-accounting",
  );
  exactKeys(nodeAccounting, [
    "positives_declared",
    "positives_passed",
    "mutants_declared",
    "mutants_killed",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (canonicalJson(nodeAccounting) !== canonicalJson(receiptAccounting)) {
    return fail(
      "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID",
      "node-accounting-mismatch",
    );
  }
  const semanticOutput = record(
    nodeSemantic.semantic_output,
    "semantic-output",
  );
  exactKeys(semanticOutput, ["proof"],
    "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  const proof = record(semanticOutput.proof, "proof");
  exactKeys(proof, [
    "schema_version",
    "result",
    "parity_receipt",
    "accounting",
    "semantic_determinism",
    "claim_ceiling",
    "authority_effect",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (proof.schema_version !== "OperationFactoryReplayProof/v1" ||
      proof.result !== "pass" ||
      proof.claim_ceiling !== OPERATION_REPLAY_CLAIM_CEILING ||
      proof.authority_effect !== "none") {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "proof");
  }
  const proofAccounting = record(proof.accounting, "proof-accounting");
  exactKeys(proofAccounting, ["positives", "mutants"],
    "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  const proofPositives = record(
    proofAccounting.positives,
    "proof-positive-accounting",
  );
  const proofMutants = record(
    proofAccounting.mutants,
    "proof-mutant-accounting",
  );
  exactKeys(proofPositives, ["declared", "passed"],
    "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  exactKeys(proofMutants, ["declared", "killed"],
    "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (proofPositives.declared !== 7 || proofPositives.passed !== 7 ||
      proofMutants.declared !== 87 || proofMutants.killed !== 87) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "proof-accounting");
  }
  const semanticDeterminism = record(
    proof.semantic_determinism,
    "semantic-determinism",
  );
  exactKeys(semanticDeterminism, [
    "dynamic_pid_fields_excluded",
    "normalized_parity_digest_pinned",
    "raw_parity_digest_validated",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (semanticDeterminism.dynamic_pid_fields_excluded !== 12 ||
      semanticDeterminism.normalized_parity_digest_pinned !== true ||
      semanticDeterminism.raw_parity_digest_validated !== true) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID",
      "semantic-determinism");
  }
  const parityReceipt = record(proof.parity_receipt, "parity-receipt");
  exactKeys(parityReceipt, [
    "schema_version",
    "result",
    "providers",
    "provider_semantic_sha256",
    "provider_evidence_sha256",
    "raw_parity_sha256_validated",
    "normalized_parity",
    "normalized_parity_sha256",
    "portable_projection_sha256",
    "parity_evaluator_sha256",
    "parity_evaluator_test_sha256",
    "parity_live_test_sha256",
    "native_fresh_processes_per_semantic_execution",
    "provider_fresh_processes",
    "redacted_dynamic_pid_fields",
    "process_ids_validated_before_redaction",
    "process_ids_in_semantic_identity",
    "native_hash_byte_comparison",
    "portable_semantics_compared",
    "claim_ceiling",
    "authority_effect",
    "receipt_sha256",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  const parityReceiptSha256 = digest(
    parityReceipt.receipt_sha256,
    "parity-receipt-sha256",
  );
  const {receipt_sha256: _receiptSha256, ...parityReceiptBody} =
    parityReceipt;
  const normalizedParitySha256 = digest(
    parityReceipt.normalized_parity_sha256,
    "normalized-parity-sha256",
  );
  const normalizedParity = record(
    parityReceipt.normalized_parity,
    "normalized-parity",
  );
  const portableProjectionSha256 = digest(
    parityReceipt.portable_projection_sha256,
    "portable-projection-sha256",
  );
  const providerEvidence = record(
    parityReceipt.provider_evidence_sha256,
    "provider-evidence",
  );
  const providerSemantic = record(
    parityReceipt.provider_semantic_sha256,
    "provider-semantic",
  );
  const providerFreshProcesses = record(
    parityReceipt.provider_fresh_processes,
    "provider-fresh-processes",
  );
  for (const providerMap of [
    providerEvidence,
    providerSemantic,
    providerFreshProcesses,
  ]) {
    exactKeys(providerMap, ["typescript", "python", "rust"],
      "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  }
  if (parityReceipt.schema_version !==
        "OperationReplayParityReceipt/v1" ||
      parityReceipt.result !== "pass" ||
      parityReceipt.authority_effect !== "none" ||
      parityReceipt.claim_ceiling !== OPERATION_REPLAY_CLAIM_CEILING ||
      parityReceipt.raw_parity_sha256_validated !== true ||
      parityReceipt.redacted_dynamic_pid_fields !== 12 ||
      parityReceipt.process_ids_validated_before_redaction !== true ||
      parityReceipt.process_ids_in_semantic_identity !== false ||
      parityReceipt.native_hash_byte_comparison !== false ||
      parityReceipt.portable_semantics_compared !== true ||
      JSON.stringify(parityReceipt.providers) !== JSON.stringify([
        "operation-typescript-v1",
        "operation-python-v1",
        "operation-rust-v1",
      ]) ||
      providerEvidence.typescript !==
        "f0657f7e5e457ff4d7d9e00ef5c36b6dca139a01e0d19c197bf69778c46363bf" ||
      providerEvidence.python !==
        "6bd050443eaffa162811b4a46100ac76fa4600d89cfb99701247697eba325297" ||
      providerEvidence.rust !==
        "f31f56e5f2a158b153b572bd5e0eccc8c9f806679ad323cec29cdc0ad17495ac" ||
      digest(providerSemantic.typescript, "provider-semantic-typescript") !==
        "c231ddc63a0887a375b325de7f10b01c30bc07bf94fbc5c58f24f24934c01e7f" ||
      digest(providerSemantic.python, "provider-semantic-python") !==
        "64231a725ea839672aa5646fda53166b1d59ae67bc56b0905da21171c66a4145" ||
      digest(providerSemantic.rust, "provider-semantic-rust") !==
        "fa67b0f8bd53d3fb93041cd2c54b2e322d4f17d48cd6a7bfcdc4c4b5b4a74415" ||
      providerFreshProcesses.typescript !== 4 ||
      providerFreshProcesses.python !== 4 ||
      providerFreshProcesses.rust !== 4 ||
      parityReceipt.native_fresh_processes_per_semantic_execution !== 12 ||
      normalizedParitySha256 !== EXPECTED_NORMALIZED_PARITY_SHA256 ||
      sha256(canonicalJson(normalizedParity)) !==
        normalizedParitySha256 ||
      sha256(canonicalJson(normalizedParity.portable_projection)) !==
        portableProjectionSha256 ||
      parityReceipt.parity_evaluator_sha256 !==
        "d3e15649819d7c95c607679be4e2dcf61f938030a5c7862ec07a4a6b48a5d36d" ||
      parityReceipt.parity_evaluator_test_sha256 !==
        "9a075be3e8f5c55080cdce11e05b36a2bf8e3a9ac3e4d31562a26bd8bc5bd135" ||
      parityReceipt.parity_live_test_sha256 !==
        "a830f1e19134830db139639b9babf894ddadbef0e859068ead162af6bb0dda9c" ||
      sha256(canonicalJson(parityReceiptBody)) !== parityReceiptSha256) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "parity-receipt");
  }
  const processEvidence = record(
    root.process_evidence,
    "process-evidence",
  );
  exactKeys(processEvidence, [
    "coordinator_pid",
    "execute_child_pids",
    "replay_child_pids",
    "factory_fresh_processes_declared",
    "native_fresh_processes_per_semantic_execution",
    "parent_nonce",
  ], "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID");
  if (!Number.isSafeInteger(processEvidence.coordinator_pid) ||
      (processEvidence.coordinator_pid as number) <= 0 ||
      processEvidence.coordinator_pid !== expected.coordinator_pid ||
      processEvidence.parent_nonce !== expected.parent_nonce ||
      !Array.isArray(processEvidence.execute_child_pids) ||
      !Array.isArray(processEvidence.replay_child_pids) ||
      processEvidence.execute_child_pids.length !== 1 ||
      processEvidence.replay_child_pids.length !== 1 ||
      processEvidence.factory_fresh_processes_declared !== 2 ||
      processEvidence.native_fresh_processes_per_semantic_execution !== 12) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "process-evidence");
  }
  const childPids = [
    ...processEvidence.execute_child_pids,
    ...processEvidence.replay_child_pids,
  ];
  if (childPids.some((pid) =>
    !Number.isSafeInteger(pid) || (pid as number) <= 0 ||
    pid === processEvidence.coordinator_pid) ||
      new Set(childPids).size !== 2) {
    return fail("RMT_OP_REPLAY_CHILD_OUTPUT_INVALID", "process-ids");
  }
  return root;
};

const runOverlayChild = async (input: Readonly<{
  child_path: string;
  output_parent: string;
  cwd: string;
  environment: NodeJS.ProcessEnv;
}>): Promise<Readonly<{
  child_pid: number | null;
  exit_code: number | null;
  error: ChildFailure | null;
  stdout: string;
  stderr: string;
}>> => new Promise((accept) => {
  let observedPid: number | null = null;
  const child = execFile(process.execPath, [
    "--import",
    "tsx",
    input.child_path,
    input.output_parent,
  ], {
    cwd: input.cwd,
    env: input.environment,
    timeout: 120_000,
    maxBuffer: 1_048_576,
    encoding: "utf8",
  }, (error, stdout, stderr) => {
    const failure = error as ChildFailure | null;
    accept(Object.freeze({
      child_pid: observedPid,
      exit_code: failure === null ? 0 :
        typeof failure.code === "number" ? failure.code : null,
      error: failure,
      stdout,
      stderr,
    }));
  });
  observedPid = child.pid ?? null;
});

export const bindOperationReplayCleanupOutcome = (input: Readonly<{
  outcome: Record<string, unknown>;
  cleanup_error: string | null;
  workspace_cleaned: boolean;
}>): Record<string, unknown> => {
  if (input.cleanup_error === null && input.workspace_cleaned) {
    return input.outcome;
  }
  const cleanupFailure = input.cleanup_error ??
    "RMT_OP_REPLAY_WORKSPACE_RESIDUE";
  if (input.outcome.result === "pass") {
    return {
      ...input.outcome,
      result: "block",
      primary_failure: "RMT_OP_REPLAY_CLEANUP_FAILED",
      cleanup_failure: cleanupFailure,
      failure_exit_preserved: true,
    };
  }
  return {
    ...input.outcome,
    cleanup_failure: cleanupFailure,
  };
};

export const runOperationFactoryReplay = async (
  input: Readonly<{probe?: ReplayProbe; transcript?: string}> = {},
): Promise<Readonly<Record<string, unknown>>> => {
  const probe = input.probe ?? "pass";
  const canonicalRegistryPath = resolve(repositoryRoot, REGISTRY_RELATIVE);
  const canonicalRegistryBefore = await readFile(canonicalRegistryPath);
  const canonicalRegistrySha256 = sha256(canonicalRegistryBefore);
  if (canonicalRegistrySha256 !== EXPECTED_CANONICAL_REGISTRY_SHA256) {
    return fail("RMT_OP_REPLAY_CANONICAL_REGISTRY_DRIFT");
  }
  const request = JSON.parse(await readFile(
    resolve(repositoryRoot, REQUEST_RELATIVE),
    "utf8",
  )) as unknown;
  const requestSha256 = sha256(canonicalJson(request));
  if (requestSha256 !== EXPECTED_REQUEST_SHA256) {
    return fail("RMT_OP_REPLAY_REQUEST_DRIFT");
  }
  const workspace = await mkdtemp(resolve(
    tmpdir(),
    "domainspec-rmt-operation-replay-",
  ));
  let outcome: Record<string, unknown> = {
    schema_version: "OperationFactoryReplayInvocation/v1",
    result: "block",
    primary_failure: "RMT_OP_REPLAY_NOT_EXECUTED",
    exit_code: null,
    stdout: "",
    stderr: "",
    authority_effect: "none",
  };
  let overlayRegistrySha256: string | null = null;
  let cleanupError: string | null = null;
  try {
    const projectsRoot = resolve(workspace, "projects");
    await mkdir(projectsRoot);
    await executeFilePromise("cp", [
      "-al",
      projectRoot,
      resolve(projectsRoot, "domainspec-v2"),
    ], {timeout: 30_000, maxBuffer: 1_048_576});
    overlayRegistrySha256 = await patchOverlayRegistry(workspace);
    if (probe === "tampered-input") {
      await tamperOverlayRequest(workspace);
    }
    const overlayImplementationRoot = resolve(
      workspace,
      "projects/domainspec-v2/impl",
    );
    const childPath = resolve(workspace, CHILD_RELATIVE);
    const outputParent = resolve(workspace, "factory-output");
    const runtimeTmp = resolve(workspace, "runtime-tmp");
    await mkdir(runtimeTmp);
    const environment: NodeJS.ProcessEnv = Object.fromEntries([
      "PATH", "HOME", "CARGO_HOME", "RUSTUP_HOME",
    ].filter((key) => process.env[key] !== undefined)
      .map((key) => [key, process.env[key]!]));
    environment.TMPDIR = runtimeTmp;
    const parentNonce = randomBytes(32).toString("hex");
    environment.DOMAINSPEC_OPERATION_REPLAY_PARENT_NONCE = parentNonce;
    if (probe === "nonzero-with-valid-output") {
      environment.DOMAINSPEC_OPERATION_REPLAY_VALID_OUTPUT_NONZERO = "1";
    } else if ([
      "malformed-output",
      "multiple-line-output",
      "empty-output",
      "surplus-output",
    ].includes(probe)) {
      environment.DOMAINSPEC_OPERATION_REPLAY_OUTPUT_PROBE = probe;
    } else if (probe === "replayed-transcript") {
      if (typeof input.transcript !== "string" ||
          input.transcript.length === 0) {
        return fail("RMT_OP_REPLAY_TRANSCRIPT_PROBE_INVALID");
      }
      const transcriptPath = resolve(workspace, "replayed-transcript.jsonl");
      await writeFile(transcriptPath, input.transcript, {
        encoding: "utf8",
        flag: "wx",
      });
      environment.DOMAINSPEC_OPERATION_REPLAY_TRANSCRIPT_PATH =
        transcriptPath;
    }
    const childRun = await runOverlayChild({
      child_path: childPath,
      output_parent: outputParent,
      cwd: overlayImplementationRoot,
      environment,
    });
    const {stdout, stderr} = childRun;
    if (childRun.error === null && childRun.exit_code === 0 &&
        childRun.child_pid !== null) {
      let rendered: Record<string, unknown>;
      try {
        rendered = decodeOperationReplayChildOutput(stdout, {
          request_sha256: requestSha256,
          coordinator_pid: childRun.child_pid,
          parent_nonce: parentNonce,
        });
      } catch (error: unknown) {
        outcome = {
          schema_version: "OperationFactoryReplayInvocation/v1",
          result: "block",
          primary_failure: error instanceof Error
            ? error.message.split(":")[0]
            : "RMT_OP_REPLAY_CHILD_OUTPUT_INVALID",
          exit_code: 0,
          stdout,
          stderr,
          stdout_sha256: sha256(stdout),
          stderr_sha256: sha256(stderr),
          output_validation_failure_preserved: true,
          failure_exit_preserved: true,
          authority_effect: "none",
        };
        rendered = {};
      }
      if (Object.keys(rendered).length === 0) {
        // The exact output decoder has already preserved the block outcome.
      } else if (probe !== "pass") {
        outcome = {
          schema_version: "OperationFactoryReplayInvocation/v1",
          result: "block",
          primary_failure: "RMT_OP_REPLAY_FAILURE_PROBE_PASSED",
          exit_code: 0,
          stdout,
          stderr,
          authority_effect: "none",
        };
      } else {
        outcome = {
          ...rendered,
          invocation_schema_version:
            "OperationFactoryReplayInvocation/v1",
          exit_code: 0,
          stdout_sha256: sha256(stdout),
          stderr_sha256: sha256(stderr),
          child_stdout: stdout,
          spawned_coordinator_pid: childRun.child_pid,
          failure_exit_preserved: true,
          authority_effect: "none",
        };
      }
    } else {
      const failure = childRun.error;
      const exitCode = childRun.exit_code;
      outcome = {
        schema_version: "OperationFactoryReplayInvocation/v1",
        result: "block",
        primary_failure: exitCode === null
          ? "RMT_OP_REPLAY_CHILD_EXECUTION_FAILED"
          : "RMT_OP_REPLAY_CHILD_NONZERO",
        exit_code: exitCode,
        stdout,
        stderr: stderr || failure?.message || "",
        stdout_sha256: sha256(stdout),
        stderr_sha256: sha256(stderr || failure?.message || ""),
        spawned_coordinator_pid: childRun.child_pid,
        failure_exit_preserved: exitCode !== null && exitCode !== 0,
        authority_effect: "none",
      };
    }
  } finally {
    try {
      await rm(workspace, {recursive: true, force: true});
    } catch (error: unknown) {
      cleanupError = error instanceof Error ? error.message : String(error);
    }
  }
  const workspaceCleaned = await absent(workspace);
  const canonicalRegistryAfter = await readFile(canonicalRegistryPath);
  const canonicalRegistryUnchanged =
    sha256(canonicalRegistryAfter) === canonicalRegistrySha256 &&
    canonicalRegistryAfter.equals(canonicalRegistryBefore);
  if (!canonicalRegistryUnchanged) {
    return fail("RMT_OP_REPLAY_CANONICAL_REGISTRY_MUTATED");
  }
  const terminalOutcome = bindOperationReplayCleanupOutcome({
    outcome,
    cleanup_error: cleanupError,
    workspace_cleaned: workspaceCleaned,
  });
  return Object.freeze({
    ...terminalOutcome,
    probe,
    canonical_registry_sha256: canonicalRegistrySha256,
    overlay_registry_sha256: overlayRegistrySha256,
    canonical_registry_unchanged: canonicalRegistryUnchanged,
    canonical_provider_ids_absent: PROVIDER_IDS,
    overlay_strategy: "hardlink-copy-on-write",
    workspace_path: workspace,
    workspace_cleaned: workspaceCleaned,
    cleanup_error: cleanupError,
    cleanup_did_not_replace_primary_exit: outcome.result === "block",
    authority_effect: "none",
  });
};
