import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it } from "vitest";

import {
  loadExecutionControl,
  runSerializedUnits,
  scanDeclaredTargets,
  validateNetworkIsolationEvidence,
  validateRouteScopes,
  verifyPackagePostimage,
} from "./one-shot.js";

const EVIDENCE =
  "projects/domainspec-v2/development/evolvable-validation-framework/evidence/SWU-X/attempt-001/Violation.csv";
const AUTHORED = "projects/domainspec-v2/impl/test-derivation-engine/src/minted-project/l2/example.ts";
const SCHEMA = "projects/domainspec-v2/development/evolvable-validation-framework/contracts/example.schema.json";
const UPDATE = "projects/domainspec-v2/impl/package.json";

const roots: string[] = [];

function fixture(): {
  readonly root: string;
  readonly stage: string;
  readonly inventoryPath: string;
  readonly executionPath: string;
  readonly inventory: Record<string, unknown>;
  readonly execution: Record<string, unknown>;
} {
  const root = mkdtempSync(join(tmpdir(), "evf-l2-scan-test-"));
  roots.push(root);
  const stage = join(root, "stage");
  mkdirSync(stage);
  const inventory = {
    create_target_classification: {
      authored_create_targets: 2,
      runtime_generated_create_targets: 1,
      authored_update_targets: 1,
    },
    partitions: {
      "SWU-X": {
        create_targets: [AUTHORED, SCHEMA, EVIDENCE],
        update_targets: [{ path: UPDATE }],
      },
    },
  };
  const execution = {
    execution_policy: {
      allowed_routes: [{
        frontier_swu: "SWU-X",
        write_scope: [AUTHORED, SCHEMA, EVIDENCE, UPDATE],
      }],
    },
  };
  const inventoryPath = join(root, "inventory.json");
  const executionPath = join(root, "execution.json");
  writeFileSync(inventoryPath, `${JSON.stringify(inventory, null, 2)}\n`);
  writeFileSync(executionPath, `${JSON.stringify(execution, null, 2)}\n`);
  put(stage, AUTHORED, "export const value = 1;\n");
  put(stage, SCHEMA, `${JSON.stringify({
    $schema: "https://json-schema.org/draft/2020-12/schema",
    type: "object",
    additionalProperties: false,
  }, null, 2)}\n`);
  put(stage, UPDATE, '{"name":"fixture"}\n');
  return { root, stage, inventoryPath, executionPath, inventory, execution };
}

function put(root: string, path: string, bytes: string | Buffer): void {
  const absolute = join(root, path);
  mkdirSync(dirname(absolute), { recursive: true });
  writeFileSync(absolute, bytes);
}

function scan(input: ReturnType<typeof fixture>, phase: "authored-prewrite" | "terminal-live") {
  return scanDeclaredTargets({
    repositoryRoot: input.root,
    contentRoot: input.stage,
    inventoryPath: input.inventoryPath,
    executionEntryPath: input.executionPath,
    phase,
    rejectExtraStagedFiles: true,
  });
}

afterEach(() => {
  while (roots.length > 0) rmSync(roots.pop()!, { recursive: true, force: true });
});

describe("EVF L2 inventory-driven scanner", () => {
  it("loads the documented cwd-relative execution control paths", () => {
    const input = fixture();
    const loaded = loadExecutionControl(
      input.root,
      relative(process.cwd(), input.inventoryPath),
      relative(process.cwd(), input.executionPath),
    );
    expect(loaded.inventory).toEqual(input.inventory);
    expect(loaded.executionEntry).toEqual(input.execution);
  });

  it("admits only the exact five-script package semantic delta", () => {
    const packagePath = fileURLToPath(new URL("../../../../package.json", import.meta.url));
    const postimage = JSON.parse(readFileSync(packagePath, "utf8")) as Record<string, unknown>;
    expect(() => verifyPackagePostimage(postimage)).not.toThrow();

    const expectBaselineDrift = (candidate: Record<string, unknown>): void => {
      expect(() => verifyPackagePostimage(candidate))
        .toThrowError(expect.objectContaining({ code: "TARGET_BASELINE_DRIFT" }));
    };
    const scriptsOf = (candidate: Record<string, unknown>): Record<string, unknown> =>
      candidate.scripts as Record<string, unknown>;

    const packageFieldDrift = structuredClone(postimage);
    packageFieldDrift.description = `${String(packageFieldDrift.description)}\\u2014`;
    expectBaselineDrift(packageFieldDrift);

    const l2CommandDrift = structuredClone(postimage);
    scriptsOf(l2CommandDrift)["verify:evf-l2"] = "tsx drifted-l2-command.ts";
    expectBaselineDrift(l2CommandDrift);

    const nonL2CommandDrift = structuredClone(postimage);
    scriptsOf(nonL2CommandDrift)["validate:docs"] = "tsx tools/drifted-doc-validator.ts";
    expectBaselineDrift(nonL2CommandDrift);

    const nonL2ScriptRemoval = structuredClone(postimage);
    delete scriptsOf(nonL2ScriptRemoval)["validate:docs"];
    expectBaselineDrift(nonL2ScriptRemoval);

    const extraScript = structuredClone(postimage);
    scriptsOf(extraScript)["verify:evf-l2:extra"] = "tsx undeclared-l2-command.ts";
    expect(() => verifyPackagePostimage(extraScript))
      .toThrowError(expect.objectContaining({ code: "TARGET_BASELINE_DRIFT" }));
  });

  it("accepts exactly the authored creates and update while runtime evidence is absent", () => {
    const input = fixture();
    const result = scan(input, "authored-prewrite");
    expect(result.scanned_paths).toHaveLength(3);
    expect(result.runtime_generated_count).toBe(1);
    expect(result.route_count).toBe(1);
  });

  it("accepts a zero-byte native empty relation at terminal closure", () => {
    const input = fixture();
    put(input.stage, EVIDENCE, Buffer.alloc(0));
    expect(scan(input, "terminal-live").scanned_paths).toHaveLength(4);
  });

  it("rejects nonempty native text without its final newline", () => {
    const input = fixture();
    put(input.stage, EVIDENCE, "financial-settlement.NoDuplicateMakeupRule");
    expect(() => scan(input, "terminal-live"))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });

  it("rejects predicted provider evidence in the authored-prewrite phase", () => {
    const input = fixture();
    put(input.stage, EVIDENCE, Buffer.alloc(0));
    expect(() => scan(input, "authored-prewrite"))
      .toThrowError(expect.objectContaining({ code: "TARGET_BASELINE_DRIFT" }));
  });

  it("rejects an untracked create with trailing whitespace", () => {
    const input = fixture();
    put(input.stage, "projects/domainspec-v2/impl/untracked.ts", "bad  \n");
    expect(() => scan(input, "authored-prewrite"))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });

  it("rejects UTF-8 BOM in an untracked or declared create", () => {
    const input = fixture();
    put(input.stage, AUTHORED, Buffer.from([0xef, 0xbb, 0xbf, 0x78, 0x0a]));
    expect(() => scan(input, "authored-prewrite"))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });

  it("meta-validates JSON Schemas rather than accepting parse-only JSON", () => {
    const input = fixture();
    put(input.stage, SCHEMA, '{"$schema":"https://json-schema.org/draft/2020-12/schema","type":7}\n');
    expect(() => scan(input, "authored-prewrite"))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });

  it("rejects a widened directory-prefix route", () => {
    const input = fixture();
    const widened = structuredClone(input.execution) as {
      execution_policy: { allowed_routes: { frontier_swu: string; write_scope: string[] }[] };
    };
    widened.execution_policy.allowed_routes[0]!.write_scope[0] = dirname(AUTHORED);
    expect(() => validateRouteScopes(input.inventory as never, widened as never))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });

  it("rejects one extra route path outside the inventory", () => {
    const input = fixture();
    const widened = structuredClone(input.execution) as {
      execution_policy: { allowed_routes: { frontier_swu: string; write_scope: string[] }[] };
    };
    widened.execution_policy.allowed_routes[0]!.write_scope.push("projects/domainspec-v2/impl/extra.ts");
    expect(() => validateRouteScopes(input.inventory as never, widened as never))
      .toThrowError(expect.objectContaining({ code: "UNDECLARED_WRITE" }));
  });
});

describe("EVF L2 serialized first-failure controller", () => {
  it("accepts only a distinct, well-formed inherited network namespace", () => {
    expect(validateNetworkIsolationEvidence("net:[200]", "net:[100]")).toEqual({
      kind: "inherited-linux-network-namespace",
      process_namespace: "net:[200]",
      host_namespace: "net:[100]",
    });
    expect(() => validateNetworkIsolationEvidence("net:[100]", "net:[100]"))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_EXECUTION_FAILED" }));
    expect(() => validateNetworkIsolationEvidence("forged", "net:[100]"))
      .toThrowError(expect.objectContaining({ code: "PROVIDER_EXECUTION_FAILED" }));
  });

  it("never starts a successor and preserves the first error when cleanup also fails", async () => {
    const calls: string[] = [];
    const first = Object.assign(new Error("provider failed"), { code: "PROVIDER_EXECUTION_FAILED" });
    await expect(runSerializedUnits([
      {
        id: "C0",
        run: () => {
          calls.push("C0");
          try {
            throw first;
          } finally {
            try {
              throw new Error("cleanup failed");
            } catch {
              // Cleanup is contained and cannot replace the first failure.
            }
          }
        },
      },
      { id: "C1", run: () => { calls.push("C1"); } },
    ])).rejects.toMatchObject({
      message: "provider failed",
      code: "PROVIDER_EXECUTION_FAILED",
      unit_states: [
        { id: "C0", status: "failed" },
        { id: "C1", status: "not-run" },
      ],
    });
    expect(calls).toEqual(["C0"]);
  });
});
