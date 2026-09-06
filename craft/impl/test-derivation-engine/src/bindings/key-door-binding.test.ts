import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  ExactBindingResolutionError,
  resolveExactBinding,
  type ExactBindingFailureCode,
} from "./index.js";
import {
  assertExactRef,
  deriveEnforcesObligations,
  loadEvfS1Bundle,
} from "../minted-project/derive.js";
import { EvfS1Error } from "../minted-project/types.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../../..", import.meta.url));

function expectBindingCode(
  action: () => unknown,
  code: ExactBindingFailureCode,
): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(ExactBindingResolutionError);
    expect((error as ExactBindingResolutionError).code).toBe(code);
    return;
  }
  throw new Error(`expected binding failure ${code}`);
}

describe("EVF S1 exact key-door binding", () => {
  it("resolves exactly one fresh binding for the generated obligation", () => {
    const bundle = loadEvfS1Bundle(REPO_ROOT);
    const obligation = deriveEnforcesObligations(REPO_ROOT, bundle)[0]!;
    const selected = resolveExactBinding(
      obligation.obligation_id,
      [bundle.binding],
      obligation.binding_id,
    );

    expect(selected).toBe(bundle.binding);
    expect(() => assertExactRef(
      REPO_ROOT,
      selected.predicate_ref,
      "BINDING_STALE",
    )).not.toThrow();
  });

  it("distinguishes missing, duplicate, and ambiguous bindings", () => {
    const binding = loadEvfS1Bundle(REPO_ROOT).binding;
    const obligationId = binding.obligation_id;
    const competing = {
      obligation_id: obligationId,
      binding_id: "evf.key-door.competing-binding.v1",
    } as const;

    expectBindingCode(
      () => resolveExactBinding(obligationId, []),
      "BINDING_MISSING",
    );
    expectBindingCode(
      () => resolveExactBinding(obligationId, [binding, binding]),
      "BINDING_DUPLICATE",
    );
    expectBindingCode(
      () => resolveExactBinding(obligationId, [binding, competing]),
      "BINDING_AMBIGUOUS",
    );
    expectBindingCode(
      () => resolveExactBinding(obligationId, [binding], competing.binding_id),
      "BINDING_AMBIGUOUS",
    );
  });

  it("rejects a stale exact reference before execution", () => {
    const ref = loadEvfS1Bundle(REPO_ROOT).binding.fixture_ref;

    try {
      assertExactRef(
        REPO_ROOT,
        { ...ref, sha256: "0".repeat(64) },
        "BINDING_STALE",
      );
    } catch (error) {
      expect(error).toBeInstanceOf(EvfS1Error);
      expect((error as EvfS1Error).code).toBe("BINDING_STALE");
      return;
    }
    throw new Error("expected stale binding rejection");
  });
});
