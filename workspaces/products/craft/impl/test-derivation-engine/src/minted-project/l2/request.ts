import { canonicalJson } from "./canonical-json.js";
import { fail, type ExactRef, type FactProjection, type GraphLawRequest, type PropertyDefinition } from "./types.js";

type CommonProviderRequestBinding = {
  readonly runtime_ref: ExactRef;
  readonly adapter_ref: ExactRef;
  readonly query_or_model_ref: ExactRef;
  readonly invocation_contract_ref: ExactRef;
};

export type ProviderRequestBinding =
  | (CommonProviderRequestBinding & {
      readonly provider_kind: "datalog";
      readonly evaluator_id: "souffle";
      readonly evaluator_version: "2.5";
    })
  | (CommonProviderRequestBinding & {
      readonly provider_kind: "alloy";
      readonly evaluator_id: "alloy";
      readonly evaluator_version: "6.2.0";
    });

export type RequestBindings = {
  readonly decision_ref: ExactRef;
  readonly prerequisite_ref: ExactRef;
  readonly fact_manifest_ref: ExactRef;
  readonly property_definition_ref: ExactRef;
  readonly comparison_contract_ref: ExactRef;
  readonly scope_contract_ref: ExactRef;
  readonly project_id: "financial-settlement";
  readonly source_set_digest: string;
  readonly registry_digests: {
    readonly profile: string;
    readonly kinds: string;
    readonly relationships: string;
  };
  readonly datalog: Extract<ProviderRequestBinding, { readonly provider_kind: "datalog" }>;
  readonly alloy: Extract<ProviderRequestBinding, { readonly provider_kind: "alloy" }>;
  readonly working_directory: string;
};

export function assertOutcomeFree(request: unknown): void {
  const forbidden = new Set([
    "expected_result",
    "expected_outcome",
    "normalized_outcome",
    "provider_result",
  ]);
  const visit = (value: unknown): void => {
    if (Array.isArray(value)) {
      value.forEach(visit);
      return;
    }
    if (value === null || typeof value !== "object") return;
    for (const [key, entry] of Object.entries(value as Record<string, unknown>)) {
      if (forbidden.has(key)) {
        fail("GRAPH_REQUEST_SCHEMA_INVALID", "admission", `request contains forbidden outcome key: ${key}`);
      }
      visit(entry);
    }
  };
  visit(request);
}

export function buildGraphLawRequest(
  requestId: string,
  projection: FactProjection,
  property: PropertyDefinition,
  bindings: RequestBindings,
): GraphLawRequest {
  const providerBase = {
    universe_digest: projection.universe_digest,
    selected_relation_digest: projection.selected_relation_digest,
    scope_contract_ref: bindings.scope_contract_ref,
  };
  const request: GraphLawRequest = {
    schema_version: "evf.graph-law-request/v1",
    request_id: requestId,
    request_kind: "graph-law-evaluation",
    request_state: "execution-ready",
    decision_ref: bindings.decision_ref,
    admission: {
      layer: "L2",
      prerequisite_receipts: [bindings.prerequisite_ref],
      authority_effect: "none",
      release_admission: "not-granted",
    },
    subject: {
      fact_manifest_ref: bindings.fact_manifest_ref,
      facts_digest: projection.facts_digest,
      project_id: bindings.project_id,
      source_set_digest: bindings.source_set_digest,
      registry_digests: bindings.registry_digests,
      universe_digest: projection.universe_digest,
    },
    property: {
      property_id: property.property_id,
      property_version: property.property_version,
      definition_ref: bindings.property_definition_ref,
      property_class: "reachability",
      result_semantics: "universal-via-violation-query",
      evaluation_mode: "exact-instance",
      selected_relation_digest: projection.selected_relation_digest,
      scope_contract_ref: bindings.scope_contract_ref,
    },
    comparison_contract_ref: bindings.comparison_contract_ref,
    providers: [
      {
        ...bindings.datalog,
        evaluation_domain: {
          kind: "exact-closed-world-fact-set",
          complete_relation_evaluation: true,
          ...providerBase,
        },
      },
      {
        ...bindings.alloy,
        evaluation_domain: {
          kind: "exact-closed-world-fact-set",
          exact_universe: true,
          exact_selected_tuples: true,
          ...providerBase,
        },
      },
    ],
    execution_policy: {
      timeout_ms: 30000,
      max_output_bytes: 1048576,
      network: "forbidden",
      working_directory: bindings.working_directory,
      environment_allowlist: ["LANG", "LC_ALL", "PATH", "TZ"],
      deterministic_seed: null,
    },
    claim_ceiling: "request-only-no-evaluation-claim",
    residue: [],
  };
  assertOutcomeFree(request);
  if (canonicalJson(request).includes('"expected_')) {
    fail("GRAPH_REQUEST_SCHEMA_INVALID", "admission", "request outcome leak");
  }
  return request;
}
