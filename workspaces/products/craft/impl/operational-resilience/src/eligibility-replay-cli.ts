import { readFileSync } from "node:fs";
import { evaluateLegacyV1EvidenceEligibility } from "./evaluate-evidence-eligibility.js";

const args = process.argv.slice(2);
const mode = args[0];
const requestPath = args[1];
const inventoryIndex = args.indexOf("--inventory");
const inventoryPath = inventoryIndex >= 0 ? args[inventoryIndex + 1] : undefined;

if (mode !== "evaluate" || requestPath === undefined || inventoryPath === undefined || args.length !== 4) {
  process.stderr.write("usage: eligibility-replay-cli.ts evaluate <request.json> --inventory <inventory.json>\n");
  process.exitCode = 2;
} else {
  try {
    const request = JSON.parse(readFileSync(requestPath, "utf8")) as unknown;
    const inventory = JSON.parse(readFileSync(inventoryPath, "utf8")) as unknown;
    const result = evaluateLegacyV1EvidenceEligibility(request, inventory);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    process.exitCode = result.decision === "replay-only" ? 0 : 1;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    process.stderr.write(`${JSON.stringify({
      schema_version: "domainspec.orodi.eligibility-replay-cli-error/v1",
      code: "ORODI_ELIGIBILITY_INPUT_READ_OR_PARSE_FAILED",
      detail,
      authority_effect: "none",
    })}\n`);
    process.exitCode = 2;
  }
}
