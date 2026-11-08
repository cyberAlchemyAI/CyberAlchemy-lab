import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import {
  decodeFiniteVocabularyDenominatorV1,
  evaluateFiniteVocabulary,
  mintFiniteVocabularyObservationV1,
} from "../../families/finite-vocabulary/index.js";
import type { FactoryUpstreamResultV1 } from
  "../../factory/contracts/factory-node-provider-v1.js";
import {
  ENUM_COMPOSITION_NODE,
  ENUM_DIRECT_HANDLES,
  evaluateEnumComposition,
  evaluateEnumParity,
  proveEnumParity,
} from "./evaluate-enum-joins.js";
import {
  parseTypeScriptEnumWire,
  runTypeScriptEnumWireProbe,
} from "./typescript-wire-probe.js";

const repositoryRoot = resolve(process.cwd(), "../../..");
const paths = Object.freeze({
  owner: "projects/domainspec-v2/development/remaining-meta-types/admissions/enum/owner-member-wire-catalogue.json",
  denominator: "projects/domainspec-v2/impl/architecture-conformance/families/finite-vocabulary/fixtures/shipment-priority/denominator.json",
  case: "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/case.json",
  expected: "projects/domainspec-v2/impl/architecture-conformance/acceptance/enum-regression/shipment-priority/expected-evidence.json",
});

const bytes = async () => Object.fromEntries(await Promise.all(Object.entries(paths).map(
  async ([role, path]) => [role, await readFile(resolve(repositoryRoot, path), "utf8")],
))) as Readonly<Record<keyof typeof paths, string>>;
const clone = <T>(value: T): T => structuredClone(value);
const digest = (digit: number): string => String(digit).repeat(64);
const reseal = (value: any): void => {
  const { composition_sha256: _prior, ...body } = value;
  value.composition_sha256 = createHash("sha256").update(JSON.stringify(body)).digest("hex");
};

const setup = async () => {
  const raw = await bytes();
  const decoded = decodeFiniteVocabularyDenominatorV1(raw.denominator, raw.owner, paths.owner);
  const owner = JSON.parse(raw.owner) as { members: readonly Readonly<{
    member_id: string; member_key: string; wire_value: string;
  }>[] };
  const target = (
    descriptor: typeof ENUM_DIRECT_HANDLES[1] | typeof ENUM_DIRECT_HANDLES[2],
    nativeEvidence: unknown,
  ) => {
    const observation = mintFiniteVocabularyObservationV1({
      schema_version: "FiniteVocabularyObservation/v1",
      observation_id: descriptor.target_id,
      source_kind: "independent-owner-bound-positive",
      target: {
        target_id: descriptor.target_id,
        language: descriptor.language,
        protocol_id: descriptor.protocol_id,
      },
      owner_catalogue_ref: decoded.denominator.owner_catalogue_ref,
      catalogue_origin: "owner-authored-admission-input",
      member_order_semantics: "none",
      members: owner.members.map(({ member_id, member_key, wire_value }) => ({
        member_id,
        native_keys: [member_key],
        emitted_wire: wire_value,
        parsed_member_id: member_id,
      })),
      unknown_wire: {
        wire_value: `__unknown_${descriptor.language}__`,
        outcome: "structured-failure",
        error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE",
        parsed_member_id: null,
      },
      native_identity_diagnostic: {
        relation: "nominal",
        claim_scope: "native-diagnostic-only",
      },
      authority_effect: "none",
    });
    const family_evaluation = evaluateFiniteVocabulary({
      denominator: decoded.denominator,
      owner_catalogue: decoded.owner_catalogue,
      observation,
    });
    return {
      proof: {
        schema_version: descriptor.language === "python"
          ? "PythonEnumComposedProof/v1" : "RustEnumComposedProof/v1",
        result: "pass",
        observation,
        family_evaluation,
        native_proof: nativeEvidence,
      },
      workspace: { isolated: true, cleaned: true, symlinks: false },
    };
  };
  const direct = Object.fromEntries(ENUM_DIRECT_HANDLES.map((descriptor, index) => {
    let semantic_output: unknown;
    if (descriptor.language === "typescript") {
      semantic_output = {
        schema_version: "ShipmentPriorityProof/v1",
        result: "pass",
        case_id: "shipment-priority-v1",
        values: owner.members.map(({ wire_value }) => wire_value),
        positive_verdict: "pass",
        mutation: {
          member_id: "priority.expedited",
          finding_code: "ARCH_ENUM_MEMBER_MISSING",
          status: "killed",
        },
      };
    } else {
      semantic_output = target(descriptor, {
        native_properties: { exact: true },
        hostile_probes: { unknown: true },
        ...(descriptor.language === "rust"
          ? { compiler: { rustc_version: "fixture", probes: { exhaustive: "E0004" } } }
          : {}),
      });
    }
    return [descriptor.node_id, {
      node_id: descriptor.node_id,
      provider_id: descriptor.provider_id,
      semantic_sha256: digest(index + 1),
      semantic_output,
    } satisfies FactoryUpstreamResultV1];
  }));
  const rawInputs = {
    owner_catalogue: raw.owner,
    denominator: raw.denominator,
    typescript_case: raw.case,
    typescript_expected: raw.expected,
  };
  const composition = evaluateEnumComposition({ upstream: direct, raw_inputs: rawInputs });
  const all = {
    ...direct,
    [ENUM_COMPOSITION_NODE.node_id]: {
      node_id: ENUM_COMPOSITION_NODE.node_id,
      provider_id: ENUM_COMPOSITION_NODE.provider_id,
      semantic_sha256: digest(4),
      semantic_output: composition,
    },
  } as Readonly<Record<string, FactoryUpstreamResultV1>>;
  return { raw, rawInputs, direct, composition, all, owner } as const;
};

const rejects = (operation: () => unknown, code: string): void => {
  expect(operation).toThrow(expect.objectContaining({ code }));
};

describe("RMT-ENUM-005 exact composition and portable parity", () => {
  it("executes the TypeScript owner-bound parse and unknown-wire algorithm", async () => {
    const { owner } = await setup();
    const members = owner.members.map(({ member_id, wire_value }) => ({ member_id, wire_value }));
    const probe = runTypeScriptEnumWireProbe(members);
    expect(probe.known.map(({ parsed_member_id }) => parsed_member_id)).toEqual(
      owner.members.map(({ member_id }) => member_id),
    );
    expect(() => parseTypeScriptEnumWire(members, "__domainspec_unknown__"))
      .toThrow(expect.objectContaining({ code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE" }));
    expect(() => runTypeScriptEnumWireProbe(members, "deferred"))
      .toThrow("TS_ENUM_UNKNOWN_PROBE_NOT_OUTSIDE_WIRES");
  });

  it("binds three exact direct handles through composed_from and preserves native evidence", async () => {
    const { composition, all } = await setup();
    expect(composition.relation).toMatchObject({ relation_id: "composed_from", status: "pass" });
    expect(composition.targets.map(({ target_id }) => target_id)).toEqual(
      ENUM_DIRECT_HANDLES.map(({ target_id }) => target_id),
    );
    expect(composition.targets[0]?.native_diagnostic.evidence).toHaveProperty("wire_probe");
    expect(composition.targets[2]?.native_diagnostic.evidence).toHaveProperty("compiler");
    const proof = proveEnumParity(all);
    expect(proof.parity.result).toBe("pass");
    expect(proof.parity.targets.map(({ portable_projection }) =>
      portable_projection.unknown_wire)).toEqual([
      { outcome: "structured-failure", error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE",
        parsed_member_id: null },
      { outcome: "structured-failure", error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE",
        parsed_member_id: null },
      { outcome: "structured-failure", error_code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE",
        parsed_member_id: null },
    ]);
    expect(proof.mutants).toHaveLength(9);
    expect(proof.mutants.every(({ status }) => status === "killed")).toBe(true);
  });

  it("rejects dependency/provider/target/owner/denominator and relation bypass", async () => {
    const { direct, rawInputs, all } = await setup();
    const missing = clone(direct) as any;
    delete missing[ENUM_DIRECT_HANDLES[1].node_id];
    rejects(() => evaluateEnumComposition({ upstream: missing, raw_inputs: rawInputs }),
      "ENUM_JOIN_DEPENDENCY_ORDER_MISMATCH");
    const extra = { ...direct, extra: clone(direct[ENUM_DIRECT_HANDLES[0].node_id]!) };
    rejects(() => evaluateEnumComposition({ upstream: extra, raw_inputs: rawInputs }),
      "ENUM_JOIN_DEPENDENCY_ORDER_MISMATCH");
    const reordered = Object.fromEntries(Object.entries(direct).reverse());
    rejects(() => evaluateEnumComposition({ upstream: reordered, raw_inputs: rawInputs }),
      "ENUM_JOIN_DEPENDENCY_ORDER_MISMATCH");
    const wrongProvider = clone(direct) as any;
    wrongProvider[ENUM_DIRECT_HANDLES[1].node_id].provider_id = "python-wrong-v1";
    rejects(() => evaluateEnumComposition({ upstream: wrongProvider, raw_inputs: rawInputs }),
      "ENUM_JOIN_HANDLE_IDENTITY_MISMATCH");
    for (const [mutation, code] of [
      [(value: any) => { value[ENUM_COMPOSITION_NODE.node_id].semantic_output = {}; },
        "ENUM_PARITY_RELATION_BYPASS"],
      [(value: any) => { value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
        .target_id = "python.wrong"; }, "ENUM_PARITY_TARGET_BINDING_MISMATCH"],
      [(value: any) => { value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
        .observation.owner_catalogue_ref.sha256 = "0".repeat(64); }, "ENUM_PARITY_OWNER_MISMATCH"],
      [(value: any) => { value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
        .family_evaluation.denominator_ref.denominator_sha256 = "0".repeat(64); },
        "ENUM_PARITY_DENOMINATOR_MISMATCH"],
    ] as const) {
      const changed = clone(all);
      mutation(changed);
      if (code !== "ENUM_PARITY_RELATION_BYPASS") {
        reseal((changed as any)[ENUM_COMPOSITION_NODE.node_id].semantic_output);
      }
      rejects(() => evaluateEnumParity(changed), code);
    }
  });

  it("kills member/wire/parse/unknown and duplicate semantic-handle mutants", async () => {
    const { all } = await setup();
    const cases = [
      ["ENUM_PARITY_DUPLICATE_SEMANTIC_HANDLE", (value: any) => {
        value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1].semantic_sha256 =
          value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[0].semantic_sha256;
        value[ENUM_DIRECT_HANDLES[1].node_id].semantic_sha256 =
          value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[0].semantic_sha256;
      }],
      ["ENUM_PARITY_MEMBER_MISMATCH", (value: any) => {
        value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
          .observation.members[0].member_id = "priority.wrong";
      }],
      ["ENUM_PARITY_WIRE_MISMATCH", (value: any) => {
        value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
          .observation.members[0].emitted_wire = "wrong";
      }],
      ["ENUM_PARITY_PARSE_MISMATCH", (value: any) => {
        value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
          .observation.members[0].parsed_member_id = "priority.wrong";
      }],
      ["ENUM_PARITY_UNKNOWN_WIRE_MISMATCH", (value: any) => {
        value[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
          .observation.unknown_wire.outcome = "member";
      }],
    ] as const;
    for (const [code, mutation] of cases) {
      const changed = clone(all);
      mutation(changed);
      reseal((changed as any)[ENUM_COMPOSITION_NODE.node_id].semantic_output);
      rejects(() => evaluateEnumParity(changed), code);
    }
  });

  it("ignores only target-local evidence values while enforcing diagnostic scope and kind", async () => {
    const { all } = await setup();
    const targetLocal = clone(all) as any;
    targetLocal[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
      .native_diagnostic.evidence = { python_version: "different-but-nonportable" };
    reseal(targetLocal[ENUM_COMPOSITION_NODE.node_id].semantic_output);
    expect(evaluateEnumParity(targetLocal).result).toBe("pass");
    const stale = clone(all) as any;
    stale[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
      .native_diagnostic.evidence = { changed: true };
    rejects(() => evaluateEnumParity(stale), "ENUM_PARITY_COMPOSITION_DIGEST_MISMATCH");
    const wrongScope = clone(all) as any;
    wrongScope[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[1]
      .native_diagnostic.claim_scope = "portable";
    reseal(wrongScope[ENUM_COMPOSITION_NODE.node_id].semantic_output);
    rejects(() => evaluateEnumParity(wrongScope), "ENUM_PARITY_NATIVE_DIAGNOSTIC_SCOPE_INVALID");
    const wrongKind = clone(all) as any;
    wrongKind[ENUM_COMPOSITION_NODE.node_id].semantic_output.targets[0]
      .native_diagnostic.relation = "nominal";
    reseal(wrongKind[ENUM_COMPOSITION_NODE.node_id].semantic_output);
    rejects(() => evaluateEnumParity(wrongKind), "ENUM_PARITY_NATIVE_DIAGNOSTIC_TARGET_INVALID");
  });
});
