import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

import type {
  GenericReplayChildRequestV2,
  GenericReplayChildResultV2,
} from "../../../kernel/contracts/generic-replay-v2.js";
import {
  buildTypeScriptRuleProof,
  type TypeScriptRuleRawInputs,
} from "./run-rule-proof.js";

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

const execute = async (): Promise<GenericReplayChildResultV2> => {
  const requestPath = process.argv[2];
  if (!requestPath) throw new Error("TS_RULE_REPLAY_REQUEST_MISSING");
  const request = JSON.parse(
    await readFile(requestPath, "utf8"),
  ) as GenericReplayChildRequestV2;
  const raw: Partial<Record<keyof TypeScriptRuleRawInputs, string>> = {};
  for (const entry of request.raw_inputs) {
    const bytes = await readFile(resolve(request.raw_root, entry.path));
    if (bytes.byteLength !== entry.byte_length || sha256(bytes) !== entry.sha256) {
      throw new Error("FACTORY_REPLAY_RAW_INPUT_TAMPERED");
    }
    const name = basename(entry.path).replace(/\.raw$/u, "") as keyof TypeScriptRuleRawInputs;
    raw[name] = bytes.toString("utf8");
  }
  const required = ["definition", "binding", "cases", "obligations", "mutants", "source"] as const;
  if (required.some((name) => raw[name] === undefined)) {
    throw new Error("TS_RULE_REPLAY_RAW_INPUT_INCOMPLETE");
  }
  const proof = await buildTypeScriptRuleProof(raw as TypeScriptRuleRawInputs);
  const diagnostics = proof.summary_sha256 === request.expected_output_sha256
    ? [] : ["TS_RULE_REPLAY_OUTPUT_MISMATCH"];
  const body = {
    schema_version: "GenericReplayChildResult/v2" as const,
    status: diagnostics.length === 0 ? "pass" as const : "fail" as const,
    child_pid: process.pid,
    semantic_recomposition: diagnostics.length === 0 ? "pass" as const : "fail" as const,
    output_sha256: proof.summary_sha256,
    observed_raw_count: request.raw_inputs.length,
    diagnostics: Object.freeze(diagnostics),
    authority_effect: "none" as const,
  };
  return Object.freeze({
    ...body,
    result_sha256: sha256(JSON.stringify(body)),
  });
};

execute().then((result) => process.stdout.write(JSON.stringify(result)))
  .catch((error: unknown) => {
    process.stderr.write(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
