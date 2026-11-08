import {execFile} from "node:child_process";
import {existsSync, readdirSync, rmdirSync} from "node:fs";
import {join} from "node:path";
import {describe, expect, it} from "vitest";

const runner = "projects/domainspec-v2/impl/architecture-conformance/acceptance/event/wp-rmt-002/replay/run-event-parity.ts";
const tsx = "projects/domainspec-v2/impl/node_modules/.bin/tsx";
const cargoRoot = "projects/domainspec-v2/development/remaining-meta-types/runs/event/cargo-target";
const childEnv = () => {
  const userHome = process.env.HOME;
  if (!userHome) throw new Error("RMT_EVENT_REPLAY_HOME_MISSING");
  return {PATH: process.env.PATH ?? "", HOME: userHome, CARGO_HOME: process.env.CARGO_HOME ?? join(userHome, ".cargo"), RUSTUP_HOME: process.env.RUSTUP_HOME ?? join(userHome, ".rustup")};
};
type Attempt = {status: number; stdout: string; stderr: string; pid: number};
const execute = (mode: string): Promise<Attempt> => new Promise(resolve => {
  const child = execFile(tsx, [runner, mode], {cwd: process.cwd(), env: childEnv(), maxBuffer: 4 * 1024 * 1024}, (error, stdout, stderr) => resolve({status: typeof (error as NodeJS.ErrnoException | null)?.code === "number" ? (error as unknown as {code: number}).code : 0, stdout, stderr, pid: child.pid!}));
});
const decode = (stdout: string) => {
  const lines = stdout.split(/\r?\n/u).filter(Boolean);
  if (lines.length !== 1) throw new Error("RMT_EVENT_REPLAY_RECEIPT_CARDINALITY");
  return JSON.parse(lines[0]!);
};
const removeWhenEmpty = async () => {
  for (let index = 0; index < 300; index++) {
    if (!existsSync(cargoRoot)) return;
    if (readdirSync(cargoRoot).length === 0) { rmdirSync(cargoRoot); return; }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error("RMT_EVENT_REPLAY_CARGO_ROOT_NOT_EMPTY");
};

describe("WP-RMT-002 Event fresh-process replay", () => {
  it("replays all providers, durable retries, recovery, and non-idempotent rejection in two real processes", async () => {
    expect(existsSync(cargoRoot), "pre-existing Cargo root is preserved and blocks this proof").toBe(false);
    const attempts = await Promise.all([execute("--emit"), execute("--emit")]);
    for (const attempt of attempts) expect(attempt.status, attempt.stderr).toBe(0);
    expect(attempts[0]!.pid).not.toBe(attempts[1]!.pid);
    const receipts = attempts.map(({stdout}) => decode(stdout));
    expect(receipts[1]).toEqual(receipts[0]);
    expect(receipts[0]).toMatchObject({result: "pass", fresh_process_count_declared: 2, provider_attempt_count: 12, provider_ids: ["event-typescript-v1", "event-python-v1", "event-rust-v1"], recovery_replay_stable: true, recovery_same_occurrence_and_outcome: true, recovery_mismatch_rejected_by_all_providers: true, non_idempotent_retry_rejected_by_all_providers: true, acknowledgement_ambiguity_preserves_durable_facts: true, parity_receipt: {sha256: "17fbbf95a213973cdd08d30f44f37124696f7634aaa049d28af912b5201d6053"}, authority_effect: "none"});
    expect(receipts[0].s1_replay_controls.map(({hostile_id}: {hostile_id: string}) => hostile_id)).toEqual(["s1/recovery-replay", "s1/non-idempotent-retry"]);
    for (const retry of receipts[0].retry_attempts) { expect(retry.occurrence_id).toBe("settlement:req-1"); expect(new Set(retry.publication_attempt_ids).size).toBe(2); }
    for (const control of receipts[0].s1_replay_controls) { expect(control.required_residue.occurrence_id).toBe("settlement:req-1"); expect(control.provider_ids).toEqual(receipts[0].provider_ids); }
    expect(attempts[0]!.stdout).not.toContain(String(attempts[0]!.pid));
    await removeWhenEmpty();
    expect(existsSync(cargoRoot)).toBe(false);
  }, 120_000);

  it("preserves nonzero failure and rejects malformed multi-receipt output", async () => {
    const failed = await execute("--fail");
    expect(failed.status).toBe(23);
    expect(failed.stderr).toContain("RMT_EVENT_REPLAY_PROBE_FAILURE");
    const malformed = await execute("--malformed-output");
    expect(malformed.status).toBe(0);
    expect(() => decode(malformed.stdout)).toThrowError("RMT_EVENT_REPLAY_RECEIPT_CARDINALITY");
    expect(existsSync(cargoRoot)).toBe(false);
  });
});
