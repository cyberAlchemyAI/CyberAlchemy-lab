import { describe, expect, it } from "vitest";

import type { FactoryNodeSemanticResultV1 } from
  "../contracts/factory-node-provider-v1.js";
import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import type { FactorySemanticNodeReceiptV1 } from
  "../contracts/factory-semantic-receipt-v1.js";
import { normalizeFactorySemanticReceipt } from
  "../evidence/normalize-semantic-receipt.js";
import { bindReplayVerifiedSemanticResult } from
  "../pipeline/execute-factory-run.js";
import {
  decodeLockedChildOutput,
  lockedComponentSetSha256,
} from "../replay/run-locked-child.js";
import { canonicalJson, sha256 } from "../shared/canonical.js";
import type {
  ProofDenominatorV1,
  ProofEvidenceV1,
} from "../../kernel/contracts/proof-denominator-v1.js";
import { recomputeProofAccounting } from
  "../../kernel/evidence/recompute-proof-accounting.js";

const PROVIDER_ID = "fixture-provider-v1";
const DENOMINATOR_PATH = "proof/fixture-denominator.json";
const DIGEST = (value: string): string => sha256(`observation:${value}`);

const denominator = (ownerRef = "family-rule-proof-owner"): ProofDenominatorV1 =>
  Object.freeze({
    schema_version: "ProofDenominator/v1" as const,
    denominator_id: "rule-proof-v1",
    owner_ref: ownerRef,
    obligation_ids: Object.freeze(["RULE-O1", "RULE-O2"]),
    mutants: Object.freeze([
      Object.freeze({ mutant_id: "RULE-M1", expected_finding_code: "RULE-F1" }),
      Object.freeze({ mutant_id: "RULE-M2", expected_finding_code: "RULE-F2" }),
    ]),
    authority_effect: "none" as const,
  });

const evidenceFor = (
  definition = denominator(),
): Readonly<{ evidence: ProofEvidenceV1; bytes: string; digest: string }> => {
  const bytes = canonicalJson(definition);
  const digest = sha256(bytes);
  return Object.freeze({
    bytes,
    digest,
    evidence: Object.freeze({
      schema_version: "ProofEvidence/v1" as const,
      denominator_ref: Object.freeze({
        role: "proof-denominator" as const,
        path: DENOMINATOR_PATH,
        sha256: digest,
      }),
      denominator_bytes: bytes,
      producer_ref: PROVIDER_ID,
      obligations: Object.freeze(definition.obligation_ids.map((obligationId) => Object.freeze({
        obligation_id: obligationId,
        status: "passed" as const,
        observation_sha256: DIGEST(obligationId),
      }))),
      mutants: Object.freeze(definition.mutants.map((mutant) => Object.freeze({
        mutant_id: mutant.mutant_id,
        status: "killed" as const,
        finding_code: mutant.expected_finding_code,
        observation_sha256: DIGEST(mutant.mutant_id),
      }))),
      authority_effect: "none" as const,
    }),
  });
};

const clone = <T>(value: T): T => structuredClone(value);

const recompute = (proof: unknown, digest: string) => recomputeProofAccounting({
  locked_denominator_ref: Object.freeze({
    role: "proof-denominator" as const,
    path: DENOMINATOR_PATH,
    sha256: digest,
  }),
  provider_id: PROVIDER_ID,
  evidence: proof,
});

const plan = (inputDigest: string | null): FactoryRunPlanV1 => {
  const inputRefs = inputDigest === null ? [] : [{
    role: "proof-denominator",
    ref: { path: DENOMINATOR_PATH, sha256: inputDigest },
  }];
  const inputs = inputDigest === null ? [] : [Object.freeze({
    role: "proof-denominator",
    path: DENOMINATOR_PATH,
    sha256: inputDigest,
    byte_length: 1,
  })];
  return Object.freeze({
    schema_version: "FactoryRunPlan/v1" as const,
    request: Object.freeze({
      schema_version: "FactoryRunRequest/v1" as const,
      request_id: "proof-request",
      suite_id: "proof-suite",
      purpose: "new-kit-proof" as const,
      nodes: Object.freeze([Object.freeze({
        node_id: "proof-node",
        kind: "direct-proof" as const,
        provider_id: PROVIDER_ID,
        depends_on: Object.freeze([]),
        input_refs: Object.freeze(inputRefs),
        claim_ceiling: "candidate proof accounting only",
      })]),
      claim_ceiling: "candidate proof accounting only",
      authority_effect: "none" as const,
    }),
    lock: Object.freeze({
      schema_version: "FactoryRunLock/v1" as const,
      request_id: "proof-request",
      suite_id: "proof-suite",
      purpose: "new-kit-proof" as const,
      request_sha256: "1".repeat(64),
      ordered_node_ids: Object.freeze(["proof-node"]),
      nodes: Object.freeze([Object.freeze({
        node_id: "proof-node",
        kind: "direct-proof" as const,
        provider_id: PROVIDER_ID,
        provider_version: "1.0.0",
        depends_on: Object.freeze([]),
        inputs: Object.freeze(inputs),
        components: Object.freeze([]),
        tools: Object.freeze([]),
        claim_ceiling: "candidate proof accounting only",
      })]),
      replay_policy: Object.freeze({
        timeout_ms: 1_000,
        output_limit_bytes: 1_048_576,
        termination_grace_ms: 100,
        environment_keys: Object.freeze([]),
      }),
      claim_ceiling: "candidate proof accounting only",
      authority_effect: "none" as const,
      lock_sha256: "2".repeat(64),
    }),
    run_id: "proof-run",
    authority_effect: "none" as const,
  });
};

const node = (
  proof: ProofEvidenceV1 | undefined,
  counts: Readonly<{
    positives_declared: number;
    positives_passed: number;
    mutants_declared: number;
    mutants_killed: number;
  }> = Object.freeze({
    positives_declared: 2,
    positives_passed: 2,
    mutants_declared: 2,
    mutants_killed: 2,
  }),
): FactorySemanticNodeReceiptV1 => Object.freeze({
  node_id: "proof-node",
  provider_id: PROVIDER_ID,
  depends_on: Object.freeze([]),
  semantic_sha256: "3".repeat(64),
  replay_sha256: "3".repeat(64),
  accounting: proof === undefined
    ? Object.freeze({ ...counts })
    : Object.freeze({ ...counts, proof }),
  claim_ceiling: "candidate proof accounting only",
});

describe("RMT-FND-003 independent proof accounting", () => {
  it("recomputes the exact owner-authored denominator and finding set", () => {
    const fixture = evidenceFor();
    const result = recompute(fixture.evidence, fixture.digest);
    expect(result).toMatchObject({
      result: "pass",
      totals: {
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 2,
        mutants_killed: 2,
      },
      diagnostics: [],
      proof: {
        denominator_id: "rule-proof-v1",
        owner_ref: "family-rule-proof-owner",
        producer_ref: PROVIDER_ID,
        obligations: [
          { obligation_id: "RULE-O1", status: "passed" },
          { obligation_id: "RULE-O2", status: "passed" },
        ],
        mutants: [
          { mutant_id: "RULE-M1", status: "killed", finding_code: "RULE-F1" },
          { mutant_id: "RULE-M2", status: "killed", finding_code: "RULE-F2" },
        ],
      },
    });
    expect(result.proof).not.toHaveProperty("denominator_bytes");
  });

  it.each([
    ["self-authored denominator", () => evidenceFor(denominator(PROVIDER_ID)),
      "FACTORY_PROOF_OWNER_SELF_AUTHORED"],
    ["filtered obligation", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.obligations = evidence.obligations.slice(0, 1);
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_OBLIGATION_UNACCOUNTED"],
    ["filtered mutant", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.mutants = evidence.mutants.slice(0, 1);
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_MUTANT_UNACCOUNTED"],
    ["duplicate obligation", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.obligations.push(evidence.obligations[0]);
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_OBLIGATION_DUPLICATE"],
    ["unexpected mutant", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.mutants.push({
        mutant_id: "RULE-MX",
        status: "killed",
        finding_code: "RULE-FX",
        observation_sha256: DIGEST("RULE-MX"),
      });
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_MUTANT_UNEXPECTED"],
    ["failed obligation", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.obligations[0]!.status = "failed";
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_OBLIGATION_FAILED"],
    ["survived mutant", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.mutants[0]!.status = "survived";
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_MUTANT_SURVIVED"],
    ["wrong finding", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.mutants[0]!.finding_code = "RULE-WRONG";
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_FINDING_MISMATCH"],
    ["invalid observation", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.mutants[0]!.observation_sha256 = "not-a-digest";
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_EVIDENCE_INVALID"],
    ["wrong producer", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.producer_ref = "another-provider-v1";
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_PRODUCER_MISMATCH"],
    ["rewritten denominator bytes", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.denominator_bytes = `${evidence.denominator_bytes} `;
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_DENOMINATOR_DIGEST_MISMATCH"],
    ["rewritten denominator reference", () => {
      const fixture = evidenceFor();
      const evidence = clone(fixture.evidence) as any;
      evidence.denominator_ref.sha256 = "9".repeat(64);
      return { ...fixture, evidence };
    }, "FACTORY_PROOF_DENOMINATOR_REF_MISMATCH"],
  ] as const)("blocks %s", (_label, build, expectedDiagnostic) => {
    const fixture = build();
    const result = recompute(fixture.evidence, fixture.digest);
    expect(result.result).toBe("block");
    expect(result.diagnostics).toContain(expectedDiagnostic);
    expect(result.proof).toBeNull();
  });

  it("requires locked proof evidence and rejects provider-authored totals or claim ceilings", () => {
    const fixture = evidenceFor();
    expect(() => normalizeFactorySemanticReceipt({
      plan: plan(fixture.digest),
      nodes: [node(undefined)],
    })).toThrow("FACTORY_PROOF_EVIDENCE_REQUIRED");
    expect(() => normalizeFactorySemanticReceipt({
      plan: plan(fixture.digest),
      nodes: [node(fixture.evidence, Object.freeze({
        positives_declared: 1,
        positives_passed: 1,
        mutants_declared: 1,
        mutants_killed: 1,
      }))],
    })).toThrow("FACTORY_PROOF_TOTALS_MISMATCH");
    expect(() => normalizeFactorySemanticReceipt({
      plan: plan(null),
      nodes: [node(fixture.evidence)],
    })).toThrow("FACTORY_PROOF_EVIDENCE_UNLOCKED");
    expect(() => normalizeFactorySemanticReceipt({
      plan: plan(fixture.digest),
      nodes: [Object.freeze({
        ...node(fixture.evidence),
        claim_ceiling: "provider-expanded claim",
      })],
    })).toThrow("FACTORY_CLAIM_CEILING_MISMATCH:proof-node");
  });

  it("writes only recomputed ID evidence to the terminal receipt and preserves legacy nodes", () => {
    const fixture = evidenceFor();
    const normalized = normalizeFactorySemanticReceipt({
      plan: plan(fixture.digest),
      nodes: [node(fixture.evidence)],
    });
    expect(normalized.receipt.ordered_nodes[0]!.accounting.proof).toMatchObject({
      denominator_id: "rule-proof-v1",
      obligations: [{ obligation_id: "RULE-O1" }, { obligation_id: "RULE-O2" }],
      mutants: [
        { mutant_id: "RULE-M1", finding_code: "RULE-F1" },
        { mutant_id: "RULE-M2", finding_code: "RULE-F2" },
      ],
    });
    expect(canonicalJson(normalized.receipt)).not.toContain("denominator_bytes");

    const legacy = normalizeFactorySemanticReceipt({ plan: plan(null), nodes: [node(undefined)] });
    expect(legacy.receipt.ordered_nodes[0]!.accounting).toEqual({
      positives_declared: 2,
      positives_passed: 2,
      mutants_declared: 2,
      mutants_killed: 2,
    });
  });

  it("preserves valid proof evidence through the closed replay decoder", () => {
    const fixture = evidenceFor();
    const semanticResult: FactoryNodeSemanticResultV1 = Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: PROVIDER_ID,
      semantic_output: Object.freeze({ fixture: true }),
      accounting: Object.freeze({
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 2,
        mutants_killed: 2,
        proof: fixture.evidence,
      }),
      claim_ceiling: "candidate proof accounting only",
      authority_effect: "none" as const,
    });
    const componentDigest = lockedComponentSetSha256([]);
    const envelope = (result: unknown) => ({
      schema_version: "FactoryReplayChildResult/v1",
      result: "pass",
      replay_mode: "same-oracle-deterministic",
      node_id: "proof-node",
      provider_id: PROVIDER_ID,
      provider_version: "1.0.0",
      component_identity: {
        algorithm: "sha256",
        locked_set_sha256: componentDigest,
        pre_load_sha256: componentDigest,
        post_execute_sha256: componentDigest,
      },
      semantic_result: result,
      semantic_result_sha256: sha256(canonicalJson(result)),
      authority_effect: "none",
    });
    const decode = (result: unknown) => decodeLockedChildOutput({
      rendered: `${JSON.stringify(envelope(result))}\n`,
      nodeId: "proof-node",
      providerId: PROVIDER_ID,
      providerVersion: "1.0.0",
      lockedComponentSetSha256: componentDigest,
    });
    expect(decode(semanticResult).accounting.proof).toEqual(fixture.evidence);
    const malformed = clone(semanticResult) as unknown as {
      accounting: { proof: Record<string, unknown> };
    };
    malformed.accounting.proof.extra = true;
    expect(() => decode(malformed)).toThrow("FACTORY_REPLAY_OUTPUT_INVALID");
  });

  it("binds downstream evidence to an isolated replay snapshot", () => {
    const fixture = evidenceFor();
    const providerOwned = clone({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: PROVIDER_ID,
      semantic_output: { state: "original" },
      accounting: {
        positives_declared: 2,
        positives_passed: 2,
        mutants_declared: 2,
        mutants_killed: 2,
        proof: fixture.evidence,
      },
      claim_ceiling: "candidate proof accounting only",
      authority_effect: "none" as const,
    });
    const replayResult = clone(providerOwned);
    const directSha256 = sha256(canonicalJson(providerOwned));
    const replaySha256 = sha256(canonicalJson(replayResult));
    const stable = bindReplayVerifiedSemanticResult({
      node_id: "proof-node",
      locked_claim_ceiling: "candidate proof accounting only",
      direct_sha256: directSha256,
      replay_result: replayResult,
      replay_result_sha256: replaySha256,
    });
    const providerExpanded = clone(providerOwned);
    providerExpanded.claim_ceiling = "provider-expanded claim";
    const expandedSha256 = sha256(canonicalJson(providerExpanded));
    expect(() => bindReplayVerifiedSemanticResult({
      node_id: "proof-node",
      locked_claim_ceiling: "candidate proof accounting only",
      direct_sha256: expandedSha256,
      replay_result: clone(providerExpanded),
      replay_result_sha256: expandedSha256,
    })).toThrow("FACTORY_CLAIM_CEILING_MISMATCH:proof-node");

    providerOwned.accounting.positives_declared = 999;
    providerOwned.semantic_output.state = "mutated-after-replay";
    providerOwned.claim_ceiling = "provider-expanded claim";
    expect(stable).toMatchObject({
      semantic_output: { state: "original" },
      accounting: { positives_declared: 2 },
      claim_ceiling: "candidate proof accounting only",
    });
    expect(Object.isFrozen(stable)).toBe(true);
    expect(Object.isFrozen(stable.accounting)).toBe(true);
    expect(Object.isFrozen(stable.semantic_output)).toBe(true);
    expect(() => {
      (stable.accounting as { positives_declared: number }).positives_declared = 3;
    }).toThrow();
    expect(() => bindReplayVerifiedSemanticResult({
      node_id: "proof-node",
      locked_claim_ceiling: "candidate proof accounting only",
      direct_sha256: "0".repeat(64),
      replay_result: clone(providerOwned),
      replay_result_sha256: sha256(canonicalJson(providerOwned)),
    })).toThrow("FACTORY_REPLAY_DRIFT");
  });
});
