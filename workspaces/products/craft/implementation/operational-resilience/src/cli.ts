#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  deriveOperationalControls,
  validateOperationalEvidence,
} from "./validate-operational-evidence.js";

const usage = (): never => {
  process.stderr.write("usage: cli.ts <validate|derive> <bundle.json> --at <RFC3339>\n");
  process.exit(2);
};

const args = process.argv.slice(2);
if (args.length !== 4 || !["validate", "derive"].includes(args[0]!) || args[2] !== "--at") usage();

const inputPath = resolve(args[1]!);
const evaluatedAt = args[3]!;

try {
  const input = JSON.parse(readFileSync(inputPath, "utf8")) as unknown;
  const result = args[0] === "derive"
    ? deriveOperationalControls(input, evaluatedAt)
    : validateOperationalEvidence(input, evaluatedAt);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = result.verdict === "pass" ? 0 : 1;
} catch (error) {
  const detail = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${JSON.stringify({
    schema_version: "domainspec.orodi.cli-error/v1",
    code: "ORODI_INPUT_READ_OR_PARSE_FAILED",
    detail,
    authority_effect: "none",
  })}\n`);
  process.exitCode = 2;
}
