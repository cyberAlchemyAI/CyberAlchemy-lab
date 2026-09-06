import { describe, expect, it } from "vitest";

import {
  decodeLogicBindingRegistry,
  type LogicBindingRegistry,
  type PureBindingSelector,
  resolvePureBinding,
  SFOL_BINDING_SCHEMA_VERSION,
} from "./index.js";

const A = "a".repeat(64);
const B = "b".repeat(64);
const C = "c".repeat(64);
const D = "d".repeat(64);
const E = "e".repeat(64);
const F = "f".repeat(64);

function selector(
  caseId = "case-001",
  fixtureDigest = D,
): PureBindingSelector {
  return {
    module_id: "framework.module",
    clause_id: "framework.clause",
    case_id: caseId,
    role: "invoke",
    module_digest: A,
    clause_digest: B,
    case_digest: C,
    fixture_digest: fixtureDigest,
  };
}

function binding(
  bindingId: string,
  exactSelector: PureBindingSelector = selector(),
  adapterKind: "pure-function" | "effect-harness" = "pure-function",
) {
  return {
    binding_id: bindingId,
    selector: exactSelector,
    target: {
      adapter_kind: adapterKind,
      module: "@framework/domain",
      symbol: "evaluateRule",
      target_digest: E,
      runtime_digest: F,
    },
    argument_map: [
      { parameter: "second", input_name: "input.second" },
      { parameter: "first", input_name: "input.first" },
    ],
    observation_map: { kind: "return" },
  };
}

function registry(bindings: readonly unknown[]) {
  return {
    schema_version: SFOL_BINDING_SCHEMA_VERSION,
    registry_id: "framework.bindings",
    bindings,
  };
}

function decode(input: unknown): LogicBindingRegistry {
  const result = decodeLogicBindingRegistry(input);
  if (!result.ok) {
    throw new Error(JSON.stringify(result.diagnostics));
  }
  return result.value;
}

describe("DS-SFOL exact pure binding registry", () => {
  it("normalizes deterministically and resolves one full identity/digest tuple", () => {
    const exact = selector("case-001");
    const decoded = decode(
      registry([
        binding("binding-b", selector("case-002")),
        binding("binding-a", exact),
      ]),
    );

    expect(decoded.bindings.map((entry) => entry.binding_id)).toEqual([
      "binding-a",
      "binding-b",
    ]);
    expect(decoded.bindings[0]?.argument_map).toEqual([
      { parameter: "first", input_name: "input.first" },
      { parameter: "second", input_name: "input.second" },
    ]);
    expect(Object.isFrozen(decoded)).toBe(true);
    expect(Object.isFrozen(decoded.bindings)).toBe(true);

    const resolved = resolvePureBinding(
      { selector: exact, adapter_kind: "pure-function" },
      decoded,
    );
    expect(resolved).toMatchObject({
      ok: true,
      value: {
        binding: { binding_id: "binding-a" },
      },
    });
    if (resolved.ok) {
      expect(resolved.value.resolution_key).toContain(
        "framework.module|framework.clause|case-001|invoke",
      );
    }
  });

  it("fails empty and unbound registries without fallback", () => {
    const empty = decode(registry([]));
    expect(
      resolvePureBinding(
        { selector: selector(), adapter_kind: "pure-function" },
        empty,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_EMPTY_REGISTRY" }],
    });

    const decoded = decode(registry([binding("only", selector("other"))]));
    expect(
      resolvePureBinding(
        { selector: selector(), adapter_kind: "pure-function" },
        decoded,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_UNBOUND" }],
    });
  });

  it("fails multiple exact matches instead of selecting the first", () => {
    const exact = selector();
    const decoded = decode(
      registry([
        binding("second", exact),
        binding("first", exact),
      ]),
    );

    expect(
      resolvePureBinding(
        { selector: exact, adapter_kind: "pure-function" },
        decoded,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        {
          code: "SFOL_BINDING_MULTIPLE",
          detail: "exact selector resolves multiple bindings: first, second",
        },
      ],
    });
  });

  it("distinguishes a stale digest set from an absent identity", () => {
    const decoded = decode(
      registry([binding("stale-binding", selector("case-001", D))]),
    );

    expect(
      resolvePureBinding(
        {
          selector: selector("case-001", E),
          adapter_kind: "pure-function",
        },
        decoded,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [
        {
          code: "SFOL_BINDING_STALE",
          detail: "identity matches stale binding(s): stale-binding",
        },
      ],
    });
  });

  it("rejects legacy first-match entries and partial selectors", () => {
    const full = binding("legacy");
    const firstMatch = {
      binding_id: "legacy",
      match: { clause_id: "framework.clause" },
      target: full.target,
      argument_map: full.argument_map,
      observation_map: full.observation_map,
    };
    expect(
      decodeLogicBindingRegistry(registry([firstMatch])),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_FIRST_MATCH_FORBIDDEN" }],
    });

    const { role: _role, ...partial } = selector();
    expect(
      decodeLogicBindingRegistry(
        registry([{ ...full, selector: partial }]),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_PARTIAL_SELECTOR" }],
    });
  });

  it("rejects predicate, expected-value, and acceptance oracle fields", () => {
    const full = binding("oracle");
    for (const forbidden of [
      { predicate: "result === true" },
      { expected_value: 42 },
      { acceptance_rule: "must pass" },
    ]) {
      expect(
        decodeLogicBindingRegistry(
          registry([{ ...full, ...forbidden }]),
        ),
      ).toMatchObject({
        ok: false,
        diagnostics: [{ code: "SFOL_BINDING_ORACLE_FIELD" }],
      });
    }
  });

  it("rejects a non-pure adapter at pure resolution", () => {
    const exact = selector();
    const decoded = decode(
      registry([binding("effect-binding", exact, "effect-harness")]),
    );

    expect(
      resolvePureBinding(
        { selector: exact, adapter_kind: "pure-function" },
        decoded,
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_WRONG_ADAPTER_KIND" }],
    });
  });

  it("rejects malformed types, digests, and duplicate stable IDs", () => {
    const full = binding("duplicate");
    expect(
      decodeLogicBindingRegistry({
        ...registry([full]),
        bindings: "not-an-array",
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_INVALID_SHAPE" }],
    });

    expect(
      decodeLogicBindingRegistry(
        registry([
          binding("bad-digest", {
            ...selector(),
            case_digest: "not-a-digest",
          }),
        ]),
      ),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_INVALID_DIGEST" }],
    });

    expect(
      decodeLogicBindingRegistry(registry([full, full])),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_DUPLICATE_ID" }],
    });
  });

  it("rejects unknown versions and unknown schema fields", () => {
    expect(
      decodeLogicBindingRegistry({
        ...registry([]),
        schema_version: "domainspec-sfol-binding/v2",
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_UNKNOWN_VERSION" }],
    });
    expect(
      decodeLogicBindingRegistry({
        ...registry([]),
        fallback: "first",
      }),
    ).toMatchObject({
      ok: false,
      diagnostics: [{ code: "SFOL_BINDING_UNKNOWN_FIELD" }],
    });
  });
});
