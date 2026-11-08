import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import type {
  GenericReplayChildRequestV2,
  GenericReplayChildResultV2,
} from "../contracts/generic-replay-v2.js";

const sha256 = (value: string | Uint8Array): string =>
  createHash("sha256").update(value).digest("hex");

const execute = async (): Promise<GenericReplayChildResultV2> => {
  const requestPath = process.argv[2];
  if (!requestPath) throw new Error("FACTORY_REPLAY_REQUEST_MISSING");
  const request = JSON.parse(
    await readFile(requestPath, "utf8"),
  ) as GenericReplayChildRequestV2;
  const recomposed: string[] = [];
  for (const entry of [...request.raw_inputs].sort((left, right) =>
    Buffer.from(left.path).compare(Buffer.from(right.path)))) {
    const value = await readFile(resolve(request.raw_root, entry.path));
    if (value.byteLength !== entry.byte_length || sha256(value) !== entry.sha256) {
      throw new Error("FACTORY_REPLAY_RAW_INPUT_TAMPERED");
    }
    recomposed.push(`${entry.path}\u0000${entry.sha256}`);
  }
  const outputSha256 = sha256(recomposed.join("\n"));
  const diagnostics = outputSha256 === request.expected_output_sha256
    ? []
    : ["FACTORY_REPLAY_OUTPUT_MISMATCH"];
  const body = {
    schema_version: "GenericReplayChildResult/v2" as const,
    status: diagnostics.length === 0 ? "pass" as const : "fail" as const,
    child_pid: process.pid,
    semantic_recomposition:
      diagnostics.length === 0 ? "pass" as const : "fail" as const,
    output_sha256: outputSha256,
    observed_raw_count: request.raw_inputs.length,
    diagnostics: Object.freeze(diagnostics),
    authority_effect: "none" as const,
  };
  return Object.freeze({
    ...body,
    result_sha256: sha256(JSON.stringify(body)),
  });
};

execute()
  .then((result) => process.stdout.write(JSON.stringify(result)))
  .catch((error: unknown) => {
    process.stderr.write(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
