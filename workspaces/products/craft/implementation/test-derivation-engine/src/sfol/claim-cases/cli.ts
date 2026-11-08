#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

import { deriveSelectedSfolClaimCases, replaySelectedSfolClaimCases,
  type SelectedSfolCaseSet, type SelectedSfolClaimSources } from "./index.js";

function option(args: readonly string[], name: string): string | undefined {
  const index = args.indexOf(name);
  return index < 0 ? undefined : args[index + 1];
}

export function runSelectedSfolClaimCasesCli(args: readonly string[]): number {
  const root = option(args, "--root");
  const selectionPath = option(args, "--selection");
  const replayPath = option(args, "--replay");
  if (!root || !selectionPath || args.some(arg => arg.startsWith("--") &&
      !["--root", "--selection", "--replay", "--summary"].includes(arg))) {
    process.stderr.write("usage: sfol:claim-cases --root <selected-source-root> --selection <selection.json> [--replay <case-set.json>] [--summary]\n");
    return 2;
  }
  try {
    const selection = JSON.parse(readFileSync(resolve(selectionPath), "utf8")) as SelectedSfolClaimSources;
    const result = replayPath
      ? replaySelectedSfolClaimCases(resolve(root), selection,
          JSON.parse(readFileSync(resolve(replayPath), "utf8")) as SelectedSfolCaseSet)
      : deriveSelectedSfolClaimCases(resolve(root), selection);
    const output = args.includes("--summary")
      ? { claim_id: result.claim_id, case_count: result.cases.length,
          cases: result.oracles.map(item => ({ case_id: item.case_id,
            inputs: result.cases.find(row => row.case_id === item.case_id)?.inputs,
            expected_value: item.expected_value })),
          proof_context_verification: result.proof_context_verification,
          f5_eligibility: result.f5_eligibility, claim_ceiling: result.claim_ceiling }
      : result;
    process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
    return 0;
  } catch (error: unknown) {
    process.stderr.write(`${error instanceof Error ? error.message : "SFOL claim case derivation failed"}\n`);
    return 1;
  }
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url)
  process.exitCode = runSelectedSfolClaimCasesCli(process.argv.slice(2));
