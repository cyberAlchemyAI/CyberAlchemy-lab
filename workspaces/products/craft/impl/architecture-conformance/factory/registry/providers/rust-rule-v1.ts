import { execFile } from "node:child_process";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";
import { resolveFactoryExecutablePath } from "../../resolution/resolve-toolchain.js";
import { fail } from "../../shared/canonical.js";

const executeFile = promisify(execFile);
const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const manifestPath = resolve(repositoryRoot,
  "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml");
const rawPaths = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/fixtures/rust-binding.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/fixtures/can_settle_payout.rs",
});

export const rustRuleV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rust-rule-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(rawPaths)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-rule-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.toml",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/Cargo.lock",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/lib.rs",
    "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/bin/rule_proof.rs",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "cargo", "rustc"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-rust-"));
    try {
      for (const [role, path] of Object.entries(rawPaths)) {
        const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
        const target = resolve(workspace, path);
        await mkdir(dirname(target), { recursive: true });
        await writeFile(target, bytes, { encoding: "utf8", flag: "wx" });
      }
      const output = resolve(workspace, "proof.json");
      const cargo = await resolveFactoryExecutablePath("cargo");
      await executeFile(cargo, [
        "run",
        "--manifest-path", manifestPath,
        "--locked",
        "--offline",
        "--quiet",
        "--bin", "rule-proof",
        "--",
        "--repository-root", workspace,
        "--output", output,
      ], {
        env: {
          PATH: process.env.PATH ?? "",
          CARGO_HOME: process.env.CARGO_HOME ?? resolve(process.env.HOME ?? workspace, ".cargo"),
          CARGO_TARGET_DIR: resolve(workspace, "target"),
        },
        timeout: 120_000,
        maxBuffer: 1_048_576,
      }).catch((error: unknown) => fail(
        "FACTORY_RUST_PROVIDER_FAILED",
        error instanceof Error ? error.message : String(error),
      ));
      const proof = JSON.parse(await readFile(output, "utf8")) as {
        summary: {
          accounting: {
            positive: { declared: number; passed: number };
            mutations: { declared: number; killed: number };
          };
          claim_ceiling: string;
        };
        runtime: { observations: unknown };
      };
      return Object.freeze({
        schema_version: "FactoryNodeSemanticResult/v1",
        result: "pass",
        provider_id: "rust-rule-v1",
        semantic_output: Object.freeze({
          summary: proof.summary,
          observations: proof.runtime.observations,
        }),
        accounting: Object.freeze({
          positives_declared: proof.summary.accounting.positive.declared,
          positives_passed: proof.summary.accounting.positive.passed,
          mutants_declared: proof.summary.accounting.mutations.declared,
          mutants_killed: proof.summary.accounting.mutations.killed,
        }),
        claim_ceiling: proof.summary.claim_ceiling,
        authority_effect: "none",
      });
    } finally {
      await rm(workspace, { recursive: true, force: true });
    }
  },
});
