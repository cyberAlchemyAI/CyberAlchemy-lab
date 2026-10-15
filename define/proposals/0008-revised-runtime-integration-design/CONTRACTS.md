# Contract design

Status: revised proposed wire and package contracts for this design. These names are implementation-format choices, not admitted Artifact Types or new semantic Definitions. Existing Lab schemas govern selected carriers. Executable schema construction and conformance evidence are future implementation work; this document does not assert an implemented v2 protocol.

## 1. Encoding and integrity

- UTF-8 only; no duplicate object keys, nonfinite numeric values, invalid surrogate/NUL content, implicit coercion, uncontrolled schema references or undeclared fields.
- Hash source files and received frames from their original bounded bytes before strict decoding; parse those same bytes. Preserve separate `source-bytes-sha256`, `pack-record-sha256` and host `decision-core` digest kinds.
- New Pack/local request metadata uses integer-valued numbers in the exact interoperable range `[-(2^53-1), 2^53-1]`. A declared parameter requiring other numeric representations must bind a selected explicit representation contract; otherwise report unsupported representation rather than rounding/coercing. This is a new-path wire limit, not a change to legacy UInt64 Calculations.
- Existing source/host bodies retain their original bytes and selected decoder/encoding contract. The JavaScript front end passes file bytes/opaque frames to Python without parsing and reserializing authority content. Python can inspect exact integers outside JavaScript's range, but cannot silently encode them into a narrower host/Pack contract.
- Python emits new Pack records as deterministic sorted-key compact JSON, UTF-8, non-ASCII preserved, no NaN, with the agreed final newline included in file-byte hashes. Original bytes and host-specific canonical/core encoding remain separate domains.
- Every locally owned object has a closed required/optional field set. Union branches use an explicit discriminator. Schema selectors are resolved only within the selected digest-closed local schema set.

## 2. One concrete adapter selection

`cal.define.lab-adapter-selection/v1` selects one exact local Lab host installation. Required fields: `selection_id`, `revision`, `host_binding`, `extension_binding`, `protocol_binding`, `source_profile_binding`, `schema_bindings`, `dependency_selection_binding`, `source_selection_contract_binding`, `operation_mapping`, `credential_locators`, `authority_posture`, `limits`, `authority_effect:none`. These are digest-closed implementation/configuration references, not an admitted policy or permission by themselves.

- `host_binding` and `extension_binding` identify the explicitly selected successor, executable/interpreter and exact source/import guard. Do not discover versions by directory order.
- The operation mapping names the actual existing status/catalog/artifact/context/session/change/review/inspection routes needed for the selected use. An unavailable operation is refused, never mapped to a fixture callback.
- The separately selected host-local extension exposes only `stage-review`, `retain-package`, `read-retained` and `inspect-local-operation` with the contracts in [handoff](REVIEW-HANDOFF.md) and [reconstruction](RECONSTRUCTION.md). These are proposed extension operations, not current public Lab API methods.
- Credential locators are external host-owned selections without secret values. Native context construction and fresh nonce/permission checks are performed by the host. No caller-provided context becomes trusted authority.
- Snapshot preparation supplies an explicitly historical captured bundle and has no live channel/Session claim. There is no automatic backend fallback or credential refresh.
- Base context/ontology capture, candidate review operator permission and actual Governance application remain independently scoped. Shared principal identity does not combine grants.

This record preserves selection/compatibility/limits; it replaces the generalized backend profile/port framework in 0006. Missing current source/provider, representation or actual caller scope remains a named runtime prerequisite. The selected host enforces original nonce, source, caller, principal, scope, policy, clock and operation budgets.

## 3. Preparation request — `cal.define.prepare-request/v2`

| Required fields | Contract |
| --- | --- |
| `request_id`, `request_revision` | Attributable request identity; not an authority grant |
| `goal`, `originating_intent`, `context`, `consumer`, `intended_use` | Preserve selected references/text and any explicit owner/source gaps; revisions cannot silently replace intent |
| `adapter_selection_binding` | One exact concrete selection; the capture bundle separately declares live or historical mode |
| `required_concepts` | Nonempty bounded array of unique concept IDs and declared questions/scope |
| `handling` | Exactly one discriminated disposition payload per required concept |
| `source_bindings`, `evidence_bindings` | Declared exact roots/refs/selectors/digests/posture, not an unbounded repository search request |
| `applications`, `assessments` | Arrays, permitted empty; all entry identities/revisions unique and bindings explicit |
| `materialization_selection` | Array, default explicitly empty; identity/new-or-successor route and purpose required when selected |
| `validation_scope` | Required checks, interpreted/provider evidence scope and claim ceiling |
| `authority_effect` | `none` |

Optional fields: `predecessor_package_binding`, `field_supplement_binding`, `language_evidence_binding`. No hidden default admission selection, domain execution permission or anonymous inferred owner.

The first kernel consumes explicit handling input and available evidence. The interaction adapter maps attributable human/chat input into the exact revised handling/supplement fields. A model suggestion records its actual producer and candidate posture; submission is not semantic acceptance. Unsupported authoring assistance remains a reported limitation. The same deterministic checks apply.

## 4. Pack — `cal.define.pack/v2`

| Required fields | Purpose |
| --- | --- |
| `pack_id`, `revision`, `schema_version` | Stable work identity and exact frozen revision |
| `status`, `authority_effect` | Candidate/working posture and `none`; no embedded admitted effect |
| `scope` | Goal, originating Intent, context, consumer, intended use and authority boundary |
| `capture_binding` | Exact source/context/profile/cut/clock capture record |
| `required_concepts`, `handling` | Exactly one current handling result for each required concept |
| `working_meanings` | Embedded unadmitted meaning identity/revision/statement, scope, boundaries, explicit parameters and lineage |
| `parameter_contracts` | Exact mechanical interpretation records for selected meaning parameter declarations; no new semantic authority |
| `applications`, `assessments` | Individually addressable embedded entries; no per-task file requirement |
| `source_bindings`, `evidence_bindings` | Exact source/evidence standing, permitted use and retention/custody |
| `relationship_records` | Explicitly scoped suggestions/references; no inferred global Typed Relation effect |
| `owner_routes`, `gaps` | Applicable route refs or explicit gaps, each with affected use and continuation |
| `materialization_selection` | Explicit selections or empty array; not admission |
| `validation_scope`, `readiness` | Preparation-time named-use observations, exact evidence limits and blockers; later observations are separate |
| `lineage`, `claim_ceiling` | Prior package/revision and why changed; preserved limits |

`parameter_contracts` is a proposed mechanical representation of already declared parameter semantics. If its mapping changes normative meaning or cannot be expressed faithfully, it becomes a semantic-change/open route, not a mechanical shortcut. The current preview schema is an input example, not the final closed executable schema.

### Disposition union

| `disposition` | Required payload | Output |
| --- | --- | --- |
| `reuse` | Exact current admitted `meaning_ref`, captured standing/Decision basis, applicability | Reference to existing meaning; no duplicate Definition |
| `specialize` + `mode:application` | Exact parent, parameter-contract ref, declared value bindings, applicability and gaps | Embedded Definition application; meaning unchanged |
| `specialize` + `mode:meaning-change` | Exact parent, explicit delta/meaning proposal and new-or-successor intention | Embedded unadmitted working meaning; selected materialization separate |
| `propose` | Exact local working-meaning ref, scope/boundaries and ownership posture | Embedded unadmitted proposal by default |
| `open` | Question, reason, affected use, owner route or gap, continuation | Explicit unresolved handling, not invalid output by itself |

Duplicate concept keys, undeclared payload fields, multiple dispositions and mismatched branch payloads are errors. A missing required handling input produces an incomplete attempt, not a fabricated `open` answer without its declared required content.

An exact candidate parent can support an application for explicitly bounded proposal examination under the reviewed application model. It retains candidate standing and cannot qualify as admitted reuse, governing Policy or production conformance. The L0 specialization coverage may use the exact candidate criterion specimen on that basis; it must not invent an admitted parameterized criterion.

## 5. References and local selectors

Three closed reference variants:

1. **External selected artifact:** exact identity/version/carrier, original path/ref, size/digest kind/SHA-256, captured standing/Decision basis, selected root and permitted use.
2. **Embedded working meaning/application/assessment:** owning Pack work identity+revision, exact entry ID+revision, selector and canonical-entry digest. The local entry does not contain its containing Pack/manifest hash. A future external reference additionally binds the exact complete Pack bytes.
3. **Unavailable or pending source:** requested exact ref, reason, affected use and resolving owner/continuation. It is a gap, not a successful resolution.

Resolve RFC6901 selectors against the already captured document, reject ambiguous duplicate IDs, and verify that selector, ID/revision and digest identify the same entry. Reordering entries changes selectors and therefore creates a new Pack revision. No live lookup substitutes an unresolved embedded or historical reference.

## 6. Application

Required fields: `application_id`, `revision`, exact `meaning_ref`, `parameter_contract_ref`, `context_ref`, `consumer`, `intended_use`, `bindings`, `value_provenance`, `applicability`, `binding_gaps`, `lineage`, `authority_effect:none`.

- A binding map is partial only when every missing required value/reference is an explicit gap.
- Reject undeclared parameter names and unsupported/wrong value representations. Do not let `tolerance`, account or filter fields change a fixed criterion.
- Bind source values to exact evidence/selectors, not just a natural-language claim.
- `fully_bound` is a check result requiring resolved required names/types/refs and established applicability. It implies neither executed assessment nor admission/permission.
- Object-valued domain bindings follow the selected parameter/value schema. A generic `F:object` declaration alone does not establish what a source system's filter keys mean; unresolved filter interpretation/applicability remains a gap, even if the JSON value is structurally valid. The synthetic fixture's declared filter semantics do not automatically qualify a real source system.
- Changed values, meaning selection, input/evidence epoch or intended use create a new revision. A new assessment over unchanged inputs can be independently revisioned without rewriting the application.

For the incident, the criterion declares S/A/F/E. Work's task/context labels remain metadata unless the selected Work meaning separately declares parameters. Preserve the earlier specimen as history rather than silently treating its context labels as a qualified generic Work parameter contract.

## 7. Imported assessment

Required fields: `assessment_id`, `revision`, exact application ref and input/evidence bindings, selected method/profile refs or explicit gaps, producer/execution provenance, reported result or unevaluable reason, captured execution posture, validation posture, applicability limits and lineage.

Possible validation postures: `binding-verified-within-scope`, `unverified-reported`, `not-evaluable`. Invalid/different digests or nonexistent application entries reject the import; missing optional execution evidence can be retained as unverified with blockers. Domain `PASS/FAIL/NOT_EVALUABLE` is recorded separately from this validation posture.

A fresh actual execution receipt is not generated by Define. A synthetic fixture's producer posture stays synthetic. Imports that claim governed Evaluation/Measurement Result standing must resolve the corresponding actual carrier/profile/producer evidence; otherwise the claimed standing is rejected or explicitly unverified. No execution of arbitrary input formulas or modules occurs.

## 8. Readiness and errors

Every preparation report or separate later-use observation separates:

- structural validity;
- captured source standing;
- currentness for this use;
- parameter/applicability completeness;
- assessment execution/validation posture;
- semantic/fidelity assurance coverage;
- materialization/review eligibility;
- actual owner selection and applied effect.

Named uses: `inspect-preparation`, `apply-parameters`, `consume-assessment`, `materialize-definition`, `prepare-owner-review`, `governing-application`. Each has `ready`, `blocked` or `not-evaluable`, exact obligations/evidence and claim ceiling. Governing application is always assessed by the host at its actual boundary, not enabled by a saved Pack flag. Frozen readiness describes preparation time. A subsequent current-use observation is separately bound and cannot mutate the Pack or authorize a changed intended use.

A structurally complete Pack with an open exclusivity question can be ready to inspect while blocked for complete export conformance or incident closure. A snapshot-only Pack cannot be marked ready for current host review just by reusing its old capture.

Result envelope: `cal.define.result/v2` with command, request/package binding, outcome, named-use readiness, diagnostics/continuation, observed writes and `authority_effect:none`. Outcomes: `prepared`, `prepared-with-gaps`, `blocked`, `invalid-input`, `unsupported`, `interrupted`, `outcome-unknown`. An attempt receipt may exist without a conforming Pack. Planned new CLI exits:0 for produced conforming Pack/materialization/review preparation (including honest named-use gaps),2 invalid input,3 stale/unavailable/refused prerequisite,4 explicit unsupported protocol/representation,130 observed interruption. Legacy exits remain unchanged; a wrapper never derives success from exit0 alone.

## 9. Materialization and review

Materialization selection requires exact Pack/working-meaning/parameter-source refs, purpose, intended authority scope, selected owner route or gap, and `new-identity` or `successor` with exact parent. Only complete, faithful Definition/v2 bodies receive `definition.json` and generated `DEFINITION.md`. Field lineage links each emitted field to source selectors or explicit authored supplement and records semantic deltas. Missing required fields produce preparation gaps without a fake complete artifact.

The review-input manifest freezes candidate bytes, source/schema/profile/generator/implementation hashes, base epoch, dependency-closed targets, requested independent effects, examples, privacy and output recipe. A separate actual-outcomes record is created only from genuine owner outcomes. A third observed-consequences manifest binds actual generated results/receipts. None hashes a future signature or itself.

Use the ordered host-owned [review handoff](REVIEW-HANDOFF.md). Core inputs and metadata exist before `change.prepare`; host validation independently recomputes them. Map to the selected successor's exact native change-proposal/validation/review schemas. No active Vault mutation or historical authorization reuse is permitted. The current review profile is a single final all-or-nothing checkpoint over its selected members. First release therefore freezes the chosen dependency-closed cohort before review. A requested partial selection creates a new cohort/package and revalidates/reviews affected bindings; it is not silently applied as a subset of an incompatible checkpoint. Shared principal identity does not merge role decisions.

## 10. Resource bounds

Reuse the existing [initial limits](../0005-amended-integration-plan/limits.json). Effective bounds are the stricter of those limits, actual selected host policy and a contract-specific bound.

| Boundary | Initial design limit |
| --- | --- |
| Pack input / supplement |1MiB each |
| Local combined request |4MiB; split into exact material references for smaller host frames |
| Host frame |At most1MiB and never more than actual host policy |
| Source file / complete selected snapshot |16MiB /64MiB |
| Output package |16MiB |
| Concepts / within-Pack pairs |24 /276 |
| Applications / assessments / parameter contracts |64 /64 /24 proposed new-path entry ceilings |
| JSON nesting / schema ref depth |64 /8 |
| Selected references / assurance comparisons per batch |256 /512 |
| History entries exported |256 |
| Inline context / maximum requested TTL |256KiB /900s; host expiry and shorter policy always win |
| Ontology depth / nodes / edges |2 /60 /100 |
| Ordinary bridge subprocess |60s; a host phase exceeding that ceiling returns explicit incomplete/timeout and is not killed/retried as a successful fresh Session |

These are design ceilings, not measured performance promises or permission periods. Batch continuation binds the original full required-set digest, completed obligations and exact next cursor; truncation cannot establish complete coverage. A longer host startup contract requires an explicit reviewed successor timeout, not a hidden increase or renewed expiry.

A source body larger than an allowed host frame needs an already supported retained-material transfer or an explicitly permitted local exact-file capture. An object reference alone does not confer permission to read its path. If neither route exists, report unsupported transfer; do not invent chunk operations or concatenate independently changing captures into one supposedly exact record.

## 11. Captured bundle — `cal.define.capture-bundle/v1`

Required fields: `capture_id`, `revision`, `mode` (`live-host` or `historical-snapshot`), `adapter_selection_binding`, `intended_use`, `source_cut`, `source_profile_binding`, `context_bindings`, `ontology_view_bindings`, `captured_at`, `permission_observation_binding`, `input_rows`, `capture_limits`, `gaps`, `authority_effect:none`. Live capture additionally requires the actual host response/currentness/expiry evidence; an actual machine Session binding is present only when genuinely established. Historical capture records its original observed standing/time and cannot manufacture a live lease.

Each input row has exactly `input_id`, `population`, `binding`, `encoding_contract_binding`, `selector`, `standing_observation`, `provenance_bindings`, `permitted_uses`, `retention_posture`. `population` is `host-member`, `local-supplement` or `external-evidence`.

- A host member additionally resolves exact artifact header/source-cut membership under the selected profile; raw file versus selected-value canonical encoding is explicit.
- A supplement binds attributable input/producer and candidate status; it never inherits the capture cut's admission.
- External evidence retains actual producer/method/receipt and execution limits. Missing facts remain gaps.

Original bytes travel as bound buffers/members, not through ambiguous parsed JSON substitution. The pure core consumes this normalized record without interpreting installation-specific directory names as semantic standing. A local copy claiming host membership must match the host's exact binding or refuse/recapture.

## 12. Later use observation — `cal.define.use-observation/v1`

Required fields: `observation_id`, `pack_binding`, `captured_intended_use_binding`, `requested_use`, `current_source_profile_binding`, `current_cut`, `observed_at`, `consumer_binding`, `permission_observation_binding`, `obligation_results`, `evidence_bindings`, `outcome`, `limitations`, `authority_effect:none`.

`pack_binding` is the exact frozen Pack-file digest/size/schema. Each obligation result has exact obligation, result (`ready`, `blocked`, `not-evaluable`), evidence and affected scope. The report distinguishes source currentness, parameter applicability, assessment provenance, owner/profile/representation standing and actual permission. A new observation may refuse unchanged frozen content for changed current conditions. A changed selected input, intended use, payload, concept set or meaning requires the applicable new frozen revision with lineage; an observation cannot mask it.

## 13. Handoff and retention formats

[Review handoff](REVIEW-HANDOFF.md) owns the closed ReviewCohort, scoped operator selection, StageReviewRequest/Result and native core algorithm. [Reconstruction](RECONSTRUCTION.md) owns the closed root/member manifest, custody completion receipt and reconstruction observation. They are implementation formats and evidence, not new Artifact Types.

Bindings are typed by role: raw-source/file bytes, new canonical record, native target/core semantics, original core-file bytes, retained root/member bytes or actual governing artifact header. Do not interchange their digests even if all use SHA-256. No future owner signature or containing receipt hash is inside the signed/hashed content itself.

Retained references require the new selected host resolver, not just a string accepted by a carrier schema. Native material controls remain at most 1 MiB each; larger retained objects use only the explicitly declared bounded local transfer, never an invented existing API chunk operation. The companion's input manifest fixes every buffer length/order/digest before any bytes are accepted; trailing, short, overflowed or interrupted streams refuse. Root/member privacy and exactness are checked before commit or caller-visible body return.
