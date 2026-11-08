import { digestSfolValue } from "../cases/index.js";
import {
  type EffectTraceContract,
  type ValidatedEffectTrace,
} from "../runners/effect/contracts.js";
import type { TypedLogicModule } from "../language/typecheck.js";
import {
  evaluatePredicate,
  integerValue,
  type EvaluationEnvironment,
  type SemanticValue,
} from "./index.js";

export interface EffectRelationEvaluation {
  readonly schema_version: "domainspec-sfol-effect-evaluation/v1";
  readonly clause_id: string;
  readonly trace_id: string;
  readonly trace_digest: string;
  readonly status: "pass" | "fail" | "indeterminate";
  readonly detail: string;
  readonly evaluation_digest: string;
}

export function evaluateEffectRelation(
  typed: TypedLogicModule,
  clauseId: string,
  contract: EffectTraceContract,
  trace: ValidatedEffectTrace,
  baseVariables: Readonly<Record<string, SemanticValue>> = {},
): EffectRelationEvaluation {
  const finish = (
    status: EffectRelationEvaluation["status"],
    detail: string,
  ): EffectRelationEvaluation => {
    const unsigned = {
      schema_version: "domainspec-sfol-effect-evaluation/v1" as const,
      clause_id: clauseId,
      trace_id: trace.trace_id,
      trace_digest: trace.trace_digest,
      status,
      detail,
    };
    return Object.freeze({
      ...unsigned,
      evaluation_digest: digestSfolValue(unsigned),
    });
  };

  if (trace.contract_id !== contract.contract_id) {
    return finish(
      "indeterminate",
      "validated trace and relation contract identities differ",
    );
  }
  const { trace_digest: _digest, ...unsignedTrace } = trace;
  if (digestSfolValue(unsignedTrace) !== trace.trace_digest) {
    return finish("indeterminate", "validated trace digest is stale");
  }
  const clause = typed.source.clauses.find(
    (candidate) => candidate.clause_id === clauseId,
  );
  if (clause === undefined) {
    return finish("indeterminate", "effect relation clause is absent");
  }
  if (clause.kind !== "effect-relation") {
    return finish(
      "indeterminate",
      `clause kind ${clause.kind} is not effect-relation`,
    );
  }
  for (const reserved of ["pre", "post", "effects", "result"]) {
    if (Object.hasOwn(baseVariables, reserved)) {
      return finish(
        "indeterminate",
        `base environment cannot override reserved variable ${reserved}`,
      );
    }
  }

  const variables: Record<string, SemanticValue> = {
    ...baseVariables,
    pre: stateValue(
      contract.pre_record_declaration_id,
      trace.pre_state,
    ),
    post: stateValue(
      contract.post_record_declaration_id,
      trace.post_state,
    ),
    effects: {
      tag: "list",
      items: trace.effects.map(
        (effect): SemanticValue => ({
          tag: "record",
          declaration_id: contract.effect_record_declaration_id,
          fields: {
            sequence: integerValue(effect.sequence.toString()),
            kind: { tag: "string", value: effect.kind },
            name: { tag: "string", value: effect.name },
            payload: effect.payload,
          },
        }),
      ),
    },
  };
  if (trace.return_value !== null) {
    variables.result = trace.return_value;
  }

  const environment: EvaluationEnvironment = { variables };
  const result = evaluatePredicate(typed, clause.expression, environment);
  if (result.status === "indeterminate") {
    return finish(
      "indeterminate",
      `${result.diagnostic.code}: ${result.diagnostic.detail}`,
    );
  }
  return finish(
    result.value ? "pass" : "fail",
    result.value
      ? "effect trace satisfies the source relation"
      : "effect trace violates the source relation",
  );
}

function stateValue(
  declarationId: string,
  fields: Readonly<Record<string, SemanticValue>>,
): SemanticValue {
  return Object.freeze({
    tag: "record",
    declaration_id: declarationId,
    fields,
  });
}
