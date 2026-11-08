import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { chmodSync, copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeAll, describe, expect, it } from "vitest";

import type { SelectedSfolClaimSources } from "./index.js";
import { observeSelectedSfolNative, replaySelectedSfolNative,
  type ExactNativeExecutable, type SelectedSfolNativeExecution } from "./native-link.js";

const repoRoot = fileURLToPath(new URL("../../../../../../../../", import.meta.url));
const authRoot = join(repoRoot, "auth-foundation");
const manifest = join(authRoot, "implementation/sfol-conformance/Cargo.toml");
const binary = join(authRoot, "implementation/sfol-conformance/target/debug/auth-foundation-sfol-conformance");
const selection = JSON.parse(readFileSync(new URL("./examples/auth-command-boundary.selection.json", import.meta.url), "utf8")) as SelectedSfolClaimSources;
const sha = (value: Buffer | string) => createHash("sha256").update(value).digest("hex");
const tempRoots: string[] = [];

function executable(path: string): ExactNativeExecutable {
  return { path, sha256: sha(readFileSync(path)), size_bytes: statSync(path).size };
}

function policy(path = binary): SelectedSfolNativeExecution {
  return { executable: executable(path), timeout_ms: 5000, max_output_bytes: 4096 };
}

function script(body: string): string {
  const root = mkdtempSync(join(tmpdir(), "tde-auth-sfol-native-"));
  tempRoots.push(root);
  const path = join(root, "native-case-adapter");
  writeFileSync(path, `#!/bin/sh\n${body}\n`, { mode: 0o700 });
  chmodSync(path, 0o700);
  return path;
}

beforeAll(() => {
  execFileSync(join(repoRoot, "tools/toolchain/run"),
    ["cargo", "build", "--offline", "--locked", "--manifest-path", manifest],
    { cwd: repoRoot, timeout: 120_000, stdio: "pipe" });
}, 125_000);
afterEach(() => { for (const path of tempRoots.splice(0)) rmSync(path, { recursive: true, force: true }); });

describe("selected Auth SFOL to native observations", () => {
  it("replays all eight derived cases against the real Rust command-boundary executable", async () => {
    const execution = policy();
    const link = await observeSelectedSfolNative(authRoot, selection, execution);
    expect(link.status).toBe("matched");
    expect(link.observations).toHaveLength(8);
    expect(link.observations.filter(row => row.observed_value === true)).toHaveLength(1);
    expect(link.observations.filter(row => row.observed_value === false)).toHaveLength(7);
    expect(link.observations.every(row => row.comparison === "match")).toBe(true);
    expect(link.mode).toBe("trusted-local-no-isolation");
    expect(link.admission_origin_verification).toBe("not-performed");
    expect(link.binary_build_provenance).toBe("not-verified");
    expect(link.f5_eligibility).toBe("blocked-missing-domainspec-v4-chain");
    expect(link.evf_join).toBe("forbidden");
    expect(link.can_satisfy_obligation).toBe(false);
    expect(await replaySelectedSfolNative(authRoot, selection, execution, link)).toEqual(link);
  }, 20_000);

  it("rejects missing, reordered and rewritten observations even with a rehashed held link", async () => {
    const execution = policy();
    const link = await observeSelectedSfolNative(authRoot, selection, execution);
    for (const change of [
      (held: any) => { held.observations.pop(); },
      (held: any) => { held.observations.reverse(); },
      (held: any) => { held.observations[0].observed_value = false; },
      (held: any) => { held.observations[0].case_id = "swapped-case"; },
    ]) {
      const held = structuredClone(link) as any;
      change(held);
      held.link_digest = sha(JSON.stringify(held));
      await expect(replaySelectedSfolNative(authRoot, selection, execution, held))
        .rejects.toThrow(/SFOL_NATIVE_LINK_REPLAY_MISMATCH/);
    }
  }, 20_000);

  it("detects wrong Boolean output and refuses matched replay", async () => {
    const execution = policy(script("printf 'false\\n'"));
    const link = await observeSelectedSfolNative(authRoot, selection, execution);
    expect(link.status).toBe("not-matched");
    expect(link.observations.some(row => row.comparison === "mismatch")).toBe(true);
    expect(link.can_satisfy_obligation).toBe(false);
    await expect(replaySelectedSfolNative(authRoot, selection, execution, link))
      .rejects.toThrow(/SFOL_NATIVE_LINK_REPLAY_MISMATCH/);
  });

  it("treats malformed, nonzero and timed-out native results as incomplete", async () => {
    for (const [body, timeout] of [["printf 'maybe\\n'", 5000], ["exit 2", 5000], ["/bin/sleep 2", 25]] as const) {
      const execution = { ...policy(script(body)), timeout_ms: timeout };
      const link = await observeSelectedSfolNative(authRoot, selection, execution);
      expect(link.status).toBe("not-matched");
      expect(link.observations).toHaveLength(1);
      expect(link.observations[0]?.comparison).toBe("incomplete");
    }
  }, 15_000);

  it("fails closed when the independently selected executable bytes drift", async () => {
    const path = script("printf 'true\\n'");
    const execution = policy(path);
    writeFileSync(path, "#!/bin/sh\nprintf 'false\\n'\n", { mode: 0o700 });
    await expect(observeSelectedSfolNative(authRoot, selection, execution))
      .rejects.toThrow(/SFOL_NATIVE_EXECUTABLE_DRIFT/);
  });

  it("rejects a forged held replay link before any native invocation", async () => {
    const root = mkdtempSync(join(tmpdir(), "tde-auth-sfol-marker-"));
    tempRoots.push(root);
    const marker = join(root, "invoked");
    const path = script(`printf 'invoked' >> '${marker}'\nprintf 'false\\n'`);
    await expect(replaySelectedSfolNative(authRoot, selection, policy(path), {} as any))
      .rejects.toThrow(/SFOL_NATIVE_LINK_REPLAY_MISMATCH/);
    expect(existsSync(marker)).toBe(false);
  });

  it("rejects a self-consistent rehashed counterfeit Auth admission selection", async () => {
    const root = mkdtempSync(join(tmpdir(), "tde-auth-sfol-counterfeit-"));
    tempRoots.push(root);
    for (const ref of [selection.decision, selection.claim, selection.module, selection.clause_manifest]) {
      const target = join(root, ref.path);
      mkdirSync(dirname(target), { recursive: true });
      copyFileSync(join(authRoot, ref.path), target);
    }
    const decisionPath = join(root, selection.decision.path);
    const decision = JSON.parse(readFileSync(decisionPath, "utf8"));
    decision.description = "counterfeit source with a recomputed caller reference";
    writeFileSync(decisionPath, JSON.stringify(decision));
    const counterfeit = { ...selection, decision: { ...executable(decisionPath), path: selection.decision.path } };
    await expect(observeSelectedSfolNative(root, counterfeit, policy()))
      .rejects.toThrow(/SFOL_NATIVE_AUTH_SOURCE_NOT_PINNED/);
  });
});
