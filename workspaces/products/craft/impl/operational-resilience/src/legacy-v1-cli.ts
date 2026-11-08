import { readFileSync } from "node:fs";
import type { LegacyV1SourceInventory } from "../contracts/legacy-v1-adapter.js";
import { normalizeLegacyV1 } from "./normalize-legacy-v1.js";

const args = process.argv.slice(2);
const mode = args[0];
const inputPath = args[1];
const inventoryIndex = args.indexOf("--inventory");
const atIndex = args.indexOf("--at");
const inventoryPath = inventoryIndex >= 0 ? args[inventoryIndex + 1] : undefined;
const replayedAt = atIndex >= 0 ? args[atIndex + 1] : undefined;

if (mode !== "normalize" || inputPath === undefined || inventoryPath === undefined || replayedAt === undefined) {
  process.stderr.write("usage: legacy-v1-cli.ts normalize <input.json> --inventory <inventory.json> --at <RFC3339>\n");
  process.exitCode = 2;
} else {
  try {
    const input = JSON.parse(readFileSync(inputPath, "utf8")) as unknown;
    const inventory = JSON.parse(readFileSync(inventoryPath, "utf8")) as LegacyV1SourceInventory;
    const result = normalizeLegacyV1(input, inventory, replayedAt);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exitCode = result.verdict === "normalized" ? 0 : 1;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    process.stderr.write(`${JSON.stringify({
      schema_version: "domainspec.orodi.legacy-v1-cli-error/v1",
      code: "ORODI_V1_INPUT_READ_OR_PARSE_FAILED",
      detail,
      authority_effect: "none",
    })}\n`);
    process.exitCode = 2;
  }
}
