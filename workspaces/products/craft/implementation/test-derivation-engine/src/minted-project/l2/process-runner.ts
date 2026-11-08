import { spawn } from "node:child_process";

import { fail, type ProcessEvidence } from "./types.js";

export type ProcessPolicy = {
  readonly cwd: string;
  readonly timeoutMs: number;
  readonly maxOutputBytes: number;
  readonly network: "forbidden";
  readonly networkIsolation: {
    readonly kind: "inherited-linux-network-namespace";
    readonly process_namespace: string;
    readonly host_namespace: string;
  };
  readonly environment?: Readonly<Record<string, string>>;
};

export async function runBoundedProcess(
  executable: string,
  args: readonly string[],
  policy: ProcessPolicy,
): Promise<ProcessEvidence> {
  if (
    executable.length === 0 ||
    policy.timeoutMs < 1 ||
    policy.maxOutputBytes < 1 ||
    policy.network !== "forbidden" ||
    policy.networkIsolation.process_namespace.length === 0 ||
    policy.networkIsolation.host_namespace.length === 0 ||
    policy.networkIsolation.process_namespace === policy.networkIsolation.host_namespace
  ) {
    fail("PROVIDER_EXECUTION_FAILED", "execution", "invalid bounded-process policy");
  }
  const startedAt = new Date().toISOString();
  const stdout: Buffer[] = [];
  const stderr: Buffer[] = [];
  let outputBytes = 0;
  let timedOut = false;
  let outputLimitExceeded = false;

  return await new Promise<ProcessEvidence>((resolve, reject) => {
    const child = spawn(executable, [...args], {
      cwd: policy.cwd,
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        PATH: process.env.PATH ?? "/usr/bin:/bin",
        LANG: "C",
        LC_ALL: "C",
        TZ: "UTC",
        ...policy.environment,
      },
    });
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, policy.timeoutMs);

    const collect = (target: Buffer[]) => (chunk: Buffer | string): void => {
      const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      outputBytes += bytes.length;
      if (outputBytes > policy.maxOutputBytes) {
        outputLimitExceeded = true;
        child.kill("SIGKILL");
        return;
      }
      target.push(bytes);
    };
    child.stdout.on("data", collect(stdout));
    child.stderr.on("data", collect(stderr));
    child.once("error", (error) => {
      clearTimeout(timer);
      reject(error);
    });
    child.once("close", (code, signal) => {
      clearTimeout(timer);
      resolve({
        argv: [executable, ...args],
        cwd: policy.cwd,
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        exit_code: code,
        signal,
        timed_out: timedOut,
        output_limit_exceeded: outputLimitExceeded,
        network_isolation: policy.networkIsolation,
        stdout: Buffer.concat(stdout),
        stderr: Buffer.concat(stderr),
      });
    });
  }).catch((error: unknown) => {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "execution",
      `provider spawn failed: ${error instanceof Error ? error.message : String(error)}`,
    );
  });
}

export function requireCompletedProcess(evidence: ProcessEvidence): ProcessEvidence {
  if (evidence.timed_out) {
    fail("PROVIDER_TIMEOUT", "execution", "provider exceeded its hard timeout");
  }
  if (evidence.output_limit_exceeded) {
    fail("PROVIDER_OUTPUT_INVALID", "execution", "provider exceeded the combined output ceiling");
  }
  if (evidence.exit_code !== 0) {
    fail(
      "PROVIDER_EXECUTION_FAILED",
      "execution",
      `provider exited nonzero: ${String(evidence.exit_code)}`,
    );
  }
  return evidence;
}
