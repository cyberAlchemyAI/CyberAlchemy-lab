import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { resolveExactBinding } from "../bindings/index.js";
import { emitEvfS1StrictTests } from "../emit/tests.js";
import { deriveEnforcesObligations, loadEvfS1Bundle } from "./derive.js";
import { executeEnforcesCases } from "./enforces-execution.js";
import { decodeBooleanEquality } from "./typed-predicate.js";
import { EvfS1Error } from "./types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

describe("EVF S1 key-door vertical", () => {
  it("joins source, lineage, obligation, binding, predicate, runtime, and strict generation", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const obligations = deriveEnforcesObligations(REPO_ROOT, bundle);
    const binding = resolveExactBinding(
      obligations[0]!.obligation_id,
      [bundle.binding],
      obligations[0]!.binding_id,
    );
    const ast = decodeBooleanEquality(bundle.predicate.predicate.ast);
    const observations = executeEnforcesCases(ast, bundle.fixtures.cases);
    const generated = emitEvfS1StrictTests({
      obligationIds: obligations.map((item) => item.obligation_id),
      binding,
      ast,
      cases: bundle.fixtures.cases,
      runtimeModule: "./fixtures/key-door-runtime.js",
      predicateModule: "./typed-predicate.js",
      executionModule: "./enforces-execution.js",
    });

    expect(observations.map((item) => item.expected_boolean)).toEqual([true, false]);
    expect(observations.map((item) => item.observed_boolean)).toEqual([true, false]);
    expect(generated.mode).toBe("evf-s1-strict");
    expect(generated.testId).toBe("evf.s1.generated-test.has-key-unlock-door.v1");
    expect(generated.file.match(/\n  it\(/g)).toHaveLength(1);
    expect(generated.file.match(/= attemptUnlock\(/g)).toHaveLength(2);
    expect(generated.file.match(/expect\(observed,/g)).toHaveLength(1);
    expect(generated.file).not.toMatch(/it\.skip|it\.todo|needs_formal|orphan|unrunnable/);
  });

  it("fails closed when strict generation receives more than one obligation", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const obligations = deriveEnforcesObligations(REPO_ROOT, bundle);
    const id = obligations[0]!.obligation_id;

    try {
      emitEvfS1StrictTests({
        obligationIds: [id, id],
        binding: bundle.binding,
        ast: bundle.predicate.predicate.ast,
        cases: bundle.fixtures.cases,
        runtimeModule: "./fixtures/key-door-runtime.js",
        predicateModule: "./typed-predicate.js",
        executionModule: "./enforces-execution.js",
      });
    } catch (error) {
      expect(error).toBeInstanceOf(EvfS1Error);
      expect((error as EvfS1Error).code).toBe("STRICT_ASSERTION_COUNT_MISMATCH");
      return;
    }
    throw new Error("expected strict assertion-count rejection");
  });
});
