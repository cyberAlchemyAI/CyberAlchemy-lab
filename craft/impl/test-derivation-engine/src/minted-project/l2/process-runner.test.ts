import { describe, expect, it } from "vitest";

import { requireCompletedProcess, runBoundedProcess } from "./process-runner.js";

const policy = {
  cwd: process.cwd(),
  timeoutMs: 2000,
  maxOutputBytes: 1024,
  network: "forbidden" as const,
  networkIsolation: {
    kind: "inherited-linux-network-namespace" as const,
    process_namespace: "net:[2]",
    host_namespace: "net:[1]",
  },
};

describe("EVF L2 bounded process runner", () => {
  it("captures an exact no-shell invocation", async () => {
    const evidence = await runBoundedProcess(
      process.execPath,
      ["-e", "process.stdout.write('ok')"],
      policy,
    );
    expect(requireCompletedProcess(evidence).stdout.toString()).toBe("ok");
    expect(evidence.argv).toEqual([process.execPath, "-e", "process.stdout.write('ok')"]);
  });

  it("preserves nonzero exit as failure", async () => {
    const evidence = await runBoundedProcess(
      process.execPath,
      ["-e", "process.exit(7)"],
      policy,
    );
    expect(() => requireCompletedProcess(evidence))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_EXECUTION_FAILED" }));
  });

  it("preserves timeout even after cleanup completes", async () => {
    const evidence = await runBoundedProcess(
      process.execPath,
      ["-e", "setTimeout(() => {}, 10000)"],
      { ...policy, timeoutMs: 25 },
    );
    expect(evidence.timed_out).toBe(true);
    expect(() => requireCompletedProcess(evidence))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_TIMEOUT" }));
  });

  it("rejects oversized combined output", async () => {
    const evidence = await runBoundedProcess(
      process.execPath,
      ["-e", "process.stdout.write('x'.repeat(2048))"],
      { ...policy, maxOutputBytes: 32 },
    );
    expect(evidence.output_limit_exceeded).toBe(true);
    expect(() => requireCompletedProcess(evidence))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_OUTPUT_INVALID" }));
  });
});
