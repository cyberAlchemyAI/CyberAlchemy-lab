# Inference router: D1 Definition Pack

Status: candidate. Owner: Alch product owner. Authority effect: none.

Machine source: [definition-pack.json](definition-pack.json). This companion presents the same eight proposed definitions and API scope. Durable Define-session evidence is unavailable; this is an isolated candidate.

## Definitions

### InferenceRequest

Disposition: propose. Decision owner: Alch product owner.

Normative: A tenant-scoped request asks for text.generate over an ordered, nonempty list of text messages, with an optional public model alias, routing strategy, positive maximum output-token count and stream flag.

Formal: Request = (request_id, tenant_id, task, messages, model?, strategy, max_output_tokens, stream).

Plain language: A caller submits a conversation and chooses automatic routing or one named model.

Domain example: Example: one user message, no model, balanced strategy, 256 output tokens, JSON response.

Boundary: Tenant and request IDs are server-assigned; request fields never select credentials or upstream URLs.

### ModelOffering

Disposition: propose. Decision owner: Alch product owner.

Normative: A versioned public alias describes a task and its supported input, output and streaming limits; discovery includes only offerings allowed for the authenticated tenant.

Formal: Offering = (alias, version, tasks, context_limit, output_limit, streaming).

Plain language: An offering tells a caller which model option it may request.

Domain example: fixture-chat-a and fixture-chat-b are local test aliases, not claims about real model availability.

Boundary: An alias is neither a provider address nor a quality or availability guarantee.

### ProviderBinding

Disposition: propose. Decision owner: Alch product owner.

Normative: A versioned operator-owned binding connects an offering to one fixed provider deployment, mapper pair, credential reference, enabled state and execution limits.

Formal: Binding = (id, version, offering, deployment_ref, credential_ref, mappers, enabled, limits).

Plain language: A binding describes how the service reaches an eligible provider.

Domain example: fixture-provider-a and fixture-provider-b are independent local bindings, both supporting text.generate and streaming.

Boundary: Configuration is private; fixture bindings grant no external-call or spending authority.

### RoutingDecision

Disposition: propose. Decision owner: Alch product owner.

Normative: A decision pins eligible bindings and the versioned policy. Automatic routing chooses the lowest configured strategy rank, breaking ties by stable binding ID. Explicit model selection restricts eligibility to that alias and never substitutes another alias.

Formal: eligible = enabled AND tenant_allowed AND task_supported AND limits_fit AND features_supported; selected = min(eligible, (strategy_rank, binding_id)).

Plain language: First exclude unsuitable providers; then choose predictably among the remaining ones.

Domain example: balanced-v1 ranks fixture-provider-a before fixture-provider-b; disabling a selects b. No eligible binding yields 503.

Boundary: Configured cost/latency ranks are operator preferences, not measured price, speed or quality evidence.

### InferenceAttempt

Disposition: propose. Decision owner: Alch product owner.

Normative: An attempt executes a pinned binding within one request deadline and concurrency budget. Automatic routing allows at most one fallback, only after a binding-specific outcome proves no execution occurred and before stream output starts.

Formal: attempts <= 2; fallback => automatic AND proven_not_executed AND NOT stream_started AND deadline_remaining.

Plain language: An uncertain timeout must not cause a second generation or charge.

Domain example: A fixture pre-execution rejection may try b after a; ambiguous timeout or a partial stream may not.

Boundary: Disconnect triggers local cancellation and an upstream cancellation attempt, not proof that remote work or charges stopped.

### InferenceResult

Disposition: propose. Decision owner: Alch product owner.

Normative: A completed result names the request, selected public alias, text output, finish reason and usage. Streaming sends started, zero or more delta events, then one completed or error event while writable; started pins the alias for that stream.

Formal: Result = (request_id, model, output.text, finish_reason, usage); Stream = started, delta*, (completed | error).

Plain language: A caller receives one attributable answer or an explicit failure.

Domain example: A partial stream followed by failure ends with error and is never spliced with a different provider.

Boundary: Connection loss before a terminal event means incomplete output; fixture text is not evidence of model inference.

### UsageObservation

Disposition: propose. Decision owner: Alch product owner.

Normative: Each attempt records input and output token counts as nonnegative integers or null, with provider-reported, locally-estimated or unavailable provenance for each count. Unknown values stay null; estimates name their estimator version.

Formal: UsageCount = (value: integer>=0 | null, provenance, estimator_version?); Usage = (attempt_id, input_tokens, output_tokens).

Plain language: Usage says what was measured, estimated or remains unknown.

Domain example: A provider omitting token counts yields null with unavailable provenance, never zero.

Boundary: Usage is neither billing nor payment verification; failed-attempt observations remain distinct from final-result usage.

### IdempotencyRecord

Disposition: propose. Decision owner: Alch product owner.

Normative: An optional tenant-scoped key binds to the normalized validated request, its defaults and pinned request record. Matching in-flight duplicates receive a defined in-progress response; different normalized bytes return 409. Completed JSON can replay within retention; streams never re-execute under the same retained key.

Formal: Identity = (tenant_id, key); same_identity AND different_request => 409; executions_per_retained_identity <= 1 logical request.

Plain language: Repeating a retained key must not start another inference request.

Domain example: Two concurrent JSON submissions with the same tenant, key and normalized request share the original request ID; the duplicate gets 409 request_in_progress until completion.

Boundary: Retention expiry ends deduplication protection; stream resumption and durable cross-restart protection remain open.

## API scope

```json
{
  "status": "semantic-candidate-not-openapi-or-compiler-output",
  "task": "text.generate",
  "messages": {
    "roles": [
      "system",
      "user",
      "assistant"
    ],
    "content": "nonempty text",
    "ordering": "preserved",
    "constraints": "nonempty array, at least one user message; no tools or multimodal parts"
  },
  "defaults": {
    "strategy": "balanced",
    "max_output_tokens": 256,
    "stream": false
  },
  "unknown_fields": "reject at every request-object level",
  "model_selection": "Omitted model selects automatically; provided nonempty alias selects explicitly. Null is invalid for optional fields.",
  "parameters": "Only max_output_tokens is supported in this slice; positive integer excluding booleans, bounded by offering and tenant limits.",
  "endpoints": [
    {
      "method": "GET",
      "path": "/v1/capabilities",
      "meaning": "Tenant-visible tasks and request/output capabilities."
    },
    {
      "method": "GET",
      "path": "/v1/models",
      "meaning": "Tenant-visible aliases and declared limits."
    },
    {
      "method": "POST",
      "path": "/v1/inference",
      "meaning": "Automatic or explicit text generation as JSON or SSE."
    },
    {
      "method": "GET",
      "path": "/healthz",
      "meaning": "Unauthenticated liveness only; no model/provider diagnostics."
    }
  ],
  "authentication": "Bearer key resolves tenant server-side for /v1/*; healthz has no secrets or readiness claim.",
  "request_example": {
    "task": "text.generate",
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "Explain event-driven systems."
        }
      ]
    },
    "routing": {
      "strategy": "balanced"
    },
    "parameters": {
      "max_output_tokens": 256
    },
    "stream": false
  },
  "errors": {
    "400": "invalid_input",
    "401": "invalid_key",
    "403": "forbidden_model_or_task",
    "404": "unknown_model",
    "409": [
      "idempotency_conflict",
      "request_in_progress",
      "stream_not_replayable"
    ],
    "429": "tenant_limit",
    "502": "upstream_failed",
    "503": "no_eligible_or_available_provider",
    "504": "deadline_exceeded"
  },
  "error_shape": "error {code, message, request_id}; no raw provider payloads or secrets.",
  "idempotency_header": "Idempotency-Key",
  "normalization": "Validate first; materialize documented defaults; canonicalize object key order; preserve message order and text bytes; include all semantic fields. Keep policy/binding versions on the original record so replay does not reroute.",
  "discovery_security": "Unknown and tenant-hidden aliases both return 404; 403 applies to a visible alias/task with an operation restriction.",
  "stream_contract": "started contains request_id and model; delta contains request_id, model and text; completed contains request_id, model, finish_reason and usage; error contains request_id and sanitized error. completed does not repeat text. No resumption.",
  "finish_reasons": [
    "stop",
    "length",
    "content_filter",
    "unknown"
  ],
  "fixture_candidates": [
    {
      "alias": "fixture-chat-a",
      "binding": "fixture-provider-a",
      "version": "fixture-v1",
      "balanced_rank": 10,
      "cost_rank": 20,
      "latency_rank": 10
    },
    {
      "alias": "fixture-chat-b",
      "binding": "fixture-provider-b",
      "version": "fixture-v1",
      "balanced_rank": 20,
      "cost_rank": 10,
      "latency_rank": 20
    }
  ],
  "fixture_limits": {
    "max_request_bytes": 65536,
    "max_output_tokens": 1024,
    "deadline_seconds": 5,
    "global_concurrency": 2,
    "tenant_concurrency": 1,
    "idempotency_retention_seconds": 60
  },
  "fixture_limit_boundary": "Proposed local acceptance-test inputs only. Input context fitting requires a binding-specific estimator; unknown fit excludes the binding. No real tokenizer or production limit is selected.",
  "out_of_scope": [
    "embeddings",
    "images",
    "tool execution",
    "payments",
    "wallets",
    "blockchain jobs",
    "subscriptions",
    "Telegraph compatibility"
  ]
}
```

## Checks and allowed use

concept-record-schema: PASS. All eight records validate against define-package.schema.json handledDefinitionRecord.

concept-and-relationship-closure: PASS. Exactly one proposed disposition per required concept; all relationship endpoints resolve.

source-currency: PASS. Four whole-file source SHA-256 bindings match.

formal-define-lifecycle: NOT_EVALUABLE. No saved session or evaluator receipt; no central Define validation or admission claimed.

Review/challenge and candidate input to D2/D3 are allowed within their selected routes. This pack grants no canonical promotion, construction handoff, implementation authority, publication, deployment, paid calls or product approval.

## Open Questions

- **OQ-PROVIDERS**: Which two real provider deployments and public aliases should replace the fixtures? Owner: Inference operator and Alch product owner. Affected stage: Live provider verification. No live calls before provider, credential and budget selection. Next: Select deployments after local contracts and bindings are testable.
- **OQ-LIMITS**: What production deadlines, concurrency, request limits and idempotency retention are required? Owner: Inference operator. Affected stage: D9 candidate freeze and production readiness. Do not claim production readiness using local fixture limits. Next: Set and test concrete targets before candidate freeze.
- **OQ-COMPILER**: Which actual Alch/DomainSpec constructs support selection, mapping and the public API? Owner: Alch language and inference implementation owner. Affected stage: D3/D4. Do not treat unsupported syntax as compiled behavior. Next: Inspect compiler extension points and derive schemas from authored Alch.
- **OQ-SESSION**: When will a durable Define session and context-sufficiency evaluator be available? Owner: Define runtime owner. Affected stage: Formal Define lifecycle admission. Do not claim saved-session or evaluator receipt evidence. Next: Retain this isolated candidate and bind runtime evidence when available.
- **OQ-DEDUP**: What persistence and replay behavior should survive host restart? Owner: Alch product owner and inference implementation owner. Affected stage: D7/D9. No cross-restart deduplication claim without a tested storage contract. Next: Select retention, terminal-failure replay and persistence semantics before execution implementation.

Source hashes, context provenance, formal lifecycle gaps and refresh route are recorded in the machine pack.
