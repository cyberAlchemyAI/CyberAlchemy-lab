import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const execute = promisify(execFile);
const here = dirname(fileURLToPath(import.meta.url));
const validator = resolve(here, "validate-provider-firewalls.mjs");
const repositoryRoot = resolve(here, "../../../../../..");

describe("provider import firewalls", () => {
  it("keeps current kernel, family, target, evaluator, and BTE expectation lanes clean", async () => {
    const { stdout } = await execute(process.execPath, [validator, repositoryRoot]);
    expect(JSON.parse(stdout)).toEqual(expect.objectContaining({
      result: "pass",
      violations: [],
      authority_effect: "none",
    }));
  });

  it.each([
    ["kernel", 'import "../../families/finite-vocabulary/index.js";', "KERNEL_IMPORTS_FAMILY"],
    ["family", 'import "../../typescript/compiler/enum/index.js";', "FAMILY_IMPORTS_TARGET_IMPLEMENTATION"],
    ["target", 'import obligations from "../../expected-results.js";', "TARGET_IMPORTS_EXPECTED_SEMANTICS"],
  ])("rejects a %s boundary violation", async (lane, source, code) => {
    let failure: { stdout?: string } | undefined;
    try {
      await execute(process.execPath, [validator, "--probe", lane, source]);
    } catch (error) {
      failure = error as { stdout?: string };
    }
    expect(failure).toBeDefined();
    expect(JSON.parse(failure?.stdout ?? "{}").violations).toContainEqual(
      expect.objectContaining({ code }),
    );
  });
});
