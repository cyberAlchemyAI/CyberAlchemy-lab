#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";

import type { SelectedSfolClaimSources } from "./index.js";
import { observeSelectedSfolNative, replaySelectedSfolNative,
  type SelectedSfolNativeExecution, type SelectedSfolNativeLink } from "./native-link.js";

function option(args: readonly string[], name: string): string | undefined {
  const index = args.indexOf(name);
  return index < 0 ? undefined : args[index + 1];
}

async function main(args: readonly string[]): Promise<number> {
  const root = option(args, "--root"), selectionPath = option(args, "--selection");
  const binaryPath = option(args, "--executable"), replayPath = option(args, "--replay");
  if (!root || !selectionPath || !binaryPath || args.some(arg => arg.startsWith("--") &&
      !["--root", "--selection", "--executable", "--replay", "--summary"].includes(arg))) {
    process.stderr.write("usage: sfol:native-link --root <auth-root> --selection <selection.json> --executable <built-binary> [--replay <link.json>] [--summary]\n");
    return 2;
  }
  try {
    const selection = JSON.parse(readFileSync(resolve(selectionPath), "utf8")) as SelectedSfolClaimSources;
    const executable = resolve(binaryPath);
    const bytes = readFileSync(executable);
    const execution: SelectedSfolNativeExecution = {
      executable: { path: executable, sha256: createHash("sha256").update(bytes).digest("hex"),
        size_bytes: statSync(executable).size },
      timeout_ms: 5000, max_output_bytes: 4096,
    };
    const link = replayPath
      ? await replaySelectedSfolNative(resolve(root), selection, execution,
          JSON.parse(readFileSync(resolve(replayPath), "utf8")) as SelectedSfolNativeLink)
      : await observeSelectedSfolNative(resolve(root), selection, execution);
    const output = args.includes("--summary")
      ? { status: link.status, case_count: link.observations.length,
          matched: link.observations.filter(row => row.comparison === "match").length,
          incomplete: link.observations.filter(row => row.comparison === "incomplete").length,
          mismatched: link.observations.filter(row => row.comparison === "mismatch").length,
          case_set_digest: link.case_set_digest, executable_sha256: link.execution.executable.sha256,
          f5_eligibility: link.f5_eligibility, can_satisfy_obligation: link.can_satisfy_obligation,
          claim_ceiling: link.claim_ceiling }
      : link;
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
    return link.status === "matched" ? 0 : 1;
  } catch (error: unknown) {
    process.stderr.write(`${error instanceof Error ? error.message : "SFOL native link failed"}\n`);
    return 1;
  }
}

main(process.argv.slice(2)).then(code => { process.exitCode = code; });
