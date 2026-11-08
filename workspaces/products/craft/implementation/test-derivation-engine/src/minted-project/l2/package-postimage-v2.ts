import { digestValue } from "./canonical-json.js";
import { fail } from "./types.js";

// Candidate reconciliation of the standalone package, not an L2 one-shot
// receipt or an adoption of the historical five-script baseline.
export const PACKAGE_POSTIMAGE_V2 = {
  schema_version: "evf.l2.package-postimage/v2-candidate",
  decision_ref:
    "projects/domainspec-v2/development/evolvable-validation-framework/decision-runs/20260823T201735Z-dirty-baselines/DECISION.json",
  observed_package_sha256:
    "6ddee96839161edd107290d7c6c4a36450bf5d9904034590c2f09798521c9199",
  remainder_digest:
    "127697377616f855421f1c8be7bed0ee6141537a7d9dc68dc8a17113ad34b9a5",
  scripts: {
    "verify:evf-l2": "tsx test-derivation-engine/src/minted-project/l2/verify-l2-one-shot.ts",
    "test:evf-l2": "vitest run test-derivation-engine/src/minted-project/l2 --maxWorkers=1 --minWorkers=1",
    "verify:evf-l2:c0": "tsx test-derivation-engine/src/minted-project/l2/verify-c0.ts",
    "verify:evf-l2:c1": "tsx test-derivation-engine/src/minted-project/l2/verify-c1.ts",
    "verify:evf-l2:c2": "tsx test-derivation-engine/src/minted-project/l2/verify-c2.ts",
    "verify:bte:financial-settlement:current": "tsx test-derivation-engine/src/bte/current-financial-settlement-terminal.ts",
    "verify:bte:financial-settlement:fixture-v2": "tsx test-derivation-engine/src/bte/financial-settlement-current-fixture.ts",
    "verify:sfol:financial-settlement:current-structural": "tsx tools/current-financial-settlement-sfol-join.ts",
  },
  authority_effect: "none",
} as const;

export function verifyPackagePostimageV2(value: unknown): void {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    fail("TARGET_BASELINE_DRIFT", "closure", "v2 package postimage is not a JSON object", 2);
  }
  const packageValue = structuredClone(value) as Record<string, unknown>;
  if (
    packageValue.scripts === null ||
    typeof packageValue.scripts !== "object" ||
    Array.isArray(packageValue.scripts)
  ) {
    fail("TARGET_BASELINE_DRIFT", "closure", "v2 package scripts are absent", 2);
  }
  const scripts = packageValue.scripts as Record<string, unknown>;
  for (const [key, expected] of Object.entries(PACKAGE_POSTIMAGE_V2.scripts)) {
    if (scripts[key] !== expected) {
      fail("TARGET_BASELINE_DRIFT", "closure", `v2 package script drifted: ${key}`, 2);
    }
    delete scripts[key];
  }
  if (digestValue(packageValue) !== PACKAGE_POSTIMAGE_V2.remainder_digest) {
    fail("TARGET_BASELINE_DRIFT", "closure", "v2 package remainder drifted", 2);
  }
}
