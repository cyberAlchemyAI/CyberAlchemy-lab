import {execFile} from "node:child_process";
import {lstat, mkdtemp, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {canonicalJson, sha256} from "../../../../factory/shared/canonical.js";

const here = dirname(fileURLToPath(import.meta.url));
const childPath = resolve(here, "replay-child.ts");
const implRoot = resolve(here, "../../../../..");
const repositoryRoot = resolve(implRoot, "../../..");
const userHomePath = process.env.HOME;
if (userHomePath === undefined) {
  throw Object.assign(new Error("RMT_RULE_REPLAY_TOOLCHAIN_HOME_MISSING"), {
    code: "RMT_RULE_REPLAY_TOOLCHAIN_HOME_MISSING",
  });
}

type Probe = "none" | "malformed-output" | "nonzero-with-valid-output";
type ChildResult = Readonly<{
  pid: number | null;
  exit_code: number | null;
  stdout: string;
  stderr: string;
}>;

const runChild = (probe: Probe): Promise<ChildResult> => new Promise((accept) => {
  let pid: number | null = null;
  const child = execFile(process.execPath, [
    "--import", "tsx", childPath,
  ], {
    cwd: implRoot,
    env: {
      PATH: process.env.PATH ?? "",
      DOMAINSPEC_RULE_REPLAY_PROBE: probe === "none" ? "" : probe,
      DOMAINSPEC_RULE_REPLAY_REPOSITORY_ROOT: repositoryRoot,
      PYTHONDONTWRITEBYTECODE: "1",
      CARGO_HOME: process.env.CARGO_HOME ?? resolve(userHomePath, ".cargo"),
      RUSTUP_HOME: process.env.RUSTUP_HOME ?? resolve(userHomePath, ".rustup"),
    },
    timeout: 120_000,
    maxBuffer: 1_048_576,
    encoding: "utf8",
  }, (error, stdout, stderr) => {
    const failure = error as (Error & {code?: number | string}) | null;
    accept(Object.freeze({
      pid,
      exit_code: failure === null ? 0 :
        typeof failure.code === "number" ? failure.code : null,
      stdout,
      stderr,
    }));
  });
  pid = child.pid ?? null;
});

const parseSingleReceipt = (stdout: string): Record<string, unknown> | null => {
  const lines = stdout.split("\n");
  if (lines.at(-1) === "") lines.pop();
  if (lines.length !== 1 || lines[0] === "") return null;
  try {
    const value: unknown = JSON.parse(lines[0]!);
    return value !== null && typeof value === "object" &&
      !Array.isArray(value) ? value as Record<string, unknown> : null;
  } catch {
    return null;
  }
};

const absent = async (path: string): Promise<boolean> => {
  try {
    await lstat(path);
    return false;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return true;
    throw error;
  }
};

export const runRuleReplay = async (input: Readonly<{
  probe?: Probe;
}> = {}) => {
  const probe = input.probe ?? "none";
  const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-rule-replay-"));
  let primary: Record<string, unknown>;
  try {
    const children = await Promise.all([runChild(probe), runChild(probe)]);
    const parsed = children.map(({stdout}) => parseSingleReceipt(stdout));
    const nonzero = children.find(({exit_code: code}) => code !== 0);
    if (nonzero !== undefined) {
      primary = {
        schema_version: "RuleWpRmt002ReplayResult/v1",
        result: "block",
        primary_failure: "RMT_RULE_REPLAY_CHILD_NONZERO",
        exit_code: nonzero.exit_code,
        failure_exit_preserved: true,
        valid_output_did_not_mask_failure:
          parseSingleReceipt(nonzero.stdout) !== null,
        child_pids: children.map(({pid}) => pid),
        authority_effect: "none",
      };
    } else if (parsed.some((value) => value === null)) {
      primary = {
        schema_version: "RuleWpRmt002ReplayResult/v1",
        result: "block",
        primary_failure: "RMT_RULE_REPLAY_CHILD_OUTPUT_INVALID",
        exit_code: 0,
        failure_exit_preserved: true,
        child_pids: children.map(({pid}) => pid),
        authority_effect: "none",
      };
    } else {
      const receipts = parsed as Record<string, unknown>[];
      const receiptDigests = receipts.map((receipt) =>
        sha256(canonicalJson(receipt)));
      const childPids = children.map(({pid}) => pid);
      const pidsValid = childPids.every((pid) =>
        Number.isSafeInteger(pid) && (pid as number) > 0 &&
        pid !== process.pid) && new Set(childPids).size === 2;
      if (new Set(receiptDigests).size !== 1 || !pidsValid) {
        primary = {
          schema_version: "RuleWpRmt002ReplayResult/v1",
          result: "block",
          primary_failure: "RMT_RULE_REPLAY_NONDETERMINISTIC",
          exit_code: 0,
          failure_exit_preserved: true,
          child_pids: childPids,
          authority_effect: "none",
        };
      } else {
        primary = {
          schema_version: "RuleWpRmt002ReplayResult/v1",
          result: "pass",
          exit_code: 0,
          semantic_receipt_sha256: receiptDigests[0],
          semantic_receipts_deterministic: true,
          fresh_process_count_declared: 2,
          child_pids: childPids,
          child_process_ids_excluded_from_semantic_identity: true,
          semantic_receipt: receipts[0],
          failure_exit_preserved: true,
          authority_effect: "none",
        };
      }
    }
  } finally {
    await rm(workspace, {recursive: true});
  }
  const workspaceCleaned = await absent(workspace);
  if (!workspaceCleaned && primary!.result === "pass") {
    return Object.freeze({
      ...primary!,
      result: "block" as const,
      primary_failure: "RMT_RULE_REPLAY_WORKSPACE_RESIDUE",
      workspace_path: workspace,
      workspace_cleaned: false,
    });
  }
  return Object.freeze({
    ...primary!,
    workspace_path: workspace,
    workspace_cleaned: workspaceCleaned,
    cleanup_did_not_replace_primary_failure: true,
  });
};
