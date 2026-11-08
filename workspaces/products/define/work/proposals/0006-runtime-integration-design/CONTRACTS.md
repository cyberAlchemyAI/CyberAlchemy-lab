# Contract design

Status: proposed closed wire and local-package contracts. These names are protocol design choices, not admitted Artifact Types or new semantic Definitions. Existing Lab schemas remain authoritative for their selected carriers. Executable schemas are future implementation work.

## 1. Encoding and integrity

- UTF-8 only; no duplicate object keys, nonfinite numeric values, invalid surrogate/NUL content, implicit coercion, uncontrolled schema references or undeclared fields.
- Hash source files and received frames from their original bounded bytes before strict decoding; parse those same bytes. Preserve separate `source-bytes-sha256`, `pack-record-sha256` and host `decision-core` digest kinds.
- New Pack/local request metadata uses integer-valued numbers in the exact interoperable range `[-(2^53-1), 2^53-1]`. A declared parameter requiring other numeric representations must bind a selected explicit representation contract; otherwise report unsupported representation rather than rounding/coercing. This is a new-path wire limit, not a change to legacy UInt64 Calculations.
- Existing source/host bodies retain their original bytes and selected decoder/encoding contract. The JavaScript front end passes file bytes/opaque frames to Python without parsing and reserializing authority content. Python can inspect exact integers outside JavaScript's range, but cannot silently encode them into a narrower host/Pack contract.
- Python emits new Pack records as deterministic sorted-key compact JSON, UTF-8, non-ASCII preserved, no NaN, with the agreed final newline included in file-byte hashes. Original bytes and host-specific canonical/core encoding remain separate domains.
- Every locally owned object has a closed required/optional field set. Union branches use an explicit discriminator. Schema selectors are resolved only within the selected digest-closed local schema set.

## 2. Runtime profile and Host Port

### Runtime profile — `cal.define.runtime-profile/v1`

| Required field | Meaning |
| --- | --- |
| `profile_id`, `revision`, `posture` | Exact local profile identity; candidate/admitted standing retained separately from execution permission |
| `backend` | Discriminated `lab-protocol` or `captured-snapshot`; never implicit fallback |
| `executable_binding`, `protocol_binding`, `source_profile_binding`, `schema_bindings` | Exact selected path/ref, digest kind, SHA-256 and original size |
| `selection_contract_binding` | Exact host current-State/source-cut contract, including allowed predecessor/history use |
| `transport` | Local stdio or explicit already selected host transport, bounded frames/timeouts; no shell command interpolation |
| `operations` | Declared host operations needed by this profile; checked against the actual selected catalog |
| `authority_posture`, `credential_locators` | Host-owned issuer/principal/policy scope and external credential locators; no secret values or inferred role grant |
| `limits` | Resource ceilings bounded by both Define and the selected host |
| `compatibility_binding` | Exact accepted/proposed consumer/store/representation disposition; no silent migration |
| `authority_effect` | `none` for this profile record |

A captured snapshot also declares source/context/evidence bindings, captured standing, capture time, permitted retention/export and `historical-snapshot` freshness. It cannot return a live Session or new currentness claim. `credential_locators` is empty for that branch.

### Internal port methods

These are proposed internal methods, not added API operations:

| Method | Result and required checks |
| --- | --- |
| `inspect_profile()` | Exact selected executable/protocol/dependency bindings, available surface and posture; fail on drift |
| `capture_context(request)` | One source cut, Context/Ontology View refs/bodies as permitted, source selection/HEAD, clock/expiry, consumer scope and exact response binding |
| `resolve_exact(ref, cut)` | Original selected bytes or explicit unavailable/refused; exact identity/version/carrier/standing and selector provenance |
| `check_current(capture, intended_use)` | Fresh exact host/source/body/profile checks; returns observation, never rewrites the frozen capture |
| `prepare_change(targets, cut)` | Existing host proposal and validation material with pending actual outcomes |
| `prepare_review(proposal, routing)` | Existing independently revalidated review/checkpoint package; no owner outcome |
| `inspect_operation(binding)` | Exact journal/receipt/current selection after uncertain outcome |
| `close()` | Release only owned channels/Sessions/resources; clear short-lived memory and persist permitted diagnostics |

The host enforces its real nonce, source, caller context, principal, scope, policy and clock. A supplied `caller_ref` is context only. If an actual host role/custody/preparation policy is unavailable, return a blocker rather than minting a fixture credential.

## 3. Preparation request — `cal.define.prepare-request/v2`

| Required fields | Contract |
| --- | --- |
| `request_id`, `request_revision` | Attributable request identity; not an authority grant |
| `goal`, `originating_intent`, `context`, `consumer`, `intended_use` | Preserve selected references/text and any explicit owner/source gaps; revisions cannot silently replace intent |
| `runtime_profile_binding` | One exact selected profile; live or snapshot mode explicit |
| `required_concepts` | Nonempty bounded array of unique concept IDs and declared questions/scope |
| `handling` | Exactly one discriminated disposition payload per required concept |
| `source_bindings`, `evidence_bindings` | Declared exact roots/refs/selectors/digests/posture, not an unbounded repository search request |
| `applications`, `assessments` | Arrays, permitted empty; all entry identities/revisions unique and bindings explicit |
| `materialization_selection` | Array, default explicitly empty; identity/new-or-successor route and purpose required when selected |
| `validation_scope` | Required checks, interpreted/provider evidence scope and claim ceiling |
| `authority_effect` | `none` |

Optional fields: `predecessor_package_binding`, `field_supplement_binding`, `language_evidence_binding`. No hidden default admission selection, domain execution permission or anonymous inferred owner.

The first kernel consumes explicit handling input and available evidence. Existing chat can help author a new request/supplement; its prose becomes candidate input. It cannot bypass the same deterministic checks.

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
| `validation_scope`, `readiness` | Named-use results, exact evidence limits and current-use observations |
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

Every result separates:

- structural validity;
- captured source standing;
- currentness for this use;
- parameter/applicability completeness;
- assessment execution/validation posture;
- semantic/fidelity assurance coverage;
- materialization/review eligibility;
- actual owner selection and applied effect.

Named uses: `inspect-preparation`, `apply-parameters`, `consume-assessment`, `materialize-definition`, `prepare-owner-review`, `governing-application`. Each has `ready`, `blocked` or `not-evaluable`, exact obligations/evidence and claim ceiling. Governing application is always assessed by the host at its actual boundary, not enabled by a saved Pack flag.

A structurally complete Pack with an open exclusivity question can be ready to inspect while blocked for complete export conformance or incident closure. A snapshot-only Pack cannot be marked ready for current host review just by reusing its old capture.

Result envelope: `cal.define.result/v2` with command, request/package binding, outcome, named-use readiness, diagnostics/continuation, observed writes and `authority_effect:none`. Outcomes: `prepared`, `prepared-with-gaps`, `blocked`, `invalid-input`, `unsupported`, `interrupted`, `outcome-unknown`. An attempt receipt may exist without a conforming Pack. Planned new CLI exits:0 for produced conforming Pack/materialization/review preparation (including honest named-use gaps),2 invalid input,3 stale/unavailable/refused prerequisite,4 explicit unsupported protocol/representation,130 observed interruption. Legacy exits remain unchanged; a wrapper never derives success from exit0 alone.

## 9. Materialization and review

Materialization selection requires exact Pack/working-meaning/parameter-source refs, purpose, intended authority scope, selected owner route or gap, and `new-identity` or `successor` with exact parent. Only complete, faithful Definition/v2 bodies receive `definition.json` and generated `DEFINITION.md`. Field lineage links each emitted field to source selectors or explicit authored supplement and records semantic deltas. Missing required fields produce preparation gaps without a fake complete artifact.

The review-input manifest freezes candidate bytes, source/schema/profile/generator/implementation hashes, base epoch, dependency-closed targets, requested independent effects, examples, privacy and output recipe. A separate actual-outcomes record is created only from genuine owner outcomes. A third observed-consequences manifest binds actual generated results/receipts. None hashes a future signature or itself.

Map to existing host change-proposal/validation/review schemas exactly. The current review profile is a single final all-or-nothing checkpoint over its selected members. First release therefore freezes the chosen dependency-closed cohort before review. A requested partial selection creates a new cohort/package and revalidates/reviews affected bindings; it is not silently applied as a subset of an incompatible checkpoint. Shared principal identity does not merge role decisions.

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
