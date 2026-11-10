# Define semantic preparation

This is the active, bounded semantic-preparation selection for the existing Define CLI. It is part of the same product and uses the same canonical `define/session.jsonl`. Generated applications and native role artifacts are disposable `.local` build outputs. The protected Entry application retains its journal-observation cache; ordinary local CLI execution does not impersonate an authenticated service actor.

`../modules/work` owns the actual session. Project and Work refs may both be `null`; the directory supplied to `--work` is a storage directory, not proof of semantic Work membership. `PreparationContext` consumes exact shared workspace observations. Work context requires Project and a membership observation. Define records source observations and declared attribution; it does not establish workspace membership or create Product, Project, Work or Goal records.

Use the product's `./define` launcher:

```sh
./define start --work SESSION_DIRECTORY --file START.json --actor ACTOR
./define ask --work SESSION_DIRECTORY --file QUESTION.json --actor ACTOR
./define respond --work SESSION_DIRECTORY --file RESPONSE.json --actor ACTOR
./define next --work SESSION_DIRECTORY
./define discover --work SESSION_DIRECTORY --catalog SELECTED_REGISTRY.json --query 'Exact identifier or term' --actor ACTOR
./define bind --file ORIGINAL_DOCUMENT
./define fields --work SESSION_DIRECTORY --file BOUND_INPUT.json --actor ACTOR --id COMMAND_ID
./define notes --work SESSION_DIRECTORY
./define replay --work SESSION_DIRECTORY
```

`start` takes the existing explicit Start document: `session_id`, `scope`, `request_revision`, `request_lineage`, and `validation_scope`. Scope carries goal, originating intent, context description, consumer and intended use; use `project: null, work: null` for preparation without those identities. Initialize the request lineage with its three optional bindings explicitly `null`. Initial context sufficiency is unknown. A context question can be asked before any sufficient-context assertion or concept declaration:

```json
{"question_id":"question:intent","concept_id":null,"target":{"tag":"Context","fields":{"field_ref":"originating_intent"}},"question":"What outcome should this meaning support?","owner_route":"declared:requester","status":"Open"}
```

For a concept question, supply its actual `concept_id` and either an explicit matching `Concept` target or `target: null` for the original concept-question route. Responses preserve Answered, Corrected, Deferred and Refused status, actual text and declared actor. A deferred/refused context answer does not create a fictional concept disposition. `next` uses the current journal state, and immediately applicable field findings for a selected candidate. Its result is guidance, not readiness permission.

Discovery reads the explicitly selected registry's `entries` (`definition_id`, `version`, `term`, `path`, `sha256`) in native batches of 25. Comparison is exact identifier or term, across the versions in that selection. Results and empty searches retain the exact catalog, query, searched scope and source cut as reported source observations. They do not certify the registry's standing, prove exhaustive semantic discovery, or automatically select reuse. Use the existing handling commands for explicit Reuse, Propose, Open, ApplyParameters or ChangeMeaning selection.

Semantic commands `context`, `lookup`, `assessment`, `contribute`, `candidate`, `fields`, `inspect-fields`, `revise`, `assess`, `handoff`, and `ack` accept `--work`, `--file`, `--actor`, and an optional stable `--id`. Their file is an envelope:

```json
{"input":{"fields":[{"field_key":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","contributions":"0"}]},"documents":[]}
```

`input` is the exact native operation input. Native UInt64 values are decimal strings; optional fields are explicit `null`. `documents` holds the original-byte `{binding, bytes_base64}` values returned by `bind`. Every Binding reachable from the operation input must resolve to exactly those original bytes. Logical aliases are `doc_<sha256>`; original paths can be retained inside bound manifests and are never truncated into aliases. A maximum 100 documents / 8 MiB aggregate is accepted, within the existing native frame and journal bounds. Oversized input is refused rather than silently shortened.

The operation shapes are authored in `contracts.alch` and `design.alch`:

| Command | Input | Effect |
|---|---|---|
| `context` | `{value: PreparationContext}` | Records the selected workspace/context observation; does not declare context sufficient. Use the existing SetContext command for an attributable sufficiency evaluation. |
| `lookup` | `{request, observation, actual_request}` | Records an externally supplied bound lookup observation; current head facts are inserted and validated. |
| `assessment` | `{value: CandidateAssessment}` | Records applicability and explanation with declared assessor and evidence. |
| `contribute` | `{value: FieldContribution, draft_document: Binding}` | Resolves source and target pointers against the captured original JSON bytes before recording attribution. |
| `candidate` | `{value: CandidateDraft}` | Records the explicitly selected draft and its contribution/requirement manifests. |
| `fields` | `{fields: List<FieldRequirement>}` | Validates reported field counts and derives missing/ambiguous keys. |
| `inspect-fields` | `{manifest: Binding}` | Resolves source and draft pointers, then derives missing or conflicting values natively. |
| `revise` | `{plan: RevisionPlan, observed_predecessor: Binding}` | Validates complete Preserve/Recheck/Retire coverage and exact predecessor. |
| `assess` | `{value: PreparationCheck}` | Inserts actual snapshot, context, selection/application counts and observation facts; produces scoped Reviewable/NeedsInput/NotEvaluable with no authority effect. |
| `handoff-input` | `{preparation_context, handoff_ref, check: PreparationCheck}` plus `--package` | Read-only preview producing a fresh `{input, documents}` bundle for handoff; no journal change. |
| `handoff` | `{value: HandoffRequest}` plus `--package` | Inspects the actual package, checks it against the current exported request, captures its original members, and creates a version-exact handoff for that observed cut. |
| `ack` | `{value: Acknowledgement}` | Validates a typed ReportedHandoffResponse against a handoff already recorded in this session; preserves reported acknowledgement posture. |

An `inspect-fields` manifest has schema version `cal.define.field-contributions/v1`, a `draft_document` Binding, `requirements:[{target_selector}]` and `contributions:[FieldContribution]`. All referenced source, draft and attribution documents must be included in the envelope. Source and target JSON Pointers must resolve; explicit null draft placeholders are allowed. Root pointers, escaped keys and array indexes are supported. Native calculations count distinct observed source JSON values per target: agreeing contributions count once; different values are ambiguous. No normative value is invented. Selected requirements do not replace full Definition/v2 structure, fidelity, applicability and complete leaf-lineage validation.

`assess --package PACKAGE` observes the matching current package and selects its native readiness for the requested use. ApplyDeclaredParameters requires actual `apply-parameters` readiness; an unrelated materialized Definition proves nothing about parameter completeness. MaterializeCandidate runs actual schema/fidelity/lineage/renderer checks without publishing files. The complete package observation is retained and reverified during replay. Without matching proof, caller completion flags cannot establish completeness. Declared checks and findings remain attributable; Reviewable never grants external permission or semantic acceptance.

Create handoff reports with `handoff-input --work SESSION --file PREVIEW.json --package PACKAGE --actor ACTOR`. Save its JSON output as the input file for `handoff` with the same current package. Preview input uses the usual `{input, documents}` envelope and supplies `preparation_context`, `handoff_ref`, and `check`. Referenced check/obligation/context documents must be captured. The preview emits typed inventory, obligations, evidence and scoped-assessment reports. Each binds the exact session, revision, source epoch, snapshot and intended use. Execution rechecks the inventory/evidence against the journal and recomputes readiness from the package. Any intervening edit requires a fresh package and preview; existing reports are never silently refreshed.

`ack` requires bound PreparedHandoff JSON (`cal.define.prepared-handoff/v1`) and ReportedHandoffResponse JSON (`cal.define.reported-handoff-response/v1`). The response contains `handoff_ref`, `handoff_sha256`, `session_ref`, `session_revision`, `source_cut`, `intended_use`, `declared_responder`, `message: Binding`, and `posture: "reported-acknowledgement"`. Capture the original message too. All correlation fields must equal the recorded handoff and acknowledgement input. Valid-looking unrecorded handoffs are refused. Documents referenced by the producer handoff are resolved from its verified canonical event and retained in acknowledgement evidence, so the consumer need not recapture the original package. Responder attribution is declared; authentication and consumer acceptance belong to their external owners.

For selective revision, add `--start SUCCESSOR_START.json --package PREDECESSOR_PACKAGE` to `revise`; use `--evaluation CONTEXT.json` if scope changes. Concept keys in the partition are SHA-256 of the original UTF-8 concept IDs. The package is actually inspected against the prior session. The native carry plan checks complete coverage and revision identity. Retired concepts are removed; Recheck concepts remain required with no copied handling. Preserve currently carries independent Reuse, Propose or Open handling only when scope is unchanged. Dependency-sensitive ApplyParameters/ChangeMeaning content requires Recheck. Applications, assessments, materialization selection and confirmation are cleared for re-evaluation. The sequence is preflighted through native transitions, then written with stable per-command IDs; retry resumes identical commands. The reviewed plan remains visible if application is refused.

Handoff records identify the observed pre-note session revision and package cut. Appending the handoff note creates a new journal revision and clears stale confirmation, as any edit does. It does not relabel the old package as the newly edited request. The handoff retains exact context, consumer/use, candidate inventory, obligations and preparation assessment. A receipt is distinct from acceptance.

Ordinary commands keep journal envelope v2. Semantic notes use explicit v3 envelopes with source-selected operation inputs/results and original-byte attachments. Replay verifies hashes, exact source epoch, session/revision scope, native operation results and package proofs. No old decoder silently accepts a new note shape. Conflicting command IDs, foreign scope, stale revisions, closed sessions and changed bytes are refused before publication. Self-contained note evidence is available to normal `prepare` from the journal, without copying runtime code or requiring a second note store.

Outside Define: construction-chain enforcement, shared workspace/catalog ownership, generic Artifact Type/business-record creation, semantic admission, signing/apply, canonical publication and consumer conformance. The pinned Craft toolchain and its resource limits are unchanged.

Run `node preparation/verify.mjs` for isolated protected Entry contract checks and `node verify-preparation-workflow.mjs` for actual local CLI, journal and package integration. Run `node verify-validation-gaps.mjs` for the four causal audit regressions and rejection cases. Retained production authority is never inferred from fixture credentials or local candidate checks.