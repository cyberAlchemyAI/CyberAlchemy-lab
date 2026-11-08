import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { runCli } from "../../src/cli/main.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const capacityOperationSource = path.resolve(testDir, "../fixtures/capacity-decision");
const featureRoot = "specs/capacity-decision";

interface Diagnostic {
  readonly code: string;
  readonly pointer: string;
  readonly message: string;
  readonly exitCode: number;
}

interface MutationCase {
  readonly mutation_id: string;
  readonly category: "malformed" | "incomplete" | "cyclic" | "ambiguous" | "unsupported" | "semantic-type-invalid";
  readonly expected_code: string;
  readonly mutate: (root: string) => void;
  readonly evaluate: (root: string) => unknown;
}

function copiedCapacitySource(): { readonly parent: string; readonly root: string } {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-typed-l2-"));
  const root = path.join(parent, "source");
  fs.cpSync(capacityOperationSource, root, { recursive: true });
  return { parent, root };
}

function mutateNode(root: string, nodeId: string, mutate: (value: Record<string, any>) => void): void {
  const nodePath = path.join(root, featureRoot, "nodes", `${nodeId}.json`);
  const value = JSON.parse(fs.readFileSync(nodePath, "utf8"));
  mutate(value);
  fs.writeFileSync(nodePath, `${JSON.stringify(value, null, 2)}\n`);
}

function load(root: string): unknown {
  return loadProjectNode(root, "capacity-decision:decide-capacity");
}

function plan(root: string): unknown {
  return planInstantiation(loadProjectNode(root, "capacity-decision:decide-capacity"), "rust");
}

function diagnostic(action: () => unknown): Diagnostic {
  let caught: unknown;
  try {
    action();
  } catch (error) {
    caught = error;
  }
  assert.ok(caught instanceof Error, "mutation must fail closed");
  const candidate = caught as Error & { readonly code?: unknown; readonly pointer?: unknown; readonly exitCode?: unknown };
  assert.equal(typeof candidate.code, "string");
  assert.equal(typeof candidate.pointer, "string");
  assert.equal(candidate.exitCode, 22);
  return {
    code: candidate.code as string,
    pointer: candidate.pointer as string,
    message: candidate.message,
    exitCode: candidate.exitCode as number,
  };
}

const mutations: readonly MutationCase[] = Object.freeze([
  {
    mutation_id: "L2-MALFORMED-RULE-SCHEMA",
    category: "malformed",
    expected_code: "MTCLI_TYPED_SCHEMA",
    mutate: (root) => mutateNode(root, "within-capacity", (node) => {
      delete node.body.typed_contract.expression.right;
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-INCOMPLETE-MISSING-OUTPUT",
    category: "incomplete",
    expected_code: "MTCLI_TYPED_CLOSURE_MISSING",
    mutate: (root) => mutateNode(root, "decide-capacity", (node) => {
      node.body.typed_contract.output.selector = "capacity-decision:missing-decision";
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-INCOMPLETE-UNTYPED-DEPENDENCY",
    category: "incomplete",
    expected_code: "MTCLI_TYPED_CLOSURE_UNTYPED",
    mutate: (root) => mutateNode(root, "within-capacity", (node) => {
      delete node.body.typed_contract;
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-CYCLIC-SELF-RULE",
    category: "cyclic",
    expected_code: "MTCLI_TYPED_CLOSURE_CYCLE",
    mutate: (root) => mutateNode(root, "within-capacity", (node) => {
      node.body.typed_contract.expression = {
        op: "rule_ref",
        selector: "capacity-decision:within-capacity",
        arguments: [{ parameter: "snapshot", value: { op: "path", root: "snapshot", properties: [] } }],
      };
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-AMBIGUOUS-PROPERTY-IDENTITY",
    category: "ambiguous",
    expected_code: "MTCLI_TYPED_DUPLICATE",
    mutate: (root) => mutateNode(root, "capacity-snapshot", (node) => {
      node.body.typed_contract.properties.push(structuredClone(node.body.typed_contract.properties[0]));
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-UNSUPPORTED-RULE-OPERATOR",
    category: "unsupported",
    expected_code: "MTCLI_TYPED_RULE",
    mutate: (root) => mutateNode(root, "within-capacity", (node) => {
      node.body.typed_contract.expression = { op: "xor", terms: [] };
    }),
    evaluate: load,
  },
  {
    mutation_id: "L2-SEMANTIC-RULE-TYPE-MISMATCH",
    category: "semantic-type-invalid",
    expected_code: "MTCLI_TYPED_RULE_TYPE",
    mutate: (root) => mutateNode(root, "within-capacity", (node) => {
      node.body.typed_contract.expression.right.properties = ["CAPACITY-SNAPSHOT#request_id"];
    }),
    evaluate: plan,
  },
]);

test("L2 mutation matrix rejects every category with deterministic typed diagnostics", () => {
  assert.deepEqual(mutations.map(({ mutation_id, category, expected_code }) => ({ mutation_id, category, expected_code })), [
    { mutation_id: "L2-MALFORMED-RULE-SCHEMA", category: "malformed", expected_code: "MTCLI_TYPED_SCHEMA" },
    { mutation_id: "L2-INCOMPLETE-MISSING-OUTPUT", category: "incomplete", expected_code: "MTCLI_TYPED_CLOSURE_MISSING" },
    { mutation_id: "L2-INCOMPLETE-UNTYPED-DEPENDENCY", category: "incomplete", expected_code: "MTCLI_TYPED_CLOSURE_UNTYPED" },
    { mutation_id: "L2-CYCLIC-SELF-RULE", category: "cyclic", expected_code: "MTCLI_TYPED_CLOSURE_CYCLE" },
    { mutation_id: "L2-AMBIGUOUS-PROPERTY-IDENTITY", category: "ambiguous", expected_code: "MTCLI_TYPED_DUPLICATE" },
    { mutation_id: "L2-UNSUPPORTED-RULE-OPERATOR", category: "unsupported", expected_code: "MTCLI_TYPED_RULE" },
    { mutation_id: "L2-SEMANTIC-RULE-TYPE-MISMATCH", category: "semantic-type-invalid", expected_code: "MTCLI_TYPED_RULE_TYPE" },
  ]);

  for (const mutation of mutations) {
    const runs: Diagnostic[] = [];
    for (let run = 0; run < 2; run += 1) {
      const fixture = copiedCapacitySource();
      try {
        mutation.mutate(fixture.root);
        runs.push(diagnostic(() => mutation.evaluate(fixture.root)));
      } finally {
        fs.rmSync(fixture.parent, { recursive: true, force: true });
      }
    }
    assert.equal(runs[0]?.code, mutation.expected_code, mutation.mutation_id);
    assert.deepEqual(runs[0], runs[1], mutation.mutation_id);
  }
});

test("typed Rule diagnostics retain their code and pointer through the CLI envelope", () => {
  const fixture = copiedCapacitySource();
  const target = path.join(fixture.parent, "target");
  try {
    mutations.at(-1)!.mutate(fixture.root);
    const errors: string[] = [];
    const exitCode = runCli([
      "instantiate", fixture.root,
      "--node", "capacity-decision:decide-capacity",
      "--language", "rust",
      "--target-root", target,
    ], { stdout: () => undefined, stderr: (value) => errors.push(value) });
    assert.equal(exitCode, 22);
    assert.equal(fs.existsSync(target), false);
    assert.equal(errors.length, 1);
    assert.deepEqual(JSON.parse(errors[0]!), {
      result: "fail",
      code: "MTCLI_TYPED_RULE_TYPE",
      pointer: "/nodes/capacity-decision:within-capacity/typed_contract/expression",
      message: "lt operands are type-incompatible",
      authority_effect: "none",
    });
  } finally {
    fs.rmSync(fixture.parent, { recursive: true, force: true });
  }
});
