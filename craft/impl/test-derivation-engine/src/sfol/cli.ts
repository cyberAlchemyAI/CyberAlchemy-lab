#!/usr/bin/env node
import { readFileSync, renameSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

import {
  challengeTestClosure,
  closeTestClosure,
  derivePartitions,
  replayPure,
  verifyContentAddressedReceipt,
  type DerivePartitionsRequest,
  type ReplayPureRequest,
} from "./api/index.js";
import type { NegativeControlEvaluationInput } from "./negative-controls/index.js";

export const SFOL_TDE_CLI_VERSION = "domainspec-sfol-tde-cli/v1" as const;

export function runSfolCli(argv: readonly string[]): number {
  const command = argv[0];
  const inputPath = option(argv, "--in");
  const outputPath = option(argv, "--out");
  if (!command || !inputPath || !["derive", "challenge", "close", "verify", "replay"].includes(command)) {
    process.stderr.write("usage: sfol-tde <derive|challenge|close|verify|replay> --in <request.json> [--out <result.json> | --check]\n");
    return 2;
  }
  try {
    const raw: unknown = JSON.parse(readFileSync(resolve(inputPath), "utf8"));
    validateRequest(command, raw);
    const result = command === "derive"
      ? derivePartitions(raw as unknown as DerivePartitionsRequest)
      : command === "challenge"
        ? challengeTestClosure(raw as unknown as NegativeControlEvaluationInput)
        : command === "close"
          ? closeTestClosure(raw as unknown as Parameters<typeof closeTestClosure>[0])
        : command === "replay"
          ? replayPure(raw as unknown as ReplayPureRequest)
          : verifyContentAddressedReceipt(raw);
    const bytes = `${JSON.stringify(result, null, 2)}\n`;
    if (outputPath && argv.includes("--check")) throw new Error("SFOL_CLI_REQUEST_INVALID: --out and --check are mutually exclusive");
    if (outputPath) atomicWrite(resolve(outputPath), bytes);
    else process.stdout.write(bytes);
    return result.ok ? 0 : 1;
  } catch (error: unknown) {
    process.stderr.write(`${error instanceof Error ? error.message : "SFOL CLI failure"}\n`);
    return 2;
  }
}

function validateRequest(command: string, raw: unknown): asserts raw is Record<string, unknown> {
  if (typeof raw !== "object" || raw === null || Array.isArray(raw)) {
    throw new Error("SFOL_CLI_REQUEST_INVALID: request must be an object");
  }
  const record = raw as Record<string, unknown>;
  if (command === "derive") {
    requireObject(record, "module");
    requireObject(record, "denominator");
    requireObject(record, "ruleset");
    requireVersion(record, "domainspec-sfol-tde-api/v1");
  } else if (command === "challenge") {
    requireVersion(record, "domainspec-sfol-negative-control/v1", "profile_version");
    for (const name of ["fault_models", "controls", "observations"]) {
      if (!Array.isArray(record[name])) throw new Error(`SFOL_CLI_REQUEST_INVALID: ${name} must be an array`);
    }
  } else if (command === "replay") {
    requireVersion(record, "domainspec-sfol-tde-api/v1");
    requireObject(record, "receipt");
    requireObject(record, "input");
    requireObject(record, "allowlist");
  } else if (command === "close") {
    if (!["domainspec-sfol-tde-api/v1", "domainspec-sfol-tde-api/v2"].includes(String(record.api_version))) {
      throw new Error("SFOL_CLI_REQUEST_INVALID: api_version must equal domainspec-sfol-tde-api/v1 or domainspec-sfol-tde-api/v2");
    }
    requireObject(record, "proof_receipt");
    if (record.api_version === "domainspec-sfol-tde-api/v1" || record.detection_matrix !== undefined) requireObject(record, "detection_matrix");
  }
}

function requireVersion(record: Record<string, unknown>, expected: string, field = "api_version"): void {
  if (record[field] !== expected) throw new Error(`SFOL_CLI_REQUEST_INVALID: ${field} must equal ${expected}`);
}

function requireObject(record: Record<string, unknown>, field: string): void {
  const value = record[field];
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`SFOL_CLI_REQUEST_INVALID: ${field} must be an object`);
  }
}

function option(argv: readonly string[], name: string): string | undefined {
  const index = argv.indexOf(name);
  return index < 0 ? undefined : argv[index + 1];
}

function atomicWrite(path: string, bytes: string): void {
  const temporary = resolve(dirname(path), `.${path.split("/").at(-1)}.tmp-${process.pid}`);
  writeFileSync(temporary, bytes, { encoding: "utf8", flag: "wx" });
  renameSync(temporary, path);
}

if (process.argv[1] && import.meta.url === new URL(`file://${resolve(process.argv[1])}`).href) {
  process.exitCode = runSfolCli(process.argv.slice(2));
}
