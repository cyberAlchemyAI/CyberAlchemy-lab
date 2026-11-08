export const L2_ERROR_CODES = [
  "L1_PREREQUISITE_MISSING",
  "L1_PREREQUISITE_UNADMITTED",
  "PROPERTY_DEFINITION_UNADMITTED",
  "COMPARISON_CONTRACT_UNADMITTED",
  "PROVIDER_RUNTIME_UNAVAILABLE",
  "PROVIDER_RUNTIME_UNAPPROVED",
  "TARGET_BASELINE_DRIFT",
  "GRAPH_REQUEST_SCHEMA_INVALID",
  "GRAPH_SCHEMA_INVALID",
  "GRAPH_AUTHORITY_MISMATCH",
  "SOURCE_MANIFEST_MISSING",
  "SOURCE_DIGEST_STALE",
  "REGISTRY_DIGEST_STALE",
  "EXTRACTOR_UNPINNED",
  "CANONICALIZATION_UNSUPPORTED",
  "FACT_NODE_ID_DUPLICATE",
  "FACT_EDGE_ID_DUPLICATE",
  "FACT_ENDPOINT_MISSING",
  "FACT_PROJECTION_DRIFT",
  "FACT_DIGEST_MISMATCH",
  "PROVIDER_VERSION_MISMATCH",
  "PROVIDER_ADAPTER_STALE",
  "PROVIDER_INPUT_DIGEST_MISMATCH",
  "PROVIDER_SCOPE_INVALID",
  "PROVIDER_TIMEOUT",
  "PROVIDER_EXECUTION_FAILED",
  "PROVIDER_OUTPUT_INVALID",
  "PROVIDER_RESULT_UNMAPPED",
  "PROVIDER_RECEIPT_TAMPERED",
  "JOIN_RECEIPT_MISSING",
  "JOIN_REQUEST_MISMATCH",
  "JOIN_FACT_DIGEST_MISMATCH",
  "JOIN_PROPERTY_MISMATCH",
  "JOIN_MAPPING_MISMATCH",
  "JOIN_DOMAIN_INCOMPARABLE",
  "JOIN_RESULT_DISAGREEMENT",
  "JOIN_CLAIM_INFLATION",
  "JOIN_RECEIPT_TAMPERED",
  "UNDECLARED_WRITE",
] as const;

export type L2ErrorCode = (typeof L2_ERROR_CODES)[number];
export type L2Phase =
  | "admission"
  | "projection"
  | "translation"
  | "execution"
  | "mapping"
  | "join"
  | "replay"
  | "closure";

export class L2Error extends Error {
  constructor(
    readonly code: L2ErrorCode,
    readonly phase: L2Phase,
    message: string,
    readonly exitCode: 1 | 2 = 1,
  ) {
    super(message);
    this.name = "L2Error";
  }
}

export function fail(
  code: L2ErrorCode,
  phase: L2Phase,
  message: string,
  exitCode: 1 | 2 = 1,
): never {
  throw new L2Error(code, phase, message, exitCode);
}

export type ExactRef = {
  readonly path: string;
  readonly sha256: string;
  readonly size_bytes: number;
};

export type NodeFact = {
  readonly node_id: string;
  readonly feature_id: string;
  readonly kind: string;
};

export type EdgeFact = {
  readonly edge_id: string;
  readonly predicate: string;
  readonly from: string;
  readonly to: string;
};

export type MintedGraph = {
  readonly schema_version: "minted-graph/v1";
  readonly authority: "generated-semantic-read-model";
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly language: {
    readonly profile_digest: string;
    readonly kinds_digest: string;
    readonly relationships_digest: string;
  };
  readonly nodes: readonly (NodeFact & { readonly body?: unknown })[];
  readonly edges: readonly {
    readonly edge_id: string;
    readonly type: string;
    readonly from: string;
    readonly to: string;
  }[];
};

export type SourceManifest = {
  readonly schema_version: "minted-source-manifest/v1";
  readonly authority: "generated-provenance-read-model";
  readonly project_id: string;
  readonly source_set_digest: string;
  readonly inputs: readonly { readonly path: string; readonly digest: string }[];
};

export type PropertyDefinition = {
  readonly schema_version: "evf.graph-law-property/v1";
  readonly property_id: string;
  readonly property_version: string;
  readonly property_class: "reachability";
  readonly result_semantics: "universal-via-violation-query";
  readonly evaluation_mode: "exact-instance";
  readonly selected_relation_digest: string;
  readonly selected_relation_digest_material: {
    readonly closure: "non-reflexive-transitive-one-or-more";
    readonly directed: true;
    readonly required_sources: readonly string[];
    readonly selected_predicates: readonly string[];
    readonly target: string;
  };
  readonly subject: {
    readonly project_id: string;
    readonly required_sources: readonly string[];
    readonly target: string;
    readonly selected_predicates: readonly string[];
  };
  readonly claim_ceiling: string;
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
};

export type FactPayload = {
  readonly nodes: readonly NodeFact[];
  readonly edges: readonly EdgeFact[];
};

export type FactProjection = FactPayload & {
  readonly facts_digest: string;
  readonly universe_digest: string;
  readonly selected_edges: readonly (readonly [string, string])[];
  readonly selected_relation_digest: string;
  readonly scope_digest: string;
  readonly atom_map: Readonly<Record<string, string>>;
};

export type GraphLawRequest = {
  readonly schema_version: "evf.graph-law-request/v1";
  readonly request_id: string;
  readonly request_kind: "graph-law-evaluation";
  readonly request_state: "execution-ready";
  readonly decision_ref: ExactRef;
  readonly admission: {
    readonly layer: "L2";
    readonly prerequisite_receipts: readonly ExactRef[];
    readonly authority_effect: "none";
    readonly release_admission: "not-granted";
  };
  readonly subject: {
    readonly fact_manifest_ref: ExactRef;
    readonly facts_digest: string;
    readonly project_id: string;
    readonly source_set_digest: string;
    readonly registry_digests: {
      readonly profile: string;
      readonly kinds: string;
      readonly relationships: string;
    };
    readonly universe_digest: string;
  };
  readonly property: {
    readonly property_id: string;
    readonly property_version: string;
    readonly definition_ref: ExactRef;
    readonly property_class: "reachability";
    readonly result_semantics: "universal-via-violation-query";
    readonly evaluation_mode: "exact-instance";
    readonly selected_relation_digest: string;
    readonly scope_contract_ref: ExactRef;
  };
  readonly comparison_contract_ref: ExactRef;
  readonly providers: readonly [
    {
      readonly provider_kind: "datalog";
      readonly evaluator_id: "souffle";
      readonly evaluator_version: "2.5";
      readonly runtime_ref: ExactRef;
      readonly adapter_ref: ExactRef;
      readonly query_or_model_ref: ExactRef;
      readonly invocation_contract_ref: ExactRef;
      readonly evaluation_domain: {
        readonly kind: "exact-closed-world-fact-set";
        readonly complete_relation_evaluation: true;
        readonly universe_digest: string;
        readonly selected_relation_digest: string;
        readonly scope_contract_ref: ExactRef;
      };
    },
    {
      readonly provider_kind: "alloy";
      readonly evaluator_id: "alloy";
      readonly evaluator_version: "6.2.0";
      readonly runtime_ref: ExactRef;
      readonly adapter_ref: ExactRef;
      readonly query_or_model_ref: ExactRef;
      readonly invocation_contract_ref: ExactRef;
      readonly evaluation_domain: {
        readonly kind: "exact-closed-world-fact-set";
        readonly exact_universe: true;
        readonly exact_selected_tuples: true;
        readonly universe_digest: string;
        readonly selected_relation_digest: string;
        readonly scope_contract_ref: ExactRef;
      };
    },
  ];
  readonly execution_policy: {
    readonly timeout_ms: 30000;
    readonly max_output_bytes: 1048576;
    readonly network: "forbidden";
    readonly working_directory: string;
    readonly environment_allowlist: readonly ["LANG", "LC_ALL", "PATH", "TZ"];
    readonly deterministic_seed: null;
  };
  readonly claim_ceiling: "request-only-no-evaluation-claim";
  readonly residue: readonly [];
};

export type NormalizedOutcome =
  | "counterexample"
  | "no-counterexample"
  | "unresolved";

export type ProcessEvidence = {
  readonly argv: readonly string[];
  readonly cwd: string;
  readonly started_at: string;
  readonly finished_at: string;
  readonly exit_code: number | null;
  readonly signal: NodeJS.Signals | null;
  readonly timed_out: boolean;
  readonly output_limit_exceeded: boolean;
  readonly network_isolation: {
    readonly kind: "inherited-linux-network-namespace";
    readonly process_namespace: string;
    readonly host_namespace: string;
  };
  readonly stdout: Buffer;
  readonly stderr: Buffer;
};

export type ProviderReceipt = {
  readonly schema_version: "evf.graph-law-provider-receipt/v1";
  readonly receipt_id: string;
  readonly receipt_family: "graph-relation" | "formal-static";
  readonly request_ref: ExactRef;
  readonly fact_manifest_ref: ExactRef;
  readonly property_definition_ref: ExactRef;
  readonly comparison_contract_ref: ExactRef;
  readonly scope_contract_ref: ExactRef;
  readonly request_id: string;
  readonly facts_digest: string;
  readonly universe_digest: string;
  readonly selected_relation_digest: string;
  readonly scope_digest: string;
  readonly property_id: string;
  readonly property_version: string;
  readonly provider: {
    readonly kind: "datalog" | "alloy";
    readonly id: "souffle" | "alloy";
    readonly version: "2.5" | "6.2.0";
    readonly runtime_ref: ExactRef;
    readonly adapter_ref: ExactRef;
    readonly query_or_model_ref: ExactRef;
    readonly invocation_contract_ref: ExactRef;
    readonly solver_id: string | null;
    readonly solver_version: string | null;
    readonly options_digest: string;
  };
  readonly translation: {
    readonly provider_input_ref: ExactRef;
    readonly source_facts_digest: string;
    readonly projection_receipt_ref: ExactRef;
    readonly omitted_fact_count: 0;
    readonly invented_fact_count: 0;
    readonly translation_digest: string;
  };
  readonly execution: {
    readonly run_id: string;
    readonly status: "completed";
    readonly exit_code: 0;
    readonly timed_out: false;
    readonly started_at: string;
    readonly finished_at: string;
    readonly stdout_ref: ExactRef;
    readonly stderr_ref: ExactRef;
    readonly raw_output_ref: ExactRef;
    readonly exact_command: readonly string[];
  };
  readonly native_result:
    | {
        readonly kind: "violation-relation";
        readonly relation_name: "Violation";
        readonly row_schema_digest: string;
        readonly row_count: number;
        readonly rows_digest: string;
        readonly rows_ref: ExactRef;
        readonly complete: true;
      }
    | {
        readonly kind: "alloy-command";
        readonly command_kind: "check";
        readonly command_label: "NoViolation";
        readonly scope: Readonly<Record<string, unknown>>;
        readonly scope_digest: string;
        readonly outcome: "sat" | "unsat" | "unknown";
        readonly instance_or_counterexample_ref: ExactRef | null;
        readonly solution_count: number | null;
        readonly cli_receipt_ref: ExactRef;
      };
  readonly normalized_result: {
    readonly outcome: NormalizedOutcome;
    readonly domain_kind: "exact-closed-world-fact-set";
    readonly evaluation_mode: "exact-instance";
    readonly evidence_refs: readonly ExactRef[];
    readonly result_payload_digest: string;
  };
  readonly semantic_result_digest: string;
  readonly residue: readonly Readonly<Record<string, unknown>>[];
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly claim_ceiling:
    | "exact-finite-corpus-relation-result-only"
    | "bounded-static-model-result-only";
};

export type JoinStatus = "consistent" | "unresolved" | "blocked";
export type JoinReceipt = {
  readonly schema_version: "evf.graph-law-join-receipt/v1";
  readonly join_receipt_id: string;
  readonly request_ref: ExactRef;
  readonly fact_manifest_ref: ExactRef;
  readonly property_definition_ref: ExactRef;
  readonly comparison_contract_ref: ExactRef;
  readonly scope_contract_ref: ExactRef;
  readonly request_id: string;
  readonly facts_digest: string;
  readonly universe_digest: string;
  readonly selected_relation_digest: string;
  readonly scope_digest: string;
  readonly property_id: string;
  readonly property_version: string;
  readonly provider_receipts: {
    readonly datalog: ExactRef;
    readonly alloy: ExactRef;
  };
  readonly provider_semantic_result_digests: {
    readonly datalog: string;
    readonly alloy: string;
  };
  readonly preflight: {
    readonly same_request: boolean;
    readonly same_facts: boolean;
    readonly same_universe: boolean;
    readonly same_property: boolean;
    readonly same_mapping: boolean;
    readonly provider_kinds_exact: boolean;
    readonly receipts_valid: boolean;
    readonly domains_comparable: boolean;
  };
  readonly mapped_results: {
    readonly datalog: {
      readonly outcome: NormalizedOutcome;
      readonly domain_kind: "exact-closed-world-fact-set";
      readonly evaluation_mode: "exact-instance";
      readonly result_payload_digest: string;
    };
    readonly alloy: {
      readonly outcome: NormalizedOutcome;
      readonly domain_kind: "exact-closed-world-fact-set";
      readonly evaluation_mode: "exact-instance";
      readonly result_payload_digest: string;
    };
  };
  readonly join_status: JoinStatus;
  readonly consistency_class:
    | "counterexample-consistent"
    | "no-counterexample-consistent-under-declared-bounds"
    | "provider-disagreement"
    | "not-comparable";
  readonly evidence_refs: readonly ExactRef[];
  readonly residue: readonly Readonly<Record<string, unknown>>[];
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly claim_ceiling: "property-specific-consistency-over-shared-facts-only";
  readonly join_payload_digest: string;
};
