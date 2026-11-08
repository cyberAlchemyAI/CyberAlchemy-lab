import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  deriveFinancialSettlementStructuralEmission,
  writeFinancialSettlementStructuralArtifacts,
} from "./structural-emitter.js";

const here = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(here, "../../..");
const allowedOutputRoot = resolve(implRoot, "generated-tests");
const defaultFeatureRoot = resolve(
  implRoot,
  "../../../validation/poker-team/docs/features/financial-settlement",
);
const bindingsPath = resolve(
  implRoot,
  "test-derivation-engine/bindings/financial-settlement.json",
);

function option(name: string): string | undefined {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function main(): void {
  const command = process.argv[2];
  if (command !== "generate") {
    console.error(
      "usage: financial-settlement-cli.ts generate [--feature-root PATH] [--output-dir PATH]",
    );
    process.exit(2);
  }
  const featureRoot = resolve(option("--feature-root") ?? defaultFeatureRoot);
  const outputDir = resolve(
    option("--output-dir") ??
      resolve(allowedOutputRoot, "financial-settlement"),
  );
  const emission = deriveFinancialSettlementStructuralEmission(
    featureRoot,
    bindingsPath,
  );
  const written = writeFinancialSettlementStructuralArtifacts(
    emission,
    allowedOutputRoot,
    outputDir,
  );
  console.log(
    JSON.stringify({
      result: emission.report.result,
      structural: emission.report.structural,
      behavioral: emission.report.behavioral,
      outputs: written,
    }),
  );
}

main();
