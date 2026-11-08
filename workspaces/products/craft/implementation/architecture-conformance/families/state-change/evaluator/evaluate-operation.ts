import type {
  OperationEvaluationV1,
  OperationObservationV1,
} from "../contracts/operation-contracts.js";

export const evaluateOperation = (input: Readonly<{
  observation: OperationObservationV1;
  expectedBindingId: string;
  expectedBindingSourceSha256: string;
  requestId: string;
}>): OperationEvaluationV1 => {
  const findings: OperationEvaluationV1["findings"][number][] = [];
  if (input.observation.binding_id !== input.expectedBindingId ||
      input.observation.binding_source_sha256 !== input.expectedBindingSourceSha256) {
    findings.push({
      code: "OP_BINDING_STALE", expected: input.expectedBindingId,
      observed: input.observation.binding_id,
    });
  }
  if (input.observation.payout_ids.length !== 1) {
    findings.push({
      code: "OP_STATE_CHANGE_MISSING", expected: 1,
      observed: input.observation.payout_ids.length,
    });
  }
  const expectedEvent = `PayoutCreated:${input.requestId}`;
  if (input.observation.payout_ids[0] !== input.requestId ||
      input.observation.events[0] !== expectedEvent) {
    findings.push({
      code: "OP_POSTCONDITION_MISSING",
      expected: { payout_id: input.requestId, event: expectedEvent },
      observed: {
        payout_id: input.observation.payout_ids[0] ?? null,
        event: input.observation.events[0] ?? null,
      },
    });
  }
  return Object.freeze({
    schema_version: "OperationEvaluation/v1" as const,
    verdict: findings.length === 0 ? "pass" as const : "fail" as const,
    findings: Object.freeze(findings.map((item) => Object.freeze({ ...item }))),
    authority_effect: "none" as const,
  });
};
