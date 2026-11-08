import { execFileSync, type SpawnOptions } from "node:child_process";
import { createHash } from "node:crypto";
import { chmodSync, mkdtempSync, readFileSync, realpathSync, rmSync, statSync, truncateSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";

const launchTrace = vi.hoisted(() => ({ calls: [] as Array<{ command: string; args: string[] }> }));
vi.mock("node:child_process", async importOriginal => {
  const actual = await importOriginal<typeof import("node:child_process")>();
  return { ...actual, spawn: (command: string, args: string[], options: SpawnOptions) => {
    launchTrace.calls.push({ command, args: [...args] });
    return actual.spawn(command, args, options);
  } };
});

import { digestSfolValue } from "../cases/index.js";
import type { SelectedSfolClaimSources } from "./index.js";
import type { ExactNativeExecutable } from "./native-link.js";
import { observeSelectedSfolNativePolicy, replaySelectedSfolNativePolicy,
  type SelectedSfolPolicyExecution } from "./native-policy-link.js";

const repoRoot = fileURLToPath(new URL("../../../../../../../../", import.meta.url));
const authRoot = join(repoRoot, "auth-foundation");
const manifest = join(authRoot, "implementation/sfol-conformance/Cargo.toml");
const binary = join(authRoot, "implementation/sfol-conformance/target/debug/auth-foundation-sfol-conformance");
const selection = JSON.parse(readFileSync(new URL("./examples/auth-command-boundary.selection.json", import.meta.url), "utf8")) as SelectedSfolClaimSources;
const sha = (bytes: Buffer) => createHash("sha256").update(bytes).digest("hex");
const tempRoots: string[] = [];
afterEach(() => { for (const path of tempRoots.splice(0)) rmSync(path, { recursive: true, force: true }); });
function ref(path: string): ExactNativeExecutable {
  const bytes = readFileSync(path);
  return { path, sha256: sha(bytes), size_bytes: statSync(path).size };
}
function policy(path = binary): SelectedSfolPolicyExecution {
  return { executable: ref(path), bwrap: ref("/usr/bin/bwrap"), prlimit: ref("/usr/bin/prlimit"),
    probe_python: ref(realpathSync("/usr/bin/python3")), address_space_limit_bytes: 128 * 1024 * 1024,
    probe_timeout_ms: 5000, probe_max_output_bytes: 4096,
    timeout_ms: 5000, max_output_bytes: 4096 };
}
function script(body: string): string {
  const base = mkdtempSync(join(tmpdir(), "tde-auth-sfol-policy-"));
  tempRoots.push(base);
  const path = join(base, "native-case-adapter");
  writeFileSync(path, `#!/bin/sh\n${body}\n`, { mode: 0o700 });
  chmodSync(path, 0o700);
  return path;
}

beforeAll(() => {
  execFileSync(join(repoRoot, "tools/toolchain/run"),
    ["cargo", "build", "--offline", "--locked", "--manifest-path", manifest],
    { cwd: repoRoot, timeout: 120_000, stdio: "pipe" });
}, 125_000);

describe("selected SFOL policy-constrained native link", () => {
  it("probes the pinned launcher, observes eight Rust cases, and independently replays", async () => {
    const execution = policy();
    const link = await observeSelectedSfolNativePolicy(authRoot, selection, execution);
    expect(link.launcher_probe).toEqual({ network_namespace_separate: true, interfaces: ["lo"],
      default_route: false, network_attempt_errno: 101,
      address_space_soft_limit_bytes: execution.address_space_limit_bytes,
      address_space_hard_limit_bytes: execution.address_space_limit_bytes,
      over_limit_allocation_failed: true });
    expect(link.status).toBe("matched");
    expect(link.schema_version).toBe("tde.selected-sfol-native-policy-link/v3-candidate");
    expect(link.observations).toHaveLength(8);
    expect(link.observations.filter(row => row.observed_value === true)).toHaveLength(1);
    expect(link.observations.every(row => row.comparison === "match")).toBe(true);
    expect(link.evf_join).toBe("forbidden");
    expect(link.can_satisfy_obligation).toBe(false);
    expect(link.claim_ceiling).toContain("no complete network denial");
    expect(await replaySelectedSfolNativePolicy(authRoot, selection, execution, link)).toEqual(link);
  }, 30_000);

  it("replays a selected temporary executable without exposing its unselected siblings", async () => {
    const adapter = script(
      "if [ -e \"$(dirname \"$0\")/unselected-sibling\" ]; then exit 23; fi\n" +
      "if [ \"$1\" = true ] && [ \"$2\" = true ] && [ \"$3\" = true ]; then\n" +
      "  printf 'true\\n'\nelse\n  printf 'false\\n'\nfi",
    );
    writeFileSync(join(dirname(adapter), "unselected-sibling"), "unselected fixture\n");
    const execution = policy(adapter);
    launchTrace.calls.length = 0;
    const link = await observeSelectedSfolNativePolicy(authRoot, selection, execution);
    expect(link.status).toBe("matched");
    expect(link.observations).toHaveLength(8);
    expect(link.observations.every(row => row.comparison === "match")).toBe(true);
    expect(link.evf_join).toBe("forbidden");
    expect(link.can_satisfy_obligation).toBe(false);
    expect(launchTrace.calls).toHaveLength(9);
    expect(launchTrace.calls[0]?.args).not.toContain(adapter);
    for (const call of launchTrace.calls.slice(1)) {
      const privateTmp = call.args.findIndex((arg, index) =>
        arg === "--tmpfs" && call.args[index + 1] === "/tmp");
      const selectedFile = call.args.findIndex((arg, index) =>
        arg === "--ro-bind" && call.args[index + 1] === adapter &&
        call.args[index + 2] === adapter);
      expect(privateTmp).toBeGreaterThanOrEqual(0);
      expect(selectedFile).toBeGreaterThan(privateTmp);
      expect(call.args.some((arg, index) => arg === "--ro-bind" &&
        ["/tmp", dirname(adapter)].includes(call.args[index + 1] ?? ""))).toBe(false);
    }
    expect(await replaySelectedSfolNativePolicy(authRoot, selection, execution, link)).toEqual(link);
  }, 30_000);

  it("rejects launcher byte drift before any selected case", async () => {
    const execution = policy();
    const changed = { ...execution, bwrap: { ...execution.bwrap, sha256: "0".repeat(64) } };
    await expect(observeSelectedSfolNativePolicy(authRoot, selection, changed)).rejects.toThrow(/EXACT_REF_DRIFT/);
    await expect(observeSelectedSfolNativePolicy(authRoot, selection,
      { ...execution, executable: { ...execution.executable, sha256: "0".repeat(64) } }))
      .rejects.toThrow(/EXACT_REF_DRIFT/);
    await expect(observeSelectedSfolNativePolicy(authRoot,
      { ...selection, module: { ...selection.module, sha256: "0".repeat(64) } }, execution))
      .rejects.toThrow(/AUTH_SOURCE_NOT_PINN/);
  });

  it("rejects an oversized actual executable before reading its bytes", async () => {
    const oversized = script("exit 0");
    truncateSync(oversized, 64 * 1024 * 1024 + 1);
    const execution = { ...policy(), executable: {
      path: oversized, sha256: "0".repeat(64), size_bytes: 64 * 1024 * 1024,
    } };
    await expect(observeSelectedSfolNativePolicy(authRoot, selection, execution))
      .rejects.toThrow(/EXACT_REF_DRIFT/);
  });

  it("rejects a missing or counterfeit launcher path", async () => {
    const execution = policy();
    const counterfeit = script("exit 0");
    await expect(observeSelectedSfolNativePolicy(authRoot, selection,
      { ...execution, bwrap: ref(counterfeit) })).rejects.toThrow(/LAUNCHER_PATH_INVALID/);
    await expect(observeSelectedSfolNativePolicy(authRoot, selection,
      { ...execution, probe_python: { ...execution.probe_python, path: "/usr/bin/not-a-python" } }))
      .rejects.toThrow();
  });

  it("keeps a wrong native output non-matching under the checked launcher", async () => {
    const execution = policy(script("printf 'false\\n'"));
    const link = await observeSelectedSfolNativePolicy(authRoot, selection, execution);
    expect(link.status).toBe("not-matched");
    expect(link.observations.some(row => row.comparison === "mismatch")).toBe(true);
    await expect(replaySelectedSfolNativePolicy(authRoot, selection, execution, link))
      .rejects.toThrow(/REPLAY_MISMATCH/);
  });

  it("keeps nonzero, timed-out and oversized native outcomes incomplete", async () => {
    for (const [body, change, expectedFlag] of [
      ["exit 17", {}, "exit_code"],
      ["sleep 2", { timeout_ms: 300 }, "timed_out"],
      ["head -c 5000 /dev/zero", { max_output_bytes: 1 }, "output_limit_exceeded"],
    ] as const) {
      const execution = { ...policy(script(body)), ...change };
      const link = await observeSelectedSfolNativePolicy(authRoot, selection, execution);
      expect(link.status).toBe("not-matched");
      expect(link.observations).toHaveLength(1);
      expect(link.observations[0]?.comparison).toBe("incomplete");
      expect(link.observations[0]?.[expectedFlag]).toBe(expectedFlag === "exit_code" ? 17 : true);
      await expect(replaySelectedSfolNativePolicy(authRoot, selection, execution, link))
        .rejects.toThrow(/REPLAY_MISMATCH/);
    }
  }, 20_000);

  it("strictly validates distinct probe and case bounds", async () => {
    const execution = policy();
    for (const change of [
      { probe_timeout_ms: 0 }, { probe_timeout_ms: 30_001 }, { probe_timeout_ms: 1.5 },
      { probe_max_output_bytes: 0 }, { probe_max_output_bytes: 65_537 },
      { probe_max_output_bytes: Number.NaN },
    ]) {
      await expect(observeSelectedSfolNativePolicy(authRoot, selection, { ...execution, ...change }))
        .rejects.toThrow(/EXECUTION_INVALID/);
    }
    const { probe_timeout_ms: _omitted, ...missing } = execution;
    await expect(observeSelectedSfolNativePolicy(authRoot, selection,
      missing as SelectedSfolPolicyExecution)).rejects.toThrow(/EXECUTION_INVALID/);
    await expect(observeSelectedSfolNativePolicy(authRoot, selection,
      { ...execution, unexpected: true } as SelectedSfolPolicyExecution)).rejects.toThrow(/EXECUTION_INVALID/);
  });

  it("fails a bounded launcher probe before running any native case", async () => {
    const adapter = script("exit 0");
    const execution = { ...policy(adapter), probe_max_output_bytes: 1 };
    launchTrace.calls.length = 0;
    await expect(observeSelectedSfolNativePolicy(authRoot, selection, execution))
      .rejects.toThrow(/^SFOL_POLICY_PROBE_FAILED:output-limit$/);
    expect(launchTrace.calls).toHaveLength(1);
    expect(launchTrace.calls[0]?.command).toBe(execution.prlimit.path);
    expect(launchTrace.calls[0]?.args).toContain(execution.probe_python.path);
    expect(launchTrace.calls.some(call => call.args.includes(adapter))).toBe(false);
  });

  it("rejects a forged held probe, reordered cases, changed policy, and recomputed digest", async () => {
    const execution = policy();
    const link = await observeSelectedSfolNativePolicy(authRoot, selection, execution);
    for (const change of [
      (held: any) => { held.launcher_probe.over_limit_allocation_failed = false; },
      (held: any) => { held.observations.reverse(); },
      (held: any) => { held.observations[0].observed_value = false; },
      (held: any) => { held.observations.pop(); },
      (held: any) => { held.execution.address_space_limit_bytes += 1; },
      (held: any) => { held.execution.probe_timeout_ms += 1; },
      (held: any) => { held.execution.probe_max_output_bytes += 1; },
      (held: any) => { held.schema_version = "tde.selected-sfol-native-policy-link/v2-candidate"; },
    ]) {
      const held = structuredClone(link) as any;
      change(held);
      const { link_digest: _digest, ...unsigned } = held;
      held.link_digest = digestSfolValue(unsigned);
      await expect(replaySelectedSfolNativePolicy(authRoot, selection, execution, held))
        .rejects.toThrow(/REPLAY_MISMATCH/);
    }
  }, 30_000);
});
