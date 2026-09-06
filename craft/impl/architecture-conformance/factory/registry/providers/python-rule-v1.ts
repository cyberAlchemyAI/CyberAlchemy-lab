import { execFile } from "node:child_process";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { promisify } from "node:util";

import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";
import { resolveFactoryExecutablePath } from "../../resolution/resolve-toolchain.js";
import { fail } from "../../shared/canonical.js";

const executeFile = promisify(execFile);
const rawPaths = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/targets/python/fixtures/python-binding.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/python/fixtures/can_settle_payout.py",
});
const runnerPath = "projects/domainspec-v2/impl/architecture-conformance/targets/python/rule_proof.py";

export const pythonRuleV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "python-rule-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(rawPaths)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-rule-v1.ts",
    runnerPath,
  ]),
  tool_ids: Object.freeze(["node", "tsx", "python"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const workspace = await mkdtemp(resolve(tmpdir(), "domainspec-factory-python-"));
    try {
      for (const [role, path] of Object.entries(rawPaths)) {
        const bytes = rawInputs[role] ?? fail("FACTORY_PROVIDER_INPUTS_INCOMPLETE", role);
        const target = resolve(workspace, path);
        await mkdir(dirname(target), { recursive: true });
        await writeFile(target, bytes, { encoding: "utf8", flag: "wx" });
      }
      const output = resolve(workspace, "proof.json");
      const python = await resolveFactoryExecutablePath("python");
      const repositoryRoot = resolve(dirname(new URL(import.meta.url).pathname), "../../../../../../..");
      const runner = resolve(repositoryRoot, runnerPath);
      await executeFile(python, [runner, "--repository-root", workspace, "--output", output], {
        env: { PATH: process.env.PATH ?? "", PYTHONDONTWRITEBYTECODE: "1" },
        timeout: 60_000,
        maxBuffer: 1_048_576,
      }).catch((error: unknown) => fail(
        "FACTORY_PYTHON_PROVIDER_FAILED",
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
        provider_id: "python-rule-v1",
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
