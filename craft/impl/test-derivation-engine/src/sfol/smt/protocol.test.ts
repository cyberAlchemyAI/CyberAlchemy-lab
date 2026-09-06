import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { canonicalJson } from "../language/contracts.js";
import {
  FORMAL_OBLIGATION_REQUEST_VERSION,
  mapSmtProviderReceipt,
  type BoundWitness,
  type ExactArtifactRef,
  type FormalObligationRequest,
  type NativeResult,
  type ProtocolMappingInput,
  witnessBindingsDigest,
} from "./protocol.js";

interface FrozenCase {
  readonly id: string;
  readonly overrides: Readonly<Record<string, unknown>>;
  readonly expected:
    | {
        readonly valid: true;
        readonly normalized: string;
        readonly claim: string;
      }
    | {
        readonly valid: false;
        readonly diagnostic: string;
      };
}

interface FixtureBundle {
  readonly schema_version: "evf.smt-protocol-fixtures/v1";
  readonly authority_effect: "none";
  readonly solver_execution: false;
  readonly evidence_origin: "synthetic-validator-input";
  readonly claim_ceiling: "protocol-validation-only-no-solver-or-domain-claim";
  readonly denominator: {
    readonly case_count: number;
    readonly positive_count: number;
    readonly negative_count: number;
  };
  readonly defaults: Readonly<Record<string, unknown>>;
  readonly cases: readonly FrozenCase[];
}

const FIXTURE_BUNDLE_URL = new URL(
  "../../../../../development/evolvable-validation-framework/fixtures/SWU-EVF-SMTP-001/protocol-validation-cases.v1.json",
  import.meta.url,
);
const fixtures = JSON.parse(
  readFileSync(FIXTURE_BUNDLE_URL, "utf8"),
) as FixtureBundle;

const A_SHA = "a".repeat(64);
const B_SHA = "b".repeat(64);
const C_SHA = "c".repeat(64);

function exactRef(path: string, current = true): ExactArtifactRef {
  return { path, sha256: A_SHA, size_bytes: 1, current };
}

function request(
  queryKind: "counterexample" | "witness",
  requestState: "ready" | "blocked" | "stale",
  refsCurrent: boolean,
): FormalObligationRequest {
  return {
    schema_version: FORMAL_OBLIGATION_REQUEST_VERSION,
    request_id: "request.fixture-001",
    request_state: requestState,
    query_kind: queryKind,
    semantic_source_ref: exactRef("semantic/source.json", refsCurrent),
    formal_obligation_ref: exactRef("formal/obligation.json", refsCurrent),
    theory_profile_ref: exactRef("theory/profile.json", refsCurrent),
    symbol_table_ref: exactRef("translation/symbols.json", refsCurrent),
    assumptions_ref: exactRef("translation/assumptions.json", refsCurrent),
    translation_contract_ref: exactRef(
      "translation/contract.json",
      refsCurrent,
    ),
    runtime_manifest_ref: exactRef("runtime/manifest.json", refsCurrent),
    execution_policy: {
      timeout_ms: 1000,
      memory_ceiling_bytes: 1048576,
      max_output_bytes: 1048576,
      network: "forbidden",
      working_directory: ".",
      environment_allowlist: ["PATH"],
    },
    authority_effect: "none",
    release_admission: "not-granted",
    claim_ceiling: "request-only-no-evaluation-claim",
    residue: [],
  };
}

function materialize(testCase: FrozenCase): ProtocolMappingInput {
  const values = merge(fixtures.defaults, testCase.overrides);
  const executionValue = values.execution as Readonly<Record<string, unknown>>;
  const queryKind = values.query_kind as "counterexample" | "witness";
  const requestState = values.request_state as "ready" | "blocked" | "stale";
  const refsCurrent = values.refs_current as boolean;
  const execution = {
    run_id: "run.fixture-001",
    status: executionValue.status as string,
    timed_out: executionValue.timed_out as boolean,
    failure_kind: executionValue.failure_kind as string | null,
    exit_code: executionValue.exit_code as number | null,
  };
  const nativeResult: NativeResult | null =
    values.native_outcome === null
      ? null
      : {
          outcome: values.native_outcome as "sat" | "unsat" | "unknown",
          result_ref: exactRef("execution/native-result.json"),
          result_digest: B_SHA,
        };
  const witnessValue = values.witness as
    | Readonly<Record<string, unknown>>
    | null;
  let witness: BoundWitness | null = null;
  if (witnessValue !== null) {
    const witnessWithoutDigest = {
      model_ref: exactRef("execution/model.json"),
      request_ref: "request.fixture-001",
      translated_query_digest: C_SHA,
      runtime_manifest_ref: "runtime/manifest.json",
      execution_run_id: "run.fixture-001",
      native_result_digest: B_SHA,
    };
    const validWitness = {
      ...witnessWithoutDigest,
      bindings_digest: witnessBindingsDigest(witnessWithoutDigest),
    };
    witness =
      witnessValue.bindings_match === false
        ? { ...validWitness, request_ref: "request.fixture-mismatch" }
        : validWitness;
  }

  return {
    receipt_id: `receipt.${testCase.id}`,
    request: request(queryKind, requestState, refsCurrent),
    translation: {
      receipt_ref: exactRef("translation/receipt.json"),
      validation_status: values.translation_status as
        | "valid"
        | "blocked"
        | "stale",
      translated_query_digest: C_SHA,
      omitted_term_count: values.omitted_term_count as number,
      invented_term_count: values.invented_term_count as number,
    },
    execution,
    native_result: nativeResult,
    witness,
    evidence_origin: values.evidence_origin as string,
    consumer: values.consumer as string,
    inline_predicate_present: values.inline_predicate as boolean,
    claimed_normalized: values.claimed_normalized as string,
    claimed_ceiling: values.claimed_ceiling as string,
    claimed_broad: values.claimed_broad as boolean,
    evidence_refs: [exactRef("execution/log.json")],
    residue: [],
  };
}

function merge(
  defaults: Readonly<Record<string, unknown>>,
  overrides: Readonly<Record<string, unknown>>,
): Record<string, unknown> {
  const result = { ...defaults, ...overrides };
  if ("execution" in overrides) {
    result.execution = {
      ...(defaults.execution as Readonly<Record<string, unknown>>),
      ...(overrides.execution as Readonly<Record<string, unknown>>),
    };
  }
  return result;
}

describe("EVF SMT solver-independent protocol kernel", () => {
  it("keeps the exact frozen 42-case denominator synthetic and authority-free", () => {
    expect(fixtures.schema_version).toBe("evf.smt-protocol-fixtures/v1");
    expect(fixtures.denominator).toEqual({
      case_count: 42,
      positive_count: 14,
      negative_count: 28,
    });
    expect(new Set(fixtures.cases.map((item) => item.id)).size).toBe(42);
    expect(fixtures.solver_execution).toBe(false);
    expect(fixtures.authority_effect).toBe("none");
    expect(fixtures.evidence_origin).toBe("synthetic-validator-input");
    expect(fixtures.claim_ceiling).toBe(
      "protocol-validation-only-no-solver-or-domain-claim",
    );
  });

  it("accepts every positive class and rejects every mutant with its stable code", () => {
    for (const testCase of fixtures.cases) {
      const result = mapSmtProviderReceipt(materialize(testCase));
      if (testCase.expected.valid) {
        expect(result, testCase.id).toMatchObject({
          ok: true,
          value: {
            normalized_result: { outcome: testCase.expected.normalized },
            claim_ceiling: testCase.expected.claim,
            authority_effect: "none",
            release_admission: "not-granted",
          },
        });
      } else {
        expect(result, testCase.id).toMatchObject({
          ok: false,
          diagnostics: [{ code: testCase.expected.diagnostic }],
        });
      }
    }
  });

  it("produces byte-identical canonical receipts across deterministic runs", () => {
    for (const testCase of fixtures.cases.filter(
      (item) => item.expected.valid,
    )) {
      const first = mapSmtProviderReceipt(materialize(testCase));
      const second = mapSmtProviderReceipt(materialize(testCase));
      expect(first.ok, testCase.id).toBe(true);
      expect(second.ok, testCase.id).toBe(true);
      if (first.ok && second.ok) {
        expect(canonicalJson(first.value), testCase.id).toBe(
          canonicalJson(second.value),
        );
      }
    }
  });
});
